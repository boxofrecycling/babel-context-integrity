"""Two independent encodings of the same handoff, and their agreement.

The point of this module is implementation diversity, not redundancy. Both
encoders read the same artifact and both must arrive at the same *semantic
world* -- the meaning of the handoff once aliases are resolved, declared
duplicates collapsed and ordering normalised.

Authority A walks the artifact as a nested document, the way a reader would.
Authority B first shreds the artifact into flat relation tuples and then
reconstitutes the world by joining them, the way a database would. The two
paths share this module's world schema and nothing else: A never calls B's
helpers and B never calls A's.

Agreement between them is evidence that the artifact encodes one coherent
world. It is *not* evidence that the world is the one that actually happened.
Two encodings built from the same artifact can agree perfectly about a story
that never occurred; that is what the ``common-mode`` lab case demonstrates
and what the external-truth layer exists to address.
"""

from __future__ import annotations

from typing import Any

from .canonical import digest
from .contract import WORLD_DOMAIN

WORLD_SCHEMA = "BABEL_PUBLIC_HANDOFF_WORLD/0.1"

ENCODING_A = "babel/authority-a/document-tree/0.1"
ENCODING_B = "babel/authority-b/relation-join/0.1"


# ---------------------------------------------------------------------------
# Authority A -- nested document walk.
# ---------------------------------------------------------------------------

