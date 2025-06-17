import pytest

from caultron.ca import xor_blocks


def test_xor_blocks_simple():
    a = bytes([0xAA] * 32)
    b = bytes([0x55] * 32)
    expected = bytes([0xFF] * 32)
    assert xor_blocks(a, b) == expected


def test_xor_blocks_identity():
    a = bytes([0x01] * 32)
    assert xor_blocks(a, a) == bytes([0x00] * 32)


def test_xor_blocks_multiple():
    a = bytes([0x0F] * 32)
    b = bytes([0xF0] * 32)
    c = bytes([0xFF] * 32)
    # a ^ b ^ c = 0x0F ^ 0xF0 ^ 0xFF = 0x0F ^ 0xF0 = 0xFF, 0xFF ^ 0xFF = 0x00
    assert xor_blocks(a, b, c) == bytes([0x00] * 32)


def test_xor_blocks_type_and_length():
    a = bytes([0x01] * 32)
    b = b"short"
    with pytest.raises(AssertionError):
        xor_blocks(a, b)
    with pytest.raises(AssertionError):
        xor_blocks(a)
