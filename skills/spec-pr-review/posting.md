# Pushing and posting

## Approval

- Every push, comment, comment edit, and remote branch deletion needs the user's yes for that
  action: what (commits, branches, the comment text) and where (repo, branch, PR).
- A yes covers only what was listed when it was given. Branches or commits created later,
  another target, or changed comment text need a new yes. A "push" or "post" in the user's
  request covers only the targets and content it names.
- Push, post, and draft nothing while an agent or test run you started is still running, even
  if the user asks: say which are, and wait for them.
- Ask in one line where you can, e.g. "Push 3 commits (abc1234..def5678) to `foo` on
  `whatwg/html` (#123)?"

## Pushing

- **The user's own PR**: the working branch to its PR branch.
- **Someone else's PR, the user a decider who can push to it** (write access to the spec repo,
  and the branch is in the spec repo or the PR allows edits by maintainers): ask `Push <n>
  commits to <PR branch>?`, offering a separate PR as the alternative.
- **Someone else's PR, otherwise**: offer to push the commits to the user's fork and open a
  separate PR.
- A wpt PR goes by the same cases, with write access to wpt in place of the spec repo.
- **Proposal and prototype branches**: only to the user's fork, never to the spec's or wpt's own
  repo, even if the user can push there; only when a comment links them. When offering a
  comment with fixes or options not applied, ask whether to push and link their branches or
  post without them. A draft can link them before they exist; push them after the yes, before
  posting. If there's no fork, offer to create one (`gh repo fork --remote=false`).
- Never push notes refs.

Right before pushing, confirm each target branch is still at the commit you built on, then
push as a fast-forward. Never force-push. If a branch moved, push and post nothing, and tell the
user. If a push fails, post nothing, and say which branches were pushed.

## Comments

Comments go on spec PRs only, never on wpt PRs, as a regular PR comment, not a review. The
user owns the comment:

- Draft it, show it, and let the user edit it or add to it. Post their final text unchanged.
- Before pushing anything that carries new IDs, refetch the thread. If IDs were posted since
  you numbered your new items, renumber them after the highest, with their branches and the
  trailers of your unpushed commits, and ask again with the change shown.
- Push what the comment refers to first: call a commit a fix only once it's on the PR branch.
- After posting, refetch once. If an earlier comment took the same new IDs for other items,
  offer to edit yours to renumber, saying which pushed commits carry the old ID (posted IDs
  win over trailers), and rename your branches for those items (locally, and on the fork by
  pushing the new name and deleting the old).
- Update rather than add: when the user's own comment on the PR goes stale (fixes applied,
  editorial commits pushed) and nobody has commented, reviewed, or approved since, offer to
  edit it (`gh api -X PATCH repos/<owner>/<repo>/issues/comments/<id>`). Otherwise, or for
  new items that need people's attention, post a new comment.

Content: a short status update, then what needs input. If a fix isn't on the spec or wpt PR
branches yet, or a question is open, the first line says which, e.g. "Not applied yet: D1 and
D2. Open: Q1." Put items first raised in this review at the top; items already raised on the
thread go after them in a `<details>`, for book-keeping, each linking the comments that raised
it. When there are both, start the new ones with "New in this review:". For each item:

- the ID with a colon, not bold (e.g. "Q1: …"), and the problem with a short concrete case;
  for an item someone else raised, link their comments and name them without `@`;
- its state, in words that can't be mistaken:
  - `Fixed in <sha>`, only for a commit on the PR branch;
  - `Not applied: proposed fix <link to the fork branch>`, or without branches `Not applied:
    suggested fix: <what it changes, in one sentence>`; "Open, no fix yet";
  - `Applied in <sha>, would like confirmation from <people>`;
  - "Kept as is", "Declined", or "Dropped", with the reason in one sentence; `Deferred to
    #<N>`; `Moved to #<N> Q<M>`;
  - for a question: the question and one line per option, with tradeoffs and prototype links,
    then the evidence in one `<details>` after the options.

Also:

- Backticks in this file only mark templates. In the comment, write SHAs, `#<N>`, and
  `owner/repo#<N>` without backticks, or they don't autolink.
- Use short SHAs (7 characters) everywhere, the "Reviewed at" line included. Link same-repo
  commits by short SHA and other repos' commits by full URL, but leave the "Reviewed at" line's
  SHAs unlinked. Link branches only for fixes and options that aren't applied, once pushed.
- Without branches, don't mention branches, prototypes, forks, or commits not on a PR branch;
  give what prototyping revealed as tradeoffs.
- Include test results only as evidence for an item, such as a browser behaving differently.
- No behavior delta list, summary of the change, editorial findings, cleanup, local paths, or
  praise. Address the people on the PR and ask; don't instruct the author.
- End with the "Reviewed at" line, collapsed (one `web-platform-tests/wpt#<N> at <sha>` per open
  wpt PR; for tests already merged, `web-platform-tests/wpt@<sha>` at the commit you ran; none
  if there are no tests). Keep the blank line, or GitHub doesn't autolink inside:

  ```
  <details><summary>Reviewed commits</summary>

  Reviewed at <spec short sha> on <base short sha>, with web-platform-tests/wpt#<N> at <short sha>, using spec-pr-review.
  </details>
  ```

  Later runs rely on this line; if the user's edit removes it, say so.
- After a design review that found nothing, offer a comment with just "No design issues
  found." and that `<details>`.
- In a group, see [`groups.md`](groups.md) §Posting.

## Shared infra

Once shared infra exists: run only when a person asked for it, name them in anything posted
(without `@`), label it as written by AI unless they edited it, and open editorial fixes as a
separate PR.
