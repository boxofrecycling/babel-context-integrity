# Human → agent

The handoff nobody instruments: a person who has been carrying the context in
their head writes a paragraph, and an agent starts from it.

Everything that goes wrong in an agent-to-agent handoff goes wrong here too,
plus one more thing — the human never writes down the constraint they consider
obvious.

## Write the handoff first, prose second

The trick is to fill in the structured fields *before* writing the summary,
because the fields ask questions a paragraph lets you skip.

```bash
cp integrations/human-to-agent/template.json .babel/draft.json
$EDITOR .babel/draft.json
babelci seal .babel/draft.json > .babel/handoff.json
babelci verify .babel/handoff.json
```

The template is the contract with every field commented, so filling it in is a
checklist:

- **What must not break?** → `retained_constraints`, `MUST`
- **What have I already decided, so nobody relitigates it?** → `decisions`
- **What do I genuinely not know?** → `unresolved`
- **Where did each fact come from?** → `objects[].provenance`

That last one is the useful discipline. "The session count is 1843" is a
different claim from "the session count was 1843 when I ran the query on
Monday", and only one of them survives contact with a week of work.

## Then brief the agent

```bash
./integrations/generic/read-handoff.sh .babel/handoff.json
```

Paste the output as the opening context. The agent gets the constraints as
constraints.

## Then check what comes back

When the agent produces its own handoff:

```bash
babelci diff .babel/handoff.json .babel/handoff-agent.json
```

`REFUSE` means it reversed something you decided, or dropped something you
marked `MUST`. That is the review you would otherwise have to do by reading a
diff and remembering what you said on Monday.

## Files

| File | What it is |
|---|---|
| [`template.json`](template.json) | the contract as a fill-in-the-blanks checklist |
| [`example-filled.json`](example-filled.json) | the template completed, sealed, and verifying |
