#!/usr/bin/env python3
"""Flag possibly normative differences between two versions of a spec change.

  spec BASE HEAD [FILE...]
      Compare spec sources (Wattsi `source`, Bikeshed `.bs`) between two git revisions of the
      repo in the current directory. Without FILEs, checks the spec files changed between BASE
      and HEAD, following renames. FILEs are paths at HEAD, relative to the repo root.

  wpt BEFORE.json AFTER.json [--map 'OLD => NEW']...
      Compare two `./wpt run --log-wptreport` results (same browser) per subtest. OLD and NEW
      are `TEST` or `TEST | SUBTEST` (`TEST | OLD => NEW` renames a subtest in place). A TEST
      map moves the test and all its subtests, and without `?` it covers every variant
      (`/a.html => /b.html` maps `/a.html?x` to `/b.html?x`). A SUBTEST map moves one subtest,
      also to another file; a file that only exists because subtests moved into it gets its
      harness status compared with the file they came from. Unmatched results come with
      suggested maps; check each before using it.

Exit status: 0 no differences, 1 differences, 2 bad input. Differences are leads for review,
not proof of a normative change, and no differences doesn't prove a change editorial.
"""

import argparse
import html
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict

SPEC_FILE = re.compile(r"(^|/)source$|\.bs$")
COMMENT = re.compile(r"<!--.*?-->", re.S)
WATTSI_IDL = re.compile(r'<pre>\s*<code class="?idl"?[^>]*>(.*?)</code>\s*</pre>', re.S)
BIKESHED_IDL = re.compile(
    r"<(pre|xmp)\b[^>]*\bclass=(?:\"[^\"]*\bidl\b[^\"]*\"|'[^']*\bidl\b[^']*'|idl\b)[^>]*>"
    r"(.*?)</\1>", re.S)
# Blocks whose content is literal text or metadata, not spec markup.
LITERAL_BLOCK = re.compile(
    r"<(xmp|script|style)\b[^>]*>.*?</\1>"
    r"|<pre\b[^>]*\bclass=[\"']?(?:[^\"'>]*\s)?(?:lang-[\w-]+|metadata|biblio|anchors"
    r"|link-defaults|ignored-specs)\b[^>]*>.*?</pre>", re.S | re.I)
BIKESHED_BLOCK = re.compile(
    r"<pre\b[^>]*\bclass=[\"']?(anchors|link-defaults)\b[^>]*>(.*?)</pre>", re.S)
TAG = re.compile(r"<[^>]*>")
START_TAG = re.compile(r"<[A-Za-z][\w-]*\b([^<>]*)>")
DFN = re.compile(r"<dfn\b([^>]*)>(.*?)</dfn>", re.S)
ATTR = re.compile(r"([\w-]+)(?:\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+))?")
KEYWORDS = re.compile(r"\b(must not|must|should not|should|may not|may|shall not|shall)\b",
                      re.I)
EXCEPTION = re.compile(r"\b[A-Z]\w*Error\b|\bDOMException\b|\b(?:re)?throw(?:s|n|ing)?\b")
EVENT_FIRE = re.compile(r"\bfir(?:e|es|ed|ing) (?:an? )?(?:[\w-]+ ){0,3}?events? named "
                        r"[\"']?([\w:-]+)", re.I)
EVENT_REF = re.compile(r"data-x=\"(event-[^\"]+)\"")
NON_NORMATIVE = re.compile(
    r"<(p|div|dl|aside|pre)\b[^>]*\bclass=(?:\"[^\"]*\b(?:note|example|XXX|warning|domintro)\b"
    r"[^\"]*\"|'[^']*\b(?:note|example|XXX|warning|domintro)\b[^']*'"
    r"|(?:note|example|XXX|warning|domintro)\b)[^>]*>")
# A <p> ends at its end tag, at the next block start or end, or at a blank line (Bikeshed).
P_END = re.compile(r"</p\s*>|(?=<(?:p|div|ol|ul|dl|pre|table|h\d|xmp)\b|</(?:div|li|dd|td)\b"
                   r"|\n[ \t]*\n)", re.I)
