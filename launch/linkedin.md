# LinkedIn

One post. Nothing has been published.

---

Long-running AI agents forget. That part is well known.

What gets less attention is the seam: when an agent runs out of context or
hands work to another agent, the successor doesn't inherit the run — it
inherits a *summary* of the run.

The constraints live in that summary. "Don't drop the legacy session table
until the migration is verified in production." And a compaction pass can
remove that sentence without anything in the toolchain noticing. The code still
compiles. The tests still pass. The next agent has simply never heard of the
constraint.

So we gave the handoff a contract, and built a verifier for it.

Eight checks, reported separately rather than averaged into a score: structure,
identity, checkpoint binding, provenance, constraint survival, conflicts,
agreement between two independently written encoders, and acceptance by
something outside the artifact.

The finding that shaped the whole design is the uncomfortable one. We
constructed a handoff where the agent had scanned the wrong branch — every fact
in it wrong — and it passes all seven internal checks. Two independent encoders
agree completely. The commitments recompute. The provenance connects.

Only a check from outside the artifact catches it.

Which means verification of this kind relocates trust rather than removing it.
We decided the tool should say that out loud: a layer that couldn't run reports
"not established" rather than passing. An unexamined check is not a clean one.

Open source under Apache-2.0. Zero dependencies, no network, runs in under a
second.

And, stated plainly: no language model was involved in this research. The test
agents are deterministic fixtures. A controlled evaluation with real agent
handoffs is designed and has not been run — calling it a result would be
exactly the sort of overclaim the project exists to catch.

[link]

---

## Notes

- No hashtag wall. Two at most, or none.
- Do not open with "🚀 Excited to announce".
- The paragraph admitting no model was involved is the one that makes this
  credible on LinkedIn specifically. Keep it.
