from dataclasses import dataclass


@dataclass
class Expression:
    pass


@dataclass
class Literal(Expression):
    value: str | int | bool | None
    # (value=None is used when parsing the keyword `unit`)


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression
