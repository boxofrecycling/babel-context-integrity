# Reproducibility appendix

## What reproduces from this repository

Everything in the paper's §7 (Results) and every number in the README.

```bash
git clone <repository> && cd babel-context-integrity
python -m venv .venv
./.venv/bin/pip install -e ".[dev]"

./.venv/bin/python -m pytest -q       # full suite
./.venv/bin/babelci lab               # 15 failure classes
./.venv/bin/babelci lab --json        # machine-readable, with lab_digest
./.venv/bin/babelci demo              # the walkthrough
./action/test-local.sh                # the CI action, without GitHub
./integrations/generic/run.sh         # the four-step handoff loop
```

No network access is required after `pip install`. The package has zero runtime
dependencies; `pytest` and `jsonschema` are development-only.

### Determinism

```bash
babelci lab --json > a.json
babelci lab --json > b.json
diff a.json b.json      # empty
```

The lab emits `lab_digest`, a SHA-256 over
`(case, verdict, caught_at, world_digest)` for every case. It is stable across
runs, processes and machines. `tests/test_lab.py` and the CI workflow both
assert this.

There is no wall-clock time, no randomness, and no environment variable that
affects output other than `NO_COLOR`, which changes only ANSI codes.

### Verifying the no-contact claim

```bash
./.venv/bin/python -m pytest tests/test_no_contact.py -v
```

That file parses every module's AST and fails if any imports `socket`, `ssl`,
`urllib`, `requests`, `httpx`, `subprocess`, `asyncio`, an LLM SDK, or anything
else that could reach outside the process; then monkeypatches the socket layer
to raise and runs every CLI command; then asserts that no command writes a file
unless `--out` or `--in-place` was given.

To check it externally rather than trusting the test:

```bash
# Linux
sudo iptables -A OUTPUT -m owner --uid-owner "$(id -u)" ! -d 127.0.0.1 -j REJECT
babelci lab && babelci demo

# macOS
sandbox-exec -p '(version 1)(allow default)(deny network*)' babelci lab

# Docker
docker run --network=none -v "$PWD:/w" -w /w python:3.12-slim \
  sh -c "pip install -q -e . 2>/dev/null || true; python -m babelci lab"
```

### Clean-checkout check

```bash
tmp=$(mktemp -d)
git clone --depth 1 <repository> "$tmp/bci"
cd "$tmp/bci"
python -m venv .venv && ./.venv/bin/pip install -q -e ".[dev]"
./.venv/bin/python -m pytest -q && ./.venv/bin/babelci lab
```

A stranger needs nothing from the authors' machines. There is no private
submodule, no fetched fixture, and no reference to a path outside the checkout.

## What does **not** reproduce from this repository

**Table 2 of [`docs/RESULTS.md`](../docs/RESULTS.md)** — the private research
findings. Those come from a separate, private, offline research repository that
is not published and is not required by anything here.

They are cited as **provenance for design decisions**, never as evidence for a
public claim. Concretely: the statement "a second verifier exposed 16
alias-structure acceptances the first missed" explains *why* Babel has two
encoders. The claim that Babel's two encoders catch `authority-disagreement` is
established by `babelci lab`, on your machine, in this repository.

If you deleted Table 2 entirely, every public claim would still stand.

### What was verified privately, and cannot be checked here

The private closeout reproduction was executed during preparation of this
export and returned `BABEL_SOFTWARE_FRONTIER_REPRODUCTION_PASS`:

```
protected tree:        PASS
focused suite:         PASS 283 tests
14 result digests:     PASS (all matching the frozen manifest)
network/model contact: PASS 0 attempts
```

You cannot check that from here, and you should treat it accordingly: as a
statement by the authors about work you have not seen, not as a result you have
been shown.

## Environment

Developed and verified on:

- macOS 15 (Darwin 25.6), Apple Silicon
- Python 3.14.6 (venv), and CI across 3.10–3.13

The package targets Python 3.10+. Nothing in it is platform specific; the shell
scripts in `action/` and `integrations/` need `bash`, and
`integrations/generic/read-handoff.sh` needs `jq`.

## Known gaps in this appendix

- The lab has been run on macOS and (in CI configuration) Linux. It has not
  been run on Windows. Cross-platform digest stability is expected — the
  canonical encoding is ASCII with no line endings involved — but has not been
  observed.
- No independent party has reproduced anything here. Every result was produced
  by the authors' own tooling, which is the ordinary situation for a v0.1
  release and worth stating rather than leaving implicit.
