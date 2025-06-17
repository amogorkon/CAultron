from itertools import islice
from struct import pack, unpack
from typing import Generator

SIGMA = (0x61707865, 0x3320646E, 0x79622D32, 0x6B206574)


def yield_chacha20_xor_stream(
    key: bytes, iv: bytes, position: int = 1
) -> Generator[int, None, None]:
    """Generate the xor stream with the ChaCha20 cipher (12-byte nonce)."""
    assert isinstance(position, int), "Position/counter must be an integer."
    assert 0 <= position < 2**32, (
        "Position/counter must be a uint32 (0 <= position < 2**32)."
    )
    assert isinstance(key, bytes), "Key must be bytes."
    assert isinstance(iv, bytes), "IV/nonce must be bytes."
    assert len(key) == 32, "Key must be 32 bytes."
    assert len(iv) == 12, "Nonce/IV must be 12 bytes (96 bits) for ChaCha20."

    def rotate(v, c):
        return ((v >> c) | (v << (32 - c))) & 0xFFFFFFFF

    def quarter_round(x, a, b, c, d):
        x[a] = (x[a] + x[b]) & 0xFFFFFFFF
        x[d] = rotate(x[d] ^ x[a], 16)
        x[c] = (x[c] + x[d]) & 0xFFFFFFFF
        x[b] = rotate(x[b] ^ x[c], 12)
        x[a] = (x[a] + x[b]) & 0xFFFFFFFF
        x[d] = rotate(x[d] ^ x[a], 8)
        x[c] = (x[c] + x[d]) & 0xFFFFFFFF
        x[b] = rotate(x[b] ^ x[c], 7)

    ctx = [0] * 16
    ctx[:4] = SIGMA
    ctx[4:12] = unpack("<8L", key)
    ctx[12] = position
    ctx[13] = unpack(">L", iv[:4])[0]
    ctx[14] = unpack(">L", iv[4:8])[0]
    ctx[15] = unpack(">L", iv[8:])[0]
    while 1:
        x = list(ctx)
        for i in range(10):
            quarter_round(x, 0, 4, 8, 12)
            quarter_round(x, 1, 5, 9, 13)
            quarter_round(x, 2, 6, 10, 14)
            quarter_round(x, 3, 7, 11, 15)
            quarter_round(x, 0, 5, 10, 15)
            quarter_round(x, 1, 6, 11, 12)
            quarter_round(x, 2, 7, 8, 13)
            quarter_round(x, 3, 4, 9, 14)
        yield from pack("<16L", *((x[i] + ctx[i]) & 0xFFFFFFFF for i in range(16)))
        ctx[12] = (ctx[12] + 1) & 0xFFFFFFFF
        if ctx[12] == 0:
            # Counter overflow: this will cause keystream reuse, which is a security vulnerability.
            raise RuntimeError(
                "ChaCha20 block counter overflow: keystream reuse would occur. Limit output to < 2^32 blocks per IV."
            )


def chacha20_encrypt(
    data: bytes, key: bytes, iv: bytes | None = None, position: int = 1
) -> bytes:
    """Encrypt (or decrypt) with the ChaCha20 cipher (12-byte nonce)."""
    assert isinstance(data, bytes), "Data must be bytes."
    assert isinstance(key, bytes), "Key must be bytes."
    assert len(key) == 32, "Key must be 32 bytes."
    if iv is None:
        iv = b"\0" * 12
    assert isinstance(iv, bytes), "IV/nonce must be bytes."
    assert len(iv) == 12, "Nonce/IV must be 12 bytes (96 bits) for ChaCha20."
    assert isinstance(position, int), "Position/counter must be an integer."
    assert 0 <= position < 2**32, (
        "Position/counter must be a uint32 (0 <= position < 2**32)."
    )

    keystream = islice(yield_chacha20_xor_stream(key, iv, position), len(data))
    return bytes(a ^ b for a, b in zip(data, keystream))
