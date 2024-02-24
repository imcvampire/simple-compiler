import subprocess
import pytest
import os
import pathlib

from compiler.assembler import assemble
from compiler.assembly_generator import generate_assembly
from compiler.builtin_type import builtin_types
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.token import Tokens
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck

root_dir = os.path.realpath(os.getcwd())


def cases() -> list[tuple[str, str]]:
    return [
        ("1", "1"),
        ("true", "true"),
        ("false", "false"),
        # ("1 - 2", -1),
        ("1 == 2", "false"),
        ("true and false", "false"),
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_assembler_assemble(test_input: str, expected: str) -> None:
    tokens = tokenize(test_input)
    ast_node = parse(Tokens(tokens))
    typecheck(ast_node)
    ir_instructions = generate_ir(builtin_types, ast_node)
    asm_code = generate_assembly(ir_instructions)

    program_name = f"compiled_program_{test_input.replace(' ', '_')}"
    assemble(asm_code, program_name)

    program_path = os.path.join(root_dir, program_name)

    result = subprocess.run(program_path, stdout=subprocess.PIPE)

    pathlib.Path.unlink(pathlib.Path(program_path))

    assert result.returncode == 0
    assert result.stdout.decode("utf-8") == f"{expected}\n"
