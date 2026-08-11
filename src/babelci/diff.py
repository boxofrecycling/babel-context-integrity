"""Semantic drift between two handoff artifacts.

This is not a line diff. Two artifacts that serialise completely differently
can describe the same world, and two artifacts that differ by one character can
describe incompatible ones. The comparison therefore runs over the semantic
world computed by :mod:`babelci.authorities`, plus the contract fields that the
world deliberately omits.

Every reported change carries a verdict, and every verdict comes from exactly
one rule in :data:`RULES`. There is no heuristic and no scoring: if a change is
not covered by a rule it is reported as ``REVIEW`` with the rule id
``unclassified-change``, which is itself a rule.
"""

from __future__ import annotations

from typing import Any

from . import authorities
from .canonical import digest
from .contract import REFUSE, REVIEW, SAFE

RESULT_SCHEMA = "babel-diff/0.1"

_ORDER = {SAFE: 0, REVIEW: 1, REFUSE: 2}


# ---------------------------------------------------------------------------
# The rule table. `docs/DIFF_RULES.md` is generated from this structure, so the
# documentation cannot drift away from the implementation.
# ---------------------------------------------------------------------------

RULES: dict[str, dict[str, str]] = {
    "task-identity-changed": {
        "verdict": REFUSE,
        "headline": "The two artifacts are about different tasks.",
        "because": "the two artifacts are about different work, so nothing else "
                   "in the comparison is meaningful",
    },
    "authority-root-changed": {
        "verdict": REFUSE,
        "headline": "Facts now trace to a different authority.",
        "because": "the successor traces its facts to a different authority than "
                   "the predecessor did",
    },
    "must-constraint-removed": {
        "verdict": REFUSE,
        "headline": "A MUST constraint stopped being carried.",
        "because": "a constraint the predecessor marked MUST no longer survives",
    },
    "must-constraint-modified": {
        "verdict": REFUSE,
        "headline": "A MUST constraint changed meaning under the same name.",
        "because": "a MUST constraint kept its identifier but changed meaning, "
                   "which is how a rewritten rule passes as the original",
    },
    "should-constraint-removed": {
        "verdict": REVIEW,
        "headline": "An advisory constraint was dropped.",
        "because": "an advisory constraint was dropped; this may be intended",
    },
    "should-constraint-modified": {
        "verdict": REVIEW,
        "headline": "An advisory constraint changed meaning under the same name.",
        "because": "an advisory constraint changed meaning under the same identifier",
    },
    "constraint-added": {
        "verdict": SAFE,
        "headline": "A new constraint was recorded.",
        "because": "adding a constraint narrows what the successor may do",
    },
    "decision-reversed": {
        "verdict": REFUSE,
        "headline": "A recorded decision changed without declaring what it replaced.",
        "because": "a recorded decision changed without declaring what it supersedes, "
                   "so the reversal is invisible to anyone reading the successor",
    },
    "decision-superseded": {
        "verdict": REVIEW,
        "headline": "A decision was replaced by one that names it.",
        "because": "the decision changed and said so; a human should confirm the "
                   "reversal was intended",
    },
    "decision-removed": {
        "verdict": REFUSE,
        "headline": "A decision disappeared rather than being superseded.",
        "because": "a decision disappeared rather than being superseded, so the "
                   "successor may silently reopen it",
    },
    "decision-added": {
        "verdict": SAFE,
        "headline": "A new decision was recorded.",
        "because": "new decisions are the normal product of doing the work",
    },
    "required-object-removed": {
        "verdict": REFUSE,
        "headline": "A required object is gone.",
        "because": "an object the predecessor marked required is gone",
    },
    "object-removed": {
        "verdict": REVIEW,
        "headline": "An optional object was dropped.",
        "because": "an optional object was dropped, which is what compaction does "
                   "and also what context loss looks like",
    },
    "object-value-changed": {
        "verdict": REVIEW,
        "headline": "An object now asserts a different value.",
        "because": "the same object now asserts a different value",
    },
    "object-added": {
        "verdict": SAFE,
        "headline": "A new object was recorded.",
        "because": "new objects are the normal product of doing the work",
    },
    "unresolved-issue-dropped": {
        "verdict": REVIEW,
        "headline": "An open question vanished without being resolved.",
        "because": "an open question vanished without a decision resolving it",
    },
    "unresolved-issue-resolved": {
        "verdict": SAFE,
        "headline": "An open question was closed by a decision that names it.",
        "because": "the open question is named by a decision that supersedes it",
    },
    "unresolved-issue-added": {
        "verdict": SAFE,
        "headline": "A new open question was recorded.",
        "because": "the successor inherits a newly surfaced open question",
    },
    "alias-bijection-lost": {
        "verdict": REFUSE,
        "headline": "Two names now collapse onto one object.",
        "because": "two names now collapse onto one object, so a reference that "
                   "used to be unambiguous no longer is",
    },
    "provenance-edge-removed": {
        "verdict": REVIEW,
        "headline": "A provenance edge was dropped.",
        "because": "a provenance edge was dropped; run verify on the successor to "
                   "see whether the chain still reaches the root",
    },
    "provenance-edge-added": {
        "verdict": SAFE,
        "headline": "A provenance edge was added.",
        "because": "additional provenance can only lengthen the chain",
    },
    "checkpoint-advanced": {
        "verdict": SAFE,
        "headline": "The checkpoint advanced from its declared parent.",
        "because": "the successor names the predecessor as its parent checkpoint",
    },
    "checkpoint-reparented": {
        "verdict": REVIEW,
        "headline": "The checkpoint changed without naming the predecessor.",
        "because": "the checkpoint changed without naming the predecessor as parent, "
                   "so the two artifacts may not be on the same line of work",
    },
    "conflict-introduced": {
        "verdict": REFUSE,
        "headline": "Contradictory values are now asserted for one object.",
        "because": "the successor asserts contradictory values for one object",
    },
    "conflict-resolved": {
        "verdict": SAFE,
        "headline": "A contradiction was resolved.",
        "because": "a contradiction present in the predecessor is gone",
    },
    "external-acceptance-lost": {
        "verdict": REFUSE,
        "headline": "An outside checker used to accept this world and no longer does.",
        "because": "an out-of-band receipt used to accept this world and no longer does",
    },
    "unclassified-change": {
        "verdict": REVIEW,
        "headline": "The artifacts differ in a way v0.1 has no rule for.",
        "because": "the artifacts differ in a way v0.1 has no rule for; a human "
                   "decides rather than the tool guessing",
    },
}


