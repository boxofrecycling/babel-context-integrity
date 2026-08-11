"""Structural validation of a handoff artifact.

The published JSON Schema in ``schema/babel-handoff-0.1.schema.json`` is the
normative specification for other tooling. This module is a second, native
implementation of the same shape so that ``babelci`` has no runtime
dependencies and stays usable in a locked-down CI container.

``tests/test_schema_parity.py`` asserts that the two implementations reach the
same accept/reject decision on every example and lab fixture whenever the
optional ``jsonschema`` package is installed. If they ever diverge, that test
fails rather than one silently winning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .canonical import is_digest
from .contract import (
    CONTRACT_VERSION,
    CONTRACT_VERSION_MISMATCH,
    MALFORMED_DIGEST,
    SCHEMA_VIOLATION,
)

SCHEMA_FILENAME = "babel-handoff-0.1.schema.json"


def schema_path() -> Path:
    """Locate the packaged copy of the normative JSON Schema."""
    packaged = Path(__file__).resolve().parent / "_schema" / SCHEMA_FILENAME
    if packaged.exists():
        return packaged
    # Running from a source checkout rather than an installed wheel.
    return Path(__file__).resolve().parents[2] / "schema" / SCHEMA_FILENAME


def load_schema() -> dict[str, Any]:
    return json.loads(schema_path().read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------

_PARTY_KEYS = {"agent", "role", "run_id"}
_OBJECT_REQUIRED = ("object_id", "kind", "value", "provenance")
_OBJECT_KEYS = {"object_id", "kind", "value", "required", "provenance", "supersedes"}
_CONSTRAINT_KEYS = {"constraint_id", "statement", "binding", "provenance"}
_DECISION_KEYS = {"decision_id", "choice", "rationale", "supersedes", "provenance"}
_UNRESOLVED_KEYS = {"issue_id", "statement", "blocking"}
_ARTIFACT_KEYS = {"path", "digest", "role"}
_AUTHORITY_KEYS = {"authority_id", "encoding", "world_digest"}
_RECEIPT_KEYS = {"receipt_id", "trust_root", "accepted", "world_digest", "findings"}

_TOP_KEYS = {
    "babel_handoff", "handoff_id", "task", "producer", "consumer", "checkpoint",
    "objects", "retained_constraints", "decisions", "unresolved", "artifacts",
    "provenance", "aliases", "summary", "authorities", "external_receipt",
}
_TOP_REQUIRED = ("babel_handoff", "handoff_id", "task", "producer",
                 "checkpoint", "objects", "provenance")


class _Collector:
    def __init__(self) -> None:
        self.findings: list[dict[str, str]] = []

    def add(self, code: str, where: str, detail: str) -> None:
        self.findings.append({"code": code, "where": where, "detail": detail})

    def require_keys(self, value: Any, required: tuple[str, ...],
                     allowed: set[str], where: str) -> bool:
        if not isinstance(value, dict):
            self.add(SCHEMA_VIOLATION, where, "expected an object")
            return False
        ok = True
        for key in required:
            if key not in value:
                self.add(SCHEMA_VIOLATION, where, f"missing required field {key!r}")
                ok = False
        for key in value:
            if key not in allowed:
                self.add(SCHEMA_VIOLATION, where, f"unknown field {key!r}")
                ok = False
        return ok

    def text(self, value: Any, where: str, *, allow_empty: bool = False) -> None:
        if not isinstance(value, str):
            self.add(SCHEMA_VIOLATION, where, "expected a string")
        elif not value and not allow_empty:
            self.add(SCHEMA_VIOLATION, where, "must not be empty")

    def commitment(self, value: Any, where: str) -> None:
        if not is_digest(value):
            self.add(MALFORMED_DIGEST, where,
                     "expected a 'sha256:' followed by 64 lowercase hex characters")

    def pair_list(self, value: Any, where: str) -> None:
        if not isinstance(value, list):
            self.add(SCHEMA_VIOLATION, where, "expected an array")
            return
        for index, entry in enumerate(value):
            spot = f"{where}[{index}]"
            if (not isinstance(entry, list) or len(entry) != 2
                    or not all(isinstance(part, str) and part for part in entry)):
                self.add(SCHEMA_VIOLATION, spot,
                         "expected a two-element array of non-empty strings")


def validate(handoff: Any) -> list[dict[str, str]]:
    """Return structural findings. An empty list means the shape is valid."""
    collector = _Collector()

    if not isinstance(handoff, dict):
        collector.add(SCHEMA_VIOLATION, "$", "top level must be a JSON object")
        return collector.findings

    declared = handoff.get("babel_handoff")
    if declared != CONTRACT_VERSION:
        collector.add(
            CONTRACT_VERSION_MISMATCH, "$.babel_handoff",
            f"this build implements contract {CONTRACT_VERSION!r}; "
            f"artifact declares {declared!r}")
        # Shape checks below assume v0.1 field names, so stop here.
        return collector.findings

    collector.require_keys(handoff, _TOP_REQUIRED, _TOP_KEYS, "$")

    collector.text(handoff.get("handoff_id"), "$.handoff_id")

    task = handoff.get("task")
    if collector.require_keys(task, ("task_id",),
                              {"task_id", "title", "family"}, "$.task"):
        collector.text(task.get("task_id"), "$.task.task_id")

    for party in ("producer", "consumer"):
        if party in handoff:
            value = handoff[party]
            if collector.require_keys(value, ("agent",), _PARTY_KEYS, f"$.{party}"):
                collector.text(value.get("agent"), f"$.{party}.agent")

    checkpoint = handoff.get("checkpoint")
    if collector.require_keys(
            checkpoint, ("checkpoint_id", "state_digest"),
            {"checkpoint_id", "state_digest", "parent_checkpoint_id"},
            "$.checkpoint"):
        collector.text(checkpoint.get("checkpoint_id"), "$.checkpoint.checkpoint_id")
        collector.commitment(checkpoint.get("state_digest"),
                             "$.checkpoint.state_digest")

    objects = handoff.get("objects")
    if not isinstance(objects, list):
        collector.add(SCHEMA_VIOLATION, "$.objects", "expected an array")
    else:
        for index, item in enumerate(objects):
            where = f"$.objects[{index}]"
            if collector.require_keys(item, _OBJECT_REQUIRED, _OBJECT_KEYS, where):
                collector.text(item.get("object_id"), f"{where}.object_id")
                collector.text(item.get("kind"), f"{where}.kind")
                collector.text(item.get("provenance"), f"{where}.provenance")
                if "required" in item and not isinstance(item["required"], bool):
                    collector.add(SCHEMA_VIOLATION, f"{where}.required",
                                  "expected a boolean")

    for index, item in enumerate(handoff.get("retained_constraints", []) or []):
        where = f"$.retained_constraints[{index}]"
        if collector.require_keys(
                item, ("constraint_id", "statement", "binding"),
                _CONSTRAINT_KEYS, where):
            collector.text(item.get("constraint_id"), f"{where}.constraint_id")
            collector.text(item.get("statement"), f"{where}.statement")
            if item.get("binding") not in ("MUST", "SHOULD"):
                collector.add(SCHEMA_VIOLATION, f"{where}.binding",
                              "expected 'MUST' or 'SHOULD'")

    for index, item in enumerate(handoff.get("decisions", []) or []):
        where = f"$.decisions[{index}]"
        if collector.require_keys(item, ("decision_id", "choice"),
                                  _DECISION_KEYS, where):
            collector.text(item.get("decision_id"), f"{where}.decision_id")
            collector.text(item.get("choice"), f"{where}.choice")

    for index, item in enumerate(handoff.get("unresolved", []) or []):
        where = f"$.unresolved[{index}]"
        if collector.require_keys(item, ("issue_id", "statement"),
                                  _UNRESOLVED_KEYS, where):
            collector.text(item.get("issue_id"), f"{where}.issue_id")
            collector.text(item.get("statement"), f"{where}.statement")

    for index, item in enumerate(handoff.get("artifacts", []) or []):
        where = f"$.artifacts[{index}]"
        if collector.require_keys(item, ("path", "digest"), _ARTIFACT_KEYS, where):
            collector.text(item.get("path"), f"{where}.path")
            collector.commitment(item.get("digest"), f"{where}.digest")

    provenance = handoff.get("provenance")
    if collector.require_keys(provenance, ("authority_root", "edges"),
                              {"authority_root", "edges"}, "$.provenance"):
        collector.text(provenance.get("authority_root"),
                       "$.provenance.authority_root")
        collector.pair_list(provenance.get("edges"), "$.provenance.edges")

    if "aliases" in handoff:
        collector.pair_list(handoff["aliases"], "$.aliases")

    if "summary" in handoff:
        summary = handoff["summary"]
        if collector.require_keys(summary, ("text", "commitment"),
                                  {"text", "commitment"}, "$.summary"):
            collector.text(summary.get("text"), "$.summary.text", allow_empty=True)
            collector.commitment(summary.get("commitment"), "$.summary.commitment")

    for index, item in enumerate(handoff.get("authorities", []) or []):
        where = f"$.authorities[{index}]"
        if collector.require_keys(
                item, ("authority_id", "encoding", "world_digest"),
                _AUTHORITY_KEYS, where):
            collector.text(item.get("authority_id"), f"{where}.authority_id")
            collector.text(item.get("encoding"), f"{where}.encoding")
            collector.commitment(item.get("world_digest"), f"{where}.world_digest")

    if "external_receipt" in handoff:
        receipt = handoff["external_receipt"]
        if collector.require_keys(
                receipt, ("receipt_id", "trust_root", "accepted", "world_digest"),
                _RECEIPT_KEYS, "$.external_receipt"):
            collector.text(receipt.get("receipt_id"), "$.external_receipt.receipt_id")
            collector.text(receipt.get("trust_root"), "$.external_receipt.trust_root")
            if not isinstance(receipt.get("accepted"), bool):
                collector.add(SCHEMA_VIOLATION, "$.external_receipt.accepted",
                              "expected a boolean")
            collector.commitment(receipt.get("world_digest"),
                                 "$.external_receipt.world_digest")

    return collector.findings


__all__ = ["validate", "load_schema", "schema_path", "SCHEMA_FILENAME"]
