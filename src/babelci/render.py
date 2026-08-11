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

from .contract import REFUSE, REVIEW, SAFE, SEVERITY_FAIL
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


def render_verify(result: dict[str, Any], *, verbose: bool = False,
                  stream=None) -> str:
    stream = stream or sys.stdout
    colour = _colour_enabled(stream)
    lines: list[str] = []

    verdict = result["verdict"]
    heading = _paint(verdict, _VERDICT_STYLE[verdict], colour)
    source = result.get("source")
    lines.append(f"{heading}  {source}" if source else heading)

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
            if "expected" in finding and "received" in finding:
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
        group = [c for c in result["changes"] if c["verdict"] == wanted]
        if not group:
            continue
        lines.append("")
        lines.append(f"  {_paint(wanted, _VERDICT_STYLE[wanted], colour)}")
        for change in group:
            lines.append(f"    {change['subject']}")
            lines.append(f"      {change['rule']}: {change['detail']}")
            if verbose:
                lines.append(f"      because {change['because']}")
                if change.get("before") is not None:
                    lines.append(f"      before: {_short(change['before'], verbose)}")
                if change.get("after") is not None:
                    lines.append(f"      after:  {_short(change['after'], verbose)}")
    return "\n".join(lines)


__all__ = ["render_verify", "render_explain", "render_diff"]
