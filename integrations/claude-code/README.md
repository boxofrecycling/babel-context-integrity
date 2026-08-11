# Claude Code

> Babel is not affiliated with, endorsed by, or reviewed by Anthropic. This is
> an example of using a general-purpose CLI alongside a tool that reads and
> writes files in your repository.

Claude Code compacts its context when the window fills, and sessions end. Both
are handoffs. This directory wires Babel into that boundary using only files
and hooks — no API, no plugin, no token.

## The shape

1. a `Stop` hook asks the session to write `.babel/handoff.json` before it ends;
2. `babelci verify` checks it against `.babel/expect.json`;
3. the next session reads the structured briefing rather than only the prose;
4. CI diffs consecutive handoffs and refuses silent reversals.

## 1. Ask for a handoff at the end of a session

Add to `.claude/settings.json` in your repository:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/integrations/claude-code/check-handoff.sh"
          }
        ]
      }
    ]
  }
}
```

[`check-handoff.sh`](check-handoff.sh) verifies `.babel/handoff.json` if one
exists and prints a reminder if it does not. It never blocks — a hook that
fails a session because a file is missing is a hook people delete.

## 2. Tell the session what to write

Add to your project `CLAUDE.md`:

```markdown
## Handing off

Before you finish, write `.babel/draft.json` following the Babel Handoff
Contract v0.1 (`babelci schema`), then run:

    babelci seal .babel/draft.json > .babel/handoff.json
    babelci verify .babel/handoff.json --expect .babel/expect.json

Record in `retained_constraints` anything the next session must not break, in
`decisions` anything already settled that should not be reopened, and in
`unresolved` anything still open. An empty `unresolved` list is a claim that
nothing is open — do not make it casually.
```

## 3. Brief the next session

```bash
./integrations/generic/read-handoff.sh .babel/handoff.json
```

Paste that at the start of the next session, or have `CLAUDE.md` reference it.
The constraints arrive as constraints rather than as a paragraph.

## 4. Refuse silent reversals in CI

```yaml
- uses: ./babel-action      # vendored; see ../../docs/CI.md
  with:
    handoff: .babel/handoff.json
    against: .babel/handoff-previous.json
    expect: .babel/expect.json
```

## What this does and does not buy you

It catches a *dropped or rewritten* constraint, a broken provenance chain, a
summary that no longer matches the recorded state, and a reversed decision.

It does not catch a session that never wrote the constraint down, or one that
wrote down something false. For the first, use `.babel/expect.json` — it is
committed by a human and lists what must survive regardless. For the second,
you need an external receipt; see
[../../docs/LIMITS.md](../../docs/LIMITS.md).
