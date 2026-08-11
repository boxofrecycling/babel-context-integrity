"""The lab scenario and its failure classes.

The scenario is a fictional migration handed from one coding agent to another.
It was chosen because every failure class below has an obvious real-world
reading: a constraint that quietly stops being enforced, a decision that gets
reversed without anyone noticing, a summary that no longer matches the state it
describes.

Each case is a single named mutation of :func:`clean`. The lab reports what the
verifier concluded and, for the cases where it matters, at which layer.
"""

from __future__ import annotations

import copy
from typing import Any, Callable

from ..canonical import digest
from ..contract import (
    LAYER_AUTHORITIES, LAYER_CHECKPOINT, LAYER_CONFLICTS, LAYER_CONSTRAINTS,
    LAYER_EXTERNAL, LAYER_PROVENANCE,
)
from ..seal import issue_receipt, seal

AUTHORITY_ROOT = "repo@a1b2c3d4"

SUMMARY_TEXT = (
    "Migrated the auth layer to OIDC behind a feature flag. Okta is the "
    "provider. Sessions migrate lazily on next login; the legacy session table "
    "is still live and must not be dropped. All 312 baseline tests pass. "
    "Refresh-token rotation interval is still unagreed with security."
)


def clean() -> dict[str, Any]:
    """The baseline handoff: agent A hands the migration to agent B."""
    draft: dict[str, Any] = {
        "babel_handoff": "0.1",
        "handoff_id": "handoff-4412-01",
        "task": {
            "task_id": "PR-4412/migrate-auth-to-oidc",
            "title": "Migrate the auth layer from session cookies to OIDC",
            "family": "code-migration",
        },
        "producer": {"agent": "agent-a", "role": "implementer",
                     "run_id": "run-0001"},
        "consumer": {"agent": "agent-b", "role": "implementer"},
        "checkpoint": {"checkpoint_id": "cp-4412-01", "state_digest": ""},
        "objects": [
            {"object_id": "auth.provider", "kind": "fact",
             "value": "okta-oidc", "required": True,
             "provenance": "scan/config"},
            {"object_id": "legacy.sessions", "kind": "fact",
             "value": 1843, "required": True, "provenance": "query/db"},
            {"object_id": "test.baseline", "kind": "metric",
             "value": {"passed": 312, "failed": 0}, "required": True,
             "provenance": "ci/run-9981"},
            {"object_id": "flag.name", "kind": "fact",
             "value": "auth_oidc_enabled", "required": False,
             "provenance": "scan/config"},
        ],
        "retained_constraints": [
            {"constraint_id": "C1", "binding": "MUST",
             "statement": "Do not drop the legacy session table until the "
                          "migration is verified in production.",
             "provenance": AUTHORITY_ROOT},
            {"constraint_id": "C2", "binding": "MUST",
             "statement": "Every new endpoint must require the oidc:read scope.",
             "provenance": AUTHORITY_ROOT},
            {"constraint_id": "C3", "binding": "SHOULD",
             "statement": "Extend AuthMiddleware rather than adding a parallel "
                          "auth path.",
             "provenance": AUTHORITY_ROOT},
        ],
        "decisions": [
            {"decision_id": "D1", "choice": "Use Okta as the OIDC provider.",
             "rationale": "Already the org IdP; no new vendor review needed.",
             "provenance": "scan/config"},
            {"decision_id": "D2",
             "choice": "Migrate sessions lazily on next login.",
             "rationale": "A batch job would need a maintenance window.",
             "provenance": "query/db"},
        ],
        "unresolved": [
            {"issue_id": "U1",
             "statement": "Refresh-token rotation interval is not agreed with "
                          "the security team.",
             "blocking": True},
        ],
        "artifacts": [
            {"path": "src/auth/oidc.py",
             "digest": digest("src/auth/oidc.py@01"), "role": "implementation"},
        ],
        "provenance": {
            "authority_root": AUTHORITY_ROOT,
            "edges": [
                ["scan/config", AUTHORITY_ROOT],
                ["query/db", AUTHORITY_ROOT],
                ["ci/run-9981", AUTHORITY_ROOT],
            ],
        },
        "aliases": [["AP", "auth.provider"]],
        "summary": {"text": SUMMARY_TEXT, "commitment": ""},
    }
    return seal(draft, declare_authority="agent-a")


def expectation() -> dict[str, Any]:
    """What a successor's handoff is required to still satisfy.

    This is what a repository would commit to ``.babel/expect.json`` so CI can
    check every later handoff against it.
    """
    base = clean()
    return {
        "babel_expectation": "0.1",
        "task_id": base["task"]["task_id"],
        "authority_root": AUTHORITY_ROOT,
        "required_constraints": [
            {"constraint_id": item["constraint_id"],
             "statement_commitment": digest(item["statement"])}
            for item in base["retained_constraints"]
            if item["binding"] == "MUST"
        ],
        "required_objects": sorted(
            item["object_id"] for item in base["objects"]
            if item.get("required")),
        "required_unresolved": ["U1"],
    }


