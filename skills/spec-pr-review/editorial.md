# Editorial phase

Fix wording, markup, and style in the change without changing what it specifies. Make no
normative change: anything that might be one goes back to the design phase.

## Scope

Text the change touches (`html-spec-review` §12.1):

- spec: the repo's own conventions; for whatwg/html, the editorial sections in
  `html-spec-review`'s phase map and its `html-style-guide.md`;
- wpt: `./wpt lint`, the style items in wpt's `docs/reviewing-tests/checklist.md`, consistency
  with nearby tests, and test and file names.

Test pass conditions and coverage belong to the design phase.

## Baseline

- B: the working branch heads (spec and wpt) at the start of this phase.
- Run the changed test files at B with `--log-wptreport`, in a browser that implements the
  feature and in one that doesn't, where they exist.

## Rounds

At most 3. Each round:

1. **Review.** Fresh reviewers get the diff against the base and the editorial checklists. They
   report editorial issues only, and list anything that looks normative separately. After the
   first round, review only the editorial commits since the previous round.
2. **Fix.** Make a few commits grouped by kind (e.g. markup, prose, IDL formatting, test style).
   Each message says what it fixes; spec commits are prefixed `Editorial: `. Run `specfmt`
   where the repo uses it.
3. **Verify against B.**
   - In the spec checkout, run `python3 <skill-dir>/scripts/check_normative_invariants.py spec
     B HEAD`. Show that each reported difference is editorial.
   - Have a fresh agent, not told why anything changed, compare the before and after text of
     each changed algorithm or normative paragraph (whole algorithms, not just hunks), and the
     assertions of each changed test. It tries to find an input, state, or reading under which
     the behavior differs, or a case a test no longer checks.
   - Rerun the tests in the same browsers with `--log-wptreport`, then run
     `check_normative_invariants.py wpt <before.json> <after.json>`, with `--rename` for renamed
     tests and subtests. It must report no differences.
   - Lint and build.

   Revert any change that fails a check unless you can show it's editorial.

Anything normative that a reviewer or a check turns up (including a real problem a reverted
change exposed) isn't fixed here. Verify it, then add it to the ledger as a defect or question,
without proposal or prototype branches; the next design phase makes those.

Stop when a round finds nothing to fix, or after the third round; then say if it didn't
converge.

## Finish

Squash fixups (see `SKILL.md`), then report: the commits, the checks run and their results, and
any new ledger items. Push as described in `SKILL.md`. There's no comment unless there are new
ledger items; post those as a design comment, if asked. With new items, the next run goes back to
the design phase.
