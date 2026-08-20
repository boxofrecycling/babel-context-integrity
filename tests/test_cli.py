"""Command line surface: exit codes, output modes, and failure handling."""

from __future__ import annotations

import json

import pytest

from babelci.cli import main
from babelci.contract import EXIT_FAIL, EXIT_OK, EXIT_REVIEW, EXIT_USAGE
from babelci.lab import cases


@pytest.fixture
def fixtures(tmp_path):
    paths = {}
    for case in cases.CASES:
        path = tmp_path / f"{case['id']}.json"
        path.write_text(json.dumps(cases.build(case["id"])), encoding="utf-8")
        paths[case["id"]] = str(path)
    expect = tmp_path / "expect.json"
    expect.write_text(json.dumps(cases.expectation()), encoding="utf-8")
    paths["__expect__"] = str(expect)
    return paths


def test_verify_pass_exits_zero(fixtures, capsys):
    assert main(["verify", fixtures["clean"]]) == EXIT_OK
    assert "PASS" in capsys.readouterr().out


def test_verify_fail_exits_one(fixtures, capsys):
    code = main(["verify", fixtures["constraint-dropped"],
                 "--expect", fixtures["__expect__"]])
    assert code == EXIT_FAIL
    assert "FAIL" in capsys.readouterr().out


def test_json_output_is_valid_json(fixtures, capsys):
    main(["verify", fixtures["clean"], "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "PASS"
    assert payload["schema"] == "babel-verify/0.1"
    assert len(payload["layers"]) == 8


def test_json_output_carries_expected_and_received_on_failure(fixtures, capsys):
    main(["verify", fixtures["constraint-dropped"],
          "--expect", fixtures["__expect__"], "--json"])
    payload = json.loads(capsys.readouterr().out)
    failures = [f for f in payload["findings"] if f["severity"] == "fail"]
    assert failures
    assert "expected" in failures[0]
    assert "received" in failures[0]


def test_diff_refuse_exits_one(fixtures, capsys):
    code = main(["diff", fixtures["clean"], fixtures["decision-reversed"]])
    assert code == EXIT_FAIL
    assert "REFUSE" in capsys.readouterr().out


def test_diff_review_exits_zero_unless_strict(tmp_path, capsys):
    # A REVIEW-only pair: object values changed, nothing refused.
    old = cases.clean()
    new = cases.build("common-mode")
    del new["external_receipt"]
    for artifact in (old, new):
        artifact["decisions"] = []

    old_path = tmp_path / "review-old.json"
    new_path = tmp_path / "review-new.json"
    old_path.write_text(json.dumps(old), encoding="utf-8")
    new_path.write_text(json.dumps(new), encoding="utf-8")

    assert main(["diff", str(old_path), str(new_path)]) == EXIT_OK
    assert main(["diff", str(old_path), str(new_path), "--strict"]) == EXIT_REVIEW
    assert "REVIEW" in capsys.readouterr().out


def test_the_census_counts_layers_and_never_averages_them(fixtures, capsys):
    """A census, not a score.

    Eight mostly-green lines read as eight checks that passed. The census is
    the one figure that cannot be skimmed past -- and it stays a set of counts
    printed side by side, because a single number is how a verifier turns into
    a rubber stamp.
    """
    main(["verify", fixtures["clean"]])
    out = capsys.readouterr().out
    assert "7 verified" in out
    assert "1 not established" in out
    assert "%" not in out
    assert "score" not in out.lower()


def test_the_census_reports_layers_that_never_ran(tmp_path, capsys):
    """A structural exit must not look like a clean short report."""
    import json as _json

    from babelci.lab import cases as lab_cases

    broken = lab_cases.clean()
    del broken["provenance"]
    path = tmp_path / "broken.json"
    path.write_text(_json.dumps(broken), encoding="utf-8")

    main(["verify", str(path)])
    out = capsys.readouterr().out
    assert "not run" in out


def test_missing_file_is_a_usage_error(capsys):
    assert main(["verify", "/nonexistent/handoff.json"]) == EXIT_USAGE
    assert "cannot read" in capsys.readouterr().err


def test_invalid_json_is_a_usage_error_not_a_crash(tmp_path, capsys):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    assert main(["verify", str(path)]) == EXIT_USAGE
    assert "not valid JSON" in capsys.readouterr().err


def test_seal_produces_a_verifying_artifact(tmp_path, capsys):
    draft = cases.clean()
    draft["checkpoint"]["state_digest"] = "sha256:" + "0" * 64
    draft["summary"]["commitment"] = "sha256:" + "0" * 64
    del draft["authorities"]
    path = tmp_path / "draft.json"
    path.write_text(json.dumps(draft), encoding="utf-8")

    assert main(["seal", str(path), "--in-place"]) == EXIT_OK
    capsys.readouterr()
    assert main(["verify", str(path)]) == EXIT_OK
    capsys.readouterr()


def test_seal_does_not_declare_an_authority_unless_asked(tmp_path, capsys):
    draft = cases.clean()
    del draft["authorities"]
    path = tmp_path / "draft.json"
    path.write_text(json.dumps(draft), encoding="utf-8")
    main(["seal", str(path)])
    sealed = json.loads(capsys.readouterr().out)
    assert "authorities" not in sealed


def test_explain_states_what_each_layer_establishes(fixtures, capsys):
    main(["explain", fixtures["clean"]])
    output = capsys.readouterr().out
    assert "what this layer establishes" in output
    assert "Agreement is not truth." in output or "not truth" in output


def test_schema_command_prints_the_normative_schema(capsys):
    assert main(["schema"]) == EXIT_OK
    document = json.loads(capsys.readouterr().out)
    assert document["title"] == "Babel Handoff Contract v0.1"


def test_rules_command_lists_every_diff_rule(capsys):
    from babelci.diff import RULES
    main(["rules", "--json"])
    printed = json.loads(capsys.readouterr().out)
    assert printed == RULES


def test_lab_exits_zero_and_is_reproducible(capsys):
    assert main(["lab", "--json"]) == EXIT_OK
    first = capsys.readouterr().out
    assert main(["lab", "--json"]) == EXIT_OK
    assert capsys.readouterr().out == first


def test_stdin_is_accepted(monkeypatch, capsys):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(cases.clean())))
    assert main(["verify", "-"]) == EXIT_OK
    capsys.readouterr()
