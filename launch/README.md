# Launch package

The prepared copy for announcing Babel Context Integrity. The repository, the
v0.1.0 release and the `babel-context-integrity` package on PyPI are public;
these files are the text written to announce them.

This directory is not a record of which announcements were posted, or when.

**These drafts were written for v0.1.0, and their console blocks are kept
current rather than historical.** `test_docs.py` runs every `$ babelci` block in
this directory against the build in the working tree and requires it to match,
so a release that changes what the tool prints changes these files too — v0.2.0
did, adding the coverage census and the `conflicts` open-issue count. Prepared
copy that advertises output the tool no longer prints is the defect that test
was written to prevent, and these drafts are unpublished. If you announce v0.1.0
specifically, take the console blocks from `release/v0.1.0-notes.md`, which is
the release record and is deliberately not regenerated.

| File | For |
|---|---|
| [`github-release.md`](github-release.md) | the v0.1.0 release notes |
| [`show-hn.md`](show-hn.md) | Show HN title, body, and expected objections |
| [`x-thread.md`](x-thread.md) | an eight-post thread |
| [`reddit.md`](reddit.md) | r/programming, r/devops, r/LocalLLaMA variants |
| [`linkedin.md`](linkedin.md) | one post |
| [`demo-video.md`](demo-video.md) | a 45–75 second terminal script with exact commands |
| [`blog-post.md`](blog-post.md) | the long technical write-up |

## The hook

Every piece leads with the same real finding, because it is the only part of
this that is genuinely interesting:

> Multiple independent validators can agree on the same wrong world.
> Babel separates agreement from truth.

The product framing of the same thing:

> An agent handoff is a set of executable assumptions. Babel makes those
> assumptions explicit and checkable.

And the blunt version, for a title:

> Your agent handoff can pass every check and still be wrong.

Then it explains how Babel separates integrity from truth, and admits that the
separation is the *limitation* rather than the feature.

## Tone rules

- Technical, curious, evidence-first. Assume the reader has been burned by a
  tool that overclaimed.
- Lead with the negative result. It is more interesting than the positive one
  and it buys the credibility to state the positive one.
- Every number traces to a command the reader can run.
- Name the closest competitor (CLAN) before anyone else does.
- Say plainly that no model was involved.

## Words that must not appear

`revolutionary` · `solves AI memory` · `guarantees correctness` · `first ever` ·
`game-changing` · `eliminates hallucinations` · `10x` · `paradigm shift`

`tests/test_docs.py` blocks several of these in the repository docs. In this
directory only the console blocks are mechanically checked — the prose, its tone
and its framing are not, and that is what this list is for.

## Claims that are safe to make

- 15 deterministic failure classes, reproducible in under a second
- 8 verification layers reported separately
- zero runtime dependencies, zero network access, enforced by tests
- integrity machinery costs 32.3% of the example artifact — a measured number
- one constructed case passes seven layers and is still entirely wrong
- the wheel is bit-reproducible; rebuild it and compare the digest
- every console block in the README is real output, asserted by a test

## Claims that are not

- anything about how often this happens with real agents (unmeasured)
- anything about model behaviour (no model was contacted)
- that Babel detects hallucination (it does not)
- that Babel is the first structured agent handoff format (CLAN and ~20 others
  precede it)
- that the lab is a benchmark (it is a regression harness on one scenario)
