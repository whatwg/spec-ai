# Design phase

Find what's wrong with the behavior the change specifies, and set up the decisions humans need
to make. One pass, no round loop. Report no editorial findings (wording, markup, style), except
where an editorial problem makes the normative meaning ambiguous.

## 1. Context

Read the PR description, linked issues and their discussion, companion spec PRs, the wpt
change, and the ledger. Before questioning existing text the change builds on, find out why it
is the way it is (`web-archeologist` if available). Where compat or implementability matters,
check what engines do (`browser-source` if available).

## 2. Behavior delta list

For each observable behavior the change affects, write the old and the new behavior: return
values, exceptions, events and their order, state, timing, rendering. Also list what is
deliberately unchanged, and the sibling entry points that share the changed algorithms. Check the
list against the stated intent; a mismatch is a finding. Everything below is checked against this
list. In a run scoped to new commits, cover only those.

## 3. Parallel reviewers

Use fresh agents, told to be adversarial. Give each the diffs, the delta list, the ledger
(decided items marked as settled), and one lens, but not your own findings. Tell them to report
only behavior, normative, and test-correctness issues, each with a concrete case (input and
wrong outcome), and to drop editorial ones. For a small change, one reviewer can take several
lenses; skip lenses that don't apply.

- **Design and intent**: does it solve the issue; alternatives; consistency with the rest of the
  platform; compat and implementer status; security and privacy.
- **Algorithm correctness**: call sites, null and fallback paths, re-entrancy, parser contexts,
  state snapshots (`html-spec-review` §2.5, §§3–6).
- **Tests** (`html-spec-review` §14):
  - Run every test file where the feature is implemented, and look for harness errors and
    timeouts, not just failures. Run them where it isn't implemented too: subtests that pass
    there may not be able to fail.
  - Every behavior delta needs a test that can fail, and expectations follow the spec, not an
    engine.
  - Look for flakiness, leaked state, and stalls: waits and cleanups that depend on the behavior
    under test should time out. Scan inline scripts for a literal `</script>`.
  - A failing test is a finding only if it contradicts the spec, can't fail, is flaky, leaks
    state, or stalls the file; otherwise it's an implementation gap.
- **Cross-spec contracts** (`html-spec-review` §13.2).

## 4. Verify

Reproduce every finding yourself, by tracing the spec (`spec-trace` if available) or running a
test, and drop what you can't. Merge findings that share a root cause (`html-spec-review`
§13.4). Drop findings that re-raise a settled decision without new evidence.

## 5. Classify and prototype

Start each proposal and prototype commit message with its item ID (e.g. `D2: …`, `Q1 option B:
…`), so later runs can tell which items they belong to.

- **Defect** (D<N>): wrong behavior with one sensible fix, because the intent is clear and only
  one behavior fits it. Write the fix, with its tests, as one commit per defect on
  `<working branch>-proposed`, so each can be applied on its own.
- **Design question** (Q<N>): more than one reasonable behavior, or unclear intent. A fix that
  would change behavior engines agree on is a design question too.
  - Write 2–3 options, including "keep as is" if it's viable.
  - Prototype each option as commits, spec and tests, on `<working branch>-q<N>-<letter>`;
    implementing an option is how you find what's wrong with it. Check each prototype against the
    delta list, the call sites, and the tests in browsers.
  - Record what prototyping revealed, and revise or drop options that fall apart, saying why.
  - For each option, give the tradeoffs: compat, implementer cost, consistency with the
    platform, ergonomics for authors, spec complexity. Don't recommend one; give a lean only if
    asked, labeled as yours.

## 6. Briefing

Report in chat, then stop:

- the phase, its scope, and "Reviewed at <short sha>" for the spec and wpt heads;
- the behavior delta list, briefly;
- defects: the problem with its concrete case, and the proposed commit;
- questions: the problem with its concrete case, options with tradeoffs, prototype branches,
  and what prototyping revealed;
- the ledger's decided, declined, and deferred items, with where each decision is recorded, or
  "unrecorded";
- "Editorial review deferred until the design is settled."

If there's a PR, offer to post a design comment (see `SKILL.md`).

## 7. Applying decisions

When a decider decides:

- Cherry-pick the chosen prototype or proposed fix, with its tests, onto the working branch,
  offer to explain the choice in the commit message, and update the ledger.
- Have one fresh agent check the applied commits against the delta list, and rerun the affected
  tests. Fix problems in your own commits with fixups; anything that needs a decision is a new
  item.
