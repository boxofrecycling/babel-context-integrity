# Commercial strategy

Written down so the boundary is a commitment rather than a mood. Nothing
described under "paid" exists today, and nothing here is a product
announcement.

## The rule

**The check stays free. Aggregation across checks is what could be sold.**

Anything a developer needs to verify one handoff, on one machine, in their own
CI, is open source under Apache-2.0 and stays that way. That is not a
marketing position; a verification tool that might one day withhold a check is
not trustworthy as a verification tool.

## Open source, permanently

| Component | Why it must stay open |
|---|---|
| `babelci` CLI — verify, explain, diff, seal, lab, demo | the product |
| The Handoff Contract and JSON Schema | a contract nobody can implement freely is not a contract |
| The dual-encoder verification core | the integrity claim is unauditable if the checker is closed |
| The lab and every fixture | claims must be reproducible by the reader |
| The GitHub Action and CI examples | the check has to run where the work happens |
| Agent integrations | adoption path |
| The technical report | it makes claims; claims need scrutiny |

A relicense of any row above would invalidate the reason to trust the tool. If
that ever looks tempting, this file is the argument against it.

## What could be paid, later

Every item below shares one property: **it requires state that spans more runs,
repositories, or people than a local CLI can see.** That is a real service with
real costs, and it is a different thing from checking a file.

| Candidate | The problem it would solve | Why local can't |
|---|---|---|
| **Hosted handoff history** | "when did constraint C1 stop being carried, and in which PR?" | needs durable storage across runs |
| **Signed team receipts** | an external receipt whose trust root is your org, not a local script | needs a key nobody on the team controls alone |
| **Cross-repository visibility** | one constraint enforced across 40 services | needs a view no single repo has |
| **Policy as code** | "no PR merges if a MUST constraint was dropped, org-wide" | needs org-level enforcement |
| **Team analytics** | which agents, tasks or handoff points lose the most | needs aggregation across many runs |
| **Managed verification** | a hosted external-truth issuer that checks claims against real repository state | needs to run outside the artifact |
| **Audit export** | evidence for a compliance review that constraints were enforced | needs immutability and retention |
| **Enterprise support** | SSO, procurement, SLAs, private contract extensions | needs people |

The strongest of these is **managed verification**, because it addresses the
one thing the open tool structurally cannot do. The external-truth layer is
where local checking stops, and an issuer that looks at your repository rather
than at the artifact is genuinely a service. It is also the one to be most
careful about: selling the external-truth issuer while giving away the checker
means selling the trust root, and it would need to be auditable and replaceable
or the honesty of the whole design erodes.

## Pricing hypotheses

Hypotheses. No pricing has been tested with anyone.

| Tier | Shape | Rationale |
|---|---|---|
| **Open source** | free, forever, unlimited | the check itself |
| **Team** | per-developer per-month, in the $10–25 range | history, dashboard, policy, cross-repo |
| **Enterprise** | annual, negotiated | SSO, retention, audit export, support, on-prem |

Deliberately rejected shapes:

- **per-verification pricing** — meters the thing that should be free, and
  penalises verifying more often, which is the behaviour worth encouraging;
- **open-core by crippled CLI** — withholding a check from the free tier makes
  the free tier untrustworthy and the paid tier unverifiable;
- **usage-based on artifact volume** — the incentive to write fewer handoffs is
  exactly wrong.

## Order of operations

1. **Adoption first.** Nobody buys handoff history before handoff artifacts
   exist in their repositories. The open tool has to be genuinely useful alone,
   which means the priority is integrations and the action, not a dashboard.
2. **Real-model evidence second.** The strongest commercial argument is a number
   from [the proposed evaluation](ROADMAP_REAL_MODEL.md): how often real
   handoffs actually drop what they promised. Without it the pitch is a
   plausible story.
3. **Hosted product third**, and only if teams are already committing
   `.babel/expect.json` and hitting the limits of a local check.

Building billing before step 1 would be building for an imaginary user.

## Trademark and naming

The name "Babel Context Integrity" and any logo would be held separately from
the code licence — the Apache-2.0 grant covers the software, not the name. A
fork can use the code; it should not claim to be this project. That is standard
practice and worth doing properly before, not after, adoption.

Note that "Babel" is heavily used in software (`@babel/cli`, the Python `babel`
i18n package), so a trademark claim on the bare word would be neither available
nor reasonable. The distinguishing form is the full phrase.

## What would make this strategy wrong

Written down so it can be checked later:

- if the external-truth issuer turns out to be trivially self-hostable, the
  managed-verification tier has no moat and the strategy should shift to
  history and policy;
- if teams do not adopt expectation files, none of the paid tiers have a hook,
  and the honest answer is that this is a good tool and not a business;
- if the real-model evaluation shows handoff loss is rare in practice, the
  commercial case weakens sharply and should be said out loud rather than
  buried.
