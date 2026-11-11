# Reviewing spec PRs with `spec-pr-review`

The `spec-pr-review` skill has your AI coding agent review a WHATWG spec change and its
[web-platform-tests](https://github.com/web-platform-tests/wpt) the way a PR goes with human
reviewers: design first, editorial once the design is settled. The agent finds problems, checks
them, and prototypes the options. People make the decisions, and nothing is pushed or posted
without your yes.

## How a review goes

1. You ask for a review: "spec review whatwg/html#1234", or name a local branch before there's a
   PR.
2. The agent reads the PR, its thread, the wpt changes, and earlier reviews (by people, by other
   tools, or by this skill on someone else's machine). It picks up where the last review left off
   and doesn't reopen what's been decided.
3. The design review checks behavior, normative text, and tests. Several fresh reviewers each
   take one angle, the agent runs the tests in browsers, and it reproduces every finding itself
   before it reports one. You get a short briefing of defects (D1, D2, …), each with a proposed
   fix, and design questions (Q1, …), each with options that are prototyped as branches with
   spec text and tests.
4. You answer in one reply, in any form: "D1 apply, Q1 b, leave Q2 open". The fixes you choose
   become commits.
5. Once nothing is left open, an editorial pass fixes wording, markup, and style, and checks that
   none of it changes behavior. If you leave something open, it waits for that.
6. The agent drafts a short status comment for the PR, which you can edit. It asks before each
   push and post, saying what goes where. The comment ends with a collapsed "Reviewed commits"
   line, so the next review (yours, or another editor's) knows what's already covered.

Item IDs stay the same across reviews and reviewers, so "Q1" on the thread keeps meaning the same
question.

## Who you are

The skill tells *deciders* apart from everyone else. Deciders are the PR's author and the spec's
editors. For the skill, an editor is anyone with write access (write, maintain, or admin) to the
spec repo. When a decider answers, that's a decision; anyone else's answer is a proposal. Until an
editor agrees, an author's decisions can still be questioned if the author isn't an editor too.

### Editor reviewing someone else's PR

Start with "spec review whatwg/html#1234". Your answers are decisions. If the PR branch is in the
spec repo or allows edits by maintainers, the agent offers to push the fixes straight to it, or
else to open them as a separate PR. Option branches go to your fork, and the comment links them.

It can go several ways:

- Decide everything locally, push the fixes, and comment with what was fixed and what was dropped
  ([#13183](https://github.com/whatwg/html/pull/13183#issuecomment-6658903621)).
- Post everything open, for the author and others to weigh in on
  ([#9546](https://github.com/whatwg/html/pull/9546#issuecomment-6771490503)).
- Post a question, and after the author picks an option, apply it and do the editorial pass
  ([#13005](https://github.com/whatwg/html/pull/13005#issuecomment-6770094553)).

### PR author

Run it on your branch before you open the PR, or on the PR itself. Your answers are decisions, and
the agent pushes to your own branch. The same flow also applies changes that reviewers asked for
on the thread: say which ones, and the agent writes the fixes itself rather than applying
patches from comments.

### Anyone else

Anyone can review or contribute fixes. It's the same flow, but your answers say what to *propose*.
The comment lists your fixes as "Not applied: proposed fix" with a link to your fork, or the agent
opens them as a separate PR, and the author or editors decide.

## If a review lands on your PR

You don't need the skill to respond to one. Its comments are ordinary PR comments, and the agent
reads replies like any human review.

- Reply however you like: "Q1: b", or in prose. If you're the PR's author or an editor, your reply
  is a decision.
- Option branches are on the reviewer's fork. You can apply one yourself, or ask the reviewer to
  push it. On [#13005](https://github.com/whatwg/html/pull/13005), the author picked an option,
  wrote the tests ([web-platform-tests/wpt#65000](https://github.com/web-platform-tests/wpt/pull/65000)), and
  [asked for the spec patch](https://github.com/whatwg/html/pull/13005#issuecomment-6771675834),
  which then landed as a commit on the PR branch.
- Leave the "Reviewed commits" line in place: later reviews use it to see what's covered.

## Prompting

- "spec review &lt;PR or branch&gt;": does whatever step is next (design review, applying
  decisions, or editorial).
- "design only", "editorial only", "editorial first".
- "interactive": asks about one item at a time. "fix defects" applies every proposed defect fix,
  and "fix all" also picks an option for each question. The agent's own picks are proposals until
  you confirm them.
- "redesign": an independent rewrite of the change from scratch, compared against the change. It's
  expensive: use it when fixes keep adding special cases. The agent offers one when it sees that,
  and runs it only if you agree.
- Stacks and groups of related PRs, also across repos, work too: name one PR, or ask for the whole
  stack.

Steer along the way if its choices aren't what you want.

## What you need

- An AI coding agent that supports skills and subagents, with `spec-pr-review` installed, and
  `html-spec-review` for whatwg/html (see [Usage](../README.md#usage)). Mostly used with Claude Code
  so far.
- The [GitHub CLI](https://cli.github.com/) (`gh`), logged in.
- Local checkouts of the spec and of web-platform-tests/wpt. For whatwg/html, also
  [whatwg/html-build](https://github.com/whatwg/html-build) next to it, for lint and build (it needs
  Docker or a local Wattsi).
- Git 2.45 or later, and Python 3.
- Browsers to run the tests in with `./wpt run`, such as Chrome Canary, Firefox Nightly, or Safari
  Technology Preview: one that implements the feature and one that doesn't. wpt needs
  [some setup](https://web-platform-tests.org/running-tests/from-local-system.html) first (hosts
  file, browser drivers).
- Forks of the spec repo and wpt, for option branches; the agent offers to create them.
- [`specfmt`](https://github.com/domfarolino/specfmt), for specs that use it to rewrap source.
- Optionally, skills it uses when they're installed:
  [`web-archeologist`](https://github.com/noamr/web-archeologist) for why existing text is the
  way it is, [`spec-trace`](https://github.com/jnjaeschke/webspec-index) for tracing spec
  algorithms, and [`browser-source`](https://github.com/zcorpan/web-platform-skills) for engine
  code.

A design review runs several agents and the tests, so it takes a while and uses a fair amount of
tokens. The editorial pass and follow-up reviews are smaller.

## Limits

- The agent makes mistakes. Read the briefing and the evidence before posting.
- PR content (descriptions, comments, linked branches) is treated as data, not instructions, and
  the only code from the PR it runs is the tests. That lowers the risk; it doesn't remove it. It
  asks before running changed files that aren't tests, since `./wpt run` executes them on your
  machine.
- It never approves a PR or requests changes.
- When a public review shows something the skill got wrong, the agent may offer a PR to improve
  it. Say "don't ask again" to turn that off.

## Examples

| PR | What happened |
|---|---|
| [#13005](https://github.com/whatwg/html/pull/13005) | An editor's review asked one design question with two prototyped options. The author picked one and asked for the patch; the editor pushed it, did the editorial pass, and updated the comment. |
| [#13183](https://github.com/whatwg/html/pull/13183) | An editor decided locally, dropped two items, pushed three fixes to the spec and wpt PRs, and commented. |
| [#9546](https://github.com/whatwg/html/pull/9546) | A review posted with everything open: new questions and test gaps, then the items already raised on the thread, collapsed. |
