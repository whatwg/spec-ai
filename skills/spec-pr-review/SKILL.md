---
name: spec-pr-review
description: Use when asked to review a change to a WHATWG specification, as a spec PR (e.g. whatwg/html#123) or a local spec branch, together with its web-platform-tests changes. Works out from the PR thread, commits, and conversation whether the change needs a design review (normative behavior, with prototyped options for humans to decide) or, once the design is settled, an editorial review and fix pass verified not to change normative behavior. Triggers on "spec review", "review this spec PR", "review the spec change", "spec design review", "spec editorial review", "editorial first". Not for reviewing code that isn't a spec.
---

# spec-pr-review

Reviews a WHATWG spec change and its wpt tests in two phases, the way a spec PR goes with human
reviewers: design first, editorial once the design is settled. Read [`design.md`](design.md) or
[`editorial.md`](editorial.md) for the phase you run. For HTML spec text, see `html-spec-review`;
its phase map says which of its sections belong to which phase.

- Humans decide design. You find problems, lay out options, and prototype them; never pick an
  option or mark an item decided yourself.
- Keep the phases apart: the design phase reports no editorial findings, and the editorial phase
  makes no normative change.
- Leave the PR thread to people: post only when asked, editorial work is commits, not comments,
  and never approve a PR.

## Gather state

Works with or without a PR. Use what exists:

- the spec and wpt branches (local, or the PR heads, fetched as in `html-spec-review` §13.0),
  their commit messages, and the base each forks from;
- existing `-proposed` and `-q<N>-<letter>` branches from earlier runs, and the item IDs in
  their commit messages;
- for a PR: its description, linked issues, companion PRs in other specs, and all comments and
  review threads;
- this conversation.

If the wpt change isn't given, look for it (the PR description, a branch with the same name in
the local wpt checkout). A normative change without tests is a design finding.

## Ledger

Rebuild it on every run. It lists design items: defects (D1, D2, …) and design questions (Q1,
Q2, …). Keep IDs already used in the thread, the conversation, or existing branch names, and
never reuse one; number new ones after the highest. Each item has a one-line statement and a
state:

- *open* (a question) or *proposed* (a defect with a proposed fix not yet applied);
- *decided*: the chosen option or fix and where it's recorded, as a link to a decider's PR
  comment or a commit whose message explains why this option over the others, or *unrecorded*
  (decided in conversation, or a commit without that explanation);
- *declined* or *deferred* (with a link to the follow-up issue).

Deciders are the PR author, the spec's editors, and the user for their own change. Others'
preferences are input, not decisions. If a reply is ambiguous, the item stays open. A human
reviewer's normative concern in an unresolved review thread is an open question too.

An item whose proposal or prototype commit is already on the working branch (`git cherry`, which
matches by patch) is decided, unrecorded unless its commit message explains the choice. Ask the
user about leftover items whose state you can't infer, rather than marking them open.

Recorded decisions are settled; give them to every reviewer as such. Revisit one only with new
evidence (a prototype or test shows it breaks something), as a new question that cites it. An
unrecorded decision may be questioned for a substantive problem; say it may already have been
decided.

The last design review is the latest of: a design review in this conversation, a posted design
comment (its "Reviewed at <sha>" line), a deciders' approval of the design, or the fork point of
existing `-proposed` and `-q*` branches.

## Pick the phase

Run the design phase if any of these hold:

- the change has had no design review;
- commits since the last design review change normative text or test expectations: review only
  those commits, plus the open items;
- an item is open or proposed;
- you're unsure about any of the above: scope the design phase to what's unclear.

Otherwise run the editorial phase. If the design phase ends with no open or proposed items,
continue to the editorial phase in the same invocation, unless it already ran ("editorial
first").

Overrides: "design only"; "editorial only" (say which items are still open, if any); "editorial
first" (cleanup before the design review, then the design phase unless also "only").

Start by saying in one line which phase you're running and why.

## Branches

- The working branch is the change's own branch when the user is its author, before or after
  there's a PR. For someone else's PR, use a local branch named after the PR branch with a
  `-fixes` suffix (adding your branch prefix if the PR branch lacks it), since a local branch
  with the PR's name may hold unrelated unpushed commits. Create it from the remote PR head if it
  doesn't exist. If it exists:
  - with your unpushed commits from earlier in this conversation, continue it. If the remote PR
    head moved, rebase only your commits onto it (`git rebase --reapply-cherry-picks
    --empty=stop --onto <new head> <the head you built on>`, Git 2.45 or later), and if that
    stops, abort it and ask the user;
  - with no unpushed commits, fast-forward it to the remote PR head;
  - otherwise, ask the user.
- Proposal and prototype branches (see `design.md`) start from the working branch, and the wpt
  counterpart gets the same name. If a branch name is taken, add a numeric suffix.
- If a checkout has uncommitted changes to tracked files when you start or before you switch
  it, ask the user. Never reset or delete an existing branch, except as below.
- At the end of every run, pushed or not, switch each checkout back to what it had checked out
  when you started.
- Fix problems in your own unpushed commits with `git commit --fixup`. Before reporting, note
  `HEAD`'s commit ID and run `git rebase --autosquash <the commit you built on>` (Git 2.44 or
  later). If it stops for any reason, abort it, keep the unsquashed commits, and tell the user.
  Then check that the tree is unchanged; if it isn't, `git reset --hard <noted ID>` and tell the
  user.
- Commits you make after reporting, e.g. at the user's request, get the same checks as in their
  phase (`design.md` §7, or `editorial.md`'s verify step) and the same squash.

## Commits

- Follow the repo's commit conventions (for WHATWG specs, whatwg/meta's `COMMITTING.md`).
  Editorial spec commits are prefixed `Editorial: `.
- When applying a decided option, offer to say in the commit message body why this option over
  the others; that records the decision.
- Add a test for every normative spec change, and where possible show that it fails against the
  old behavior.

## Pushing and posting

Ask before pushing or posting anything, unless the prompt already said to.

- **Commits for someone else's PR**, design or editorial: push them to the PR branch only if the
  user is an editor who says to; otherwise offer to open them as a separate PR.
- **Proposal and prototype branches**: push them only if the user agrees, to a repo they can push
  to.
- **Design comment**, once there's a PR: if the user is the PR author, settle what you can with
  them in chat first. Start with "Reviewed at <short sha>" (the spec and wpt heads). Put each
  open or proposed item in the comment body, outside any `<details>`, so the thread can be
  followed in the PR: its ID, the problem with a concrete case, and the options with their
  tradeoffs, or the proposed fix. Supporting material (traces, test runs, links to pushed
  branches) goes in a `<details>` below. Address the people on the PR and ask; don't instruct the
  author. No editorial findings, summaries, or praise. If the user hasn't read the comment before
  it's posted, label it as written by AI.
- **Editorial fixes** get no comment; their commit messages say what they fix.
- Right before pushing, confirm each target branch is still at the commit you built on, then
  push as a fast-forward. Never force-push. If a branch moved, push and post nothing, and tell
  the user. If a push fails, post nothing, and say which branches were pushed.
- Shared infra, once it exists: run only when a person asked for it, name them in anything posted
  (without `@`), and open editorial fixes as a separate PR.
