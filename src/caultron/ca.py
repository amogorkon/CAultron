import hashlib
import secrets
from functools import reduce

import numpy as np
from numba import njit

from .chacha20 import chacha20_encrypt

SEED = 32  # 32 bytes = 256 bits


def generate_salt() -> bytes:
    """
    Generate a cryptographically secure 32-byte (256-bit) bitstream suitable for XOR with a SHA-256 hash.
    """
    return secrets.token_bytes(32)


@njit(cache=True)
def _evolve_numba(bits, meta_rule_bytes):
    # Manual big-endian conversion for 4 bytes
    rule_bits = 0
    for b in meta_rule_bytes:
        rule_bits = (rule_bits << 8) | b
    core_rule = (rule_bits >> 20) & 0xFF
    neighborhood_size = ((rule_bits >> 18) & 0x3) + 3
    boundary = (rule_bits >> 17) & 0x1
    inversion = (rule_bits >> 16) & 0x1
    modulation = (rule_bits >> 8) & 0xFF
    temporal = rule_bits & 0xFF
    n = len(bits)
    new_bits = np.zeros_like(bits)
    rule_table_size = 2**neighborhood_size
    if neighborhood_size == 3:
        rule_table = np.array(
            [(core_rule >> i) & 1 for i in range(7, -1, -1)], dtype=np.uint8
        )
    else:
        base = np.array(
            [(core_rule >> (i % 8)) & 1 for i in range(rule_table_size - 1, -1, -1)],
            dtype=np.uint8,
        )
        mask = np.array(
            [(modulation >> (i % 8)) & 1 for i in range(rule_table_size - 1, -1, -1)],
            dtype=np.uint8,
        )
        rule_table = base ^ mask
    if temporal:
        temporal_mod = temporal % rule_table_size
        rule_table = np.concatenate((
            rule_table[temporal_mod:],
            rule_table[:temporal_mod],
        ))
    for i in range(n):
        idxs = np.empty(neighborhood_size, dtype=np.int64)
        for j in range(neighborhood_size):
            offset = j - (neighborhood_size // 2)
            idx = i + offset
            if boundary == 0:
                idx = idx % n
            elif idx < 0 or idx >= n:
                idxs[j] = -1
                continue
            idxs[j] = idx
        idx_val = 0
        for j in range(neighborhood_size):
            b = 0 if idxs[j] == -1 else bits[idxs[j]]
            idx_val = (idx_val << 1) | int(b)
        idx_val = idx_val % rule_table_size
        out_bit = rule_table[idx_val]
        if inversion:
            out_bit ^= 1
        new_bits[i] = out_bit
    return new_bits


def evolve(bits: np.ndarray, seed: bytes) -> np.ndarray:
    assert isinstance(bits, np.ndarray)
    assert isinstance(seed, bytes) and len(seed) == SEED, f"Seed must be {SEED} bytes."
    meta_rule = seed[:4]
    return _evolve_numba(bits, meta_rule)


def inject_seed(bits: np.ndarray, seed: bytes, nonce: bytes = b"\0" * 12) -> np.ndarray:
    """
    Inject a seed into the CA state by XORing the current bits with a ChaCha20 keystream generated from the seed.
    The seed must be 32 bytes (256 bits). Returns a new numpy array.
    """
    assert isinstance(bits, np.ndarray)
    assert isinstance(seed, bytes) and len(seed) == SEED, (
        f"Seed must be {SEED} bytes, not {len(seed)}."
    )
    keystream = chacha20_encrypt(bytes([0] * len(bits)), seed, nonce)
    keystream_bits = np.frombuffer(keystream, dtype=np.uint8) & 1
    return _xor_bits_numba(bits, keystream_bits)


@njit(cache=True)
def _xor_bits_numba(bits, keystream_bits):
    n = len(bits)
    out = np.empty_like(bits)
    for i in range(n):
        out[i] = bits[i] ^ keystream_bits[i]
    return out


def get_mid_end(seed: bytes) -> tuple[int, int]:
    """
    Get the midpoint and endpoint from the end of the seed.
    Returns a tuple (midpoint_bits, endpoint_bits).
    """
    assert isinstance(seed, bytes) and len(seed) == SEED, f"Seed must be {SEED} bytes."
    seed_int = int.from_bytes(seed, "big")
    a = max((seed_int >> 0) & 0b11111111, 1)
    b = max((seed_int >> 8) & 0b11111111, 1)
    if a == b:
        a += 1
    return min(a, b), max(a, b)


def derive_key(secrets: list[bytes], salt: bytes, counter: int, size=1024) -> bytes:
    """Evolve the universe for the target counter and derive a key."""
    state = np.zeros(size, dtype=bool)

    midpoint = b""
    endpoint = b""
    seed = b""

    counter_block = hashlib.sha256(counter.to_bytes(8, "big")).digest()
    seed = xor_blocks(*secrets, counter_block, salt)
    mid, end = get_mid_end(seed)

    meta_rule = bytearray(seed[:4])
    for i in range(1, end):
        state = inject_seed(
            state, seed, nonce=f"cnt={counter:04d}_step={i:04d}".encode()[:12]
        )
        prev_entropy = bit_entropy(state)
        next_bits = _evolve_numba(state, meta_rule)
        next_entropy = bit_entropy(next_bits)
        if abs(next_entropy - prev_entropy) < 0.1:
            # Rotate rule bits (meta_rule) by 1 bit to the left
            rule_bits = int.from_bytes(meta_rule, "big")
            rule_bits = ((rule_bits << 1) | (rule_bits >> 27)) & 0x0FFFFFFF  # 28 bits
            meta_rule = rule_bits.to_bytes(4, "big")
        state = next_bits
        if i == mid:
            if all(x == 0 for x in state):
                state = inject_seed(state, seed, nonce=f"mid={i:<12}".encode()[:12])
            midpoint = _calculate_key(state)

    if all(x == 0 for x in state):
        state = inject_seed(state, seed, nonce=f"end={counter:<12}".encode()[:12])
    endpoint = _calculate_key(state)

    assert midpoint
    assert endpoint

    if midpoint == endpoint:  # extremely unlikely, but possible
        return endpoint

    return bytes(x ^ y for x, y in zip(midpoint, endpoint))


def _calculate_key(bits: np.ndarray) -> bytes:
    """
    Derive a cryptographic key by hashing the full CA state with SHA-512.
    """
    bitstring = "".join(map(str, bits.astype(np.uint8).tolist()))
    pad_len = (8 - len(bitstring) % 8) % 8
    bitstring += "0" * pad_len
    bytelist = [int(bitstring[i : i + 8], 2) for i in range(0, len(bitstring), 8)]
    state_bytes = bytes(bytelist)
    return hashlib.sha512(state_bytes).digest()


def xor_blocks(*blocks: bytes) -> bytes:
    """
    Derive a seed from any number of secrets (bytes) by XOR'ing their SHA-256 hashes.
    Returns a 32-byte (256-bit) seed.
    """
    assert len(blocks) >= 2, "At least two secrets must be provided."
    assert all(isinstance(s, bytes) for s in blocks), "All secrets must be bytes."
    assert all(len(s) == 32 for s in blocks), "All secrets must be 32 bytes (256 bits)."

    return reduce(lambda a, b: bytes(x ^ y for x, y in zip(a, b)), blocks)


def prepare_secrets(*secrets: bytes | str) -> list[bytes]:
    """
    Prepare the secrets and derive a seed from them.
    """
    return [
        hashlib.sha256(s.encode() if isinstance(s, str) else s).digest()
        for s in secrets
    ]


def bit_entropy(state: np.ndarray) -> float:
    """Shannon entropy of a CA state."""
    p = np.mean(state)
    return 0.0 if p in [0, 1] else -p * np.log2(p) - (1 - p) * np.log2(1 - p)
