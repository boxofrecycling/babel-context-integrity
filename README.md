# Babel Context Integrity

**Verify what survives when one AI agent hands work to the next.**

Git checks your code. Babel checks what your next agent thinks happened.

When a coding agent runs out of context, gets interrupted, or hands off to
another agent, the successor inherits a *story* — a summary, a state file, a
compacted transcript. That story is where the constraints live. It is also
where they quietly stop living, and nothing in your toolchain notices.

Babel gives that story a contract, and checks it.

```console
$ babelci verify examples/clean-handoff.json

PASS  examples/clean-handoff.json
      7 verified · 1 not established
  structure ............. verified   contract 0.1, 4 objects
  identity .............. verified   agent-a -> agent-b
  checkpoint ............ verified   cp-4412-01
  provenance ............ verified   4 objects to repo@a1b2c3d4
  retained constraints .. verified   2 MUST, 1 SHOULD
  conflicts ............. verified   none, 1 open
  authority agreement ... verified   3 encodings agree
  external truth ........ not established
```

Now the successor drops one constraint — the one that said *don't drop the
legacy session table yet*. The prose summary still reads fine:

```console
$ babelci verify examples/corrupted-handoff.json --expect examples/expect.json

FAIL  examples/corrupted-handoff.json
      6 verified · 1 FAILED · 1 not established
  structure ............. verified   contract 0.1, 4 objects
  identity .............. verified   agent-b -> agent-c
  checkpoint ............ verified   cp-4412-02
  provenance ............ verified   4 objects to repo@a1b2c3d4
  retained constraints .. FAILED
  conflicts ............. verified   none, 1 open
  authority agreement ... verified   3 encodings agree
  external truth ........ not established

  RETAINED_CONSTRAINT_MISSING
    constraint 'C1' was required to survive this handoff and is absent
    expected: C1
    received: None
```

Exit code 1. Your CI check goes red.

```bash
pip install babel-context-integrity
babelci demo        # the whole thing in 60 seconds, offline
```

Python 3.10+. Zero dependencies, zero network, zero telemetry.

*(Both example files ship in this repository. Every console block in this README
is real output you can reproduce, and a test asserts it stays that way — in your
own project the conventional path is `.babel/handoff.json`.)*

---

## The part most tools skip

Look at the last line of both outputs: `external truth ... not established`.

Everything above it is *internal consistency*. Babel recomputed the
commitments, walked the provenance graph, and encoded the artifact twice with
two independent encoders that agreed. That is a real and useful result. It is
also not the same as the story being **true**.

The lab has a case that makes the difference concrete. An agent scanned the
wrong branch. Every fact it wrote down is wrong. Every check passes:

```console
$ babelci verify examples/common-mode-handoff.json

FAIL  examples/common-mode-handoff.json
      7 verified · 1 FAILED
  structure ............. verified   contract 0.1, 4 objects
  identity .............. verified   agent-b -> agent-c
  checkpoint ............ verified   cp-4412-02
  provenance ............ verified   4 objects to repo@a1b2c3d4
  retained constraints .. verified   2 MUST, 1 SHOULD
  conflicts ............. verified   none, 1 open
  authority agreement ... verified   3 encodings agree
  external truth ........ FAILED

  EXTERNAL_RECEIPT_REJECTED
    repository working tree at repo@a1b2c3d4 rejected this world
      - auth.provider is okta-oidc in the tree, not auth0-oidc
      - legacy.sessions counted 1843 rows, not 12
      - D1 contradicts the recorded provider
```

Seven layers of checking accept a handoff describing a branch nobody worked on.
Only a receipt issued *outside* the artifact catches it — and that receipt is
now the thing you have to trust.

To be precise about the scope: `babelci diff` against a *correct predecessor*
would also flag this one, because a recorded decision changed. But an agent
that scanned the wrong branch from the very first handoff has no correct
predecessor to compare against, and then nothing local catches it. The lab
asserts both halves of that.

**Agreement is not truth.** Babel is built to show you exactly where one stops
and the other begins, instead of collapsing them into a green tick.

---

## Install

Python 3.10+. No runtime dependencies. No network access. No telemetry.

```bash
pip install babel-context-integrity
```

From a checkout:

```bash
pip install -e ".[dev]"
```

