# Disclosure audit

This repository is a **sanitised export**. It was written for publication
alongside a private research repository that is not published and is not
required by anything here.

This file records what was checked before that export was considered
releasable, and what was deliberately left out. It is published because a
project that asks you to trust its verification claims should show its own
work.

Audited twice: once against the release candidate, and again at the release
freeze against the final tree **and** against the built `sdist` and `wheel`,
which are separate surfaces — an archive can contain a file the working tree
scan skipped.

## What was scanned

Every file in the repository, excluding `.venv/` and `.git/`; then every file
inside `dist/*.tar.gz` and `dist/*.whl`, extracted and scanned independently.

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

## v0.2.0 — scanned 2026-08-21

Re-run at commit `1275294cc6aec83e8f55c552c736b8508122733c`, which tag `v0.2.0`
points at, against three surfaces: the working tree, the extracted `sdist`, and
the extracted `wheel`. The archives scanned were the exact bytes published —
sha256 `85439f40…` (wheel) and `358901005…` (sdist), matching
[`../release/DIGESTS.txt`](../release/DIGESTS.txt), the GitHub release assets
and the digests PyPI records.

Same checks as the v0.1.0 scan above, plus a pattern for PyPI API tokens
(`pypi-AgEI…`), added because this release was the first published through the
Trusted Publishing workflow and it was worth confirming no token had been
introduced anywhere. None exists; the workflow uses a short-lived OIDC token
and stores nothing.

| Check | Tree | sdist | wheel |
|---|---|---|---|
| API keys, tokens, private keys, PyPI tokens | none | none | none |
| Local filesystem paths (`/Users/…`, `/home/…`, `C:\…`) | none | none | none |
| Machine hostnames or usernames | none | none | none |
| Email addresses | one, below | none | none |
| Private research vocabulary or lane names | none | none | none |
| Private repository commit identifiers | none | none | none |

**The one match, and why it is not a finding.** `site/index.html` contains
`placeholder="you@company.com"` on the landing page's waitlist input. It is
placeholder text in a form that collects nothing, which the page itself states.
It is not in either archive.

Nothing was removed or changed as a result of this scan.

### What changed in v0.2.0 that this scan covers

Four externally visible surfaces were added since the v0.1.0 scan —
`SILENCE_UNATTESTED`, `PROVENANCE_ROOT_MISMATCH`, the coverage census and
`babelci carry` — along with a new module, a new test file, and regenerated
console blocks across the documentation and the unpublished launch drafts. All
are inside the tree scan; the module is inside both archives.
[`CLAIM_AUDIT.md`](CLAIM_AUDIT.md) covers the same four surfaces against
`LIMITS.md`, which is a different question from disclosure and is recorded
separately.

### Boundary of this scan

It was run on the same day as publication, by the same party that prepared the
release, using the pattern set above. It establishes that those patterns did not
match, and nothing more. The v0.1.0 caveats below apply unchanged.

## What this audit does not establish

- It does not establish that the code is free of defects. It is a disclosure
  audit, not a code audit.
- It was performed by the same party that wrote the export. No independent
  review has taken place.
- Automated scanning finds patterns. A disclosure that does not match a pattern
  would not have been found, and reporting one is welcome — see
  [../SECURITY.md](../SECURITY.md).
