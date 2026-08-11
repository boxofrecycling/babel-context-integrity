# Reddit

Nothing has been posted. Three variants; the difference is which part leads.

---

## r/programming

**Title:** Your AI agent's handoff can pass every check and still be wrong

**Body:**

I've been working on the boundary where one coding agent hands work to the
next — context exhausted, session over, task passed on. The successor inherits
a summary, and constraints live in that summary. "Don't drop the legacy session
table yet." Then a compaction pass drops it and nothing notices.

So: give the handoff a contract, and check it.

The verifier runs eight checks and reports each one separately rather than
averaging them: structure, identity, checkpoint binding, provenance
connectivity, constraint survival, conflicts, agreement between two
independently implemented encoders, and acceptance by an out-of-band receipt.

The interesting result is the last one. I built a case where the agent scanned
the wrong branch — every fact wrong — and it passes all seven internal layers.
Both encoders agree. The commitments recompute. The provenance connects. The
artifact is internally perfect and describes a branch nobody worked on.

Only a receipt from outside the artifact rejects it. Trust got relocated, not
removed, and I'd rather the tool said so than showed a green tick.

That's why a layer that couldn't run reports "not established" instead of
passing. An artifact with no external receipt isn't clean at that layer, it's
unexamined there.

`pip install babel-context-integrity && babelci demo` — 60 seconds, zero
dependencies, no network (enforced by a test that parses every import).
Apache-2.0.

Prior art, since this space is crowded: CLAN is a handoff file format with
checksums, JSON Schema and provenance, and the agent-handoff GitHub topic has
20+ projects. And no language model was involved in any of this — the lab
agents are fixtures. What's real is the verifier's behaviour on them.

[link]

---

## r/devops

**Title:** A CI check for AI agent handoffs (Apache-2.0, zero deps, no network)

Lead with the workflow, not the philosophy:

- agent writes `.babel/handoff.json`
- CI runs `babelci verify .babel/handoff.json --expect .babel/expect.json`
- a dropped constraint or reversed decision fails the check

The `.babel/expect.json` bit is the part worth explaining: it's committed by a
human, not written by the agent under test. An agent that omits a constraint
produces a smaller *valid* artifact, so something outside it has to say what
must survive.

Zero runtime dependencies, works in `--network=none`, exit codes 0/1/2/3, JSON
output for jq. GitHub Action included, plus a script that runs the action
locally so you can see it pass and fail before committing it.

[link]

---

## r/LocalLLaMA

**Title:** Handoff verification for long-running agents — no model calls, runs offline

This community will care that it's local and that the claims are scoped.

Lead: compaction is unavoidable (context rot is real and measured), so every
long run is a chain of handoffs, and nothing checks them.

Emphasise: no model calls anywhere, no network, works fully offline, 15
deterministic failure classes you can reproduce in under a second.

Be very clear that no model was contacted in the research either, and that a
real-model evaluation is designed but not run. This crowd will find that out
and respect being told first.

[link]

---

## Rules for all three

- Reply to critical comments first and concede what's true. The threat-model
  objection ("why would the agent write an honest handoff?") is correct and
  documented — do not argue past it.
- Never post the same body text to two subreddits.
- No edits adding "EDIT: wow, front page!"
