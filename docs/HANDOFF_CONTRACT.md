# The Babel Handoff Contract, v0.1

A handoff artifact is a JSON document describing what one agent claims happened
and what must survive into the next one. This document is the human-readable
specification; [`schema/babel-handoff-0.1.schema.json`](../schema/babel-handoff-0.1.schema.json)
is the normative machine-readable one, printable with `babelci schema`.

The contract is deliberately small. Every field below has a *law* — something
the verifier actually checks. A field that could not be checked would be
decoration, and decoration in a trust artifact is worse than nothing.

## Shape

```json
{
  "babel_handoff": "0.1",
  "handoff_id": "handoff-4412-01",
  "task": { "task_id": "...", "title": "...", "family": "..." },
  "producer": { "agent": "...", "role": "...", "run_id": "..." },
  "consumer": { "agent": "...", "role": "..." },
  "checkpoint": {
    "checkpoint_id": "...",
    "parent_checkpoint_id": "...",
    "state_digest": "sha256:..."
  },
  "objects": [
    { "object_id": "...", "kind": "...", "value": ..., "required": true,
      "provenance": "...", "supersedes": "..." }
  ],
  "retained_constraints": [
    { "constraint_id": "...", "statement": "...", "binding": "MUST" }
  ],
  "decisions": [
    { "decision_id": "...", "choice": "...", "rationale": "...",
      "supersedes": "..." }
  ],
  "unresolved": [ { "issue_id": "...", "statement": "...", "blocking": true } ],
  "artifacts": [ { "path": "...", "digest": "sha256:...", "role": "..." } ],
  "provenance": { "authority_root": "...", "edges": [["from", "to"]] },
  "aliases": [["short", "canonical"]],
  "summary": { "text": "...", "commitment": "sha256:..." },
  "authorities": [
    { "authority_id": "...", "encoding": "...", "world_digest": "sha256:..." }
  ],
  "external_receipt": {
    "receipt_id": "...", "trust_root": "...", "accepted": false,
    "world_digest": "sha256:...", "findings": ["..."]
  }
}
```

Required: `babel_handoff`, `handoff_id`, `task`, `producer`, `checkpoint`,
`objects`, `provenance`. Everything else is optional, and its absence is
reported rather than assumed benign.

## Fields and their laws

### `babel_handoff`

The contract version. A verifier that implements a different version refuses
rather than guessing which fields it recognises. This is the one field checked
before anything else.

### `handoff_id`

Opaque, unique within the producing system. Not checked for uniqueness — a
single-artifact verifier cannot know what else exists.

### `task`

Identity, compared and never interpreted. When an expectation file supplies
`task_id`, a mismatch fails the identity layer. Babel does not read `title`.

### `producer`, `consumer`

Who handed what to whom. `consumer` is optional because the successor is often
unknown at write time; when an expectation names one, a mismatch fails.

### `checkpoint`

`state_digest` is a commitment over the state the artifact carries. It is
recomputed on every verify:

```
state_digest = sha256( "BABEL_HANDOFF_CHECKPOINT/0.1\0" || canonical_json({
    task_id, checkpoint_id,
    objects:     sorted [object_id, kind, sha256(value)],
    constraints: sorted [constraint_id, binding, sha256(statement)],
    decisions:   sorted [decision_id, sha256(choice)],
    unresolved:  sorted issue_id,
    artifacts:   sorted [path, digest],
}) )
```

Editing state after the commitment was computed does not survive
recomputation. `parent_checkpoint_id` is what makes a chain of handoffs a
chain; an expectation can require a specific parent, which is how replay of a
stale-but-valid artifact is caught.

### `objects`

Typed assertions. `kind` is a free string — Babel does not have a type system
for your domain and does not pretend to. What it checks is that every object
names a `provenance` label that reaches the authority root, and that two
objects sharing an `object_id` do not assert different values without a
declared `supersedes`.

`required: true` means the object must survive; an expectation lists which
object ids are required.

### `retained_constraints`

The reason this project exists. A constraint is a statement that must survive
the handoff unchanged. `binding` is `MUST` or `SHOULD`.

Both the identifier *and* the statement are committed to, so a constraint
cannot keep its id and change its meaning. That is the `constraint-softened`
lab case, and it is the failure mode that identifier-only checking misses.

### `decisions`

Choices the successor inherits rather than reopens. `supersedes` names the
decision or open issue this one replaces. A decision whose `choice` changes
without a `supersedes` is a silent reversal: `verify` on a single artifact
cannot see it, and `babelci diff` refuses it.

