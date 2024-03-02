from dataclasses import dataclass

from compiler.ir import Label
from typing import TypeVar, Generic

IrGeneratorState = TypeVar("IrGeneratorState")


@dataclass
class WhileIrGeneratorState(Generic[IrGeneratorState]):
    label_start: Label
    label_end: Label
