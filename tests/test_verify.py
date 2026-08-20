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


def test_handoff_without_a_declared_authority_does_not_claim_agreement():
    """The verifier agreeing with itself is a self-check, not agreement.

    Both of this tool's encoders are this tool's. With no producer-side
    commitment to compare against, nothing independent examined the artifact,
    and the layer must say so in the same word it uses for a missing receipt.
    """
    handoff = cases.clean()
    handoff.pop("authorities", None)
    result = verify(handoff, expectation=cases.expectation())
    entry = layer(result, contract.LAYER_AUTHORITIES)
    assert entry["status"] != VERIFIED
    assert entry["status"] == NOT_ESTABLISHED
    assert contract.AUTHORITY_SINGLE_ENCODING in {
        finding["code"] for finding in result["findings"]}


def test_an_unestablished_authority_layer_does_not_fail_the_run():
    """`not established` is an unexamined layer, not a defect.

    This is the compatibility guarantee: an artifact that never declared an
    authority keeps passing and keeps its exit code. Only the word changes.
    """
    handoff = cases.clean()
    handoff.pop("authorities", None)
    result = verify(handoff, expectation=cases.expectation())
    assert result["verdict"] == "PASS"
    assert not codes(result)


def test_a_declared_authority_still_verifies_the_layer():
    """Producers that do the stronger thing keep the stronger result."""
    result = verify(cases.clean(), expectation=cases.expectation())
    entry = layer(result, contract.LAYER_AUTHORITIES)
    assert entry["status"] == VERIFIED
    assert contract.AUTHORITY_SINGLE_ENCODING not in {
        finding["code"] for finding in result["findings"]}


def test_authority_disagreement_stays_failed_and_is_not_softened():
    """A real disagreement must not be downgraded to merely unexamined.

    `authority-disagreement` declares no authorities either, so it reaches the
    same branch. Silence and contradiction are different findings and the
    guard that separates them is load-bearing.
    """
    result = verify(cases.build("authority-disagreement"),
                    expectation=cases.expectation())
    entry = layer(result, contract.LAYER_AUTHORITIES)
    assert entry["status"] == FAILED
    assert contract.AUTHORITY_DISAGREEMENT in codes(result)


def test_expected_authority_root_that_matches_verifies_provenance():
    """The repository named a root and the artifact grounds its facts there."""
    expectation = cases.expectation()
    assert expectation.get("authority_root") is not None, "fixture lost its root"
    result = verify(cases.clean(), expectation=expectation)
    assert layer(result, contract.LAYER_PROVENANCE)["status"] == VERIFIED
    assert contract.PROVENANCE_ROOT_MISMATCH not in codes(result)


def test_expected_authority_root_that_differs_fails_provenance():
    """A chain drawn to the wrong root is a chain to the wrong root.

    Every other check in this layer asks whether the artifact reaches the root
    it chose for itself. Only the expectation can say that root was the one
    the repository meant.
    """
    handoff = cases.clean()
    actual_root = handoff["provenance"]["authority_root"]
    expectation = {**cases.expectation(), "authority_root": "repo@deadbeef"}
    result = verify(handoff, expectation=expectation)

    assert result["verdict"] == "FAIL"
    assert layer(result, contract.LAYER_PROVENANCE)["status"] == FAILED
    assert contract.PROVENANCE_ROOT_MISMATCH in codes(result)
    finding = next(item for item in result["findings"]
                   if item["code"] == contract.PROVENANCE_ROOT_MISMATCH)
    assert finding["expected"] == "repo@deadbeef"
    assert finding["received"] == actual_root


def test_root_enforcement_does_not_disturb_the_authority_layer():
    """C1 and C2 answer different questions about different fields.

    Enforcing which root the facts hang from says nothing about whether an
    independent encoder agreed, so the authority layer must still report
    `not established` when the producer declared none.
    """
    handoff = cases.clean()
    handoff.pop("authorities", None)
    result = verify(handoff, expectation=cases.expectation())
    assert layer(result, contract.LAYER_AUTHORITIES)["status"] == NOT_ESTABLISHED
    assert layer(result, contract.LAYER_PROVENANCE)["status"] == VERIFIED
    assert result["verdict"] == "PASS"


def _handoff_declaring_nothing_open():
    """A clean artifact with an empty `unresolved`, resealed.

    `unresolved` is inside both the checkpoint commitment and the semantic
    world, so emptying it without resealing and re-declaring the authority
    fails the checkpoint and authority layers for unrelated reasons.
    """
    from babelci.seal import seal

    handoff = cases.clean()
    handoff["unresolved"] = []
    return seal(handoff, declare_authority="agent-a")


def _expectation_requiring_nothing_open():
    """The lab expectation minus its `required_unresolved`.

    That key is what attests the silence; a repository that has not written it
    is the case these tests are about.
    """
    return {key: value for key, value in cases.expectation().items()
            if key != "required_unresolved"}


def test_empty_unresolved_is_reported_as_unattested_not_as_none():
    """Absence must not read as knowledge.

    The contract says silence in `unresolved` claims nothing is open. Nothing
    checks that claim, so the layer says so rather than printing a bare
    "none" that a reader takes for a clean check.
    """
    result = verify(_handoff_declaring_nothing_open(),
                    expectation=_expectation_requiring_nothing_open())
    entry = layer(result, contract.LAYER_CONFLICTS)

    assert contract.SILENCE_UNATTESTED in {f["code"] for f in result["findings"]}
    assert "unattested" in entry["detail"]
    assert entry["detail"] != "none"


def test_silence_is_a_note_and_never_fails_the_run():
    """An unexamined claim is not a defect, and must not become an exit code."""
    result = verify(_handoff_declaring_nothing_open(),
                    expectation=_expectation_requiring_nothing_open())
    assert result["verdict"] == "PASS"
    assert layer(result, contract.LAYER_CONFLICTS)["status"] == VERIFIED
    assert contract.SILENCE_UNATTESTED not in codes(result)


def test_declared_open_issues_are_not_silence():
    """A producer that named its open questions is not being silent."""
    result = verify(cases.clean(), expectation=cases.expectation())
    assert contract.SILENCE_UNATTESTED not in {
        f["code"] for f in result["findings"]}
    assert layer(result, contract.LAYER_CONFLICTS)["detail"] == "none, 1 open"


def test_an_expectation_requiring_an_open_issue_attests_the_silence():
    """When the repository names what must stay open, the claim is checked."""
    expectation = {**cases.expectation(), "required_unresolved": ["U1"]}
    result = verify(_handoff_declaring_nothing_open(), expectation=expectation)
    assert contract.SILENCE_UNATTESTED not in {
        f["code"] for f in result["findings"]}
    assert "unattested" not in layer(result, contract.LAYER_CONFLICTS)["detail"]


def test_an_expectation_that_names_no_root_is_unaffected():
    """The compatibility guarantee for every expectation file written so far.

    Projects whose expectation predates this check -- Lantern's among them --
    must keep the behaviour they had. Silence is not a wildcard the verifier
    fills in; it is a question the repository has not answered.
    """
    without_root = {key: value for key, value in cases.expectation().items()
                    if key != "authority_root"}
    result = verify(cases.clean(), expectation=without_root)
    assert result["verdict"] == "PASS"
    assert layer(result, contract.LAYER_PROVENANCE)["status"] == VERIFIED
    assert contract.PROVENANCE_ROOT_MISMATCH not in codes(result)

    unexpecting = verify(cases.clean())
    assert unexpecting["verdict"] == "PASS"
    assert contract.PROVENANCE_ROOT_MISMATCH not in codes(unexpecting)


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
