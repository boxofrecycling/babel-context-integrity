# Demo video — 45–75 second terminal script

No production. One terminal, no cuts, no music, no face. The output is the
content.

**Nothing has been recorded.** This is the plan.

## Setup

```bash
# 100 columns, 30 rows, large readable font, dark background
printf '\033[8;30;100t'
export NO_COLOR=          # keep colour: PASS green, FAIL red carries the story
export PS1='$ '
clear

# Deterministic fixtures, so the recording can be repeated exactly
babelci lab --out /tmp/demo >/dev/null
cd /tmp/demo
```

Every command below is real and produces the output shown. Nothing is staged.

## Script

### 0:00–0:06 — the premise

Type, do not run:

```
# Your agent hands work to the next agent.
# It also hands over a story about what happened.
```

*(No voiceover needed. If there is one: "Git checks your code. Nothing checks
what your next agent thinks happened.")*

### 0:06–0:18 — a clean handoff passes

```bash
babelci verify clean.json --expect expect.json
```

Let the eight-line block sit on screen for three full seconds.

If narrating: *"Eight checks, reported separately. Note the last line."*

### 0:18–0:22 — point at `not established`

No command. Just let the viewer read:

```
external truth ........ not established
```

*"Nothing outside the artifact was consulted, so it says so."*

### 0:22–0:38 — break one thing

```bash
babelci verify constraint-dropped.json --expect expect.json
```

The failure block:

```
retained constraints .. FAILED

  RETAINED_CONSTRAINT_MISSING
    constraint 'C1' was required to survive this handoff and is absent
```

*"One constraint stopped being carried. The prose summary still reads fine."*

Optional, if the pacing allows — show that the summary is unchanged:

```bash
jq -r .summary.text constraint-dropped.json
```

### 0:38–0:44 — restore

```bash
babelci verify restart-resume.json --expect expect.json
```

Back to PASS. *"Fixed."*

### 0:44–1:05 — the turn

```bash
babelci verify common-mode.json --expect expect.json
```

Let it render fully. Seven `verified`, then `external truth ... FAILED`.

*"This one passes every internal check. Both independent encoders agree. The
commitments recompute. The provenance connects."*

Beat.

*"It describes a branch nobody worked on. Only the receipt from outside the
artifact catches it."*

### 1:05–1:10 — the line

Type, do not run:

```
# Agreement is not truth.
```

Hold four seconds. End.

## Total

~70 seconds. If it must be 45, cut the restore step (0:38–0:44) and the
optional `jq`.

## Recording

```bash
# asciinema keeps it text, small, and copy-pasteable — preferred
asciinema rec babel-demo.cast --cols 100 --rows 30 --idle-time-limit 1.5

# or a GIF, if a GIF is required
agg babel-demo.cast babel-demo.gif --font-size 20 --theme asciinema
```

Prefer asciinema: a viewer can select the text, and it makes the point that
this is a terminal tool rather than a screencast of a dashboard.

## Repeatability

Fixtures come from `babelci lab --out`, which is deterministic — the same
artifacts, byte for byte, on any machine. A retake produces identical output.
Verify before recording:

```bash
babelci lab --json | shasum -a 256
```

## Rules

- No speed-ups. If it is slow, it is slow; it is not.
- No zoom effects, no highlight boxes, no captions over the terminal.
- Do not cut between the seven `verified` lines and the `FAILED` line in the
  last act. The whole point is that the viewer reads them together.
- Do not add a call to action at the end. `Agreement is not truth.` is the
  ending.
