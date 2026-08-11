# The real-model evaluation: designed, not authorised, not run

## Current status

**No language model has been contacted anywhere in this project or in the
private research it derives from.**

That is a verified statement, not an aspiration. The private closeout
reproduction reports `network/model contact: PASS 0 attempts`, and the public
package is checked by `tests/test_no_contact.py`, which fails if any module so
much as imports `socket`.

The private programme's recorded decision is:

```
SOFTWARE_FRONTIER_CLOSED_AND_PARKED
Real-model execution readiness: NO AUTHORIZATION
```

Publishing this repository does not change that, and nothing here should be
read as changing it.

## Why this is the strongest next step

Everything demonstrated so far is about a *contract* and a *verifier*. The
scripted fixtures establish that the apparatus behaves as specified. They
establish nothing about the phenomenon the project is named after: whether real
agents, handing real work to each other, actually lose the things Babel checks
for — and if so, which ones, how often, and at what point in a run.

The honest description is that Babel currently answers *"can this be checked?"*
and has not attempted *"does this happen?"*

Nothing in the public claims depends on the second question. But it is the
question that would make the first one matter.

## Proposed design

Public-safe, category-level, deliberately omitting the frozen private
authorization material.

### Question

When a real coding agent hands work to a successor, which parts of the handoff
contract fail to survive, and does an enforced contract change the successor's
behaviour?

### Shape

A three-arm comparison over the same task set:

| Arm | Predecessor writes | Successor receives |
|---|---|---|
| **A. baseline** | free-form prose summary | the prose |
| **B. contract** | a Babel handoff artifact | the artifact's structured briefing |
| **C. enforced** | a Babel handoff artifact | the briefing, and `verify --expect` gates the handoff |

### Primary measures

- **survival rate** per contract element (constraint, decision, unresolved
  issue, provenance edge) across a handoff boundary;
- **violation rate**: how often a successor breaks a `MUST` constraint the
  predecessor recorded, by arm;
- **rediscovery cost**: successor tokens and tool calls spent re-establishing
  what the predecessor already knew, by arm;
- **verifier yield**: what fraction of real failures the contract catches, and
  at which layer.

### The measurement that matters most

**How often does a handoff pass every internal layer and still describe the
wrong world?** That is the `common-mode` case in the lab, constructed by hand.
Its real-world rate is unknown, and it is the number that would tell you
whether the external-truth layer is a footnote or the main event.

Measuring it needs a ground-truth oracle independent of both agents — the
repository state itself, for a task where correctness is mechanically
checkable.

### Controls the design would need

- task order randomised; handoff points fixed in advance, not chosen post hoc;
- the successor blind to which arm it is in;
- prompts and rubrics frozen and hashed before any run;
- no retry on failure, and failed runs reported rather than discarded;
- a pre-registered analysis plan, so the arm comparison cannot be chosen after
  seeing results;
- an explicit list of claims the study *cannot* unlock regardless of outcome.

### What it could and could not establish

**Could:** survival rates and violation rates for the tested models, tasks and
handoff points; whether an enforced contract reduces violations; the real
frequency of coherent-but-wrong handoffs in that setting.

**Could not:** anything about untested models or task families; any general
claim about agent memory or context compression; any claim that Babel prevents
errors rather than detecting a specific class of them; any claim that the
contract is complete.

## What authorisation would require

The private programme records that a real-model stage needs a fresh, explicit
human authorisation binding, before any prompt is opened or submitted:

1. the exact authority object and frozen repository identity;
2. the exact environment, dependency and no-retry requirements;
3. the exact model, provider, version, interface and role identities;
4. confirmation that the pre-registered materials are still sealed and that no
   held-out content has been read;
5. one-shot submission and capture behaviour, with custody receipts;
6. stop conditions for identity drift, prompt mismatch, transport failure,
   ambiguous output, custody loss, or any unexpected retry;
7. the narrow claims the observation could unlock;
8. the claims it cannot unlock — including universal communication,
   independence, hidden state, compression thresholds, or general model rank.

None of that has been supplied, and preparing this repository did not open,
consume, or advance any of it.

## For the reader

If you are evaluating Babel: judge it on the public lab, which reproduces on
your machine in under a second. The real-model study is the *proposed* next
step, and treating it as a completed result would be exactly the sort of
overclaim this project is built to catch.

If you want to run something like it: the design above is deliberately
publishable. Independent replication would be more valuable than another
in-house run.
