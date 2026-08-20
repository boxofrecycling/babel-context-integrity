"""Carry a handoff forward into its successor.

``seal`` fills in the commitments a draft is missing. ``carry`` produces the
draft: it takes the artifact a session is finishing with and returns the one
its successor starts from, so that continuity is the default and losing
something takes a deliberate act rather than a forgetful one. A producer that
retypes its constraints every session will eventually retype them wrong.

The interesting part is what it refuses to carry.

An artifact's ``authorities`` are commitments its producer computed over its
own world. The successor describes a different world, and the successor's
producer has computed nothing yet. Carrying the predecessor's entry forward
would attach a commitment nobody made to a world nobody encoded -- inventing
authority data, which is the one thing a continuity tool must never do. It is
withheld, and the successor's authority layer reports ``not established``
until its own producer declares something.

An ``external_receipt`` is an acceptance issued against the predecessor's
world by something outside it. Carried forward it would launder an old
acceptance onto new work.

A ``summary`` is prose asserting what is true *now*. Carried into a new
checkpoint and resealed it becomes a fresh commitment to a stale claim, which
is the drift Babel exists to catch. Pass ``--summary`` to write a new one; an
artifact with no summary makes no prose claim, which is honest and legal.

Everything else -- the task, the provenance graph and its authority root, the
retained constraints, the decisions, the open issues, the objects and the
aliases -- carries verbatim. ``carry`` takes no view on what project facts
should say and does not refresh them. An authority root of ``repo`` stays
``repo``: upgrading it to something more precise would assert a grounding its
producer never claimed.
"""

from __future__ import annotations

import copy
from typing import Any

from .seal import PLACEHOLDER

#: Carried verbatim. Continuity is the default for everything the predecessor
#: asserted about the work rather than about its own run.
CARRIED = (
    "babel_handoff",
    "task",
    "provenance",
    "objects",
    "retained_constraints",
    "decisions",
    "unresolved",
    "artifacts",
    "aliases",
)

#: Withheld, each for a reason in the module docstring. Not an oversight.
WITHHELD = ("authorities", "external_receipt", "summary")


def carry(predecessor: dict[str, Any], *, checkpoint_id: str,
          handoff_id: str | None = None, producer: str | None = None,
          consumer: str | None = None, summary: str | None = None,
          ) -> dict[str, Any]:
    """Return the successor draft of ``predecessor``.

    The result is a *draft*: its checkpoint commitment is a placeholder, so it
    is meant to be piped through ``seal``. Performs no I/O and contacts
    nothing.
    """
    if not isinstance(predecessor, dict):
        raise ValueError("a handoff artifact is a JSON object")
    if not checkpoint_id:
        raise ValueError("a successor must name its own checkpoint")

    successor: dict[str, Any] = {
        field: copy.deepcopy(predecessor[field])
        for field in CARRIED if field in predecessor
    }
    successor.setdefault("babel_handoff", "0.1")
    successor.setdefault("objects", [])
    successor["handoff_id"] = handoff_id or checkpoint_id

    checkpoint: dict[str, Any] = {
        "checkpoint_id": checkpoint_id,
        "state_digest": PLACEHOLDER,
    }
    parent = (predecessor.get("checkpoint") or {}).get("checkpoint_id")
    if parent is not None:
        checkpoint["parent_checkpoint_id"] = parent
    successor["checkpoint"] = checkpoint

    inherited = predecessor.get("consumer") or {}
    if producer:
        successor["producer"] = {"agent": producer}
    elif inherited.get("agent"):
        # The predecessor named who it was handing to, and that party is now
        # doing the work. Its run_id is not carried: that identified the
        # predecessor's run, and reusing it would name a run that never
        # happened.
        successor["producer"] = {key: value for key, value in inherited.items()
                                 if key != "run_id"}
    else:
        raise ValueError(
            "the predecessor names no consumer, so there is nobody for the "
            "work to pass to; name the successor's producer explicitly")

    if consumer:
        successor["consumer"] = {"agent": consumer}
    if summary is not None:
        successor["summary"] = {"text": summary, "commitment": PLACEHOLDER}
    return successor


__all__ = ["carry", "CARRIED", "WITHHELD"]
