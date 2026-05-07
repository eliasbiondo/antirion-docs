"""
ULID generation — Crockford base32, 26 chars, sortable by creation time.

Two flavors:
- `ulid_now()` — real ULID with current millisecond timestamp + 80 random bits.
  Used by `req new` for fresh nodes.
- `synthetic_ulid(seed, ts_ms)` — deterministic ULID-shape id derived from a
  seed string + a chosen timestamp. Used by the migration helper so re-running
  the migration produces byte-identical output.

The synthetic form keeps the timestamp portion meaningful: migrated nodes get
a timestamp that increases with their legacy sequence number, so a sort by id
mirrors the order the nodes had in the legacy YAML. New nodes (real ULIDs)
necessarily sort after the migration window.
"""

from __future__ import annotations

import hashlib
import os
import time

# Crockford base32: drops I, L, O, U so humans don't misread.
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _encode(value: int, n_chars: int) -> str:
    """Encode `value` (non-negative int) to exactly `n_chars` Crockford base32
    characters, big-endian."""
    if value < 0:
        raise ValueError("ULID encoder requires non-negative int")
    out = []
    for _ in range(n_chars):
        out.append(ALPHABET[value & 0x1F])
        value >>= 5
    if value != 0:
        raise ValueError("value too large for requested width")
    return "".join(reversed(out))


def encode_timestamp(ms: int) -> str:
    """48-bit ms timestamp → 10 Crockford base32 chars."""
    if ms < 0 or ms >= (1 << 48):
        raise ValueError(f"timestamp out of 48-bit range: {ms}")
    return _encode(ms, 10)


def encode_random(value: int) -> str:
    """80-bit value → 16 Crockford base32 chars."""
    if value < 0 or value >= (1 << 80):
        raise ValueError(f"randomness out of 80-bit range: {value}")
    return _encode(value, 16)


def ulid_now() -> str:
    """Real ULID for `req new`. Current ms timestamp + cryptographic randomness."""
    ts_ms = int(time.time() * 1000)
    rnd = int.from_bytes(os.urandom(10), "big")
    return encode_timestamp(ts_ms) + encode_random(rnd)


def synthetic_ulid(seed: str, ts_ms: int) -> str:
    """Deterministic ULID-shape id.

    The 48-bit timestamp portion encodes `ts_ms` (chosen by the caller — for
    the migration this is `MIGRATION_BASE_MS + 60_000 * legacy_seq`, which
    keeps id-sort order matching legacy-id order). The 80-bit "randomness"
    portion is the first 10 bytes of sha256(seed), making the id stable across
    migration re-runs.
    """
    h = hashlib.sha256(seed.encode("utf-8")).digest()[:10]
    rnd = int.from_bytes(h, "big")
    return encode_timestamp(ts_ms) + encode_random(rnd)


# Pattern for validation. 26 chars, Crockford alphabet, uppercase.
ULID_PATTERN = r"[0-9A-HJKMNP-TV-Z]{26}"
