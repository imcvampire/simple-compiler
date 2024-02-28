from __future__ import annotations

from dataclasses import dataclass

import compiler.ir as ir


@dataclass
class BasicBlock:
    instructions: list[ir.Instruction]


@dataclass
class FlowNode:
    name: str
    block: BasicBlock
    next: list[FlowNode]
    prev: list[FlowNode]


def create_basic_block(instructions: list[ir.Instruction]) -> list[BasicBlock]:
    if len(instructions) == 0:
        raise Exception("Instructions cannot be empty")

    blocks = []
    current_block = BasicBlock(instructions=[])

    for instruction in instructions:
        if isinstance(instruction, ir.Label):
            if len(current_block.instructions) == 0:
                current_block.instructions.append(instruction)
            else:
                blocks.append(current_block)
                current_block = BasicBlock(instructions=[instruction])
        else:
            current_block.instructions.append(instruction)

            if isinstance(instruction, ir.Jump | ir.CondJump | ir.Return):
                blocks.append(current_block)
                current_block = BasicBlock(instructions=[])

    return blocks


def create_flow_graph(blocks: list[BasicBlock]) -> dict[str, FlowNode]:
    if len(blocks) == 0:
        raise Exception("Blocks cannot be empty")

    flow_graph = {}

    for block in blocks:
        if len(block.instructions) == 0:
            raise Exception("Block cannot be empty")

        if isinstance(block.instructions[0], ir.Label):
            name = block.instructions[0].name
        else:
            raise Exception("First instruction should be a label")

        flow_graph[name] = FlowNode(name=name, block=block, next=[], prev=[])

    for index, block in enumerate(blocks):
        if isinstance(block.instructions[0], ir.Label):
            name = block.instructions[0].name
        else:
            raise Exception("First instruction should be a label")

        last_instruction = block.instructions[-1]

        if isinstance(last_instruction, ir.Jump):
            next_name = last_instruction.label.name
            flow_graph[name].next.append(flow_graph[next_name])
            flow_graph[next_name].prev.append(flow_graph[name])
        elif isinstance(last_instruction, ir.CondJump):
            then_name = last_instruction.then_label.name
            else_name = last_instruction.else_label.name
            flow_graph[name].next.append(flow_graph[then_name])
            flow_graph[then_name].prev.append(flow_graph[name])
            flow_graph[name].next.append(flow_graph[else_name])
            flow_graph[else_name].prev.append(flow_graph[name])
        elif isinstance(last_instruction, ir.Return):
            pass
        else:
            if index + 1 >= len(blocks):
                raise Exception("No next block")

            next_block = blocks[index + 1]
            if isinstance(next_block.instructions[0], ir.Label):
                next_name = next_block.instructions[0].name
            else:
                raise Exception("First instruction should be a label")

            flow_graph[name].next.append(flow_graph[next_name])
            flow_graph[next_name].prev.append(flow_graph[name])

    return flow_graph
