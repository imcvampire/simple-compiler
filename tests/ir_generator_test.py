import pytest

from compiler.builtin_type import builtin_types
from compiler.ir import (
    LoadIntConst,
    Instruction,
    IRVar,
    Call,
    Label,
    Return,
    CondJump,
    Jump,
    LoadBoolConst,
    Copy,
)
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.token import Tokens
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck


def cases() -> list[tuple[str, list[Instruction]]]:
    return [
        (
            "var a = 1;",
            [
                Label("Start"),
                LoadIntConst(1, IRVar("v0")),
                Copy(IRVar("v0"), IRVar("v1")),
                Return(),
            ],
        ),
        (
            "1 == 1",
            [
                Label("Start"),
                LoadIntConst(1, IRVar("v0")),
                LoadIntConst(1, IRVar("v1")),
                Call(IRVar("=="), [IRVar("v0"), IRVar("v1")], IRVar("v2")),
                Call(IRVar("print_bool"), [IRVar("v2")], IRVar("v3")),
                Return(),
            ],
        ),
        (
            "1 + 2 * 3",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                LoadIntConst(2, IRVar("v1")),
                LoadIntConst(3, IRVar("v2")),
                Call(IRVar("*"), [IRVar("v1"), IRVar("v2")], IRVar("v3")),
                Call(IRVar("+"), [IRVar("v0"), IRVar("v3")], IRVar("v4")),
                Call(IRVar("print_int"), [IRVar("v4")], IRVar("v5")),
                Return(),
            ],
        ),
        (
            """
                var a = false;
                true or { a = true; a };
                print_bool(a);
            """,
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
        ),
        (
            """
                var a = 1;
                false and { a = 2; a == 2 }
                print_int(a);
            """,
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                Copy(IRVar("v0"), IRVar("v1")),
                # v2 is and result
                LoadBoolConst(False, IRVar("v3")),
                CondJump(IRVar("v3"), Label("L1"), Label("L0")),
                Label(name="L0"),
                LoadBoolConst(False, IRVar("v2")),
                Jump(Label("L2")),
                Label(name="L1"),
                LoadIntConst(2, IRVar("v4")),
                Copy(IRVar("v4"), IRVar("v1")),
                LoadIntConst(2, IRVar("v5")),
                Call(IRVar("=="), [IRVar("v1"), IRVar("v5")], IRVar("v6")),
                Copy(IRVar("v6"), IRVar("v2")),
                Jump(Label("L2")),
                Label(name="L2"),
                Call(IRVar("print_int"), [IRVar("v1")], IRVar("v7")),
                Return(),
            ],
        ),
        (
            "if 1 == 1 then 1",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                LoadIntConst(1, IRVar("v1")),
                Call(IRVar("=="), [IRVar("v0"), IRVar("v1")], IRVar("v2")),
                CondJump(IRVar("v2"), Label("L0"), Label("L1")),
                Label(name="L0"),
                LoadIntConst(1, IRVar("v3")),
                Label(name="L1"),
                Return(),
            ],
        ),
        (
            "if 1 == 1 then 1 else 2",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                LoadIntConst(1, IRVar("v1")),
                Call(IRVar("=="), [IRVar("v0"), IRVar("v1")], IRVar("v2")),
                CondJump(IRVar("v2"), Label("L0"), Label("L1")),
                Label(name="L0"),
                LoadIntConst(1, IRVar("v4")),
                Copy(IRVar("v4"), IRVar("v3")),
                Jump(Label("L2")),
                Label(name="L1"),
                LoadIntConst(2, IRVar("v5")),
                Copy(IRVar("v5"), IRVar("v3")),
                Label(name="L2"),
                Call(IRVar("print_int"), [IRVar("v3")], IRVar("v6")),
                Return(),
            ],
        ),
        (
            "{ var a = 1; var b = 2; }",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                Copy(IRVar("v0"), IRVar("v1")),
                LoadIntConst(2, IRVar("v2")),
                Copy(IRVar("v2"), IRVar("v3")),
                Return(),
            ],
        ),
        (
            "{ var a = 1; a }",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                Copy(IRVar("v0"), IRVar("v1")),
                Call(IRVar("print_int"), [IRVar("v1")], IRVar("v2")),
                Return(),
            ],
        ),
        (
            "{ var a = 1; var b = 2; a = 3 }",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                Copy(IRVar("v0"), IRVar("v1")),
                LoadIntConst(2, IRVar("v2")),
                Copy(IRVar("v2"), IRVar("v3")),
                LoadIntConst(3, IRVar("v4")),
                Copy(IRVar("v4"), IRVar("v1")),
                Return(),
            ],
        ),
        (
            "print_int(1)",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                Call(IRVar("print_int"), [IRVar("v0")], IRVar("v1")),
                Call(IRVar("print_int"), [IRVar("v1")], IRVar("v2")),
                Return(),
            ],
        ),
        (
            "print_bool(true);",
            [
                Label(name="Start"),
                LoadBoolConst(True, IRVar("v0")),
                Call(IRVar("print_bool"), [IRVar("v0")], IRVar("v1")),
                Return(),
            ],
        ),
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_generate_ir(test_input: str, expected: list[Instruction]) -> None:
    node = parse(Tokens(tokenize(test_input)))
    typecheck(node)

    assert generate_ir(builtin_types, node) == expected
