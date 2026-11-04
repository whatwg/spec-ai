#!/usr/bin/env python3
"""Flag possibly normative differences introduced by editorial changes.

  spec BASE HEAD [FILE...]   Compare spec sources (Wattsi `source`, Bikeshed `.bs`) between two
                             git revisions, in the current directory's repo. Without FILEs,
                             checks the spec files changed between BASE and HEAD.
  wpt BEFORE.json AFTER.json [--rename '[TEST | ]OLD => NEW']...
                             Compare two `./wpt run --log-wptreport` results per subtest,
                             after renaming test paths (with any variants), or subtests of
                             TEST (the old test ID).

Exits 1 if anything differs. Differences are leads for review, not proof of a normative change.
"""

import argparse
import html
import json
import re
import subprocess
import sys
from collections import Counter

SPEC_FILE = re.compile(r"(^|/)source$|\.bs$")
COMMENT = re.compile(r"<!--.*?-->", re.S)
WATTSI_IDL = re.compile(r'<pre><code class="?idl"?[^>]*>(.*?)</code></pre>', re.S)
BIKESHED_IDL = re.compile(
    r"<(pre|xmp)\b[^>]*\bclass=(?:\"[^\"]*\bidl\b[^\"]*\"|'[^']*\bidl\b[^']*'|idl\b)[^>]*>"
    r"(.*?)</\1>", re.S)
IDL_DEFINITION = re.compile(r"\b(?:interface(?: mixin)?|dictionary|enum|namespace|callback)\s+"
                            r"(\w+)")
TAG = re.compile(r"<[^>]*>")
DFN = re.compile(r"<dfn\b([^>]*)>(.*?)</dfn>", re.S)
ATTR = re.compile(r"([\w-]+)(?:\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+))?")
ID = re.compile(r"\sid=(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))")
START_TAG = re.compile(r"<[a-zA-Z][^>]*>")
KEYWORDS = re.compile(r"\b(must not|must|should not|should|may not|may|shall not|shall)\b",
                      re.I)
EXCEPTION = re.compile(r"\b(?:[A-Z]\w*Error|DOMException)\b|\b(?:re)?throws?\b")
EVENT_FIRE = re.compile(r"\bfir(?:e|es|ing) (?:a|an) (?:[\w-]+ )*?event(?:=\])? named \"?"
                        r"(?:\{\{)?(?:[\w-]+/)?([\w:-]+)", re.I)
EVENT_REF = re.compile(r"data-x=\"(event-[^\"]+)\"")
NON_NORMATIVE = re.compile(
    r"<(p|div|dl|aside)\b[^>]*\bclass=(?:\"[^\"]*\b(?:note|example|XXX|warning|domintro)\b"
    r"[^\"]*\"|'[^']*\b(?:note|example|XXX|warning|domintro)\b[^']*'"
    r"|(?:note|example|XXX|warning|domintro)\b)[^>]*>")
# A <p> ends at its end tag, at the next block start or end, or at a blank line (Bikeshed).
P_END = re.compile(r"</p\s*>|(?=<(?:p|div|ol|ul|dl|pre|table|h\d|xmp)\b|</(?:div|li|dd|td)\b"
                   r"|\n[ \t]*\n)", re.I)
# Bikeshed treats paragraphs starting with "Note: " or "Note, " as notes.
BIKESHED_NOTE = re.compile(r"(?:^|(?<=\n\n)|(?<=<p>))[ \t]*(?:<p>)?\s*Note[:,].*?"
                           r"(?=</p\s*>|\n[ \t]*\n|$)", re.S)
LITERAL = re.compile(r"\"<code\b[^>]*>(.*?)</code>\"|\"\{\{([^}]*)\}\}\"|\"`([^`]*)`\"", re.S)
BYTE_LITERAL = re.compile(r"`<code\b[^>]*>(.*?)</code>`", re.S)


def git_show(rev, path):
    """Return the file at rev, or None if rev exists but the file doesn't. Fail otherwise."""
    result = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True,
                            errors="replace")
    if result.returncode == 0:
        return result.stdout
    if subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
                      capture_output=True).returncode != 0:
        sys.exit(f"error: unknown revision {rev}")
    return None


