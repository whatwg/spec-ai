# Branches, commits, and checkouts

## Checkouts

- Work in the user's spec and wpt checkouts.
- To have two states at once (a build or test run at the baseline, a prototype), use
  `git clone --shared <checkout> <temp dir>`, not `git worktree`: html-build's `build.sh` needs
  `.git` to be a directory. Fetch commits back with `git fetch <temp dir> <branch>:<branch>`,
  and delete the clone when done.

## Names

Name every branch you create `<prefix>spec-review/<key>/<name>`, where `<prefix>` is the user's
branch prefix if they use one, and `<key>` is `<repo>-<N>` for a PR (e.g. `html-12345`) or the
local branch name (with `/` replaced by `-`) before there's a PR. A proposal or prototype
branch's wpt counterpart, or a wpt-only fix, gets the same name. A wpt PR's own working branch
is keyed by that wpt PR (`wpt-<N>/fixes`), since one wpt PR can serve several spec PRs.

- `fixes`: the working branch for someone else's PR;
- `d<N>`: the proposed fix for defect `D<N>`;
- `q<N>-<letter>`: option `<letter>` of question `Q<N>`.

If a name is taken, add a numeric suffix.

## Working branch

- The user's own change, before or after there's a PR: their branch, synced with the PR head
  ([`state.md`](state.md) §Sync).
- Someone else's PR: `fixes`. Create it from the PR head if it doesn't exist. If it exists:
  - with your unpushed commits from earlier in this conversation, continue it. If the PR head
    moved, rebase only your commits onto it (`git rebase --reapply-cherry-picks --empty=stop
    --onto <new head> <the head you built on>`, Git 2.45 or later), and if that stops, abort
    it and ask the user;
  - with no unpushed commits of yours, move it to the PR head, also after a force-push;
  - otherwise, or if you can't tell, ask the user.
- Never reset or delete an existing branch, except as described here.

## Proposal and prototype branches

- Start them from the working branch, one commit per defect, and commits (spec and tests) per
  option.
- When the working branch moves (new commits, a force-push), rebase them onto it. If that
  conflicts in normative text or tests, don't resolve it by hand: rebuild the fix or option on
  the new head, verify it again, and say so.

## Commits

- Follow the repo's commit conventions (for WHATWG specs, whatwg/meta's `COMMITTING.md`).
- Give every commit for a ledger item a `Review-item: <ID>` trailer (`Review-item: Q2 b` on a
  prototype). Later sessions find applied items by it, even after a rebase changes patch IDs.
- Add a test for every normative spec change, and where possible show that it fails against the
  old behavior. If nothing can observe the change, say so in the item instead.
- Fix problems in your own unpushed commits with `git commit --fixup`.

## Finish

At the end of every run, pushed or not:

- On each branch you made fixups on, note its head and run `git rebase --autosquash <the commit
  you built on>` (Git 2.44 or later). If it stops for any reason, abort it, keep the unsquashed
  commits, and tell the user. Then check that the tree is unchanged; if it isn't, `git reset
  --hard <noted ID>` and tell the user.
- Read each of your commits (`git show`) and check that its message describes exactly its diff:
  nothing it describes is missing, and nothing in the diff is undescribed. Fix mismatches.
- Before there's a PR, combine your applied and editorial fixes into one commit by default,
  keeping every `Review-item:` trailer, and offer to fold it into the user's own commits.
- Write the local record ([`state.md`](state.md) §Local record).
- Switch each checkout back to what it had checked out at the start.

Commits you make after reporting, e.g. at the user's request, get the same checks as in their
phase and the same finish.

## Cleanup

Keep your branches at least until their PR is merged or closed, so others can review the
options behind a decision. After rebuilding the ledger, list them (`git branch --list
'*spec-review/*'` in each checkout, and the same pattern in the user's fork). A branch can go
only when all of these hold:

- every PR it serves is merged or closed: its key's PR, and PR N for an `-on-<N>` branch. For a
  local key, the branch it's named after no longer exists and no PR was opened from it;
- it holds no item that's open or proposed in any ledger;
- it isn't the head of an open PR (e.g. a separate PR opened from the fork);
- every commit on it that isn't in the PR's final head has a `Review-item:` trailer.

Ask once, listing the local and fork branches, then delete them, along with
`refs/spec-review/pr/<N>` refs of closed PRs and leftover shared clones. Mention any branch you
kept, and why.
