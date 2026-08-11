# Security

## Threat model

Babel assumes a **non-adversarial producer that is unreliable**: an agent that
means to record the handoff correctly and fails through compaction,
summarisation loss, or re-deriving a settled decision differently.

It does **not** defend against an adversarial producer. Every commitment in an
artifact is computed by the producer over the producer's own claims. A producer
that lies from the start emits an artifact that verifies. Babel detects drift
and corruption after the fact; it is not tamper-evidence and should not be
described as such.

See [docs/LIMITS.md](docs/LIMITS.md) for the full boundary.

## What counts as a vulnerability

**The serious class: the verifier accepts something it should refuse.**

Concretely, any artifact that:

- passes `verify` while violating a stated law in
  [docs/HANDOFF_CONTRACT.md](docs/HANDOFF_CONTRACT.md);
- produces a layer status of `verified` where the layer's own
  `LAYER_MEANING` was not established;
- makes the two authority encoders agree on different meanings, or disagree on
  the same meaning;
- passes the native validator but fails the published JSON Schema, or vice
  versa;
- produces a `SAFE` diff verdict for a change a rule says is `REFUSE`.

Also in scope:

- a crash, hang, or unbounded memory use on a malformed artifact (a verifier
  that can be DoS'd by input is a verifier that can be bypassed);
- any code path that performs I/O beyond the files named on the command line;
- **any network access whatsoever** — this would be a critical bug, and
  `tests/test_no_contact.py` exists to make it hard to introduce accidentally.

## Out of scope

- A producer writing false content into a well-formed artifact. This is the
  documented threat-model boundary, not a bug. `common-mode` in the lab is this
  case, on purpose.
- A missing constraint that was never recorded. Use an expectation file.
- Trusting a bad external receipt. Babel reports what the receipt said and names
  its `trust_root`; evaluating the issuer is the operator's job.

## Reporting

Open a GitHub security advisory on the repository, or a normal issue if the
finding is not sensitive. Include a minimal artifact that reproduces it —
`babelci verify --json` output is the most useful attachment.

Expect an acknowledgement within a week. This is a small project with no
security team; that is stated plainly rather than promised around.

## Supply chain

- **Zero runtime dependencies.** Nothing is pulled in at install time beyond
  the package itself.
- Development dependencies (`pytest`, `jsonschema`) are not distributed in the
  wheel and are not imported by any runtime module.
- Pin the version in CI: `babel-context-integrity==0.1.0`.
- The wheel contains only `src/babelci` plus the JSON Schema.
