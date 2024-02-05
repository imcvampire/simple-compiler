from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Expression:
    pass


@dataclass
class Literal(Expression):
    value: int | bool | None


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
    arguments: list[Expression] = field(default_factory=list)


@dataclass
class BlockExpression(Expression):
    expressions: list[Expression] = field(default_factory=list)
    result: Expression = field(default_factory=lambda: Literal(None))


@dataclass
class TypeExpression(Expression):
    type: str


@dataclass
class VariableDeclarationExpression(Expression):
    name: str
    value: Expression
    type: Optional[TypeExpression | None] = None