# Bikeshed treats paragraphs starting with "Note: " or "Note, " as notes.
BIKESHED_NOTE = re.compile(r"(?:^|(?<=\n\n)|(?<=<p>))[ \t]*(?:<p>)?\s*Note[:,].*?"
                           r"(?=</p\s*>|\n[ \t]*\n|$)", re.S)
STRING_LITERAL = re.compile(
    r"\"<code\b[^>]*>((?:(?!</code>)[^\"])*)</code>\"|\"\{\{([^}\"]*)\}\}\"|\"`([^`\"]*)`\"")
BYTE_LITERAL = re.compile(
    r"`(?:<a\b[^>]*>)?<code\b[^>]*>((?:(?!</code>)[^`])*)</code>(?:</a>)?`")
# Bikeshed autolink shorthands, reduced to the text they render.
SHORTHANDS = [
    re.compile(r"\{\{(.*?)\}\}", re.S),
    re.compile(r"\[=(.*?)=\]", re.S),
    re.compile(r"\[\$(.*?)\$\]", re.S),
    re.compile(r"<\{(.*?)\}>", re.S),
    re.compile(r"''(.*?)''", re.S),
]
BIKESHED_VAR = re.compile(r"\|(\w[\w -]*?)\|")


def run_git(*args):
    result = subprocess.run(["git", *args], capture_output=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    return result.stdout.decode("utf-8", "replace")


def git_show(rev, path):
    """Return the file at rev, or None if rev exists but the file doesn't."""
    result = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if result.returncode == 0:
        return result.stdout.decode("utf-8", "replace")
    if subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
                      capture_output=True).returncode != 0:
        print(f"error: unknown revision {rev}", file=sys.stderr)
        sys.exit(2)
    return None


def changed_spec_files(base, head):
    """Return (base path or None, head path or None) pairs, following renames."""
    out = run_git("diff", "-M", "--name-status", "-z", base, head).split("\0")
    pairs, i = [], 0
    while i < len(out) - 1:
        status = out[i]
        if status[:1] in ("R", "C"):
            old, new = out[i + 1], out[i + 2]
            i += 3
        else:
            old = new = out[i + 1]
            i += 2
            if status[:1] == "A":
                old = None
            elif status[:1] == "D":
                new = None
        if any(p and SPEC_FILE.search(p) for p in (old, new)):
            pairs.append((old, new))
    return pairs


def base_path_for(base, head, path):
    for old, new in changed_spec_files(base, head):
        if new == path:
            return old
    return path


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


def link_text(inner):
    """Return what a Bikeshed autolink renders: `for/term!!type|text` -> text or term."""
    if "|" in inner:
        return inner.rsplit("|", 1)[1]
    inner = inner.split("!!", 1)[0]
    return inner.rstrip("/").rsplit("/", 1)[-1] if "/" in inner.rstrip("/") else inner


def plain(markup):
    for pattern in SHORTHANDS:
        markup = pattern.sub(lambda m: link_text(m.group(1)), markup)
    text = html.unescape(TAG.sub("", markup))
    return squash(BIKESHED_VAR.sub(r"\1", text))


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


def normalize_idl(text):
    text = re.sub(r"\s*,\s*", ", ", squash(text))
    text = re.sub(r"([(\[<])\s+", r"\1", text)
    text = re.sub(r"\s+([)\]>])", r"\1", text)
    return re.sub(r"\s*=\s*", "=", text)


def idl_definitions(src):
    """Return Counters of IDL top-level statements and of members keyed by their definition."""
    headers, members = Counter(), Counter()

    def add_member(owner, text):
        if squash(text):
            members[f"{owner}: {normalize_idl(text)}"] += 1

    for m in list(WATTSI_IDL.finditer(src)) + list(BIKESHED_IDL.finditer(src)):
        text = html.unescape(TAG.sub("", m.group(m.lastindex)))
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"//[^\n]*", "", text)
        depth, current, owner, kind = 0, "", None, None
        for ch in text:
            if depth == 0:
                if ch == "{":
                    header = normalize_idl(current)
                    headers[header] += 1
                    name = re.sub(r"^(?:\[.*?\]\s*)?(?:partial\s+)?", "", header)
                    owner = re.split(r"\s*[:=]", name)[0]
                    kind = owner.split(" ")[0]
                    depth, current = 1, ""
                elif ch == ";":
                    if squash(current):
                        headers[normalize_idl(current)] += 1
                    current = ""
                else:
                    current += ch
                continue
            if ch in "{[(":
                depth += 1
            elif ch in ")]":
                depth -= 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    for part in current.split(",") if kind == "enum" else [current]:
                        add_member(owner, part)
                    current = ""
                    continue
            if depth == 1 and (ch == ";" or (ch == "," and kind == "enum")):
                add_member(owner, current)
                current = ""
            else:
                current += ch
    return headers, members


