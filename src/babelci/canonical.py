"""Canonical serialisation and digests.

Every commitment in the Babel Handoff Contract is a SHA-256 over a canonical
JSON encoding. The encoding is deliberately boring and fully specified so that
an independent implementation in another language can reproduce it:

* UTF-8 output, but ``ensure_ascii`` so the byte stream is pure ASCII;
* object keys sorted by Unicode code point;
* no insignificant whitespace (``,`` and ``:`` separators);
* ``NaN``/``Infinity`` rejected;
* integers and floats serialised by Python's ``json`` rules.

Digests are prefixed with ``sha256:`` in artifacts so the algorithm is visible
at the point of use rather than implied.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

DIGEST_PREFIX = "sha256:"


def canonical_bytes(value: Any) -> bytes:
    """Return the canonical ASCII byte encoding of ``value``."""
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def digest(value: Any, *, domain: bytes = b"") -> str:
    """Return the prefixed SHA-256 commitment over ``value``.

    ``domain`` is an optional domain-separation tag mixed in ahead of the
    payload so that commitments computed for different purposes over the same
    structure cannot be confused with one another.
    """
    return DIGEST_PREFIX + hashlib.sha256(domain + canonical_bytes(value)).hexdigest()


def is_digest(value: Any) -> bool:
    """True when ``value`` is a syntactically well-formed commitment string."""
    if not isinstance(value, str) or not value.startswith(DIGEST_PREFIX):
        return False
    body = value[len(DIGEST_PREFIX):]
    return len(body) == 64 and all(character in "0123456789abcdef" for character in body)


def bit_length(value: Any) -> int:
    """Size of the canonical encoding of ``value`` in bits.

    Used by the lab to report transmission cost. It measures the artifact, not
    any model's token accounting.
    """
    return len(canonical_bytes(value)) * 8


__all__ = ["DIGEST_PREFIX", "canonical_bytes", "digest", "is_digest", "bit_length"]