# ---------------------------------------------------------------------------
# Mutations. Each takes the clean handoff and returns a broken one.
# ---------------------------------------------------------------------------

def _reseal(handoff: dict[str, Any]) -> dict[str, Any]:
    """Recompute commitments, i.e. a producer that mutated state honestly."""
    return seal(handoff, declare_authority="agent-a")


def _successor(handoff: dict[str, Any]) -> dict[str, Any]:
    handoff["handoff_id"] = "handoff-4412-02"
    handoff["producer"] = {"agent": "agent-b", "role": "implementer",
                           "run_id": "run-0002"}
    handoff["consumer"] = {"agent": "agent-c", "role": "reviewer"}
    handoff["checkpoint"] = {"checkpoint_id": "cp-4412-02",
                             "parent_checkpoint_id": "cp-4412-01",
                             "state_digest": ""}
    return handoff


def case_restart_resume() -> dict[str, Any]:
    """Agent B resumes, does real work, and hands on correctly."""
    handoff = _successor(clean())
    handoff["objects"].append({
        "object_id": "migration.applied", "kind": "fact", "value": True,
        "required": True, "provenance": "ci/run-9981"})
    handoff["decisions"].append({
        "decision_id": "D3",
        "choice": "Rotate refresh tokens every 12 hours.",
        "rationale": "Security team agreed on 2026-08-11.",
        "supersedes": "U1", "provenance": "ci/run-9981"})
    handoff["unresolved"] = []
    handoff["summary"]["text"] = (
        SUMMARY_TEXT.replace(
            "Refresh-token rotation interval is still unagreed with security.",
            "Refresh-token rotation is set to 12 hours, agreed with security."))
    return _reseal(handoff)


def case_constraint_dropped() -> dict[str, Any]:
    """The MUST constraint protecting the legacy table stops being carried."""
    handoff = _successor(clean())
    handoff["retained_constraints"] = [
        item for item in handoff["retained_constraints"]
        if item["constraint_id"] != "C1"]
    return _reseal(handoff)


def case_constraint_softened() -> dict[str, Any]:
    """The constraint survives by id but its statement is rewritten."""
    handoff = _successor(clean())
    for item in handoff["retained_constraints"]:
        if item["constraint_id"] == "C1":
            item["statement"] = ("Avoid dropping the legacy session table if "
                                 "convenient.")
    return _reseal(handoff)


def case_decision_reversed() -> dict[str, Any]:
    """A settled decision is reversed with no record that it was reversed."""
    handoff = _successor(clean())
    for item in handoff["decisions"]:
        if item["decision_id"] == "D2":
            item["choice"] = "Migrate sessions in a single batch job."
            item["rationale"] = "Simpler to reason about."
    return _reseal(handoff)


def case_checkpoint_mismatch() -> dict[str, Any]:
    """State was edited after the checkpoint was committed."""
    handoff = clean()
    for item in handoff["objects"]:
        if item["object_id"] == "legacy.sessions":
            item["value"] = 0
    return handoff  # deliberately not resealed


def case_summary_drift() -> dict[str, Any]:
    """The prose the successor reads no longer matches the state it describes."""
    handoff = clean()
    handoff["summary"]["text"] = SUMMARY_TEXT.replace(
        "must not be dropped", "can be dropped once tests pass")
    return handoff  # deliberately not resealed


def case_provenance_break() -> dict[str, Any]:
    """Compaction removed the edge that connected a fact to the repository."""
    handoff = _successor(clean())
    handoff["provenance"]["edges"] = [
        edge for edge in handoff["provenance"]["edges"]
        if edge[0] != "query/db"]
    return _reseal(handoff)


def case_alias_collapse() -> dict[str, Any]:
    """Compaction gave one source two short names, so a reference is ambiguous.

    Both ``S1`` and ``S2`` shorten ``query/db``. Two facts that used to be
    distinguishable by where they came from are now indistinguishable.
    """
    handoff = _successor(clean())
    handoff["aliases"] = [["AP", "auth.provider"],
                          ["S1", "query/db"], ["S2", "query/db"]]
    for item in handoff["objects"]:
        if item["object_id"] == "legacy.sessions":
            item["provenance"] = "S1"
        if item["object_id"] == "flag.name":
            item["provenance"] = "S2"
    return _reseal(handoff)


