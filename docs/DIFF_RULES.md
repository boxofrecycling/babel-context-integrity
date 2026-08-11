# Diff verdict rules

Generated from `src/babelci/diff.py`. Do not edit by hand -- run
`python tools/gen_docs.py`. `tests/test_docs.py` fails if this file drifts.

`babelci diff` reports every change with a verdict, and every verdict comes
from exactly one rule below. There is no scoring and no heuristic. A change
with no matching rule is reported as `REVIEW` under `unclassified-change`,
which is itself a rule -- a human deciding beats a tool guessing.

The overall verdict is the worst individual verdict.

| Verdict | Exit code | Meaning |
|---|---|---|
| `SAFE` | 0 | the change is normal progress under the contract |
| `REVIEW` | 0 (3 with `--strict`) | a human should look; the contract does not forbid it |
| `REFUSE` | 1 | the contract forbids this change |

## REFUSE

### `alias-bijection-lost`

Two names now collapse onto one object, so a reference that used to be unambiguous no longer is.

### `authority-root-changed`

The successor traces its facts to a different authority than the predecessor did.

### `conflict-introduced`

The successor asserts contradictory values for one object.

### `decision-removed`

A decision disappeared rather than being superseded, so the successor may silently reopen it.

### `decision-reversed`

A recorded decision changed without declaring what it supersedes, so the reversal is invisible to anyone reading the successor.

### `external-acceptance-lost`

An out-of-band receipt used to accept this world and no longer does.

### `must-constraint-modified`

A must constraint kept its identifier but changed meaning, which is how a rewritten rule passes as the original.

### `must-constraint-removed`

A constraint the predecessor marked must no longer survives.

### `required-object-removed`

An object the predecessor marked required is gone.

### `task-identity-changed`

The two artifacts are about different work, so nothing else in the comparison is meaningful.

## REVIEW

### `checkpoint-reparented`

The checkpoint changed without naming the predecessor as parent, so the two artifacts may not be on the same line of work.

### `decision-superseded`

The decision changed and said so; a human should confirm the reversal was intended.

### `object-removed`

An optional object was dropped, which is what compaction does and also what context loss looks like.

### `object-value-changed`

The same object now asserts a different value.

### `provenance-edge-removed`

A provenance edge was dropped; run verify on the successor to see whether the chain still reaches the root.

### `should-constraint-modified`

An advisory constraint changed meaning under the same identifier.

### `should-constraint-removed`

An advisory constraint was dropped; this may be intended.

### `unclassified-change`

The artifacts differ in a way v0.1 has no rule for; a human decides rather than the tool guessing.

### `unresolved-issue-dropped`

An open question vanished without a decision resolving it.

## SAFE

### `checkpoint-advanced`

The successor names the predecessor as its parent checkpoint.

### `conflict-resolved`

A contradiction present in the predecessor is gone.

### `constraint-added`

Adding a constraint narrows what the successor may do.

### `decision-added`

New decisions are the normal product of doing the work.

### `object-added`

New objects are the normal product of doing the work.

### `provenance-edge-added`

Additional provenance can only lengthen the chain.

### `unresolved-issue-added`

The successor inherits a newly surfaced open question.

### `unresolved-issue-resolved`

The open question is named by a decision that supersedes it.
