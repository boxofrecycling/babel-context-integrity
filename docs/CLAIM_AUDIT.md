# Claim audit

[`LIMITS.md`](LIMITS.md) is the boundary. This file records the audit of every
externally visible surface against it, performed at the v0.1.0 release freeze.

The rule applied: **no visible sentence may imply that Babel determines
arbitrary truth, guarantees correct agent reasoning, validates hidden model
state, solves AI memory, establishes universal semantic equivalence, has been
validated on real models, or eliminates external trust roots.**

## Surfaces audited

| Surface | Result |
|---|---|
| `README.md` | clean |
| `pyproject.toml` (summary, keywords, classifiers) | clean |
| `CITATION.cff` (abstract) | clean |
| `action/action.yml` (marketplace description) | **one fix**, below |
| `docs/*.md` (13 files) | clean |
| `paper/*.md` | clean |
| `release/v0.1.0-notes.md` | clean |
| `site/index.html` | clean |
| `launch/*.md` (7 drafts) | clean |
| `integrations/**/README.md` | clean |
| `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md` | clean |
| CLI output strings (`contract.LAYER_MEANING`, finding details) | clean |

## The one thing that was wrong

The GitHub Action's marketplace description said it fails the check when a
required **decision** did not survive the handoff. At the time, `verify` did not
check decision survival at all — `required_decisions` in an expectation only fed
the `supersedes` reachability set.

Two ways to fix a claim that outruns the code. The description could have been
softened, or the code could be made to match. **The code was changed**:
`required_decisions` is now a presence check emitting
`REQUIRED_DECISION_MISSING`, documented in
[`FINDING_CODES.md`](FINDING_CODES.md) and
[`HANDOFF_CONTRACT.md`](HANDOFF_CONTRACT.md), with tests including one that
asserts it *does not* catch a silent reversal — the limit stated so it cannot be
quietly widened later.

## Distinctions checked as still separate

The five categories LIMITS requires never be collapsed. Each is reported by a
different layer, with its own status, and none is averaged into the others:

| Category | Where it is reported | Never claims |
|---|---|---|
| structural integrity | `structure` layer | that content is meaningful |
| semantic equivalence under the tested contract | `authority agreement`, `diff` | universal equivalence |
| provenance | `provenance` layer | that claimed origins are real |
| authority agreement | `authority agreement` layer | truth |
| external truth | `external truth` layer | more than the receipt's issuer warrants |

Verified mechanically by
`tests/test_verify.py::test_every_layer_reports_a_status` and
`test_common_mode_passes_every_layer_except_external`, which iterate layers
rather than checking a summary verdict.

## Standing enforcement

Three tests keep this from decaying:

- `test_readme_does_not_make_forbidden_claims` — blocks a list of unearned
  phrases across README and all of `docs/`.
- `test_readme_console_output_matches_the_real_command` — runs every `console`
  block in the README and compares against what the tool actually prints. This
  caught a composite diff sample that no single command produced.
- `test_every_finding_code_the_verifier_can_emit_is_documented` and
  `test_no_finding_code_is_dead` — the set of codes the tool can emit and the
  set documented must be equal in both directions.

## Deliberate statements that look like overclaims and are not

- *"Verify what survives when one AI agent hands work to the next."* — the
  package summary. It says what the tool checks, not that the surviving content
  is correct.
- *"Agreement is not truth."* — a limitation stated as a slogan, which is the
  intended reading.
- *"Babel checks what your next agent thinks happened."* — checks the artifact
  recording that, against a declared contract. The following paragraph in every
  surface using this line makes the object of the checking explicit.

## The second thing that was wrong

The v0.1.0 audit recorded `launch/*.md` as clean. It was not, and the reason is
worth stating: the audit checked launch copy for *forbidden claims* and no test
checked it for *false output*. Two drafts — `launch/show-hn.md` and the
superseded `launch/github-release.md` — showed a `FAIL` against
`.babel/handoff.json` citing a constraint `C1`. The repository's own `.babel/`
files verify **PASS** and their expectation requires `R1`–`R4`; `C1` belongs to
the `examples/` fixtures. The output had been transplanted from the README's
`examples/corrupted-handoff.json` case and relabelled.

At the time the defect was found, neither draft had yet been published — and
the live v0.1.0 release notes and `release/v0.1.0-notes.md` always used the
real `examples/` command — but the Show HN body is the most scrutinised text
this project will post, and it advertised a command that prints the opposite of
what it showed.

Both now use the real invocation and its real output, and
`test_launch_copy_console_output_matches_the_real_command` runs every
`$ babelci` block in `launch/` against the tool. The README test skips
`.babel/` paths deliberately, since those stand in for a user's own project;
that skip is what let the launch drafts drift.