def case_authority_disagreement() -> dict[str, Any]:
    """One short name is bound twice, and the two encodings part company.

    ``S1`` shortens both ``query/db`` and ``ci/run-9981``. Authority A reads the
    alias table as a mapping and silently keeps the last binding, which is what
    a single implementation using a dict would do and would never report.
    Authority B reads it as a join and keeps both. Neither is wrong; the
    artifact is ambiguous, and only having two readers makes that visible.
    """
    from ..verify import checkpoint_commitment

    handoff = _successor(clean())
    handoff["aliases"] = [["AP", "auth.provider"],
                          ["S1", "query/db"], ["S1", "ci/run-9981"]]
    for item in handoff["objects"]:
        if item["object_id"] == "legacy.sessions":
            item["provenance"] = "S1"
    # A summary cannot be sealed against a world the two encoders do not agree
    # on, which is itself the finding; this producer emitted none.
    handoff.pop("summary", None)
    handoff.pop("authorities", None)
    handoff["checkpoint"]["state_digest"] = ""
    handoff["checkpoint"]["state_digest"] = checkpoint_commitment(handoff)
    return handoff


def case_compression_loss() -> dict[str, Any]:
    """A compaction pass dropped a required object to save room."""
    handoff = _successor(clean())
    handoff["objects"] = [item for item in handoff["objects"]
                          if item["object_id"] != "test.baseline"]
    handoff["provenance"]["edges"] = [
        edge for edge in handoff["provenance"]["edges"]
        if edge[0] != "ci/run-9981"]
    return _reseal(handoff)


def case_duplicate_conflict() -> dict[str, Any]:
    """Two passes assert different values for the same object, neither ranked."""
    handoff = _successor(clean())
    handoff["objects"].append({
        "object_id": "legacy.sessions", "kind": "fact", "value": 0,
        "required": True, "provenance": "query/db"})
    return _reseal(handoff)


def case_stale_replay() -> dict[str, Any]:
    """A valid earlier handoff is replayed where a successor was expected."""
    handoff = clean()
    handoff["handoff_id"] = "handoff-4412-01-replay"
    return handoff


def case_common_mode() -> dict[str, Any]:
    """Everything local agrees. Every fact is wrong.

    The producer scanned the wrong branch. The artifact it emitted is perfectly
    self-consistent: the checkpoint recomputes, provenance connects, both
    encodings agree, the summary is bound to the state. Nothing inside the
    artifact can detect this, because nothing inside the artifact disagrees.

    The external receipt is issued by something that looked at the repository
    rather than at the handoff, and it rejects.
    """
    handoff = _successor(clean())
    for item in handoff["objects"]:
        if item["object_id"] == "auth.provider":
            item["value"] = "auth0-oidc"
        if item["object_id"] == "legacy.sessions":
            item["value"] = 12
    for item in handoff["decisions"]:
        if item["decision_id"] == "D1":
            item["choice"] = "Use Auth0 as the OIDC provider."
    handoff["summary"]["text"] = SUMMARY_TEXT.replace("Okta", "Auth0")
    handoff = _reseal(handoff)
    handoff["external_receipt"] = issue_receipt(
        handoff,
        receipt_id="receipt-4412-02",
        trust_root="repository working tree at repo@a1b2c3d4",
        accepted=False,
        findings=["auth.provider is okta-oidc in the tree, not auth0-oidc",
                  "legacy.sessions counted 1843 rows, not 12",
                  "D1 contradicts the recorded provider"])
    return handoff


def case_externally_confirmed() -> dict[str, Any]:
    """The same clean world, this time with an out-of-band receipt that accepts."""
    handoff = case_restart_resume()
    handoff["external_receipt"] = issue_receipt(
        handoff,
        receipt_id="receipt-4412-02-ok",
        trust_root="repository working tree at repo@a1b2c3d4",
        accepted=True)
    return handoff


# ---------------------------------------------------------------------------

Case = dict[str, Any]

