import pytest

from compiler.ir import (
    LoadIntConst,
    Instruction,
    IRVar,
    Call,
    Label,
    Return,
    CondJump,
    Jump,
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
            [Label("Start"), LoadIntConst(1, IRVar("a")), Return()],
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
            "if 1 == 1 then 1",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("v0")),
                LoadIntConst(1, IRVar("v1")),
                Call(IRVar("=="), [IRVar("v0"), IRVar("v1")], IRVar("v2")),
                CondJump(IRVar("v2"), Label("L_0"), Label("L_1")),
                Label(name="L_0"),
                LoadIntConst(1, IRVar("v3")),
                Label(name="L_1"),
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
                CondJump(IRVar("v2"), Label("L_0"), Label("L_1")),
                Label(name="L_0"),
                LoadIntConst(1, IRVar("v3")),
                Jump(Label("L_2")),
                Label(name="L_1"),
                LoadIntConst(2, IRVar("v4")),
                Label(name="L_2"),
                Return(),
            ],
        ),
        (
            "{ var a = 1; var b = 2; }",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("a")),
                LoadIntConst(2, IRVar("b")),
                Return(),
            ],
        ),
        (
            "{ var a = 1; a }",
            [
                Label(name="Start"),
                LoadIntConst(1, IRVar("a")),
                Call(IRVar("print_int"), [IRVar("a")], IRVar("v0")),
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
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_generate_ir(test_input: str, expected: list[Instruction]) -> None:
    node = parse(Tokens(tokenize(test_input)))
    typecheck(node)

    assert generate_ir({}, node) == expected
