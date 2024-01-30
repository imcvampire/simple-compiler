from typing import List, Tuple, Type

import pytest

from compiler.ast import (
    Literal,
    BinaryOp,
    Expression,
    IfExpression,
    FunctionExpression,
    BlockExpression,
    VariableDeclarationExpression,
)
from compiler.parser import parse
from compiler.parser_exception import (
    EndOfInputException,
    VariableCannotBeDeclaredException,
)
from compiler.token import Tokens
from compiler.tokenizer import tokenize


def cases() -> list[tuple[str, Expression]]:
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
            "(1 + 2) - 3",
            BinaryOp(
                left=BinaryOp(left=Literal(value=1), op="+", right=Literal(value=2)),
                op="-",
                right=Literal(value=3),
            ),
        ),
        (
            "1 + (2 - 3)",
            BinaryOp(
                left=Literal(value=1),
                op="+",
                right=BinaryOp(left=Literal(value=2), op="-", right=Literal(value=3)),
            ),
        ),
        (
            "a = if 1 then 2",
            BinaryOp(
                left=Literal(value="a"),
                op="=",
                right=IfExpression(
                    condition=Literal(value=1),
                    then_clause=Literal(value=2),
                ),
            ),
        ),
        (
            "a = if 1 then 3 else 4",
            BinaryOp(
                left=Literal(value="a"),
                op="=",
                right=IfExpression(
                    condition=Literal(value=1),
                    then_clause=Literal(value=3),
                    else_clause=Literal(value=4),
                ),
            ),
        ),
        (
            "1 + if true then 2 else 3",
            BinaryOp(
                left=Literal(value=1),
                op="+",
                right=IfExpression(
                    condition=Literal(value="true"),
                    then_clause=Literal(value=2),
                    else_clause=Literal(value=3),
                ),
            ),
        ),
        (
            "f(a, 1)",
            FunctionExpression(
                name="f", arguments=[Literal(value="a"), Literal(value=1)]
            ),
        ),
        (
            "a = f(b, 1)",
            BinaryOp(
                left=Literal(value="a"),
                op="=",
                right=FunctionExpression(
                    name="f", arguments=[Literal(value="b"), Literal(value=1)]
                ),
            ),
        ),
        (
            "1 or a",
            BinaryOp(
                left=Literal(value=1),
                op="or",
                right=Literal(value="a"),
            ),
        ),
        (
            "a and b",
            BinaryOp(
                left=Literal(value="a"),
                op="and",
                right=Literal(value="b"),
            ),
        ),
        (
            "a == 1",
            BinaryOp(
                left=Literal(value="a"),
                op="==",
                right=Literal(value=1),
            ),
        ),
        (
            "a and b != 1",
            BinaryOp(
                left=Literal(value="a"),
                op="and",
                right=BinaryOp(
                    left=Literal(value="b"),
                    op="!=",
                    right=Literal(value=1),
                ),
            ),
        ),
        (
            "a != 1 and 2",
            BinaryOp(
                left=BinaryOp(
                    left=Literal(value="a"),
                    op="!=",
                    right=Literal(value=1),
                ),
                op="and",
                right=Literal(value=2),
            ),
        ),
        (
            "a = b = 1",
            BinaryOp(
                left=Literal(value="a"),
                op="=",
                right=BinaryOp(
                    left=Literal(value="b"),
                    op="=",
                    right=Literal(value=1),
                ),
            ),
        ),
        (
            "var x = 123",
            VariableDeclarationExpression(
                name="x",
                value=Literal(value=123),
            ),
        ),
        (
            "{var x = 123}",
            BlockExpression(
                expressions=[],
                result=VariableDeclarationExpression(
                    name="x",
                    value=Literal(value=123),
                ),
            ),
        ),
        (
            "{var x = 123; x}",
            BlockExpression(
                expressions=[
                    VariableDeclarationExpression(
                        name="x",
                        value=Literal(value=123),
                    ),
                ],
                result=Literal(value="x"),
            ),
        ),
        (
            """{
    f(a);
    x = y;
    f(x)
}""",
            BlockExpression(
                expressions=[
                    FunctionExpression(
                        name="f",
                        arguments=[Literal(value="a")],
                    ),
                    BinaryOp(
                        left=Literal(value="x"),
                        op="=",
                        right=Literal(value="y"),
                    ),
                ],
                result=FunctionExpression(
                    name="f",
                    arguments=[Literal(value="x")],
                ),
            ),
        ),
        (
            """{
    f(a);
    x = y;
    a != 1 and 2;
}""",
            BlockExpression(
                expressions=[
                    FunctionExpression(
                        name="f",
                        arguments=[Literal(value="a")],
                    ),
                    BinaryOp(
                        left=Literal(value="x"),
                        op="=",
                        right=Literal(value="y"),
                    ),
                    BinaryOp(
                        left=BinaryOp(
                            left=Literal(value="a"),
                            op="!=",
                            right=Literal(value=1),
                        ),
                        op="and",
                        right=Literal(value=2),
                    ),
                ],
                result=Literal(None),
            ),
        ),
        (
            "",
            Literal(None),
        ),
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_parser_parse(test_input: str, expected: Expression) -> None:
    assert parse(Tokens(tokens=tokenize(test_input))) == expected


def error_cases() -> list[tuple[str, Type[Exception]]]:
    return [
        ("a + b c", EndOfInputException),
        ("(var a = 1)", VariableCannotBeDeclaredException),
        ("if a then var a = 1", VariableCannotBeDeclaredException),
    ]


@pytest.mark.parametrize("test_input,expected_exception", error_cases())
def test_parser_parse_error(
    test_input: str, expected_exception: Type[Exception]
) -> None:
    with pytest.raises(Exception) as e:
        parse(Tokens(tokens=tokenize(test_input)))

    assert e.type is expected_exception
