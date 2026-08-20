# CLI reference

```
babelci <command> [options]
```

The binary is `babelci`. `babel-verify` is an installed alias. Neither is
`babel` — that belongs to `@babel/cli` in JavaScript and to the `babel` i18n
package on PyPI.

## Global

| Flag | Effect |
|---|---|
| `--version` | print the version and exit |
| `--help` | usage; also available per subcommand |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | everything that ran, passed |
| `1` | a verification layer failed, or `diff` returned `REFUSE` |
| `2` | usage or input error — missing file, invalid JSON, unknown case |
| `3` | `diff --strict` returned `REVIEW` |

## Environment

| Variable | Effect |
|---|---|
| `NO_COLOR` | disable ANSI colour (any value) |
| `BABELCI_FORCE_COLOR` | force colour even when not a terminal |

Nothing else. There is no config file, no cache directory, no state, and no
telemetry.

---

## `babelci verify`

```
babelci verify HANDOFF.json [--expect EXPECT.json] [--json] [-v]
```

Run the eight verification layers. `HANDOFF.json` may be `-` for stdin.

Without `--expect`, only internal consistency is checked — the tool cannot know
what was *supposed* to survive. With it, the identity, checkpoint and retained
constraint layers gain teeth.

```console
$ babelci verify .babel/handoff.json --expect .babel/expect.json
PASS  .babel/handoff.json
  structure ............. verified   contract 0.1, 5 objects
  identity .............. verified   agent-a -> agent-b
  checkpoint ............ verified   cp-4412-01
  provenance ............ verified   5 objects to repo@a1b2c3d4
  retained constraints .. verified   2 MUST, 1 SHOULD
  conflicts ............. verified   none
  authority agreement ... verified   3 encodings agree
  external truth ........ not established
```

`-v` prints full expected/received values instead of truncating them, plus the
computed world digest and the encodings used.

`--json` emits the machine-readable result:

```json
{
  "schema": "babel-verify/0.1",
  "verdict": "PASS",
  "handoff_id": "...",
  "task_id": "...",
  "layers": [ { "layer": "...", "status": "...", "detail": "...", "findings": [] } ],
  "findings": [ { "code": "...", "severity": "...", "layer": "...",
                  "detail": "...", "expected": "...", "received": "..." } ],
  "computed": { "world_digest": "sha256:...", "encodings": [ ... ] }
}
```

`severity` is `fail` or `note`. Only `fail` affects the exit code.

## `babelci explain`

```
babelci explain HANDOFF.json [--expect EXPECT.json] [--json]
```

Same checks, different output: for each layer, what it establishes, what it
observed, and any findings. Use it when a `verify` failure is not
self-explanatory, or when deciding how much a passing result is worth.

## `babelci diff`

```
babelci diff OLD.json NEW.json [--strict] [--json] [-v]
```

Semantic drift between two artifacts. Compares the computed world plus the
contract fields the world omits — not the JSON text. Reordering fields or
re-serialising produces no changes.

Every change cites a rule from `babelci rules`. The overall verdict is the
worst individual verdict.

```console
$ babelci diff handoff-01.json handoff-02.json
REFUSE

  REFUSE
    decisions[D2]
      decision-reversed: choice changed under the same identifier

  SAFE
    checkpoint
      checkpoint-advanced: cp-4412-01 -> cp-4412-02
```

`-v` adds the rule's reasoning and the before/after values.
`--strict` makes `REVIEW` exit 3 instead of 0.

## `babelci carry`

```
babelci carry HANDOFF.json --checkpoint ID [--handoff-id ID]
                           [--producer AGENT] [--consumer AGENT]
                           [--summary TEXT]
```

Draft the successor of a handoff. The task, the provenance graph and its
authority root, the retained constraints, the decisions, the open issues, the
objects and the aliases carry forward verbatim; the checkpoint advances and
declares its predecessor as `parent_checkpoint_id`; the predecessor's consumer
becomes the successor's producer unless `--producer` says otherwise.

Continuity is the default because the alternative — retyping the constraints
every session — eventually retypes them wrong.

Three fields are deliberately **not** carried:

| Field | Why not |
|---|---|
| `authorities` | A commitment its producer computed over its own world. The successor's producer has computed nothing, so carrying one would invent authority data. The successor's authority layer reports `not established` until it declares its own. |
| `external_receipt` | An acceptance of the predecessor's world. Carrying it would launder an old acceptance onto new work. |
| `summary` | Prose asserting what is true *now*. Carried into a new checkpoint and resealed it becomes a fresh commitment to a stale claim. Write a new one with `--summary`. |

`carry` takes no view on what project facts should say and does not refresh
them. An authority root of `repo` stays `repo` — upgrading it to something
more precise would assert a grounding its producer never claimed.

The output is a draft: its checkpoint commitment is a placeholder, so pipe it
through `seal`.

```bash
babelci carry .babel/handoff.json --checkpoint cp-12 --consumer next-session \
  | babelci seal - > next.json
```

## `babelci seal`

```
babelci seal DRAFT.json [--in-place] [--declare-authority ID]
```

Compute the commitments a draft is missing: `checkpoint.state_digest` and,
when a summary is present, `summary.commitment`. Writes to stdout unless
`--in-place`.

`seal` does **not** add an `authorities` entry by default. An authority
commitment is meant to be a producer's own independent encoding; having the
verifier write its own encodings into the artifact and then check them would be
marking its own homework. `--declare-authority ID` records this build's
commitment under `ID` when you genuinely want that.

Sealing an artifact whose two encodings disagree is an error — the ambiguity has
to be fixed, not committed to.

## `babelci lab`

```
babelci lab [CASE] [--list] [--out DIR] [--json]
```

Run the fifteen-case failure lab. Each case declares its expected verdict and
the layer that should catch it; a case caught at the wrong layer fails the lab
even when the verdict matches.

`--out DIR` writes every generated fixture plus `expect.json` to `DIR`, which
is how the `examples/` directory is produced.

Exit 0 if every case behaved as declared, 1 otherwise.

## `babelci demo`

```
babelci demo
```

The 60-second walkthrough: a clean handoff passes, a corrupted one fails at a
named layer, and a handoff that passes every internal check is still wrong.

## `babelci schema`

```
babelci schema [--path]
```

Print the normative JSON Schema, or its path on disk.

## `babelci rules`

```
babelci rules [--json]
```

Print every diff rule with its verdict and the reason for it.

---

## Piping

`--json` output is a single JSON document on stdout; human output goes to
stdout too, and errors to stderr. Broken pipes exit 0, so
`babelci verify x --json | head` behaves.

```bash
# Which layer failed?
babelci verify h.json --json | jq -r '.layers[] | select(.status=="failed") | .layer'

# Every failing finding code across a directory of artifacts
for f in .babel/*.json; do
  babelci verify "$f" --json | jq -r --arg f "$f" \
    '.findings[] | select(.severity=="fail") | "\($f) \(.code)"'
done

# Refuse a merge on any REFUSE change
babelci diff old.json new.json --json | jq -e '.verdict != "REFUSE"'
```
