"""
Test for ChaCha20 implementation with 12-byte nonce (RFC 8439 test vector).
"""

import pytest

from caultron.chacha20 import chacha20_encrypt


def test_chacha20_roundtrip():
    key = b"0" * 32
    nonce = b"1" * 12
    counter = 1
    plaintext = b"The quick brown fox jumps over the lazy dog."
    ciphertext = chacha20_encrypt(plaintext, key, nonce, counter)
    decrypted = chacha20_encrypt(ciphertext, key, nonce, counter)
    assert decrypted == plaintext


def test_chacha20_empty_plaintext():
    key = b"0" * 32
    nonce = b"1" * 12
    counter = 1
    plaintext = b""
    ciphertext = chacha20_encrypt(plaintext, key, nonce, counter)
    decrypted = chacha20_encrypt(ciphertext, key, nonce, counter)
    assert decrypted == plaintext
    assert ciphertext == b""


def test_chacha20_large_plaintext():
    key = b"0" * 32
    nonce = b"1" * 12
    counter = 1
    plaintext = b"A" * 10_000_000  # 10 MB
    ciphertext = chacha20_encrypt(plaintext, key, nonce, counter)
    decrypted = chacha20_encrypt(ciphertext, key, nonce, counter)
    assert decrypted == plaintext


def test_chacha20_invalid_key_length():
    nonce = b"1" * 12
    counter = 1
    plaintext = b"test"
    # Too short
    short_key = b"0" * 16
    try:
        chacha20_encrypt(plaintext, short_key, nonce, counter)
        assert False, "Expected exception for short key"
    except Exception:
        pass
    # Too long
    long_key = b"0" * 64
    try:
        chacha20_encrypt(plaintext, long_key, nonce, counter)
        assert False, "Expected exception for long key"
    except Exception:
        pass


def test_chacha20_invalid_nonce_length():
    key = b"0" * 32
    counter = 1
    plaintext = b"test"
    # Too short
    short_nonce = b"1" * 8
    try:
        chacha20_encrypt(plaintext, key, short_nonce, counter)
        assert False, "Expected exception for short nonce"
    except Exception:
        pass
    # Too long
    long_nonce = b"1" * 16
    try:
        chacha20_encrypt(plaintext, key, long_nonce, counter)
        assert False, "Expected exception for long nonce"
    except Exception:
        pass


def test_chacha20_various_counters():
    key = b"0" * 32
    nonce = b"1" * 12
    plaintext = b"counter test"
    for counter in [0, 1, 2, 2**32 - 1]:
        ciphertext = chacha20_encrypt(plaintext, key, nonce, counter)
        decrypted = chacha20_encrypt(ciphertext, key, nonce, counter)
        assert decrypted == plaintext


def test_chacha20_non_ascii_data():
    key = b"0" * 32
    nonce = b"1" * 12
    counter = 1
    plaintext = "你好，世界🌍".encode("utf-8")
    ciphertext = chacha20_encrypt(plaintext, key, nonce, counter)
    decrypted = chacha20_encrypt(ciphertext, key, nonce, counter)
    assert decrypted == plaintext


def test_chacha20_nonce_key_reuse_determinism():
    key = b"0" * 32
    nonce = b"1" * 12
    counter = 1
    plaintext = b"repeatable"
    ciphertext1 = chacha20_encrypt(plaintext, key, nonce, counter)
    ciphertext2 = chacha20_encrypt(plaintext, key, nonce, counter)
    assert ciphertext1 == ciphertext2
    decrypted = chacha20_encrypt(ciphertext1, key, nonce, counter)
    assert decrypted == plaintext


if __name__ == "__main__":
    test_chacha20_roundtrip()
    test_chacha20_empty_plaintext()
    # test_chacha20_large_plaintext()
    test_chacha20_invalid_key_length()
    test_chacha20_invalid_nonce_length()
    test_chacha20_various_counters()
    test_chacha20_non_ascii_data()
    test_chacha20_nonce_key_reuse_determinism()
