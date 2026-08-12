# Show HN

## Title

Preferred:

```
Show HN: Babel – verify what survives when one AI agent hands work to the next
```

Alternates, leading with the negative result:

```
Show HN: Babel – multiple validators can agree on the same wrong world
Show HN: A handoff verifier that passes every check and is still wrong
```

The first is clearest about what it is; use it. The alternates are more
interesting but risk reading as a gimmick in a title, and the body carries that
argument anyway.

## Body

```
Git checks your code. Nothing checks what your next agent thinks happened.

When a coding agent runs out of context or hands off to another agent, the
successor inherits a summary. Constraints live in that summary — "don't drop
the legacy session table yet" — and they can quietly stop living there.
Nothing in a normal toolchain notices.

Babel gives the handoff a contract (a small JSON schema) and a verifier. The
verifier runs eight checks and reports each separately: structure, identity,
checkpoint binding, provenance connectivity, constraint survival, conflicts,
agreement between two independently implemented encoders, and acceptance by an
out-of-band receipt.

    $ babelci verify examples/corrupted-handoff.json --expect examples/expect.json

    FAIL  examples/corrupted-handoff.json
      structure ............. verified   contract 0.1, 4 objects
      identity .............. verified   agent-b -> agent-c
      checkpoint ............ verified   cp-4412-02
      provenance ............ verified   4 objects to repo@a1b2c3d4
      retained constraints .. FAILED
      conflicts ............. verified   none
      authority agreement ... verified   3 encodings agree
      external truth ........ not established

      RETAINED_CONSTRAINT_MISSING
        constraint 'C1' was required to survive this handoff and is absent
        expected: C1
        received: None

Exit 1, CI goes red. Both files ship in the repo, so that is a command you can
run against a fresh clone; in your own project the conventional path is
.babel/handoff.json.

The part I actually want to show you is the last line of that output.

Everything above "external truth" is internal consistency. I built a case where
an agent scanned the wrong branch: every fact it recorded is wrong, and it
passes all seven internal layers. Both independent encoders agree. Commitments
recompute. Provenance connects. The artifact is perfect and describes a branch
nobody worked on.

Only a receipt issued outside the artifact rejects it. Which means trust got
relocated, not removed — and the tool says so instead of showing you a green
tick.

That's why the layers are reported separately and never averaged, and why a
layer that couldn't run says "not established" rather than passing. An artifact
with no external receipt isn't clean at that layer; it's unexamined there.

    pip install babel-context-integrity
    babelci demo          # 60 seconds, no network, no model
    babelci lab           # 15 failure classes, each one named mutation

Zero runtime dependencies. No network access — that's enforced by a test that
parses every module's imports and by a CI job that runs the suite with outbound
traffic firewalled off. No telemetry, no config file, no daemon.

Honest scoping, since this space is crowded: structured agent handoffs are not
new. CLAN (github.com/saieeshward/clan) is a handoff file format with
checksums, a JSON Schema, provenance and a validate command, and the
`agent-handoff` GitHub topic already contains dozens of repositories. What I
haven't found elsewhere is the layer separation, the "not established" state,
two encoders with no tiebreak, and an external-truth layer that can reject what
everything else accepted.

Also honest: no language model was involved in any of this. The lab agents are
fixtures. What's real is the verifier's behaviour on them. A controlled
evaluation with real agent handoffs is designed and written up, and hasn't been
run.

Apache-2.0. Technical report, related-work review and limits doc in the repo.
The limits doc is the one I'd read first.
```

## Expected objections, and honest answers

**"This is just a JSON schema with extra steps."**
Structural validity is one of eight layers and it is the least interesting.
`babelci lab` includes seven cases that are structurally perfect and still
fail. Point at `common-mode`.

**"Why would an agent write a truthful handoff?"**
It often won't, and Babel does not fix that. That is exactly what the threat
model says: non-adversarial but unreliable producer. The expectation file
exists because the *repository*, not the agent, should decide what must
survive. Do not argue past this — concede it and point at SECURITY.md.

**"Agents should just write better summaries."**
Sure. The failure mode is that nobody notices when they stop. This is the same
argument as "developers should just write correct code", which is why we have
CI.

**"Isn't this what OpenTelemetry / the Agents SDK does?"**
Different boundary. The SDK validates a handoff payload in flight inside one
runtime; OTel describes what happened for observability. Babel checks a
persisted artifact after the fact, across runtimes, possibly days later, with
no trust in the tool that wrote it.

**"You said no model was involved — so what has this actually shown?"**
That the verifier behaves as specified on fifteen constructed failure classes,
and that internal consistency provably cannot distinguish a true handoff from a
coherent false one. Nothing about how often real agents fail. That is the next
study and it hasn't been run. Do not soften this.

**"32.3% overhead is a lot."**
It is. It is also measured and reported rather than hidden. The private
research this came from had a worse version: carrying full proofs cost more
than the context they were proving.

## Timing

Tuesday–Thursday, 8–10am ET. Be available to reply for the first three hours or
do not post.
