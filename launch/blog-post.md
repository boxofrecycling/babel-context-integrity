# Blog post — long technical write-up

Draft. Not published.

**Working title:** *Your agent handoff can pass every check and still be wrong*

**Alternate:** *Agreement is not truth: what we learned building a verifier for
agent handoffs*

Target length ~2,000 words. Structure below, with the argument spelled out so
the draft can be written straight through.

---

## 1. The seam nobody instruments (≈250 words)

Open with the concrete failure, not the abstraction.

An agent is migrating an auth layer. It knows the legacy session table can't be
dropped yet — that's live in its context. It runs out of window. Compaction
runs. The successor picks up a summary that mentions the migration and doesn't
mention the table.

The code compiles. The tests pass. The constraint is gone and nothing in the
toolchain has an opinion about it.

Then generalise: every compaction is a handoff from a past self, every session
boundary is a handoff between agents, and context rot means compaction isn't
optional. Cite Chroma's context-rot result — 18 frontier models, all degrade —
and handoff debt for the measured cost of resuming.

## 2. What "verify a handoff" could even mean (≈300 words)

The move: separate *what the agent claims happened* from *what must survive*.
The first is the artifact; the second is an expectation committed by a human.

Explain why the asymmetry matters, because this is the bit people miss: an
agent that omits a constraint has produced a smaller, entirely valid artifact.
Without an external statement of what was required, there is nothing to fail.

Show the contract briefly. Don't enumerate all fourteen fields; show
`retained_constraints`, `decisions`, `unresolved`, `provenance`, and say that
every field has a law the verifier checks — a field that couldn't be checked
would be decoration, and decoration in a trust artifact is worse than nothing.

## 3. Eight layers, not a score (≈300 words)

List them. Explain why they aren't averaged: structurally perfect and
semantically wrong are different failures with different fixes, and one number
hides that.

Introduce the three states, and spend real space on `not established`. This is
the design decision to defend hardest. An artifact with no external receipt
isn't clean at that layer, it's unexamined there, and the difference between a
verifier and a rubber stamp is whether it tells you which.

## 4. Two readers, no tiebreak (≈300 words)

Why the world is encoded twice by implementations sharing only an output
schema. Authority A walks the document like a reader; Authority B shreds it
into relations and joins like a database.

The concrete payoff: an alias table binds one short name to two targets. A's
dictionary keeps the last binding silently — what almost any hand-written
parser does — and reports nothing. B's join keeps both. The disagreement is the
finding, and **no vote is taken**.

Then the honest framing: this is implementation diversity, not independent
replication. Same authors, same language, same schema. It catches blind spots;
it doesn't establish independence.

## 5. The case that changed the design (≈450 words)

The centrepiece. Take it slowly.

Build the wrong-branch artifact. Walk the reader through each layer accepting
it. Show the output with seven `verified` and `external truth ... FAILED`.

Then the reasoning: both encoders agree because both are reading the same
artifact. Adding a third would add a third reader of the same false story.
Agreement establishes that the artifact is *unambiguous*. It says nothing about
whether it's *true*.

Bring in the private result that closed the software programme: six coherent
wrong worlds accepted by all six verification paths, rejected only by a
separately constructed receipt. More verifiers didn't help because the
verifiers weren't the problem.

State the conclusion plainly: no software construction removes the trust root.
It only moves it. The external-truth layer exists to make the root *nameable* —
the `trust_root` field forces you to write down what you're now trusting.

Be precise about scope here or a careful reader will catch it: `diff` against a
correct predecessor *does* catch this particular case, because a decision
changed. An agent whose first handoff is wrong has no predecessor. Say so.

## 6. What it costs (≈150 words)

32.3% of the example artifact is integrity machinery. Measured, not estimated,
by a command the reader can run.

Then the sharper private number: carrying full proofs alongside summaries cost
*more* than the original context — 5,520 and 5,888 bits more. That's why the
public contract carries commitments instead of proofs. A design decision with a
receipt behind it.

## 7. What this doesn't do (≈250 words)

Not a soft "limitations" section — the strongest part of the post.

Doesn't detect hallucination. Doesn't check whether text is true. Non-adversarial
threat model: the producer computes commitments over its own claims, so a
producer that lies from the start produces an artifact that verifies. Not
tamper-evidence.

No model was involved. Not here, not in the private research. The lab agents
are fixtures and the scenario is fictional. What's real is the verifier's
behaviour on it.

And the prior art: CLAN, ESAA-Conversational, 20+ projects under the
`agent-handoff` topic, the OpenAI Agents SDK. Name them before someone else
does.

## 8. What would make this matter (≈100 words)

The unmeasured number: how often does a real handoff pass every internal layer
and still describe the wrong world? The lab case is hand-constructed. Its
real-world rate is unknown, and it decides whether the external-truth layer is
a footnote or the main event.

Sketch the three-arm study. Say it's designed and not run. Invite someone else
to run it — independent replication would be worth more than another in-house
result.

Close on the line without decorating it: **agreement is not truth.**

---

## Rules for the draft

- Every number gets a command next to it.
- Every comparison to another project links to that project.
- No paragraph that could be deleted without losing an argument.
- The limitations section is not an apology. It is the reason to believe the
  rest.
