import hashlib
import secrets
from functools import reduce

import numpy as np

from .chacha20 import chacha20_encrypt

SEED = 32  # 32 bytes = 256 bits


def generate_crypto_bitstream() -> bytes:
    """
    Generate a cryptographically secure 32-byte (256-bit) bitstream suitable for XOR with a SHA-256 hash.
    """
    return secrets.token_bytes(32)


def _init_state(
    size: int,
    secrets: list[bytes],
    salt: bytes,
    counter: int = 1,
) -> np.ndarray:
    """
    Initialize a CA state as a numpy array of bits.
    """
    assert size > 256, "Universe size must be greater than 256 (seed size)."
    assert size % 8 == 0, "Universe size must be a multiple of 8."
    assert len(secrets) == 256, "Key must be exactly 256 bytes."
    assert 1 <= counter <= 2**64 - 1, "Counter must be between 1 and 2^64 - 1."
    assert isinstance(salt, bytes), "Salt must be a bytes object."
    assert len(salt) == 256, "Salt must be exactly 256 bytes."
    counter_block = hashlib.sha256(counter.to_bytes(8, "big")).digest()
    seed = xor_blocks(*secrets, counter_block, salt)
    keystream = chacha20_encrypt(bytes([0] * size), seed, b"\0" * 12, 1)
    return np.frombuffer(keystream, dtype=np.uint8) & 1


def evolve(bits: np.ndarray, seed: bytes) -> np.ndarray:
    """
    Evolve the CA state using a 32-byte seed. The meta-rule is derived as the first 4 bytes of the seed.
    Returns a new numpy array of bits.
    """
    assert isinstance(bits, np.ndarray)
    assert isinstance(seed, bytes) and len(seed) == 32, "Seed must be 32 bytes."
    meta_rule = seed[:4]
    rule_bits = int.from_bytes(meta_rule, "big")
    # Decode meta-rule fields
    core_rule = (rule_bits >> 20) & 0xFF  # bits 20-27
    neighborhood_size = ((rule_bits >> 18) & 0x3) + 3  # bits 18-19, values 0-3 → 3-6
    boundary = (rule_bits >> 17) & 0x1  # bit 17
    inversion = (rule_bits >> 16) & 0x1  # bit 16
    modulation = (rule_bits >> 8) & 0xFF  # bits 8-15
    temporal = rule_bits & 0xFF  # bits 0-7

    n = len(bits)
    new_bits = np.zeros_like(bits)
    # Prepare rule table for the given neighborhood size
    rule_table_size = 2**neighborhood_size
    # For 3-neighbor, use core_rule directly; for larger, expand core_rule with modulation
    if neighborhood_size == 3:
        rule_table = [(core_rule >> i) & 1 for i in reversed(range(8))]
    else:
        # Expand core_rule to fill rule_table_size using modulation as a mask or permutation
        base = [(core_rule >> (i % 8)) & 1 for i in reversed(range(rule_table_size))]
        mask = [(modulation >> (i % 8)) & 1 for i in reversed(range(rule_table_size))]
        rule_table = [b ^ m for b, m in zip(base, mask)]

    # Apply temporal: rotate rule_table by 'temporal' positions
    if temporal:
        temporal_mod = temporal % rule_table_size
        rule_table = rule_table[temporal_mod:] + rule_table[:temporal_mod]

    for i in range(n):
        # Get neighborhood
        neighborhood = []
        for j in range(-(neighborhood_size // 2), neighborhood_size // 2 + 1):
            idx = i + j
            if boundary == 0:  # Toroidal
                idx = idx % n
            elif idx < 0 or idx >= n:
                neighborhood.append(0)
                continue
            neighborhood.append(bits[idx])
        # Convert neighborhood to index
        idx = 0
        for b in neighborhood:
            idx = (idx << 1) | int(b)
        idx = idx % rule_table_size
        out_bit = rule_table[idx]
        # Inversion
        if inversion:
            out_bit ^= 1
        new_bits[i] = out_bit
    return new_bits


def inject_seed(bits: np.ndarray, seed: bytes, nonce: bytes = b"\0" * 12) -> np.ndarray:
    """
    Inject a seed into the CA state by XORing the current bits with a ChaCha20 keystream generated from the seed.
    The seed must be 32 bytes (256 bits). Returns a new numpy array.
    """
    assert isinstance(bits, np.ndarray)
    assert isinstance(seed, bytes) and len(seed) == SEED, f"Seed must be {SEED} bytes."
    keystream = chacha20_encrypt(bytes([0] * len(bits)), seed, nonce, 1)
    keystream_bits = np.frombuffer(keystream, dtype=np.uint8) & 1
    return bits ^ keystream_bits


def get_mid_end(seed: bytes) -> tuple[int, int]:
    """
    Get the midpoint and endpoint bits from the seed.
    Returns a tuple (midpoint_bits, endpoint_bits).
    """
    assert isinstance(seed, bytes) and len(seed) == SEED, f"Seed must be {SEED} bytes."
    seed_int = int.from_bytes(seed, "big")
    a = max((seed_int >> 0) & 0b111111, 1)
    b = max((seed_int >> 6) & 0b111111, 1)
    return min(a, b), max(a, b)


def derive_key(
    secrets: list[bytes], salt: bytes, target_counter: int, size=1024
) -> bytes:
    """Evolve the universe up to the target counter and derive a key."""
    state = np.zeros(size, dtype=bool)

    midpoint = b""
    endpoint = b""
    seed = b""

    for counter in range(1, target_counter + 1):
        counter_block = hashlib.sha256(counter.to_bytes(8, "big")).digest()
        seed = xor_blocks(*secrets, counter_block, salt)
        state = inject_seed(state, seed)
        mid, end = get_mid_end(seed)

        for i in range(1, end + 1):
            if i == mid:
                midpoint = _calculate_key(state)
            state = evolve(state, seed)
        endpoint = _calculate_key(state)

    assert midpoint
    assert endpoint
    if midpoint == endpoint:  # highly unlikely, but possible
        return endpoint
    if all(x == b"\0" for x in endpoint):  # again, extremely unlikely but possible
        state = inject_seed(state, seed)
        return _calculate_key(state)
    return bytes(x ^ y for x, y in zip(midpoint, endpoint))


def _calculate_key(bits: np.ndarray) -> bytes:
    """
    Derive a cryptographic key by hashing the full CA state with SHA-512.
    """
    bitstring = "".join(map(str, bits.tolist()))
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
