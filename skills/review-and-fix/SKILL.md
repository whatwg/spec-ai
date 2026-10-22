---
name: review-and-fix
description: Use when asked to review a WHATWG spec PR together with its web-platform-tests PR and then fix the findings yourself, i.e., check out the PR branches, find issues, commit a fix per finding, self-review, push to the PR branches, and post a findings-and-fixes comment. Triggers on "review and fix", "fix your review comments", "fix those things and push", "review the PRs again and fix".
---

# review-and-fix

Workflow for reviewing a spec PR with its wpt PR, fixing what you find on the PR branches, and
reporting back. For what to check in HTML spec text, see `html-spec-review`.

## Reviewing

- Review from the current PR heads, after reading comments since the last round.
- For large PRs, split the review across parallel reviewers, and tell them what's already reported
  or decided by the author. Verify every finding yourself before reporting it.
- Reading misses things that running catches:
  - Run every test file where the feature is implemented, and look for harness errors and
    timeouts, not just failures.
  - Run them where it isn't implemented. Subtests that pass there may not be able to fail.
  - Scan inline scripts for a literal `</script>`; it ends the script element.
- A failing test is a finding only if it contradicts the spec, can't fail, is flaky, leaks state,
  or stalls the file. Otherwise it's an implementation gap.
- Say so if one of your own earlier suggestions caused a problem.

## Fixing

- Work on a fresh local branch from the remote PR head; a local branch with the PR's name may hold
  unpushed commits.
- One commit per finding, so each fix can be cited.
- If the obvious fix regresses something and the right behavior is a judgment call, don't change
  behavior; fix any inaccurate notes and ask the PR author in the comment.
- Add a test for every normative spec change, and where possible show it fails against the old
  behavior.
- Waits and cleanups that depend on the behavior under test should time out, so one failure
  doesn't stall the rest of the file.

## Self-review, push, report

- Re-read the cumulative diff, then re-lint, rebuild, and rerun the changed tests the way you ran
  them during review.
- Then stop and let the user review locally: list the commits and show the draft comment. Ask
  before pushing or posting anything, unless the prompt already asked you to.
- Right before pushing, confirm each PR branch is still at the commit you built on, then push as a
  fast-forward. Never force-push.
- Post one comment covering findings and fixes, citing the fix commit for each finding or saying
  why it wasn't changed. Put questions to the author and follow-up items in their own section
  before the findings, not inline, where they're easy to miss.
