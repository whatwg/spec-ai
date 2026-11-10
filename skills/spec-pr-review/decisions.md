# Decisions

## Modes

The user's words pick the mode. The default is *ask*. If the user's words don't clearly name
a mode (e.g. "apply all"), list what each mode would do here and ask.

- *ask*: end the briefing with one line per item needing a decision, e.g. `D1: apply, decline,
  or leave open` and `Q2: a, b, keep as is, or leave open`. The user answers in one reply, in
  any form; items they don't mention stay as they are.
- *interactive*: ask about one item at a time, with the same choices.
- *fix defects*: apply every proposed defect fix, and ask about questions as in *ask*.
- *fix all*: also apply, for each question, the option you'd pick, with one line on why.

Bulk modes skip items first raised by anyone other than the user or a decider, unless the user
names them. What you apply without the user's explicit choice (in *fix defects* and *fix all*)
is a proposal, not a decision:

- It stays *proposed* until the user confirms it, so the flow's Decide step lists each such
  item, one line each with what you applied and why, before the editorial phase and before
  anything is pushed or posted. Revert what the user rejects.
- Your reasons never go into a commit message as a decision record; only the reason the user
  confirms does.

Before pushing, any decision can be changed or made open again: drop or replace its commit. A
decider can also have a fix applied but left for others to confirm (*applied, awaiting
confirmation*). If the user isn't a decider, their choices are proposals to the deciders: posted
as not applied, or opened as a separate PR ([`posting.md`](posting.md)).

## Decisions from the thread

For decisions found on GitHub ([`state.md`](state.md) §Deciders) but not applied, list each
item, the decider's login, a link, and the outcome, and apply them after the user's yes. Apply
only items the user has seen in this conversation's briefing or list.

## Applying

- Apply only from your own proposal and prototype branches, or write the fix fresh on the
  working branch.
- Cherry-pick the chosen commits, spec and tests, onto the working branches. On a conflict in
  normative text or tests, see [`git.md`](git.md) §Proposal and prototype branches.
- Set the `Review-item:` trailer to the item's ID, and offer to add the decider's reason for
  this option over the others to the message body; that records the decision.
- With a PR, keep one commit per item, so each can be cited as "Fixed in <sha>", and offer to
  squash related small fixes that don't need separate review into one commit with all their
  trailers. Before a PR, they're combined at finish ([`git.md`](git.md) §Finish).
- Outcomes without a commit (keep as is, declined, deferred, dropped) go in the local record
  and, with a PR, in the next comment ([`posting.md`](posting.md)).
- Have one fresh agent check the applied commits against the delta list, and rerun the affected
  tests. Fix problems in your own commits with fixups ([`git.md`](git.md)); anything that needs
  a decision is a new item.
- Update the ledger, then continue with the flow in [`SKILL.md`](SKILL.md); with nothing open or
  proposed, that's the editorial phase, in the same run.
