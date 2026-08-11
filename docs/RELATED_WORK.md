# Related work, and what Babel does not claim to have invented

Reviewed August 2026. Every claim of difference below is checkable against a
cited source; where a system genuinely overlaps, it is named first and the
overlap is described before the difference.

**Summary judgement:** the problem Babel addresses is well established and
actively worked on. Structured handoff artifacts with provenance and schema
validation already exist in shipped tools. Babel's contribution is narrower
than "agent handoffs" and should be described as such — see
[Where Babel differs](#where-babel-differs).

---

## The closest system: CLAN

**CLAN** (Context and Live Agent Notation) — a file format for agent-to-agent
handoffs. ZIP container with `manifest.yaml` (identity, lineage, file registry
with checksums), an `output-schema.json` enforcing contracts at write time,
per-agent namespaces, a `merge-report.yaml` with conflict provenance, and a
`clan validate` CLI command. MPL-2.0.
<https://github.com/saieeshward/clan>

This overlaps substantially with Babel: a handoff file format, a JSON Schema, a
validate command, checksums, provenance, and surfaced conflicts.

**Where CLAN goes further:** it is a full container with per-agent namespaces,
parallel-work merge semantics, a rendered human view, and a desktop
application. It enforces attribution *at write time* — a mutation without
`--agent` and `--action` is rejected by the CLI.

**Where Babel goes further:** verification runs entirely from the artifact
after the fact, with no runtime, no CLI having mediated the writes, and no
trust in the producing tool. Babel additionally separates the checks into
layers that report independently, and — the part with no equivalent found — has
an **external-truth layer that can reject an artifact every other layer
accepted**.

Anyone choosing between them should probably choose CLAN if they want a
container format with a workflow around it, and Babel if they want a check that
runs in CI over a file the producer wrote unsupervised.

## Handoff artifacts and agent memory

**ESAA-Conversational** (dos Santos Filho, arXiv:2606.23752, June 2026)
captures visible conversation turns into an append-only `activity.jsonl` and
deterministically projects `handoff.md`, `state.md`, `decisions.md` and
`tasks.json`. It has a `verify` command. The emphasis is on *capture and
projection* across heterogeneous agents without a shared runtime; the abstract
describes no commitment semantics, provenance-chain checking, or refusal.
<https://arxiv.org/abs/2606.23752>

The overlap in vocabulary is real: decisions, tasks, handoff, state. Babel does
not produce these artifacts; it checks one.

**PROJECTMEM** (arXiv:2606.12329, June 2026), a local-first event-sourced
memory and judgment layer for coding agents, sits in the same family.
<https://arxiv.org/pdf/2606.12329>

**The `agent-handoff` GitHub topic** carries 20+ active projects as of August
2026 — `agent-chorus`, `ctxbin`, `autorunne`, `agent-handoff-kit`, `xstitch`,
`reporelay` and others — mostly local-first tools that move session context
between Claude Code, Codex, Cursor and Gemini. Several mention validation.
<https://github.com/topics/agent-handoff>

**This space is crowded.** Any claim that structured agent handoffs are novel
would be false.

## Handoff cost, measured

**Handoff Debt** (KC and Budathoki, arXiv:2606.02875, June 2026) measures the
rediscovery cost when a coding agent takes over an interrupted task: repository
state alone leaves successors re-deriving predecessor context, producing
substantially more agent events and prompt tokens. Empirical; proposes no
verification tool or schema.
<https://arxiv.org/pdf/2606.02875>

This is the closest thing to a measurement of the problem Babel addresses, and
it is the study Babel's proposed real-model evaluation would extend.

## Compaction validation

**Slipstream** (Chen, Pan, Dai and Netravali, arXiv:2605.08580, May 2026)
validates context compaction by trajectory grounding: whether an agent can
still reach the same outcome after compaction, rather than whether the
compacted text looks similar. It finds that standard compaction methods remove
information agents need.
<https://arxiv.org/pdf/2605.08580>

This is the nearest research analogue to Babel's `compression-loss` case, and
it is *stronger evidence* than anything Babel offers, because Slipstream
measures behaviour on real trajectories while Babel's lab is a fixture. Babel's
difference is cheapness and locality: it checks a declared contract in
milliseconds with no agent execution, and correspondingly concludes much less.

## Provenance and traces

**From Agent Traces to Trust** (Wang, Zhang, Cai, Liu et al., arXiv:2606.04990,
June 2026) surveys evidence tracing and execution provenance, defining
execution provenance as "the typed graph of an agent execution" and evidence
tracing as its projection onto evidence-support relations. A survey; it
catalogues directions rather than proposing a contract or tool.
<https://arxiv.org/abs/2606.04990>

Babel's provenance layer is a small, concrete instance of what that survey
describes in general.

**Auditing Provenance Sensitivity in LLM Agent Action Selection**
(arXiv:2607.20827, July 2026) examines how agents choose tools and arguments
from context mixing user requests, tool outputs, retrieved records, memory and
untrusted text. <https://arxiv.org/abs/2607.20827v1>

## Context degradation

**Context Rot** (Hong, Troynikov and Huber, Chroma Research, July 2025) tested
18 frontier models and found performance degrades as input length grows across
all of them. This is the empirical backdrop: compaction is not optional, so
handoffs are not optional either.
<https://research.trychroma.com/context-rot>

**LOCA-bench** (arXiv:2602.07962) benchmarks agents under controllable and
extreme context growth, covering context-editing strategies.
<https://arxiv.org/html/2602.07962v1>

Anthropic's context-engineering framework (September 2025) names *write,
select, compress, isolate* as the levers, with context editing and a memory
tool as platform primitives. Babel operates at the seam that *compress* and
*isolate* create; it is not an alternative to either.

## Runtime handoffs

**OpenAI Agents SDK** handoffs expose a schema to the model as the handoff
tool's parameters, validate the returned JSON locally, and pass the parsed
value on. <https://openai.github.io/openai-agents-python/handoffs/>

This is schema validation at the *routing* boundary inside one runtime, on a
message in flight. Babel checks a persisted artifact after the fact, across
runtimes, in CI, potentially days later. The word "handoff" is doing different
work in each.

## Observability standards

The **OpenTelemetry GenAI semantic conventions** (GenAI SIG, experimental as of
2026) standardise attributes for agent tasks, actions, teams, artifacts and
memory, including agent-to-agent communication and state transitions.
<https://github.com/open-telemetry/semantic-conventions/issues/2664>

These describe *what happened* for observability. Babel describes *what must
survive* for verification. They are complementary, and a future version
emitting OTel-compatible attributes would be a reasonable idea rather than a
competing one.

---

## Where Babel differs

Stated narrowly, because the space is crowded:

1. **Verification from the artifact alone, after the fact.** No runtime
   mediated the write, no CLI enforced attribution, no trust in the producing
   tool. This is what makes it a CI check rather than a workflow.

2. **Layers that report independently and are never averaged.** Structural
   integrity, identity, checkpoint binding, provenance, constraint survival,
   conflict state, authority agreement and external truth are eight separate
   answers. No system reviewed reports them separately.

3. **`not established` as a first-class result.** A layer that could not run
   says so rather than passing. No system reviewed distinguishes "checked and
   clean" from "not checked".

4. **Two independent encoders with no tiebreak.** The artifact is encoded twice
   by implementations sharing only an output schema; disagreement is reported
   rather than resolved. Derived from a private result where a second verifier
   exposed 16 acceptances the first had missed.

5. **An expectation file separate from the artifact.** What must survive is
   committed by a human to the repository, not declared by the agent being
   checked. An agent that omits a constraint produces a smaller valid artifact;
   the expectation is what makes that a failure.

6. **An external-truth layer that can reject what every other layer accepted.**
   This is the one Babel would defend hardest, and it is a *limitation* made
   explicit rather than a capability: it exists to show where internal
   consistency stops.

## What Babel does not claim

- Not the first structured agent handoff format. CLAN and others precede it.
- Not the first to validate a handoff against a schema. CLAN's `validate` and
  the OpenAI Agents SDK both do.
- Not the first to attach provenance to agent state. See CLAN and the
  provenance survey.
- Not the first to measure handoff cost. Handoff Debt did that empirically,
  with real agents, which Babel has not.
- Not a benchmark. The lab is a regression harness on one fictional scenario.
- Not validated against real agents at all. See
  [ROADMAP_REAL_MODEL.md](ROADMAP_REAL_MODEL.md).

If a system is missing from this review, that is an error worth reporting, not
a claim of absence.