CASES: list[Case] = [
    {
        "id": "clean",
        "title": "A well-formed handoff",
        "build": clean,
        "expect_verdict": "PASS",
        "expect_layer": None,
        "teaches": "Every layer that can run, runs. External truth is reported "
                   "as not established, because nothing outside the artifact "
                   "was consulted.",
        "mirrors": "restart-resume-integrity",
    },
    {
        "id": "restart-resume",
        "title": "A successor resumes and hands on correctly",
        "build": case_restart_resume,
        "expect_verdict": "PASS",
        "expect_layer": None,
        "teaches": "Work advanced, an open issue was closed by a decision that "
                   "names it, and the checkpoint declares its parent.",
        "mirrors": "restart-resume-integrity",
    },
    {
        "id": "constraint-dropped",
        "title": "A MUST constraint stops being carried",
        "build": case_constraint_dropped,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_CONSTRAINTS,
        "teaches": "The successor is free to drop the legacy table. Nothing in "
                   "the prose would have told you.",
        "mirrors": "handoff-corruption",
    },
    {
        "id": "constraint-softened",
        "title": "A constraint keeps its id and changes its meaning",
        "build": case_constraint_softened,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_CONSTRAINTS,
        "teaches": "Identifier-level checks are not enough; the statement is "
                   "committed to as well.",
        "mirrors": "semantic-equivalence",
    },
    {
        "id": "decision-reversed",
        "title": "A settled decision is silently reversed",
        "build": case_decision_reversed,
        "expect_verdict": "PASS",
        "expect_layer": None,
        "teaches": "verify cannot catch this from one artifact -- the reversal "
                   "is internally consistent. babelci diff against the "
                   "predecessor refuses it.",
        "mirrors": "semantic-equivalence",
        "diff_against": "clean",
        "expect_diff": "REFUSE",
    },
    {
        "id": "checkpoint-mismatch",
        "title": "State edited after the checkpoint was committed",
        "build": case_checkpoint_mismatch,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_CHECKPOINT,
        "teaches": "The commitment is over the state, so post-hoc edits do not "
                   "survive recomputation.",
        "mirrors": "handoff-corruption",
    },
    {
        "id": "summary-drift",
        "title": "The prose no longer matches the state",
        "build": case_summary_drift,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_CONSTRAINTS,
        "teaches": "The summary is the part a successor actually reads. It is "
                   "bound to the structured world it claims to describe.",
        "mirrors": "proof-carrying-summaries",
    },
    {
        "id": "provenance-break",
        "title": "A fact loses its chain to the repository",
        "build": case_provenance_break,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_PROVENANCE,
        "teaches": "An assertion with no path to the authority root is an "
                   "assertion with no source.",
        "mirrors": "duplicate-provenance-handling",
    },
    {
        "id": "alias-collapse",
        "title": "Compaction makes two names mean one thing",
        "build": case_alias_collapse,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_PROVENANCE,
        "teaches": "Shortening identifiers is where references quietly stop "
                   "being unambiguous.",
        "mirrors": "orthogonal-semantic-ablation",
    },
    {
        "id": "authority-disagreement",
        "title": "Two encodings read the same artifact differently",
        "build": case_authority_disagreement,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_AUTHORITIES,
        "teaches": "The artifact is ambiguous. No vote is taken and no winner "
                   "is picked; the disagreement is the result.",
        "mirrors": "second-verifier",
    },
    {
        "id": "compression-loss",
        "title": "Compaction drops a required object",
        "build": case_compression_loss,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_CONSTRAINTS,
        "teaches": "The artifact is still valid JSON, still self-consistent, "
                   "and no longer carries what the task requires.",
        "mirrors": "context-compression",
    },
    {
        "id": "duplicate-conflict",
        "title": "Two passes disagree and neither outranks the other",
        "build": case_duplicate_conflict,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_CONFLICTS,
        "teaches": "Equal-rank conflicts fail closed. Picking one by document "
                   "order would be a coin flip wearing a suit.",
        "mirrors": "duplicate-provenance-handling",
    },
    {
        "id": "stale-replay",
        "title": "An old handoff is replayed as if it were current",
        "build": case_stale_replay,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_CHECKPOINT,
        "teaches": "Valid is not the same as current. The expectation names the "
                   "parent checkpoint the successor must build on.",
        "mirrors": "proof-carrying-summaries",
        "needs_expectation": {"parent_checkpoint_id": "cp-4412-01"},
    },
    {
        "id": "externally-confirmed",
        "title": "A handoff an outside checker also accepted",
        "build": case_externally_confirmed,
        "expect_verdict": "PASS",
        "expect_layer": None,
        "teaches": "This is the only case in the lab where the external-truth "
                   "layer reaches a conclusion instead of abstaining.",
        "mirrors": "common-mode-trust-controls",
    },
    {
        "id": "common-mode",
        "title": "Everything agrees. Everything is wrong.",
        "build": case_common_mode,
        "expect_verdict": "FAIL",
        "expect_layer": LAYER_EXTERNAL,
        "teaches": "Seven layers of internal checking pass. The artifact is "
                   "coherent, committed and self-consistent, and it describes a "
                   "branch nobody worked on. Only the out-of-band receipt "
                   "rejects it -- and that receipt is now the thing you have to "
                   "trust.",
        "mirrors": "common-mode-trust-controls",
    },
]

CASES_BY_ID = {case["id"]: case for case in CASES}


def build(case_id: str) -> dict[str, Any]:
    return copy.deepcopy(CASES_BY_ID[case_id]["build"]())


__all__ = ["CASES", "CASES_BY_ID", "build", "clean", "expectation",
           "AUTHORITY_ROOT", "SUMMARY_TEXT"]
