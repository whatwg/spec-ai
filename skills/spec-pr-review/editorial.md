# Editorial phase

Fix wording, markup, and style without changing what the change specifies. Make no normative
change: anything that might be one goes to the ledger, not into a commit.

## Scope

- Text the change touches (`html-spec-review` §12.1, and §12.2 except its logic-bug items).
- Non-normative text anywhere that the change makes stale: introductions, notes, domintro,
  examples, and cross-references that still describe the old behavior (`html-spec-review`
  §13.5). Updating it to match the change is editorial.
- Editorial concerns from the thread ([`state.md`](state.md) §Human concerns).
- Spec style: the repo's own conventions; for whatwg/html, the editorial sections in
  `html-spec-review`'s phase map and its `html-style-guide.md`.
- wpt: `./wpt lint`, the style items in wpt's `docs/reviewing-tests/checklist.md`, consistency
  with nearby tests, and test and file names.

Test pass conditions and coverage belong to the design phase.

A finding is *possibly normative* only if fixing it could change what a conforming
implementation does or what a test checks. Normative text elsewhere that still assumes the old
behavior is one. Before raising one, compare with the base: if the problem predates the change,
it goes in the "Not this change's" list ([`design.md`](design.md) §5), with its issue if one
exists.

## Baseline

- B: the working branch heads (spec and wpt) at the start of this phase.
- Run the changed test files at B with `--log-wptreport`, in a browser that implements the
  feature and in one that doesn't, where they exist.
- To build or run tests at B while you work, use a shared clone ([`git.md`](git.md)
  §Checkouts).

## Rounds

At most 3. Each round:

1. **Review.** Fresh reviewers get the diff against the base, the commit messages, the
   stale-text scope, and the editorial checklists. They report editorial issues only, and list
   anything possibly normative separately. After the first round, review only the editorial
   commits since the previous round.
2. **Fix.** Make a few commits grouped by kind (e.g. markup, prose, IDL formatting, stale
   notes, test style). Each message says what it fixes; spec commits are prefixed `Editorial: `.
   Run `specfmt` where the repo uses it.
3. **Verify against B.**
   - In the spec checkout, run `python3 <skill-dir>/scripts/check_normative_invariants.py spec
     B HEAD`. Show that each reported difference is editorial.
   - Have a fresh agent, not told why anything changed, compare the before and after text of
     each changed algorithm or normative paragraph (whole algorithms, not just hunks), and the
     assertions of each changed test. It tries to find an input, state, or reading under which
     the behavior differs, or a case a test no longer checks.
   - Rerun the tests in the same browsers with `--log-wptreport`, then run
     `check_normative_invariants.py wpt <before.json> <after.json>`, with a `--map` for each
     test or subtest you renamed or moved. Use a map the script suggests only if it matches a
     rename or move you made. It must report no differences.
   - Check each commit's message against its diff ([`git.md`](git.md) §Commits).
   - Lint and build.

   Revert any change that fails a check unless you can show it's editorial.

Anything normative that a reviewer or a check turns up (including a real problem a reverted
change exposed) isn't fixed here. Verify it, then add it to the ledger as a defect or question,
as in [`design.md`](design.md) §5; the flow takes it to the design steps next.

Stop when a round finds nothing to fix, or after the third round; then say if it didn't
converge.

## Finish

Report the commits, the checks run and their results, new ledger items, and the "Not this
change's" list. Push as in [`posting.md`](posting.md). Editorial fixes get no comment of their
own; if the user's design comment on the PR now names an old head, offer to update it
([`posting.md`](posting.md) §Comments).
