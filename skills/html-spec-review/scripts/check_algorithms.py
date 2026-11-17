#!/usr/bin/env python3
"""
Algorithm Static Analyzer for WHATWG HTML Specification.

Checks algorithm blocks (<div algorithm>) in HTML spec sources or diffs:
1. Rule 4: Variable lifecycle:
   - First declaration must be 'Let <var>x</var> be'.
   - Reassignment must be 'Set <var>x</var> to'.
   - Detects undeclared 'Set <var>x</var> to'.
   - Detects duplicate 'Let <var>x</var> be' declarations in the same scope.
2. Dictionary Type Checking in Algorithms (Untyped Infra Map):
   - Prohibits checking 'If <var>x</var> is a <code>SomeOptions/Init/Config</code>'.
3. Standard Namespace Casing:
   - Flags uppercase 'Namespace' (e.g. <span>MathML Namespace</span>).
4. Multi-interface Method Step Intro Qualification:
   - Flags unqualified intros like "The innerHTML setter steps are:" when methods exist across multiple interfaces.
5. Scope Leaks & Unbound Variables:
   - Detects variables declared with 'Let' inside conditional branches (<ol> depth >= 2) that are referenced in outer scope.
6. Unused Variables:
   - Detects variables declared with 'Let' that are never read/referenced in the algorithm and lack '<var ignore>'.
7. Infra List Iteration Syntax:
   - Flags 'For each <var>x</var> in ...' (Infra requires 'of', not 'in').
8. Assertion & Loop Control Formatting:
   - Flags bare 'Assert:' lacking '<span>Assert</span>:' markup.
   - Flags bare 'continue.' or 'break.' in algorithm steps lacking '<span>continue</span>' / '<span>break</span>' markup.
9. Redundant data-x:
   - Flags '<span data-x="Foo">Foo</span>' where data-x equals inner text.
10. Nested List Paragraph Closure:
    - Flags '<li><p>...<ol>' missing '</p>' before the nested list.
11. Step Terminal Punctuation:
    - Flags leaf algorithm steps missing terminal '.' or ':'.
12. Tag Formatting:
    - Flags newlines immediately preceding '>' in HTML tags.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Set


class AlgorithmIssue:
    def __init__(self, filename: str, line_no: int, rule: str, message: str, snippet: str = ""):
        self.filename = filename
        self.line_no = line_no
        self.rule = rule
        self.message = message
        self.snippet = snippet

    def __str__(self):
        msg = f"{self.filename}:{self.line_no}: [{self.rule}] {self.message}"
        if self.snippet:
            msg += f"\n    Snippet: {self.snippet.strip()}"
        return msg


class AlgorithmAnalyzer:
    def __init__(self):
        self.issues: List[AlgorithmIssue] = []

    def extract_algorithms(self, content: str) -> List[Tuple[int, str]]:
        """Finds all <div algorithm...>...</div> blocks with line numbers."""
        blocks = []
        pattern = re.compile(r'<div\s+algorithm(?:\s+[^>]*)?>(.*?)</div>', re.DOTALL | re.IGNORECASE)
        for match in pattern.finditer(content):
            start_pos = match.start(1)
            line_no = content[:start_pos].count('\n') + 1
            blocks.append((line_no, match.group(1)))
        return blocks

    def check_formatting_and_markup(self, filename: str, content: str):
        """Scans the entire file for formatting, namespace casing, and markup issues."""
        # 1. Namespace casing
        pattern_ns = re.compile(r'<span>(HTML|SVG|MathML|XML|XLink|XMLNS)\s+(Namespace)</span>')
        for match in pattern_ns.finditer(content):
            line_no = content[:match.start()].count('\n') + 1
            self.issues.append(AlgorithmIssue(
                filename, line_no, "NAMESPACE-CASING",
                f"Standard namespace cross-reference uses uppercase '{match.group(2)}'. Standard namespaces must use lowercase 'namespace' (e.g. '<span>{match.group(1)} namespace</span>').",
                match.group(0)
            ))

        # 2. Redundant data-x
        pattern_data_x = re.compile(r'<span\s+data-x="([^"]+)">([^<]+)</span>', re.IGNORECASE)
        for match in pattern_data_x.finditer(content):
            attr_val = match.group(1).strip()
            inner_text = match.group(2).strip()
            if attr_val.lower() == inner_text.lower():
                line_no = content[:match.start()].count('\n') + 1
                self.issues.append(AlgorithmIssue(
                    filename, line_no, "ALGO-REDUNDANT-DATA-X",
                    f"Redundant data-x=\"{attr_val}\" on '<span>{inner_text}</span>'. When cross-reference text matches the definition name, 'data-x' should be omitted.",
                    match.group(0)
                ))

        # 3. Newline before '>' in tag
        pattern_newline_gt = re.compile(r'([^\n<]+)\n\s*>', re.MULTILINE)
        for match in pattern_newline_gt.finditer(content):
            line_no = content[:match.start()].count('\n') + 1
            preceding_chunk = content[max(0, match.start() - 200):match.end()]
            if '<' in preceding_chunk and '>' in match.group(0):
                self.issues.append(AlgorithmIssue(
                    filename, line_no, "ALGO-NO-NEWLINE-BEFORE-GT",
                    "Newline immediately preceding '>' in HTML tag. Place '>' on the same line as the tag name or last attribute.",
                    match.group(0)
                ))

    def check_algorithm_block(self, filename: str, block_start_line: int, block_text: str):
        # Extract declared parameters from the algorithm preamble (before the first <ol>)
        preamble_match = re.search(r'^(.*?)<ol', block_text, re.DOTALL | re.IGNORECASE)
        preamble = preamble_match.group(1) if preamble_match else block_text.split('\n')[0]

        # Parameters passed to algorithm are pre-declared
        declared_vars: Set[str] = set()
        outer_declared_vars: Set[str] = set()
        uncond_decl_depth: Dict[str, int] = {}
        for var_match in re.finditer(r'<var(?:\s+[^>]*)?>(\w+)</var>', preamble):
            v_name = var_match.group(1)
            declared_vars.add(v_name)
            outer_declared_vars.add(v_name)
            uncond_decl_depth[v_name] = 0

        # Check multi-interface qualification on preamble (e.g., innerHTML, setHTMLUnsafe)
        multi_interface_members = ["innerHTML", "outerHTML", "setHTML", "setHTMLUnsafe"]
        for member in multi_interface_members:
            unqualified_intro = re.search(
                rf'\bThe\s+(?:<code[^>]*>)?{member}(?:</code>)?\s+(?:getter|setter|steps)\b',
                preamble,
                re.IGNORECASE
            )
            if unqualified_intro and not re.search(rf'\b(?:Element|ShadowRoot)\b.*?\b{member}\b', preamble):
                self.issues.append(AlgorithmIssue(
                    filename, block_start_line, "ALGO-QUALIFIED-INTRO",
                    f"Algorithm preamble introduces '{member}' steps without qualifying the interface (e.g., 'The Element {member} setter steps are:'). Qualify the interface explicitly when members exist on multiple interfaces.",
                    preamble.strip()
                ))

        # Check for unclosed <p> before nested <ol> or <ul>
        nested_p_pattern = re.compile(r'<li>\s*<p>((?:(?!</p>)(?!</li>).)*?)<(?:ol|ul)\b', re.DOTALL | re.IGNORECASE)
        for match in nested_p_pattern.finditer(block_text):
            line_no = block_start_line + block_text[:match.start()].count('\n')
            snippet = match.group(0).strip()
            if len(snippet) > 80:
                snippet = snippet[:80] + "..."
            self.issues.append(AlgorithmIssue(
                filename, line_no, "ALGO-NESTED-LIST-P",
                "Missing closing '</p>' before nested list in algorithm step. The introducing text must be closed with '</p>' before the sub-list begins.",
                snippet
            ))

        lines = block_text.split('\n')
        list_depth = 0
        ul_depth = 0
        div_note_stack: List[bool] = []
        in_p_note = False
        switch_dl_stack: List[bool] = []
        branch_declared_vars: Dict[str, int] = {}  # var_name -> decl_line_no for depth >= 2
        let_declared_vars: Dict[str, int] = {}     # var_name -> decl_line_no for unused var check
        conditional_inline_depth: Dict[str, int] = {}
        inline_if_depth: Dict[str, int] = {}

        line_offsets: List[int] = []
        curr_offset = 0
        for ln_str in lines:
            line_offsets.append(curr_offset)
            curr_offset += len(ln_str) + 1

        let_decl_pattern = re.compile(
            r'\b(?P<kw>Let|let)\s+(?P<lhs>(?:\(\s*)?<var(?:\s+[^>]*)?>[^<]+</var>'
            r'(?:\s*(?:,\s*(?:and\s+)?|and\s+)<var(?:\s+[^>]*)?>[^<]+</var>)*(?:\s*\))?)\s+(?:be|have)\b'
        )
        for_each_pattern = re.compile(
            r'\b[Ff]or each\b(?:(?!</p>)(?!:).)*?'
            r'(?P<lhs><var(?:\s+[^>]*)?>[^<]+</var>'
            r'(?:\s*(?:→|&rarr;|,\s*|\band\s+)<var(?:\s+[^>]*)?>[^<]+</var>)*)\s+(?:of|in)\b',
            re.DOTALL
        )
        closure_param_pattern = re.compile(
            r'\b(?:the following (?:<[^>]+>[^<]*</[^>]+>\s+)?(?:steps|substeps|algorithm)\b[^.:]*?\bgiven\b(?P<p1>[^:]*):|'
            r'given\b(?P<p2>[^.:]*?)\bbe the following (?:steps|substeps|algorithm)\b)',
            re.IGNORECASE
        )

        binding_spans: List[Tuple[int, int]] = []
        let_matches_by_line: Dict[int, List[Tuple[re.Match, str]]] = {}
        for let_m in let_decl_pattern.finditer(block_text):
            binding_spans.append((let_m.start("lhs"), let_m.end("lhs")))
            start_idx = block_text[:let_m.start()].count('\n')
            p_start = block_text.rfind('<p', 0, let_m.start())
            before = block_text[p_start if p_start != -1 else 0 : let_m.start()]
            let_matches_by_line.setdefault(start_idx, []).append((let_m, before))

        for fe_m in for_each_pattern.finditer(block_text):
            binding_spans.append((fe_m.start("lhs"), fe_m.end("lhs")))

        closure_vars_by_line: Dict[int, List[str]] = {}
        for cp_m in closure_param_pattern.finditer(block_text):
            grp = "p1" if cp_m.group("p1") is not None else "p2"
            binding_spans.append((cp_m.start(grp), cp_m.end(grp)))
            start_idx = block_text[:cp_m.start(grp)].count('\n')
            for vm in re.finditer(r'<var(?:\s+[^>]*)?>(\w+)</var>', cp_m.group(grp)):
                closure_vars_by_line.setdefault(start_idx, []).append(vm.group(1))

        for idx, line in enumerate(lines):
            line_no = block_start_line + idx

            # Update list and block state
            ol_opens = len(re.findall(r'<ol\b', line, re.IGNORECASE))
            ol_closes = len(re.findall(r'</ol>', line, re.IGNORECASE))
            ul_opens = len(re.findall(r'<ul\b', line, re.IGNORECASE))
            ul_closes = len(re.findall(r'</ul>', line, re.IGNORECASE))
            list_depth += ol_opens
            ul_depth += ul_opens
            for div_m in re.finditer(r'<div\b[^>]*>', line, re.IGNORECASE):
                div_note_stack.append(bool(re.search(r'\bclass="(?:note|example|warning)"', div_m.group(0), re.IGNORECASE)))
            if re.search(r'<p\b[^>]*\bclass="(?:note|example|warning)"', line, re.IGNORECASE):
                in_p_note = True
            for dl_m in re.finditer(r'<dl\b[^>]*>', line, re.IGNORECASE):
                switch_dl_stack.append(bool(re.search(r'\bclass="switch"', dl_m.group(0), re.IGNORECASE)))

            for c_var in closure_vars_by_line.get(idx, []):
                declared_vars.add(c_var)

            # --- Check: Infra List Iteration Syntax ('of' not 'in') ---
            if re.search(r'\bFor each\s+(?:<var>\w+</var>|\w+)\s+in\b', line, re.IGNORECASE):
                self.issues.append(AlgorithmIssue(
                    filename, line_no, "ALGO-LIST-OF",
                    "Infra list iteration uses 'of', not 'in' (e.g. 'For each <var>x</var> of <var>list</var>:').",
                    line
                ))

            # --- Check: Assert Formatting ('<span>Assert</span>:') ---
            if re.search(r'(?:<p>|<li>|\s)(?<!<span>)Assert:', line):
                self.issues.append(AlgorithmIssue(
                    filename, line_no, "ALGO-ASSERT-SPAN",
                    "Algorithm assertions must be marked up as '<span>Assert</span>:' (found bare 'Assert:').",
                    line
                ))

            # --- Check: Loop Control Formatting ('<span>continue</span>' / '<span>break</span>') ---
            loop_ctrl_match = re.search(r'(?:<p>|<li>|\bOtherwise,\s+|\bthen\s+)(continue|break)\.', line)
            if not loop_ctrl_match and idx > 0 and re.search(r'(?:\bOtherwise,|\bthen)\s*$', lines[idx - 1]):
                loop_ctrl_match = re.match(r'\s*(continue|break)\.', line)
            if loop_ctrl_match:
                kw = loop_ctrl_match.group(1)
                self.issues.append(AlgorithmIssue(
                    filename, line_no, "ALGO-LOOP-CONTROL-SPAN",
                    f"Infra loop control keyword '{kw}' must be marked up as '<span>{kw}</span>'.",
                    line
                ))

            # --- Check: Untyped Dictionary Checking Anti-pattern ---
            dict_type_check = re.search(
                r'If\s+<var>\w+</var>\s+is\s+(?:an?|the)\s+<code>\w*(?:Options|Init|Config)</code>',
                line,
                re.IGNORECASE
            )
            if dict_type_check:
                self.issues.append(AlgorithmIssue(
                    filename, line_no, "ALGO-DICT-TYPE-CHECK",
                    "Checking dictionary type in algorithm prose. Web IDL dictionaries convert to untyped Infra maps without a type tag, so this only makes sense for telling the members of an IDL union apart. Otherwise, check member existence on the map (e.g., `If options[\"member\"] exists`) instead.",
                    line
                ))

            # Check: Outer scope referencing branch-scoped variable
            in_non_normative = in_p_note or any(div_note_stack)
            if list_depth <= 1 and not in_non_normative and branch_declared_vars:
                l_off = line_offsets[idx]
                for vm in re.finditer(r'<var(?:\s+[^>]*)?>(\w+)</var>', line):
                    b_var = vm.group(1)
                    if b_var in branch_declared_vars and b_var not in outer_declared_vars:
                        b_decl_line = branch_declared_vars[b_var]
                        abs_pos = l_off + vm.start()
                        if b_decl_line < line_no and not any(s <= abs_pos < e for s, e in binding_spans):
                            self.issues.append(AlgorithmIssue(
                                filename, line_no, "ALGO-UNBOUND-VAR-OUTER-SCOPE",
                                f"Variable '<var>{b_var}</var>' was declared with 'Let' inside a conditional branch at line {b_decl_line}, but is referenced at outer scope without being declared in the outer scope. It will be unbound on alternative execution paths. Initialize with 'Let <var>{b_var}</var> be null' in outer scope before branching.",
                                line
                            ))
                            del branch_declared_vars[b_var]

            # --- Rule 4: Variable lifecycle ('Let' vs. 'Set') ---
            for let_m, before in let_matches_by_line.get(idx, []):
                is_capital_let = let_m.group("kw") == "Let"
                lhs = let_m.group("lhs")
                last_dot = before.rfind('.')
                clause = before[last_dot + 1:] if last_dot != -1 else before
                is_cond_if = (not is_capital_let) and bool(re.search(r'\b(?:If|if|unless|in which case)\b', clause))
                is_otherwise = (not is_capital_let) and bool(re.search(r'\b(?:Otherwise|otherwise)\b', clause))
                is_uncond_otherwise = is_otherwise and not bool(re.search(r'\b(?:Otherwise|otherwise),\s+if\b', clause))

                for m in re.finditer(r'<var(\s+[^>]*)?>(\w+)</var>', lhs):
                    attrs = m.group(1) or ""
                    var_name = m.group(2)
                    is_ignored = bool(re.search(r'\bignore\b', attrs))

                    skip_duplicate = (
                        var_name in conditional_inline_depth
                        and list_depth > conditional_inline_depth[var_name]
                        and uncond_decl_depth.get(var_name, 999) > conditional_inline_depth[var_name]
                    )
                    if is_capital_let and var_name in declared_vars and not skip_duplicate:
                        self.issues.append(AlgorithmIssue(
                            filename, line_no, "ALGO-DUPLICATE-LET",
                            f"Variable '<var>{var_name}</var>' is re-declared with 'Let'. Use 'Set <var>{var_name}</var> to' for reassignments, or rename if a distinct variable was intended.",
                            line
                        ))
                    declared_vars.add(var_name)

                    if is_cond_if:
                        inline_if_depth[var_name] = list_depth
                        conditional_inline_depth.setdefault(var_name, list_depth)
                    elif is_otherwise and not (is_uncond_otherwise and inline_if_depth.get(var_name) == list_depth):
                        conditional_inline_depth.setdefault(var_name, list_depth)
                    else:
                        uncond_decl_depth[var_name] = min(uncond_decl_depth.get(var_name, list_depth), list_depth)
                        conditional_inline_depth.pop(var_name, None)
                        if list_depth <= 1:
                            outer_declared_vars.add(var_name)
                        elif var_name not in outer_declared_vars:
                            branch_declared_vars[var_name] = line_no

                    if not is_ignored:
                        let_declared_vars[var_name] = line_no


            # Match: "Set <var>x</var> to"
            set_matches = re.finditer(r'\bSet\s+<var>(\w+)</var>\s+to\b', line)
            for m in set_matches:
                var_name = m.group(1)
                if var_name not in declared_vars:
                    self.issues.append(AlgorithmIssue(
                        filename, line_no, "ALGO-UNDECLARED-SET",
                        f"Variable '<var>{var_name}</var>' is mutated with 'Set' before being declared with 'Let'. Every variable must first be introduced via 'Let <var>{var_name}</var> be'.",
                        line
                    ))
                    declared_vars.add(var_name)

            # Terminal punctuation check for leaf steps (<li><p>...</p></li>) in <ol>
            leaf_step_match = ul_depth == 0 and re.search(r'<li>\s*<p>(.*?)</p>\s*</li>', line)
            if leaf_step_match:
                inner_text = leaf_step_match.group(1)
                clean_text = re.sub(r'<[^>]+>', '', inner_text).strip()
                if clean_text and not clean_text.endswith(('.', ':', '?', '!')):
                    self.issues.append(AlgorithmIssue(
                        filename, line_no, "ALGO-STEP-PUNCTUATION",
                        "Algorithm step is missing terminal punctuation (expected '.' or ':').",
                        line
                    ))

            list_depth -= ol_closes
            ul_depth = max(0, ul_depth - ul_closes)
            for _ in re.findall(r'</div>', line, re.IGNORECASE):
                if div_note_stack:
                    div_note_stack.pop()
            if in_p_note and re.search(r'</p>', line, re.IGNORECASE):
                in_p_note = False
            if any(switch_dl_stack) and re.search(r'</dd>', line, re.IGNORECASE):
                branch_declared_vars.clear()
            for _ in re.findall(r'</dl>', line, re.IGNORECASE):
                if switch_dl_stack:
                    switch_dl_stack.pop()

        # --- Check: Unused Variables ---
        for var_name, decl_line in let_declared_vars.items():
            occurrences = len(re.findall(rf'<var(?:\s+[^>]*)?>\s*{re.escape(var_name)}\s*</var>', block_text))
            if occurrences <= 1:
                self.issues.append(AlgorithmIssue(
                    filename, decl_line, "ALGO-UNUSED-VAR",
                    f"Variable '<var>{var_name}</var>' is declared with 'Let' but never referenced again in this algorithm. Remove it if unneeded, or mark with '<var ignore>{var_name}</var>' if intentionally unused.",
                    f"Let <var>{var_name}</var> be..."
                ))

    def analyze_file(self, filepath: Path) -> List[AlgorithmIssue]:
        content = filepath.read_text(encoding='utf-8', errors='replace')

        # Check global file-level rules (like namespace casing, formatting)
        self.check_formatting_and_markup(str(filepath), content)

        # Check algorithm blocks
        algos = self.extract_algorithms(content)
        for line_no, block_text in algos:
            self.check_algorithm_block(str(filepath), line_no, block_text)

        return self.issues


def main():
    parser = argparse.ArgumentParser(description="Lint algorithm blocks in WHATWG HTML specifications.")
    parser.add_argument("files", nargs="+", type=Path, help="HTML source files to inspect")
    parser.add_argument("--fail-on-issue", action="store_true", default=True, help="Exit with non-zero status if issues are found")
    args = parser.parse_args()

    analyzer = AlgorithmAnalyzer()
    total_issues = 0

    for f in args.files:
        if not f.is_file():
            continue
        file_issues = analyzer.analyze_file(f)
        total_issues += len(file_issues)

    if total_issues > 0:
        print(f"Found {total_issues} Algorithm issue(s):")
        for issue in analyzer.issues:
            print(f"  {issue}")
        if args.fail_on_issue:
            sys.exit(1)
    else:
        print("Algorithm Analyzer: All checks passed. No issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
