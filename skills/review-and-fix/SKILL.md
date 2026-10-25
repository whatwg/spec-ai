---
name: review-and-fix
description: Use when asked to review a WHATWG spec PR together with its web-platform-tests PR and then fix the findings yourself, i.e., check out the PR branches, then repeat rounds of review, a fix commit per finding, and self-review until a round comes back clean, push to the PR branches, and post one findings-and-fixes comment. Triggers on "review and fix", "fix your review comments", "fix those things and push", "review the PRs again and fix".
---

# review-and-fix

Workflow for reviewing a spec PR with its wpt PR, fixing what you find on the PR branches, and
reporting back. For what to check in HTML spec text, see `html-spec-review`.

One invocation runs rounds of review, fixing, and self-review in a loop until a stop condition
below holds. Don't push or post between rounds.

## Rounds

- A *full* round reviews the whole PR at its current state, spec and tests, running the tests as
  described under Reviewing. A *delta* round reviews only what changed since the previous round
  (your fix commits, or in a first round, commits the author pushed since your last posted review)
  and how it interacts with the rest.
- The first round is full, unless your review was posted in an earlier invocation; then it may be a
  delta round over the commits since that review. Later rounds are delta rounds, except as below.
- Stop after a round when:
  - it found nothing, or only nits: fix the nits and self-review, without another delta round;
  - it raised a new open question, something only the author can decide: finish the round's other
    fixes first; or
  - it was the fifth round: report that the loop didn't converge.
- But before stopping, make sure the invocation included a full round. If not, run one now and fix
  what it finds; keep looping only if it finds more than nits and no round in this invocation
  raised a new open question.
- Never run more than five rounds. If four rounds pass without a full round, make the fifth full.
- Problems in your own unpushed fixes aren't reported as separate findings: fix them, and cite every
  fix commit on the original finding. They still count, at their severity, for the stop conditions.

## Reviewing

- Review from the current PR heads plus your unpushed fixes, after reading comments since the last
  round.
- For large PRs, split the review across parallel reviewers, and tell them what's already reported,
  fixed, or decided by the author. In delta rounds, give fresh reviewers the diff since the previous
  round. Verify every finding yourself before reporting it.
- Reading misses things that running catches:
  - Run every test file where the feature is implemented, and look for harness errors and
    timeouts, not just failures.
  - Run them where it isn't implemented. Subtests that pass there may not be able to fail.
  - Scan inline scripts for a literal `</script>`; it ends the script element.
- A failing test is a finding only if it contradicts the spec, can't fail, is flaky, leaks state,
  or stalls the file. Otherwise it's an implementation gap.
- Classify each verified finding as a blocker, suggestion, or nit; the stop conditions depend on it.
- Say so if one of your own earlier suggestions caused a problem.

## Fixing

- At the start of the invocation, create a fresh local branch from the remote PR head, and keep
  using it across rounds; a local branch with the PR's name may hold unpushed commits.
- One commit per finding, so each fix can be cited.
- If the obvious fix regresses something and the right behavior is a judgment call, don't change
  behavior; fix any inaccurate notes and ask the PR author in the comment.
- Add a test for every normative spec change, and where possible show it fails against the old
  behavior.
- Waits and cleanups that depend on the behavior under test should time out, so one failure
  doesn't stall the rest of the file.

## Self-review

- In every round, re-read the cumulative diff, then re-lint, rebuild, and rerun the changed tests
  the way you ran them during review.

## Stop, push, report

- After the loop, stop and let the user review locally: list the commits, show the draft comment,
  and say how many rounds ran and why the loop stopped. Ask before pushing or posting anything,
  unless the prompt already asked you to.
- Right before pushing, confirm each PR branch is still at the commit you built on, then push as a
  fast-forward. Never force-push. If either branch moved since you built on it, push and post
  nothing; tell the user.
- Post one comment covering findings and fixes from all rounds, citing the fix commits for each
  finding or saying why it wasn't changed. Put questions to the author and follow-up items in
  their own section before the findings, not inline, where they're easy to miss.
