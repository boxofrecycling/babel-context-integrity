"""The Babel handoff verifier.

Eight layers run in order. Each answers one question and reports its own
status; the layers are never averaged into a score. A layer can end in one of
three states:

``verified``        the check ran and the artifact satisfied it
``failed``          the check ran and the artifact did not satisfy it
``not established`` the artifact did not supply what the check needs

The third state matters more than it looks. An artifact with a single authority
encoding and no external receipt is not "clean" -- it is unexamined at those
layers, and saying so is the difference between an honest tool and a rubber
stamp.
"""

from __future__ import annotations

from typing import Any

from . import authorities
from .canonical import digest
from .contract import (
    ALIAS_NOT_BIJECTIVE, ALIAS_TARGET_MISSING, AUTHORITY_COMMITMENT_MISMATCH,
    AUTHORITY_DISAGREEMENT, AUTHORITY_SINGLE_ENCODING, CHECKPOINT_DOMAIN,
    CHECKPOINT_COMMITMENT_MISMATCH, CHECKPOINT_REPLAY, CONSUMER_IDENTITY_MISMATCH,
    DECISION_SUPERSEDES_MISSING, DUPLICATE_OBJECT_CONFLICT,
    EXTERNAL_RECEIPT_ABSENT, EXTERNAL_RECEIPT_REJECTED,
    EXTERNAL_RECEIPT_WORLD_MISMATCH, LAYER_AUTHORITIES, LAYER_CHECKPOINT,
    LAYER_CONFLICTS, LAYER_CONSTRAINTS, LAYER_EXTERNAL, LAYER_IDENTITY,
    LAYER_PROVENANCE, LAYER_STRUCTURE, PROVENANCE_CHAIN_BROKEN, PROVENANCE_CYCLE,
    PRODUCER_IDENTITY_MISMATCH, PROVENANCE_EDGE_DANGLING,
    PROVENANCE_ROOT_UNDECLARED,
    REQUIRED_DECISION_MISSING, REQUIRED_OBJECT_MISSING,
    RETAINED_CONSTRAINT_MISSING,
    RETAINED_CONSTRAINT_MODIFIED,
    SEVERITY_FAIL, SEVERITY_NOTE, SUMMARY_COMMITMENT_MISMATCH, SUMMARY_DOMAIN,
    TASK_IDENTITY_MISMATCH, UNRESOLVED_ISSUE_UNDECLARED,
)
from . import schema as schema_module

VERIFIED = "verified"
FAILED = "failed"
NOT_ESTABLISHED = "not established"

RESULT_SCHEMA = "babel-verify/0.1"


# ---------------------------------------------------------------------------
# Commitment recipes. These are normative: a producer in any language must
# compute them exactly this way for its artifacts to verify.
# ---------------------------------------------------------------------------

def bound_state(handoff: dict[str, Any]) -> dict[str, Any]:
    """The state a checkpoint commits to."""
    return {
        "task_id": handoff["task"]["task_id"],
        "checkpoint_id": handoff["checkpoint"]["checkpoint_id"],
        "objects": sorted(
            [item["object_id"], item["kind"], digest(item["value"])]
            for item in handoff.get("objects", [])),
        "constraints": sorted(
            [item["constraint_id"], item["binding"], digest(item["statement"])]
            for item in handoff.get("retained_constraints", []) or []),
        "decisions": sorted(
            [item["decision_id"], digest(item["choice"])]
            for item in handoff.get("decisions", []) or []),
        "unresolved": sorted(
            item["issue_id"] for item in handoff.get("unresolved", []) or []),
        "artifacts": sorted(
            [item["path"], item["digest"]]
            for item in handoff.get("artifacts", []) or []),
    }


def checkpoint_commitment(handoff: dict[str, Any]) -> str:
    return digest(bound_state(handoff), domain=CHECKPOINT_DOMAIN)


def summary_commitment(handoff: dict[str, Any], world_digest: str) -> str:
    return digest(
        {"world_digest": world_digest, "text": handoff["summary"]["text"]},
        domain=SUMMARY_DOMAIN)


