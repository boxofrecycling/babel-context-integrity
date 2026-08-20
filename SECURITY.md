# Security

Babel is a local, deterministic verifier. It has no server, no network access,
no credentials and no telemetry. That removes most of the usual attack surface
and concentrates the rest in one place: **whether the verifier can be made to
accept something it should refuse.**

## Threat model

Babel assumes a **non-adversarial producer that is unreliable** — an agent that
means to record the handoff correctly and fails through compaction,
summarisation loss, or re-deriving a settled decision differently.

It does **not** defend against an adversarial producer. Every commitment in an
artifact is computed by the producer over the producer's own claims, so a
producer that lies from the start emits an artifact that verifies. Babel
detects drift and corruption after the fact; it is not tamper-evidence and must
not be described as such.

See [docs/LIMITS.md](docs/LIMITS.md) for the full boundary.

## What to report

### Verification bypass — the serious class

An artifact that passes `verify` while violating a law stated in
[docs/HANDOFF_CONTRACT.md](docs/HANDOFF_CONTRACT.md). Concretely:

- a layer reports `verified` when its own `LAYER_MEANING` was not established;
- a required constraint, object or decision is absent and the run still passes;
- provenance does not reach the authority root and the provenance layer passes;
- a rejecting `external_receipt` does not fail the run;
- `diff` returns `SAFE` for a change a rule declares `REFUSE`.

### Schema or parser ambiguity

Two artifacts that a reasonable reader would call different, which the tool
treats as the same — or the reverse. Specifically:

- the native validator (`src/babelci/schema.py`) and the published JSON Schema
  reach different accept/reject decisions on the same input;
- an artifact where the two authority encoders agree but encode different
  meanings, or disagree while encoding the same meaning;
- a field the contract says is checked, which no code path actually checks.

### Canonicalisation collision

Two artifacts with different meanings that produce the same commitment. The
canonical encoding is specified in
[docs/HANDOFF_CONTRACT.md](docs/HANDOFF_CONTRACT.md#canonical-json); a case
where it collides, or where an independent implementation following that
specification produces a different digest, is a defect in the specification
rather than in one implementation.

Deliberate SHA-256 collisions are out of scope; structural ones — where the
encoding loses a distinction it should have preserved — are exactly in scope.

### Unsafe file handling

`verify`, `explain`, `diff`, `lab` and `rules` read the paths you name and
write nothing. `seal --in-place` and `lab --out` write, and only where told.
Report anything that:

- writes outside a path given on the command line;
- reads a path not given on the command line;
- follows a symlink or a path traversal out of an expected directory;
- crashes, hangs, or consumes unbounded memory on a malformed artifact. A
  verifier that can be stalled by its input can be bypassed by it.

### CI and Action issues

- shell injection through an action input, a file path, or artifact content
  reaching a command line;
- artifact content escaping into a workflow command (`::set-output`,
  `::error`, `GITHUB_OUTPUT`, `GITHUB_STEP_SUMMARY`) in a way that forges
  annotations or output values;
- a failing verification that does not fail the step.

### Any network access at all

This would be critical. The package has no HTTP client and no model SDK.
`tests/test_no_contact.py` parses every module's imports and fails on
`socket`, `ssl`, `urllib`, `requests`, `httpx`, `subprocess`, `asyncio` or an
LLM SDK, then monkeypatches the socket layer and runs every command. CI
additionally runs the whole suite with outbound traffic rejected.

## Out of scope

- **A producer writing false content into a well-formed artifact.** This is the
  documented threat-model boundary. The `common-mode` lab case is exactly this,
  on purpose.
- **A constraint that was never recorded.** Use an expectation file — it is
  committed by a human, not by the agent under test.
- **Trusting a bad external receipt.** Babel reports what the receipt said and
  names its `trust_root`. Evaluating the issuer is the operator's job.
- **Dependency vulnerabilities.** There are no runtime dependencies.

## How to report

**Use GitHub's private vulnerability reporting.** It is enabled on this
repository:

<https://github.com/boxofrecycling/babel-context-integrity/security/advisories/new>

That opens a private advisory visible only to you and the maintainers. Use it
for anything that could be exploited — a verification bypass above all.

For anything that is **not** itself exploitable — a documentation error, a
confusing finding message, a hardened-CI edge case — a public issue is fine and
faster:

<https://github.com/boxofrecycling/babel-context-integrity/issues>

Please do not open a public issue for a verification bypass. Please also do not
email anyone privately about one; the advisory form exists so reports are
tracked rather than lost in a mailbox.

Please include a **minimal artifact that reproduces it**. The most useful
attachment is the output of:

```bash
babelci verify YOUR_ARTIFACT.json --json
```

Expect an acknowledgement within a week. This is a small project with no
security team, and saying so plainly is better than promising a response time
nobody is on call for.

GitHub secret scanning and push protection are enabled on the repository.

## Disclosure

If you report a verification bypass, we will fix it, publish the fix, describe
the defect in `CHANGELOG.md`, and credit you unless you ask otherwise. There is
no embargo policy beyond common sense: a bypass in a tool that nobody has
deployed in production yet is not worth sitting on.

## Supply chain

- Zero runtime dependencies; nothing is fetched at install time beyond the
  package itself.
- `pytest` and `jsonschema` are development-only and are not in the wheel.
- The wheel contains `babelci/` and the JSON Schema. Nothing else.
- Pin the version in CI: `babel-context-integrity==0.2.0`.
- Distribution digests for each release are recorded in `release/DIGESTS.txt`.
