# Diff verdict rules

Generated from `src/babelci/diff.py`. Do not edit by hand -- run
`python tools/gen_docs.py`. `tests/test_docs.py` fails if this file drifts.

`babelci diff` reports every change with a verdict, and every verdict comes
from exactly one rule below. Human output leads with the sentence; the rule id
is the machine handle and appears in `--json` and `-v`. There is no scoring and no heuristic. A change
with no matching rule is reported as `REVIEW` under `unclassified-change`,
which is itself a rule -- a human deciding beats a tool guessing.

The overall verdict is the worst individual verdict.

| Verdict | Exit code | Meaning |
|---|---|---|
| `SAFE` | 0 | the change is normal progress under the contract |
| `REVIEW` | 0 (3 with `--strict`) | a human should look; the contract does not forbid it |
| `REFUSE` | 1 | the contract forbids this change |

## REFUSE

### Two names now collapse onto one object.

Rule id `alias-bijection-lost`. Two names now collapse onto one object, so a reference that used to be unambiguous no longer is.

### Facts now trace to a different authority.

Rule id `authority-root-changed`. The successor traces its facts to a different authority than the predecessor did.

### Contradictory values are now asserted for one object.

Rule id `conflict-introduced`. The successor asserts contradictory values for one object.

### A decision disappeared rather than being superseded.

Rule id `decision-removed`. A decision disappeared rather than being superseded, so the successor may silently reopen it.

### A recorded decision changed without declaring what it replaced.

Rule id `decision-reversed`. A recorded decision changed without declaring what it supersedes, so the reversal is invisible to anyone reading the successor.

### An outside checker used to accept this world and no longer does.

Rule id `external-acceptance-lost`. An out-of-band receipt used to accept this world and no longer does.

### A MUST constraint changed meaning under the same name.

Rule id `must-constraint-modified`. A must constraint kept its identifier but changed meaning, which is how a rewritten rule passes as the original.

### A MUST constraint stopped being carried.

Rule id `must-constraint-removed`. A constraint the predecessor marked must no longer survives.

### A required object is gone.

Rule id `required-object-removed`. An object the predecessor marked required is gone.

### The two artifacts are about different tasks.

Rule id `task-identity-changed`. The two artifacts are about different work, so nothing else in the comparison is meaningful.

## REVIEW

### The checkpoint changed without naming the predecessor.

Rule id `checkpoint-reparented`. The checkpoint changed without naming the predecessor as parent, so the two artifacts may not be on the same line of work.

### A decision was replaced by one that names it.

Rule id `decision-superseded`. The decision changed and said so; a human should confirm the reversal was intended.

### An optional object was dropped.

Rule id `object-removed`. An optional object was dropped, which is what compaction does and also what context loss looks like.

### An object now asserts a different value.

Rule id `object-value-changed`. The same object now asserts a different value.

### A provenance edge was dropped.

Rule id `provenance-edge-removed`. A provenance edge was dropped; run verify on the successor to see whether the chain still reaches the root.

### An advisory constraint changed meaning under the same name.

Rule id `should-constraint-modified`. An advisory constraint changed meaning under the same identifier.

### An advisory constraint was dropped.

Rule id `should-constraint-removed`. An advisory constraint was dropped; this may be intended.

### The artifacts differ in a way v0.1 has no rule for.

Rule id `unclassified-change`. The artifacts differ in a way v0.1 has no rule for; a human decides rather than the tool guessing.

### An open question vanished without being resolved.

Rule id `unresolved-issue-dropped`. An open question vanished without a decision resolving it.

## SAFE

### The checkpoint advanced from its declared parent.

Rule id `checkpoint-advanced`. The successor names the predecessor as its parent checkpoint.

### A contradiction was resolved.

Rule id `conflict-resolved`. A contradiction present in the predecessor is gone.

### A new constraint was recorded.

Rule id `constraint-added`. Adding a constraint narrows what the successor may do.

### A new decision was recorded.

Rule id `decision-added`. New decisions are the normal product of doing the work.

### A new object was recorded.

Rule id `object-added`. New objects are the normal product of doing the work.

### A provenance edge was added.

Rule id `provenance-edge-added`. Additional provenance can only lengthen the chain.

### A new open question was recorded.

Rule id `unresolved-issue-added`. The successor inherits a newly surfaced open question.

### An open question was closed by a decision that names it.

Rule id `unresolved-issue-resolved`. The open question is named by a decision that supersedes it.