[On PyPI](https://pypi.org/project/babel-context-integrity/). Published from
this repository with [PyPI Trusted
Publishing](https://docs.pypi.org/trusted-publishers/) — no API token exists,
and each release carries a signed attestation naming the workflow that built
it.

The command is `babelci` (`babel-verify` is an alias). It is not `babel` —
that name belongs to [@babel/cli](https://babeljs.io) in JavaScript and to the
[Babel](https://pypi.org/project/babel/) i18n library on PyPI, and shadowing
either would be rude and confusing.

## 60-second demo

```bash
babelci demo
```

Three acts: a clean handoff passes, a corrupted one fails at a named layer, and
a handoff that passes every internal check is still wrong. No network, no
model, no setup.

## Core concepts

A **handoff artifact** is a JSON document conforming to the
[Babel Handoff Contract v0.1](docs/HANDOFF_CONTRACT.md). It records what the
producing agent claims happened and what must survive into the next agent:

| Field | What it is for |
|---|---|
| `task`, `producer`, `consumer` | who is handing what to whom |
| `checkpoint` | a commitment binding the artifact to a point in the work |
| `objects` | typed assertions, each naming where it came from |
| `retained_constraints` | statements that must survive, `MUST` or `SHOULD` |
| `decisions` | choices the successor inherits rather than reopens |
| `unresolved` | known-open questions; silence here is a claim |
| `provenance` | how each assertion reaches the authority root |
| `aliases` | short names introduced by compaction |
| `summary` | the prose a successor actually reads, bound to the structure |
| `authorities` | independently computed commitments over the same world |
| `external_receipt` | an acceptance or rejection from outside the artifact |

Verification runs **eight layers**, reported separately and never averaged:

```
structure → identity → checkpoint → provenance → retained constraints
          → conflicts → authority agreement → external truth
```

Each layer ends in `verified`, `FAILED`, or `not established`. The third state
is the one that keeps the tool honest: an artifact with no external receipt is
not clean at that layer, it is *unexamined* there, and Babel says so.

Full detail: [docs/CONCEPTS.md](docs/CONCEPTS.md).

## Commands

```bash
babelci verify HANDOFF.json [--expect EXPECT.json] [--json] [-v]
babelci explain HANDOFF.json          # what each layer establishes, and found
babelci diff OLD.json NEW.json        # semantic drift, not a line diff
babelci carry OLD.json --checkpoint ID  # draft the successor
babelci seal DRAFT.json --in-place    # fill in the commitments
babelci lab [CASE] [--list] [--json]  # the 15-case failure lab
babelci demo                          # the walkthrough
babelci schema                        # the normative JSON Schema
babelci rules                         # why diff says SAFE/REVIEW/REFUSE
```

Exit codes: `0` pass, `1` fail or refuse, `2` usage error, `3` review (with
`diff --strict`). Full surface: [docs/CLI.md](docs/CLI.md). Every failure code
it can print is documented in
[docs/FINDING_CODES.md](docs/FINDING_CODES.md).

## Babel Diff

Two artifacts that serialise completely differently can describe the same
world. Two that differ by one character can describe incompatible ones. `diff`
compares the *semantic world*, then applies a fixed rule table:

```console
$ babelci diff examples/clean.json examples/common-mode.json

REFUSE

  REFUSE
    A recorded decision changed without declaring what it replaced.
      decisions[D1]
        was  "Use Okta as the OIDC provider."
        now  "Use Auth0 as the OIDC provider."

  REVIEW
    An object now asserts a different value.
      objects[auth.provider]    okta-oidc -> auth0-oidc
      objects[legacy.sessions]  1843 -> 12

  SAFE
    The checkpoint advanced from its declared parent.
      checkpoint  cp-4412-01 -> cp-4412-02
```

Every verdict comes from exactly one rule, and `babelci rules` prints all of
them with the reasoning. There is no scoring and no heuristic; a change with no
matching rule is reported as `REVIEW` under the rule `unclassified-change`,
because a human deciding beats a tool guessing.

Human output leads with what changed and shows the values. Rule ids are the
machine handle and appear in `--json` and under `-v`, which also prints the
reasoning behind each verdict.

Rules: [docs/DIFF_RULES.md](docs/DIFF_RULES.md).

## GitHub Action

```yaml
- uses: boxofrecycling/babel-context-integrity/action@v0.2.0
  with:
    handoff: .babel/handoff.json
    expect: .babel/expect.json
```

Failures block the check. No cloud account, no service, no token. The action is
a thin wrapper over the same CLI, and
[`action/test-local.sh`](action/test-local.sh) runs it locally so you can see it
pass and fail before you commit it. Details: [docs/CI.md](docs/CI.md).

## Integrations

Worked examples for [Claude Code](integrations/claude-code/),
[Codex](integrations/codex/), a
[generic coding agent](integrations/generic/), and a
[human handing work to an agent](integrations/human-to-agent/). Each shows the
same four steps: predecessor writes the handoff, Babel validates it, successor
consumes it, and either side can diff it later. None of them require a vendor
API — they are files and shell commands.

*These are examples of using Babel alongside those tools. No vendor has
endorsed, reviewed, or is affiliated with this project.*

## Lab results

`babelci lab` runs 15 cases generated from one clean handoff by one named
mutation each, so the difference between pass and fail is always a single edit
you can read.

| Case | Verdict | Caught at |
|---|---|---|
| `clean` | PASS | — |
| `restart-resume` | PASS | — |
| `constraint-dropped` | FAIL | retained constraints |
| `constraint-softened` | FAIL | retained constraints |
| `decision-reversed` | PASS | *(verify cannot see it; `diff` REFUSEs)* |
| `checkpoint-mismatch` | FAIL | checkpoint |
| `summary-drift` | FAIL | retained constraints |
| `provenance-break` | FAIL | provenance |
| `alias-collapse` | FAIL | provenance |
| `authority-disagreement` | FAIL | authority agreement |
| `compression-loss` | FAIL | retained constraints |
| `duplicate-conflict` | FAIL | conflicts |
| `stale-replay` | FAIL | checkpoint |
| `externally-confirmed` | PASS | — |
| `common-mode` | FAIL | **external truth only** |

Integrity machinery costs **7,064 of 21,848 bits (32.3%)** of the example
artifact. That is measured by the lab, not estimated.

`decision-reversed` is worth dwelling on: it is the one case that a
single-artifact verifier structurally *cannot* catch, because the reversal is
internally consistent. It takes the predecessor to see it. The lab asserts this
rather than glossing it.

Every case names the private research result it derives from. Full table with
commands and limits: [docs/RESULTS.md](docs/RESULTS.md).

## Limits

Read these before believing anything above.

- **Babel does not check whether text is true.** It checks whether a structured
  artifact satisfies a declared contract. Those are different problems and the
  tool never conflates them.
- **Agreement between encoders is not truth.** Two independent encodings can
  agree perfectly about a world that never existed. That is the `common-mode`
  case, and it is a limitation, not a feature.
- **The external receipt is a trust root, not a solution.** Babel moves trust
  somewhere you can name and audit. It does not remove it.
- **No result here involves a language model.** The lab agents are fixtures.
  The scenario is fictional. What is real is the verifier's behaviour on it.
- **Contract v0.1 is small on purpose** and will change. See
  [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

The full list, including what each verification layer is *not* entitled to
conclude: [docs/LIMITS.md](docs/LIMITS.md).

## Architecture

```
handoff.json ──► structure   (native validator + published JSON Schema)
             ──► identity    (compared, never interpreted)
             ──► checkpoint  (recomputed from the state carried)
             ──► provenance  (graph walk to the authority root)
             ──► constraints (survival + summary binding)
             ──► conflicts   (equal-rank contradictions fail closed)
             ──► authorities (two independent encoders, no vote)
             ──► external    (out-of-band receipt, or abstain)
```

Two things in this package are deliberately implemented twice: the structural
validator (native + JSON Schema) and the world encoder (document-tree +
relation-join). Both pairs are tested against each other. This is not
redundancy — it is the only way a single implementation can notice its own
blind spots, and the `authority-disagreement` lab case exists because it works.

More: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Research

Babel Context Integrity is the public, product-shaped part of a larger private
research programme on context handoff integrity. The technical report —
including the threat model, the full experimental apparatus, related work, and
an explicit "proof is not truth" limitation — is in
[paper/](paper/README.md).

The report states plainly what the private apparatus did and did not establish.
In particular: **no result in this project involves a real language model.**
Every agent is a deterministic fixture. A controlled real-model evaluation is
the proposed next step and is [designed but not
authorised](docs/ROADMAP_REAL_MODEL.md).

## Provenance of this repository

This is a sanitised export from a private research repository. What was scanned
before publication, what was removed, and what is deliberately excluded are all
recorded in [docs/DISCLOSURE_AUDIT.md](docs/DISCLOSURE_AUDIT.md). Every public
claim reproduces here without the private repository.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: new verification
rules need a lab case, new diff verdicts need a rule-table entry with stated
reasoning, and no change may make a layer claim more than it checks.

## License

[Apache-2.0](LICENSE). Zero runtime dependencies, so there is nothing to be
incompatible with. See [NOTICE](NOTICE) for the attribution split between code
copyright and project creator credit, and
[docs/COMMERCIAL_STRATEGY.md](docs/COMMERCIAL_STRATEGY.md) for the open-core
boundary — everything in this repository is and stays open source.

## Citation

See [CITATION.cff](CITATION.cff).

---

Created by **Scott Henry and Anthony Colasante**.
