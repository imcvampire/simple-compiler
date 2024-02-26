import typing

import pytest

from compiler.parser import parse
from compiler.token import Tokens
from compiler.tokenizer import tokenize
from compiler.type import Int, Bool, Type, Unit, ConstInt, ConstBool
from compiler.type_checker import typecheck
from compiler.type_checker_exception import (
    IncompatibleTypeException,
    UnknownTypeException,
    UnknownIdentifierException,
    WrongNumberOfArgumentsException,
)


def cases() -> list[tuple[str, Type]]:
    return [
        ("1", Int),
        ("true", Bool),
        ("1 - 2", Int),
        ("1 == 2", Bool),
        ("true and false", Bool),
        ("if 1 < 2 then 3", Unit),
        ("if 1 < 2 then 3 else 4", Int),
        ("if 1 < 2 then 3 < 4 else 4 < 5", Bool),
        ("print_int(1)", Int),
        ("print_bool(true)", Bool),
        ("var a = 1", Int),
        ("var a = 0; \n a = 1", Int),
        ("var a = 0; \n a = 1;", Unit),
        ("{var a = 0; \n a = 1}", Int),
        ("{var a = 0; \n a = 1;}", Unit),
        ("var a: Int = 0; \n a = 1", Int),
        ("{var a: Int = 0; \n a = 1;}", Unit),
        ("if not true then 1 else 2", Int),
        ("var a = -1", Int),
        ("var a = -true; a", Bool),
        ("var a = not true; a", Bool),
        ("while true do { 1 }", Unit),
        ("read_int()", Int),
        ("const a = 1", ConstInt),
        ("const a = true", ConstBool),
        ("var a = 1; const b = 2; a = b", Int),
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_typecheck(test_input: str, expected: Type) -> None:
    assert typecheck(parse(Tokens(tokenize(test_input)))) == expected


def error_cases() -> list[tuple[str, typing.Type[Exception]]]:
    return [
        ("1 - true", IncompatibleTypeException),
        ("1 == true", IncompatibleTypeException),
        ("1 and true", IncompatibleTypeException),
        ("1 and 2", IncompatibleTypeException),
        ("(1 < 2) + 3", IncompatibleTypeException),
        ("if 1 then 2 else 3", IncompatibleTypeException),
        ("if 1 < 2 then 3 else 3 < 5", IncompatibleTypeException),
        ("print_int(true)", IncompatibleTypeException),
        ("print_bool(1)", IncompatibleTypeException),
        ("var a = 1; \n a = true", IncompatibleTypeException),
        ("a = 1", UnknownIdentifierException),
        ("var a = 1; \n b = true", UnknownIdentifierException),
        ("var a: Bool = 1", IncompatibleTypeException),
        ("{ var a = true; { b = true } }", UnknownIdentifierException),
        ("while 1 do { 1 }", IncompatibleTypeException),
        # TODO: handle this case
        # ("var a = not 1", IncompatibleTypeException),
        ("read_int(1)", WrongNumberOfArgumentsException),
        ("const a = 1; a = 2", IncompatibleTypeException),
        ("const a = 1; a = 1", IncompatibleTypeException),
        ("const a = false; a = true", IncompatibleTypeException),
    ]


@pytest.mark.parametrize("test_input,expected_exception", error_cases())
def test_typecheck_error(
    test_input: str, expected_exception: typing.Type[Exception]
) -> None:
    with pytest.raises(expected_exception):
        typecheck(parse(Tokens(tokenize(test_input))))
