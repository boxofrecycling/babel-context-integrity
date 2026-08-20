"""Continuity between checkpoints.

`carry` is judged by one question: does the successor it drafts stand up to
the same checks the predecessor did, without asserting anything its producer
did not?
"""

from __future__ import annotations

import copy

from babelci import contract
from babelci.carry import carry
from babelci.contract import REFUSE, SAFE
from babelci.diff import diff
from babelci.lab import cases
from babelci.seal import seal
from babelci.verify import FAILED, NOT_ESTABLISHED, VERIFIED, verify


def layer(result, name):
    return next(entry for entry in result["layers"] if entry["layer"] == name)


def codes(result):
    return {finding["code"] for finding in result["findings"]
            if finding["severity"] == contract.SEVERITY_FAIL}


def successor_of(predecessor, **kwargs):
    """A carried, sealed successor -- the pipeline the CLI documents."""
    kwargs.setdefault("checkpoint_id", "cp-4412-02")
    return seal(carry(predecessor, **kwargs))


# ---------------------------------------------------------------------------
# 1. a valid authority root carries forward

def test_a_valid_authority_root_carries_forward():
    """The successor is grounded in exactly what the predecessor was."""
    predecessor = cases.clean()
    root = predecessor["provenance"]["authority_root"]
    successor = successor_of(predecessor, consumer="agent-c")

    assert successor["provenance"]["authority_root"] == root
    assert successor["provenance"]["edges"] == predecessor["provenance"]["edges"]

    result = verify(successor, expectation=cases.expectation())
    assert result["verdict"] == "PASS"
    assert layer(result, contract.LAYER_PROVENANCE)["status"] == VERIFIED
    assert contract.PROVENANCE_ROOT_MISMATCH not in codes(result)


def test_carry_declares_the_parent_checkpoint():
    """Sixty-five handoffs with no lineage is a ledger nobody can walk."""
    predecessor = cases.clean()
    successor = successor_of(predecessor, consumer="agent-c")
    assert successor["checkpoint"]["parent_checkpoint_id"] == \
        predecessor["checkpoint"]["checkpoint_id"]
    assert successor["checkpoint"]["checkpoint_id"] == "cp-4412-02"


def test_a_carried_successor_is_legitimate_progress():
    """Held against the hand-built continuity fixture, `carry` must agree.

    `restart-resume` is what a correct successor looks like; a drafted one
    must read the same way to the differ.
    """
    result = diff(cases.clean(), successor_of(cases.clean(), consumer="agent-c"))
    assert result["verdict"] == SAFE
    assert "checkpoint-advanced" in {change["rule"] for change in result["changes"]}


# ---------------------------------------------------------------------------
# 2. a changed authority root is detected

def test_a_changed_authority_root_is_detected_by_diff():
    """Regrounding facts elsewhere is refused, not merely noted."""
    tampered = successor_of(cases.clean(), consumer="agent-c")
    tampered["provenance"]["authority_root"] = "repo@deadbeef"
    tampered = seal(tampered)

    result = diff(cases.clean(), tampered)
    assert result["verdict"] == REFUSE
    assert "authority-root-changed" in {c["rule"] for c in result["changes"]}


def test_a_changed_authority_root_is_detected_against_the_expectation():
    """The repository's declared root still binds a carried artifact."""
    tampered = successor_of(cases.clean(), consumer="agent-c")
    tampered["provenance"]["authority_root"] = "repo@deadbeef"
    tampered = seal(tampered)

    result = verify(tampered, expectation=cases.expectation())
    assert result["verdict"] == "FAIL"
    assert layer(result, contract.LAYER_PROVENANCE)["status"] == FAILED
    assert contract.PROVENANCE_ROOT_MISMATCH in codes(result)


# ---------------------------------------------------------------------------
# 3. missing authority stays unestablished

def test_carry_withholds_authority_and_the_layer_stays_unestablished():
    """Carrying a predecessor's authority would invent the successor's.

    An authority entry is a commitment its producer computed over its own
    world. The successor's producer has computed nothing, so there is nothing
    to carry, and the layer must say it was never examined.
    """
    predecessor = cases.clean()
    assert predecessor.get("authorities"), "fixture lost its authority"

    successor = successor_of(predecessor, consumer="agent-c")
    assert "authorities" not in successor

    result = verify(successor, expectation=cases.expectation())
    entry = layer(result, contract.LAYER_AUTHORITIES)
    assert entry["status"] != VERIFIED
    assert entry["status"] == NOT_ESTABLISHED
    assert result["verdict"] == "PASS"


def test_carry_withholds_a_receipt_and_a_stale_summary():
    """An acceptance of the old world is not an acceptance of the new one."""
    predecessor = cases.build("externally-confirmed")
    assert predecessor.get("external_receipt"), "fixture lost its receipt"

    successor = carry(predecessor, checkpoint_id="cp-4412-02",
                      producer="agent-b")
    assert "external_receipt" not in successor
    assert "summary" not in successor

    result = verify(seal(successor), expectation=cases.expectation())
    assert layer(result, contract.LAYER_EXTERNAL)["status"] == NOT_ESTABLISHED


def test_a_supplied_summary_is_the_producers_own():
    successor = successor_of(cases.clean(), consumer="agent-c",
                             summary="Auth migration resumed at cp-4412-02.")
    assert successor["summary"]["text"].startswith("Auth migration resumed")
    result = verify(successor, expectation=cases.expectation())
    assert contract.SUMMARY_COMMITMENT_MISMATCH not in codes(result)


# ---------------------------------------------------------------------------
# 4. artifacts without the optional fields stay compatible

def test_an_artifact_carrying_none_of_the_optional_fields_still_carries():
    """The minimum legal artifact must survive the round trip.

    Nothing optional is synthesised on the way through: an absent field in the
    predecessor is an absent field in the successor, because inventing one
    would assert something nobody claimed.
    """
    minimal = cases.clean()
    for field in ("authorities", "external_receipt", "summary", "decisions",
                  "unresolved", "artifacts", "aliases"):
        minimal.pop(field, None)
    minimal["checkpoint"].pop("parent_checkpoint_id", None)
    minimal = seal(minimal)

    successor = seal(carry(minimal, checkpoint_id="cp-4412-02",
                           producer="agent-b"))
    for field in ("decisions", "unresolved", "artifacts", "aliases",
                  "authorities", "external_receipt", "summary"):
        assert field not in successor, field

    result = verify(successor)
    assert result["verdict"] == "PASS"
    assert layer(result, contract.LAYER_STRUCTURE)["status"] == VERIFIED


def test_carry_does_not_mutate_its_input():
    predecessor = cases.clean()
    before = copy.deepcopy(predecessor)
    carry(predecessor, checkpoint_id="cp-4412-02", consumer="agent-c")
    assert predecessor == before


def test_carry_needs_somebody_for_the_work_to_pass_to():
    """A handoff with no named consumer cannot silently invent a successor."""
    orphan = cases.clean()
    orphan.pop("consumer", None)
    try:
        carry(orphan, checkpoint_id="cp-4412-02")
    except ValueError as error:
        assert "producer" in str(error)
    else:
        raise AssertionError("carry invented a producer")
