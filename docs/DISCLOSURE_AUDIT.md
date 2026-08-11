# Disclosure audit

This repository is a **sanitised export**. It was written for publication
alongside a private research repository that is not published and is not
required by anything here.

This file records what was checked before that export was considered
releasable, and what was deliberately left out. It is published because a
project that asks you to trust its verification claims should show its own
work.

Audited: 11 August 2026, against the state at the second commit.

## What was scanned

Every file in the repository, excluding `.venv/` and `.git/`.

| Check | Result |
|---|---|
| API keys, tokens, private keys, credential-shaped strings | none found |
| Local filesystem paths (`/Users/…`, `/home/…`, `C:\…`) | none found |
| Machine hostnames or usernames | none found |
| Email addresses | one found, removed |
| Personal data | none beyond deliberate creator credit |
| Private repository commit identifiers | none found |
| Private research vocabulary | one instance found, rewritten |
| Vendor proprietary text, prompts, or branding assets | none |
| Dangling references to files outside this repository | none |
| Dangling relative links in documentation | none |
| Repository history predating this export | none — history begins here |

## What was removed or changed

Three findings, all fixed before the first release candidate was considered
complete:

1. **A personal email address** appeared in `NOTICE`, in a sentence
   establishing git authorship of the private repository. The claim was kept;
   the address was removed. Creator credit does not require contact details.

2. **Internal programme vocabulary** appeared in
   [`ROADMAP_REAL_MODEL.md`](ROADMAP_REAL_MODEL.md) — terms describing the
   private authorisation apparatus that leak its structure without informing a
   public reader. Rewritten in public-legible language with the same meaning.

3. **A real first name** appeared as an agent identifier in an example
   artifact. Replaced with a role name.

## What is deliberately excluded

The following exist in the private research repository and are **not** in this
export. This is a design decision, not an oversight.

| Excluded | Why |
|---|---|
| Frozen protected prompt content | sealed material; not opened during this export |
| Authorisation lifecycle artifacts, ordinals, custody receipts | governance apparatus of a private programme, meaningless and misleading in public |
| Held-out experimental content | would compromise a future evaluation |
| Sealed condition maps, randomisation receipts, case packs | same |
| Stage-specific governance documents (~120 files) | internal process records with no public claim resting on them |
| The frozen experimental runtime and its fixtures | the public lab is written fresh against the public contract |
| Raw experimental receipts and freeze-hash ledgers | not needed to reproduce any public claim |
| Machine-specific bootstrap, vendored wheels, dependency locks | environment-specific and not reproducible elsewhere |
| Unrelated project history | not this project |

## The reproducibility consequence

**Every public claim in this repository reproduces without the private one.**

Table 1 of [`RESULTS.md`](RESULTS.md) is produced by `babelci lab` on your
machine. Table 2 cites private findings as *provenance for design decisions*
and is explicitly marked as not reproducible here. If Table 2 were deleted
entirely, no public claim would lose its support.

Verified from a fresh `git clone --depth 1` into a temporary directory, with a
new virtual environment and outbound network denied at the sandbox level:

```
108 tests                          passed
babelci lab                        15/15 at declared layers
babelci demo                       ran
action/test-local.sh               8 passed, 0 failed
integrations/generic/run.sh        completed
lab digest, two runs, two trees    byte-identical
```

## What this audit does not establish

- It does not establish that the code is free of defects. It is a disclosure
  audit, not a code audit.
- It was performed by the same party that wrote the export. No independent
  review has taken place.
- Automated scanning finds patterns. A disclosure that does not match a pattern
  would not have been found, and reporting one is welcome — see
  [../SECURITY.md](../SECURITY.md).
