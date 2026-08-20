# Changelog

## 0.2.0 — 2026-08-20

Babel became more truthful about three things: what it verified, what nobody
attested, and what legitimately carries forward. No artifact format changed and
no run changes verdict.

Every change here came from running the verifier against a real handoff that
had been carried across sixty-five sessions, and reading what it printed.

### Changed

- **The `authority agreement` layer reports `not established` when the producer
  declared no authority, instead of `verified`.**

  0.1.0 printed `verified   2 encodings agree` for an artifact whose producer
  declared nothing. Those two encodings were the verifier's own, agreeing with
  itself — a self-check, reported in the same word used for a layer an outside
  encoder had corroborated. `seal` already refused to write its own authority
  entries on the grounds that it would be "marking its own homework"; the
  verifier was doing exactly that in its status column.

  This is the same condition `external truth` has always reported honestly, so
  it now uses the same word. `AUTHORITY_SINGLE_ENCODING` keeps its `note`
  severity and its meaning.

- **The `conflicts` layer says what it knows about open issues.** `none` became
  `none, 2 open` when the producer named them, and `none, 0 open (unattested)`
  when it named nothing and no expectation required an issue to survive.

### Added

- **A coverage census under the verdict.**

  ```
  PASS  .babel/handoff.json
        6 verified · 2 not established
  ```

  Eight mostly-green lines read as eight checks that passed. The census is one
  line that cannot be skimmed past. The counts sit side by side and are never
  combined into a figure — collapsing them is how a verifier becomes a rubber
  stamp, which is why the layers themselves are never averaged either. After a
  structural exit it also reports the layers that never ran, so a short report
  cannot be mistaken for a clean one.

- **`SILENCE_UNATTESTED`** (severity `note`). The contract has always said that
  silence in `unresolved` is a claim that nothing is open. Nothing checked that
  claim unless an expectation named an issue that had to survive, and the layer
  printed a bare `none` that reads as a completed check. The note says the claim
  is the producer's alone.

- **`PROVENANCE_ROOT_MISMATCH`.** The `provenance` layer now checks the
  artifact's `authority_root` against the one the expectation names. Every other
  check in that layer asks whether an artifact reaches the root it chose for
  itself; only the repository can say that root was the right one to choose.
  `examples/expect.json` has shipped an `authority_root` key since 0.1.0 and the
  verifier never read it — documentation of a check that did not exist.

  Enforced only when the expectation names a root.

- **`babelci carry`.** Drafts the successor of a handoff. The task, provenance
  graph, authority root, retained constraints, decisions, open issues, objects
  and aliases carry forward verbatim, and the checkpoint advances declaring its
  predecessor as `parent_checkpoint_id` — a field the contract has always had
  and producers rarely wrote, which is why `CHECKPOINT_REPLAY` could not fire.

  Producers hand-author this at the end of a session, when context is shortest.
  What gets retyped every session eventually gets retyped wrong.

  It withholds three fields, each because carrying it would assert something the
  successor's producer never claimed: `authorities` (a commitment computed over
  the predecessor's world), `external_receipt` (an acceptance of that world, not
  this one), and `summary` (prose about what is true now — `--summary` writes a
  fresh one). `carry` invents nothing: an authority root of `repo` stays `repo`.

### Migration

Nothing to do. No artifact needs changing and no configuration needs adding.

- **Exit codes are unchanged for every artifact that exists.** `not established`
  has never been a failure, and `SILENCE_UNATTESTED` is `note` severity, which
  does not set a layer state. The new `PROVENANCE_ROOT_MISMATCH` is the only
  check that can fail a run, and only when an expectation names an
  `authority_root` — a key no expectation outside this repository's own
  examples currently sets.
- **Output changed for artifacts that declare no `authorities`.** One status
  line becomes `not established`, and a census line appears. Anything parsing
  the human-readable output should read `--json` instead, where
  `layers[].status` carries the same information and always has.
- **To adopt `authority_root` enforcement**, add the key to your expectation
  file. Note that the artifact must already ground its facts in that root; if
  your producer writes a placeholder root, enforcing a real one fails the run
  until the producer is updated too.

### Compatibility

Contract version is unchanged at `0.1`. No field was added or removed, no digest
recipe or canonical encoding changed, no existing finding code changed meaning,
and no diff rule changed verdict. Artifacts sealed by 0.1.0 verify identically
under 0.2.0, and artifacts produced by 0.2.0 verify identically under 0.1.0.

One judgement call worth stating plainly: `docs/COMPATIBILITY.md` lists
"changes what a layer status implies" as breaking. The `authority agreement`
layer's `verified` now implies strictly *more* than it did — it means a
producer-declared authority agreed, where before it could also mean nobody had
declared one. Nothing about the contract moved, and no verdict or exit code
changed, so this is a change to what the tool *reports* rather than to what an
artifact *is*. `docs/COMPATIBILITY.md` now draws that distinction explicitly
rather than leaving it to be inferred.

### Known limitations

`docs/LIMITS.md` is unchanged, and that is the point: nothing in this release
moved the claim boundary. Babel still does not determine whether text is true,
still does not detect hallucination, and encoder agreement is still not truth.
Specific to this release:

- A `not established` authority layer says nobody independent checked. It does
  not say the artifact is wrong, and a `verified` one still only means two
  encoders agreed about a world that may never have existed.
- `SILENCE_UNATTESTED` reports that a claim went unchecked. It cannot tell you
  whether anything is actually open.
- `PROVENANCE_ROOT_MISMATCH` compares two strings. A matching root establishes
  that the artifact names the root the repository expected, not that the root is
  real or trustworthy.
- `carry` copies what a predecessor asserted. If the predecessor was wrong, the
  successor inherits the error faithfully — that is what continuity means, and
  `babelci diff` remains the check against a *correct* predecessor.
- The census counts layers. It is not a score and must not be read as one.

### Deferred and dropped

- **Claim objects with confidence rungs: deferred.** Designed, not built. The
  reporting changes above already state the epistemic position of an artifact
  without new vocabulary or anything for a producer to fill in. Deferred until a
  real use case needs to record a claim the existing objects and constraints
  cannot carry.
- **A diff rule for unchanged summaries: dropped.** It was meant to catch stale
  prose being silently re-committed by `seal`. `carry` withholds the summary
  instead, which prevents the path rather than detecting it afterwards.

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
