# What Babel does not establish

This is the most important document in the repository. Everything the tool can
do is only worth something if the boundary is stated precisely.

## The one-sentence version

Babel checks whether a structured handoff artifact satisfies a declared
contract. It does not check whether the artifact is true.

## Five things that are not the same

The verifier reports these separately and never averages them into a score,
because collapsing them is how a verification tool becomes a rubber stamp.

**1. Structural integrity.** The artifact parses and matches the contract's
shape. Establishes nothing about content. A perfectly-formed artifact can be
entirely fabricated.

**2. Semantic equivalence under tested fixtures.** Two representations mean the
same thing *under the transformations this apparatus tests*. Establishes
nothing about representations nobody wrote a case for. There is no universal
equivalence law here and Babel does not claim one.

**3. Provenance.** Every assertion traces to a declared authority root by
connected, acyclic edges. Establishes that a *claim of origin* is internally
coherent. It does not establish that the origin is real, that the root is
trustworthy, or that the claim about it is accurate. A fabricated chain to a
fabricated root verifies.

**4. Authority agreement.** Two independently implemented encoders read the
same artifact and produce the same semantic world. Establishes that the
artifact is unambiguous. Establishes nothing about whether the world it
describes occurred. **Two encodings built from one artifact can agree perfectly
about a story that never happened.**

**5. External truth.** Something outside the artifact — a test run, a
repository scan, a human — accepted or rejected the world. This is the only
layer that can speak to truth, and it is exactly as trustworthy as whatever
issued the receipt. Babel does not issue it and cannot check it.

## Specific non-claims

**Babel is not an AI truth verifier.** It cannot determine whether arbitrary
model-generated text is true. If someone describes it that way, they are wrong.

**Babel does not detect hallucination.** A hallucinated fact, written into a
well-formed artifact with a plausible provenance label and a correct
commitment, verifies. The `common-mode` lab case is precisely this.

**Babel is not agent memory, a vector database, RAG, or an agent framework.**
It stores nothing, retrieves nothing, and runs no agents.

**Babel does not compress context.** It measures what the integrity machinery
costs (32.3% of the example artifact) and reports it.

**A passing verify is not a guarantee of correctness.** It is a statement that
the specific checks that ran, passed, and that specific others did not run.

**No result in this project involves a language model.** The lab agents are
deterministic fixtures. The scenario is fictional. The private research
programme this derives from also contacted no model — see
[ROADMAP_REAL_MODEL.md](ROADMAP_REAL_MODEL.md).

## What each layer is not entitled to conclude

| Layer | Passing means | Passing does **not** mean |
|---|---|---|
| structure | the shape is legal | the content is meaningful |
| identity | identifiers match what was expected | the identifiers name real things |
| checkpoint | the commitment recomputes from carried state | the state is correct |
| provenance | claimed origins form a connected chain to the root | the origins are real |
| retained constraints | required statements survived verbatim | they are being obeyed in the code |
| conflicts | no unresolved equal-rank contradiction | the surviving values are right |
| authority agreement | the artifact is unambiguous | the world is true |
| external truth | an outside checker accepted | the outside checker is correct |

## Where verification structurally cannot help

**A single artifact cannot reveal a silent reversal.** If a decision changes
and the artifact is otherwise consistent, one artifact contains no evidence
that anything changed. This is the `decision-reversed` lab case: `verify`
passes, and only `babelci diff` against the predecessor refuses it.

**A first handoff has no predecessor.** `diff` needs two artifacts. An agent
whose very first handoff describes the wrong world has nothing to be compared
against, and no local check catches it.

**Babel cannot verify what the producer chose not to record.** An agent that
omits a constraint from `retained_constraints` in the first place has produced
a smaller, entirely valid contract. Expectation files exist for this reason —
they are how a repository, rather than an agent, decides what must survive.

**Babel cannot tell you the producer was honest.** Every commitment in the
artifact is computed by the producer over the producer's own claims. The
machinery detects *drift and corruption after the fact*; it is not an
adversarial integrity scheme and a producer that lies from the start will
produce an artifact that verifies. Signing (a v0.2 candidate) would bind an
artifact to an identity; it would still not make the contents true.

## Boundary of the lab numbers

The lab reports what happened on **one fictional scenario with fifteen
generated mutations**. Those numbers characterise the verifier's behaviour on
that scenario. They are not prevalence estimates, not benchmark scores, and not
evidence about how often real agents corrupt real handoffs — nobody has
measured that here.

## Relationship to the private research

Every lab case names the private result it derives from
([RESULTS.md](RESULTS.md)). Those private results are themselves bounded:
deterministic offline scripted-fixture apparatus, no real model, no independent
scientific replication. The public claims are deliberately *weaker* than the
private ones, not stronger.
