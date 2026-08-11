"""Run the lab and report what the verifier concluded on each case.

The lab is a regression harness first and a demonstration second. Each case
declares in advance which verdict it expects and, when it fails, which layer
should catch it. A case that fails at the wrong layer is a lab failure even
though the verdict matched -- otherwise the layering claim would be untested.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..canonical import bit_length, digest
from ..contract import EXIT_FAIL, EXIT_OK
from ..diff import diff
from ..verify import FAILED, verify
from . import cases


HEADLINE = {
    "clean": "clean-handoff.json",
    "constraint-dropped": "corrupted-handoff.json",
    "common-mode": "common-mode-handoff.json",
}


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    handoff = cases.build(case["id"])

    expectation = cases.expectation()
    if case.get("needs_expectation"):
        expectation = {**expectation, **case["needs_expectation"]}

    result = verify(handoff, expectation=expectation, source=f"lab:{case['id']}")

    failed_layers = [layer["layer"] for layer in result["layers"]
                     if layer["status"] == FAILED]

    record: dict[str, Any] = {
        "case": case["id"],
        "title": case["title"],
        "verdict": result["verdict"],
        "expected_verdict": case["expect_verdict"],
        "caught_at": failed_layers[0] if failed_layers else None,
        "expected_layer": case["expect_layer"],
        "codes": sorted({finding["code"] for finding in result["findings"]
                         if finding["severity"] == "fail"}),
        "teaches": case["teaches"],
        "mirrors_private_result": case["mirrors"],
        "world_digest": (result.get("computed") or {}).get("world_digest"),
        "artifact_bits": bit_length(handoff),
    }

    if case.get("diff_against"):
        other = cases.build(case["diff_against"])
        drift = diff(other, handoff,
                     old_source=case["diff_against"], new_source=case["id"])
        record["diff_verdict"] = drift["verdict"]
        record["expected_diff"] = case.get("expect_diff")
        record["diff_rules"] = sorted({change["rule"] for change in drift["changes"]
                                       if change["verdict"] != "SAFE"})

    ok = record["verdict"] == record["expected_verdict"]
    if case["expect_layer"] is not None:
        ok = ok and record["caught_at"] == case["expect_layer"]
    if case.get("expect_diff"):
        ok = ok and record.get("diff_verdict") == case["expect_diff"]
    record["lab_ok"] = ok
    return record


def overhead() -> dict[str, Any]:
    """Measure what the integrity machinery costs on this scenario.

    The private apparatus found that carrying a full proof alongside a summary
    made the transmission larger than the context it replaced. The public
    contract is much lighter -- it carries commitments rather than proofs -- so
    this measures the actual number instead of inheriting the old one.
    """
    handoff = cases.clean()
    payload = {key: value for key, value in handoff.items()
               if key not in ("checkpoint", "summary", "authorities",
                              "provenance", "aliases")}
    integrity = {key: value for key, value in handoff.items()
                 if key in ("checkpoint", "summary", "authorities",
                            "provenance", "aliases")}
    return {
        "content_bits": bit_length(payload),
        "integrity_bits": bit_length(integrity),
        "total_bits": bit_length(handoff),
        "integrity_fraction": round(
            bit_length(integrity) / bit_length(handoff), 4),
    }


def run_all(only: str | None = None) -> dict[str, Any]:
    selected = ([cases.CASES_BY_ID[only]] if only else cases.CASES)
    records = [run_case(case) for case in selected]
    return {
        "schema": "babel-lab/0.1",
        "scenario": cases.clean()["task"]["task_id"],
        "cases": records,
        "overhead": overhead(),
        "all_ok": all(record["lab_ok"] for record in records),
        "lab_digest": digest([
            [record["case"], record["verdict"], record["caught_at"],
             record["world_digest"]]
            for record in records]),
    }


def _render(report: dict[str, Any]) -> str:
    lines = [f"BABEL LAB  {report['scenario']}", ""]
    width = max(len(record["case"]) for record in report["cases"])
    for record in report["cases"]:
        mark = "ok  " if record["lab_ok"] else "LAB "
        verdict = record["verdict"]
        where = f"  at {record['caught_at']}" if record["caught_at"] else ""
        lines.append(f"{mark}{record['case']:<{width}}  {verdict:<4}{where}")
        if record.get("diff_verdict"):
            lines.append(f"    {'':<{width}}  diff {record['diff_verdict']}")
    lines.append("")
    overheads = report["overhead"]
    lines.append(
        f"integrity overhead: {overheads['integrity_bits']} of "
        f"{overheads['total_bits']} bits "
        f"({overheads['integrity_fraction'] * 100:.1f}% of the artifact)")
    lines.append(f"lab digest: {report['lab_digest']}")
    lines.append("")
    lines.append("PASS" if report["all_ok"] else "LAB REGRESSION")
    return "\n".join(lines)


def main(args) -> int:
    if getattr(args, "list", False):
        for case in cases.CASES:
            print(f"{case['id']:<24} {case['title']}")
        return EXIT_OK

    only = getattr(args, "case", None)
    if only and only not in cases.CASES_BY_ID:
        print(f"babelci: unknown lab case {only!r}; try --list")
        return 2

    report = run_all(only)

    out = getattr(args, "out", None)
    if out:
        directory = Path(out)
        directory.mkdir(parents=True, exist_ok=True)
        for case in (cases.CASES if not only else [cases.CASES_BY_ID[only]]):
            path = directory / f"{case['id']}.json"
            path.write_text(
                json.dumps(cases.build(case["id"]), indent=2, sort_keys=True,
                           ensure_ascii=False) + "\n", encoding="utf-8")
        (directory / "expect.json").write_text(
            json.dumps(cases.expectation(), indent=2, sort_keys=True,
                       ensure_ascii=False) + "\n", encoding="utf-8")
        # The three the README and the demo point at, under names that say what
        # they are to someone who has not read the case list yet.
        for case_id, friendly in HEADLINE.items():
            if only and case_id != only:
                continue
            (directory / friendly).write_text(
                json.dumps(cases.build(case_id), indent=2, sort_keys=True,
                           ensure_ascii=False) + "\n", encoding="utf-8")

    if getattr(args, "json", False):
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(_render(report))
    return EXIT_OK if report["all_ok"] else EXIT_FAIL


__all__ = ["run_all", "run_case", "overhead", "main"]
