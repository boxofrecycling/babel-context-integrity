"""Human-readable output.

Terse by default. The verbose form exists for when a check fails and the reader
needs the expected/received pair, not before. Colour is emitted only to a real
terminal and is suppressed by ``NO_COLOR``.
"""

from __future__ import annotations

import os
import sys
import textwrap
from typing import Any

from .contract import LAYERS, REFUSE, REVIEW, SAFE, SEVERITY_FAIL
from .verify import FAILED, NOT_ESTABLISHED, VERIFIED

_WIDTH = 22

_STATUS_STYLE = {
    VERIFIED: ("32", "verified"),
    FAILED: ("31", "FAILED"),
    NOT_ESTABLISHED: ("33", "not established"),
}

_VERDICT_STYLE = {
    "PASS": "32", "FAIL": "31",
    SAFE: "32", REVIEW: "33", REFUSE: "31",
}


def _colour_enabled(stream) -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("BABELCI_FORCE_COLOR"):
        return True
    return hasattr(stream, "isatty") and stream.isatty()


def _paint(text: str, code: str, enabled: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if enabled else text


def _dots(label: str) -> str:
    pad = max(1, _WIDTH - len(label))
    return f"{label} {'.' * pad}"


def _wrap(text: str, indent: str) -> list[str]:
    """Wrap a finding's prose so a long detail stays readable in a terminal.

    Fixed width rather than the terminal's, so that output pasted into an
    issue, a README or a CI log looks the same everywhere -- and so that
    documentation showing this output cannot drift with window size.
    """
    wrapped = textwrap.wrap(
        text, width=76 - len(indent), break_long_words=False,
        break_on_hyphens=False)
    return [indent + line for line in (wrapped or [""])]


def _census(layers: list[dict[str, Any]]) -> str:
    """What was assessed, and what was not.

    A census, never a score: the counts are printed side by side and never
    combined, for the same reason the layers themselves are not averaged. Its
    job is to stop eight lines of mostly-green being read as eight checks that
    passed, and to make an early structural exit visible as unrun rather than
    absent.
    """
    counted = [(sum(1 for entry in layers if entry["status"] == status), label)
               for status, (_, label) in _STATUS_STYLE.items()]
    parts = [f"{count} {label}" for count, label in counted if count]
    unrun = len(LAYERS) - len(layers)
    if unrun > 0:
        parts.append(f"{unrun} not run")
    return " \u00b7 ".join(parts)


def render_verify(result: dict[str, Any], *, verbose: bool = False,
                  stream=None) -> str:
    stream = stream or sys.stdout
    colour = _colour_enabled(stream)
    lines: list[str] = []

    verdict = result["verdict"]
    heading = _paint(verdict, _VERDICT_STYLE[verdict], colour)
    source = result.get("source")
    lines.append(f"{heading}  {source}" if source else heading)
    lines.append(f"      {_census(result['layers'])}")

    for layer in result["layers"]:
        code, label = _STATUS_STYLE[layer["status"]]
        text = _paint(label, code, colour)
        suffix = ""
        if layer["status"] == VERIFIED and layer.get("detail"):
            suffix = f"   {layer['detail']}"
        lines.append(f"  {_dots(layer['layer'])} {text}{suffix}")

    failures = [f for f in result["findings"] if f["severity"] == SEVERITY_FAIL]
    if failures:
        lines.append("")
        for finding in failures:
            lines.append(f"  {_paint(finding['code'], '31', colour)}")
            lines.extend(_wrap(finding["detail"], "    "))
            if isinstance(finding.get("received"), list) and finding["received"]:
                # A list of reasons reads as a list, not as a Python repr.
                for item in finding["received"]:
                    lines.extend(_wrap(f"- {item}", "      "))
            elif "expected" in finding and "received" in finding:
                lines.append(f"    expected: {_short(finding['expected'], verbose)}")
                lines.append(f"    received: {_short(finding['received'], verbose)}")
            elif "received" in finding:
                lines.append(f"    received: {_short(finding['received'], verbose)}")

    notes = [f for f in result["findings"] if f["severity"] != SEVERITY_FAIL]
    if notes and (verbose or not failures):
        lines.append("")
        for finding in notes:
            wrapped = _wrap(finding["detail"], "        ")
            lines.append("  note  " + wrapped[0].lstrip())
            lines.extend(wrapped[1:])

    if verbose and result.get("computed"):
        lines.append("")
        lines.append(f"  world digest: {result['computed']['world_digest']}")
        for encoding in result["computed"]["encodings"]:
            lines.append(f"    {encoding['encoding']}")

    return "\n".join(lines)


def _short(value: Any, verbose: bool) -> str:
    text = value if isinstance(value, str) else repr(value)
    if not verbose and len(text) > 96:
        return text[:93] + "..."
    return text


def render_explain(result: dict[str, Any], meanings: dict[str, str], *,
                   stream=None) -> str:
    stream = stream or sys.stdout
    colour = _colour_enabled(stream)
    lines = [f"{result.get('source') or 'handoff'}",
             f"  task     {result.get('task_id')}",
             f"  handoff  {result.get('handoff_id')}",
             ""]
    for layer in result["layers"]:
        code, label = _STATUS_STYLE[layer["status"]]
        lines.append(f"{layer['layer']}: {_paint(label, code, colour)}")
        lines.append(f"  what this layer establishes")
        lines.append(f"    {meanings[layer['layer']]}")
        if layer.get("detail"):
            lines.append(f"  observed")
            lines.append(f"    {layer['detail']}")
        for finding in layer["findings"]:
            lines.append(f"  {finding['code']}")
            lines.append(f"    {finding['detail']}")
            if "expected" in finding:
                lines.append(f"    expected: {finding['expected']}")
            if "received" in finding:
                lines.append(f"    received: {finding['received']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_diff(result: dict[str, Any], *, verbose: bool = False,
                stream=None) -> str:
    stream = stream or sys.stdout
    colour = _colour_enabled(stream)
    verdict = result["verdict"]
    lines = [_paint(verdict, _VERDICT_STYLE[verdict], colour)]
    if result["identical_world"]:
        lines.append("  the two artifacts describe the same semantic world")
        return "\n".join(lines)
    if not result["changes"]:
        lines.append("  no contract-level changes")
        return "\n".join(lines)

    for wanted in (REFUSE, REVIEW, SAFE):
        group = [change for change in result["changes"]
                 if change["verdict"] == wanted]
        if not group:
            continue
        lines.append("")
        lines.append(f"  {_paint(wanted, _VERDICT_STYLE[wanted], colour)}")

        # Group by rule so the reader gets one plain sentence per kind of
        # change, then the instances underneath. The rule id is a machine
        # handle; it belongs in --json and -v, not at the front of the line a
        # developer reads first.
        for index, rule in enumerate(_rules_in_order(group)):
            instances = [c for c in group if c["rule"] == rule]
            if index:
                lines.append("")
            lines.append(f"    {instances[0]['headline']}")
            if verbose:
                lines.extend(_wrap(f"({instances[0]['because']})", "      "))
                lines.append(f"      rule: {rule}")
            # Align the value column across the instances of one rule.
            width = max(len(c["subject"]) for c in instances)
            for change in instances:
                lines.extend(_change_lines(change, verbose, width))
    return "\n".join(lines)


def _rules_in_order(group: list[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for change in group:
        if change["rule"] not in seen:
            seen.append(change["rule"])
    return seen


def _change_lines(change: dict[str, Any], verbose: bool,
                  width: int) -> list[str]:
    """Render one instance: what it is, and what actually changed."""
    before, after = change.get("before"), change.get("after")
    subject = change["subject"].ljust(width)

    left = _value(before, verbose)
    right = _value(after, verbose)
    inline_budget = 56 - width

    if before is not None and after is not None:
        # Short values read better on one line than stacked.
        if len(left) + len(right) + 4 <= inline_budget:
            return [f"      {subject}  {left} -> {right}"]
        return [f"      {change['subject']}",
                f"        was  {left}",
                f"        now  {right}"]
    if before is not None:
        if len(left) <= inline_budget:
            return [f"      {subject}  was {left}"]
        return [f"      {change['subject']}", f"        was  {left}"]
    if after is not None:
        if len(right) <= inline_budget:
            return [f"      {subject}  {right}"]
        return [f"      {change['subject']}", f"        {right}"]
    return [f"      {subject}  {change['detail']}"]


def _value(value: Any, verbose: bool) -> str:
    if value is None:
        return "(absent)"
    if isinstance(value, str):
        text = value if verbose or len(value) <= 88 else value[:85] + "..."
        return f'"{text}"' if " " in text or not text else text
    return _short(value, verbose)


__all__ = ["render_verify", "render_explain", "render_diff"]
