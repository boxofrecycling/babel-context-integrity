"""Documentation that is generated must not drift from its source.

Two things in this repository claim to describe the code: the diff rule table
in `docs/DIFF_RULES.md` and the finding codes in `docs/`. Both are checked
here, because documentation that quietly stops matching the tool is worse than
documentation that does not exist.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    not (ROOT / "tools" / "gen_docs.py").exists(),
    reason="not running from a source checkout")


def test_diff_rules_doc_is_in_sync_with_the_rule_table():
    target = ROOT / "docs" / "DIFF_RULES.md"
    before = target.read_text(encoding="utf-8")
    subprocess.run([sys.executable, "tools/gen_docs.py"], cwd=ROOT, check=True,
                   capture_output=True)
    after = target.read_text(encoding="utf-8")
    assert before == after, "run `python tools/gen_docs.py` and commit the result"


def test_every_finding_code_the_verifier_can_emit_is_documented():
    from babelci import contract

    codes = {
        name for name in dir(contract)
        if name.isupper() and isinstance(getattr(contract, name), str)
        and getattr(contract, name) == name
    }
    documented = " ".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "docs").glob("*.md"))
    documented += (ROOT / "README.md").read_text(encoding="utf-8")

    missing = sorted(code for code in codes if code not in documented)
    assert not missing, f"finding codes with no documentation: {missing}"


def test_readme_does_not_make_forbidden_claims():
    """Words this project has not earned."""
    banned = [
        "revolutionary", "guarantees correctness", "solves AI memory",
        "first ever", "world's first", "never fails", "provably true",
        "eliminates hallucination", "100% accurate",
    ]
    text = " ".join(
        path.read_text(encoding="utf-8").lower()
        for path in [ROOT / "README.md", *(ROOT / "docs").glob("*.md")])
    found = [phrase for phrase in banned if phrase in text]
    assert not found, f"unearned claims in public docs: {found}"


def test_readme_command_examples_use_the_real_binary_name():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for match in re.finditer(r"^\$ (\S+)", text, flags=re.MULTILINE):
        assert match.group(1) in ("babelci", "babel-verify", "pip"), match.group(0)


def test_examples_referenced_by_the_readme_exist():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in re.findall(r"examples/([\w.-]+\.json)", text):
        assert (ROOT / "examples" / name).exists(), name


def test_no_finding_code_is_dead():
    """Every declared code must be emittable by some code path.

    A code that nothing can produce is documentation of a check that does not
    exist, which is the exact failure this project complains about.
    """
    from babelci import contract

    declared = {
        name for name in dir(contract)
        if name.isupper() and isinstance(getattr(contract, name), str)
        and getattr(contract, name) == name
    }
    sources = " ".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "src" / "babelci").rglob("*.py")
        if path.name != "contract.py")
    unreachable = sorted(code for code in declared if code not in sources)
    assert not unreachable, f"finding codes nothing can emit: {unreachable}"
