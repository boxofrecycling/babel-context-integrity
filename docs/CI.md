# Running Babel in CI

The pitch: your agent writes `.babel/handoff.json` when it finishes. CI checks
that the handoff still satisfies what the repository requires. If a constraint
stopped being carried, the check goes red before a human reads a summary that
no longer matches the code.

No cloud account, no service, no token. The action installs a PyPI package with
zero dependencies and runs a local CLI.

## Minimal workflow

```yaml
name: Handoff integrity
on: [pull_request]

jobs:
  babel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: boxofrecycling/babel-context-integrity/action@v0.1.0
        with:
          handoff: .babel/handoff.json
          expect: .babel/expect.json
```

## Also checking drift against the predecessor

Some failures are invisible in a single artifact. A decision that gets reversed
produces a perfectly consistent handoff; only comparing it to the previous one
shows the reversal. Supply `against:` to run `babelci diff` as well.

```yaml
      - uses: boxofrecycling/babel-context-integrity/action@v0.1.0
        with:
          handoff: .babel/handoff.json
          against: .babel/handoff-previous.json
          expect: .babel/expect.json
          strict: "true"      # a REVIEW verdict also fails
          json-report: babel-report.json
```

## Inputs

| Input | Default | Meaning |
|---|---|---|
| `handoff` | `.babel/handoff.json` | artifact to verify |
| `expect` | *(none)* | expectation file it must satisfy |
| `against` | *(none)* | predecessor artifact to diff against |
| `strict` | `false` | treat a diff `REVIEW` as a failure |
| `json-report` | *(none)* | write machine-readable results here |
| `version` | `babel-context-integrity==0.1.0` | pin the CLI version |

## Outputs

| Output | Values |
|---|---|
| `verdict` | `PASS`, `FAIL` |
| `diff-verdict` | `SAFE`, `REVIEW`, `REFUSE` (only when `against` is set) |

## Exit codes

The action fails the check on any non-zero exit:

| Code | Cause |
|---|---|
| 0 | verify passed, and diff was `SAFE` (or `REVIEW` without `strict`) |
| 1 | a verification layer failed, or diff returned `REFUSE` |
| 2 | usage or input error — missing file, invalid JSON |
| 3 | diff returned `REVIEW` with `strict: "true"` |

## Testing the action without GitHub

```bash
./action/test-local.sh
```

The action is a wrapper over the CLI, so it can be run directly by setting the
same environment variables Actions would set. `test-local.sh` does that across
eleven scenarios and asserts the exit codes, the annotations and the summary:

```
ok    clean handoff passes                           exit 0
ok    dropped MUST constraint fails                  exit 1
ok    rejected external receipt fails                exit 1
ok    missing artifact fails                         exit 1
ok    normal progress diffs SAFE                     exit 0
ok    silent reversal diffs REFUSE                   exit 1
ok    strict mode still passes SAFE                  exit 0
ok    json report                                    written
ok    error annotations                              2 emitted
ok    no spurious annotations                        none on success
ok    step summary                                   names the failure

11 passed, 0 failed
```

## What a failure looks like on the pull request

Every failing finding is emitted as a GitHub `::error` annotation against the
handoff file, so it appears inline on the PR rather than only in the log:

```
Babel: RETAINED_CONSTRAINT_MISSING
  constraint 'C1' was required to survive this handoff and is absent
  expected: C1
  received: None
```

`diff` verdicts annotate too — `REFUSE` as an error, `REVIEW` as a warning.

The step summary at the top of the run names the layers that failed, the
finding codes, and the exact commands to reproduce it locally:

```markdown
### Babel Context Integrity

- **verify: FAIL** — `.babel/handoff.json`
  - `retained constraints` failed
    - `RETAINED_CONSTRAINT_MISSING` — constraint 'C1' was required to survive
      this handoff and is absent
- **diff vs `.babel/handoff-previous.json`: REFUSE**

Reproduce locally:

    babelci verify .babel/handoff.json --expect .babel/expect.json
    babelci diff .babel/handoff-previous.json .babel/handoff.json
```

A passing handoff produces no annotations at all.

If you want to run it in a container, `docker run --network=none` works — the
CLI never needs the network after install.

## Other CI systems

There is nothing GitHub-specific in the tool. Anywhere you can run a command:

```bash
pip install babel-context-integrity==0.1.0
babelci verify .babel/handoff.json --expect .babel/expect.json
```

GitLab:

```yaml
handoff-integrity:
  image: python:3.12-slim
  script:
    - pip install babel-context-integrity==0.1.0
    - babelci verify .babel/handoff.json --expect .babel/expect.json
```

A pre-commit hook, if you want the check before the push rather than after:

```yaml
- repo: local
  hooks:
    - id: babel-verify
      name: babel verify handoff
      entry: babelci verify .babel/handoff.json --expect .babel/expect.json
      language: system
      files: ^\.babel/
      pass_filenames: false
```

## Where the expectation file comes from

`.babel/expect.json` is committed to the repository by a **human**, not written
by the agent being checked. That asymmetry is the point: an agent that omits a
constraint has produced a smaller, entirely valid artifact. The expectation is
how the repository decides what must survive regardless.

Generate a starting point from a handoff you trust:

```bash
babelci lab --out /tmp/babel-example
cp /tmp/babel-example/expect.json .babel/expect.json
```

then edit it to name your task, your authority root, and the constraints that
actually matter to you.
