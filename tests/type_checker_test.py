import typing

import pytest

from compiler.parser import parse
from compiler.token import Tokens
from compiler.tokenizer import tokenize
from compiler.type import Int, Bool, Type, Unit
from compiler.type_checker import typecheck
from compiler.type_checker_exception import IncompatibleTypeException


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
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_type_checker_typecheck(test_input: str, expected: Type) -> None:
    assert typecheck(parse(Tokens(tokenize(test_input)))) == expected


def error_cases() -> list[tuple[str, typing.Type[Exception]]]:
    return [
        ("1 - true", IncompatibleTypeException),
        ("1 == true", IncompatibleTypeException),
        ("1 and true", IncompatibleTypeException),
        ("1 and 2", IncompatibleTypeException),
        ("(1 < 2) + 3", IncompatibleTypeException),
        ("if 1 then 2 else 3", IncompatibleTypeException),
        ("if 1 < 2 then 3 else 3 < 5", IncompatibleTypeException)
    ]


@pytest.mark.parametrize("test_input,expected_exception", error_cases())
def test_type_checker_typecheck_error(
    test_input: str, expected_exception: typing.Type[Exception]
) -> None:
    with pytest.raises(expected_exception):
        typecheck(parse(Tokens(tokenize(test_input))))
