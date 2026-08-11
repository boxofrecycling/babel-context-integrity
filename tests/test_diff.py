"""Semantic drift detection."""

from __future__ import annotations

from babelci.contract import REFUSE, REVIEW, SAFE
from babelci.diff import RULES, diff
from babelci.lab import cases


def rules_fired(result):
    return {change["rule"] for change in result["changes"]}


def test_identical_artifacts_have_no_drift():
    result = diff(cases.clean(), cases.clean())
    assert result["verdict"] == SAFE
    assert result["identical_world"]
    assert not result["changes"]


def test_reserialised_artifact_is_the_same_world():
    """A line diff would light up; a semantic diff must not."""
    import json
    reordered = json.loads(json.dumps(cases.clean(), sort_keys=False))
    reordered["objects"] = list(reversed(reordered["objects"]))
    reordered["retained_constraints"] = list(
        reversed(reordered["retained_constraints"]))
    result = diff(cases.clean(), reordered)
    assert result["identical_world"]
    assert result["verdict"] == SAFE


def test_normal_progress_is_safe():
    result = diff(cases.clean(), cases.build("restart-resume"))
    assert result["verdict"] == SAFE
    assert "checkpoint-advanced" in rules_fired(result)
    assert "unresolved-issue-resolved" in rules_fired(result)


def test_silent_decision_reversal_is_refused():
    result = diff(cases.clean(), cases.build("decision-reversed"))
    assert result["verdict"] == REFUSE
    assert "decision-reversed" in rules_fired(result)


def test_dropped_must_constraint_is_refused():
    result = diff(cases.clean(), cases.build("constraint-dropped"))
    assert result["verdict"] == REFUSE
    assert "must-constraint-removed" in rules_fired(result)


def test_rewritten_must_constraint_is_refused():
    result = diff(cases.clean(), cases.build("constraint-softened"))
    assert result["verdict"] == REFUSE
    assert "must-constraint-modified" in rules_fired(result)


def test_required_object_dropped_by_compaction_is_refused():
    result = diff(cases.clean(), cases.build("compression-loss"))
    assert result["verdict"] == REFUSE
    assert "required-object-removed" in rules_fired(result)


def test_alias_collapse_is_refused():
    result = diff(cases.clean(), cases.build("alias-collapse"))
    assert "alias-bijection-lost" in rules_fired(result)
    assert result["verdict"] == REFUSE


def test_new_conflict_is_refused():
    result = diff(cases.clean(), cases.build("duplicate-conflict"))
    assert "conflict-introduced" in rules_fired(result)
    assert result["verdict"] == REFUSE


def test_losing_external_acceptance_is_refused():
    result = diff(cases.build("externally-confirmed"), cases.build("common-mode"))
    assert "external-acceptance-lost" in rules_fired(result)
    assert result["verdict"] == REFUSE


def test_diff_against_a_correct_predecessor_does_catch_common_mode():
    """The honest scope of the common-mode claim.

    `verify` cannot catch a coherent wrong world from one artifact. `diff` can,
    but only when a correct predecessor exists to compare against -- here it
    fires because D1 changed. An agent that scanned the wrong branch from the
    very first handoff has no predecessor, and then nothing local catches it.
    """
    common = cases.build("common-mode")
    del common["external_receipt"]
    result = diff(cases.clean(), common)
    assert result["verdict"] == REFUSE
    assert "decision-reversed" in rules_fired(result)


def test_a_wrong_world_with_no_prior_decisions_is_only_review():
    """Strip the shared decision and the same corruption drops to REVIEW."""
    old = cases.clean()
    new = cases.build("common-mode")
    del new["external_receipt"]
    for artifact in (old, new):
        artifact["decisions"] = []
    result = diff(old, new)
    assert result["verdict"] == REVIEW
    assert "object-value-changed" in rules_fired(result)
    assert not [c for c in result["changes"] if c["verdict"] == REFUSE]


def test_every_change_cites_a_declared_rule():
    for case in cases.CASES:
        result = diff(cases.clean(), cases.build(case["id"]))
        for change in result["changes"]:
            assert change["rule"] in RULES
            assert change["verdict"] == RULES[change["rule"]]["verdict"]
            assert change["because"] == RULES[change["rule"]]["because"]


def test_verdict_is_the_worst_change():
    for case in cases.CASES:
        result = diff(cases.clean(), cases.build(case["id"]))
        order = {SAFE: 0, REVIEW: 1, REFUSE: 2}
        worst = max((order[change["verdict"]] for change in result["changes"]),
                    default=0)
        assert order[result["verdict"]] == worst
