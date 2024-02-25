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
        ("1 - 2", "-1"),
        ("1 == 2", "false"),
        ("true and false", "false"),
        ("var a = -1; a", "-1"),
        ("if 1 < 2 then 3", ""),
        ("if true then 4 else 5", "4"),
        ("if 1 >= 2 then -1 else -2", "-2"),
        ("if not true then -10 else 0", "0"),
        ("if not not true then 8589934592 else 0", "8589934592"),
        ("var a = 1; false and { a = 2; a == 1 }; a", "1"),
        ("var a = true; true or { a = false; a }; a", "true"),
        ("var a = true; { a = false; a } or false", "false"),
        ("var a = 1; a + 1", "2"),
        ("var a = 2; a * 2", "4"),
        ("var a = 2; a / 2", "1"),
        ("var a = 2; a == 2", "true"),
        ("var a = 2; a != 2", "false"),
        ("var a = 2; a < 2", "false"),
        ("var a = 2; a > 2", "false"),
        ("var a = 2; a <= 2", "true"),
        ("var a = 2; a >= 2", "true"),
        ("var a = 2; var b = 3; a + b", "5"),
        ("var a = 2; var b = 3; a * b", "6"),
        ("var a = 2; var b = 3; a / b", "0"),
        ("var a = 2; var b = 3; a == b", "false"),
        ("var a = 2; var b = 3; a != b", "true"),
        ("var a = 2; var b = 3; a < b", "true"),
        ("var a = 2; var b = 3; a > b", "false"),
        ("var a = 2; var b = 3; a <= b", "true"),
        ("var a = 2; var b = 3; a >= b", "false"),
        ("var a = 2; var b = 3; if a < b then a + b else a - b", "5"),
        ("var a = 2; var b = 3; if a > b then a + b else a - b", "-1"),
        ("var a = 2; var b = 3; var c = 4; a + b + c", "9"),
        ("var a = 2; var b = 3; var c = 4; a * b * c", "24"),
        ("var a = 2; var b = 3; var c = 4; a / b / c", "0"),
        ("var a = 8589934593; var b = 2; a * b", "17179869186"),
        ("var a = 17179869186; var b = 2; a / b", "8589934593"),
        ("1 + 2 * 3", "7"),
        ("1 * 2 + 3", "5"),
        ("1 + 2 - 3", "0"),
        ("{ var a = -2; a + 2 }", "0"),
        ("var a: Int = 1; a", "1"),
        ("var a: Bool = false; a", "false"),
        ("1 + if true then 2 else 3", "3"),
        ("var a = 1; if 1 == 2 then a = 2 else a = 3; a", "3"),
        ("(1 + 2) * 3", "9"),
        ("1 * (2 + 3)", "5"),
        ("(1 + 2) - 3", "0"),
        ("(1 - 2) * 3", "-3"),
        ("1 * (2 - 3)", "-1"),
        ("(1 + 2) / 3", "1"),
        ("1 / (2 + 3)", "0"),
        ("(1 - 2) / 3", "0"),
        ("1 / (2 - 3)", "-1"),
        ("(1 + 2) == 3", "true"),
        ("1 == (2 + 1)", "false"),
        ("(1 - 2) == -1", "true"),
        ("1 == (2 - 3)", "false"),
        ("(1 + 2) != 3", "false"),
        ("1 != (2 + 1)", "true"),
        ("(1 - 2) != -1", "false"),
        ("1 != (2 - 3)", "true"),
        ("(1 + 2) < 3", "false"),
        ("1 < (2 + 1)", "true"),
        ("(1 - 2) < -1", "false"),
        ("1 < (2 - 3)", "false"),
        ("(1 + 2) > 3", "false"),
        ("1 > (2 + 1)", "false"),
        ("(1 - 2) > -1", "false"),
        ("1 > (2 - 3)", "true"),
        ("(1 + 2) <= 3", "true"),
        ("1 <= (2 + 1)", "true"),
        ("(1 - 2) <= -1", "true"),
        ("1 <= (2 - 3)", "false"),
        ("(1 + 2) >= 3", "true"),
        ("1 >= (2 + 1)", "false"),
        ("(1 - 2) >= -1", "true"),
        ("1 >= (2 - 3)", "true"),
        ("if (true and false) then 1 else 2", "2"),
        ("if (true and { var a = 1; a == 1 }) then 1 else 2", "1"),
        ("var a = 1 + 2; a", "3"),
        ("var a = true and false; a", "false"),
        ("var a = 1; while (a < 10) do { a = a + 1 } a", "10"),
        ("var a = 1; var b = (a = 2); b", "2"),
        ("var a = 1; var b = 2; a = b = 3", "3"),
        ("const a = 1; a", "1"),
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_assembler_assemble(test_input: str, expected: str) -> None:
    tokens = tokenize(test_input)
    ast_node = parse(Tokens(tokens))
    typecheck(ast_node)
    ir_instructions = generate_ir(builtin_types, ast_node)
    asm_code = generate_assembly(ir_instructions)

    program_name = r"compiled_program_{test_input.replace(' ', '_')}"
    assemble(asm_code, program_name)

    program_path = os.path.join(root_dir, program_name)

    result = subprocess.run(program_path, stdout=subprocess.PIPE)

    pathlib.Path.unlink(pathlib.Path(program_path))

    assert result.returncode == 0
    assert result.stdout.decode("utf-8") == (f"{expected}\n" if expected else "")