# ---------------------------------------------------------------------------

class _Layers:
    def __init__(self) -> None:
        self.order: list[str] = []
        self.state: dict[str, str] = {}
        self.findings: dict[str, list[dict[str, Any]]] = {}
        self.detail: dict[str, str] = {}

    def open(self, layer: str) -> None:
        if layer not in self.state:
            self.order.append(layer)
            self.state[layer] = VERIFIED
            self.findings[layer] = []

    def fail(self, layer: str, code: str, detail: str,
             *, severity: str = SEVERITY_FAIL, **extra: Any) -> None:
        self.open(layer)
        if severity == SEVERITY_FAIL:
            self.state[layer] = FAILED
        self.findings[layer].append(
            {"code": code, "severity": severity, "detail": detail, **extra})

    def unestablished(self, layer: str, code: str, detail: str) -> None:
        self.open(layer)
        self.state[layer] = NOT_ESTABLISHED
        self.findings[layer].append(
            {"code": code, "severity": SEVERITY_NOTE, "detail": detail})

    def note(self, layer: str, text: str) -> None:
        self.open(layer)
        self.detail[layer] = text


def verify(handoff: Any, *, expectation: dict[str, Any] | None = None,
           source: str | None = None) -> dict[str, Any]:
    """Verify one handoff artifact. Performs no I/O and contacts nothing."""
    layers = _Layers()

    # -- layer 1: structure -------------------------------------------------
    layers.open(LAYER_STRUCTURE)
    structural = schema_module.validate(handoff)
    for finding in structural:
        layers.fail(LAYER_STRUCTURE, finding["code"],
                    f"{finding['where']}: {finding['detail']}",
                    where=finding["where"])
    if structural:
        # Deeper layers index fields that may not exist. Stopping here is the
        # honest outcome: we know the shape is wrong and nothing else was checked.
        return _result(handoff, layers, source, computed=None)

    layers.note(LAYER_STRUCTURE,
                f"contract {handoff['babel_handoff']}, "
                f"{len(handoff.get('objects', []))} objects")

    # -- layer 2: identity --------------------------------------------------
    layers.open(LAYER_IDENTITY)
    task_id = handoff["task"]["task_id"]
    if expectation:
        expected_task = expectation.get("task_id")
        if expected_task is not None and expected_task != task_id:
            layers.fail(LAYER_IDENTITY, TASK_IDENTITY_MISMATCH,
                        f"expected task_id {expected_task!r}, artifact declares {task_id!r}",
                        expected=expected_task, received=task_id)
        expected_producer = expectation.get("producer")
        actual_producer = handoff["producer"]["agent"]
        if expected_producer is not None and expected_producer != actual_producer:
            layers.fail(LAYER_IDENTITY, PRODUCER_IDENTITY_MISMATCH,
                        f"expected producer {expected_producer!r}, "
                        f"artifact declares {actual_producer!r}",
                        expected=expected_producer, received=actual_producer)
        expected_consumer = expectation.get("consumer")
        actual_consumer = (handoff.get("consumer") or {}).get("agent")
        if expected_consumer is not None and expected_consumer != actual_consumer:
            layers.fail(LAYER_IDENTITY, CONSUMER_IDENTITY_MISMATCH,
                        f"expected consumer {expected_consumer!r}, "
                        f"artifact declares {actual_consumer!r}",
                        expected=expected_consumer, received=actual_consumer)
    layers.note(LAYER_IDENTITY,
                f"{handoff['producer']['agent']} -> "
                f"{(handoff.get('consumer') or {}).get('agent', '(unspecified)')}")

    # -- layer 3: checkpoint ------------------------------------------------
    layers.open(LAYER_CHECKPOINT)
    declared = handoff["checkpoint"]["state_digest"]
    recomputed = checkpoint_commitment(handoff)
    if declared != recomputed:
        layers.fail(LAYER_CHECKPOINT, CHECKPOINT_COMMITMENT_MISMATCH,
                    "the checkpoint commitment does not recompute from the state "
                    "this artifact carries",
                    expected=recomputed, received=declared)
    if expectation and expectation.get("parent_checkpoint_id") is not None:
        expected_parent = expectation["parent_checkpoint_id"]
        actual_parent = handoff["checkpoint"].get("parent_checkpoint_id")
        if expected_parent != actual_parent:
            layers.fail(LAYER_CHECKPOINT, CHECKPOINT_REPLAY,
                        f"expected parent checkpoint {expected_parent!r}, "
                        f"artifact declares {actual_parent!r}",
                        expected=expected_parent, received=actual_parent)
    layers.note(LAYER_CHECKPOINT, handoff["checkpoint"]["checkpoint_id"])

    # -- layer 4: provenance ------------------------------------------------
    layers.open(LAYER_PROVENANCE)
    _check_provenance(handoff, layers)

    # -- layer 5: retained constraints --------------------------------------
    layers.open(LAYER_CONSTRAINTS)
    constraints = {item["constraint_id"]: item
                   for item in handoff.get("retained_constraints", []) or []}
    if expectation:
        for required in expectation.get("required_constraints", []) or []:
            constraint_id = required["constraint_id"]
            present = constraints.get(constraint_id)
            if present is None:
                layers.fail(LAYER_CONSTRAINTS, RETAINED_CONSTRAINT_MISSING,
                            f"constraint {constraint_id!r} was required to survive "
                            "this handoff and is absent",
                            expected=constraint_id, received=None)
                continue
            expected_commitment = required.get("statement_commitment")
            actual_commitment = digest(present["statement"])
            if expected_commitment and expected_commitment != actual_commitment:
                layers.fail(LAYER_CONSTRAINTS, RETAINED_CONSTRAINT_MODIFIED,
                            f"constraint {constraint_id!r} survived but its statement "
                            "changed",
                            expected=expected_commitment,
                            received=actual_commitment,
                            received_statement=present["statement"])
        # Compaction may have renamed object ids; a declared alias means the
        # object is still carried, just under a shorter name.
        alias_map = {name: target
                     for name, target in (handoff.get("aliases", []) or [])}
        present_objects = {alias_map.get(item["object_id"], item["object_id"])
                           for item in handoff.get("objects", [])}
        for object_id in expectation.get("required_objects", []) or []:
            if object_id not in present_objects:
                layers.fail(LAYER_CONSTRAINTS, REQUIRED_OBJECT_MISSING,
                            f"object {object_id!r} was required to survive this "
                            "handoff and is absent; the artifact is still valid "
                            "JSON and no longer carries what the task needs",
                            expected=object_id, received=None)
        # Presence only. A decision that changes its *content* under the same
        # identifier is a silent reversal, and a single artifact contains no
        # evidence that it happened -- that is `babelci diff`'s job, and the
        # `decision-reversed` lab case exists to keep the distinction honest.
        present_decisions = {item["decision_id"]
                             for item in handoff.get("decisions", []) or []}
        superseded_by = {item.get("supersedes")
                         for item in handoff.get("decisions", []) or []}
        for decision_id in expectation.get("required_decisions", []) or []:
            if decision_id in present_decisions or decision_id in superseded_by:
                continue
            layers.fail(LAYER_CONSTRAINTS, REQUIRED_DECISION_MISSING,
                        f"decision {decision_id!r} was required to survive this "
                        "handoff and is neither present nor superseded by a "
                        "decision that names it",
                        expected=decision_id, received=None)
        for issue_id in expectation.get("required_unresolved", []) or []:
            known = {item["issue_id"]
                     for item in handoff.get("unresolved", []) or []}
            resolved = {item.get("supersedes")
                        for item in handoff.get("decisions", []) or []}
            if issue_id not in known and issue_id not in resolved:
                layers.fail(LAYER_CONSTRAINTS, UNRESOLVED_ISSUE_UNDECLARED,
                            f"open issue {issue_id!r} is neither still open nor "
                            "recorded as resolved by a decision",
                            expected=issue_id, received=None)
    layers.note(LAYER_CONSTRAINTS,
                f"{sum(1 for c in constraints.values() if c['binding'] == 'MUST')} MUST, "
                f"{sum(1 for c in constraints.values() if c['binding'] == 'SHOULD')} SHOULD")

    # -- layer 6: conflicts -------------------------------------------------
    layers.open(LAYER_CONFLICTS)
    conflicts = _check_conflicts(handoff, layers, expectation)
    layers.note(LAYER_CONFLICTS, "none" if not conflicts else f"{conflicts} found")

    # -- layer 7: authority agreement ---------------------------------------
    layers.open(LAYER_AUTHORITIES)
    computed = authorities.compute(handoff)
    if not computed["agree"]:
        left, right = computed["encodings"]
        layers.fail(LAYER_AUTHORITIES, AUTHORITY_DISAGREEMENT,
                    "the two independent encodings of this artifact do not describe "
                    "the same world; no vote is taken",
                    expected=f"{left['encoding']} -> {left['world_digest']}",
                    received=f"{right['encoding']} -> {right['world_digest']}")
    world_digest = computed["world_digest"]

    declared_authorities = handoff.get("authorities", []) or []
    if world_digest is not None:
        for entry in declared_authorities:
            if entry["world_digest"] != world_digest:
                layers.fail(LAYER_AUTHORITIES, AUTHORITY_COMMITMENT_MISMATCH,
                            f"declared authority {entry['authority_id']!r} commits to a "
                            "world this artifact does not encode",
                            expected=world_digest, received=entry["world_digest"])
    # The verifier's own two encodings are genuinely independent of each other,
    # so a passing check here is a real result. It is a weaker result than a
    # producer computing the world with its own encoder and committing to it,
    # and the note says so rather than letting green imply the stronger claim.
    distinct = {entry["encoding"] for entry in declared_authorities}
    if not distinct and layers.state[LAYER_AUTHORITIES] == VERIFIED:
        layers.fail(LAYER_AUTHORITIES, AUTHORITY_SINGLE_ENCODING,
                    "this verifier's two encodings agree; the producer declared no "
                    "independently computed commitment to compare against",
                    severity=SEVERITY_NOTE)
    if layers.state[LAYER_AUTHORITIES] == VERIFIED:
        layers.note(LAYER_AUTHORITIES,
                    f"{len(distinct) + 2} encodings agree")

    # summary commitment binds prose to the structured world -- checked here
    # because it needs the world digest.
    if "summary" in handoff and world_digest is not None:
        expected_summary = summary_commitment(handoff, world_digest)
        if handoff["summary"]["commitment"] != expected_summary:
            layers.fail(LAYER_CONSTRAINTS, SUMMARY_COMMITMENT_MISMATCH,
                        "the summary prose is not bound to the world this artifact "
                        "encodes; the text or the state changed after commitment",
                        expected=expected_summary,
                        received=handoff["summary"]["commitment"])

    # -- layer 8: external truth --------------------------------------------
    layers.open(LAYER_EXTERNAL)
    receipt = handoff.get("external_receipt")
    if receipt is None:
        layers.unestablished(
            LAYER_EXTERNAL, EXTERNAL_RECEIPT_ABSENT,
            "no out-of-band receipt was supplied; everything above is internal "
            "consistency and cannot distinguish a true world from a coherent "
            "false one")
    else:
        if world_digest is not None and receipt["world_digest"] != world_digest:
            layers.fail(LAYER_EXTERNAL, EXTERNAL_RECEIPT_WORLD_MISMATCH,
                        "the external receipt was issued against a different world "
                        "than this artifact encodes",
                        expected=world_digest, received=receipt["world_digest"])
        elif not receipt["accepted"]:
            # The issuer's findings are the useful content, so they are carried
            # as a list and rendered as one line each rather than flattened
            # into a sentence that runs off the side of the terminal.
            layers.fail(LAYER_EXTERNAL, EXTERNAL_RECEIPT_REJECTED,
                        f"{receipt['trust_root']} rejected this world",
                        received=list(receipt.get("findings", [])))
        else:
            layers.note(LAYER_EXTERNAL, f"accepted by {receipt['trust_root']}")

    return _result(handoff, layers, source, computed=computed)


