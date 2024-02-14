from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Optional, Any


@dataclass(frozen=True)
class IRVar:
    """Represents the name of a memory location or built-in."""

    name: str

    def __str__(self) -> str:
        return self.name


@dataclass
class SymTab:
    symbols: list[IRVar]
    parent: Optional[SymTab] = None

    def add_local(self, symbol: IRVar) -> None:
        if symbol in self.symbols:
            raise Exception(f"symbol {symbol} already defined")

        self.symbols.append(symbol)

    def find(self, symbol: IRVar) -> Optional[IRVar]:
        if symbol in self.symbols:
            return self.symbols[self.symbols.index(symbol)]

        if self.parent:
            return self.parent.find(symbol)

        return None

    def require(self, name: str) -> IRVar:
        if name in [
            "=",
            "+",
            "-",
            "*",
            "/",
            ">",
            "<",
            ">=",
            "<=",
            "==",
            "!=",
            "and",
            "or",
        ]:
            return IRVar(name)

        result = self.find(IRVar(name))

        if result is None:
            raise Exception(f"symbol {name} not found")

        return result

    def __getitem__(self, item: IRVar) -> Optional[IRVar]:
        return self.find(item)


@dataclass(frozen=True)
class Instruction:
    """Base class for IR instructions."""

    # location: Location

    def __str__(self) -> str:
        """Returns a string representation similar to
        our IR code examples, e.g. 'LoadIntConst(3, x1)'"""

        def format_value(v: Any) -> str:
            if isinstance(v, list):
                return f'[{", ".join(format_value(e) for e in v)}]'
            else:
                return str(v)

        args = ", ".join(
            format_value(getattr(self, field.name))
            for field in dataclasses.fields(self)
            if field.name != "location"
        )
        return f"{type(self).__name__}({args})"


@dataclass(frozen=True)
class LoadBoolConst(Instruction):
    """Loads a boolean constant value to `dest`."""

    value: bool
    dest: IRVar


@dataclass(frozen=True)
class LoadIntConst(Instruction):
    """Loads a constant value to `dest`."""

    value: int
    dest: IRVar


@dataclass(frozen=True)
class Copy(Instruction):
    """Copies a value from one variable to another."""

    source: IRVar
    dest: IRVar


@dataclass(frozen=True)
class Call(Instruction):
    """Calls a function or built-in."""

    fun: IRVar
    args: list[IRVar]
    dest: IRVar


@dataclass(frozen=True)
class Jump(Instruction):
    """Unconditionally continues execution from the given label."""

    label: Label


@dataclass(frozen=True)
class CondJump(Instruction):
    """Continues execution from `then_label` if `cond` is true, otherwise from `else_label`."""

    cond: IRVar
    then_label: Label
    else_label: Label


@dataclass(frozen=True)
class Label(Instruction):
    """Marks the destination of a jump instruction."""

    name: str


@dataclass(frozen=True)
class Return(Instruction):
    """Returns from the current function."""

    pass
