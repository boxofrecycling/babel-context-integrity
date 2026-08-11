"""Verifier behaviour, layer by layer."""

from __future__ import annotations

import copy

import pytest

from babelci import contract
from babelci.lab import cases
from babelci.verify import FAILED, NOT_ESTABLISHED, VERIFIED, verify


def layer(result, name):
    return next(entry for entry in result["layers"] if entry["layer"] == name)


def codes(result):
    return {finding["code"] for finding in result["findings"]
            if finding["severity"] == contract.SEVERITY_FAIL}


def test_clean_handoff_passes():
    result = verify(cases.clean(), expectation=cases.expectation())
    assert result["verdict"] == "PASS"
    assert not codes(result)


def test_clean_handoff_does_not_claim_external_truth():
    """The absence of an outside check is reported, not treated as success."""
    result = verify(cases.clean(), expectation=cases.expectation())
    assert layer(result, contract.LAYER_EXTERNAL)["status"] == NOT_ESTABLISHED
    assert contract.EXTERNAL_RECEIPT_ABSENT in {
        finding["code"] for finding in result["findings"]}


def test_every_layer_reports_a_status():
    result = verify(cases.clean(), expectation=cases.expectation())
    assert [entry["layer"] for entry in result["layers"]] == list(contract.LAYERS)


def test_structural_failure_stops_before_deeper_layers():
    """A malformed artifact must not produce green ticks for unrun checks."""
    broken = cases.clean()
    del broken["provenance"]
    result = verify(broken)
    assert result["verdict"] == "FAIL"
    assert [entry["layer"] for entry in result["layers"]] == [
        contract.LAYER_STRUCTURE]


def test_unknown_contract_version_is_refused_not_guessed():
    artifact = cases.clean()
    artifact["babel_handoff"] = "0.2"
    result = verify(artifact)
    assert contract.CONTRACT_VERSION_MISMATCH in codes(result)


@pytest.mark.parametrize("case_id,expected_layer,expected_code", [
    ("constraint-dropped", contract.LAYER_CONSTRAINTS,
     contract.RETAINED_CONSTRAINT_MISSING),
    ("constraint-softened", contract.LAYER_CONSTRAINTS,
     contract.RETAINED_CONSTRAINT_MODIFIED),
    ("compression-loss", contract.LAYER_CONSTRAINTS,
     contract.REQUIRED_OBJECT_MISSING),
    ("summary-drift", contract.LAYER_CONSTRAINTS,
     contract.SUMMARY_COMMITMENT_MISMATCH),
    ("checkpoint-mismatch", contract.LAYER_CHECKPOINT,
     contract.CHECKPOINT_COMMITMENT_MISMATCH),
    ("stale-replay", contract.LAYER_CHECKPOINT, contract.CHECKPOINT_REPLAY),
    ("provenance-break", contract.LAYER_PROVENANCE,
     contract.PROVENANCE_CHAIN_BROKEN),
    ("alias-collapse", contract.LAYER_PROVENANCE, contract.ALIAS_NOT_BIJECTIVE),
    ("duplicate-conflict", contract.LAYER_CONFLICTS,
     contract.DUPLICATE_OBJECT_CONFLICT),
    ("authority-disagreement", contract.LAYER_AUTHORITIES,
     contract.AUTHORITY_DISAGREEMENT),
    ("common-mode", contract.LAYER_EXTERNAL, contract.EXTERNAL_RECEIPT_REJECTED),
])
def test_failure_class_is_caught_at_its_layer(case_id, expected_layer,
                                              expected_code):
    expectation = cases.expectation()
    case = cases.CASES_BY_ID[case_id]
    if case.get("needs_expectation"):
        expectation = {**expectation, **case["needs_expectation"]}
    result = verify(cases.build(case_id), expectation=expectation)
    assert result["verdict"] == "FAIL"
    assert layer(result, expected_layer)["status"] == FAILED
    assert expected_code in codes(result)


def test_common_mode_passes_every_layer_except_external():
    """The headline claim, asserted rather than narrated."""
    result = verify(cases.build("common-mode"), expectation=cases.expectation())
    for entry in result["layers"]:
        if entry["layer"] == contract.LAYER_EXTERNAL:
            assert entry["status"] == FAILED
        else:
            assert entry["status"] == VERIFIED, entry["layer"]


def test_verification_is_deterministic():
    handoff = cases.clean()
    first = verify(handoff, expectation=cases.expectation())
    second = verify(copy.deepcopy(handoff), expectation=cases.expectation())
    assert first == second


def test_verifier_does_not_mutate_its_input():
    handoff = cases.clean()
    before = copy.deepcopy(handoff)
    verify(handoff, expectation=cases.expectation())
    assert handoff == before


def test_no_expectation_still_checks_internal_consistency():
    """Without an expectation the tool checks what it can and no more."""
    result = verify(cases.build("checkpoint-mismatch"))
    assert result["verdict"] == "FAIL"
    result = verify(cases.build("constraint-dropped"))
    assert result["verdict"] == "PASS"  # nothing said C1 had to survive


def test_required_decision_must_survive_or_be_superseded():
    """A dropped decision fails on its own, not as a side effect of resealing."""
    from babelci.seal import seal

    expectation = {**cases.expectation(), "required_decisions": ["D1", "D2"]}
    assert verify(cases.clean(), expectation=expectation)["verdict"] == "PASS"

    dropped = cases.clean()
    dropped["decisions"] = [d for d in dropped["decisions"]
                            if d["decision_id"] != "D2"]
    dropped = seal(dropped, declare_authority="agent-a")

    result = verify(dropped, expectation=expectation)
    assert codes(result) == {contract.REQUIRED_DECISION_MISSING}
    assert layer(result, contract.LAYER_CONSTRAINTS)["status"] == FAILED


def test_a_superseded_decision_satisfies_the_requirement():
    """Superseding is how a decision legitimately leaves the artifact."""
    from babelci.seal import seal

    expectation = {**cases.expectation(), "required_decisions": ["D2"]}
    replaced = cases.clean()
    replaced["decisions"] = [d for d in replaced["decisions"]
                             if d["decision_id"] != "D2"]
    replaced["decisions"].append({
        "decision_id": "D9", "choice": "Batch-migrate after all.",
        "supersedes": "D2", "provenance": "query/db"})
    replaced = seal(replaced, declare_authority="agent-a")
    assert verify(replaced, expectation=expectation)["verdict"] == "PASS"


def test_required_decisions_do_not_catch_a_silent_reversal():
    """The honest limit, asserted so it cannot be quietly widened later."""
    expectation = {**cases.expectation(), "required_decisions": ["D1", "D2"]}
    result = verify(cases.build("decision-reversed"), expectation=expectation)
    assert result["verdict"] == "PASS"