def attrs(raw):
    return {m.group(1).lower(): (m.group(2) or "").strip("\"'") for m in ATTR.finditer(raw)}


def dfns(src):
    keys, exported, external = Counter(), Counter(), Counter()
    for m in DFN.finditer(src):
        a = attrs(m.group(1))
        names = a.get("data-x") or a.get("lt") or a.get("data-lt") or plain(m.group(2)).lower()
        fors = [squash(f) for f in (a.get("for") or a.get("data-dfn-for") or "").split(",")]
        for name in names.split("|"):
            for f in [f for f in fors if f] or [None]:
                key = f"{f}/{squash(name)}" if f else squash(name)
                if "data-x-href" in a:
                    external[f"{key} -> {a['data-x-href']}"] += 1
                    continue
                keys[key] += 1
                if ("export" in a or "data-export" in a) and "noexport" not in a:
                    exported[key] += 1
    return keys, exported, external


def bikeshed_anchors(src):
    """Return normalized entries of <pre class=anchors> and <pre class=link-defaults> blocks."""
    entries = Counter()
    for m in BIKESHED_BLOCK.finditer(src):
        kind, stack = m.group(1), []  # (indent, fields) of enclosing context lines
        for line in html.unescape(m.group(2)).splitlines():
            if not line.strip():
                stack = []
                continue
            indent = len(line) - len(line.lstrip())
            parts = {}
            for part in line.split(";"):
                key, sep, value = part.partition(":")
                if sep:
                    parts[squash(key)] = squash(value)
            while stack and stack[-1][0] >= indent:
                stack.pop()
            context = {k: v for _, fields in stack for k, v in fields.items()}
            if kind == "anchors" and "text" not in parts:
                stack.append((indent, parts))
                continue
            merged = {**context, **parts}
            if "urlPrefix" in merged and "url" in merged:
                merged["url"] = merged.pop("urlPrefix") + merged["url"]
            entries[f"{kind}: " + "; ".join(f"{k}:{v}" for k, v in sorted(merged.items()))] += 1
    return entries


def ids(markup):
    found = Counter()
    for m in START_TAG.finditer(markup):
        value = attrs(m.group(1)).get("id")
        if value:
            found[value] += 1
    return found


def literals(normative):
    found = Counter()
    for code, link, backticked in STRING_LITERAL.findall(normative):
        value = plain(code or (link and link_text(link)) or backticked)
        if value and not re.fullmatch(r"\w*Error", value):
            found[f'"{value}"'] += 1
    for value in BYTE_LITERAL.findall(normative):
        found[f"`{plain(value)}`"] += 1
    return found


def extract(src):
    src = COMMENT.sub("", src)
    headers, members = idl_definitions(src)
    body = LITERAL_BLOCK.sub("", BIKESHED_IDL.sub("", WATTSI_IDL.sub("", src)))
    normative = without_non_normative(body)
    normative_text = plain(normative)
    dfn_keys, exported, external = dfns(src)
    external.update(bikeshed_anchors(src))
    return {
        "IDL definitions and top-level statements": headers,
        "IDL members": members,
        "dfns": dfn_keys,
        "exported dfns": exported,
        "external terms (data-x-href, anchors, link-defaults)": external,
        "ids": ids(body),
        "RFC 2119 keywords (normative text)": Counter(
            k.lower() for k in KEYWORDS.findall(normative_text)),
        "exceptions and throws (normative text)": Counter(EXCEPTION.findall(normative_text)),
        "fired events (normative text)": Counter(EVENT_FIRE.findall(normative_text)),
        "event references": Counter(EVENT_REF.findall(body)),
        "string and byte literals (normative text)": literals(normative),
    }


