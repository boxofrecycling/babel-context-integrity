# Contributing

## The rule that governs everything

**No layer may claim more than it checks.**

If a change makes a verification layer report `verified` in a case where it did
not actually establish what its `LAYER_MEANING` entry says it establishes, that
change is wrong regardless of how convenient it is. This project's only value
is that its green ticks mean something.

## Adding a verification check

1. a finding code in `src/babelci/contract.py` (codes are stable; add, never
   repurpose);
2. the check in the correct layer of `src/babelci/verify.py`;
3. a lab case in `src/babelci/lab/cases.py` declaring its expected verdict
   **and the layer that should catch it**;
4. a test in `tests/test_verify.py`;
5. documentation — `tests/test_docs.py` fails if a finding code appears nowhere
   in `docs/` or `README.md`.

A lab case that fails at the wrong layer fails the lab even when the verdict is
right. That is intentional: without it, the layering claim is untested.

## Adding a diff verdict

1. an entry in `diff.RULES` with a `verdict` and a `because` that explains the
   reasoning to a stranger;
2. `python tools/gen_docs.py`;
3. commit the regenerated `docs/DIFF_RULES.md`.

`SAFE`, `REVIEW` and `REFUSE` must each come from an explicit rule. If you find
yourself wanting a heuristic, the answer is `REVIEW` under
`unclassified-change` — a human deciding beats a tool guessing.

## Changing the contract

Read [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) first. Adding an optional
field is compatible. Changing a digest recipe, a required field, or the meaning
of a code is breaking and needs a contract version bump — and a v0.1 verifier
must keep refusing v0.2 artifacts rather than mis-verifying them.

Both the native validator (`src/babelci/schema.py`) and the JSON Schema
(`schema/`) must change together. `tests/test_schema_parity.py` fails otherwise,
which is the point of having two.

## Things that will be declined

- **A runtime dependency.** The tool has to install into a locked-down CI image.
- **Anything that opens a socket or spawns a process.** `tests/test_no_contact.py`
  enforces this by parsing imports.
- **Telemetry, a config file, a cache directory, or a daemon.** A verifier that
  phones home is not a verifier.
- **Collapsing layers into a score.** The separation is the design.
- **Removing the `not established` state**, or reporting it as passing.
- **A claim in the README that the lab does not reproduce.**
  `tests/test_docs.py` blocks a list of unearned phrases; the list is not
  exhaustive and the spirit governs.

## Running things

```bash
pip install -e ".[dev]"
python -m pytest -q          # suite
babelci lab                  # failure classes
./action/test-local.sh       # the CI action, without GitHub
python tools/gen_docs.py     # regenerate generated docs
```

## Style

Match what is there. Comments explain *why* a check exists or why a design
refuses something, not what the line does. If a rule is subtle enough to need a
paragraph, it belongs in `docs/` with a pointer from the code.

## Reporting a bug

The serious class is **a verifier that accepts something it should refuse**.
See [SECURITY.md](SECURITY.md). A minimal artifact that reproduces it is worth
more than a description.
