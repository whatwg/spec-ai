---
name: html-spec-review
description: >-
  Read before reading, drafting, editing, or reviewing text in the WHATWG HTML standard: `whatwg/html`'s `source` file, a PR against it, or new spec prose, algorithms, IDL, or examples for it. Triggers on: "HTML spec", "HTML standard", "whatwg/html", reading/editing `source`, "split the source", reviewing a whatwg/html PR.
---

# Agent Skill: HTML Specification Writing and Review Guide

> **Note on Extended Guidelines:**
> For broader guidance on substantive architectural judgment (including threading models, backwards compatibility, API design consistency, and state encapsulation) across W3C, WHATWG, and WICG specifications, as well as additional Bikeshed/Wattsi syntax rules, please refer to the external [spec-writing-skill repository](https://github.com/domfarolino/spec-writing-skill).

This skill provides the official guidelines, prose style conventions, algorithmic requirements, structural review principles, and tooling for reading, writing, editing, and reviewing the WHATWG HTML standard.

House-style rules (markup, dfns, preambles, IDL member prose, tasks/events, promises, conformance language, vocabulary) are catalogued with stable rule IDs in [`html-style-guide.md`](html-style-guide.md) (in this skill directory); §16 condenses the most common ones.

Refer to this skill when authoring spec text, reviewing pull requests, or conducting rigorous self-reviews to prevent common failure modes that pass automated syntax checks (Wattsi/Bikeshed) but introduce critical logical, security, or architectural regressions.

### Working with `whatwg/html`'s `source` File (`split_html.py`)

`whatwg/html`'s `source` file is over 160,000 lines, so reading or editing it whole is slow and error-prone. Before examining or editing `source`, use `scripts/split_html.py` (bundled in this skill directory) to split `source` at each `<h2` tag into `split_source/` (`00_start.html`, `01_introduction.html`, etc.):

1. **Split**: `python3 <skill-dir>/scripts/split_html.py split <path/to/html/source>`
2. **Read, Edit & Analyze**: Use standard file/search tools (`view_file`/`Read`, `replace_file_content`/`Edit`, `grep_search`/`Grep`) and the static analyzers in `scripts/` directly on the relevant section file(s) in `split_source/` (e.g., `10_webappapis.html`).
3. **Concatenate (if edited)**: `python3 <skill-dir>/scripts/split_html.py concat <path/to/html/source>`
4. **Clean up**: `split_source/` is scratch state and is not gitignored in `whatwg/html`. Always concatenate before building, diffing, or committing, then delete `rm -r <path/to/html>/split_source` and verify `git status`.

---

## 1. Web IDL Rules & Cross-References

### 1.1. Cross-references inside `<pre class="idl">`
- In Web IDL blocks (`<pre class="idl">`), cross-references MUST use `<span>`, NEVER `<code>`.
- Web IDL syntax is already preformatted as code. Using `<code>` creates nested markup that violates WHATWG style and triggers reviewer objections.
  - *Correct*: `static <span>Document</span> <span data-x="dom-parseHTMLUnsafe">parseHTMLUnsafe</span>((<span>TrustedHTML</span> or DOMString) html, optional (<span>ParseHTMLUnsafeOptions</span> or <span>TrustedParserOptions</span>) options = {});`
  - *Incorrect*: `static <span>Document</span> ... optional (<code data-x="tt-trustedparseroptions">TrustedParserOptions</code>) options = {});`

### 1.2. Dictionaries Become Untyped Infra Maps (No "is a Dictionary" in Algorithms)
- Once an IDL dictionary argument passes the Web IDL conversion boundary into algorithm prose, it is converted into an **Infra ordered map** of strings to values.
- **It does NOT retain any type tag, branding, or record of which dictionary type it came from.**
- **Anti-Pattern**:
  - *Never write*: `If <var>options</var> is a <code>SetHTMLUnsafeOptions</code>:`
  - *Never write*: `If <var>options</var> is a dictionary:`
- **Correct Pattern**:
  - Check member existence on the map: `If <var>options</var>["<code data-x="dom-SetHTMLUnsafeOptions-runScripts">runScripts</code>"] <span data-x="map exists">exists</span>:` or use map fallback: `<var>options</var>["runScripts"] <span data-x="map with default">with default</span> false`.
  - Only platform objects / interfaces (e.g. `TrustedParserOptions`, `Node`, `Element`) retain type identity and can be checked with `If <var>x</var> is an <span>InterfaceName</span>:`.

### 1.3. Web IDL Optional Arguments & Dictionary Defaults
- If an optional dictionary parameter has **no required members**, it MUST specify `= {}` in its IDL declaration:
  - *Correct*: `optional ParseHTMLOptions options = {};`
  - *Incorrect*: `optional ParseHTMLOptions options;`
- **Variadic Parameters**:
  - A trailing variadic argument (`any... arguments`) forces the preceding parameter to be optional in Web IDL.

### 1.4. Formatting IDL Members
- Every attribute, constant, and operation must be on its own line.
- Do not wrap parameter names or type names in `<var>` tags within IDL blocks.

---

## 2. Algorithms, Variable Lifecycle & Scope

### 2.1. Variable Lifecycle: Strict "Let" vs. "Set"
- **First declaration**: MUST use **"Let `<var>x</var>` be `<var>y</var>`"**.
- **Reassignment / Mutation**: MUST use **"Set `<var>x</var>` to `<var>y</var>`"**.
- **Failure Modes to Catch**:
  1. Using `Set <var>x</var> to ...` when `<var>x</var>` was never declared with `Let`.
  2. Re-declaring a variable with `Let <var>x</var> be ...` in the same algorithm scope.
  3. **Re-using a name for a different object**: a second `Let <var>x</var> be ...` for a different value in the same algorithm (even in exclusive branches) — rename one. A fresh `Let` inside a separate closure (fetch callback, queued task) is a new scope and is fine.
  - `Let <var>x</var> be null` before an `If/Otherwise` that assigns `<var>x</var>` in every branch is **not** a defect: variables declared inside a nested `<ol>` are not visible outside it, so hoisting with a null initial value is the required idiom (`VAR-LET-SET`).

### 2.2. Dangling Antecedents & Variable Reassignment
- If a variable is mutated or reassigned, never refer to "the original `<var>x</var>`" in later steps unless explicitly preserved:
  - *Correct*: `Let <var>originalContext</var> be <var>context</var>.` ... `Set <var>context</var> to ...` ... `Use <var>originalContext</var>.`
  - *Incorrect*: Reassigning `<var>context</var>` and then later referring to "the original context".

### 2.3. Algorithm Container & Scoping
- Wrap every algorithm in `<div algorithm>`. The preamble (name, arguments, return type) goes inside the `<div>`. Do not indent algorithm container contents.
- Multi-algorithm scopes can use `<div var-scope>`. If a variable is only referenced once, mark it `<var ignore>x</var>`.
- Use the "initially" pattern: "...initially null", "...initially false", "...initially the empty list « »".

### 2.4. Phrasing Conventions
- Use standard Infra conjugation: `the result of <span data-x="...">getting the popcorn</span> given <var>args</var>` (not "the result of calling get the popcorn with...").
- Assertions: `<span>Assert</span>: <var>x</var> is non-null.` (Always wrap in `<span>Assert</span>:`, never bare `Assert:`).
- Context: `<span>this</span>` (never bare "this").

### 2.5. Scope Leaks & Branch-Bound Variables (`ALGO-UNBOUND-VAR-OUTER-SCOPE`)
- **Blocker Bug**: Declaring a variable with `Let <var>x</var> be` inside a nested conditional sub-list (`<ol>`) and subsequently reading `<var>x</var>` at the outer algorithm scope or in an `Otherwise` branch.
  - On any execution path where the conditional branch does not run, `<var>x</var>` is completely unbound and dereferencing it creates an invalid specification state.
- **Rule**:
  - If a variable is read or tested outside a branch, it MUST be initialized at the outer algorithm scope *before* the branching block:
    ```html
    <!-- Correct Pattern -->
    <li><p>Let <var>fetchTimingInfo</var> be null.</p></li>
    <li><p>If <var>navigationParams</var>'s fetch controller is not null:</p>
     <ol>
      <li><p>Set <var>fetchTimingInfo</var> to the result of extracting the full timing info...</p></li>
     </ol>
    </li>
    ...
    <li><p>If <var>fetchTimingInfo</var> is not null:</p>...</li>
    ```

### 2.6. Unused Variables & Argument Renaming (`ALGO-UNUSED-VAR`)
- Every variable introduced with `Let <var>x</var> be` must be referenced in subsequent steps.
- **Refactoring Hazard**:
  - When refactoring algorithm signatures or renaming parameters (e.g., replacing `context` with `target`), authors frequently introduce the new parameter but leave dangling references to the old name or create dead intermediate bindings.
  - Always audit the entire algorithm to ensure the old variable name is not referenced and the new variable is actually consumed.
  - If a destructured tuple member or parameter is intentionally unused, mark it with `<var ignore>name</var>`.

### 2.7. Infra List Iteration Syntax (`ALGO-LIST-OF`)
- In Infra, iterating over a list, set, or map always uses **"of"**, NEVER "in":
  - *Correct*: `For each <var>node</var> of <var>children</var>:`
  - *Incorrect*: `For each <var>node</var> in <var>children</var>:`

### 2.8. Redundant `data-x` Elimination (`ALGO-REDUNDANT-DATA-X`)
- Wattsi automatically links cross-references when the inner text matches the term definition name (case-insensitively).
- Writing `<span data-x="Foo">Foo</span>` or `<span data-x="set and filter HTML">set and filter HTML</span>` is redundant.
- Omit `data-x` when the text is identical to the target concept: `<span>set and filter HTML</span>`. Keep `data-x` only when the visible text differs from the definition key (e.g. inflections, plurals, or abbreviations).

---

## 3. State Mutation, Aliasing & Temporal Sequencing

### 3.1. The Shallow Clone Trap (`[=map/clone=]`)
- In Infra, `[=map/clone=]` and `[=list/clone=]` are **strictly shallow**. Keys and values are copied into a new collection, but nested maps, lists, sets, and objects are **referenced, not copied**.
- If a cloned dictionary/map contains nested maps (e.g. `SanitizerConfig`'s `elements`, `attributes`, `removeElements`), running in-place mutative algorithms (such as removing entries or modifying nested lists) **directly mutates the original object's internal data structures!**
- **Review Rule**:
  - If a spec guarantees immutability or script-isolation, verify whether values inside the map are mutable objects or nested maps.
  - If nested mutable collections exist, the algorithm must deep-clone, recursively copy, or canonicalize via fresh throwaway instances rather than relying on `[=map/clone=]`.
- **Platform Object Encapsulation**:
  - Never return an internal platform map/dictionary directly by reference from a getter or `[NewObject]` method if script can observe mutations or if subsequent calls expect immutability.

### 3.2. Temporal State Snapshotting (Evaluate Before Tree/Stack Mutation)
- Algorithms that query dynamic parser or DOM state (e.g. `adjusted insertion location`, `current node`, `stack of open elements`, `insertion parent`) MUST capture that state **before** executing steps that mutate the tree or stack.
- **Classic Regression**:
  - Re-evaluating `adjusted insertion location` *after* calling `insert a foreign element` or pushing an element to the stack causes `scope` to resolve to the *new element's own contents* (breaking `<template for>` patching).
- **Review Rule**:
  - Whenever an algorithm inspects tree context, check whether any preceding step in the same sequence added, reparented, or removed elements.
  - If so, the location/parent MUST be captured into a local variable *before* the insertion:
    `Let <var>adjustedInsertionLocation</var> be the <span>appropriate place for inserting a node</span>.`
    `Let <var>scope</var> be <var>adjustedInsertionLocation</var>'s target parent.`
    `Insert the element...`

### 3.3. Post-Construction Local Mutation Bug
- When constructing an object or parser whose initialization takes parameters (e.g., `Create a new HTML parser whose scripting mode is <var>scriptingMode</var>`):
  - Any subsequent mutation of the local variable `<var>scriptingMode</var>` does **NOT** update the parser's stored mode!
- **Review Rule**:
  - Calculate all configuration flags and modes **before** constructing the object, OR explicitly update the object's internal slot afterward.

### 3.4. Atomic Validation before Destructive Mutation
- APIs that perform destructive DOM operations (such as clearing an element's children or removing a node from its parent) MUST perform all option validation, sanitization parsing, and dependency construction **before** mutating the DOM.
- If option validation or parser construction fails and throws an exception, the DOM must remain pristine and unmutated. Never clear or detach nodes before validation can throw!

### 3.5. Pre-Initialization State Access (Unborn Object Capabilities)
- **Failure Mode**: Inspecting permissions policy, environment settings, or cross-origin capabilities on an object *before* its child components, document, or global have been instantiated and linked.
  - *Example*: Checking `window's relevant settings object's cross-origin isolated capability` before `window` has an associated `Document`. In a newly created Window, its associated document is unset; in a reused `about:blank`, it resolves to the old document's policy rather than the new response's permissions policy!
- **Review Rule**:
  - Audit the lifecycle of objects passed to algorithms. Never query capability getters or policy algorithms on an object until all associated subordinates (`window.document`, `intendedParent`, execution context) are fully linked.
  - If a timestamp or state must be captured early, capture the raw/uncoarsened value (e.g. `unsafeSharedCurrentTime`), and coarsen or convert it *after* the document and its permissions policy are bound.

### 3.6. Fallback & Null Path Auditing on Previously Unconditional Steps
- **Failure Mode**: When turning a previously unconditional algorithm step into a conditional branch (e.g. `If <var>controller</var> is not null:`), the `Otherwise` path is frequently neglected or assumes all inputs are regular network fetches.
  - *Example*: Restricting navigation timing entry creation to when `navigationParams's fetch controller is not null` causes timing entries to silently disappear for `srcdoc` documents, `javascript:` URLs, UA error pages, and `multipart/x-mixed-replace` continuations.
- **Review Rule**:
  - Whenever an algorithm step is guarded by a non-null condition, explicitly audit and document the behavior for every possible non-fetch or null-controller scenario:
    1. `about:srcdoc` and `about:blank` navigations
    2. `javascript:` URL documents
    3. UA-generated error pages
    4. Navigations supplied with synthetic responses (`<object>`, `<embed>`, multipart)
    5. In-flight aborted traversals
  - Ensure the fallback branch creates synthetic fallback structs or documents the intentional omission with matching WPT tests.

---

## 4. HTML Parser, Tree Construction & Edge Cases

### 4.1. The Adoption Agency Algorithm (AAA) Audit
- The Adoption Agency Algorithm (AAA) is the premier source of parser-level corner cases. AAA clones formatting elements, creates elements directly from tokens, moves nodes, and reparents subtrees.
- **Review Checklist for Any Tree-Builder / Sanitization Modification**:
  1. *Token creation bypass*: Does AAA create elements from tokens without going through your new insertion/sanitization algorithm? (Audit AAA steps 4.13.8 and 4.18).
  2. *Parentless `lastNode`*: If nodes are removed or rejected during AAA, can `lastNode` have no parent? Verify `lastNode`'s parent is non-null before calling `remove`, and reset `lastNode` to null.
  3. *Self-ancestor reparenting loops*: Ensure AAA reparenting steps do not attempt to append an element to itself when an inner loop has already moved it.

### 4.2. Speculative Parsing & Preload Scanner Integrity
- Tree-builder behaviors (such as script blocking, sanitization, or custom element delays) must account for speculative HTML parsing.
- If a node or attribute would be removed or blocked by the tree builder, speculative parsing must either sanitize mock elements or be suppressed for that subtree. Otherwise, speculative fetches (e.g. for `<img>`, `<script>`, or `<base>`) will execute over the network before the tree builder removes them.

### 4.3. Direct Root & Body Appends / Attribute Merging
- Not all elements enter the tree through standard element insertion:
  - Initial `<html>` and `<body>` elements may be created and appended through dedicated root creation steps.
  - Duplicate `<html>` and `<body>` start tags in markup **merge attributes directly** into existing open elements without running generic element insertion.
- When adding tree-builder policies (e.g. sanitization, CSP hooks), explicitly audit attribute merging and root creation steps.

### 4.4. `<template>` Target Redirection
- Setting content on an `HTMLTemplateElement` (`innerHTML`, `setHTML`, `streamHTML`, positional insertion) MUST target the template's **`template contents` (`content`)**, NOT the `HTMLTemplateElement` itself.
- **Review Rule**:
  - Use a centralized helper (e.g. "appropriate place for inserting a node" or "HTML insertion target") rather than ad-hoc inline checks at individual API call sites to avoid regressions across sibling methods.

---

## 5. Parallel Call Site Exhaustiveness & Internal Helpers

### 5.1. Exhaustive Sibling Call Site Audit
- When modifying the signature, parameters, or return type of an internal parsing or serialization algorithm (e.g. `fragment parsing algorithm steps`, `set and filter HTML`), you MUST audit **every parallel caller across HTML, DOM, and DOM Parsing specifications**:
  - `Element.prototype.innerHTML` setter
  - `ShadowRoot.prototype.innerHTML` setter
  - `Element.prototype.outerHTML` setter
  - `Element.prototype.insertAdjacentHTML()`
  - `Range.prototype.createContextualFragment()`
  - `DOMParser.prototype.parseFromString()`
  - `Document.parseHTML()` / `Document.parseHTMLUnsafe()`
  - `Element.prototype.setHTML()` / `Element.prototype.setHTMLUnsafe()`
  - `ShadowRoot.prototype.setHTMLUnsafe()`
  - Streaming variants (`streamHTML`, `streamPrependHTML`, etc.)
- A change to `fragment parsing algorithm steps` that only updates `setHTML()` will silently leave `ShadowRoot.innerHTML` or `createContextualFragment()` broken or passing stale arguments.

### 5.2. No Masking Defaults on Core Internal Algorithms
- **Do not add optional parameters with default values to internal abstract algorithms merely to avoid updating existing call sites.**
  - *Example*: Adding `an optional fragment parser mode mode (default Normal)` to `fragment parsing algorithm steps`.
- Defaults silently mask forgotten call sites. Legacy callers (like `outerHTML` or `createContextualFragment`) will pick up the default without explicit author consideration.
- **Rule**: Make parameters mandatory on internal algorithms during refactoring so that omitted call sites fail loudly during spec review and compilation.

### 5.3. Internal Helper Contract & Parameter Typing
- Ensure that helper algorithms and their callers agree on parameter types and order:
  - If a helper expects `(target, html, options, mode)`, do not pass `(html, this, options, safeBoolean)` at call sites.
  - Avoid conflating enums (`Legacy`, `Unsafe`, `Normal`) with boolean flags (`safe`).

---

## 6. Cross-Spec Layering, Sinks & CSP Reporting

### 6.1. No Fabricated or Synthetic Sinks
- Sink names passed to security violation algorithms (Content Security Policy, Trusted Types) MUST correspond to **real, JavaScript-observable API entry points**:
  - *Valid sinks*: `"Element innerHTML"`, `"ShadowRoot innerHTML"`, `"Document parseHTMLUnsafe"`, `"Range createContextualFragment"`.
  - *Invalid synthetic sinks*: `"Sanitizer"`, `"HTMLParser"`, `"FragmentParser"`.
- Passing synthetic sink names causes sample reports and developer console errors to report nonsensical entries like `"Sanitizer|"`.

### 6.2. Cross-Spec Sentinels vs. String Literals
- If a dependency specification defines a sentinel value (e.g., the `Stream` sentinel in Trusted Types), pass the actual sentinel object/record across the spec boundary.
- Do NOT pass string literals like `"Stream"`. String literals trigger string conversion paths (e.g. running `createHTML` on the word "Stream") instead of selecting sentinel dispatch branches.

### 6.3. Layering & Clean Inversion
- Core HTML tree-construction and fragment-parsing algorithms should remain agnostic of external subsystems where possible. Subsystems (such as CSP) should define integration hooks into HTML rather than HTML reaching directly into subsystem algorithms.

---

## 7. Formatting and Markup Rules

### 7.1. Line Wrapping
- Wrap lines at **100 characters** (`SRC-WRAP-100`). When reviewing, flag only prose that is clearly unwrapped (a line well over 100, or a whole paragraph on one line); a 1–2 character overrun or an under-filled line is not a review comment.
- Attributes or their values can contain newlines to respect this.
- Do not insert newlines between inline tag names and text if it inserts unwanted spaces (e.g., `<i data-x="...">\ntext</i>` is incorrect).
- After editing, run [`specfmt`](https://github.com/domfarolino/specfmt) in the `whatwg/html` checkout before committing (`-f` if the changes are uncommitted). It reflows only the lines changed on the current branch, and catches wrapping that the linter doesn't.

### 7.2. Lists (`<ol>`, `<ul>`, `<li>`, `<dt>`, `<dd>`)
- Every `<li>` must wrap its text content in a `<p>` (except in `<ul class="brief">`).
- Format as `<li><p>Text</p></li>` on the same line if possible, or indent nested blocks.
- Separate consecutive list items with a blank line. Do not put blank lines at the list's absolute start/end, nor just inside a `<div class="note">`, `<div class="example">`, or multi-line `<li>` (`SRC-LI-P`).
- A multi-line `<li>` indents its child `<p>`s one space deeper than the `<li>` (`SRC-INDENT-BLOCK`).
- `SRC-LI-P` / `SRC-END-TAGS`: `<li><p>…</p></li>` even for one-liners; all end tags explicit in touched lines.
- Indentation uses a single space per block nesting level:
  - For top-level lists, `<ol>` is indented by 2 spaces, and `<li>` is indented by 3 spaces.
  - Wrapped lines within `<li><p>...</p></li>` match the indentation of the line (3 spaces for top-level list items).
  - Nested block elements (`<p>`, `<ul>`, `<ol>`) starting on their own line inside `<li>` are indented by 1 space relative to the parent `<li>`.
- **Brief Lists (`<ul class="brief">`)**: Use for simple/short lists. Items must **not** wrap content in a `<p>` tag. No blank lines between items.
- **Switch Lists (`<dl class="switch">`)**: Use for complex branch logic. Sibling `<dt>` conditions map to a single `<dd>` consequence/action.

### 7.3. Tags and Quotation
- Always use double quotes for attributes.
- Never omit end tags (always close all `<p>`, `<li>`, `<dt>`, and `<dd>` tags) (`SRC-END-TAGS`). Fix a missing one in touched lines; leave the Legacy unclosed `<dt>`/`<dd>`s of old definition lists alone.
- No newline before `>` in closing tags: write `>attribute</code>` not `\n>attribute</code>`.

---

## 8. Prose Style, Grammar and Conventions

### 8.1. Conditional Statements
- **Inline consequence**: Use the full **"If [condition], then [consequence]"** structure (e.g., "If <var>x</var> is true, **then** return.").
- **Block/Sub-list consequence**: Omit "**then**" and end with a colon (e.g., "If <var>x</var> is true:" followed by a nested list).
- **Multiple conditions (more than two)**: Use **"If any of the following are true:"** or **"If all of the following are true:"**, followed by a `<ul>` containing conditions, with the consequence in a subsequent `<p>` starting with "then...". Do not chain multiple "or" clauses in inline prose.

### 8.2. Branching & Fallbacks ("otherwise")
- **Subsequent branches**: "Otherwise, if [condition], [consequence]." (No "then" keyword).
- **Fallback branch**: Use a simple "**Otherwise, [consequence]**" or "**Otherwise:**". Do not repeat negative conditions from previous branches.
- **Inline Ternary**: Use the format: `[value1] if [condition]; otherwise [value2]` (note the semicolon before `otherwise`).

### 8.3. Antonym and Negative Concept Linking
- When setting boolean flags or checking disabled states, link to the explicit negative definition rather than linking the negative phrase to the positive definition.
- *Example*: `concept-n-script` defines "scripting is enabled", whereas `concept-n-noscript` defines "scripting is disabled".
  - *Correct*: `Set <var>parser</var>'s <span>parser scripting disabled</span> to true if <span data-x="concept-n-noscript">scripting is disabled</span> for <var>document</var>; otherwise false.`

### 8.4. Enums, Actions, and State Values
- **Web IDL Enums**: Defined as `"butt"`. Reference in prose as `"<code data-x="">butt</code>"`.
- **Defined Actions**: Defined as `<dfn data-x="...">"Remove"</dfn>`. Reference as `<span data-x="...">"Remove"</span>`.
- **States & Modes**: Capitalize exactly as defined in their definition (e.g., `<span>Disabled</span>`).

### 8.5. Standard Namespaces Casing
- All standard namespace cross-references use lowercase `"namespace"`:
  - `<span>HTML namespace</span>`
  - `<span>SVG namespace</span>`
  - `<span>MathML namespace</span>` (never `<span>MathML Namespace</span>`)
  - `<span>XML namespace</span>`, `<span>XLink namespace</span>`, `<span>XMLNS namespace</span>`

### 8.6. General Conventions
- Omit "the string" prefix before string literals (e.g., "match for `<code data-x="">text/html</code>`").
- Navigation & Exit: Use "return" or "return <var>value</var>" for entire algorithms; "abort these steps" for sub-steps or parallel sequences.
- Use American English (`behavior`, `color`) and Oxford commas in listings.

### 8.7. Grammatical Conjunctions on Item Removal
- When removing an item from a comma-separated list of items in prose (e.g. deleting an obsolete property or concept from an enumeration like "The encoding, mode, custom element registry, and allow declarative shadow roots"):
  - Verify that the coordinating conjunction ("and" or "or") is preserved and correctly placed before the new final item.
  - Deleting the trailing item without moving "and" to the preceding item creates an ungrammatical sentence (e.g. "The encoding, mode, custom element registry.").

---

## 9. Infra Data Structures and Iteration

- **Lists**:
  - Literal: `Let <var>list</var> be « "a", "b" ».`
  - Destructuring: `Let « <var>a</var>, <var>b</var> » be <var>list</var>.`
  - Access & Size: Zero-based index `list[0]` and `size` (never `length` or `count`).
  - Verbs: `append`, `extend A with B`, `prepend`, `replace ... within ...`, `insert ... into ... before [index]`, `remove ... from ...`, `contains`, `is empty`.
- **Maps**:
  - Literal: `Let <var>map</var> be «[ "a" → 1 ]».` (right arrow `→`).
  - Access & Default: `map["key"]` or `map["key"] with default 0`. Check existence with `exists`.
  - Verbs: `set map[key] to value`, `remove map[key]`, `clear map`, `get the keys`, `get the values`, `map's size`.
- **Structs & Tuples**:
  - Struct: `Let <var>x</var> be a struct whose property is value.`
  - Tuple: `Let <var>x</var> be (value1, value2).` Access by field name or index (`x[0]`).
- **Loops**:
  - For each: `For each <var>item</var> of <var>items</var>:` (use **of**, not in).
  - Map entries: `For each <var>key</var> → <var>value</var> of <var>map</var>:`
  - While: `While [condition]:`. Control with `continue` and `break`.

---

## 10. Writing domintro Blocks, Notes & Warnings

`<dl class="domintro">` provides developer-friendly Web IDL explanations (IDL and normative steps are hidden in the Developer's Edition).

### 10.1. Structure & Placement
- Position directly after the Web IDL block (`<pre class="idl">`) and before implementation algorithms. Do not mark it with `w-nodev`.
- **Signatures (`<dt>`)**: Describe JS usage. Use `<var>` for placeholder names. Register first introductions with `<span subdfn data-x="dom-IDL-name">`.
- **Explanation (`<dd>`)**: Explain behavior concisely using present-tense verbs ("Returns...", "Updates...", "Throws..."). Never use normative RFC2119 keywords ("must").

### 10.2. Exception Parity & Synchronization
- Document every `DOMException` that an API can throw explicitly in the `domintro` `<dd>` block (e.g., `Throws a "NotSupportedError" DOMException if...`).
- **Synchronization Rule**:
  - If normative algorithm steps change so that an exception is no longer thrown (e.g., falling through or returning null), **any domintro sentence promising that exception becomes false and must be removed**.
  - If normative steps add a new throwing condition, the domintro must document it.

### 10.3. Stale Warning Boxes
- Check existing `<p class="warning">` and `<p class="note">` blocks in the modified section.
- If a warning claims a method "performs no sanitization", and the PR introduces default policy or parser sanitization capabilities, the warning must be updated or qualified to prevent outdated information from misleading developers.

### 10.4. Qualified Interface Names in Method Intros
- When defining method steps for attributes or methods implemented across multiple interfaces (e.g. `innerHTML` on `Element` and `ShadowRoot`), qualify the intro explicitly:
  - *Correct*: `"The Element innerHTML setter steps are:"`
  - *Incorrect*: `"The innerHTML setter steps are:"` (ambiguous with ShadowRoot).

---

## 11. Developer's Edition (w-dev / w-nodev)

The HTML specification compiles into a **Living Standard** and a **Developer's Edition**.

- **What to Keep**: High-level overviews, descriptive introductions, authoring guidelines, examples (`<div class="example">`), and `<dl class="domintro">` blocks.
- **What to Omit**: Web IDL algorithmic rules, parser state machines, and implementer-only tree manipulations.
- **Attributes**:
  - Use `w-nodev` to exclude implementer-only content from Developer's Edition.
  - Do not nest `w-dev` or `w-nodev` attributes inside an ancestor already marked `w-nodev`.
  - Use `subdfn` on `<span data-x="...">` when defining terms whose primary `<dfn>` is omitted with `w-nodev`.

---

## 12. PR Scope Discipline, Legacy Clauses & Opportunistic Cleanups

### 12.1. PR Scope Discipline (Do Not Touch Unrelated Areas)
- **Do NOT touch or modify areas unrelated to the main purpose of the current branch/PR.**
- Avoid "drive-by" reformatting, opportunistic refactoring of distant algorithms, rewrapping unrelated paragraphs, or speculative syntax modernization across unaffected sections of the specification.
- Unrelated edits create review friction, obscure the core change, increase merge conflict risk across concurrent WHATWG PRs, and risk introducing inadvertent normative regressions into stable spec text.

### 12.2. The Scoped Cleanup Rule (Fix Issues in Touched Areas)
- **If an area, algorithm, or clause IS being touched by the PR, DO fix any pre-existing style issues, editorial flaws, markup mistakes, or logic bugs within it.**
- When you are already rewriting, inserting into, or restructuring an algorithm step or clause:
  - Fix legacy variable lifecycle issues (`Set` without `Let`, duplicate `Let` for different objects, unbound `<var>`s).
  - Fix outdated markup (e.g. `<code>` inside `<pre class="idl">`, bare `Assert:`, redundant `data-x`, missing `</p>` before nested lists).
  - Fix grammar, missing step punctuation (`.`/`:`), or stale domintro notes in the touched section.
  - Fix subtle logic bugs (e.g. unbound variables on conditional branches, unhandled fallback/null paths, shallow clone leaks) in the modified algorithm.
- Do NOT perpetuate broken patterns or copy-paste legacy flaws just because the surrounding block previously had them.
- If the cleanup in the touched area is substantial, place it in a separate preparatory commit (e.g. `Editorial: Clean up <algorithm name>` or `Refactor <algorithm name>`) immediately preceding the substantive behavioral commit, rather than mingling them in a single diff.

### 12.3. Consistency vs. Modern Style in Legacy Clauses
- *New Features / Rewrites*: Strictly follow modern guidelines.
- *Minor Edits*: Prioritize local consistency if modern rules would make a small patch look out-of-place within a legacy block; however, never perpetuate semantic bugs or invalid Web IDL.

### 12.4. Separation of Commits
- Never mix structural/editorial cleanup (whitespace, IDL formatting, tag modernization) with functional/behavioral changes in the same commit.
- Keep editorial cleanups in dedicated commits prefixed `Editorial: ...`.

---

## 13. Reviewing PR Descriptions & Cross-Spec Companion PRs

A rigorous review does not stop at the specification diff; the PR description and any linked companion PRs in external specifications are frequent vectors for architectural oversights, description drift, and out-of-sync contracts.

### 13.0. Verify You Are Reviewing the Current Head
- Fetch with `git fetch -f origin pull/N/head:pr-N`, and check that `git rev-parse pr-N` matches `gh pr view N --json headRefOid` before reviewing, for companion PRs too. Without `-f`, a stale local `pr-N` can silently survive.

### 13.1. PR Description Hygiene & Preventing Drift
- **Description Drift / Staleness**: During multi-round reviews or stacked PR refactors, PRs frequently evolve. The PR description easily becomes stale, describing abandoned algorithms, dropped helpers, or obsolete parameters.
  - *Audit Rule*: The PR description MUST accurately represent the *final proposed diff*, not the author's initial draft.
  - *Pruning*: Explicitly remove references to dropped helpers (e.g., if a helper like "fold set and filter HTML" was eliminated during refactoring, update the PR description).
  - *Checklist Completeness*: Ensure the WHATWG PR template checklist is fully filled out (tests linked, engine bugs referenced, related issues tagged). Avoid empty test items or broken markdown links.
- **Documenting Intentional Scope Limits & Invariants**:
  - If sibling methods or edge-case legacy sinks are intentionally omitted from a refactor (e.g., `document.execCommand("insertHTML")` or XML document handling), the PR description should explicitly state that they are out-of-scope and explain the rationale.
  - Call out observable behavioral changes (such as text node coalescing differences, changes to mutation observer records, or custom element reaction timing).

### 13.2. Multi-Spec & Companion PR Review
Features touching parsing, security, loading, or scripting often span multiple specifications (e.g., HTML, DOM, Trusted Types, CSP, Fetch, Streams, URL, Web IDL). When a PR depends on or modifies an external spec:
- **Lockstep Companion Audit**:
  - Never review an HTML PR in isolation if it relies on an open companion PR in another repository (e.g., W3C Trusted Types or WHATWG DOM).
  - The reviewer MUST read the companion PR's diff and ensure the cross-spec contract matches in both directions.
- **Contract & Polarity Synchronization**:
  - Verify parameter order, types, and Boolean polarities across the spec boundary.
  - *Real-world failure mode*: HTML expected streaming sinks to require `createParserOptions` and non-stream sinks to fall back, while the companion Trusted Types PR implemented `throwIfMissing` with reversed polarity!
- **Sentinel Objects vs. String Literals**:
  - When passing sentinel values defined in external specs (e.g., Trusted Types `Stream` sentinel), verify that the HTML algorithm passes the actual sentinel object rather than a string literal (e.g., `"Stream"`), which would trigger string conversions.
- **Anchor Fragment & Definition Matching**:
  - Ensure external `<dfn>` links and `data-x-href` attributes match the companion PR's anchor IDs exactly (including casing and hyphenation, e.g., `#trustedparseroptions-sanitizer-config`), preventing link rot or Wattsi build warnings.
- **Landing Order & Release Sequencing**:
  - Explicitly document the landing dependency sequence in both PR descriptions. If HTML depends on terms defined in an external spec, confirm whether the dependency PR must be merged first.

### 13.3. The "Editorial:" Prefix Trap on Observable Behavior
- **Never prefix a PR title or commit message with `Editorial:` if the change introduces ANY web-observable behavioral difference.**
  - *Failure Mode*: Tagging a commit as `Editorial:` when the algorithm change causes navigation timing entries to be created for `srcdoc`, `javascript:`, or error pages, or when it binds previously unbound parameters.
  - *Maintainer Impact*: WHATWG maintainers and automated bots rely on the `Editorial:` prefix as a signal to skip cross-browser implementer consensus checks, MDN documentation issues, and WPT tests.
  - *Rule*: If an algorithm alteration changes a returned value, alters exception throwing, or modifies when an entry or event is queued, it is **normative**. Keep the commit message un-prefixed (or prefixed with the topic area, e.g. `Navigation timing: ...`).
  - *Calibration*: editors do accept `Editorial:` for fixes where the old text had exactly one sensible reading and implementations already agree — an unbound `<var>` that can only mean one thing, a call site passing `x's value` where `x` was already the value, or arguments in the wrong order (e.g. whatwg/html#13026). Flag the prefix only when the fix *chooses* between plausible readings or changes what a conforming implementation does.

### 13.4. Consolidate Findings That Share a Root Cause
- If one finding's fix also resolves another, report them as one finding, with one fix aimed at the cause.
- *Failure Mode*: A symptom and its cause are reported separately, each with its own fix. The author applies both. The symptom's fix changes pre-existing text more broadly than needed, and the next round has to revert it.

---

## 14. Reviewing Web Platform Tests (WPT) & Coverage Auditing

A specification review is never complete without inspecting the accompanying Web Platform Tests (WPT). Reviewing the WPT PR diff in parallel with the spec diff is essential to catch edge cases, omitted sibling methods, and underspecified behaviors.

### 14.1. The Diff-to-Test Mapping (Audit Every Changed Branch)
- **Line-by-Branch Verification**: Every algorithmic condition (`If ...`, `Otherwise, if ...`, `Switch ...`, `Assert`, `throw a ... DOMException`) introduced or modified in the spec diff must have a corresponding test case in WPT.
- **Audit Sibling Call Sites**: Authors often write tests only for the flagship API that prompted the PR (e.g. `setHTML()`), while omitting tests for the 5 legacy methods (`innerHTML`, `outerHTML`, `insertAdjacentHTML`, `createContextualFragment`, `DOMParser`) that were refactored in the same spec diff.
  - *Review Rule*: Check that every modified caller in the spec PR is explicitly tested in WPT.

### 14.2. Negative Testing & Atomic Rollback
- Do not accept test suites that only test the "happy path".
- **Exact Exception Names**: Verify tests assert the exact `DOMException` name specified (`SyntaxError`, `NotSupportedError`, `HierarchyRequestError`, `TypeError`).
- **Atomicity Tests**: When an API is specified to validate options before mutating the DOM, the WPT must verify that throwing an exception leaves the destination DOM **completely untouched** (e.g., child nodes were not cleared or removed prior to throwing).
- **Disconnected Nodes**: Verify behavior when invoked on detached elements or nodes without parents (does it throw, no-op, or return a closed/errored stream?).

### 14.3. Combinatorial Matrix Coverage
- When an API introduces multiple configuration flags or modes (e.g. `safe` vs. `unsafe`, `runScripts: true` vs. `false` vs. omitted/default, synchronous vs. streaming), the WPTs must test the **Cartesian product** of those options.
- Test both the explicit values (`{ runScripts: false }`, `{ runScripts: true }`) and the default/omitted dictionary behavior (`{}`).

### 14.4. Context-Sensitive Node Edge Cases
Fragment parsing and DOM mutations vary significantly across node types. Ensure WPT coverage exists for:
- **`<template>` Elements**: Verify operations target `template.content` (`template contents`) rather than direct template children across all method variants.
- **Foster Parenting & Table Contexts**: Parsing fragments in `<table>`, `<tbody>`, `<tr>`, `<td>` contexts.
- **Form Contexts**: Parsing fragments inside `<select>` or `<optgroup>`.
- **Script Elements**: Parsing inside `<script>` in HTML and SVG namespaces (verifying script execution suppression or early null returns).
- **XML / XHTML Documents**: Verifying XML parsing vs. HTML parsing, and testing that XML-specific error conditions or unsupported modes throw as specified.

### 14.5. Testing Observable Side Effects & Invariants
- **Script Execution Suppression**: Assert that scripts do not execute under safe or `runScripts: false` modes (testing `<script>` tags, inline event handlers like `<img onerror=...>`, and SVG scripts).
- **Custom Elements & Shadow Roots**: Assert whether custom element constructors, `connectedCallback`, and declarative shadow roots fire, and test the exact timing of their reactions.
- **Text Node Coalescing**: If an algorithm alters parsing or insertion pipelines, test text node boundary merging via `childNodes.length`.

### 14.6. WPT Antipatterns to Catch
- **Engine-Driven vs. Spec-Driven Assertions**: Authors occasionally write WPT tests that assert current browser engine behavior (e.g. Chromium's current implementation) rather than what the specification change dictates. Reject tests that encode known engine bugs as expected behavior.
- **Tentative vs. Non-Tentative Files**:
  - Novel APIs not yet fully integrated into a ratified standard belong in `*.tentative.html` files.
  - Tests for bug fixes or normative changes to **pre-existing standard APIs** (e.g., `innerHTML` on `<template>` or XML throwing behavior) MUST be added to standard, non-tentative WPT files.

---

## 15. Automated Static Analyzers

The skill includes three deterministic Python static analyzers in `scripts/` to catch syntactic, IDL, variable lifecycle, and coverage failures automatically before or during spec review:

### 15.1. Web IDL Analyzer (`check_webidl.py`)
Validates `<pre class="idl">` blocks against WHATWG Web IDL guidelines:
- **Rule 1 (IDL-XREF-SPAN)**: Flags any `<code>` tags used inside `<pre class="idl">` (xrefs must use `<span>`).
- **Rule 2 (IDL-OPTIONAL-DICT-DEFAULT)**: Flags optional dictionary arguments that omit the required `= {}` default value.
- **IDL-NO-VAR**: Flags `<var>` tags used inside Web IDL declarations.
- **IDL-SINGLE-MEMBER-PER-LINE**: Flags multiple semicolon-terminated member declarations on a single line.

```bash
python3 scripts/check_webidl.py path/to/source.html
```

### 15.2. Algorithm Prose & Lifecycle Analyzer (`check_algorithms.py`)
Validates algorithm steps inside `<div algorithm>` blocks and spec markup:
- **Rule 4 (ALGO-UNDECLARED-SET / ALGO-DUPLICATE-LET)**: Validates variable lifecycle. Flags `Set <var>x</var> to` when `<var>x</var>` was never introduced with `Let`, and flags duplicate `Let <var>x</var> be` declarations in the same algorithm.
- **ALGO-UNBOUND-VAR-OUTER-SCOPE**: Flags variables declared with `Let` inside conditional sub-steps (`<ol>` depth >= 2) that are subsequently referenced at outer scope without an outer declaration.
- **ALGO-UNUSED-VAR**: Flags variables declared with `Let` that are never read/referenced again in the algorithm and omit `<var ignore>`.
- **ALGO-LIST-OF**: Flags `For each <var>x</var> in ...` (Infra list iteration requires `of`, not `in`).
- **ALGO-ASSERT-SPAN**: Flags bare `Assert:` lacking `<span>Assert</span>:` markup.
- **ALGO-REDUNDANT-DATA-X**: Flags redundant `data-x="term"` on `<span data-x="term">term</span>` where the cross-reference matches the definition name.
- **ALGO-NESTED-LIST-P**: Flags algorithm list items (`<li><p>...<ol>`) missing `</p>` before a nested `<ol>` or `<ul>`.
- **ALGO-STEP-PUNCTUATION**: Flags leaf algorithm steps missing terminal punctuation (`.` or `:`).
- **ALGO-NO-NEWLINE-BEFORE-GT**: Flags newlines immediately preceding `>` in HTML tags (`\n>`).
- **ALGO-DICT-TYPE-CHECK**: Flags invalid dictionary type checking (`If <var>options</var> is a <code>SomeOptions</code>:` or `is a dictionary`).
- **NAMESPACE-CASING**: Flags uppercase `<span>HTML Namespace</span>` or `<span>MathML Namespace</span>`.
- **ALGO-QUALIFIED-INTRO**: Flags unqualified method step intros (`"The innerHTML setter steps are:"`) when the method exists on multiple interfaces (`Element` vs `ShadowRoot`).

```bash
python3 scripts/check_algorithms.py path/to/source.html
```

### 15.3. WPT Coverage & Diff Analyzer (`check_wpt_coverage.py`)
Audits spec changes against accompanying Web Platform Tests:
- **WPT-MISSING-SINK-COVERAGE**: Extracts all modified IDL methods and algorithm sinks from the spec diff, scans the WPT directory/diff, and flags any modified sinks with zero test coverage (catching forgotten sibling methods like `ShadowRoot.innerHTML` or `createContextualFragment`).
- **WPT-MISSING-EXCEPTION-TEST**: Verifies that every `throw a "..." DOMException` in the spec algorithm has a corresponding `assert_throws_dom("...")` test.
- **WPT-TENTATIVE-ON-STANDARD-API**: Flags tests for pre-existing standard APIs erroneously placed in `.tentative.html` files.

```bash
python3 scripts/check_wpt_coverage.py --spec-file path/to/spec.html --wpt-dir path/to/wpt/
```

---

## 16. House Style (Rule IDs from `html-style-guide.md`)

[`html-style-guide.md`](html-style-guide.md) (in this skill directory) is the de-facto style guide for `whatwg/html`'s `source`, distilled from the text itself, `CONTRIBUTING.md`, and recent editor reviews, with spec examples for every rule. This section condenses the rules most often hit in review; **read [`html-style-guide.md`](html-style-guide.md)** when authoring new sections, touching an unfamiliar area, or when a rule below is ambiguous. Cite rule IDs (e.g. `API-STEPS-FORM`) in review comments.

### 16.1. Branch Tiers, Infra vs. HTML, and Scope
Where the spec uses more than one style for the same construct, the guide ranks them:
- **Modern**: use in new text.
- **Accepted**: fine to use; match surrounding text. Do not demand a rewrite.
- **Legacy**: do not introduce in new text; rewriting existing text is optional.
- **Obsolete**: fix when touching.

**Infra vs. HTML house style:** rules marked **Infra:** in [`html-style-guide.md`](html-style-guide.md) restate conventions of the [Infra Standard](https://infra.spec.whatwg.org/) that apply to every WHATWG spec (algorithm declarations, parameters, variables, control flow, assertions, lists/maps/structs, conformance language); the guide only states HTML's markup or where Legacy HTML prose diverges. Rules without **Infra:** are HTML-specific.

**Scope:** style rules apply to *new or rewritten normative text* (algorithm steps, state declarations, IDL member prose) — not to notes, examples, `dl.domintro`, or author-facing prose, and not to carried-over text (a re-wrapped step, text restored by a revert, or a single step added inside an algorithm written in a Legacy style). Flag a Legacy form only when a PR introduces a new algorithm, section, or several new steps.

### 16.2. Blocks, Definitions, Headings & Cross-References
- **`BLK-NOTE` / `BLK-EXAMPLE` / `DEV-W-NODEV`**: `<p class="note">` for one paragraph, `<div class="note">` for more (no leading `"Note:"`; place algorithm notes after the step's `<p>`, never inside one bullet of an any/all condition list). Wrap multi-element examples in `<div class="example">` with `<pre><code class="html|js|css">`. Wrap implementer-only prose/algorithms in `<div w-nodev>` and developer-only replacements in `w-dev`.
- **`IDL-BLOCK` / `ELEM-DEFINITION` / `ELEM-DOMINTRO`**: Place IDL in `<pre><code class="idl">` (2-space indent, no `w-nodev`, no `<var>`). Start element sections with `<dl class="element">`, define content/enumerated attributes (`<dfn element-attr>`, `<dfn attr-value>`), and update the index tables. Follow author-exposed IDL with `<dl class="domintro">` using `<span subdfn data-x="dom-…">` and non-normative present-tense `<dd>`s.
- **`DFN-TYPED`**: Use typed `<dfn>` attributes (`element`, `interface`, `dictionary`, `enum`, `attribute for="I"`, `method for="I"`, `constructor for="I"`, `dict-member for="D"`, `enum-value for="E"`, `element-attr for="el"`, `attr-value for="el/attr"`, `event for="I"`). Plain `<dfn>` is for concepts and algorithms. Put `data-x` on the inner `<code>` in prose (`<dfn attribute for="I"><code data-x="dom-I-x">x</code></dfn>`) and on the `<dfn>` inside `<pre><code class="idl">`. `for="a,area"` has no spaces; attribute values use `element/attribute` pairs.
- **`DFN-EXPORT`**: Add `export` on `<dfn>`s referenced by other specs; use `data-lt="a|b"` instead of duplicate `<dfn>`s.
- **`DFN-NAMES`**: Algorithm `<dfn>`s are lowercase imperative verb phrases (`parse a URL`), with no leading article and no `"algorithm"` suffix; concept `<dfn>`s are lowercase noun phrases, disambiguated with `data-x="concept-<owner>-<name>"`.
- **`DFN-NO-FLAGS`**: Declare *new* boolean state as `"a boolean <dfn>…</dfn>, initially false"`, tested with `"is true"`/`"is false"` and mutated with `"set … to true"` — not a `"flag"` (`set`/`unset`). Using an existing flag in HTML or another spec in new steps is fine.
- **`DFN-STRUCT`**: `"…, which is a <span>struct</span> with the following <span data-x="struct item">items</span>:"` + `<ul>` of `<li><p><dfn>Name</dfn>, a TYPE, initially VALUE.</p></li>` (the `<dl>` form is Accepted). Tuples of any arity are fine for small fixed-shape values.
- **`HDR-SENTENCE-CASE` / `HDR-ALIAS-ANCHOR`**: Headings are sentence case. When renaming or moving a heading, an `export`ed `<dfn>`, or an anchor linked externally, preserve the old fragment with `<span id="old-id"></span>` or `<dfn id="old-id">`.
- **`XREF-SPAN-AUTOLINK`**: `<span>` autolinks matching terms; add `data-x` when the surface text is inflected or uses a `concept-*` key, and verify `data-x` targets the exact `<dfn>` named by the text. When an algorithm is a sentence subject, write `"the <span>X</span> algorithm"`.
- **`XREF-CODE`**: Element and interface names are bare `<code>` (pluralize outside: `<code>div</code> elements`); content attributes use `attr-<el>-<name>`, IDL members `dom-<Interface>-<member>` (methods with `()`), events `event-<name>`, handlers `handler-on<name>`, and HTTP headers `` `<code data-x="http-…">…</code>` `` in literal backticks.
- **`XREF-STRING-LITERAL`**: Write code-level string literals as `"<code data-x="">value</code>"` with quotes *outside* `<code>`, compare directly with `"is"`, and write `"the empty string"` for `""`.

### 16.3. Algorithm Structure, Variables & State
- **`ALG-PREAMBLE`**: Wrap algorithms in `<div algorithm>` and follow [Infra's algorithm declaration](https://infra.spec.whatwg.org/#algorithm-declaration) and [parameter](https://infra.spec.whatwg.org/#algorithm-params) conventions: `To <dfn>name</dfn>, given a TYPE <var>x</var>, an optional TYPE <var>y</var> (default V):` (nullable types are `TYPE-or-null`; test optional args with `"If <var>y</var> was not given"`; add `"…, run these steps. They return …."` when the return type is not obvious from the steps; `"…, run these steps:"` is Accepted on non-`<dfn>` hooks).
- **`ALG-ASSERT`**: `<span>Assert</span>: condition.`
- **`FLOW-IF-THEN` / `FLOW-ANY-ALL` / `FLOW-RETURN` / `FLOW-SWITCH` / `FLOW-FOR-EACH`**: Single-step `"If X, then Y."`; multi-step `"If X:"` + nested `<ol>` (`"then:"` is Legacy); 3+ long/heterogeneous conditions use `"If any/all of the following are true:"` + `<ul class="brief">` + `<p>then …</p>`; `"Return"` exits the algorithm while `"Abort these steps"` exits a parallel block or substeps; `"Switch on <var>x</var>:"` + `<dl class="switch">`; `"For each <var>item</var> of <var>list</var>:"` (never `"in"`).
- **`VAR-LET-SET` / `VAR-BIND-THEN-TEST` / `VAR-CAMELCASE` / `VAR-THIS`**: `Let` once per scope, `Set` thereafter; `Let <var>x</var> be null` before branches that assign `<var>x</var>` is required hoisting, not a defect. Do not reuse one `<var>` name for two different objects in the same algorithm. Bind a complex expression with `Let` before testing and reusing it (never refer back to an unbound expression as `"it"`). Variable names are `<var>camelCase</var>`; receiver in IDL steps is `<span>this</span>`.
- **`VAL-LIST-OPS` / `VAL-MAP-OPS`**: Use Infra lists (`« »`, `data-x="list …"`) and maps (`«[ "k" → v ]»`, `<var>map</var>[<var>k</var>]`, `<span data-x="map exists">exists</span>`); read Web IDL dictionary members as `<var>options</var>["<code data-x="dom-X-y">y</code>"]`.
- **`STATE-DECLARATION`**: `"Each X has a TYPE <dfn>name</dfn>, initially VALUE."` in a single `<p>` (reserve `[[Slot]]`s for objects with ECMAScript internal methods). If the declaring sentence lists when the state changes, update it when adding a transition.

### 16.4. Invoking Algorithms, IDL Prose, Tasks, Promises & Vocabulary
- **`CALL-CONJUGATED` / `CALL-RELEVANT-OBJECTS` / `CALL-IMPERATIVE`**: Conjugate algorithm links inline (`"the result of <span data-x="parse a URL">parsing</span> <var>url</var>"`) or `"running <span>X</span>"`, passing arguments with `"given"`. Obtain JS context via `<object>'s <span>relevant global object</span>` / `relevant settings object` / `relevant realm` (never `entry` or `incumbent`). Algorithm `<ol>` steps are bare imperatives without `"the user agent must"`.
- **`API-STEPS-FORM` / `API-READ-INTERNAL-STATE` / `IDL-REFLECT-IN-IDL`**: `"The <dfn …><code data-x="dom-X-y">y</code></dfn> getter/setter/method/constructor steps are …"`; test optional IDL arguments with `"was not given"`, never `"is undefined"` (unless `any`). Read internal concepts or content attributes in algorithms rather than Web IDL getters. Prefer `[Reflect*]` in IDL over reflection prose when expressible.
- **`TASK-QUEUE-GLOBAL` / `PAR-IN-PARALLEL` / `EVT-FIRE`**: `"<span>queue a global task</span> on the <span>X task source</span> given <var>global</var> to …"` (or `queue an element task`). Inside `"Run the following steps <span>in parallel</span>:"` (or a parallel queue), touch no JS objects/promises and throw nothing; do not introduce Legacy `"spin the event loop"`, `"await a stable state"`, or `"synchronous section"` in new algorithms. Dispatch events via `"<span data-x="concept-event-fire">fire an event</span> named <code data-x="event-…">…</code> at <var>target</var>"`.
- **`EXC-THROW-DOMEXCEPTION` / `PROM-HANDLING`**: `throw a/an <span>"<code>Name</code>"</span> <code>DOMException</code>` or `throw a <code>TypeError</code>`. Create promises in a named realm, settle with `"resolve <var>p</var> with undefined"` / `"reject <var>p</var> with …"` (from a queued task when in parallel), and react with `"<span>Upon fulfillment/rejection</span> of <var>p</var>"`.
- **`CONF-RFC2119` / `VOC-NAVIGABLE` / `VOC-SAME-ORIGIN`**: Lowercase `"must"`/`"should"`/`"may"` with an explicit conformance class outside algorithms; `<!-- NON-NORMATIVE SECTION -->` after informative headings; `<span>navigable</span>` / `<span>traversable</span>` rather than `"browsing context"`; predicate `"is <span>same origin</span> with"` vs. adjective `"same-origin"`.

---

## 17. Comprehensive Self-Review & PR Review Checklist

Before finalizing or approving any HTML specification PR, run through this comprehensive checklist:

### Automated Static Analysis
- [ ] Run `python3 scripts/check_webidl.py <files>` (zero Web IDL xref or optional dict default errors).
- [ ] Run `python3 scripts/check_algorithms.py <files>` (zero variable lifecycle, scope leak, unused var, punctuation, or assertion errors).
- [ ] Run `python3 scripts/check_wpt_coverage.py --spec-file <spec> --wpt-dir <wpt>` (all modified sinks and exceptions covered).

### PR Description, Commit Hygiene & Companion PR Audit
- [ ] **Current Head Verified**: Does the local SHA match `headRefOid` for every PR reviewed (see 13.0)?
- [ ] **PR Scope Discipline (No Unrelated Edits)**: Are all modified files, algorithms, and clauses directly relevant to the main purpose of the PR? Have drive-by reformatting, opportunistic refactoring of distant algorithms, and unrelated edits been pruned?
- [ ] **Scoped Cleanup in Touched Areas**: Have pre-existing style issues, editorial flaws, markup mistakes, and logic bugs in the *touched* clauses been fixed rather than perpetuated?
- [ ] **Commit Separation for Cleanups**: If cleanups in touched areas are non-trivial, are they separated into dedicated preparatory commits (e.g. `Editorial: ...`) preceding the substantive changes?
- [ ] **No "Editorial:" Prefix on Observable Behavior**: Is the PR or commit prefixed with `Editorial:`? If the change causes entries to be created/queued, changes return values, or rejects promises, remove `Editorial:`.
- [ ] **PR Description Freshness**: Does the PR description match the actual final diff? Have mentions of dropped helpers, obsolete steps, or old syntax been pruned?
- [ ] **Checklist & Template Completeness**: Are WPT test links, issue links, and engine bugs properly documented without broken markdown links?
- [ ] **Scope Exclusions Noted**: Are intentional out-of-scope sibling sinks (e.g. legacy `execCommand`, XML document limits) documented in the PR body?
- [ ] **Companion PR Synchronization**: If a companion PR in another spec exists (e.g. Trusted Types, DOM, Fetch), has it been audited? Do parameter contracts, sentinel types, and boolean polarities agree in both directions?
- [ ] **Anchor & Link Validation**: Do cross-spec `data-x-href` links match the companion spec's exact exported anchor fragments?
- [ ] **Landing Order Established**: Is the merge sequence clearly stated between the companion PRs?
- [ ] **Findings Consolidated**: Are findings with a shared root cause reported as one, with one fix (see 13.4)?

### Web Platform Tests (WPT) Coverage Audit
- [ ] **Diff-to-Test Mapping**: Does every new branch, throwing condition, and fallback path in the spec diff have an explicit test case?
- [ ] **Sibling Sinks Tested**: Are all modified parallel methods (`Element.innerHTML`, `ShadowRoot.innerHTML`, `outerHTML`, `insertAdjacentHTML`, `createContextualFragment`, `setHTML`) tested, not just the primary new API?
- [ ] **Atomicity Tested**: Are tests present verifying that when an exception is thrown, the destination DOM remains pristine and unmutated?
- [ ] **Context-Sensitive Elements**: Are tests included for `<template>`, `<table>`/`<tbody>`, `<select>`, `<script>`, and XML/XHTML documents?
- [ ] **Fallback Paths Tested**: Are tests present for non-fetch / null-controller navigations (`about:srcdoc`, `javascript:`, error pages)?
- [ ] **Combinatorial Matrix**: Are all combinations of boolean flags (e.g. `safe` × `runScripts` false/true/default) tested?
- [ ] **Spec vs. Engine Truth**: Do tests assert the normative spec behavior rather than current browser engine quirks?
- [ ] **Tentative Naming Correctness**: Are fixes to existing standard methods placed in non-tentative files, while novel APIs use `.tentative.html`?

### Algorithmic Correctness & State
- [ ] **Scope Leaks & Unbound Variables**: Are any variables declared with `Let` inside conditional sub-lists (`<ol>`) referenced outside that branch? (Initialize with `Let <var>x</var> be null` in outer scope).
- [ ] **Pre-Initialization State Access**: Are capability checks, permissions policy, or environment settings queried on an object *before* its subordinate objects (`window.document`, parent) are linked?
- [ ] **Fallback & Null Path Auditing**: When guarding an algorithm step with `If <var>controller</var> is non-null:`, what happens on the fallback path (`srcdoc`, `javascript:`, error pages)? Are entries or state dropped?
- [ ] **Shallow Clones**: Are any cloned dictionaries/maps holding nested maps/lists? If so, are mutations safely isolated, or do they leak into the source object?
- [ ] **Temporal State Snapshots**: Are dynamic locations (`adjusted insertion location`, context node, open elements) captured *before* any insertion or tree mutation?
- [ ] **Object Construction Ordering**: Are all flags/modes finalized before object construction, or are object internal slots explicitly updated afterward?
- [ ] **Atomic Failure**: Are option validation, parser creation, and type checks performed *before* any destructive DOM mutations (clearing children, detaching nodes)?
- [ ] **Dictionary Types in Algorithms**: Are there any invalid `If options is a FooOptions` checks? (Check keys via `exists` or default fallback instead).

### Parser & Tree Construction
- [ ] **Adoption Agency Algorithm**: Does AAA create, reparent, or clone elements without your new checks? Are parentless `lastNode` and self-append loops prevented?
- [ ] **Root & Body Attribute Merging**: Do duplicate start tags merge attributes without passing through element sanitization/validation?
- [ ] **Speculative Parsing**: Does speculative parsing reflect any new blocking, sanitization, or script rules?
- [ ] **Template Redirection**: Does every insertion method redirect `HTMLTemplateElement` to `template.content`?

### Call Site & Architecture Audit
- [ ] **Exhaustive Call Sites**: Have all sibling entry points (`Element.innerHTML`, `ShadowRoot.innerHTML`, `outerHTML`, `insertAdjacentHTML`, `createContextualFragment`, `parseFromString`, `setHTML`, `parseHTML`) been audited for signature changes?
- [ ] **No Masking Defaults**: Are internal abstract algorithm parameters mandatory where defaults could silently mask forgotten callers?
- [ ] **Real Sink Names**: Are sink names passed to security violation reporting actual API names (e.g. `"Element innerHTML"`), never synthetic names (`"Sanitizer"`)?
- [ ] **Cross-Spec Sentinels**: Are sentinels passed as proper specification objects, not string literals?

### Web IDL, Prose & Markup
- [ ] **IDL Cross-References**: Do cross-references inside `<pre class="idl">` use `<span>` exclusively, without `<code>` (`IDL-XREF-SPAN`)?
- [ ] **Optional IDL Dictionaries**: Do optional dictionaries without required members specify `= {}` (`IDL-DICTIONARY`)?
- [ ] **Variable Declarations**: Does the first assignment use `Let` and subsequent assignments use `Set` (`VAR-LET-SET`)? No second `Let` for a different object; every `<var>` bound? (`Let <var>x</var> be null` before branches that assign it is correct hoisting, not a defect.)
- [ ] **Unused Variables**: Are all `Let`-bound variables referenced in subsequent steps (or marked `<var ignore>`)?
- [ ] **List Iteration Keyword**: Does iteration use `For each <var>x</var> of <var>list</var>` (never `in`) (`FLOW-FOR-EACH`)?
- [ ] **Assertion Markup**: Are assertions formatted as `<span>Assert</span>:` (`ALG-ASSERT`)?
- [ ] **Cross-Reference Targets & Redundant `data-x`**: Does link text name the `<dfn>` it targets, and are redundant `data-x` attributes omitted when matching concept text (`XREF-SPAN-AUTOLINK`)?
- [ ] **Nested List Closures & End Tags**: Are `<p>` tags closed before nested `<ol>` or `<ul>` lists, and all `</p>`/`</li>`/`</dt>`/`</dd>` present in touched lines (`SRC-END-TAGS`)?
- [ ] **Step Punctuation**: Do algorithm steps end with a period `.` or colon `:`?
- [ ] **Line Wrapping & Block Layout**: Any clearly unwrapped prose (`SRC-WRAP-100`)? No newlines immediately before `>`? No blank line just inside a note/example/`<li>` (`SRC-LI-P`)? Multi-line `<li>` children indented (`SRC-INDENT-BLOCK`)?
- [ ] **Grammatical Conjunctions**: Did removing an item from a list preserve the "and"/"or" conjunction?

### House Style (`html-style-guide.md`)
- [ ] **Branch Tier & Scope**: Is new normative text written in the **Modern** style and touched text free of **Obsolete** forms, without demanding Accepted → Modern rewrites of untouched or carried-over text?
- [ ] **Typed dfns, Keys & Export**: Do new `<dfn>`s use typed attributes (`attribute`, `method`, `element-attr`, `event`, …) with `for=""`, `data-x` in the right place, and `export` when needed by other specs (`DFN-TYPED`, `DFN-EXPORT`)?
- [ ] **Preserved Anchors**: Do renamed/moved headings and exported `<dfn>`s keep the old id via `<span id="old-id">` or `<dfn id="old-id">` (`HDR-ALIAS-ANCHOR`)?
- [ ] **Algorithm Preambles**: Wrap in `<div algorithm>` and follow Infra's `To <dfn>x</dfn>, given a TYPE <var>y</var>:` convention (`ALG-PREAMBLE`)?
- [ ] **IDL Member Prose**: `"getter/setter/method/constructor steps are"` (`API-STEPS-FORM`)?
- [ ] **No "user agent must" in Steps**: Are `<ol>` steps bare imperatives (`CALL-IMPERATIVE`)?
- [ ] **State Declarations**: Is new state `"has a boolean <dfn>x</dfn>, initially false"` rather than a new flag (`STATE-DECLARATION`, `DFN-NO-FLAGS`)?
- [ ] **Tasks, Parallelism & Events**: Does every return from parallel steps name a task source and global/element (`TASK-QUEUE-GLOBAL`, `PAR-IN-PARALLEL`)? Are events dispatched with `<span data-x="concept-event-fire">fire an event</span> named <code data-x="event-…">…</code>` (`EVT-FIRE`)?
- [ ] **Exceptions & Promises**: `throw a/an <span>"<code>XError</code>"</span> <code>DOMException</code>`; promises created in a named realm and resolved `"with undefined"` (`EXC-THROW-DOMEXCEPTION`, `PROM-HANDLING`)?
- [ ] **Conformance & Vocabulary**: Lowercase `"must"`/`"should"`/`"may"` with an explicit conformance class (`CONF-RFC2119`)? `"navigable"` rather than `"browsing context"` (`VOC-NAVIGABLE`)? `"is <span>same origin</span> with"` vs. `"same-origin"` (`VOC-SAME-ORIGIN`)?

### Domintro & Documentation
- [ ] **Exception Parity**: Do domintro `<dd>` exception statements match the actual normative throwing behavior?
- [ ] **Stale Warnings & Notes**: Have `<p class="warning">` and adjacent notes been updated to reflect changed steps or new policy, parser, or security capabilities?
- [ ] **Interface Qualification**: Are multi-interface methods qualified (e.g. `"The Element innerHTML setter steps are:"`)?