def _verdict(rule: str) -> str:
    return RULES[rule]["verdict"]


def _index(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def diff(old: dict[str, Any], new: dict[str, Any], *,
         old_source: str | None = None,
         new_source: str | None = None) -> dict[str, Any]:
    """Compare two handoff artifacts and report semantic drift."""
    changes: list[dict[str, Any]] = []

    def record(rule: str, subject: str, detail: str, **extra: Any) -> None:
        changes.append({
            "rule": rule,
            "verdict": _verdict(rule),
            "headline": RULES[rule]["headline"],
            "subject": subject,
            "detail": detail,
            "because": RULES[rule]["because"],
            **extra,
        })

    # -- identity -----------------------------------------------------------
    if old["task"]["task_id"] != new["task"]["task_id"]:
        record("task-identity-changed", "task",
               f"{old['task']['task_id']!r} -> {new['task']['task_id']!r}",
               before=old["task"]["task_id"], after=new["task"]["task_id"])

    if old["provenance"]["authority_root"] != new["provenance"]["authority_root"]:
        record("authority-root-changed", "provenance.authority_root",
               f"{old['provenance']['authority_root']!r} -> "
               f"{new['provenance']['authority_root']!r}",
               before=old["provenance"]["authority_root"],
               after=new["provenance"]["authority_root"])

    # -- checkpoint ---------------------------------------------------------
    old_checkpoint = old["checkpoint"]["checkpoint_id"]
    new_checkpoint = new["checkpoint"]["checkpoint_id"]
    if old_checkpoint != new_checkpoint:
        if new["checkpoint"].get("parent_checkpoint_id") == old_checkpoint:
            record("checkpoint-advanced", "checkpoint",
                   f"{old_checkpoint} -> {new_checkpoint}",
                   before=old_checkpoint, after=new_checkpoint)
        else:
            record("checkpoint-reparented", "checkpoint",
                   f"{old_checkpoint} -> {new_checkpoint} "
                   f"(parent declared: "
                   f"{new['checkpoint'].get('parent_checkpoint_id')!r})",
                   before=old_checkpoint, after=new_checkpoint)

    # -- retained constraints ----------------------------------------------
    old_constraints = _index(old.get("retained_constraints", []) or [],
                             "constraint_id")
    new_constraints = _index(new.get("retained_constraints", []) or [],
                             "constraint_id")
    for constraint_id, before in sorted(old_constraints.items()):
        after = new_constraints.get(constraint_id)
        binding = before["binding"]
        if after is None:
            rule = ("must-constraint-removed" if binding == "MUST"
                    else "should-constraint-removed")
            record(rule, f"retained_constraints[{constraint_id}]",
                   f"{binding} constraint dropped",
                   before=before["statement"], after=None)
        elif digest(before["statement"]) != digest(after["statement"]):
            rule = ("must-constraint-modified" if binding == "MUST"
                    else "should-constraint-modified")
            record(rule, f"retained_constraints[{constraint_id}]",
                   "statement changed under the same identifier",
                   before=before["statement"], after=after["statement"])
    for constraint_id in sorted(set(new_constraints) - set(old_constraints)):
        record("constraint-added", f"retained_constraints[{constraint_id}]",
               new_constraints[constraint_id]["binding"] + " constraint added",
               before=None, after=new_constraints[constraint_id]["statement"])

    # -- decisions ----------------------------------------------------------
    old_decisions = _index(old.get("decisions", []) or [], "decision_id")
    new_decisions = _index(new.get("decisions", []) or [], "decision_id")
    superseded = {row.get("supersedes")
                  for row in (new.get("decisions", []) or [])
                  if row.get("supersedes")}
    for decision_id, before in sorted(old_decisions.items()):
        after = new_decisions.get(decision_id)
        if after is None:
            if decision_id in superseded:
                record("decision-superseded", f"decisions[{decision_id}]",
                       "replaced by a decision that names it",
                       before=before["choice"], after=None)
            else:
                record("decision-removed", f"decisions[{decision_id}]",
                       "decision no longer present",
                       before=before["choice"], after=None)
        elif digest(before["choice"]) != digest(after["choice"]):
            rule = ("decision-superseded" if after.get("supersedes")
                    else "decision-reversed")
            record(rule, f"decisions[{decision_id}]",
                   "choice changed under the same identifier",
                   before=before["choice"], after=after["choice"])
    for decision_id in sorted(set(new_decisions) - set(old_decisions)):
        record("decision-added", f"decisions[{decision_id}]",
               new_decisions[decision_id]["choice"],
               before=None, after=new_decisions[decision_id]["choice"])

    # -- objects ------------------------------------------------------------
    old_objects = _index(old.get("objects", []), "object_id")
    new_objects = _index(new.get("objects", []), "object_id")
    for object_id, before in sorted(old_objects.items()):
        after = new_objects.get(object_id)
        if after is None:
            rule = ("required-object-removed" if before.get("required")
                    else "object-removed")
            record(rule, f"objects[{object_id}]", f"{before['kind']} dropped",
                   before=before["value"], after=None)
        elif digest(before["value"]) != digest(after["value"]):
            record("object-value-changed", f"objects[{object_id}]",
                   f"{before['kind']} value changed",
                   before=before["value"], after=after["value"])
    for object_id in sorted(set(new_objects) - set(old_objects)):
        record("object-added", f"objects[{object_id}]",
               f"{new_objects[object_id]['kind']} added",
               before=None, after=new_objects[object_id]["value"])

    # -- unresolved ---------------------------------------------------------
    old_issues = _index(old.get("unresolved", []) or [], "issue_id")
    new_issues = _index(new.get("unresolved", []) or [], "issue_id")
    for issue_id, before in sorted(old_issues.items()):
        if issue_id in new_issues:
            continue
        rule = ("unresolved-issue-resolved" if issue_id in superseded
                else "unresolved-issue-dropped")
        record(rule, f"unresolved[{issue_id}]", before["statement"],
               before=before["statement"], after=None)
    for issue_id in sorted(set(new_issues) - set(old_issues)):
        record("unresolved-issue-added", f"unresolved[{issue_id}]",
               new_issues[issue_id]["statement"],
               before=None, after=new_issues[issue_id]["statement"])

    # -- aliases ------------------------------------------------------------
    def bijective(handoff: dict[str, Any]) -> bool:
        pairs = handoff.get("aliases", []) or []
        names = [pair[0] for pair in pairs]
        targets = [pair[1] for pair in pairs]
        return len(set(names)) == len(names) and len(set(targets)) == len(targets)

    if bijective(old) and not bijective(new):
        record("alias-bijection-lost", "aliases",
               "the successor's alias table maps two names onto one object",
               before=old.get("aliases", []), after=new.get("aliases", []))

    # -- provenance edges ---------------------------------------------------
    old_edges = {tuple(edge) for edge in old["provenance"]["edges"]}
    new_edges = {tuple(edge) for edge in new["provenance"]["edges"]}
    for edge in sorted(old_edges - new_edges):
        record("provenance-edge-removed", "provenance.edges",
               f"{edge[0]} -> {edge[1]}", before=list(edge), after=None)
    for edge in sorted(new_edges - old_edges):
        record("provenance-edge-added", "provenance.edges",
               f"{edge[0]} -> {edge[1]}", before=None, after=list(edge))

    # -- conflicts ----------------------------------------------------------
    def conflicts(handoff: dict[str, Any]) -> set[str]:
        grouped: dict[str, set[str]] = {}
        for item in handoff.get("objects", []):
            grouped.setdefault(item["object_id"], set()).add(digest(item["value"]))
        return {key for key, values in grouped.items() if len(values) > 1}

    old_conflicts, new_conflicts = conflicts(old), conflicts(new)
    for object_id in sorted(new_conflicts - old_conflicts):
        record("conflict-introduced", f"objects[{object_id}]",
               "contradictory values asserted for one object",
               before=None, after=object_id)
    for object_id in sorted(old_conflicts - new_conflicts):
        record("conflict-resolved", f"objects[{object_id}]",
               "contradiction no longer present", before=object_id, after=None)

    # -- external receipt ---------------------------------------------------
    old_receipt = old.get("external_receipt")
    new_receipt = new.get("external_receipt")
    if old_receipt and old_receipt.get("accepted") and (
            new_receipt is None or not new_receipt.get("accepted")):
        record("external-acceptance-lost", "external_receipt",
               f"{old_receipt['trust_root']} accepted the predecessor's world; "
               + ("the successor carries no receipt" if new_receipt is None
                  else f"{new_receipt['trust_root']} rejects the successor's"),
               before=True, after=bool(new_receipt and new_receipt.get("accepted")))

    verdict = SAFE
    for change in changes:
        if _ORDER[change["verdict"]] > _ORDER[verdict]:
            verdict = change["verdict"]

    old_world = authorities.compute(old)
    new_world = authorities.compute(new)

    return {
        "schema": RESULT_SCHEMA,
        "old_source": old_source,
        "new_source": new_source,
        "old_world_digest": old_world["world_digest"],
        "new_world_digest": new_world["world_digest"],
        "identical_world": (
            old_world["world_digest"] is not None
            and old_world["world_digest"] == new_world["world_digest"]),
        "verdict": verdict,
        "changes": changes,
    }


__all__ = ["diff", "RULES", "RESULT_SCHEMA"]