## v0.2.0 surfaces — audited 2026-08-20

The audit above was performed at the v0.1.0 freeze. v0.2.0 adds four externally
visible surfaces. Each was audited against the same rule, and the surfaces
inherited from v0.1.0 were re-checked for sentences the new behaviour makes
inaccurate.

| Surface | Visible strings | Result |
|---|---|---|
| `SILENCE_UNATTESTED` | finding detail; `conflicts` detail `none, 0 open (unattested)`; `FINDING_CODES.md` entry | clean |
| `PROVENANCE_ROOT_MISMATCH` | finding detail; `FINDING_CODES.md` entry; extended `LAYER_MEANING[provenance]` | clean |
| coverage census | one line under the verdict | clean |
| `babelci carry` | CLI help; `docs/CLI.md`; the withheld-field table | clean, with one thing stated below |
| `README.md`, `docs/*.md`, `site/index.html`, `launch/*.md` (re-check) | regenerated console blocks | clean; see the disclosure below |

**`SILENCE_UNATTESTED` reduces the claim surface rather than adding to it.** It
exists to stop `none` being read as a completed check. Its detail says the
producer's claim "was not checked here" — a disclaimer, not an assertion.

**`PROVENANCE_ROOT_MISMATCH` states a string comparison and nothing more.** The
detail is `expected facts to trace to authority root X, artifact grounds them
in Y`. A match establishes that the artifact names the root the repository
expected. It does not establish that the root is real or trustworthy, which is
[`LIMITS.md`](LIMITS.md) item 3 and is unchanged. The extended
`LAYER_MEANING[provenance]` adds only "and that root is the one the expectation
required when it named one" — a statement about the expectation, not about the
world.

**The census was the one surface with a real risk, and it was considered.** A
figure printed under a verdict invites reading as a score, and a score is how a
verifier becomes a rubber stamp — the failure the eight separate layers exist to
avoid. It prints counts side by side and never combines them; there is no
percentage, no ratio and no total quality figure.
`test_the_census_counts_layers_and_never_averages_them` asserts that the output
contains neither `%` nor the word `score`. Verdict: clean, and the guard is
mechanical rather than editorial.

**One thing worth stating about `carry`.** With v0.2.0 Babel *produces*
artifacts as well as checking them, for the first time. Nothing about Babel
having written an artifact makes its contents true, and `carry` copies what a
predecessor asserted: a wrong predecessor yields a faithfully wrong successor.
The withheld fields exist so that it cannot do worse than that — it will not
carry an `authorities` entry, an `external_receipt` or a `summary`, because each
would assert something the successor's producer never claimed. This is stated in
[`CLI.md`](CLI.md), in the release notes and in the module docstring. It is
recorded here because "the tool wrote it" is exactly the kind of unearned
authority this audit exists to catch, and it is a new category of risk that the
v0.1.0 audit had no reason to consider.

**Noted, not fixed.** The rationale prose for `carry` in `CLI.md` and
`CHANGELOG.md` says that constraints retyped every session "eventually" get
retyped wrong. That is an unmeasured generalisation about producer behaviour.
It is not one of the seven banned implications and it is rationale rather than a
claim about what Babel establishes, but it is the kind of sentence
[`../launch/README.md`](../launch/README.md) would not allow in announcement
copy, and it should not migrate there.

## Launch drafts regenerated at v0.2.0 — disclosure

The v0.2.0 reporting changes altered lines that appear inside console blocks in
`launch/github-release.md` and `launch/show-hn.md`. Those two files are **v0.1.0
announcement drafts**, and their blocks now show v0.2.0 output: a census line,
and `conflicts ... none, 1 open` in place of `none`.

This was not an edit of a historical record. It is what
`test_launch_copy_console_output_matches_the_real_command` enforces — every
`$ babelci` block in `launch/` is run against the current build and must match.
That test exists because these drafts drifted once before, described in the
section above. Neither draft has been published; they are prepared copy, and
prepared copy that shows output the tool no longer prints is the defect the test
was written to prevent.

The consequence is recorded rather than hidden: **three documents describe
v0.1.0 and two of them now show v0.2.0 output.**
[`../release/v0.1.0-notes.md`](../release/v0.1.0-notes.md) is the published
release record, is not scanned by any test, and is deliberately unchanged — it
shows what v0.1.0 actually printed. If the launch drafts are ever used to
announce v0.1.0 specifically, their console blocks no longer match that release
and must be taken from the v0.1.0 notes instead.

## What this audit does not cover

Prose in launch copy is still unasserted for tone and framing —
`launch/README.md` carries the banned-phrase list and the list of claims that
are and are not safe to make. Only the console blocks are mechanically checked.
