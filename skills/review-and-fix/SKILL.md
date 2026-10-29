---
name: review-and-fix
description: Use when asked to review a WHATWG spec PR together with its web-platform-tests PR and then fix the findings yourself, i.e., check out the PR branches, then repeat rounds of review, a fix commit per finding, and self-review until a full round finds only nits or a round raises a new open question (at most ten rounds), then, after asking unless told to, push to the PR branches and post one findings-and-fixes comment. Triggers on "review and fix", "fix your review comments", "fix those things and push", "review the PRs again and fix".
---

# review-and-fix

Workflow for reviewing a spec PR with its wpt PR, fixing what you find on the PR branches, and
reporting back. For what to check in HTML spec text, see `html-spec-review`.

One invocation runs rounds of review, fixing, and self-review in a loop until a stop condition
below holds. Don't push or post between rounds.

## Rounds

- A *full* round reviews the whole PR at its current state, including any tests, run as described
  under Reviewing, and looks closely at what changed since your last posted review. A *delta*
  round reviews only your fix commits since the previous round and how they interact with the
  rest.
- The first and tenth rounds are full, and the tenth also looks closely at the previous round's
  fixes; other rounds are delta rounds, except as below.
- Stop after a round when:
  - it found nothing, or only nits: fix the nits and self-review. If it was a delta round, make
    the next round full instead of stopping, unless it raised a new open question;
  - it raised a new open question, something only the author can decide: finish the round's other
    fixes first; or
  - it was the tenth round: fix its findings, and if it found more than nits and raised no new
    open question, tell the user that the loop didn't converge.
- Problems in your own unpushed fixes aren't reported as separate findings: fix them with a fixup
  commit for that fix (`git commit --fixup`). They still count, at their severity, for the stop
  conditions.
- Items you deliberately leave with the author, in this invocation or an earlier review (findings
  you declined to fix, follow-ups, questions still unanswered), don't count as findings for the stop
  conditions; a new open question still stops the loop. Open findings carried over from an earlier
  review, which you fix, do count.

## Reviewing

- Review your local branches: the PR heads at the start of the invocation plus your fixes. At the
  start, read the comments since your last posted review (all of them, if you haven't posted one).
- The first round's findings include what's still open from your last posted review, or from your
  last draft comment if it wasn't posted: findings neither fixed nor declined, and the answers (the
  author's or the user's) to its open questions.
- For large PRs, split the review across parallel reviewers, and tell them what's already reported,
  fixed, or decided by the author or the user. In delta rounds, give fresh reviewers the diff since
  the previous round. Verify every finding yourself before reporting it.
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

- At the start, use a local branch named after the PR branch with a `-fixes` suffix (adding your
  branch prefix if the PR branch lacks it), and keep using it across rounds; a local branch with the
  PR's name may hold unrelated unpushed commits. If it doesn't exist, create it from the remote PR
  head. Never reset or delete an existing branch. If the `-fixes` branch exists:
  - with your unpushed fixes from earlier in this conversation, continue it. If the remote PR head
    moved, rebase only your fixes onto it (`git rebase --reapply-cherry-picks --empty=stop --onto
    <new head> <the head you built on>`, Git 2.45 or later, so no fix is dropped silently), and if
    that stops, abort it and ask the user;
  - with no unpushed commits, fast-forward it to the remote PR head;
  - otherwise, including when it can't be fast-forwarded, ask the user.
- If a checkout has uncommitted changes to tracked files at the start, or before you switch it, ask
  the user.
- One commit per finding, so each fix can be cited.
- If the obvious fix regresses something and the right behavior is a judgment call, don't change
  behavior; fix any inaccurate notes and ask the PR author in the comment.
- Add a test for every normative spec change, and where possible show it fails against the old
  behavior.
- Waits and cleanups that depend on the behavior under test should time out, so one failure
  doesn't stall the rest of the file.

## Self-review

- In every round, re-read the cumulative diff, then re-lint, rebuild, and rerun the changed tests
  the way you ran them during review, where the repo has them.

## Stop, push, report

- After the loop, squash the fixup commits into their fixes, so each finding has one commit: note
  `HEAD`'s commit ID, then run `git rebase --autosquash <the remote PR head you built on>` (Git 2.44
  or later), which leaves pushed commits alone. If it stops for any reason (a conflict, or a commit
  left empty), abort it with `git rebase --abort`, keep the unsquashed commits, and tell the user.
  Then check that the tree is unchanged; if it isn't, go back with `git reset --hard <noted ID>`
  (the one reset this skill allows) and tell the user.
- Then stop and let the user review locally: list the commits, show the draft comment, and say how
  many rounds ran, why the loop stopped, and which fixes had only self-review: name the findings and
  fixups from the last round and what each changed, since squashing hides that (none if it found
  nothing). Ask before pushing or posting anything, unless the prompt already asked you to.
- If you commit anything while the user reviews, self-review it, add any new finding or open
  question to the draft comment, squash again the same way, and update the cited commits. If the
  draft changed beyond the cited commits, show it again before pushing, unless the user already said
  to push.
- Right before pushing, confirm each PR branch is still at the commit you built on, then push each
  `-fixes` branch to its PR branch as a fast-forward. Never force-push. If either branch moved since
  you built on it, don't push or post anything; tell the user. If a push fails, post nothing; tell
  the user which branches were pushed. Once every push succeeds, or if there's nothing to push,
  switch each checkout back to what it had checked out before you last switched it to the `-fixes`
  branch.
- Post one comment covering findings and fixes from all rounds since your last posted review,
  including fixes from earlier in the conversation that you're pushing, citing the current fix
  commits for each finding or saying why it wasn't changed. Put questions to the author and
  follow-up items in their own section before the findings, not inline, where they're easy to miss.
  Include only what's relevant to the author: leave out how the review was run (rounds, reviewers,
  which fixes were re-reviewed), but keep how the fixes were checked (lint, build, test results).