def show(items, limit=40):
    lines = [f"      {k!r}" + (f" x{n}" if n > 1 else "") for k, n in sorted(items.items())]
    if len(lines) > limit:
        lines = lines[:limit] + [f"      ... {len(lines) - limit} more"]
    return "\n".join(lines)


def check_spec(args):
    if args.files:
        pairs = [(base_path_for(args.base, args.head, f), f) for f in args.files]
    else:
        pairs = changed_spec_files(args.base, args.head)
    if not pairs:
        print("No spec files changed.")
        return 0
    found = False
    for old_path, new_path in pairs:
        old = git_show(args.base, old_path) if old_path else None
        new = git_show(args.head, new_path) if new_path else None
        label = new_path if old_path in (None, new_path) else f"{old_path} => {new_path}"
        label = label or old_path
        if old is None and new is None:
            print(f"error: {label} exists in neither revision (paths are relative to the repo "
                  "root)", file=sys.stderr)
            return 2
        if old is None or new is None:
            print(f"{label}: only in {args.head if old is None else args.base}")
            found = True
            continue
        before, after = extract(old), extract(new)
        report = []
        for category in before:
            removed = before[category] - after[category]
            added = after[category] - before[category]
            if removed or added:
                report.append(f"  {category}:")
                if removed:
                    report.append(f"    removed ({sum(removed.values())}):\n{show(removed)}")
                if added:
                    report.append(f"    added ({sum(added.values())}):\n{show(added)}")
        if report:
            found = True
            print(f"{label}:")
            print("\n".join(report))
        else:
            print(f"{label}: no differences")
    return 1 if found else 0


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