def _a_alias_map(handoff: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pair in handoff.get("aliases", []):
        mapping[pair[0]] = pair[1]
    return mapping


def _a_resolve(name: str, aliases: dict[str, str]) -> str:
    # One hop only. Chained aliases are not part of v0.1; an alias whose target
    # is itself an alias resolves to that alias's name, which will then fail to
    # match any object id and surface as a dangling reference.
    return aliases.get(name, name)


def encode_a(handoff: dict[str, Any]) -> dict[str, Any]:
    """Project the artifact into the public world by reading it as a document."""
    aliases = _a_alias_map(handoff)

    objects = []
    for item in handoff.get("objects", []):
        objects.append({
            "object_id": _a_resolve(item["object_id"], aliases),
            "kind": item["kind"],
            "value_commitment": digest(item["value"]),
            "required": bool(item.get("required", False)),
            "provenance": _a_resolve(item["provenance"], aliases),
        })
    objects.sort(key=lambda row: (row["object_id"], row["kind"], row["value_commitment"]))

    constraints = []
    for item in handoff.get("retained_constraints", []):
        constraints.append({
            "constraint_id": item["constraint_id"],
            "binding": item["binding"],
            "statement_commitment": digest(item["statement"]),
        })
    constraints.sort(key=lambda row: (row["constraint_id"], row["binding"]))

    decisions = []
    for item in handoff.get("decisions", []):
        decisions.append({
            "decision_id": item["decision_id"],
            "choice_commitment": digest(item["choice"]),
            "supersedes": item.get("supersedes"),
        })
    decisions.sort(key=lambda row: row["decision_id"])

    unresolved = sorted(
        item["issue_id"] for item in handoff.get("unresolved", []))

    artifacts = sorted(
        (item["path"], item["digest"]) for item in handoff.get("artifacts", []))

    edges = sorted(
        (_a_resolve(edge[0], aliases), _a_resolve(edge[1], aliases))
        for edge in handoff["provenance"]["edges"])

    return _world(
        task=handoff["task"],
        checkpoint_id=handoff["checkpoint"]["checkpoint_id"],
        authority_root=handoff["provenance"]["authority_root"],
        objects=objects,
        constraints=constraints,
        decisions=decisions,
        unresolved=unresolved,
        artifacts=[list(row) for row in artifacts],
        edges=[list(row) for row in edges],
    )


# ---------------------------------------------------------------------------
# Authority B -- shred to relations, then join.
# ---------------------------------------------------------------------------

def _b_relations(handoff: dict[str, Any]) -> list[tuple[str, ...]]:
    """Flatten the whole artifact into sorted, typed relation tuples."""
    rows: list[tuple[str, ...]] = []

    for pair in handoff.get("aliases", []):
        rows.append(("alias", pair[0], pair[1]))

    for item in handoff.get("objects", []):
        rows.append((
            "object",
            item["object_id"],
            item["kind"],
            digest(item["value"]),
            "1" if item.get("required", False) else "0",
            item["provenance"],
        ))

    for item in handoff.get("retained_constraints", []):
        rows.append((
            "constraint",
            item["constraint_id"],
            item["binding"],
            digest(item["statement"]),
        ))

    for item in handoff.get("decisions", []):
        rows.append((
            "decision",
            item["decision_id"],
            digest(item["choice"]),
            item.get("supersedes") or "",
        ))

    for item in handoff.get("unresolved", []):
        rows.append(("unresolved", item["issue_id"]))

    for item in handoff.get("artifacts", []):
        rows.append(("artifact", item["path"], item["digest"]))

    for edge in handoff["provenance"]["edges"]:
        rows.append(("edge", edge[0], edge[1]))

    rows.sort()
    return rows


def encode_b(handoff: dict[str, Any]) -> dict[str, Any]:
    """Project the artifact into the public world by joining flat relations."""
    rows = _b_relations(handoff)

    # The alias relation is applied as a join over every name-bearing column.
    # Where A does a dict lookup with last-write-wins, B collects every match,
    # so a non-bijective alias table makes B produce a different world.
    alias_targets: dict[str, list[str]] = {}
    for row in rows:
        if row[0] == "alias":
            alias_targets.setdefault(row[1], []).append(row[2])

    def join(name: str) -> str:
        targets = alias_targets.get(name)
        if not targets:
            return name
        if len(targets) == 1:
            return targets[0]
        return "|".join(sorted(targets))

    objects = sorted(
        (
            {
                "object_id": join(row[1]),
                "kind": row[2],
                "value_commitment": row[3],
                "required": row[4] == "1",
                "provenance": join(row[5]),
            }
            for row in rows if row[0] == "object"
        ),
        key=lambda item: (item["object_id"], item["kind"], item["value_commitment"]),
    )

    constraints = sorted(
        (
            {
                "constraint_id": row[1],
                "binding": row[2],
                "statement_commitment": row[3],
            }
            for row in rows if row[0] == "constraint"
        ),
        key=lambda item: (item["constraint_id"], item["binding"]),
    )

    decisions = sorted(
        (
            {
                "decision_id": row[1],
                "choice_commitment": row[2],
                "supersedes": row[3] or None,
            }
            for row in rows if row[0] == "decision"
        ),
        key=lambda item: item["decision_id"],
    )

    unresolved = sorted(row[1] for row in rows if row[0] == "unresolved")
    artifacts = sorted([row[1], row[2]] for row in rows if row[0] == "artifact")
    edges = sorted([join(row[1]), join(row[2])] for row in rows if row[0] == "edge")

    return _world(
        task=handoff["task"],
        checkpoint_id=handoff["checkpoint"]["checkpoint_id"],
        authority_root=handoff["provenance"]["authority_root"],
        objects=objects,
        constraints=constraints,
        decisions=decisions,
        unresolved=unresolved,
        artifacts=artifacts,
        edges=edges,
    )


# ---------------------------------------------------------------------------
# Shared world shape.
# ---------------------------------------------------------------------------

def _world(*, task, checkpoint_id, authority_root, objects, constraints,
           decisions, unresolved, artifacts, edges) -> dict[str, Any]:
    return {
        "schema": WORLD_SCHEMA,
        "task_id": task["task_id"],
        "task_family": task.get("family"),
        "checkpoint_id": checkpoint_id,
        "authority_root": authority_root,
        "objects": objects,
        "constraints": constraints,
        "decisions": decisions,
        "unresolved": unresolved,
        "artifacts": artifacts,
        "provenance_edges": edges,
    }


def world_digest(world: dict[str, Any]) -> str:
    return digest(world, domain=WORLD_DOMAIN)


def compute(handoff: dict[str, Any]) -> dict[str, Any]:
    """Run both encoders and report agreement without resolving it by vote.

    When the two encodings disagree the result records both digests. Nothing in
    this package picks a winner: a disagreement is a finding, not a tie to be
    broken.
    """
    world_a = encode_a(handoff)
    world_b = encode_b(handoff)
    digest_a = world_digest(world_a)
    digest_b = world_digest(world_b)
    return {
        "encodings": [
            {"authority_id": "babelci.authority_a", "encoding": ENCODING_A,
             "world_digest": digest_a},
            {"authority_id": "babelci.authority_b", "encoding": ENCODING_B,
             "world_digest": digest_b},
        ],
        "agree": digest_a == digest_b,
        "world": world_a if digest_a == digest_b else None,
        "world_digest": digest_a if digest_a == digest_b else None,
    }


__all__ = [
    "WORLD_SCHEMA", "ENCODING_A", "ENCODING_B",
    "encode_a", "encode_b", "world_digest", "compute",
]
