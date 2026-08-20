# Versioning and compatibility

## Contract versions vs tool versions

Two version numbers, deliberately independent:

- **the contract**, declared in every artifact as `babel_handoff: "0.1"`;
- **the tool**, `babelci --version`.

The tool may release many versions against one contract version. An artifact
declares which contract it conforms to, and a verifier that does not implement
that contract **refuses** rather than guessing which fields it recognises:

```
CONTRACT_VERSION_MISMATCH
  this build implements contract '0.1'; artifact declares '0.2'
```

Silently ignoring unknown fields would let a v0.2 artifact carrying a new
`signature` field pass a v0.1 verifier that never checked it, and report PASS.
That is the failure mode this whole project exists to complain about, so the
tool does not do it.

## What v0.1 promises

**v0.1 is pre-1.0 and the contract will change.** Concretely:

- finding codes will not change meaning; new ones may be added;
- diff rule names will not change meaning; new ones may be added;
- the `--json` result schemas (`babel-verify/0.1`, `babel-diff/0.1`,
  `babel-lab/0.1`) may gain keys; existing keys keep their meaning;
- exit codes 0, 1, 2 and 3 are stable;
- **the digest recipes may change before 1.0.** If they do, the contract
  version goes to `0.2` and artifacts sealed under `0.1` will be refused by a
  `0.2` verifier rather than mis-verified.

Pin the version in CI:

```yaml
with:
  version: "babel-context-integrity==0.2.0"
```

## Compatibility rules

A change is **compatible** and lands in the same contract version if it:

- adds an optional field;
- adds a finding code, diff rule, or `--json` key;
- makes an existing check catch strictly more without changing its meaning.

A change is **breaking** and requires a new contract version if it:

- adds or removes a required field;
- changes a digest recipe or the canonical encoding;
- changes what an existing finding code means;
- changes a diff rule's verdict;
- changes what a layer status implies **about the artifact**.

## Contract compatibility vs report compatibility

Those two lists are about the contract: what an artifact *is*, and whether two
implementations agree about it. A separate question is what the tool *prints*,
and the two can move independently.

The tool may tighten what it is willing to claim without any artifact changing.
That is not a contract change: the same bytes parse the same way, produce the
same digests, and reach the same verdict and exit code. It is still a change
someone can notice, so it belongs in the changelog and in release notes, stated
plainly rather than left to be discovered.

0.2.0 is the worked example. The `authority agreement` layer stopped reporting
`verified` for an artifact whose producer declared no authority, because those
two agreeing encodings were the verifier's own. The word on one status line
changed; nothing about the artifact did, and no run changed verdict. Read
strictly, "changes what a layer status implies" could have been read as
breaking — hence the clarification above. A status now implying *more* than it
did, with no artifact and no verdict affected, is a report change.

The rule of thumb: if an artifact sealed by the old version still verifies
identically under the new one, and vice versa, the contract did not move.

If you parse Babel's output, parse `--json`. `layers[].status` has carried this
information since 0.1.0 and is subject to the compatibility rules above; the
human-readable rendering is not.

Since a v0.1 verifier refuses non-v0.1 artifacts outright, a breaking change is
loud by construction. That is the intended cost.

## Named candidates for v0.2

Not commitments — the current thinking, written down so it can be argued with:

- **producer signatures.** Bind an artifact to an identity, so a handoff cannot
  be swapped for another that also verifies. This addresses authorship, not
  truth: a signed lie is still a lie, and the [limits](LIMITS.md) would not
  move.
- **typed object kinds.** A small registry of well-known `kind` values, so
  tooling can interpret `metric` or `file` without guessing. `kind` stays a
  free string; the registry would only add optional meaning.
- **multi-parent checkpoints.** For merges, where a successor legitimately
  inherits from two predecessors.
- **structured external receipts.** A schema for what a receipt issuer checked,
  rather than a free-form `findings` list.
- **constraint scope.** Marking a constraint as applying to a file, a
  directory, or a phase, so a successor knows where it binds.

Deliberately *not* planned: anything that would let Babel conclude a handoff is
true. That is not a missing feature, it is the boundary.

## Deprecation

If a field or code is deprecated, it keeps working for at least one contract
version and the tool emits a `note`-severity finding naming the replacement.
Nothing is removed without a version bump.

## Reporting a problem

A verifier that accepts something it should refuse is the serious bug class.
See [SECURITY.md](../SECURITY.md).
