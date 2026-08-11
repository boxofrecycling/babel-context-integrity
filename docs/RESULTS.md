# Results

Two tables, kept apart on purpose.

**Table 1** is what this repository reproduces. Run the command, get the number.

**Table 2** is what the private research programme established. It is cited
here because the public design derives from it, and it is clearly marked as
**not reproducible from this repository**. Nothing in the public README or the
public claims depends on it.

---

## Table 1 — the public lab (reproducible here)

```bash
babelci lab            # or: babelci lab --json
```

Fifteen cases, each generated from one clean handoff by one named mutation.
Each row states the verdict and the layer that caught it. A case that fails at
the *wrong* layer is a lab failure even when the verdict matches, because
otherwise the layering claim would be untested.

| Case | Verdict | Caught at | Finding code |
|---|---|---|---|
| `clean` | PASS | — | — |
| `restart-resume` | PASS | — | — |
| `constraint-dropped` | FAIL | retained constraints | `RETAINED_CONSTRAINT_MISSING` |
| `constraint-softened` | FAIL | retained constraints | `RETAINED_CONSTRAINT_MODIFIED` |
| `decision-reversed` | PASS | — (`diff` REFUSEs) | `decision-reversed` |
| `checkpoint-mismatch` | FAIL | checkpoint | `CHECKPOINT_COMMITMENT_MISMATCH` |
| `summary-drift` | FAIL | retained constraints | `SUMMARY_COMMITMENT_MISMATCH` |
| `provenance-break` | FAIL | provenance | `PROVENANCE_CHAIN_BROKEN` |
| `alias-collapse` | FAIL | provenance | `ALIAS_NOT_BIJECTIVE` |
| `authority-disagreement` | FAIL | authority agreement | `AUTHORITY_DISAGREEMENT` |
| `compression-loss` | FAIL | retained constraints | `REQUIRED_OBJECT_MISSING` |
| `duplicate-conflict` | FAIL | conflicts | `DUPLICATE_OBJECT_CONFLICT` |
| `stale-replay` | FAIL | checkpoint | `CHECKPOINT_REPLAY` |
| `externally-confirmed` | PASS | — | — |
| `common-mode` | FAIL | **external truth only** | `EXTERNAL_RECEIPT_REJECTED` |

### Measured quantities

| Quantity | Value | How to reproduce |
|---|---|---|
| Lab cases passing at their declared layer | 15 / 15 | `babelci lab` |
| Layers that a lab case exercises | 6 of 6 failable | `pytest tests/test_lab.py` |
| Example artifact, total size | 21,848 bits | `babelci lab --json` |
| — content | 14,792 bits | `.overhead.content_bits` |
| — integrity machinery | 7,064 bits (32.3%) | `.overhead.integrity_bits` |
| Verification layers reported separately | 8 | `babelci verify X --json` |
| Runtime dependencies | 0 | `pyproject.toml` |
| Network operations during any command | 0 | `pytest tests/test_no_contact.py` |
| Files written by verify/explain/diff/lab | 0 | `pytest tests/test_no_contact.py` |

### Two claims worth stating precisely

**`common-mode` passes every layer except external truth.** Not "most layers" —
all seven others. This is asserted by
`tests/test_verify.py::test_common_mode_passes_every_layer_except_external`,
which iterates the layers rather than checking the verdict.

**`decision-reversed` is invisible to single-artifact verification.** `verify`
returns PASS. Only `diff` against the predecessor refuses it. The lab records
this as a *limitation of verify*, not as a success.

A related precision: `diff` against a correct predecessor also catches
`common-mode`, because a decision changed. An agent whose *first* handoff
describes the wrong world has no predecessor, and then nothing local catches
it. `tests/test_diff.py` asserts both halves.

### Determinism

```bash
babelci lab --json > a.json
babelci lab --json > b.json
diff a.json b.json     # empty
```

The lab reports a `lab_digest` over `(case, verdict, caught_at, world_digest)`
for every case. It is stable across runs and across processes.

