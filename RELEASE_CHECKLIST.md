# Release checklists

## v0.2.0 — published 2026-08-21

Tag `v0.2.0` → `1275294cc6aec83e8f55c552c736b8508122733c`. GitHub release and
PyPI publication both complete and verified; see **Published** below for the
evidence each item rests on.

### Prepared

- [x] `CHANGELOG.md` — 0.2.0 entry with migration, compatibility, limitations
- [x] `release/v0.2.0-notes.md` — GitHub release body
- [x] `docs/COMPATIBILITY.md` — contract vs report compatibility
- [x] Version bumped to `0.2.0`: `pyproject.toml`, `src/babelci/__init__.py`,
      `CITATION.cff`, `action/action.yml` default pin, docs pin examples
- [x] `action@v0.2.0` references updated in `README.md` and `docs/CI.md`.
      These resolve once the tag exists, same as `@v0.1.0` did before its tag.
- [x] 142 tests pass; `babelci lab` 15/15; `action/test-local.sh` 11/11
- [x] Claim audit re-run against `docs/LIMITS.md` for the four new visible
      surfaces — `SILENCE_UNATTESTED`, `PROVENANCE_ROOT_MISMATCH`, the coverage
      census, `babelci carry` — recorded in `docs/CLAIM_AUDIT.md`. All clean;
      two things stated rather than fixed, both noted there.
- [x] Disclosed: the v0.2.0 reporting changes regenerated the console blocks in
      `launch/github-release.md` and `launch/show-hn.md`, which are v0.1.0
      drafts. `test_launch_copy_console_output_matches_the_real_command`
      requires it. `release/v0.1.0-notes.md` is deliberately unchanged.
      Reasoning in `docs/CLAIM_AUDIT.md`.

### Published

- [x] Release text reviewed; five accuracy findings (R1–R5) raised and resolved
      before the tag. One further finding — the unbounded "no language model was
      involved in any of this" in three unpublished launch drafts — was found in
      pre-push review and narrowed to the results claim it supports.
- [x] Merged to `main`, fast-forward, matching the repository's linear history.
- [x] Built and digests recorded. `release/DIGESTS.txt` gains a v0.2.0 section
      above the preserved v0.1.0 record. Bit-reproducible across three builds
      (twice from the tree, once from a fresh clone) and again on a CI runner
      rebuilding from the tag. `twine check` passed both artifacts.
- [x] Disclosure scan on the working tree **and** both archives, at the released
      commit, recorded in `docs/DISCLOSURE_AUDIT.md`. Clean; one placeholder
      email in the landing-page form, present in no archive.
- [x] `git tag -a v0.2.0`, pushed `main` then the tag, then
      `gh release create v0.2.0 --notes-file release/v0.2.0-notes.md` with both
      artifacts attached. The release body is byte-identical to the notes file.
- [x] Published to PyPI. **TestPyPI was not used and could not be**: this project
      holds no API token by design and the Trusted Publishing workflow has no
      TestPyPI target, so `twine upload --repository testpypi` — inherited from
      the v0.1.0 sequence below, written before that workflow existed — is not a
      runnable step. The workflow's own `dry-run: true` was run first instead: it
      re-established three-way byte equality, passed `twine check`, and smoke-
      tested the wheel in a `--network=none` container, stopping before upload.
      The real run then uploaded via Trusted Publishing, `200 OK` for both files.
- [x] Verified from the index: `pip install babel-context-integrity` into a clean
      venv resolves 0.2.0, `babelci --version` reports 0.2.0, `babelci lab`
      exits 0 with the expected digest, and PyPI's recorded sha256 for both files
      matches `release/DIGESTS.txt`.

### Still open

- [ ] Decide whether 0.2.0 warrants any announcement. It is a point release; the
      `launch/` drafts were written for v0.1.0, and their provenance wording was
      corrected during this release, so they need rereading before any use.
- [ ] Update the stale `twine upload --repository testpypi` lines in the v0.1.0
      publication sequence below, which no longer describe how this project
      publishes. Left in place here as the historical record of that release.

---

# Release checklist — v0.1.0

Everything above the line is done. Everything below it needs a human, and
nothing below it has been done.

---

## Frozen and verified

- [x] `docs/LIMITS.md` is the claim boundary; every visible surface audited
      against it (`docs/CLAIM_AUDIT.md`)
- [x] 115 tests pass, including README and landing-page output fidelity, and no-network
      enforcement
- [x] `babelci lab` — 15/15 cases at their declared layer
- [x] `action/test-local.sh` — 11/11 without GitHub, including annotations
- [x] `sdist` and `wheel` build, inspected, installed clean, digests recorded
      (`release/DIGESTS.txt`)