def changed_spec_files(base, head):
    """(old path, new path) for each changed spec file, following renames."""
    out = subprocess.run(["git", "diff", "--name-status", "-M", base, head], capture_output=True,
                         text=True, check=True).stdout
    pairs = []
    for line in out.splitlines():
        status, *paths = line.split("\t")
        old, new = (paths[0], paths[-1])
        if SPEC_FILE.search(old) or SPEC_FILE.search(new):
            pairs.append((old, new))
    return pairs


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


def plain(markup):
    return squash(html.unescape(TAG.sub("", markup)))


def idl_blocks(src):
    return [m.group(1) for m in WATTSI_IDL.finditer(src)] + \
           [m.group(2) for m in BIKESHED_IDL.finditer(src)]


def without_idl(src):
    return BIKESHED_IDL.sub("", WATTSI_IDL.sub("", src))


def without_non_normative(src):
    """Drop notes, examples, warnings, XXX boxes, and domintro, matching nested same-name tags."""
    out, pos = [], 0
    while (m := NON_NORMATIVE.search(src, pos)):
        out.append(src[pos:m.start()])
        name, depth, end = m.group(1), 1, m.end()
        if name.lower() == "p":
            t = P_END.search(src, end)
            pos = t.end() if t else len(src)
            continue
        tags = re.compile(rf"<(/?){name}\b[^>]*>", re.I)
        while depth and (t := tags.search(src, end)):
            depth += -1 if t.group(1) else 1
            end = t.end()
        if depth:  # Unclosed: drop only the start tag rather than the rest of the file.
            end = m.end()
        pos = end
    out.append(src[pos:])
    return BIKESHED_NOTE.sub("", "".join(out))


def idl_statements(src):
    """IDL statements, with members keyed by their enclosing definition's name."""
    stmts = Counter()
    for block in idl_blocks(src):
        text = html.unescape(TAG.sub("", block))
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"//[^\n]*", "", text)
        names = []
        for stmt, delim in re.findall(r"([^;{}]*)([;{}]|$)", text):
            stmt = squash(stmt)
            if delim == "{":
                m = IDL_DEFINITION.search(stmt)
                names.append(m.group(1) if m else stmt)
            if stmt:
                stmts[f"{names[-1]}: {stmt}" if names and delim != "{" else stmt] += 1
            if delim == "}" and names:
                names.pop()
    return stmts


def attrs(raw):
    return {m.group(1): (m.group(2) or "").strip("\"'") for m in ATTR.finditer(raw)}


def dfns(src):
    keys, exported, external = Counter(), Counter(), Counter()
    for m in DFN.finditer(src):
        a = attrs(m.group(1))
        name = a.get("data-x") or a.get("lt") or plain(m.group(2)).lower()
        key = f"{a['for']}/{name}" if a.get("for") else name
        if "data-x-href" in a:
            external[f"{key} -> {a['data-x-href']}"] += 1
            continue
        keys[key] += 1
        if "export" in a:
            exported[key] += 1
    return keys, exported, external


def ids(src):
    """ids on real start tags, so escaped markup in examples doesn't count."""
    return Counter(next(g for g in m.groups() if g is not None)
                   for tag in START_TAG.finditer(src) for m in ID.finditer(tag.group()))


def extract(src):
    src = COMMENT.sub("", src)
    body = without_idl(src)
    text = plain(body)
    normative_text = plain(without_non_normative(body))
    dfn_keys, exported, external = dfns(src)
    return {
        "IDL statements": idl_statements(src),
        "dfns": dfn_keys,
        "exported dfns": exported,
        "external terms (data-x-href)": external,
        "ids": ids(src),
        "RFC 2119 keywords (normative text)": Counter(
            k.lower() for k in KEYWORDS.findall(normative_text)),
        "exceptions and throws": Counter(EXCEPTION.findall(text)),
        "fired events": Counter(EVENT_FIRE.findall(text)),
        "event references": Counter(EVENT_REF.findall(body)),
        "quoted string literals": Counter(
            lit for a, b, c in LITERAL.findall(body)
            if not re.fullmatch(r"\w*Error", lit := re.sub(r"!!\w+$", "", plain(a or b or c)))),
        "byte-sequence literals": Counter(plain(m) for m in BYTE_LITERAL.findall(body)),
    }


def diff_counters(before, after):
    removed = before - after
    added = after - before
    return removed, added


