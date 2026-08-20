# Finding codes

Every failure `babelci verify` reports carries a code. Codes are stable: a code
never changes meaning, and new ones are added rather than repurposed. Grep for
one here.

Severity is `fail` (affects the verdict and the exit code) or `note` (does
not). `--json` output carries the severity on every finding.

---

## Structure

Checked first. If any of these fire, verification **stops** — deeper layers
would be indexing fields that may not exist, and reporting seven green ticks
for checks that never ran would be a lie.

Invalid JSON is not a finding. A file that does not parse has not been verified
at all, so the CLI reports it as a usage error and exits 2.

### `CONTRACT_VERSION_MISMATCH`
The artifact declares a contract version this build does not implement. The
verifier refuses rather than guessing which fields it recognises — silently
ignoring an unknown field is how a newer artifact gets a green tick for a check
that never happened. See [COMPATIBILITY.md](COMPATIBILITY.md).

### `SCHEMA_VIOLATION`
A required field is missing, an unknown field is present, or a value has the
wrong type. `where` gives a JSON path.

### `MALFORMED_DIGEST`
A field that must be a commitment is not `sha256:` followed by 64 lowercase hex
characters.

---

## Identity

Only fires when an expectation supplies something to compare against.

### `TASK_IDENTITY_MISMATCH`
The artifact is about different work than the expectation names. Nothing else
in the comparison is meaningful when this fires.

### `PRODUCER_IDENTITY_MISMATCH`
A different agent produced this handoff than the expectation named.

### `CONSUMER_IDENTITY_MISMATCH`
The artifact is addressed to a different successor than expected.

---

## Checkpoint

### `CHECKPOINT_COMMITMENT_MISMATCH`
`checkpoint.state_digest` does not recompute from the state the artifact
carries. Something was edited after the commitment was taken. The recipe is in
[HANDOFF_CONTRACT.md](HANDOFF_CONTRACT.md#checkpoint).

### `CHECKPOINT_REPLAY`
The artifact does not declare the parent checkpoint the expectation requires. A
valid but stale handoff presented where a successor was expected. Valid is not
the same as current.

---

## Provenance

### `PROVENANCE_ROOT_UNDECLARED`
No provenance edge reaches the declared `authority_root`, so nothing in the
handoff is grounded in anything.

### `PROVENANCE_EDGE_DANGLING`
An edge ends at a node that is neither the root nor has an onward edge. The
chain hangs in mid-air.

### `PROVENANCE_CHAIN_BROKEN`
An object names a provenance label that does not reach the authority root. An
assertion with no path to the root is an assertion with no source.

### `PROVENANCE_CYCLE`
An object's provenance chain loops without reaching the root.

### `ALIAS_NOT_BIJECTIVE`
Two alias names resolve to the same canonical name. A reference that used to be
unambiguous no longer is. This is what compaction does when it shortens
identifiers carelessly.

### `ALIAS_TARGET_MISSING`
An alias points at something that is not an object, a provenance source, or the
authority root in this handoff.

> One alias name bound to **two different** targets is deliberately not checked
> here. It surfaces at the authority-agreement layer as
> `AUTHORITY_DISAGREEMENT`, because a single implementation using a dictionary
> silently keeps the last binding and never notices. See
> [ARCHITECTURE.md](ARCHITECTURE.md#the-world-encoder).

---

## Retained constraints

The reason this project exists.

### `RETAINED_CONSTRAINT_MISSING`
A constraint the expectation required to survive is absent.

### `RETAINED_CONSTRAINT_MODIFIED`
A constraint survived under the same identifier but its statement changed. This
is the failure identifier-only checking misses: a rewritten rule passing as the
original.

### `REQUIRED_OBJECT_MISSING`
An object the expectation required is absent. The artifact is still valid JSON
and still internally consistent; it just no longer carries what the task needs.
This is what compaction loss looks like.

### `REQUIRED_DECISION_MISSING`
A decision the expectation required is neither present nor named by another
decision's `supersedes`. It was dropped rather than superseded, so the
successor is free to reopen it.

**Presence only.** A decision that keeps its identifier and changes its
*content* is a silent reversal, and a single artifact contains no evidence that
it happened. That is `babelci diff`'s job — see the `decision-reversed` case in
[RESULTS.md](RESULTS.md).

### `UNRESOLVED_ISSUE_UNDECLARED`
An open issue the expectation tracks is neither still listed in `unresolved`
nor named by a decision's `supersedes`. It did not get resolved; it got
dropped.

### `SUMMARY_COMMITMENT_MISMATCH`
The prose summary is not bound to the world the artifact encodes — either the
text or the state changed after the commitment. The summary is the part a
successor actually reads, so it is bound to the structure that justifies it.

---

## Conflicts

### `DUPLICATE_OBJECT_CONFLICT`
One `object_id` is asserted more than once with different values and no
declared `supersedes`. Equal-rank conflicts fail closed; picking one by
document order would be a coin flip wearing a suit.

Identical restatements of the same value are not a conflict.

### `DECISION_SUPERSEDES_MISSING`
A decision supersedes something neither the artifact nor the expectation
mentions. Only checked when an expectation is supplied, because a decision that
resolves an issue necessarily removes that issue from the artifact.

---

## Authority agreement

### `AUTHORITY_DISAGREEMENT`
The two independent encoders do not describe the same world. The artifact is
ambiguous. **No vote is taken** and no winner is picked — the disagreement is
the result.

### `AUTHORITY_COMMITMENT_MISMATCH`
A declared authority commits to a world this artifact does not encode. Either
the artifact changed after that authority computed its commitment, or the
authority computed it over something else.

### `AUTHORITY_SINGLE_ENCODING` — severity `note`
This verifier's own two encoders agreed, but the producer declared no
independently computed commitment to compare against, so the layer reports
`not established`. Does not fail the run. The verifier agreeing with itself is
a self-check, and calling it `verified` would imply the stronger property of
producer-side independence — which nothing here established.

---

## External truth

The only layer that can speak to truth rather than integrity.

### `EXTERNAL_RECEIPT_REJECTED`
Something outside the artifact examined the world it describes and rejected it.
This fails verification regardless of every layer above — which is the entire
point. See the `common-mode` case in [RESULTS.md](RESULTS.md).

### `EXTERNAL_RECEIPT_WORLD_MISMATCH`
The receipt was issued against a different world than the artifact encodes. An
acceptance for some other artifact is not an acceptance for this one.

### `EXTERNAL_RECEIPT_ABSENT` — severity `note`
No out-of-band receipt was supplied, so the layer reports `not established`.
Does not fail the run. It is not a defect to lack a receipt; it *is* a
misrepresentation to call an unexamined layer clean.

---

## Diff rules

`babelci diff` uses a separate vocabulary. See
[DIFF_RULES.md](DIFF_RULES.md) or run `babelci rules`.
