"""Constants and vocabulary of the Babel Handoff Contract.

Nothing in this module makes a decision. It fixes the names that the schema,
the verifier, the differ and the documentation all share, so that a finding
code printed by the CLI can be grepped for in the specification.
"""

from __future__ import annotations

CONTRACT_VERSION = "0.1"
CONTRACT_ID = "babel-handoff/0.1"

# Domain-separation tags. See canonical.digest.
WORLD_DOMAIN = b"BABEL_PUBLIC_HANDOFF_WORLD/0.1\0"
CHECKPOINT_DOMAIN = b"BABEL_HANDOFF_CHECKPOINT/0.1\0"
SUMMARY_DOMAIN = b"BABEL_HANDOFF_SUMMARY/0.1\0"

# ---------------------------------------------------------------------------
# Verification layers.
#
# The layers are ordered and never collapsed into a single score. A handoff can
# be structurally perfect and semantically wrong; it can be semantically
# coherent and still describe a world that never existed. Each layer answers a
# different question and the CLI prints them separately for that reason.
# ---------------------------------------------------------------------------

LAYER_STRUCTURE = "structure"
LAYER_IDENTITY = "identity"
LAYER_CHECKPOINT = "checkpoint"
LAYER_PROVENANCE = "provenance"
LAYER_CONSTRAINTS = "retained constraints"
LAYER_CONFLICTS = "conflicts"
LAYER_AUTHORITIES = "authority agreement"
LAYER_EXTERNAL = "external truth"

LAYERS = (
    LAYER_STRUCTURE,
    LAYER_IDENTITY,
    LAYER_CHECKPOINT,
    LAYER_PROVENANCE,
    LAYER_CONSTRAINTS,
    LAYER_CONFLICTS,
    LAYER_AUTHORITIES,
    LAYER_EXTERNAL,
)

# What each layer is entitled to conclude. Quoted verbatim by `babelci explain`
# so that the tool states its own limits rather than leaving them to a README
# the user may never open.
LAYER_MEANING = {
    LAYER_STRUCTURE:
        "The artifact parses and satisfies the declared contract version's shape.",
    LAYER_IDENTITY:
        "Task, producer and consumer identifiers are well formed and, when an "
        "expectation was supplied, match it.",
    LAYER_CHECKPOINT:
        "The declared checkpoint commitment recomputes from the state the "
        "artifact actually carries.",
    LAYER_PROVENANCE:
        "Every asserted object traces to the declared authority root through "
        "connected, acyclic edges, and that root is the one the expectation "
        "required when it named one.",
    LAYER_CONSTRAINTS:
        "Constraints the producer marked as surviving the handoff are still "
        "present and unmodified.",
    LAYER_CONFLICTS:
        "No two assertions about the same object disagree without a declared "
        "resolution.",
    LAYER_AUTHORITIES:
        "Independently computed encodings of this artifact agree on the same "
        "semantic world. Agreement is not truth.",
    LAYER_EXTERNAL:
        "An out-of-band receipt, produced by something other than this "
        "artifact, accepted the world the artifact describes.",
}

# ---------------------------------------------------------------------------
# Finding codes.
#
# Stable identifiers. New codes may be added in a minor contract revision;
# existing codes do not change meaning.
# ---------------------------------------------------------------------------

# structure
# (Invalid JSON is a usage error at the CLI boundary, exit 2, not a finding:
#  a file that does not parse has not been verified at all.)
CONTRACT_VERSION_MISMATCH = "CONTRACT_VERSION_MISMATCH"
SCHEMA_VIOLATION = "SCHEMA_VIOLATION"
MALFORMED_DIGEST = "MALFORMED_DIGEST"

# identity
TASK_IDENTITY_MISMATCH = "TASK_IDENTITY_MISMATCH"
PRODUCER_IDENTITY_MISMATCH = "PRODUCER_IDENTITY_MISMATCH"
CONSUMER_IDENTITY_MISMATCH = "CONSUMER_IDENTITY_MISMATCH"

# checkpoint
CHECKPOINT_COMMITMENT_MISMATCH = "CHECKPOINT_COMMITMENT_MISMATCH"
CHECKPOINT_REPLAY = "CHECKPOINT_REPLAY"

# provenance
PROVENANCE_ROOT_UNDECLARED = "PROVENANCE_ROOT_UNDECLARED"
PROVENANCE_ROOT_MISMATCH = "PROVENANCE_ROOT_MISMATCH"
PROVENANCE_EDGE_DANGLING = "PROVENANCE_EDGE_DANGLING"
PROVENANCE_CHAIN_BROKEN = "PROVENANCE_CHAIN_BROKEN"
PROVENANCE_CYCLE = "PROVENANCE_CYCLE"
ALIAS_NOT_BIJECTIVE = "ALIAS_NOT_BIJECTIVE"
ALIAS_TARGET_MISSING = "ALIAS_TARGET_MISSING"

# retained constraints
RETAINED_CONSTRAINT_MISSING = "RETAINED_CONSTRAINT_MISSING"
RETAINED_CONSTRAINT_MODIFIED = "RETAINED_CONSTRAINT_MODIFIED"
REQUIRED_OBJECT_MISSING = "REQUIRED_OBJECT_MISSING"
REQUIRED_DECISION_MISSING = "REQUIRED_DECISION_MISSING"
SUMMARY_COMMITMENT_MISMATCH = "SUMMARY_COMMITMENT_MISMATCH"

# conflicts
DUPLICATE_OBJECT_CONFLICT = "DUPLICATE_OBJECT_CONFLICT"
DECISION_SUPERSEDES_MISSING = "DECISION_SUPERSEDES_MISSING"
UNRESOLVED_ISSUE_UNDECLARED = "UNRESOLVED_ISSUE_UNDECLARED"

# authorities
AUTHORITY_DISAGREEMENT = "AUTHORITY_DISAGREEMENT"
AUTHORITY_COMMITMENT_MISMATCH = "AUTHORITY_COMMITMENT_MISMATCH"
AUTHORITY_SINGLE_ENCODING = "AUTHORITY_SINGLE_ENCODING"

# external truth
EXTERNAL_RECEIPT_REJECTED = "EXTERNAL_RECEIPT_REJECTED"
EXTERNAL_RECEIPT_WORLD_MISMATCH = "EXTERNAL_RECEIPT_WORLD_MISMATCH"
EXTERNAL_RECEIPT_ABSENT = "EXTERNAL_RECEIPT_ABSENT"

# ---------------------------------------------------------------------------
# Severities.
#
# `note` never fails a run. It exists so that the tool can say "nothing
# out-of-band confirmed this" without pretending that silence is a defect.
# ---------------------------------------------------------------------------

SEVERITY_FAIL = "fail"
SEVERITY_WARN = "warn"
SEVERITY_NOTE = "note"

# Diff verdicts. Each is produced only by an explicit rule in diff.RULES.
SAFE = "SAFE"
REVIEW = "REVIEW"
REFUSE = "REFUSE"

# Exit codes.
EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_REVIEW = 3

__all__ = [name for name in dir() if name.isupper() or name.startswith("LAYER")]
