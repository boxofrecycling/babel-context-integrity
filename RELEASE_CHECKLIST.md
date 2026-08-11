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
