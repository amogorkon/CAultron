import contextlib

from caultron import xor_blocks


def test_xor_blocks_single_block():
    block = bytes([0xAA] * 256)
    assert xor_blocks(block) == block


def test_xor_blocks_two_blocks():
    block1 = bytes([0xAA] * 256)
    block2 = bytes([0x55] * 256)
    expected = bytes([0xFF] * 256)
    assert xor_blocks(block1, block2) == expected


def test_xor_blocks_multiple_blocks():
    block1 = bytes([0x01] * 256)
    block2 = bytes([0x02] * 256)
    block3 = bytes([0x04] * 256)
    expected = bytes([0x01 ^ 0x02 ^ 0x04] * 256)
    assert xor_blocks(block1, block2, block3) == expected


def test_xor_blocks_assertion():
    block = bytes([0x00] * 255)
    with contextlib.suppress(AssertionError):
        xor_blocks(block)
        assert False, "Should have raised an assertion error for wrong block size"
