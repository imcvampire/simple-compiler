import pytest

from compiler.type import Int, ConstInt, ConstType, PrimitiveType


def test_type() -> None:
    assert Int == ConstInt
    assert ConstInt != Int
    assert not ConstInt == Int
