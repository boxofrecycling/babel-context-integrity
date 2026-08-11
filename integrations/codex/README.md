# Codex

> Babel is not affiliated with, endorsed by, or reviewed by OpenAI. This is an
> example of using a general-purpose CLI alongside a tool that works in your
> repository.

The integration is the same four steps as
[the generic example](../generic/README.md); what differs is where the
instruction lives and when the check runs.

## 1. Put the instruction where the agent will read it

Codex reads `AGENTS.md`. Add:

```markdown
## Handing off

When you finish a task, or before a long run ends, write a Babel handoff:

1. write `.babel/draft.json` per the contract (`babelci schema` prints it);
2. run `babelci seal .babel/draft.json > .babel/handoff.json`;
3. run `babelci verify .babel/handoff.json --expect .babel/expect.json`;
4. if verification fails, fix the draft — do not edit the digests by hand.

Put in `retained_constraints` whatever the next run must not break, in
`decisions` whatever is settled, and in `unresolved` whatever is still open.
An empty `unresolved` list asserts that nothing is open.
```

## 2. Check it as part of the task

Because Codex runs shell commands, the check is just a command. Append to
whatever the task's verification step is:

```bash
babelci verify .babel/handoff.json --expect .babel/expect.json
```

A non-zero exit is a failed task, which is the behaviour you want: a run that
produced code but destroyed the handoff has not finished.

## 3. Resume from it

```bash
./integrations/generic/read-handoff.sh .babel/handoff.json
```

Give that to the next run as its opening context.

## 4. Diff consecutive runs

```bash
cp .babel/handoff.json .babel/handoff-previous.json   # before the next run
# ... run ...
babelci diff .babel/handoff-previous.json .babel/handoff.json
```

Exit 1 means a decision was reversed, a MUST constraint was dropped, or a
required object disappeared. Exit 0 means the drift was normal progress.

## Full loop

[`../generic/run.sh`](../generic/run.sh) demonstrates all four steps offline
with no agent involved, so you can see what the files look like before wiring
anything up.
