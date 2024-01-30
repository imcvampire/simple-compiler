from dataclasses import dataclass
from typing import Optional


@dataclass
class Expression:
    pass


@dataclass
class Literal(Expression):
    value: str | int | bool | None


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass
class IfExpression(Expression):
    condition: Expression
    then_clause: Expression
    else_clause: Expression | None = None


@dataclass
class FunctionExpression(Expression):
    name: str
    arguments: list[Expression]


@dataclass
class BlockExpression(Expression):
    expressions: list[Expression]
    result: Optional[Expression]
