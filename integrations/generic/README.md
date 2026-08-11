# Generic coding agent

The pattern every other integration is a variation on. Four steps, no vendor
API, nothing but files and shell commands.

## 1. The predecessor writes a handoff

At the end of its run, the agent writes `.babel/handoff.json`. It does not need
to compute any digests — `babelci seal` does that:

```jsonc
// .babel/draft.json — what the agent writes
{
  "babel_handoff": "0.1",
  "handoff_id": "run-2026-08-11-a",
  "task": { "task_id": "PR-4412/migrate-auth-to-oidc" },
  "producer": { "agent": "my-agent", "run_id": "run-0001" },
  "consumer": { "agent": "next" },
  "checkpoint": { "checkpoint_id": "cp-01", "state_digest": "" },
  "objects": [
    { "object_id": "auth.provider", "kind": "fact", "value": "okta-oidc",
      "required": true, "provenance": "scan/config" }
  ],
  "retained_constraints": [
    { "constraint_id": "C1", "binding": "MUST",
      "statement": "Do not drop the legacy session table yet." }
  ],
  "decisions": [
    { "decision_id": "D1", "choice": "Use Okta as the OIDC provider." }
  ],
  "unresolved": [
    { "issue_id": "U1", "statement": "Rotation interval unagreed.",
      "blocking": true }
  ],
  "provenance": {
    "authority_root": "repo@a1b2c3d4",
    "edges": [["scan/config", "repo@a1b2c3d4"]]
  },
  "summary": { "text": "Migrated auth behind a flag...", "commitment": "" }
}
```

```bash
babelci seal .babel/draft.json > .babel/handoff.json
```

`seal` fills in `checkpoint.state_digest` and `summary.commitment`. It does
*not* write an `authorities` entry unless you ask — a verifier writing its own
independence claim into an artifact would be marking its own homework.

## 2. Babel validates it

```bash
babelci verify .babel/handoff.json --expect .babel/expect.json
```

In CI, the same thing via the action. See [../../docs/CI.md](../../docs/CI.md).

## 3. The successor consumes it

The successor reads the same file. The useful move is to read the *structured*
fields rather than only the prose, because the structured fields are the ones
that were checked:

```bash
# What must not be broken:
jq -r '.retained_constraints[] | select(.binding=="MUST") | "MUST: \(.statement)"' \
  .babel/handoff.json

# What has already been decided (do not reopen):
jq -r '.decisions[] | "DECIDED: \(.choice)"' .babel/handoff.json

# What is still open (this is your job):
jq -r '.unresolved[] | "OPEN: \(.statement)"' .babel/handoff.json
```

Put that output in the successor's opening prompt. The constraints arrive as
constraints, not as a paragraph the model may or may not weight correctly.

## 4. Either side can diff later

```bash
babelci diff .babel/handoff-01.json .babel/handoff-02.json
```

This is what catches the failure a single artifact cannot show: a decision that
was reversed without being declared. `verify` passes on both files; `diff`
refuses.

## Scripts in this directory

| File | What it does |
|---|---|
| [`write-handoff.sh`](write-handoff.sh) | build and seal a handoff from shell variables |
| [`read-handoff.sh`](read-handoff.sh) | print the successor briefing shown above |
| [`run.sh`](run.sh) | the whole four-step loop, end to end, offline |

```bash
./integrations/generic/run.sh
```

## What Babel does not do here

It does not run your agent, read your repository, or decide whether the facts
are right. Step 2 checks that the *artifact* satisfies the contract. Whether
`auth.provider` really is `okta-oidc` is a question for an external receipt —
see [../../docs/CONCEPTS.md](../../docs/CONCEPTS.md#external-truth-and-why-it-is-separate).
