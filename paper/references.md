# References

Retrieved and checked August 2026. Each entry states what was actually read —
abstract, full text, or repository — so a reader knows how much weight the
citation carries.

## Handoff cost and continuity

**[KC and Budathoki 2026]** Dipesh KC and Anjila Budathoki. *Handoff Debt: The
Rediscovery Cost When Coding Agents Take Over Interrupted Tasks.*
arXiv:2606.02875, June 2026.
<https://arxiv.org/abs/2606.02875> · PDF: <https://arxiv.org/pdf/2606.02875>
*Read: abstract and structure. Empirical measurement of rediscovery cost on
resumed coding tasks; proposes no verification tool or schema.*

**[dos Santos Filho 2026]** Elzo Brito dos Santos Filho. *ESAA-Conversational:
An Event-Sourced Memory Layer for Continuity, Handoff, and Curation Across
Heterogeneous LLM Coding Agents.* arXiv:2606.23752, June 2026.
<https://arxiv.org/abs/2606.23752>
*Read: abstract. Captures conversation turns into an append-only event store
and projects `handoff.md`, `state.md`, `decisions.md`, `tasks.json`. Has a
`verify` command; the abstract describes no commitment or refusal semantics.*

**[PROJECTMEM 2026]** *PROJECTMEM: A Local-First, Event-Sourced Memory and
Judgment Layer for AI Coding Agents.* arXiv:2606.12329, June 2026.
<https://arxiv.org/pdf/2606.12329>
*Read: title and abstract listing.*

## Compaction and context degradation

**[Hong et al. 2025]** Kelly Hong, Anton Troynikov and Jeff Huber. *Context
Rot: How Increasing Input Tokens Impacts LLM Performance.* Chroma Research,
July 2025. <https://research.trychroma.com/context-rot>
*Read: secondary summaries. 18 frontier models tested; all degrade as input
length grows. Cited as the empirical reason compaction is unavoidable.*

**[Chen et al. 2026]** Zhuofu Chen, Rui Pan, Yinwei Dai and Ravi Netravali.
*Slipstream: Trajectory-Grounded Compaction Validation for Long-Horizon
Agents.* arXiv:2605.08580, May 2026. <https://arxiv.org/pdf/2605.08580>
*Read: abstract and method summary. Validates compaction by whether an agent
still reaches the same outcome. Nearest research analogue to the
`compression-loss` case, and stronger evidence than this report offers.*

**[LOCA-bench 2026]** *LOCA-bench: Benchmarking Language Agents Under
Controllable and Extreme Context Growth.* arXiv:2602.07962.
<https://arxiv.org/html/2602.07962v1> · *Read: abstract.*

**[Anthropic 2025]** *Effective context engineering for AI agents.* Anthropic
Engineering, September 2025.
<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
*Read: secondary summaries. Source of the write / select / compress / isolate
framing referenced in §1.*

## Provenance and traces

**[Wang et al. 2026]** Yiqi Wang, Jiaqi Zhang, Taotao Cai, Zirui Liu et al.
*From Agent Traces to Trust: A Survey of Evidence Tracing and Execution
Provenance in LLM Agents.* arXiv:2606.04990, submitted 3 June 2026, revised 28
June 2026. <https://arxiv.org/abs/2606.04990>
*Read: abstract and taxonomy summary. Defines execution provenance as "the
typed graph of an agent execution". Survey; proposes no contract or tool.*

**[Provenance Sensitivity 2026]** *Auditing Provenance Sensitivity in LLM Agent
Action Selection.* arXiv:2607.20827, July 2026.
<https://arxiv.org/abs/2607.20827v1> · *Read: abstract.*

## Systems and tools

**[CLAN]** *CLAN — Context and Live Agent Notation: a file format for
agent-to-agent handoffs.* MPL-2.0. <https://github.com/saieeshward/clan>
*Read: repository README. ZIP container with `manifest.yaml` (identity,
lineage, checksums), `output-schema.json`, `clan validate`, write-time
provenance attribution, merge conflict provenance. **The closest overlapping
system to this work.***

**[agent-handoff topic]** GitHub topic index, retrieved August 2026.
<https://github.com/topics/agent-handoff>
*Read: topic listing. 20+ active projects including `agent-chorus`, `ctxbin`,
`autorunne`, `agent-handoff-kit`, `xstitch`, `reporelay`, `infernoflow`.*

**[OpenAI Agents SDK]** *Handoffs.* OpenAI Agents SDK documentation.
<https://openai.github.io/openai-agents-python/handoffs/>
*Read: documentation page. Schema exposed as handoff tool parameters, JSON
validated locally at the routing boundary within one runtime.*

**[OTel GenAI]** OpenTelemetry GenAI Semantic Conventions, Agentic Systems
(`gen_ai.*`). Experimental as of 2026.
<https://github.com/open-telemetry/semantic-conventions/issues/2664>
*Read: issue and secondary summaries. Attributes for tasks, actions, agents,
teams, artifacts, memory, and agent-to-agent communication.*

## A note on citation quality

Several entries were read as abstracts or secondary summaries rather than full
texts, and are marked as such above. Where this report makes a comparative
claim — particularly about CLAN, ESAA-Conversational and Slipstream — the claim
is restricted to what the cited material states directly.

Two known gaps:

1. The quantitative findings of [KC and Budathoki 2026] are not reported here,
   because they were not extracted from the PDF. Any future version citing
   specific handoff-debt numbers must read the full text first.
2. This review was assembled from web search in August 2026 and is certainly
   incomplete. A system missing from it is an error, not evidence of absence.
