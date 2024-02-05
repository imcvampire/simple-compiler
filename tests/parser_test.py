from typing import Type

import pytest

from compiler.ast import (
    Literal,
    BinaryOp,
    Expression,
    IfExpression,
    FunctionExpression,
    BlockExpression,
    VariableDeclarationExpression,
    Identifier,
    TypeExpression,
)
from compiler.parser import parse
from compiler.parser_exception import (
    EndOfInputException,
    VariableCannotBeDeclaredException,
    MissingSemicolonException,
    MissingTypeException,
)
from compiler.token import Tokens
from compiler.tokenizer import tokenize


def cases() -> list[tuple[str, Expression]]:
    return [
        ("1 + 2", BinaryOp(left=Literal(value=1), op="+", right=Literal(value=2))),
        ("a = 1", BinaryOp(left=Identifier(name="a"), op="=", right=Literal(value=1))),
        (
            "a = 1 + 2",
            BinaryOp(
                left=Identifier(name="a"),
                op="=",
                right=BinaryOp(left=Literal(value=1), op="+", right=Literal(value=2)),
            ),
        ),
        (
            "a = 1 + 2 - 3",
            BinaryOp(
                left=Identifier(name="a"),
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
                left=Identifier(name="a"),
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
                left=Identifier(name="a"),
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
                left=Identifier(name="a"),
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
                    condition=Literal(value=True),
                    then_clause=Literal(value=2),
                    else_clause=Literal(value=3),
                ),
            ),
        ),
        (
            "f(a, 1)",
            FunctionExpression(
                name="f", arguments=[Identifier(name="a"), Literal(value=1)]
            ),
        ),
        (
            "a = f(b, 1)",
            BinaryOp(
                left=Identifier(name="a"),
                op="=",
                right=FunctionExpression(
                    name="f", arguments=[Identifier(name="b"), Literal(value=1)]
                ),
            ),
        ),
        (
            "1 or a",
            BinaryOp(
                left=Literal(value=1),
                op="or",
                right=Identifier(name="a"),
            ),
        ),
        (
            "a and b",
            BinaryOp(
                left=Identifier(name="a"),
                op="and",
                right=Identifier(name="b"),
            ),
        ),
        (
            "a == 1",
            BinaryOp(
                left=Identifier(name="a"),
                op="==",
                right=Literal(value=1),
            ),
        ),
        (
            "a and b != 1",
            BinaryOp(
                left=Identifier(name="a"),
                op="and",
                right=BinaryOp(
                    left=Identifier(name="b"),
                    op="!=",
                    right=Literal(value=1),
                ),
            ),
        ),
        (
            "a != 1 and 2",
            BinaryOp(
                left=BinaryOp(
                    left=Identifier(name="a"),
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
                left=Identifier(name="a"),
                op="=",
                right=BinaryOp(
                    left=Identifier(name="b"),
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
                result=Identifier(name="x"),
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
                        arguments=[Identifier(name="a")],
                    ),
                    BinaryOp(
                        left=Identifier(name="x"),
                        op="=",
                        right=Identifier(name="y"),
                    ),
                ],
                result=FunctionExpression(
                    name="f",
                    arguments=[Identifier(name="x")],
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
                        arguments=[Identifier(name="a")],
                    ),
                    BinaryOp(
                        left=Identifier(name="x"),
                        op="=",
                        right=Identifier(name="y"),
                    ),
                    BinaryOp(
                        left=BinaryOp(
                            left=Identifier(name="a"),
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
            "{ { a } { b } }",
            BlockExpression(
                expressions=[
                    BlockExpression(
                        expressions=[],
                        result=Identifier(name="a"),
                    ),
                ],
                result=BlockExpression(
                    expressions=[],
                    result=Identifier(name="b"),
                ),
            ),
        ),
        (
            "{ if true then { a } b }",
            BlockExpression(
                expressions=[
                    IfExpression(
                        condition=Literal(value=True),
                        then_clause=BlockExpression(
                            expressions=[],
                            result=Identifier(name="a"),
                        ),
                    ),
                ],
                result=Identifier(name="b"),
            ),
        ),
        (
            "{ if true then { a }; b }",
            BlockExpression(
                expressions=[
                    IfExpression(
                        condition=Literal(value=True),
                        then_clause=BlockExpression(
                            expressions=[],
                            result=Identifier(name="a"),
                        ),
                    ),
                ],
                result=Identifier(name="b"),
            ),
        ),
        (
            "{ if true then { a } b; c }",
            BlockExpression(
                expressions=[
                    IfExpression(
                        condition=Literal(value=True),
                        then_clause=BlockExpression(
                            expressions=[],
                            result=Identifier(name="a"),
                        ),
                    ),
                    Identifier(name="b"),
                ],
                result=Identifier(name="c"),
            ),
        ),
        (
            "{ if true then { a } else { b } 3 }",
            BlockExpression(
                expressions=[
                    IfExpression(
                        condition=Literal(value=True),
                        then_clause=BlockExpression(
                            expressions=[],
                            result=Identifier(name="a"),
                        ),
                        else_clause=BlockExpression(
                            expressions=[],
                            result=Identifier(name="b"),
                        ),
                    ),
                ],
                result=Literal(value=3),
            ),
        ),
        (
            "x = { { f(a) } { b } }",
            BinaryOp(
                left=Identifier(name="x"),
                op="=",
                right=BlockExpression(
                    expressions=[
                        BlockExpression(
                            expressions=[],
                            result=FunctionExpression(
                                name="f",
                                arguments=[Identifier(name="a")],
                            ),
                        ),
                    ],
                    result=BlockExpression(expressions=[], result=Identifier(name="b")),
                ),
            ),
        ),
        (
            "var a = 0; \n a = 1",
            BlockExpression(
                expressions=[
                    VariableDeclarationExpression(
                        name="a",
                        value=Literal(value=0),
                    ),
                ],
                result=BinaryOp(
                    left=Identifier(name="a"),
                    op="=",
                    right=Literal(value=1),
                ),
            ),
        ),
        (
            "var a = 0; \n a = 1;",
            BlockExpression(
                expressions=[
                    VariableDeclarationExpression(
                        name="a",
                        value=Literal(value=0),
                    ),
                    BinaryOp(
                        left=Identifier(name="a"),
                        op="=",
                        right=Literal(value=1),
                    ),
                ],
            ),
        ),
        (
            "var a: Int = 1",
            VariableDeclarationExpression(
                name="a",
                value=Literal(value=1),
                type=TypeExpression("Int"),
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
        ("{ a b }", MissingSemicolonException),
        ("{ if true then { a } b c }", MissingSemicolonException),
        ("var a: Foo = 1", MissingTypeException),
    ]


@pytest.mark.parametrize("test_input,expected_exception", error_cases())
def test_parser_parse_error(
    test_input: str, expected_exception: Type[Exception]
) -> None:
    with pytest.raises(Exception) as e:
        parse(Tokens(tokens=tokenize(test_input)))

    assert e.type is expected_exception
