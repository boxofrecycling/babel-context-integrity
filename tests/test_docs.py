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


def _console_blocks(text):
    """Yield (command_argv, expected_output_lines) from ```console fences."""
    for block in re.findall(r"```console\n(.*?)```", text, flags=re.DOTALL):
        lines = block.rstrip("\n").split("\n")
        if not lines or not lines[0].startswith("$ babelci "):
            continue
        argv = lines[0][len("$ babelci "):].split()
        expected = [line for line in lines[1:] if line.strip()]
        yield argv, expected


def test_readme_console_output_matches_the_real_command():
    """The README shows real output, or it shows a lie.

    Every ```console block whose first line is a babelci invocation is run and
    compared against what the tool actually prints. Composite or aspirational
    output fails here.
    """
    import io
    import os
    from contextlib import redirect_stdout

    from babelci.cli import main

    text = (ROOT / "README.md").read_text(encoding="utf-8")
    checked = 0
    previous = os.getcwd()
    os.chdir(ROOT)
    try:
        for argv, expected in _console_blocks(text):
            if not any(part.startswith("examples/") for part in argv):
                continue  # commands against a user's own .babel/ paths
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                main(argv)
            actual = [line.rstrip() for line in buffer.getvalue().split("\n")
                      if line.strip()]
            for line in expected:
                assert line.rstrip() in actual, (
                    f"README shows a line `babelci {' '.join(argv)}` "
                    f"does not print:\n  {line}")
            checked += 1
    finally:
        os.chdir(previous)
    assert checked >= 3, f"only {checked} README console blocks were verifiable"


def _indented_console_blocks(text):
    """Yield (argv, expected_lines) for `$ babelci ...` blocks at any indent.

    Launch copy nests terminal output inside an outer fence, so the invocation
    is indented rather than starting the line. A block runs from the `$` line
    until the first non-blank line indented less than it, then is dedented by
    the `$` line's own indent.
    """
    lines = text.split("\n")
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if not stripped.startswith("$ babelci "):
            continue
        indent = len(line) - len(stripped)
        argv = stripped[len("$ babelci "):].split()
        body = []
        for following in lines[index + 1:]:
            if not following.strip():
                continue
            if following.strip().startswith("```"):
                break
            if len(following) - len(following.lstrip()) < indent:
                break
            body.append(following[indent:].rstrip())
        yield argv, body


def test_launch_copy_console_output_matches_the_real_command():
    """Launch copy is the most scrutinised text this project will publish.

    The README and landing page are already asserted against real output.
    Launch drafts were not, and drifted: two blocks showed a FAIL against
    `.babel/handoff.json` that the repository's own `.babel/` files do not
    produce, with a constraint id those files never contained. Anyone who ran
    the advertised command would have seen a PASS.
    """
    import io
    import os
    from contextlib import redirect_stdout

    from babelci.cli import main

    checked = 0
    previous = os.getcwd()
    os.chdir(ROOT)
    try:
        for path in sorted((ROOT / "launch").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for argv, expected in _indented_console_blocks(text):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    main(argv)
                actual = [line.rstrip()
                          for line in buffer.getvalue().split("\n")
                          if line.strip()]
                for line in expected:
                    assert line in actual, (
                        f"{path.name} shows a line that "
                        f"`babelci {' '.join(argv)}` does not print:\n"
                        f"  {line}")
                checked += 1
    finally:
        os.chdir(previous)
    assert checked >= 2, (
        f"only {checked} launch console blocks were verifiable; the launch "
        f"copy must not become unasserted again")


def test_no_url_points_at_a_repository_that_does_not_exist():
    """Metadata that 404s is worse than metadata that is absent.

    Until the repository is published, nothing may link to a plausible-looking
    URL for it. `site/index.html` uses the greppable token
    PLACEHOLDER_REPOSITORY_URL instead, which RELEASE_CHECKLIST.md covers.
    """
    forbidden = [
        "github.com/babel-context-integrity",
        "babel-context-integrity.dev",
        "verify-action@v0",
    ]
    offenders = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(
                part in (".git", ".venv", "__pycache__", "dist", "build")
                for part in path.parts):
            continue
        if path.suffix not in (".md", ".toml", ".cff", ".json", ".yml", ".yaml",
                               ".html", ".sh", ".py"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in forbidden:
            if needle in text and path.name != "test_docs.py":
                offenders.append(f"{path.relative_to(ROOT)}: {needle}")
    assert not offenders, offenders


def test_placeholders_are_confined_to_undeployed_material():
    """A placeholder in shipped code or metadata would be a bug, not a TODO."""
    shipped = list((ROOT / "src").rglob("*.py")) + [
        ROOT / "pyproject.toml", ROOT / "CITATION.cff", ROOT / "README.md",
        ROOT / "LICENSE", ROOT / "NOTICE",
    ]
    for path in shipped:
        assert "PLACEHOLDER_REPOSITORY_URL" not in path.read_text(
            encoding="utf-8"), path


def test_landing_page_terminal_blocks_match_real_output():
    """The site shows the same output the tool prints, or it shows a mockup.

    Only the finding lines are compared -- the page strips the trailing `note`
    output for space, which is a presentation choice rather than a fabrication.
    """
    import io
    import os
    import re as _re
    from contextlib import redirect_stdout

    from babelci.cli import main

    page = ROOT / "site" / "index.html"
    if not page.exists():
        pytest.skip("no landing page in this checkout")

    html = page.read_text(encoding="utf-8")
    blocks = _re.findall(r"<pre>(.*?)</pre>", html, flags=_re.DOTALL)

    previous = os.getcwd()
    os.chdir(ROOT)
    checked = 0
    try:
        for block in blocks:
            text = _re.sub(r"<[^>]+>", "", block)
            text = (text.replace("&gt;", ">").replace("&lt;", "<")
                        .replace("&amp;", "&"))
            lines = [line.rstrip() for line in text.split("\n") if line.strip()]
            if not lines or not lines[0].startswith("$ babelci "):
                continue
            argv = lines[0][len("$ babelci "):].split()
            if not any(part.startswith("examples/") for part in argv):
                continue
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                main(argv)
            actual = [line.rstrip() for line in buffer.getvalue().split("\n")
                      if line.strip()]
            for line in lines[1:]:
                assert line in actual, (
                    f"site shows a line `babelci {' '.join(argv)}` does not "
                    f"print:\n  {line}")
            checked += 1
    finally:
        os.chdir(previous)
    assert checked >= 1, "no verifiable terminal block found on the landing page"
