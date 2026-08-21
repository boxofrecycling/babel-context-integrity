# X / Twitter thread

Eight posts. Nothing has been posted.

---

**1/**

Git checks your code.

Nothing checks what your next agent thinks happened.

When an agent runs out of context and hands off, the successor inherits a
summary. Constraints live in that summary. They can quietly stop living there.

I built a verifier for that. 🧵

---

**2/**

The handoff gets a contract — a small JSON document recording what the
predecessor claims happened and, separately, what must survive.

Then eight checks, reported separately and never averaged into a score:

structure · identity · checkpoint · provenance · constraints · conflicts ·
authority agreement · external truth

---

**3/**

[screenshot: clean PASS, all eight lines]

A clean handoff. Note the last line:

    external truth ........ not established

Nothing outside the artifact was consulted, so the tool says so instead of
showing you a green tick.

---

**4/**

[screenshot: constraint-dropped FAIL]

Now the successor drops one MUST constraint — the one that said don't drop the
legacy session table yet.

The prose summary still reads fine. The contract doesn't.

Exit 1. CI goes red.

---

**5/**

Here's the part I actually care about.

I built a case where the agent scanned the wrong branch. Every fact it recorded
is wrong.

It passes all seven internal layers. Both independent encoders agree.
Commitments recompute. Provenance connects.

[screenshot: common-mode]

---

**6/**

Only a receipt issued *outside* the artifact rejects it.

Which means trust got relocated, not removed — and that's a limitation, not a
feature. Two encoders reading the same artifact can agree perfectly about a
story that never happened.

Agreement is not truth.

---

**7/**

Honest scoping, because this space is crowded:

structured agent handoffs aren't new. CLAN is a handoff format with checksums,
schema and provenance. The agent-handoff GitHub topic has 20+ projects.

And: no language model produced any result here. The lab agents are
deterministic fixtures.

Development is a separate question — parts of this were written with AI
assistance. That's evidence of nothing. The claims rest on rebuildable
artifacts and runnable tests.

---

**8/**

    pip install babel-context-integrity
    babelci demo

60 seconds. Zero dependencies. No network — enforced by a test that parses
every import, and a CI job that firewalls outbound traffic.

Apache-2.0. The limits doc is the one to read first.

[link]

---

## Notes

- Posts 3, 4 and 5 need screenshots. Use `NO_COLOR=` unset so PASS/FAIL are
  coloured; crop to the terminal, no window chrome.
- Post 5 is the one that gets quoted. Make that screenshot the cleanest.
- Do not thread a "if you found this useful" post on the end.