---

## Table 2 — private research findings (NOT reproducible from this repository)

These come from a private, deterministic, fully offline research apparatus
using **scripted fixture agents**. They are cited because the public design
derives from them.

> **No real language model was contacted anywhere in that work.** Every agent
> is a deterministic fixture. Every label is a synthetic known-answer oracle.
> These are software apparatus results, not scientific results about models.

| Private finding | Measured value | Public case it informs |
|---|---|---|
| Restart/resume receipt identity | 9/9 byte-identical, 78 unique matrix entries, 0 hidden retries | `restart-resume` |
| Protocol drift detection | 12/12 specified mutation classes detected; 10 recovered lawfully | — |
| Scripted handoff corruption | 20/20 corruptions detected across firewall, receiver, task check | `constraint-dropped`, `checkpoint-mismatch` |
| Semantic equivalence | 40/40 transformations and 32/32 compositions matched the authority verdict | `constraint-softened` |
| Exact-size corrupt controls | 40/40 passed early checks; 25 produced a false success; the separate authority rejected all 40 | `common-mode` |
| Context compression boundary | lowest safe tested levels 55% referential / 70% compositional; 16/16 recoveries | `compression-loss` |
| Orthogonal ablation | reference, order, provenance, checkpoint and alias bijection each separately load-bearing; 0/20 pairs added a novel interaction | `alias-collapse`, `provenance-break` |
| Second verifier | matched all 80 prior decisions; exposed 16 alias-structure acceptances the first verifier missed | `authority-disagreement` |
| Shared-assumption controls | 6 injected shared assumptions produced false pair agreement | `authority-disagreement` |
| Minimal sufficient context | exhaustive over 1,024 frozen-vocabulary candidates: 7,176-bit referential, 8,112-bit compositional minima | — |
| Dual authority encodings | 4/4 clean worlds matched across two distinct encodings | `authority-disagreement` |
| Proof-carrying summaries | six-entry matrix, separate dispositions, no vote | `summary-drift` |
| **Proof overhead** | proof + summary exceeded the original context by **5,520 bits (referential)** and **5,888 bits (compositional)** | `overhead` measurement |
| Duplicate / provenance handling | 8 duplicate and 9 provenance cases deterministic and order-free across 6 paths; depth 1 minimum sufficient chain | `duplicate-conflict`, `provenance-break` |
| **Common-mode trust** | **all 6 coherent wrong worlds accepted by all 6 normal paths; rejected only by a separately constructed receipt** | `common-mode` |

### Verified state of that apparatus

The closeout reproduction was executed during preparation of this export and
returned `BABEL_SOFTWARE_FRONTIER_REPRODUCTION_PASS`: 283 focused tests
passing, all 14 result digests matching the frozen manifest, protected tree
digest unchanged, **0 network or model-contact attempts**.

Its recorded decision is `SOFTWARE_FRONTIER_CLOSED_AND_PARKED`, and its
real-model execution readiness is `NO AUTHORIZATION`. See
[ROADMAP_REAL_MODEL.md](ROADMAP_REAL_MODEL.md).

### Why the numbers differ

The private "proof overhead" result (proof transmission *larger* than the
original context) and the public "integrity overhead" measurement (32.3% of the
artifact) are **not the same measurement**. The private apparatus carried full
proofs; the public contract carries commitments, which are far smaller. The
public number is measured on the public artifact by `babelci lab` and is not
inherited from the private figure.

This is the general rule for this repository: **public claims are measured
publicly.** Where a private result is cited, it is cited as provenance for a
design decision, never as evidence for a public claim.

---

## Traceability

Every lab case carries the id of the private result it derives from, in the
`mirrors` field of `src/babelci/lab/cases.py`, surfaced as
`mirrors_private_result` in `babelci lab --json`.
`tests/test_lab.py::test_every_case_names_the_private_result_it_mirrors`
enforces that the field is populated.
