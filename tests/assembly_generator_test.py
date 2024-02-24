import pytest
import os

from compiler.assembly_generator import generate_assembly
from compiler.builtin_type import builtin_types
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.token import Tokens
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck

test_dir = os.path.join(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))),
    "assembly_generator_test_data",
)


def read_test_data(filename: str) -> tuple[str, str]:
    with open(os.path.join(test_dir, filename)) as f:
        data = f.read().split("----------------\n")

        if len(data) != 2:
            raise ValueError(f"Invalid test data file {filename}")

        return data[0], data[1]


def cases() -> list[tuple[str, str]]:
    files = os.listdir(test_dir)
    return [read_test_data(file) for file in files]


@pytest.mark.parametrize("test_input,expected", cases())
def test_generate_assembly(test_input: str, expected: list[str]) -> None:
    node = parse(Tokens(tokenize(test_input)))
    typecheck(node)

    result = generate_assembly(generate_ir(builtin_types, node))

    assert result == expected