def load_wptreport(path):
    """Return ({(subsuite, test, subtest or None): set of statuses}, run_info)."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        fail(f"can't read {path}: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        fail(f"{path} is not a wptreport (no results list)")
    if not data["results"]:
        fail(f"{path} has no results; did the run fail or match no tests?")
    results = defaultdict(set)
    for test in data["results"]:
        suite, name = test.get("subsuite") or "", test["test"]
        results[(suite, name, None)].add(test.get("status"))
        for sub in test.get("subtests", []):
            results[(suite, name, sub["name"])].add(sub.get("status"))
    return results, data.get("run_info") or {}


def parse_side(text):
    test, sep, sub = text.partition(" | ")
    test = test.strip()
    if not test.startswith("/"):
        fail(f"test path must start with '/': {text!r}")
    return test, (sub if sep else None)


def fmt(key):
    suite, test, sub = key
    return (f"[{suite}] " if suite else "") + test + (f" | {sub}" if sub is not None else "")


def apply_maps(before, maps):
    """Move BEFORE results per the maps. Return (mapped results, errors)."""
    test_maps, sub_maps, errors = {}, {}, []
    for old, new in maps:
        if (old[1] is None) != (new[1] is None):
            errors.append(f"{old[0]} => {new[0]}: give a subtest on both sides, or neither")
        elif old[1] is None:
            test_maps[old[0]] = new[0]
        else:
            sub_maps[old] = new
    used, out, sources, split_from = set(), {}, defaultdict(list), {}

    def map_test(test):
        if test in test_maps:
            used.add(test)
            return test_maps[test]
        path, sep, query = test.partition("?")
        if sep and path in test_maps and "?" not in test_maps[path]:
            used.add(path)
            return f"{test_maps[path]}?{query}"
        return test

    for (suite, test, sub), statuses in before.items():
        if sub is not None and (test, sub) in sub_maps:
            used.add((test, sub))
            new_test, new_sub = sub_maps[(test, sub)]
            split_from.setdefault((suite, new_test), test)
            key = (suite, new_test, new_sub)
        else:
            key = (suite, map_test(test), sub)
        sources[key].append((suite, test, sub))
        out[key] = statuses
    for key, srcs in sources.items():
        if len(srcs) > 1:
            errors.append(f"collision: {fmt(key)} would get the results of "
                          + " and ".join(fmt(s) for s in srcs))
    for source in list(test_maps) + list(sub_maps):
        if source not in used:
            name = source if isinstance(source, str) else " | ".join(source)
            errors.append(f"not in BEFORE: {name}")
    for (suite, new_test), origin in split_from.items():
        if (suite, new_test, None) not in out and (suite, origin, None) in before:
            out[(suite, new_test, None)] = before[(suite, origin, None)]
    return out, errors


def show_statuses(statuses):
    return "/".join(sorted(s or "?" for s in statuses))


def suggestions(lost, added):
    """Suggest maps that would match results only in BEFORE with results only in AFTER."""
    hints, whole = [], set()
    lost_tests, added_tests = defaultdict(set), defaultdict(set)
    for suite, test, sub in lost:
        lost_tests[(suite, test)].add(sub)
    for suite, test, sub in added:
        added_tests[(suite, test)].add(sub)
    for (suite, test), subs in sorted(lost_tests.items()):
        if None in subs:
            for (suite2, test2), subs2 in sorted(added_tests.items()):
                if suite2 == suite and None in subs2 and subs <= subs2:
                    hints.append(f"--map '{test} => {test2}'")
                    whole.add((suite, test))
                    break
    by_name = defaultdict(list)
    for key in added:
        if key[2] is not None:
            by_name[(key[0], key[2])].append(key)
    for suite, test, sub in sorted(lost, key=fmt):
        if sub is None or (suite, test) in whole:
            continue
        candidates = by_name.get((suite, sub), [])
        if len(candidates) == 1:
            hints.append(f"--map '{test} | {sub} => {candidates[0][1]} | {sub}'")
            continue
        new_here = sorted(s for s in added_tests.get((suite, test), ()) if s is not None)
        lost_here = [s for s in lost_tests[(suite, test)] if s is not None]
        if len(new_here) == 1 and len(lost_here) == 1:
            hints.append(f"--map '{test} | {sub} => {test} | {new_here[0]}'  (renamed?)")
    return hints


def check_wpt(args):
    maps = []
    for r in args.map:
        old, sep, new = r.partition(" => ")
        if not sep:
            fail(f"--map expects 'OLD => NEW', got {r!r}")
        old = parse_side(old)
        if old[1] is not None and " | " not in new and not new.strip().startswith("/"):
            new = f"{old[0]} | {new}"  # 'TEST | OLD => NEW' renames a subtest in place.
        maps.append((old, parse_side(new)))
    before_raw, before_info = load_wptreport(args.before)
    after, after_info = load_wptreport(args.after)
    for field in ("product", "browser_channel"):
        old, new = before_info.get(field), after_info.get(field)
        if old and new and old != new:
            fail(f"{field} differs ({old!r} vs {new!r}); compare runs in the same browser")
    before, errors = apply_maps(before_raw, maps)
    if errors:
        print("Bad maps:\n" + "\n".join(f"  {e}" for e in errors), file=sys.stderr)
        return 2
    changed, lost, added = [], [], []
    for key in sorted(before.keys() | after.keys(), key=lambda k: (k[0], k[1], k[2] or "")):
        old, new = before.get(key), after.get(key)
        if old is None:
            added.append(key)
        elif new is None:
            lost.append(key)
        elif old != new:
            changed.append(f"  {fmt(key)}: {show_statuses(old)} -> {show_statuses(new)}")
    if not (changed or lost or added):
        print(f"No differences ({len(after)} results).")
        multi = sum(1 for v in after.values() if len(v) > 1)
        if multi:
            print(f"note: {multi} results have more than one status on both sides (reruns or "
                  "duplicate subtest names)")
        return 0
    if changed:
        print("Changed status:\n" + "\n".join(changed))
    if lost:
        print("Only in BEFORE:\n" + "\n".join(
            f"  {fmt(k)}: {show_statuses(before[k])}" for k in lost))
    if added:
        print("Only in AFTER:\n" + "\n".join(
            f"  {fmt(k)}: {show_statuses(after[k])}" for k in added))
    hints = suggestions(lost, added)
    if hints:
        print("Possible maps (check each before using it):\n"
              + "\n".join(f"  {h}" for h in hints))
    return 1


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
    wpt.add_argument("--map", "--rename", action="append", default=[], metavar="'OLD => NEW'",
                     help="map a renamed or moved test or subtest (repeatable)")
    args = parser.parse_args()
    return check_spec(args) if args.command == "spec" else check_wpt(args)


if __name__ == "__main__":
    sys.exit(main())
