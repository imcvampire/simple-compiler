from dataclasses import dataclass, field
from typing import Optional

from compiler.type import Unit, Type


@dataclass
class TypeExpression:
    pass


class IntTypeExpression(TypeExpression):
    pass


class BoolTypeExpression(TypeExpression):
    pass


class UnitTypeExpression(TypeExpression):
    pass


@dataclass
class Expression:
    type: Type = field(kw_only=True, default=Unit)


@dataclass
class Literal(Expression):
    value: int | bool | None


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class BinaryOp(Expression):
    left: Expression | None
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
class VariableDeclarationExpression(Expression):
    name: str
    value: Expression
    type_expression: Optional[TypeExpression | None] = None


@dataclass
class ForExpression(Expression):
    condition: Expression
    body: BlockExpression
    # TODO
    # initial: Optional[Expression] = None
    # increment: Optional[Expression] = None