### `unresolved`

Known-open questions. **Silence here is a claim** — an empty or absent list
asserts that nothing is open. An expectation can require that a specific issue
is either still listed or named by a decision's `supersedes`.

### `artifacts`

Files produced, bound by digest. Babel does not read your filesystem, so it
checks the digest is well-formed and includes it in the checkpoint commitment;
comparing it to a real file is the job of whatever issues an external receipt.

### `provenance`

`authority_root` is the thing everything must trace back to — a commit id, a
dataset version, a ticket. `edges` are `[from, to]` pairs forming a directed
graph over source labels.

Checked: the root is reached by at least one edge; no edge ends at a node with
no route onward to the root; every object's provenance label reaches the root;
no cycles.

Provenance nodes are *source labels* (`ci/run-9981`, `query/db`), not object
ids. They name where a claim came from.

### `aliases`

`[short_name, canonical_name]` pairs, recording renames introduced by
compaction. An alias may rename an object id or a provenance label.

Checked: **injectivity** — two short names may not collapse onto one canonical
name, because a reference that used to be unambiguous would stop being one.

Deliberately *not* checked here: one short name bound to two canonical names.
That case is left to the authority-agreement layer, because it is the exact
situation where a single implementation using a dictionary silently keeps the
last binding and never notices. See [ARCHITECTURE.md](ARCHITECTURE.md).

### `summary`

The prose a successor actually reads, bound to the structured world:

```
commitment = sha256( "BABEL_HANDOFF_SUMMARY/0.1\0" ||
                     canonical_json({ world_digest, text }) )
```

Editing the prose without recomputing, or changing the state the prose
describes, breaks the binding. This is what stops a summary from drifting away
from the structure that is supposed to justify it.

### `authorities`

Independently computed commitments over the same semantic world. Each entry
declares who computed it and with what encoding.

Babel computes the world twice itself, with two encoders that share nothing but
the output schema, and compares. Declared authorities are additionally checked
against that result. **Agreement is not truth** — see [LIMITS.md](LIMITS.md).

### `external_receipt`

The only field that can speak to truth rather than integrity: an acceptance or
rejection issued by something that is not this artifact and not this verifier —
a test run, a repository scan, a human review, a production probe.

`trust_root` names what issued it, because a receipt is exactly as trustworthy
as its issuer. Checked: the receipt was issued against the world this artifact
encodes (not a different one), and if it rejects, verification fails regardless
of every layer above.

If absent, the external-truth layer reports `not established`. It is never
reported as passing.

## The semantic world

Several commitments are over the *world*: the meaning of the artifact once
aliases are resolved, values replaced by their digests, and ordering
normalised. Two artifacts that serialise differently but mean the same thing
have the same world digest.

```
world = {
  schema, task_id, task_family, checkpoint_id, authority_root,
  objects:           sorted [{object_id, kind, value_commitment, required, provenance}],
  constraints:       sorted [{constraint_id, binding, statement_commitment}],
  decisions:         sorted [{decision_id, choice_commitment, supersedes}],
  unresolved:        sorted issue_id,
  artifacts:         sorted [path, digest],
  provenance_edges:  sorted [from, to],
}
world_digest = sha256( "BABEL_PUBLIC_HANDOFF_WORLD/0.1\0" || canonical_json(world) )
```

## Canonical JSON

Every digest is over the same encoding, specified so another language can
reproduce it exactly:

- UTF-8 output that is pure ASCII (`ensure_ascii`);
- object keys sorted by Unicode code point;
- separators `,` and `:` with no insignificant whitespace;
- `NaN` and `Infinity` rejected.

Digests are written `sha256:` + 64 lowercase hex characters.

## Expectation files

An expectation is what a repository commits so that CI can check later handoffs
against it:

```json
{
  "babel_expectation": "0.1",
  "task_id": "PR-4412/migrate-auth-to-oidc",
  "authority_root": "repo@a1b2c3d4",
  "parent_checkpoint_id": "cp-4412-01",
  "consumer": "agent-b",
  "required_constraints": [
    { "constraint_id": "C1", "statement_commitment": "sha256:..." }
  ],
  "required_objects": ["auth.provider", "legacy.sessions"],
  "required_unresolved": ["U1"],
  "required_decisions": ["D1", "D2"]
}
```

Every key is optional. Verification without an expectation still checks
internal consistency; it just cannot know what was supposed to survive.

## Compatibility policy

See [COMPATIBILITY.md](COMPATIBILITY.md).
