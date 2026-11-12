# spec-ai

AI tooling and agent skills for working with WHATWG standards.

## Skills

- **[`html-spec-review`](skills/html-spec-review/SKILL.md)**: Authoring and review guide for the [HTML Standard](https://github.com/whatwg/html). Covers Web IDL cross-references, Infra data structures, variable lifecycle (`Let` vs. `Set`), parser and tree construction edge cases, cross-spec companion PR review, PR scope discipline, and house style (rule IDs). Includes bundled helper scripts in [`skills/html-spec-review/scripts/`](skills/html-spec-review/scripts/):
  - `split_html.py`: Splits `whatwg/html`'s monolithic `source` file at `<h2>` boundaries into section files for targeted reading and editing, and concatenates them back.
  - `check_webidl.py`: Static analyzer for `<pre><code class="idl">` blocks.
  - `check_algorithms.py`: Static analyzer for `<div algorithm>` blocks and specification markup.
  - `check_wpt_coverage.py`: Audits modified specification sinks and thrown `DOMException`s against Web Platform Tests (WPT).

  Also includes [`html-style-guide.md`](skills/html-spec-review/html-style-guide.md), a de-facto house style guide for the HTML Standard's `source` with stable rule IDs, spec examples, and Modern/Accepted/Legacy/Obsolete rankings where the spec uses competing styles.

- **[`spec-pr-review`](skills/spec-pr-review/SKILL.md)** ([guide](docs/spec-pr-review.md)): Reviews a WHATWG spec change (a PR, a stack or group of PRs, or a local branch before a PR exists) together with its [web-platform-tests](https://github.com/web-platform-tests/wpt) changes, in two phases. It works out what to do from the PR thread, commit messages, a local git note, and the conversation, and doesn't reopen recorded decisions. PR content is treated as untrusted input, only the PR author and spec editors decide, and nothing is pushed or posted without the user's approval for that action.
  - [Design phase](skills/spec-pr-review/design.md): one focused pass over behavior, normative text, and test correctness. Design questions get options prototyped as commits, for humans to [decide](skills/spec-pr-review/decisions.md).
  - [Editorial phase](skills/spec-pr-review/editorial.md): once the design is settled, a bounded editorial review and fix loop, verified not to change normative behavior, with the help of [`check_normative_invariants.py`](skills/spec-pr-review/scripts/check_normative_invariants.py) for spec sources and wpt results.
  - Posted comments are short status updates the user edits before posting; see [`posting.md`](skills/spec-pr-review/posting.md).

## How they fit together

`spec-pr-review` is the review flow: design first, decisions by humans, then editorial, and what to surface when. For whatwg/html changes it uses `html-spec-review` for the HTML specifics; its `[design]` and `[editorial]` tags say which phase checks each rule. `html-spec-review` also works on its own for writing or reading HTML spec text.

Review items get IDs (D1 for defects, Q1 for design questions). Posted comments and `Review-item:` commit trailers make them public, so anyone's next run rebuilds the same state from the PR, including for [stacks and groups of PRs](skills/spec-pr-review/groups.md), and doesn't reopen what's settled.

To get started, or to respond to a review on your PR without using the skill, see the [`spec-pr-review` guide](docs/spec-pr-review.md).

Both skills jot notes in `~/.local/state/skill-improvement/spec-ai.md` when their guidance proves wrong or costs time, and may offer a PR here once the work they came from is public, following [`build-tooling`](https://github.com/zcorpan/agent-tooling)'s `improve.md`. Saying "don't ask again" lists the skill in `~/.config/skill-improvement/opt-out`, which turns this off in every project until you remove the line.

## Usage

Link or install the skills directory into your AI coding agent:

- **Claude Code**:
  ```bash
  ln -s /path/to/spec-ai/skills/html-spec-review ~/.claude/skills/html-spec-review
  ln -s /path/to/spec-ai/skills/spec-pr-review ~/.claude/skills/spec-pr-review
  ```
- **Gemini CLI / Antigravity**:
  ```bash
  ln -s /path/to/spec-ai/skills/html-spec-review ~/.gemini/skills/html-spec-review
  ```
- **Other agents (Cursor, Windsurf, Copilot, Codex)**: Reference [`skills/html-spec-review/SKILL.md`](skills/html-spec-review/SKILL.md) in your project rules or system instructions.