def show(items, limit=40):
    lines = [f"      {k!r}" + (f" ×{n}" if n > 1 else "") for k, n in sorted(items.items())]
    if len(lines) > limit:
        lines = lines[:limit] + [f"      … {len(lines) - limit} more"]
    return "\n".join(lines)


def check_spec(args):
    pairs = [(p, p) for p in args.files] or changed_spec_files(args.base, args.head)
    if not pairs:
        print("No spec files changed.")
        return 0
    found = False
    for old_path, path in pairs:
        old, new = git_show(args.base, old_path), git_show(args.head, path)
        if old is None and new is None:
            sys.exit(f"error: {path} exists in neither revision (paths are relative to the repo "
                     "root)")
        if old is None or new is None:
            print(f"{path}: only in {args.head if old is None else args.base}")
            found = True
            continue
        if old_path != path:
            print(f"{old_path} -> {path} (renamed)")
        before, after = extract(old), extract(new)
        report = []
        for category in before:
            removed, added = diff_counters(before[category], after[category])
            if removed or added:
                report.append(f"  {category}:")
                if removed:
                    report.append(f"    removed ({sum(removed.values())}):\n{show(removed)}")
                if added:
                    report.append(f"    added ({sum(added.values())}):\n{show(added)}")
        if report:
            found = True
            print(f"{path}:")
            print("\n".join(report))
        else:
            print(f"{path}: no differences")
    return 1 if found else 0


def load_wptreport(path):
    """Map (subsuite, test, subtest or None) to the sorted statuses of every run of it."""
    with open(path) as f:
        data = json.load(f)
    results = {}
    for test in data.get("results", []):
        suite = test.get("subsuite", "")
        results.setdefault((suite, test["test"], None), []).append(test.get("status"))
        for sub in test.get("subtests", []):
            results.setdefault((suite, test["test"], sub["name"]), []).append(sub.get("status"))
    if not results:
        sys.exit(f"error: {path} has no results")
    return {k: sorted(v) for k, v in results.items()}


def parse_renames(specs):
    """'OLD => NEW' renames a test path (variants and all); 'TEST | OLD => NEW' a subtest."""
    paths, subtests = {}, {}
    for spec in specs:
        lhs, sep, new = spec.partition(" => ")
        if not sep:
            sys.exit(f"error: --rename expects 'OLD => NEW' or 'TEST | OLD => NEW', got {spec!r}")
        test, bar, old = lhs.partition(" | ")
        if bar:
            subtests[(test, old)] = new
        else:
            paths[lhs] = new
    return paths, subtests


def renamed(results, paths, subtests):
    out = {}
    for (suite, test, sub), statuses in results.items():
        if sub is not None:
            sub = subtests.get((test, sub), sub)
        path, q, variant = test.partition("?")
        test = paths.get(path, path) + q + variant
        key = (suite, test, sub)
        if key in out:
            sys.exit(f"error: renames map two results onto {test}" + (f" | {sub}" if sub else ""))
        out[key] = statuses
    return out


def check_wpt(args):
    before = renamed(load_wptreport(args.before), *parse_renames(args.rename))
    after = load_wptreport(args.after)
    diffs = []
    for key in sorted(before.keys() | after.keys(), key=lambda k: (k[0], k[1], k[2] or "")):
        old, new = before.get(key, ["(absent)"]), after.get(key, ["(absent)"])
        if old != new:
            suite, test, sub = key
            diffs.append(f"  {suite + ': ' if suite else ''}{test}" + (f" | {sub}" if sub else "")
                         + f": {', '.join(old)} -> {', '.join(new)}")
    if diffs:
        print("Result differences:")
        print("\n".join(diffs))
        return 1
    print(f"No differences ({len(before)} results).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    spec = sub.add_parser("spec", help="compare spec sources between two git revisions")
    spec.add_argument("base")
    spec.add_argument("head")
    spec.add_argument("files", nargs="*")
    wpt = sub.add_parser("wpt", help="compare two wptreport JSON files")
    wpt.add_argument("before")
    wpt.add_argument("after")
    wpt.add_argument("--rename", action="append", default=[], metavar="'[TEST | ]OLD => NEW'",
                     help="map a renamed test path, or a subtest of TEST (repeatable)")
    args = parser.parse_args()
    return check_spec(args) if args.command == "spec" else check_wpt(args)


if __name__ == "__main__":
    sys.exit(main())
