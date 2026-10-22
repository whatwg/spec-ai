# spec-ai

AI tooling and agent skills for working with WHATWG standards.

## Skills

- **[`html-spec-review`](skills/html-spec-review/SKILL.md)**: Authoring and review guide for the [HTML Standard](https://github.com/whatwg/html). Covers Web IDL cross-references, Infra data structures, variable lifecycle (`Let` vs. `Set`), parser and tree construction edge cases, cross-spec companion PR review, and PR scope discipline. Includes bundled helper scripts in [`skills/html-spec-review/scripts/`](skills/html-spec-review/scripts/):
  - `split_html.py`: Splits `whatwg/html`'s monolithic `source` file at `<h2>` boundaries into section files for targeted reading and editing, and concatenates them back.
  - `check_webidl.py`: Static analyzer for `<pre class="idl">` blocks.
  - `check_algorithms.py`: Static analyzer for `<div algorithm>` blocks and specification markup.
  - `check_wpt_coverage.py`: Audits modified specification sinks and thrown `DOMException`s against Web Platform Tests (WPT).

- **[`review-and-fix`](skills/review-and-fix/SKILL.md)**: Workflow for reviewing a WHATWG spec PR together with its [web-platform-tests](https://github.com/web-platform-tests/wpt) PR, then fixing the findings on the PR branches: one commit per finding, self-review (lint, build, running the tests in browsers that do and don't implement the feature), pushing, and posting a findings-and-fixes comment.

## Usage

Link or install the skills directory into your AI coding agent:

- **Claude Code**:
  ```bash
  ln -s /path/to/spec-ai/skills/html-spec-review ~/.claude/skills/html-spec-review
  ```
- **Gemini CLI / Antigravity**:
  ```bash
  ln -s /path/to/spec-ai/skills/html-spec-review ~/.gemini/skills/html-spec-review
  ```
- **Other agents (Cursor, Windsurf, Copilot, Codex)**: Reference [`skills/html-spec-review/SKILL.md`](skills/html-spec-review/SKILL.md) in your project rules or system instructions.

