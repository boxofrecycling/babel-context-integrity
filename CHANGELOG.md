# Changelog

## Unreleased

### Added

- `PROVENANCE_ROOT_MISMATCH`. The `provenance` layer now checks the artifact's
  `authority_root` against the one the expectation names. Every other check in
  that layer asks whether an artifact reaches the root it chose for itself;
  only the repository can say that root was the right one to choose. The
  expectation file has carried an `authority_root` key since 0.1.0 and the
  verifier never read it — it was documentation of a check that did not exist.

  Enforced only when the expectation names a root. An expectation without the
  key behaves exactly as it did, so no repository written against 0.1.0
  changes verdict. Silence is a question the repository has not answered, not
  a wildcard the verifier fills in.

### Changed

- The `authority agreement` layer now reports `not established` when the
  producer declared no authority, instead of `verified`. 0.1.0 printed
  `verified   2 encodings agree` on an artifact whose producer declared
  nothing — those two encodings were the verifier's own, agreeing with
  itself. That is a self-check, and reporting it in the same word used for
  an independently corroborated layer overstated what had been examined.
  This is the same condition `external truth` already reported honestly, so
  it now uses the same word.

  No verdict or exit code changes: `not established` has never been a
  failure. Artifacts that declare an authority are unaffected, including
  every example in this repository and this project's own handoff.

## 0.1.0 — 2026-08-11

Published to [PyPI](https://pypi.org/project/babel-context-integrity/0.1.0/)
via Trusted Publishing from `.github/workflows/release.yml`. No API token
exists for this project; the upload was authorised by a short-lived OIDC
token and carries signed attestations naming the workflow that produced it.

The published artifacts are byte-identical to those attached to the GitHub
`v0.1.0` release and to the digests recorded in `release/DIGESTS.txt` at that
tag. The release workflow requires that three-way equality before uploading
anything.

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

### Release-freeze changes

- `required_decisions` in an expectation is now checked. It was documented and
  advertised before it was implemented; the code was changed to match the claim
  rather than the claim softened. New code `REQUIRED_DECISION_MISSING`.
- `babelci diff` human output leads with a plain sentence and shows the actual
  before/after values. Rule ids moved to `--json` and `-v`, where a machine
  handle belongs.
- Long finding details wrap at a fixed width, so terminal, CI log and README
  output are identical. A rejecting external receipt lists its findings one per
  line instead of printing a Python repr.
- The GitHub Action emits `::error` annotations for every failing finding and
  every `REFUSE` change, so failures appear inline on the pull request rather
  than only in the log. The step summary names the failed layers and the exact
  commands to reproduce locally.
- `babelci demo` explains *why* the external-truth layer differs in kind from
  authority agreement, rather than only asserting that it does.
- Removed every URL pointing at a repository that does not exist. Package
  metadata carries no `[project.urls]`, `CITATION.cff` carries no
  `repository-code`, and the landing page uses a greppable placeholder. A test
  enforces this until publication.
- Schema `$id` is a URN rather than an invented domain.

### Release artifacts

- `RELEASE_CHECKLIST.md` — what is done, what needs a human, and the exact
  publication sequence.
- `release/v0.1.0-notes.md` and `release/DIGESTS.txt`.
- `docs/CLAIM_AUDIT.md` — every visible surface audited against `docs/LIMITS.md`.
- `docs/FINDING_CODES.md` — every code the verifier can emit.

### Known open decisions

- The `LICENSE` copyright line names one holder; whether it should name two is
  a decision for the copyright holders and has deliberately been left unmade.
- No repository slug or package name has been registered anywhere.
