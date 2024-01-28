import pytest

from compiler.ast import Literal, BinaryOp, Expression
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_cases() -> list[tuple[str, Expression]]:
    return [
        ("1 + 2", BinaryOp(left=Literal(value=1), op="+", right=Literal(value=2))),
        ("a = 1", BinaryOp(left=Literal(value="a"), op="=", right=Literal(value=1))),
        (
            "a = 1 + 2",
            BinaryOp(
                left=Literal(value="a"),
                op="=",
                right=BinaryOp(left=Literal(value=1), op="+", right=Literal(value=2)),
            ),
        ),
        (
            "a = 1 + 2 - 3",
            BinaryOp(
                left=Literal(value="a"),
                op="=",
                right=BinaryOp(
                    left=BinaryOp(
                        left=Literal(value=1), op="+", right=Literal(value=2)
                    ),
                    op="-",
                    right=Literal(value=3),
                ),
            ),
        ),
        (
            "a = 1 * 2",
            BinaryOp(
                left=Literal(value="a"),
                op="=",
                right=BinaryOp(left=Literal(value=1), op="*", right=Literal(value=2)),
            ),
        ),
        (
            "",
            Literal(None),
        ),
    ]


@pytest.mark.parametrize("test_input,expected", test_cases())
def test_parser_parse(test_input: str, expected: Expression) -> None:
    assert parse(tokenize(test_input)) == expected
