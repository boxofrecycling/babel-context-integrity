# Architecture

Roughly 1,500 lines of Python, no runtime dependencies, no I/O beyond reading
the files you name and writing what you asked for.

```
src/babelci/
  canonical.py     canonical JSON, digests, bit measurement
  contract.py      layer names, finding codes, verdicts -- no logic
  schema.py        native structural validator
  authorities.py   two independent world encoders
  verify.py        the eight layers
  diff.py          semantic drift + the rule table
  seal.py          fill in commitments a draft is missing
  render.py        human output
  cli.py           argument parsing, exit codes
  lab/
    cases.py       the scenario and its fifteen mutations
    run.py         the lab harness
    demo.py        the 60-second walkthrough
schema/            the normative JSON Schema
```

`contract.py` deliberately contains no logic. It exists so that a finding code
printed in a terminal can be grepped for in exactly one place, and so that the
documentation, the schema and the verifier cannot disagree about what a layer
is called.

## Two things implemented twice, on purpose

### The structural validator

`schema.py` is a hand-written validator. `schema/babel-handoff-0.1.schema.json`
is a JSON Schema. They specify the same shape.

The native one exists so the package has zero runtime dependencies and works in
a locked-down CI image. The JSON Schema exists so that tooling in any language
can validate artifacts without reimplementing anything.

Two implementations of one specification is precisely the setup where they
drift apart, so `tests/test_schema_parity.py` runs both against every lab
fixture and against twelve deliberately malformed artifacts and asserts they
reach the same decision. When they diverge, that test fails rather than one
silently winning.

### The world encoder

`authorities.py` contains two encoders that share nothing but their output
schema:

**Authority A** walks the artifact as a nested document, resolving aliases
through a dictionary — the way a person reading the JSON would.

**Authority B** shreds the artifact into flat, sorted relation tuples, then
reconstitutes the world by joining them — the way a database would.

Both must produce the same `world` object. Its digest is what commitments are
taken over.

This is not redundancy. It is the only mechanism by which a single
implementation can notice its own blind spot.

The concrete case: an alias table binds one short name to two different
targets. Authority A's dictionary keeps the last binding, silently, and reports
nothing — which is what nearly any hand-written parser would do. Authority B's
join keeps both and produces a different world. The disagreement is the
finding.

**No vote is taken.** When the encoders disagree, neither is declared correct.
The artifact is ambiguous, and reporting that is more useful than picking a
winner by coin flip.

This mirrors a private research result: a second, separately implemented
verifier matched all 80 of the first verifier's prior decisions *and* exposed
16 alias-structure acceptances the first had missed.

## The eight layers

```
handoff.json
   │
   ├─► structure         native validator; stops here if the shape is wrong
   ├─► identity          compared against an expectation, never interpreted
   ├─► checkpoint        recompute the commitment from the carried state
   ├─► provenance        graph walk to the authority root; alias injectivity
   ├─► constraints       survival vs the expectation; summary binding
   ├─► conflicts         equal-rank contradictions fail closed
   ├─► authorities       encode twice, compare, do not vote
   └─► external truth    an out-of-band receipt, or abstain
```

Ordering matters for reporting: the first failing layer is what `caught_at`
names in the lab. It does not short-circuit — every layer after the structural
one still runs, so a single verify shows you everything wrong at once.

Structure is the one exception. If the shape is wrong, deeper layers would be
indexing fields that may not exist, so verification stops and reports only what
it actually checked. An artifact missing `provenance` gets one layer in its
report, not eight with seven green ticks for checks that never ran.

## Failing closed

Two places where the tool refuses rather than resolving:

**Equal-rank conflicts.** Two objects with the same id and different values,
with no declared `supersedes`, produce `DUPLICATE_OBJECT_CONFLICT`. Picking one
by document order would be a coin flip wearing a suit.

**Authority disagreement.** No majority, no tiebreak, no preferred encoder.

Both mirror the private apparatus, which kept verifier disagreements preserved
rather than voting them away.

## The `not established` state

A layer that cannot run does not report success. `external truth` on an
artifact with no receipt is `not established`, and the tool says why.

This is the single most important design decision in the codebase. Everything
else Babel does is arithmetic; this is the part that stops the arithmetic from
being mistaken for a guarantee.

## Determinism

- no wall-clock time, no randomness, no environment reads that affect output
  (`NO_COLOR` affects only ANSI codes);
- all iteration over collections is explicitly sorted before hashing;
- the lab emits a `lab_digest` that is stable across runs and processes;
- `tests/test_cli.py::test_lab_exits_zero_and_is_reproducible` and the CI
  workflow both diff two consecutive runs.

## No contact, enforced

`tests/test_no_contact.py` does two things:

1. parses every module's AST and fails if any of them imports `socket`, `ssl`,
   `urllib`, `requests`, `httpx`, `subprocess`, `asyncio`, an LLM SDK, or
   anything else that could reach outside the process;
2. monkeypatches the socket layer to raise, then runs every CLI command.

It also asserts that no command writes a file unless you passed `--out` or
`--in-place`: no cache, no log, no telemetry.

The CI workflow additionally runs the whole suite with outbound traffic
rejected at the firewall.

## Extending it

Adding a check means:

1. a finding code in `contract.py`;
2. the check in the right layer of `verify.py`;
3. a lab case in `lab/cases.py` declaring its expected verdict *and layer*;
4. a test in `tests/test_verify.py`.

Adding a diff verdict means an entry in `diff.RULES` with a stated reason, then
`python tools/gen_docs.py`. `tests/test_docs.py` fails if the generated
documentation drifts from the table.

The rule that governs all of it: **no layer may claim more than it checks.**