# ---------------------------------------------------------------------------

def _check_provenance(handoff: dict[str, Any], layers: _Layers) -> None:
    """Check that every asserted object traces to the declared authority root.

    Provenance nodes are opaque source labels -- ``ci/run-9981``, ``query/db``,
    a commit id. They are not object ids. An object names one source label; the
    edge list says how that label reaches the root.
    """
    provenance = handoff["provenance"]
    root = provenance["authority_root"]
    edges = [(edge[0], edge[1]) for edge in provenance["edges"]]

    aliases = handoff.get("aliases", []) or []
    alias_names = [pair[0] for pair in aliases]
    alias_targets = [pair[1] for pair in aliases]
    object_ids = {item["object_id"] for item in handoff.get("objects", [])}

    # Two names collapsing onto one object is a bijection failure: a reference
    # that used to be unambiguous no longer is.
    #
    # One name bound to two objects is deliberately NOT checked here. That case
    # is what the authority-agreement layer exists to catch: a dict-based reader
    # silently keeps the last binding and never notices, while a join-based
    # reader keeps both. Catching it here would hide the demonstration that a
    # single implementation cannot see its own blind spot.
    duplicated_targets = sorted(
        {target for target in alias_targets if alias_targets.count(target) > 1})
    if duplicated_targets:
        layers.fail(LAYER_PROVENANCE, ALIAS_NOT_BIJECTIVE,
                    "the alias table is not injective, so two different names "
                    "collapse onto one object: " + ", ".join(duplicated_targets),
                    received=duplicated_targets)

    # An alias may rename any identifier the artifact uses: an object id or a
    # provenance source label. What it may not do is name something that is not
    # in the artifact at all.
    edge_nodes = {node for edge in edges for node in edge}
    nameable = object_ids | edge_nodes | {root}
    for name, target in aliases:
        if target not in nameable:
            layers.fail(LAYER_PROVENANCE, ALIAS_TARGET_MISSING,
                        f"alias {name!r} points at {target!r}, which is not an "
                        "object, a provenance source or the authority root in "
                        "this handoff",
                        expected=target, received=None)

    parents: dict[str, set[str]] = {}
    for source_node, target_node in edges:
        parents.setdefault(source_node, set()).add(target_node)

    # Reachability follows the same one-hop, last-binding-wins resolution that
    # authority A uses. When a name is bound more than once the two authority
    # encodings disagree, and that -- not a silently chosen winner here -- is
    # the reported finding.
    alias_map = {name: target for name, target in aliases}

    if edges and not any(target == root for _, target in edges):
        layers.fail(LAYER_PROVENANCE, PROVENANCE_ROOT_UNDECLARED,
                    f"authority root {root!r} is never reached by any provenance "
                    "edge, so nothing in this handoff is grounded",
                    expected=root, received=None)

    # An edge whose target neither is the root nor has an onward edge leaves the
    # chain hanging in mid-air.
    for source_node, target_node in sorted(set(edges)):
        if target_node != root and target_node not in parents:
            layers.fail(LAYER_PROVENANCE, PROVENANCE_EDGE_DANGLING,
                        f"provenance edge {source_node!r} -> {target_node!r} ends "
                        f"at a node with no route onward to {root!r}",
                        expected=root, received=target_node)

    for item in sorted(handoff.get("objects", []),
                       key=lambda row: row["object_id"]):
        origin = item["provenance"]
        node = alias_map.get(origin, origin)
        seen: set[str] = set()
        reached_root = False
        cycled = False
        while True:
            node = alias_map.get(node, node)
            if node == root:
                reached_root = True
                break
            if node in seen:
                cycled = True
                break
            seen.add(node)
            nexts = parents.get(node)
            if not nexts:
                break
            node = sorted(nexts)[0]
        if cycled:
            layers.fail(LAYER_PROVENANCE, PROVENANCE_CYCLE,
                        f"provenance for object {item['object_id']!r} cycles "
                        f"through {node!r} and never reaches the root",
                        received=node)
        elif not reached_root:
            layers.fail(LAYER_PROVENANCE, PROVENANCE_CHAIN_BROKEN,
                        f"object {item['object_id']!r} claims provenance "
                        f"{origin!r}, which does not reach the authority root "
                        f"{root!r}",
                        expected=root, received=origin)

    if layers.state[LAYER_PROVENANCE] == VERIFIED:
        layers.note(LAYER_PROVENANCE,
                    f"{len(object_ids)} objects to {root}")


