# GitHub Release — v0.1.0

Draft. **Nothing has been tagged, released, or published.**

---

**Tag:** `v0.1.0`
**Title:** `v0.1.0 — Babel Handoff Contract and verifier`

---

## Verify what survives when one AI agent hands work to the next

First public release candidate. The handoff contract, the verifier, the
failure lab, and a CI action.

```bash
pip install babel-context-integrity
babelci demo
```

### What this is

When a coding agent runs out of context or hands off, the successor inherits a
summary. Constraints live in that summary and can quietly stop living there.
Babel gives the handoff a machine-readable contract and checks it.

```
$ babelci verify examples/corrupted-handoff.json --expect examples/expect.json

FAIL  examples/corrupted-handoff.json
  structure ............. verified   contract 0.1, 4 objects
  identity .............. verified   agent-b -> agent-c
  checkpoint ............ verified   cp-4412-02
  provenance ............ verified   4 objects to repo@a1b2c3d4
  retained constraints .. FAILED
  conflicts ............. verified   none
  authority agreement ... verified   3 encodings agree
  external truth ........ not established

  RETAINED_CONSTRAINT_MISSING
    constraint 'C1' was required to survive this handoff and is absent
    expected: C1
    received: None
```

### Highlights

- **Babel Handoff Contract v0.1** — fourteen fields, each with a law the
  verifier checks. Normative JSON Schema plus a dependency-free native
  validator, with a parity test that fails if they disagree.
- **Eight verification layers**, reported separately and never averaged.
- **`not established`** as a first-class result. A check that could not run
  does not report success.
- **Two independent world encoders**, no tiebreak. Disagreement is a finding.
- **`babelci diff`** — semantic drift, not a line diff. Every verdict cites one
  rule from a printed table.
- **The lab** — 15 failure classes, each one named mutation of one clean
  artifact, covering all six failable layers.
- **GitHub Action**, with a script that runs it locally without GitHub.
- **Zero runtime dependencies. Zero network access.** Enforced by a test that
  parses every module's imports and a CI job that firewalls outbound traffic.

### The result worth reading about

One lab case passes structure, identity, checkpoint, provenance, constraints,
conflicts and authority agreement — and describes a repository branch nobody
worked on. Both independent encoders agree completely, because they are both
reading the same false artifact.

Only an out-of-band receipt rejects it. Verification of this kind relocates
trust; it does not remove it. That is why the layers are separate and why the
tool abstains rather than passing.

Full write-up in `paper/README.md`. Start with `docs/LIMITS.md`.

_(Relative links in this body resolve from the repository root when pasted
into a GitHub release.)_

### Honest scoping

- No language model was contacted in this work. The lab agents are
  deterministic fixtures. A controlled real-model evaluation is designed and
  **has not been run** — see `docs/ROADMAP_REAL_MODEL.md`.
- Structured agent handoffs are not new. See `docs/RELATED_WORK.md`, which
  names CLAN and ~20 other projects before describing what differs here.
- The lab is a regression harness on one fictional scenario, not a benchmark.

### Compatibility

Pre-1.0. Digest recipes may change before 1.0; if they do, the contract version
bumps and old artifacts are **refused** rather than mis-verified. Pin the
version in CI:

```yaml
with:
  version: "babel-context-integrity==0.1.0"
```

See `docs/COMPATIBILITY.md`.

### License

Apache-2.0. Created by Scott Henry and Anthony Colasante.
