from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import compiler.ir as ir


@dataclass
class BasicBlock:
    instructions: list[ir.Instruction]


def create_basic_block(instructions: list[ir.Instruction]) -> list[BasicBlock]:
    if len(instructions) == 0:
        raise Exception("Instructions cannot be empty")

    blocks = []
    current_block = BasicBlock(instructions=[])

    for instruction in instructions:
        if isinstance(instruction, ir.Label) and len(current_block.instructions) != 0:
            raise Exception("Label should be the first instruction in a block")

        current_block.instructions.append(instruction)

        if isinstance(instruction, ir.Jump | ir.CondJump | ir.Return):
            blocks.append(current_block)
            current_block = BasicBlock(instructions=[])

    return blocks
