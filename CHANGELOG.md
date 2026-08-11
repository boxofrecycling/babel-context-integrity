# Changelog

## 0.1.0 — unreleased

First public release candidate. Nothing has been published to any registry.

### Contract

- Babel Handoff Contract v0.1: fourteen top-level fields, each with a law the
  verifier checks.
- Normative JSON Schema, plus a native dependency-free validator; a parity test
  fails if they ever disagree.
- Domain-separated SHA-256 commitments over a fully specified canonical JSON
  encoding, so another language can reproduce them byte for byte.

### Verifier

- Eight layers reported independently and never averaged: structure, identity,
  checkpoint, provenance, retained constraints, conflicts, authority agreement,
  external truth.
- Three layer states, including `not established` for checks the artifact did
  not supply the inputs for.
- Two independent world encoders (document-tree and relation-join) with no
  tiebreak; disagreement is a finding.
- Equal-rank conflicts fail closed.

### CLI

- `verify`, `explain`, `diff`, `seal`, `lab`, `demo`, `schema`, `rules`.
- Human and `--json` output; stable exit codes 0/1/2/3.
- Zero runtime dependencies, zero network access, no telemetry, no config file,
  no cache.

### Lab

- Fifteen failure classes generated from one clean artifact by one named
  mutation each, covering all six failable layers.
- Each case declares its expected verdict *and* catching layer.
- Reproducible `lab_digest`.

### CI

- GitHub Action wrapping the CLI, with `action/test-local.sh` to exercise it
  without GitHub.
- Workflow runs the suite on Python 3.10–3.13 and again with outbound network
  rejected.

### Docs

- Handoff contract, concepts, CLI reference, architecture, limits, results,
  diff rules, compatibility policy, CI guide, commercial strategy, real-model
  roadmap, related-work review.
- Technical report draft with references and a reproducibility appendix.

### Known open decisions

- The `LICENSE` copyright line names one holder; whether it should name two is
  a decision for the copyright holders and has deliberately been left unmade.
- No repository slug or package name has been registered anywhere.
