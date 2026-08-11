"""The native validator and the published JSON Schema must agree.

``babelci`` ships a hand-written structural validator so that it has no runtime
dependencies. The JSON Schema in ``schema/`` is the normative specification for
everyone else. Two implementations of one specification is exactly the setup
that lets them drift, so this file is the check that they have not.
"""

from __future__ import annotations

import copy

import pytest

from babelci import schema as native
from babelci.lab import cases

jsonschema = pytest.importorskip(
    "jsonschema", reason="optional dev dependency; install with .[dev]")


@pytest.fixture(scope="module")
def validator():
    document = native.load_schema()
    return jsonschema.Draft202012Validator(document)


def _malformed():
    """Artifacts that must be rejected, one defect each."""
    def drop(field):
        artifact = cases.clean()
        del artifact[field]
        return artifact

    yield "missing-provenance", drop("provenance")
    yield "missing-checkpoint", drop("checkpoint")
    yield "missing-task", drop("task")
    yield "missing-producer", drop("producer")

    unknown = cases.clean()
    unknown["extra_field"] = "not in the contract"
    yield "unknown-top-level-field", unknown

    bad_digest = cases.clean()
    bad_digest["checkpoint"]["state_digest"] = "deadbeef"
    yield "unprefixed-digest", bad_digest

    short_digest = cases.clean()
    short_digest["checkpoint"]["state_digest"] = "sha256:abc"
    yield "short-digest", short_digest

    bad_binding = cases.clean()
    bad_binding["retained_constraints"][0]["binding"] = "MAYBE"
    yield "unknown-binding", bad_binding

    bad_alias = cases.clean()
    bad_alias["aliases"] = [["only-one-element"]]
    yield "malformed-alias-pair", bad_alias

    bad_object = cases.clean()
    del bad_object["objects"][0]["provenance"]
    yield "object-without-provenance", bad_object

    bad_receipt = cases.clean()
    bad_receipt["external_receipt"] = {"receipt_id": "r", "trust_root": "t",
                                       "accepted": "yes",
                                       "world_digest": "sha256:" + "0" * 64}
    yield "receipt-accepted-not-boolean", bad_receipt

    wrong_type = cases.clean()
    wrong_type["objects"] = {"not": "an array"}
    yield "objects-not-an-array", wrong_type


ALL_CASES = [(case["id"], case) for case in cases.CASES]


@pytest.mark.parametrize("case_id,case", ALL_CASES)
def test_lab_fixtures_satisfy_both_implementations(case_id, case, validator):
    artifact = cases.build(case_id)
    native_findings = native.validate(artifact)
    schema_errors = list(validator.iter_errors(artifact))
    assert not native_findings, native_findings
    assert not schema_errors, [error.message for error in schema_errors]


@pytest.mark.parametrize("name,artifact", list(_malformed()))
def test_both_implementations_reject_the_same_defects(name, artifact, validator):
    native_findings = native.validate(artifact)
    schema_errors = list(validator.iter_errors(artifact))
    assert native_findings, f"native validator accepted {name}"
    assert schema_errors, f"JSON Schema accepted {name}"


def test_schema_declares_the_version_this_build_implements():
    document = native.load_schema()
    from babelci.contract import CONTRACT_VERSION
    assert document["properties"]["babel_handoff"]["const"] == CONTRACT_VERSION


def test_native_validator_does_not_mutate_input():
    artifact = cases.clean()
    before = copy.deepcopy(artifact)
    native.validate(artifact)
    assert artifact == before
