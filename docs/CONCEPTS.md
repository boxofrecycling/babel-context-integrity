# Core concepts

## The problem

An agent works for a while, then stops — context exhausted, session ended, task
handed to a specialist, human stepping away. Whatever comes next inherits a
*story*: a summary, a state file, a compacted transcript.

That story is where the constraints live. "Don't drop the legacy table yet."
"We chose Okta, not Auth0, and here's why." "Refresh-token rotation is still
unagreed." It is also where they quietly stop living. Summarisation drops
things. Compaction renames things. A successor re-derives a decision the
predecessor already made and makes it differently.

Nothing in a normal toolchain notices. `git diff` shows you the code. It has no
opinion about whether the story your next agent is reading still matches it.

## The idea

Give the story a contract, and check the contract.

A **handoff artifact** is JSON. It says what the producing agent claims
happened, and — separately — what must survive into whatever comes next. Then a
deterministic, offline verifier checks it: do the commitments recompute, does
provenance connect, did the constraints marked as surviving actually survive,
do two independent encoders read it the same way.

## Layers, not a score

Verification runs eight layers, in order, and reports each one separately:

```
structure → identity → checkpoint → provenance → retained constraints
          → conflicts → authority agreement → external truth
```

They are not averaged. A handoff can be structurally perfect and semantically
wrong. It can be semantically coherent and describe a world that never
happened. Those are different failures with different fixes, and a single
number hides that.

Each layer ends in one of three states:

| State | Meaning |
|---|---|
| `verified` | the check ran and the artifact satisfied it |
| `FAILED` | the check ran and the artifact did not satisfy it |
| `not established` | the artifact did not supply what the check needs |

The third one matters more than it looks. An artifact with no external receipt
is not *clean* at that layer — it is *unexamined* there. Reporting that
honestly is the difference between a verifier and a rubber stamp.

## Commitments

Three things are committed to with SHA-256 over a fully specified canonical
JSON encoding:

- **the checkpoint** binds the artifact to the state it carries;
- **the summary** binds the prose a successor reads to the structured world;
- **the world** is what independent encoders must agree on.

Every recipe is written out in [HANDOFF_CONTRACT.md](HANDOFF_CONTRACT.md) so an
implementation in another language can reproduce them byte for byte.

## The semantic world

The *world* is the meaning of an artifact once aliases are resolved, values
replaced by their digests, and ordering normalised.

This is what makes `babelci diff` useful. Two artifacts that serialise
completely differently can have the same world digest, and a line diff would
scream about both. Two artifacts differing by one character can have different
worlds, and a line diff would shrug.

## Authority agreement

Babel encodes every artifact into that world **twice**, with two encoders that
share nothing but the output schema:

- **Authority A** walks the artifact as a nested document, the way a reader
  would;
- **Authority B** shreds it into flat relation tuples and reconstitutes the
  world by joining them, the way a database would.

When they disagree, the artifact is ambiguous. No vote is taken and no winner
is picked — the disagreement *is* the result.

This is not redundancy. It is the only way a single implementation notices its
own blind spots. The `authority-disagreement` lab case is a short name bound to
two different targets: a dictionary-based reader silently keeps the last one
and never reports anything, which is what almost any hand-written parser would
do. Having a second reader is what makes the ambiguity visible.

## External truth, and why it is separate

Everything above is *internal consistency*. It cannot distinguish a true world
from a coherent false one, because a coherent false world is internally
consistent by construction.

An **external receipt** is an acceptance or rejection issued by something that
is not the artifact and not the verifier: a test run, a repository scan, a
production probe, a human. Babel does not issue it. Babel checks that the
receipt was issued against *this* world and reports what it said.

That relocates trust rather than removing it. The receipt's `trust_root` field
exists so the thing you are now trusting has to be named out loud. That is the
honest outcome, and pretending otherwise would be the dishonest one.

## Expectations

An artifact declares what it carries. An **expectation** declares what a
successor is *required* to carry — committed to the repository, not written by
the agent being checked.

That asymmetry is the point. An agent that omits a constraint has produced a
smaller valid artifact. An expectation is how the repository, rather than the
agent, decides what must survive.

## Where this came from

Babel Context Integrity is the product-shaped part of a private research
programme on context handoff integrity that ran entirely offline with scripted
fixture agents. Each lab case here names the private result it derives from.
The public claims are deliberately weaker than the private ones. See
[RESULTS.md](RESULTS.md) and [../paper/README.md](../paper/README.md).
