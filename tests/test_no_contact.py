"""The package must not be able to reach anything.

This is the claim the README makes on the first screen, so it is a test rather
than a promise. It is enforced two ways: by static inspection of what the
package imports, and by monkeypatching the socket layer to explode and then
running every command.
"""

from __future__ import annotations

import ast
import json
import socket
from pathlib import Path

import pytest

import babelci
from babelci.cli import main

PACKAGE = Path(babelci.__file__).resolve().parent

# Modules that can open a socket, spawn a process, or load code from elsewhere.
FORBIDDEN_IMPORTS = {
    "socket", "ssl", "http", "http.client", "urllib", "urllib.request",
    "requests", "httpx", "aiohttp", "urllib3", "ftplib", "smtplib",
    "telnetlib", "xmlrpc", "asyncio", "subprocess", "multiprocessing",
    "ctypes", "pickle", "shelve", "marshal", "importlib",
    "anthropic", "openai", "google.generativeai", "boto3", "litellm",
    "transformers", "torch",
}


def _source_files():
    return sorted(PACKAGE.rglob("*.py"))


def _imported_names(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                yield node.module


@pytest.mark.parametrize("path", _source_files(), ids=lambda p: p.name)
def test_no_module_imports_anything_that_can_reach_out(path):
    for name in _imported_names(path):
        root = name.split(".")[0]
        assert name not in FORBIDDEN_IMPORTS and root not in FORBIDDEN_IMPORTS, (
            f"{path.name} imports {name!r}")


def test_package_declares_no_runtime_dependencies():
    pyproject = PACKAGE.parents[1] / "pyproject.toml"
    if not pyproject.exists():  # installed wheel, not a source checkout
        pytest.skip("not running from a source checkout")
    text = pyproject.read_text(encoding="utf-8")
    body = text.split("dependencies = ", 1)[1].split("\n", 1)[0]
    assert body.strip() == "[]"


@pytest.fixture
def no_network(monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("babelci attempted a network operation")

    monkeypatch.setattr(socket, "socket", explode)
    monkeypatch.setattr(socket, "create_connection", explode)
    monkeypatch.setattr(socket, "getaddrinfo", explode)
    return explode


def test_every_command_runs_with_the_network_disabled(no_network, tmp_path,
                                                      capsys):
    from babelci.lab import cases

    clean = tmp_path / "clean.json"
    clean.write_text(json.dumps(cases.clean()), encoding="utf-8")
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps(cases.build("constraint-dropped")),
                      encoding="utf-8")

    assert main(["verify", str(clean)]) == 0
    assert main(["explain", str(clean)]) == 0
    assert main(["diff", str(clean), str(broken)]) == 1
    assert main(["seal", str(clean)]) == 0
    assert main(["schema"]) == 0
    assert main(["rules"]) == 0
    assert main(["lab"]) == 0
    assert main(["demo"]) == 0
    capsys.readouterr()


def test_no_files_are_written_outside_an_explicit_out_directory(tmp_path,
                                                               monkeypatch,
                                                               capsys):
    """Verification is read-only; nothing caches, logs or phones home."""
    monkeypatch.chdir(tmp_path)
    from babelci.lab import cases

    artifact = tmp_path / "h.json"
    artifact.write_text(json.dumps(cases.clean()), encoding="utf-8")
    before = set(tmp_path.rglob("*"))

    main(["verify", str(artifact)])
    main(["explain", str(artifact)])
    main(["lab"])
    capsys.readouterr()

    assert set(tmp_path.rglob("*")) == before