- [x] Disclosure scan on the working tree **and** on both archives
      (`docs/DISCLOSURE_AUDIT.md`)
- [x] Fresh-clone gate with outbound network denied; lab digest matches
- [x] No URL points at a repository that does not exist (enforced by test)
- [x] Private research repository untouched

## Needs a human before publication

### 1. Copyright line — RESOLVED

**Decision: keep `Copyright 2026 Scott Henry`.** Anthony Colasante is not added
as a copyright holder on the basis of project creator credit alone. Creator
credit remains `Scott Henry and Anthony Colasante` where truthful.

<details><summary>original decision text</summary>

#### Copyright line — decide

`LICENSE` and `NOTICE` say **Copyright 2026 Scott Henry**. Project creator
credit says **Scott Henry and Anthony Colasante**. These are deliberately
different: creator credit and copyright ownership are separate concepts, and
the evidence available supports only the narrower statement (129 of 129 commits
in the private research repository are authored by Scott Henry; the public
source was written for this export).

- [x] Resolved: no change. `LICENSE` and `NOTICE` keep the single holder.

</details>

### 2. Repository — DONE

- [x] Created: https://github.com/boxofrecycling/babel-context-integrity (public, account `boxofrecycling`).
- [x] `[project.urls]` populated in `pyproject.toml`.
- [x] `repository-code` and `url` populated in `CITATION.cff`.
- [x] `PLACEHOLDER_REPOSITORY_URL` replaced throughout `site/index.html`.
- [x] Private vulnerability reporting enabled; `SECURITY.md` points at the
      advisory form rather than a personal address.

### 3. Package name

- [ ] `babel-context-integrity` was free on PyPI at the time of the freeze. Not
      reserved. Confirm before publishing.
- [ ] Decide whether to reserve the name before or with the release.

### 4. The GitHub Action — DONE

- [x] Referenced as `boxofrecycling/babel-context-integrity/action@v0.1.0`,
      which is a supported `owner/repo/path@ref` form and resolves once the
      v0.1.0 tag exists. Not published to the Marketplace; that remains
      optional and is not required for the reference above to work.

### 5. Review

- [ ] Scott reads `docs/LIMITS.md` and agrees it is the boundary.
- [ ] Anthony Colasante reviews before publication, if that is wanted.
- [ ] Decide whether to record the demo (`launch/demo-video.md` has the script;
      fixtures are deterministic so retakes are identical).

### 6. Deliberately not doing

- [ ] Trademark on the full phrase — noted in `docs/COMMERCIAL_STRATEGY.md`, not
      filed.
- [ ] DOI / Zenodo — no DOI is claimed anywhere and none should be added until
      one exists.
- [ ] Waitlist backend — the form on the landing page collects nothing and says
      so.
- [ ] Real-model evaluation — designed, not authorised, not run.

---

## Publication sequence, once the decision is GO

Ordered so that each step is verifiable before the next becomes hard to undo.

```bash
# From the root of a clone of this repository.

# 1. Resolve the copyright decision (item 1) and commit it.

# 2. Point the metadata at the repository you are about to create.
#    pyproject.toml [project.urls], CITATION.cff repository-code,
#    site/index.html PLACEHOLDER_REPOSITORY_URL.

# 3. Prove it still holds together.
python -m pytest -q
babelci lab
./action/test-local.sh
rm -rf dist && python -m build && python -m twine check dist/*

# 4. Tag.
git tag -a v0.1.0 -m "Babel Context Integrity v0.1.0"

# 5. Create the remote and push. THIS IS THE FIRST IRREVERSIBLE STEP.
gh repo create <owner>/babel-context-integrity --public --source=. --push
git push origin v0.1.0

# 6. Release notes from release/v0.1.0-notes.md.
gh release create v0.1.0 --title "v0.1.0" --notes-file release/v0.1.0-notes.md

# 7. Publish the package. Test index first.
python -m twine upload --repository testpypi dist/*
#    install from TestPyPI into a clean venv and run `babelci demo`
python -m twine upload dist/*

# 8. Only then, the announcements in launch/. One at a time; be available to
#    reply for three hours after posting Show HN or do not post it.
```

Steps 1–4 are reversible. Step 5 onward is not.

## If something is wrong after publishing

- A defect in the verifier that makes it **accept** something it should refuse
  is the serious class. Yank the release, fix, re-release. See `SECURITY.md`.
- A wrong claim in the documentation is the second-most serious. Correct it in
  place and note the correction in `CHANGELOG.md`; do not quietly edit.
