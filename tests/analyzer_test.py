import pytest

from compiler.analyzer import BasicBlock, create_basic_block
from compiler.ir import (
    Instruction,
    Label,
    LoadIntConst,
    IRVar,
    Copy,
    Return,
    LoadBoolConst,
    CondJump,
    Jump,
    Call,
)


def cases() -> list[tuple[list[Instruction], list[BasicBlock]]]:
    return [
        (
            [
                Label("Start"),
                LoadIntConst(1, IRVar("v0")),
                Copy(IRVar("v0"), IRVar("v1")),
                Return(),
            ],
            [
                BasicBlock(
                    [
                        Label("Start"),
                        LoadIntConst(1, IRVar("v0")),
                        Copy(IRVar("v0"), IRVar("v1")),
                        Return(),
                    ]
                )
            ],
        ),
        (
            [
                Label(name="Start"),
                LoadBoolConst(False, IRVar("v0")),
                Copy(IRVar("v0"), IRVar("v1")),
                # v2 is or result
                LoadBoolConst(True, IRVar("v3")),
                CondJump(IRVar("v3"), Label("L0"), Label("L1")),
                Label(name="L0"),
                LoadBoolConst(True, IRVar("v2")),
                Jump(Label("L2")),
                Label(name="L1"),
                LoadBoolConst(True, IRVar("v4")),
                Copy(IRVar("v4"), IRVar("v1")),
                Copy(IRVar("v1"), IRVar("v2")),
                Jump(Label("L2")),
                Label(name="L2"),
                Call(IRVar("print_bool"), [IRVar("v1")], IRVar("v5")),
                Return(),
            ],
            [
                BasicBlock(
                    [
                        Label(name="Start"),
                        LoadBoolConst(False, IRVar("v0")),
                        Copy(IRVar("v0"), IRVar("v1")),
                        # v2 is or result
                        LoadBoolConst(True, IRVar("v3")),
                        CondJump(IRVar("v3"), Label("L0"), Label("L1")),
                    ]
                ),
                BasicBlock(
                    [
                        Label(name="L0"),
                        LoadBoolConst(True, IRVar("v2")),
                        Jump(Label("L2")),
                    ]
                ),
                BasicBlock(
                    [
                        Label(name="L1"),
                        LoadBoolConst(True, IRVar("v4")),
                        Copy(IRVar("v4"), IRVar("v1")),
                        Copy(IRVar("v1"), IRVar("v2")),
                        Jump(Label("L2")),
                    ]
                ),
                BasicBlock(
                    [
                        Label(name="L2"),
                        Call(IRVar("print_bool"), [IRVar("v1")], IRVar("v5")),
                        Return(),
                    ]
                ),
            ],
        ),
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_analyzer_create_basic_block(
    test_input: list[Instruction], expected: list[BasicBlock]
) -> None:
    assert create_basic_block(test_input) == expected
