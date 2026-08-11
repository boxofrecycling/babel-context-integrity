"""The lab is a regression harness before it is a demonstration."""

from __future__ import annotations

import json

from babelci.lab import cases
from babelci.lab.run import run_all


def test_every_case_reaches_its_declared_verdict_and_layer():
    report = run_all()
    failures = [record for record in report["cases"] if not record["lab_ok"]]
    assert not failures, [
        (record["case"], record["verdict"], record["caught_at"])
        for record in failures]


def test_lab_digest_is_stable_across_runs():
    assert run_all()["lab_digest"] == run_all()["lab_digest"]


def test_every_case_names_the_private_result_it_mirrors():
    """Public claims must trace to something that was actually established."""
    for case in cases.CASES:
        assert case["mirrors"], case["id"]
        assert case["teaches"], case["id"]


def test_the_lab_covers_every_verification_layer_that_can_fail():
    from babelci.contract import (
        LAYER_AUTHORITIES, LAYER_CHECKPOINT, LAYER_CONFLICTS, LAYER_CONSTRAINTS,
        LAYER_EXTERNAL, LAYER_PROVENANCE,
    )
    covered = {case["expect_layer"] for case in cases.CASES}
    for layer in (LAYER_CHECKPOINT, LAYER_PROVENANCE, LAYER_CONSTRAINTS,
                  LAYER_CONFLICTS, LAYER_AUTHORITIES, LAYER_EXTERNAL):
        assert layer in covered, f"no lab case exercises {layer}"


def test_generated_fixtures_round_trip_through_json(tmp_path):
    for case in cases.CASES:
        artifact = cases.build(case["id"])
        text = json.dumps(artifact, sort_keys=True)
        assert json.loads(text) == artifact


def test_overhead_is_measured_not_asserted():
    report = run_all()
    overhead = report["overhead"]
    assert overhead["total_bits"] > 0
    assert 0 < overhead["integrity_fraction"] < 1
    assert (overhead["content_bits"] + overhead["integrity_bits"]
            >= overhead["total_bits"] * 0.9)
