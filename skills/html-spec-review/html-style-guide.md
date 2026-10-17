# HTML Standard — de-facto style guide

How the HTML Standard's `source` is written in practice, distilled from the specification text,
[CONTRIBUTING.md](https://github.com/whatwg/html/blob/main/.github/CONTRIBUTING.md), and recent
editor reviews. Focused on recurring authoring and review conventions that are not already enforced
by Wattsi at build time.

Each rule has a stable ID (`PREFIX-NAME`), a summary title, a concise description, and an example
from the live specification (`https://html.spec.whatwg.org/`). Where the spec uses more than one
style for the same construct, a **Branch** note ranks them:

- **Modern** — use in new text.
- **Accepted** — fine to use; match the surrounding text. Do not ask to rewrite.
- **Legacy** — do not introduce in new text; rewriting existing text is optional.
- **Obsolete** — fix when touching.

**Infra vs. HTML house style.** Rules that build on the [Infra Standard](https://infra.spec.whatwg.org/)
carry an **Infra:** link. The linked Infra section defines the cross-spec convention (which applies
to every WHATWG standard); this guide states how HTML marks it up or where Legacy HTML prose
diverges. Rules without an **Infra:** line are HTML-specific.

**Scope.** Rules apply to *new or rewritten normative text* (algorithm steps, state declarations,
IDL member prose). They do not apply to notes, examples, `dl.domintro`, or author-facing prose, and
they do not turn carried-over text into a finding: a step that was merely re-wrapped, text restored
by a revert, or a single step added inside a Legacy algorithm follows the surrounding style. Flag a
Legacy form only when a PR introduces a new algorithm, section, or several new steps.

Companion documents:
[CONTRIBUTING.md](https://github.com/whatwg/html/blob/main/.github/CONTRIBUTING.md),
the [WHATWG style guide](https://whatwg.org/style-guide), and the spec's guidance on
[realms, settings objects, and global objects](https://html.spec.whatwg.org/#realms-settings-objects-global-objects),
[parallelism](https://html.spec.whatwg.org/#parallelism),
and [the event loop](https://html.spec.whatwg.org/#event-loop-for-spec-authors).

| § | Section | Prefixes |
|---|---|---|
| 1 | Source layout and blocks | `SRC`, `BLK`, `DEV` |
| 2 | Headings, ids, and cross-references | `HDR`, `XREF` |
| 3 | Definitions (`<dfn>`) | `DFN` |
| 4 | Web IDL and element definitions | `IDL`, `ELEM` |
| 5 | Algorithm structure and control flow | `ALG`, `FLOW` |
| 6 | Variables, values, and state | `VAR`, `VAL`, `STATE` |
| 7 | Invoking algorithms and IDL member prose | `CALL`, `API` |
| 8 | Tasks, parallelism, and events | `TASK`, `PAR`, `EVT` |
| 9 | Exceptions and promises | `EXC`, `PROM` |
| 10 | Conformance and vocabulary | `CONF`, `VOC` |

---

## 1. Source layout and blocks (`SRC`, `BLK`, `DEV`)

### `SRC-WRAP-100` — Wrap prose at 100 columns; never break right after an inline start tag
Wrap new or modified prose paragraphs at 100 characters (`specfmt`), breaking only at whitespace and
filling each line before wrapping. Never break immediately after an inline opening tag (`<i
data-x="…">\ntext</i>` introduces unwanted spaces); break between attributes or inside a
whitespace-containing attribute value instead. Do not rewrap `<pre>`, `<table>`, `<svg>`, `<script>`,
`<style>`, comments, `<dt>`, `<img>`/`<iframe>` tags, `ul.domTree`, Dependencies `<dfn>`s, or
References `<dd>`s. In review, flag only clearly unwrapped prose (a line well over 100 characters or
an unwrapped paragraph), not 1–2 character overruns or under-filled lines.
**Example:** [#parallelism](https://html.spec.whatwg.org/#parallelism)

### `SRC-INDENT-BLOCK` — One space of indentation per block; transparent wrappers do not indent
Indent one space for each block-level ancestor (`<ol>`, multi-line `<li>`, `<dl>`, `<dd>`,
`<div class="example">`, `<div class="note">`, `<div class="warning">`, table rows). A `<p>` inside
a one-line `<li>` is not indented further, whereas a multi-line `<li>` puts `<li>` on its own line
and indents its child `<p>`s one space deeper. `<div algorithm>`, `<div w-nodev>`, and
`<div var-scope>` are transparent wrappers: their children stay at the surrounding indentation level.
**Example:** [#dom-track-track](https://html.spec.whatwg.org/#dom-track-track)
```html
  <div algorithm>
  <p>The <dfn attribute for="HTMLTrackElement"><code data-x="dom-track-track">track</code></dfn>
  getter steps are to return <span>this</span>'s <span>text track</span>.</p>
  </div>
```

### `SRC-LI-P` — Wrap `<li>` text in `<p>` (except in `ul.brief`); blank lines between sibling blocks only
Write `<li><p>…</p></li>` even for single-line items; only `<ul class="brief">` uses bare `<li>`s.
`<dd>` wraps prose sentences in `<p>`, while short phrases in `dl.element` and `dl.switch` are bare.
Separate sibling `<li>`, `<dt>`, `<dd>`, and `<p>` blocks with a blank line, and never place a blank
line immediately after the opening tag or before the closing tag of `<ol>`, `<ul>`, `<li>`, `<dd>`,
`<div class="note">`, or `<div class="example">`.
**Example:** [#parallelism](https://html.spec.whatwg.org/#parallelism) · [#ports-and-garbage-collection](https://html.spec.whatwg.org/#ports-and-garbage-collection)
```html
  <div class="note">
   <p>First paragraph.</p>

   <p>Second paragraph.</p>
  </div>
```

### `SRC-END-TAGS` — Close every `</p>`, `</li>`, `</dt>`, `</dd>`; double-quote attributes
Never omit end tags in new or touched lines: close every `<p>`, `<li>`, `<dt>`, and `<dd>`, and
always close `</p>` before a nested `<ol>` or `<ul>`. Double-quote all attribute values, and never
put a newline immediately before `>`.
**Example:** [#parallelism](https://html.spec.whatwg.org/#parallelism)
> **Branch**
> 1. **Modern** — all end tags present.
> 2. **Legacy** — unclosed `<dt>`/`<dd>` in older `dl.element` and definition lists ([#the-html-element](https://html.spec.whatwg.org/#the-html-element)).

### `BLK-NOTE` — `<p class="note">` for one paragraph, `<div class="note">` for more
Notes are non-normative asides explaining rationale or consequences; keep rationale in a note rather
than inside a normative algorithm step. Notes start with a capital letter and never with `"Note:"`.
Inside an algorithm step, place `<p class="note">` inside the `<li>` after the step's `<p>`; for an
`"If any/all of the following are true:"` list, place any note after the `<p>then …</p>` paragraph,
never inside an individual condition bullet.
**Example:** [#event-loop-for-spec-authors](https://html.spec.whatwg.org/#event-loop-for-spec-authors)

### `BLK-EXAMPLE` — `<div class="example">` with an intro sentence and `<pre><code class="LANG">`
Wrap multi-element examples in `<div class="example">` with an introductory `<p>` and
`<pre><code class="html">` (`js`, `css`), or `<p class="example">` for a single prose paragraph.
Mark anti-examples with `<pre class="bad"><code class="html">`.
**Example:** [#example-cite-usage-correct-vs-incorrect](https://html.spec.whatwg.org/#example-cite-usage-correct-vs-incorrect)

### `DEV-W-NODEV` — Wrap implementer-only text in `w-nodev`; use `w-dev` for developer-only substitutes
Processing models, algorithms, IDL member prose, and implementer notes go inside `<div w-nodev>`
(or `<p w-nodev>` / `<span w-nodev>`). `dl.domintro`, `dl.element`, examples, and author conformance
requirements stay visible. `<pre><code class="idl">` is omitted from the Developer's Edition
automatically, so do not put `w-nodev` on it; use `w-dev` for replacement text shown only in the
Developer's Edition (e.g. `<dd w-dev>Uses <code>HTMLHtmlElement</code>.</dd>`).
**Example:** [#introduction](https://html.spec.whatwg.org/#introduction) · [#the-html-element](https://html.spec.whatwg.org/#the-html-element)

---

## 2. Headings, ids, and cross-references (`HDR`, `XREF`)

### `HDR-SENTENCE-CASE` — Headings are sentence case
Capitalize only the first word and proper nouns or IDL names.
**Example:** [#how-to-catch-mistakes-when-writing-html:-validators-and-conformance-checkers](https://html.spec.whatwg.org/#how-to-catch-mistakes-when-writing-html:-validators-and-conformance-checkers)
```html
  <h4>How to catch mistakes when writing HTML: validators and conformance checkers</h4>
```

### `HDR-ALIAS-ANCHOR` — Preserve old anchors with `<span id="old-id">` or `<dfn id="old-id">`
When renaming or moving a heading, an `export`ed `<dfn>`, or any anchor that external specs or MDN
link to, keep the old fragment working with `<span id="old-id"></span>` inside the heading/paragraph
or `id="old-id"` on the renamed `<dfn>`. Deleting a non-exported internal helper when inlining its
steps does not require an alias.
**Example:** [#rel-alternate](https://html.spec.whatwg.org/#rel-alternate)
```html
  <h5 id="rel-alternate"><span id="link-type-alternate"></span>Link type "<code data-x="rel-alternate">alternate</code>"</h5>
```

### `XREF-SPAN-AUTOLINK` — `<span>` autolinks terms; use `data-x` when the surface text differs
Wattsi autolinks `<span>term</span>` case-insensitively (including simple `-s` plurals) to a
matching `<dfn>`. Add `data-x="…"` when the surface text is conjugated or inflected
(`<span data-x="obtain a site">obtaining a site</span>`) or when the target uses an internal key
(`concept-*`), and verify that `data-x` points to the exact `<dfn>` named by the visible text
(Wattsi catches missing targets, not wrong sibling targets). When an algorithm is the subject of a
sentence rather than being invoked, write `"the <span>X</span> algorithm"`.
**Example:** [#a-quick-introduction-to-html](https://html.spec.whatwg.org/#a-quick-introduction-to-html)

### `XREF-CODE` — `<code>` cross-references for elements, attributes, IDL, events, and HTTP headers
Wrap code-level identifiers in `<code>` in prose (inside `<pre><code class="idl">`, use `<span>` per
`IDL-XREF-SPAN`). Pluralize outside the tag (`<code>div</code> elements`, never `<code>divs</code>`).

| Target | Prose markup | Notes |
|---|---|---|
| Element | `<code>div</code>` | Bare `<code>`, no `data-x` |
| Content attribute | `<code data-x="attr-img-src">src</code>` | `attr-<name>` for globals; `attr-<group>-<name>` for shared (`attr-hyperlink-href`) |
| Attribute keyword / state | `<code data-x="attr-…-keyword">keyword</code>`, `<span data-x="attr-…-keyword-state">State</span>` | Keywords use `<code>`; states use `<span>` |
| IDL interface / type | `<code>Document</code>` | Bare `<code>` |
| IDL member | `<code data-x="dom-Document-hidden">hidden</code>`, `<code data-x="dom-Window-close">close()</code>` | Methods include `()`; attributes do not; element interfaces often use `dom-<el>-<member>` (`dom-img-decode`) |
| Event / handler | `<code data-x="event-click">click</code>`, `<code data-x="handler-onclick">onclick</code>` | Scoped events use `event-<group>-<name>` (`event-media-loadstart`) |
| HTTP header | `` `<code data-x="http-last-modified">Last-Modified</code>` `` | Wrapped in literal backticks |

**Example:** [#document-base-url](https://html.spec.whatwg.org/#document-base-url) · [#dom-structuredclone](https://html.spec.whatwg.org/#dom-structuredclone)

### `XREF-STRING-LITERAL` — String literals: `"<code data-x="">text</code>"` and `"the empty string"`
Write code-level string literals as `"<code data-x="">value</code>"` with the quotation marks
*outside* `<code>` and an empty `data-x=""` to suppress autolinking. Compare directly with `"is"` /
`"is not"` (`If <var>type</var> is "<code data-x="">module</code>"`, not `"is the string …"`), write
`"the empty string"` (not `""`), and use `"is an <span>ASCII case-insensitive</span> match for"` or
`<span data-x="string starts with">starts with</span>` for Infra string predicates. Internal parser
token/state descriptions (`"ok"`/`"not ok"`, `a "body" start tag token`) stay as bare quoted words.
**Infra:** [§strings](https://infra.spec.whatwg.org/#strings) (HTML adds `"<code data-x="">…</code>"`)
**Example:** [#create-a-potential-cors-request](https://html.spec.whatwg.org/#create-a-potential-cors-request)
```html
   <li><p>Let <var>mode</var> be "<code data-x="">no-cors</code>" if <var>corsAttributeState</var> is
   <span data-x="attr-crossorigin-none">No CORS</span>, and "<code data-x="">cors</code>" otherwise.</p></li>
```

---

## 3. Definitions (`<dfn>`) (`DFN`)

### `DFN-TYPED` — Use Wattsi's typed `<dfn>` attributes, `for=""`, and `data-x` placement
Mark every non-concept `<dfn>` with its Wattsi type attribute so cross-spec linking works:
`<dfn element>`, `<dfn interface>`, `<dfn dictionary>`, `<dfn enum>`, `<dfn typedef>`,
`<dfn callback>`, `<dfn extended-attribute>`, `<dfn attribute for="I">`, `<dfn method for="I">`,
`<dfn constructor for="I">`, `<dfn dict-member for="D">`, `<dfn enum-value for="E">`,
`<dfn element-attr for="el">`, `<dfn attr-value for="el/attr">`, `<dfn element-state for="el/attr">`,
`<dfn event for="I">`. Plain `<dfn>` is for concepts and algorithms.
- **`for=""` syntax:** comma-separated without spaces (`for="a,area"`); attribute values/states use
  `element/attribute` pairs (`for="img/loading,iframe/loading"` or `html-global/translate`).
- **`data-x` placement:** in prose, place `data-x` on the inner `<code>` (`<dfn attribute for="I"><code data-x="dom-I-x">x</code></dfn>`); inside `<pre><code class="idl">`, place `data-x` on the `<dfn>` itself with no inner `<code>` (`<dfn attribute for="HTMLElement" data-x="dom-lang">lang</dfn>`).
- **Events:** HTML-owned events are defined with `<dfn event for="Interface"><code data-x="event-…">name</code></dfn>` in `#events-2` (or a feature event table); events defined by another spec are imported in `#dependencies` and never redefined with `<dfn event>`.
**Example:** [#dom-img-decoding](https://html.spec.whatwg.org/#dom-img-decoding) · [#dom-lang](https://html.spec.whatwg.org/#dom-lang)
> **Branch**
> 1. **Modern** — typed `<dfn>` with `for=""`, `data-x` on inner `<code>` (prose) or on `<dfn>` (IDL).
> 2. **Accepted** — `data-x` on `<dfn>` wrapping a bare `<code>` in prose (`<dfn method for="DOMStringList" data-x="dom-DOMStringList-item"><code>item(<var>index</var>)</code></dfn>`).
> 3. **Obsolete** — untyped `<dfn><code data-x="…">…</code></dfn>` without `for=""`; add type and `for=""` when touching.

### `DFN-EXPORT` — Export definitions consumed by other specifications
Add `export` on `<dfn>`s referenced by external specs; use `data-lt="alt1|alt2"` for alternate link
texts instead of duplicate `<dfn>`s.
**Example:** [#obtain-a-site](https://html.spec.whatwg.org/#obtain-a-site)

### `DFN-NAMES` — Lowercase imperative verb phrases for algorithms; lowercase noun phrases for concepts
Name algorithms as what they do (`<dfn>parse a URL</dfn>`, `<dfn>obtain a site</dfn>`), with no
leading article and no `"algorithm"` suffix in the `<dfn>` text (hooks for other specs end in
`"steps"`, e.g. `<dfn>removing steps</dfn>`). Name internal concepts as lowercase noun phrases
(`<dfn>close watcher manager</dfn>`), disambiguating collisions with
`data-x="concept-<owner>-<name>"`.
**Example:** [#parse-a-url](https://html.spec.whatwg.org/#parse-a-url) · [#concept-document-navigation-id](https://html.spec.whatwg.org/#concept-document-navigation-id)

### `DFN-NO-FLAGS` — Define new boolean state as a boolean, not a "flag"
Declare new boolean state as `"a boolean <dfn>…</dfn>, initially false"`, tested with `"is true"` /
`"is false"` and mutated with `"set … to true/false"` — never a new `<dfn>… flag</dfn>` that is
`"set"` or `"unset"`. Referencing an existing flag in HTML or another spec (e.g. Fetch's
`use-URL-credentials flag`) in new steps is fine; do not ask to rename existing flags in passing.
**Infra:** [§booleans](https://infra.spec.whatwg.org/#booleans)
**Example:** [#was-created-via-cross-origin-redirects](https://html.spec.whatwg.org/#was-created-via-cross-origin-redirects)
```html
  <p>A <code>Document</code> has a boolean <dfn export>was created via cross-origin redirects</dfn>,
  initially false.</p>
```
> **Branch**
> 1. **Modern** — boolean (`"is true"` / `"is false"`, `"set … to true"`).
> 2. **Legacy** — `<dfn>… flag</dfn>` (`"set"` / `"unset"`, [#click-in-progress-flag](https://html.spec.whatwg.org/#click-in-progress-flag)).

### `DFN-STRUCT` — Structs (`"is a struct with the following items:"` + `<ul>`) and tuples
Define compound state as an Infra struct whose items are a `<ul>` of
`<li><p><dfn data-x="…">Name</dfn>, a TYPE, initially VALUE.</p></li>`, accessed with the possessive
(`<var>manager</var>'s <span>groups</span>`). Tuples (`"is a <span>tuple</span> consisting of …"`)
of any arity are equally fine for small fixed-shape values; prefer a struct when items are mutable,
optional, or numerous.
**Infra:** [§structs](https://infra.spec.whatwg.org/#structs) · [§tuples](https://infra.spec.whatwg.org/#tuples)
**Example:** [#close-watcher-manager](https://html.spec.whatwg.org/#close-watcher-manager)
```html
  <p>Each <code>Window</code> has a <dfn>close watcher manager</dfn>, which is a <span>struct</span>
  with the following <span data-x="struct item">items</span>:</p>

  <ul>
   <li><p><dfn data-x="close watcher manager groups">Groups</dfn>, a <span>list</span> of
```
> **Branch**
> 1. **Modern** — `"…, which is a <span>struct</span> with the following <span data-x="struct item">items</span>:"` + `<ul>`.
> 2. **Accepted** — `"…is a <span>struct</span>. It has the following items:"` + `<dl>` ([#preload-entry](https://html.spec.whatwg.org/#preload-entry)).

---

## 4. Web IDL and element definitions (`IDL`, `ELEM`)

### `IDL-BLOCK` — Place Web IDL in `<pre><code class="idl">` with 2-space indent, no `w-nodev`, and no `<var>`
Interface definitions follow the section heading (or `dl.element`'s `"DOM interface"` `<dd w-nodev>`)
in `<pre><code class="idl">`, with interface-level extended attributes (`[Exposed=Window]`) on the
line before `interface`, 2-space indentation for members, one member per line, and no `<var>` tags.
**Example:** [#the-toggleevent-interface](https://html.spec.whatwg.org/#the-toggleevent-interface)
```html
  <pre><code class="idl">[Exposed=Window]
interface <dfn interface>HTMLHtmlElement</dfn> : <span>HTMLElement</span> {
  [<span>HTMLConstructor</span>] constructor();
```

### `IDL-XREF-SPAN` — Cross-references inside IDL use `<span>`, never `<code>`
Inside `<pre><code class="idl">` (or `<pre class="idl">`), link types, prose-defined members, and
HTML-defined extended attributes (`[<span>CEReactions</span>]`, `[<span>HTMLConstructor</span>]`,
`[<span data-x="xattr-Reflect">Reflect</span>]`, `[<span>LegacyUnforgeable</span>]`) with `<span>` or
`<span data-x="…">`, never `<code>`. Leave Web IDL built-in extended attributes (`[Exposed=…]`,
`[SameObject]`, `[NewObject]`, `[PutForwards=…]`, `[Replaceable]`, `[SecureContext]`) unlinked, and
escape `<` in generics (`<span data-x="idl-Promise">Promise</span>&lt;undefined>`).
**Example:** [#dom-document-hidden](https://html.spec.whatwg.org/#dom-document-hidden)

### `IDL-REFLECT-IN-IDL` — Declare reflected attributes with `[Reflect]` in the IDL when expressible
When an IDL attribute's reflection behavior can be expressed with `[<span data-x="xattr-Reflect">Reflect</span>]`
(and `ReflectSetter`, `ReflectURL`, `ReflectDefault`, `ReflectRange`, `ReflectNonNegative`), put the
`<dfn attribute>` and `[Reflect*]` directly in the IDL instead of writing a reflection paragraph in
prose.
**Example:** [#dom-lang](https://html.spec.whatwg.org/#dom-lang) · [#using-reflect-via-idl-extended-attributes](https://html.spec.whatwg.org/#using-reflect-via-idl-extended-attributes)
```html
  [<span>CEReactions</span>, <span data-x="xattr-Reflect">Reflect</span>] attribute DOMString <dfn attribute for="HTMLElement" data-x="dom-lang">lang</dfn>;
```
> **Branch**
> 1. **Modern** — `[Reflect*]` plus `<dfn attribute>` in the IDL.
> 2. **Accepted** (when `[Reflect*]` cannot express it, e.g. enumerated attributes with `limited to only known values`) — prose: `"The <dfn attribute …>…</dfn> IDL attribute must <span>reflect</span> the … content attribute, <span>limited to only known values</span>."` ([#dom-img-decoding](https://html.spec.whatwg.org/#dom-img-decoding)).

### `IDL-DICTIONARY` — Define dictionary members inline; optional dictionary arguments default to `= {}`
Define `<dfn dict-member for="Dict" data-x="dom-Dict-member">member</dfn>` inline inside the
dictionary block with explicit defaults where applicable. Optional dictionary arguments with no
required members must specify `= {}` (`optional <span>FooOptions</span> options = {}`).
**Example:** [#dom-navigateeventinit-canintercept](https://html.spec.whatwg.org/#dom-navigateeventinit-canintercept)

### `ELEM-DEFINITION` — `<dl class="element">`, content attributes, and index tables
Every element section starts with `<dl class="element">` containing the seven `<dt>` headers in
order: `Categories`, `Contexts in which this element can be used`, `Content model`,
`Tag omission in text/html`, `Content attributes`, `Accessibility considerations`, `DOM interface`.
Define content attributes with `<dfn element-attr for="el"><code data-x="attr-el-name">name</code></dfn>`,
and for enumerated attributes list the keywords (`<dfn attr-value for="el/attr">`) and states
(`<dfn data-x="attr-…-state">`) followed by any `<i data-x="missing value default">missing value
default</i>` / `<i data-x="invalid value default">invalid value default</i>`. Adding an element,
content attribute, or event also updates the index tables at the bottom of `source`.
**Example:** [#the-head-element](https://html.spec.whatwg.org/#the-head-element) · [#lazy-loading-attributes](https://html.spec.whatwg.org/#lazy-loading-attributes)

### `ELEM-DOMINTRO` — Follow author-exposed IDL with `<dl class="domintro">`
Place `<dl class="domintro">` (not `w-nodev`) after author-exposed IDL blocks:
`<dt><code data-x=""><var>obj</var>.<span subdfn data-x="dom-…">member</span>(<var>arg</var>)</code></dt>`,
followed by `<dd><p>…</p></dd>` written in non-normative present tense (`"Returns …"`, `"Throws a
<span>"<code>…</code>"</span> <code>DOMException</code> if …"`), never `"must"`.
**Example:** [#the-htmlformcontrolscollection-interface](https://html.spec.whatwg.org/#the-htmlformcontrolscollection-interface)
```html
  <dl class="domintro">
   <dt><code data-x=""><var>collection</var>.<span subdfn data-x="dom-HTMLCollection-length">length</span></code></dt>
   <dd><p>Returns the number of elements in <var>collection</var>.</p></dd>
```

---

## 5. Algorithm structure and control flow (`ALG`, `FLOW`)

### `ALG-PREAMBLE` — `<div algorithm>` and Infra algorithm declarations
Wrap every algorithm (including single-sentence algorithms) in `<div algorithm>` with no attribute
value, and follow [Infra's algorithm declaration](https://infra.spec.whatwg.org/#algorithm-declaration)
and [parameter](https://infra.spec.whatwg.org/#algorithm-params) conventions:
- **Declaration:** `<p>To <dfn>name</dfn>, given a TYPE <var>x</var>, an optional TYPE <var>y</var> (default VALUE):</p>` (a comma before `"given"` is optional; nullable types are `"TYPE-or-null"`; omit the type only when the `<var>` name makes it obvious).
- **Optional arguments:** list after required parameters with `(default VALUE)` (booleans default to `false`), or test inside the steps with `"If <var>y</var> was not given"`.
- **Return type:** when the return type is not obvious from the `Return` steps, end the preamble with `"…, run these steps. They return a TYPE or failure."` (`"It returns"` is Legacy).
- **External hooks:** when implementing a hook defined in another spec (e.g. DOM `insertion steps`), link the hook with `<span>` instead of `<dfn>`.
**Infra:** [§algorithm declaration](https://infra.spec.whatwg.org/#algorithm-declaration) · [§algorithm parameters](https://infra.spec.whatwg.org/#algorithm-params) (HTML adds `<div algorithm>`, `"TYPE-or-null"`, and `"…, run these steps:"` for event/attribute hooks)
**Example:** [#light-dismiss-open-dialogs](https://html.spec.whatwg.org/#light-dismiss-open-dialogs) · [#parse-a-url](https://html.spec.whatwg.org/#parse-a-url)
```html
  <p>To <dfn>light dismiss open dialogs</dfn>, given a <code>PointerEvent</code> <var>event</var>:</p>
```
> **Branch**
> 1. **Modern** — `"To <dfn>…</dfn>, given …:"` (or `"…, run these steps. They return …."`).
> 2. **Accepted** — `"…, perform the following steps:"`, and `"…, run these steps:"` on non-`<dfn>` hook preambles (`"Whenever X's attribute is added or removed, run these steps:"`).
> 3. **Legacy** — `"…, run the following steps:"`, `"the user agent must run the following steps"`, `"When the user agent is to <dfn>…</dfn>, it must…"`.

### `ALG-ASSERT` — `<span>Assert</span>: condition.`
Write assertions as `<span>Assert</span>: ….` with `<span>` around `Assert`, never bare `Assert:`.
**Infra:** [§assertions](https://infra.spec.whatwg.org/#assertions) (linking `<span>Assert</span>` is HTML's)
**Example:** [#light-dismiss-open-dialogs](https://html.spec.whatwg.org/#light-dismiss-open-dialogs)

### `FLOW-IF-THEN` — `"If <condition>, then <action>."` / `"If <condition>:"` + `<ol>` / `"Otherwise, …"`
Single-sentence conditionals always include `", then"` (`"If <var>x</var> is null, then return."`).
When the consequent has multiple steps, end the lead-in with a colon (`"If <condition>:"`), close
`</p>`, and nest an `<ol>`. Follow-up branches use `"Otherwise, if …, then …"` and `"Otherwise, …"`
(never `"Else"`).
**Infra:** [§conditional statements](https://infra.spec.whatwg.org/#algorithm-conditional-statements) (the colon + nested `<ol>` form is HTML's)
**Example:** [#starting-a-new-parallel-queue](https://html.spec.whatwg.org/#starting-a-new-parallel-queue)
> **Branch**
> 1. **Modern** — `"If <condition>:"` + nested `<ol>`.
> 2. **Legacy** — `"If <condition>, then:"` and `"do the following:"`; do not introduce in new algorithms.

### `FLOW-ANY-ALL` — `"If any/all of the following are true:"` + `<ul class="brief">` + `<p>then …</p>`
When nesting 3+ long or heterogeneous conditions, format them as `<p>If (all|any) of the following
are true:</p>`, a `<ul class="brief">` (or `<ul>`) whose items end with `;`, `; (and|or)` on the
penultimate item, and `,` on the last item, followed by `<p>then …</p>` in the same `<li>`. (Three
short conditions on the same subject that read clearly on one line may stay inline.)
**Example:** [#set-the-frozen-base-url](https://html.spec.whatwg.org/#set-the-frozen-base-url)

### `FLOW-RETURN` — `"Return"` exits an algorithm; `"Abort these steps"` exits a parallel block or substeps
Use `"Return"` / `"Return <var>x</var>."` to exit the algorithm or method. Reserve `"Abort these
steps."` for terminating a set of substeps or `<span>in parallel</span>` steps while continuing the
outer procedure.
**Infra:** [§control flow](https://infra.spec.whatwg.org/#algorithm-control-flow) · [§conditional abort](https://infra.spec.whatwg.org/#algorithm-conditional-abort) (reserving `"abort these steps"` for substeps/parallel blocks is HTML's; see [CONTRIBUTING.md](https://github.com/whatwg/html/blob/main/.github/CONTRIBUTING.md#common-mistakes-around-prose-style))
**Example:** [#parallelism](https://html.spec.whatwg.org/#parallelism)

### `FLOW-SWITCH` — `"Switch on <var>x</var>:"` + `<dl class="switch">`
Multi-way branches on a value use `<p>Switch on <var>x</var>:</p>` followed by `<dl class="switch">`
with `<dt>` cases and `<dd>` bodies (ending with `<dt>Otherwise</dt>` when needed).
**Example:** [#the-embed-element](https://html.spec.whatwg.org/#the-embed-element) · [#the-dir-attribute](https://html.spec.whatwg.org/#the-dir-attribute)
> **Branch**
> 1. **Modern** — `"Switch on <var>x</var>:"` + `<dl class="switch">`.
> 2. **Legacy** — `"Run the appropriate steps from the following list:"`, `"Follow these substeps:"`.

### `FLOW-FOR-EACH` — `"For each <var>item</var> of <var>list</var>:"`
Iterate over lists and maps with `"For each"` (`<span data-x="list iterate">For each</span>` when
linked) and `"of"` (`"For each <var>key</var> → <var>value</var> of <var>map</var>:"`), never `"in"`.
**Infra:** [§iteration](https://infra.spec.whatwg.org/#algorithm-iteration) · [§lists](https://infra.spec.whatwg.org/#list-iterate)
**Example:** [#create-a-potential-cors-request](https://html.spec.whatwg.org/#create-a-potential-cors-request)
> **Branch**
> 1. **Modern** — `"For each <var>x</var> of <var>y</var>"`.
> 2. **Legacy** — `"For each <var>x</var> in <var>y</var>"`.

---

## 6. Variables, values, and state (`VAR`, `VAL`, `STATE`)

### `VAR-LET-SET` — `"Let <var>x</var> be …"` declares once; `"Set <var>x</var> to …"` mutates
Introduce each local variable once per scope with `Let <var>x</var> be …` and mutate it thereafter
with `Set <var>x</var> to …`. Do not reuse the same `<var>` name for two different objects in one
algorithm (a fresh `Let` inside a separate closure or queued task is a new scope and is fine).
Because variables declared inside a nested `<ol>` are not visible outside it, hoist variables
assigned across branches by declaring `Let <var>x</var> be null` in the outer scope first. Every
`<var>` must be scoped by `<div algorithm>`, `<div var-scope>`, `<dl class="domintro">`, or
`<var ignore>`.
**Infra:** [§variables](https://infra.spec.whatwg.org/#variables) (HTML adds `<var>` scoping rules in [CONTRIBUTING.md](https://github.com/whatwg/html/blob/main/.github/CONTRIBUTING.md#var-and-var-scope))
**Example:** [#starting-a-new-parallel-queue](https://html.spec.whatwg.org/#starting-a-new-parallel-queue)

### `VAR-BIND-THEN-TEST` — Bind a repeated expression with `Let` before testing and using it
When a multi-part expression (`<var>moduleMap</var>[(<var>url</var>, <var>type</var>)]'s fetch
options`) is tested in a condition and used again in the consequent, bind it with `Let <var>x</var>
be …` first rather than repeating the chain or referring back to it as `"it"`. Conversely, inline a
`Let` variable that is used only once on the very next line if doing so keeps the step readable
(and never leave an unused `Let` variable without `<var ignore>`).
**Example:** [#fetch-a-single-module-script](https://html.spec.whatwg.org/#fetch-a-single-module-script)

### `VAR-CAMELCASE` — Variable names are camelCase
Write variable names in `<var>camelCase</var>` (`<var>parallelQueue</var>`, `<var>urlRecord</var>`),
without type suffixes like `…Flag` or `…List`.
**Example:** [#set-the-frozen-base-url](https://html.spec.whatwg.org/#set-the-frozen-base-url)
> **Branch**
> 1. **Modern** — `<var>camelCase</var>`.
> 2. **Legacy** — space-separated `<var>date present</var>` ([#parse-a-date-or-time-string](https://html.spec.whatwg.org/#parse-a-date-or-time-string)).
> 3. **Obsolete** — hyphenated `<var>foo-bar</var>`; fix when touching.

### `VAR-THIS` — The receiver is `<span>this</span>`, not `<var>this</var>` or `"this element"`
In IDL getter, setter, and method steps, refer to the receiver as `<span>this</span>`
(`<span>this</span>'s <span>node document</span>`). Bind `Let <var>element</var> be
<span>this</span>` only when passing the receiver into a closure or parallel steps that have their
own `this`.
**Example:** [#dom-domstringlist-length](https://html.spec.whatwg.org/#dom-domstringlist-length)
> **Branch**
> 1. **Modern** — `<span>this</span>`.
> 2. **Legacy** — `"this element"`, `"the element"`.

### `VAL-LIST-OPS` — Infra lists (`« »`) and list verbs linked with `data-x="list …"`
Write list literals with spaces inside guillemets (`« »`, `« <var>a</var>, <var>b</var> »`) and
empty lists as `"an empty <span>list</span>"`. Link list operations to Infra using HTML's
`data-x="list …"` keys: `<span data-x="list append">append</span>`,
`<span data-x="list contains">contains</span>`, `<span data-x="list size">size</span>`,
`<span data-x="list remove">remove</span>`, `<span data-x="list extend">extend</span>`,
`<span data-x="list is empty">is empty</span>` (never `"array"`, `"push"`, or `"length"` in
algorithm steps).
**Infra:** [§lists](https://infra.spec.whatwg.org/#lists) (the `data-x="list …"` keys are HTML's)
**Example:** [#parallelism](https://html.spec.whatwg.org/#parallelism)

### `VAL-MAP-OPS` — Infra maps (`«[ "key" → value ]»`, `<var>map</var>[<var>key</var>]`, `exists`) and dictionary access
Use bracket lookup `<var>map</var>[<var>key</var>]`, `<span data-x="map exists">exists</span>`, and
`<span data-x="map set">set</span> <var>map</var>[<var>k</var>] to <var>v</var>`. Web IDL
dictionaries convert to Infra maps; access their members with a linked member key:
`<var>options</var>["<code data-x="dom-X-y">y</code>"]` (and never check whether a converted value
`"is a dictionary"`).
**Infra:** [§maps](https://infra.spec.whatwg.org/#maps)
**Example:** [#dom-structuredclone](https://html.spec.whatwg.org/#dom-structuredclone)
> **Branch** (dictionary member access)
> 1. **Modern** — `<var>options</var>["<code data-x="dom-StructuredSerializeOptions-transfer">transfer</code>"]`.
> 2. **Legacy** — `"<var>options</var>'s <code>foo</code> member"`.

### `STATE-DECLARATION` — `"Each X has a TYPE <dfn>name</dfn>, initially VALUE."`
Declare per-object state in a single `<p>` giving the owner, type, `<dfn>`, and a trailing
`", initially VALUE."` clause (never a separate `"must"` sentence). Reserve `[[Slot]]` internal
slots for objects with ECMAScript internal methods (`Window`, `Location`, `WindowProxy`); ordinary
platform objects use spec concepts. If the declaring sentence enumerates when the state changes,
update it when adding a new transition.
**Example:** [#was-created-via-cross-origin-redirects](https://html.spec.whatwg.org/#was-created-via-cross-origin-redirects)
> **Branch**
> 1. **Modern** — `"Each X has a TYPE <dfn>name</dfn>, initially VALUE."`
> 2. **Accepted** — `"has an associated <dfn>name</dfn>, which is a TYPE, initially VALUE."`
> 3. **Legacy** — `"has a <dfn>x flag</dfn>, which is initially unset"` (`DFN-NO-FLAGS`).

---

## 7. Invoking algorithms and IDL member prose (`CALL`, `API`)

### `CALL-CONJUGATED` — Conjugate algorithm links inline (`"the result of <span data-x="…">…ing</span>"`) and pass arguments with `"given"`
Invoke algorithms by conjugating the verb inside the link (`"the result of <span data-x="parse a
URL">parsing</span> <var>url</var>"`) or `"running <span>X</span>"`, introducing arguments with
`"given"` (`"given <var>a</var> and <var>b</var>"` — not `"passing"` or `"with … as the argument"`).
Define closures with `"Let <var>steps</var> be the following steps given <var>x</var>:"` and invoke
them with `"run <var>steps</var> given …"`. Call ECMAScript abstract operations with ECMA-262
notation: `Perform ? <span>Call</span>(…)` / `Let <var>n</var> be ! <span>ToUint32</span>(…)`.
**Example:** [#starting-a-new-parallel-queue](https://html.spec.whatwg.org/#starting-a-new-parallel-queue)
> **Branch**
> 1. **Modern** — conjugated link (`"<span data-x="dequeue">dequeuing</span>"`) or `"running <span>X</span> given …"`.
> 2. **Accepted** — `"invoking"` for Web IDL callbacks; `Perform ? <span>Op</span>(…)` for ECMAScript abstract operations.
> 3. **Legacy** — `"applying the <span>X</span> algorithm to"`, bare `"with"` for arguments, and `"…, and let <var>x</var> be the result."`
> 4. **Obsolete** — unconjugated verb after `"the result of"` (`"the result of <span>update …</span>"`); fix when touching.

### `CALL-RELEVANT-OBJECTS` — `"<span>this</span>'s <span>relevant global object</span>"`
Obtain the JavaScript context through the possessive on the platform object being operated on:
`<span>this</span>'s <span>relevant global object</span>`, `<span>this</span>'s <span
data-x="concept-relevant-realm">relevant realm</span>`, `<span>this</span>'s <span>relevant
settings object</span>`. Never introduce `entry` or `incumbent` in new specifications
([whatwg/html#1430](https://github.com/whatwg/html/issues/1430),
[whatwg/html#1431](https://github.com/whatwg/html/issues/1431)).
**Example:** [#parallelism](https://html.spec.whatwg.org/#parallelism) · [#realms-settings-objects-global-objects](https://html.spec.whatwg.org/#realms-settings-objects-global-objects)

### `CALL-IMPERATIVE` — Steps are imperatives; no `"the user agent must"` inside algorithms
Inside `<ol>` algorithm steps the user agent subject is implicit (`"Fire an event…"`, `"Return
<var>p</var>."`). `"The user agent must …"` inside `<ol>` steps is Legacy.
**Example:** [#starting-a-new-parallel-queue](https://html.spec.whatwg.org/#starting-a-new-parallel-queue)

### `API-STEPS-FORM` — `"The <dfn>x</dfn> getter/setter/method/constructor steps are …"`
Specify Web IDL member behavior as `"The <dfn attribute for="X"><code data-x="dom-X-y">y</code></dfn>
getter steps are to return …"` (one-liner) or `"… getter steps are:"` + `<ol>`, and likewise
`"setter steps"`, `"method steps"`, and `"The <dfn constructor for="X"><code data-x="dom-X">new
X(<var>a</var>)</code></dfn> constructor steps are:"`. When a method/attribute name exists on
multiple interfaces in the same section, qualify the interface (`"The <code>Element</code> <dfn …>
setter steps are:"`). Refer to arguments directly by their `<var>` names from the signature, and
test optional IDL arguments with `"If <var>x</var> was not given"`, never `"is undefined"` (unless
the IDL type is `any`). Within a section, order is IDL block → `dl.domintro` → normative prose in
IDL member order.
**Example:** [#dom-domstringlist-item](https://html.spec.whatwg.org/#dom-domstringlist-item) · [#dom-offscreencanvas](https://html.spec.whatwg.org/#dom-offscreencanvas)
```html
  <p>The <dfn method for="DOMStringList" data-x="dom-DOMStringList-item"><code>item(<var>index</var>)</code></dfn> method steps are to
  return the <var>index</var>th item in <span>this</span>'s associated list, or null if
```
> **Branch**
> 1. **Modern** — `"getter/setter/method/constructor steps are"`.
> 2. **Legacy** — `"The <code>x</code> attribute must return …"`, `"On getting, …"`, `"On setting, …"`, `"The <code>x()</code> method, when invoked, must …"`.

### `API-READ-INTERNAL-STATE` — Algorithms read internal state, not Web IDL attribute getters
Algorithm steps must read underlying spec concepts (`<var>img</var>'s <span>current request</span>'s
<span data-x="img-req-url">current URL</span>`) or content attributes (`<var>el</var>'s <code
data-x="attr-…">…</code> content attribute) rather than invoking another Web IDL attribute getter
(`<var>img</var>'s <code data-x="dom-img-currentSrc">currentSrc</code>`).
**Example:** [#dom-img-currentsrc](https://html.spec.whatwg.org/#dom-img-currentsrc)

---

## 8. Tasks, parallelism, and events (`TASK`, `PAR`, `EVT`)

### `TASK-QUEUE-GLOBAL` — `"<span>queue a global task</span> on the <span>X task source</span> given <var>global</var> to …"`
Returning from parallel steps to the event loop always names a task source (reusing an existing
`<dfn>… task source</dfn>` before minting a new one) and the target global (or element via `"<span>queue
an element task</span> on the <span>… task source</span> given <var>element</var> to …"`).
**Example:** [#parallelism](https://html.spec.whatwg.org/#parallelism) · [#queue-an-element-task](https://html.spec.whatwg.org/#queue-an-element-task)
```html
       then <span>queue a global task</span> on the <span>DOM manipulation task source</span> given
       <var>global</var> to reject <var>p</var> with a <code>TypeError</code>, and abort these
       steps.</p></li>
```
> **Branch**
> 1. **Modern** — `"queue a global task"` / `"queue an element task"`.
> 2. **Accepted** — `"<span>queue a microtask</span> to …"` for same-turn microtask continuations.
> 3. **Legacy** — bare `"<span>queue a task</span> to …"` without task source or global.

### `PAR-IN-PARALLEL` — `"Run the following steps <span>in parallel</span>:"` and parallel queues
Start off-main-thread work with `"Run the following steps <span>in parallel</span>:"` (or `"start a
new parallel queue"` + `"enqueue the following steps to <var>queue</var>:"` when work must be
serialized). Inside parallel steps, never touch JavaScript objects or promises, never read live DOM
state, and never throw; hand results back to the event loop via `TASK-QUEUE-GLOBAL`. Blocking with
`"Wait until …"` is valid only inside parallel steps.
**Example:** [#starting-a-new-parallel-queue](https://html.spec.whatwg.org/#starting-a-new-parallel-queue)
> **Branch**
> 1. **Modern** — `"Run the following steps <span>in parallel</span>:"` + `TASK-QUEUE-GLOBAL`, or a parallel queue.
> 2. **Legacy** — `"<span>spin the event loop</span>"`, `"<span>await a stable state</span>"`, and `"synchronous section"` (`⌛` step markers); do not introduce in new algorithms, but editing a `⌛` step inside an existing synchronous section is fine.

### `EVT-FIRE` — `"<span data-x="concept-event-fire">fire an event</span> named <code data-x="event-load">load</code> at <var>target</var>"`
Dispatch events through DOM's `"fire an event"` with a linked event name (`XREF-CODE`), followed by
`"using <code>XEvent</code>, with its <code data-x="dom-XEvent-y">y</code> attribute initialized to
…"` when using a custom `Event` subclass or initializing attributes.
**Example:** [#event-media-addtrack](https://html.spec.whatwg.org/#event-media-addtrack)
```html
     <li><p>If <var>success</var> is true, <span data-x="concept-event-fire">fire an event</span>
     named <code data-x="event-load">load</code> at <var>element</var>.</p></li>
```

---

## 9. Exceptions and promises (`EXC`, `PROM`)

### `EXC-THROW-DOMEXCEPTION` — `throw an <span>"<code>IndexSizeError</code>"</span> <code>DOMException</code>`
Format `DOMException` throws with the quoted name inside a linking `<span>` and `<code>` followed by
`<code>DOMException</code>`, with the article matching the exception name (`an "IndexSizeError"`,
`a "SyntaxError"`). Format JS errors as `"throw a <code>TypeError</code>"` (no trailing
`"exception"`). Make exception catching/rethrowing explicit (`"If this throws an exception, catch
it, and …"`), except when using ECMA-262 `?`/`!`.
**Example:** [#html-element-constructors](https://html.spec.whatwg.org/#html-element-constructors)
```html
     <span>"<code>IndexSizeError</code>"</span> <code>DOMException</code>.</p></li>
```
> **Branch**
> 1. **Modern** — `"throw a <code>TypeError</code>"` / `"throw a <span>"<code>NotSupportedError</code>"</span> <code>DOMException</code>"`.
> 2. **Legacy** — `"throw a <code>TypeError</code> exception"`, `"the user agent must throw …"`.

### `PROM-HANDLING` — Creating, settling, and reacting to promises
- **Creation:** `"Let <var>p</var> be a new promise created in <span>this</span>'s <span data-x="concept-relevant-realm">relevant realm</span>."` (omitting `"created in …"` is Accepted when the realm is unambiguous).
- **Short-circuit return:** `"return <span>a promise rejected with</span> a <span>"<code>NotSupportedError</code>"</span> <code>DOMException</code>"` or `"<span>a promise resolved with</span> undefined"`.
- **Settlement:** `"resolve <var>p</var> with undefined"` (never bare `"resolve <var>p</var>"`) or `"reject <var>p</var> with …"`, always inside a queued task when settling from `<span>in parallel</span>` steps, and `"Return <var>p</var>."` as the outer algorithm's final step.
- **Reactions:** `"<span>Upon fulfillment</span> of <var>p</var>, …"` / `"<span>Upon rejection</span> of <var>p</var>, …"`.
**Example:** [#parallelism](https://html.spec.whatwg.org/#parallelism)
```html
    <li><p>Let <var>p</var> be a new promise created in <span>this</span>'s <span
    data-x="concept-relevant-realm">relevant realm</span>.</p></li>
```

---

## 10. Conformance and vocabulary (`CONF`, `VOC`)

### `CONF-RFC2119` — Lowercase `"must"`/`"should"`/`"may"`; explicit conformance class; `<!-- NON-NORMATIVE SECTION -->`
Write requirement keywords in ordinary lowercase (`must`, `must not`, `should`, `may`), never
capitalized or wrapped in `<em>`. Outside `<ol>` algorithms (`CALL-IMPERATIVE`), name the
conformance class as the sentence subject (`"User agents must …"`, `"Authors must not …"`), except
in attribute/header syntax definitions (`"The x attribute's value must be a valid integer"`). Use
`"web developers"` (not `"authors"`) in notes and `dl.domintro`, and `"JavaScript"` (not
`"ECMAScript"` unless naming ECMA-262 or its terms). Place `<!-- NON-NORMATIVE SECTION -->` on the
line immediately after the heading of informative sections.
**Infra:** [§conformance](https://infra.spec.whatwg.org/#conformance) (the `<!-- NON-NORMATIVE SECTION -->` marker and `"Authors"` / `"User agents"` phrasing are HTML's)
**Example:** [#conformance-requirements](https://html.spec.whatwg.org/#conformance-requirements) · [#semantics](https://html.spec.whatwg.org/#semantics)

### `VOC-NAVIGABLE` — `"navigable"` / `"traversable"`, not `"browsing context"`
Use `<span>navigable</span>`, `<span>top-level traversable</span>`, and
`<span>child navigable</span>` in new prose and algorithms. As the spec's own warning states, avoid
`<span>browsing context</span>` unless specifically dealing with browsing context group switches,
agent clusters, opener relationships, or `WindowProxy`.
**Example:** [#warning-avoid-using-bcs](https://html.spec.whatwg.org/#warning-avoid-using-bcs)
> **Branch**
> 1. **Modern** — `Document` and `navigable` / `traversable` concepts ([#navigables](https://html.spec.whatwg.org/#navigables)).
> 2. **Accepted** — `browsing context` for browsing context groups, agent clusters, opener relationships, and `WindowProxy`.
> 3. **Legacy** — `"browsing context"` / `"top-level browsing context"` where a navigable or traversable is meant.

### `VOC-SAME-ORIGIN` — Predicate `"is <span>same origin</span> with"`; adjective `"same-origin"`
Write the relation as an unhyphenated linked predicate (`"<var>a</var> is <span>same origin</span>
with <var>b</var>"`, `"<span>same origin-domain</span>"`) and hyphenate only when used as an
attributive adjective (`"a same-origin navigation"`).
**Example:** [#same-origin](https://html.spec.whatwg.org/#same-origin)