def _check_conflicts(handoff: dict[str, Any], layers: _Layers,
                     expectation: dict[str, Any] | None) -> int:
    found = 0

    by_id: dict[str, list[dict[str, Any]]] = {}
    for item in handoff.get("objects", []):
        by_id.setdefault(item["object_id"], []).append(item)

    for object_id, items in sorted(by_id.items()):
        commitments = {digest(item["value"]) for item in items}
        if len(commitments) <= 1:
            continue  # identical restatements are not a conflict
        resolved = any(item.get("supersedes") for item in items)
        if not resolved:
            found += 1
            layers.fail(LAYER_CONFLICTS, DUPLICATE_OBJECT_CONFLICT,
                        f"object {object_id!r} is asserted {len(items)} times with "
                        "different values and no declared resolution; equal-rank "
                        "conflicts fail closed rather than picking one",
                        received=sorted(commitments))

    # A decision that resolves an open issue removes that issue from
    # `unresolved`, so the target of `supersedes` is routinely absent from the
    # artifact that supersedes it. Checking it against this artifact alone would
    # therefore punish correct behaviour. The check runs only when an
    # expectation supplies the predecessor's identifiers, which is the only
    # place a dangling reference can actually be established.
    if expectation is None:
        return found

    known = (
        {item["decision_id"] for item in handoff.get("decisions", []) or []}
        | {issue["issue_id"] for issue in handoff.get("unresolved", []) or []}
        | set(expectation.get("required_unresolved", []) or [])
        | set(expectation.get("required_decisions", []) or [])
    )
    for item in handoff.get("decisions", []) or []:
        target = item.get("supersedes")
        if target and target not in known:
            found += 1
            layers.fail(LAYER_CONFLICTS, DECISION_SUPERSEDES_MISSING,
                        f"decision {item['decision_id']!r} supersedes {target!r}, "
                        "which neither this handoff nor the expectation mentions",
                        expected=target, received=None)
    return found


def _result(handoff: Any, layers: _Layers, source: str | None,
            computed: dict[str, Any] | None) -> dict[str, Any]:
    failed = any(state == FAILED for state in layers.state.values())
    all_findings = [
        dict(finding, layer=layer)
        for layer in layers.order
        for finding in layers.findings[layer]
    ]
    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "source": source,
        "handoff_id": handoff.get("handoff_id") if isinstance(handoff, dict) else None,
        "task_id": (handoff.get("task", {}) or {}).get("task_id")
        if isinstance(handoff, dict) else None,
        "verdict": "FAIL" if failed else "PASS",
        "layers": [
            {
                "layer": layer,
                "status": layers.state[layer],
                "detail": layers.detail.get(layer),
                "findings": layers.findings[layer],
            }
            for layer in layers.order
        ],
        "findings": all_findings,
    }
    if computed is not None:
        result["computed"] = {
            "world_digest": computed["world_digest"],
            "encodings": computed["encodings"],
        }
    return result


__all__ = [
    "verify", "bound_state", "checkpoint_commitment", "summary_commitment",
    "VERIFIED", "FAILED", "NOT_ESTABLISHED", "RESULT_SCHEMA",
]
