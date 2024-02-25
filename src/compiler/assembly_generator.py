import dataclasses

import compiler.ir as ir
from compiler.assembler_exception import (
    UnknownFunction,
    TooManyArguments,
    WrongNumberOfArguments,
)
from compiler.intrinsics import all_intrinsics, IntrinsicArgs

byte_size = 8


class Locals:
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {}
        self._stack_used = byte_size

        for v in variables:
            self._var_to_location[v] = f"-{self._stack_used}(%rbp)"
            self._stack_used += byte_size

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used


def get_all_ir_variables(instructions: list[ir.Instruction]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(var: ir.IRVar) -> None:
        if var not in result_set:
            result_list.append(var)
            result_set.add(var)

    for insn in instructions:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        add(v)
    return result_list


def generate_assembly(instructions: list[ir.Instruction]) -> str:
    lines = []

    def emit(line: str) -> None:
        lines.append(line)

    locals = Locals(get_all_ir_variables(instructions))

    emit(".extern print_int")
    emit(".extern print_bool")
    emit(".extern read_int")

    emit(".global main")
    emit(".type main, @function")

    emit("")
    emit(".section .text")

    emit("")
    emit("main:")

    emit("pushq %rbp")
    emit("movq %rsp, %rbp")
    emit(f"subq ${locals.stack_used()}, %rsp")

    for insn in instructions:
        emit("")

        if not isinstance(insn, ir.Label):
            emit("# " + str(insn))

        match insn:
            case ir.Label():
                emit(f".L{insn.name}:")

            case ir.LoadIntConst():
                if -(2**31) <= insn.value < 2**31:
                    emit(f"movq ${insn.value}, {locals.get_ref(insn.dest)}")
                else:
                    emit(f"movabsq ${insn.value}, %rax")
                    emit(f"movq %rax, {locals.get_ref(insn.dest)}")

            case ir.LoadBoolConst():
                emit(f"movq ${1 if insn.value else 0}, {locals.get_ref(insn.dest)}")

            case ir.Copy():
                emit(f"movq {locals.get_ref(insn.source)}, %rax")
                emit(f"movq %rax, {locals.get_ref(insn.dest)}")

            case ir.Jump():
                emit(f"jmp .L{insn.label.name}")

            case ir.Call():
                if len(insn.args) > 6:
                    raise TooManyArguments(
                        f"Too many arguments for function call: {insn.fun.name}"
                    )

                if (intrinsic := all_intrinsics.get(insn.fun.name)) is not None:
                    args = IntrinsicArgs(
                        [locals.get_ref(arg) for arg in insn.args], "%rax", emit
                    )

                    intrinsic(args)

                elif insn.fun.name in ["print_int", "print_bool"]:
                    if len(insn.args) != 1:
                        raise WrongNumberOfArguments(
                            f"Wrong number of arguments for function call: {insn.fun.name}. Expected 1, got {len(insn.args)}"
                        )

                    emit(f"movq {locals.get_ref(insn.args[0])}, %rdi")
                    emit(f"call {insn.fun.name}")
                elif insn.fun.name == "read_int":
                    if len(insn.args) != 0:
                        raise WrongNumberOfArguments(
                            f"Wrong number of arguments for function call: {insn.fun.name}. Expected 0, got {len(insn.args)}"
                        )

                    emit(f"call {insn.fun.name}")
                else:
                    raise UnknownFunction(f"Unknown function: {insn.fun.name}")

                emit(f"movq %rax, {locals.get_ref(insn.dest)}")

            case ir.CondJump():
                emit(f"cmpq $0, {locals.get_ref(insn.cond)}")
                emit(f"jne .L{insn.then_label.name}")
                emit(f"jmp .L{insn.else_label.name}")

            case ir.Return():
                emit("movq $0, %rax")
                emit("movq %rbp, %rsp")
                emit("popq %rbp")
                emit("ret")

            case _:
                raise ValueError(f"Unknown instruction: {insn}")

    emit("")

    return "\n".join(lines)
