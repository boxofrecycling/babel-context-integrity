"""Fill in the commitments a draft handoff is missing.

Producers should compute commitments themselves -- that is the point of a
commitment. ``babelci seal`` exists for the common case where the producer is
a coding agent writing JSON, and for building fixtures. It computes exactly the
recipes in :mod:`babelci.verify` and nothing else.

``seal`` deliberately does *not* write ``authorities`` entries by default. An
authority commitment is supposed to be a producer's own independent encoding of
the world; having the verifier write its own encodings into the artifact and
then check them would be a tool marking its own homework. ``--declare-authority``
is available for producers that genuinely want to record this build's encoding,
and it labels the entry with the encoding that produced it.
"""

from __future__ import annotations

import copy
from typing import Any

from . import authorities
from .canonical import DIGEST_PREFIX
from .verify import checkpoint_commitment, summary_commitment

PLACEHOLDER = DIGEST_PREFIX + "0" * 64


def seal(draft: dict[str, Any], *, declare_authority: str | None = None
         ) -> dict[str, Any]:
    """Return a copy of ``draft`` with all computable commitments filled in."""
    handoff = copy.deepcopy(draft)

    handoff.setdefault("babel_handoff", "0.1")
    checkpoint = handoff.setdefault("checkpoint", {})
    checkpoint.setdefault("checkpoint_id", "checkpoint-0")
    checkpoint["state_digest"] = PLACEHOLDER
    checkpoint["state_digest"] = checkpoint_commitment(handoff)

    if "summary" in handoff:
        computed = authorities.compute(handoff)
        if computed["world_digest"] is None:
            raise ValueError(
                "cannot seal a summary for an artifact whose two encodings "
                "disagree; fix the artifact first")
        handoff["summary"]["commitment"] = summary_commitment(
            handoff, computed["world_digest"])

    if declare_authority:
        computed = authorities.compute(handoff)
        if computed["world_digest"] is None:
            raise ValueError("cannot declare an authority for a disagreeing artifact")
        entries = handoff.setdefault("authorities", [])
        entries[:] = [entry for entry in entries
                      if entry["authority_id"] != declare_authority]
        entries.append({
            "authority_id": declare_authority,
            "encoding": authorities.ENCODING_A,
            "world_digest": computed["world_digest"],
        })
        entries.sort(key=lambda entry: entry["authority_id"])

    return handoff


def issue_receipt(handoff: dict[str, Any], *, receipt_id: str, trust_root: str,
                  accepted: bool, findings: list[str] | None = None
                  ) -> dict[str, Any]:
    """Build an external-truth receipt over the world this artifact encodes.

    This helper is for fixtures and for wiring a real out-of-band checker into
    the contract. It does not itself decide anything: the caller supplies
    ``accepted``, because whatever established it is the trust root, not Babel.
    """
    computed = authorities.compute(handoff)
    if computed["world_digest"] is None:
        raise ValueError("cannot issue a receipt for a disagreeing artifact")
    return {
        "receipt_id": receipt_id,
        "trust_root": trust_root,
        "accepted": accepted,
        "world_digest": computed["world_digest"],
        "findings": list(findings or []),
    }


__all__ = ["seal", "issue_receipt", "PLACEHOLDER"]
