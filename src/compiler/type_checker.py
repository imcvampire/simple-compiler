import typing
from typing import Optional, Callable

from compiler.ast import (
    Expression,
    BinaryOp,
    Literal,
    IfExpression,
    FunctionExpression,
    VariableDeclarationExpression,
    Identifier,
    BlockExpression,
    IntTypeExpression,
    BoolTypeExpression,
    UnitTypeExpression,
    TypeExpression,
)
from compiler.type import Int, Type, Bool, Unit
from compiler.type_checker_exception import (
    UnknownTypeException,
    IncompatibleTypeException,
    UnknownOperator,
)


def create_typecheck(
    expected_types: list[Type], return_type: Optional[Type] = None
) -> Callable[[list[Type]], Type]:
    def _(types: list[Type]) -> Type:
        for i, t in enumerate(types):
            if t is not expected_types[i]:
                raise IncompatibleTypeException(
                    f"Incompatible types. Expect {expected_types}, got: {types}"
                )

        return return_type if return_type is not None else expected_types[0]

    return _


def create_typecheck_binary_operator(
    operators: list[str], expected_type: Type, return_type: Optional[Type] = None
) -> Callable[[list[Type]], Type]:
    def _(types: list[Type]) -> Type:
        return create_typecheck([expected_type, expected_type], return_type)(types)

    return _


def typecheck_equal_operator(types: tuple[Type, Type]) -> Type:
    if types[0] is types[1]:
        return types[0]

    raise IncompatibleTypeException(
        f"Incompatible types. Expect {types[0]}, got: {types[1]}"
    )


operator_types: list[tuple[list[str], Callable[[list[Type]], Type]]] = [
    (["+", "-", "*", "/"], create_typecheck_binary_operator(["+", "-", "*", "/"], Int)),
    (
        ["<", ">", "<=", ">=", "==", "!="],
        create_typecheck_binary_operator(["<", ">", "<=", ">=", "==", "!="], Int, Bool),
    ),
    (["and", "or"], create_typecheck_binary_operator(["and", "or"], Bool, Bool)),
    (["print_int"], create_typecheck([Int], Int)),
    (["print_bool"], create_typecheck([Bool], Bool)),
]

ast_types: list[tuple[typing.Type[TypeExpression], Type]] = [
    (IntTypeExpression, Int),
    (BoolTypeExpression, Bool),
    (UnitTypeExpression, Unit),
]


def typecheck(
    node: Expression, identifier_types: Optional[dict[str, Type]] = None
) -> Type:
    node.type = _typecheck(node, identifier_types)
    return node.type


def _typecheck(
    node: Expression, identifier_types: Optional[dict[str, Type]] = None
) -> Type:
    match node:
        case Literal():
            match node.value:
                case bool():
                    return Bool
                case int():
                    return Int
                case None:
                    return Unit
                case _:
                    raise UnknownTypeException(f"Unknown type: {node.value}")
        case BinaryOp():
            t1 = typecheck(node.left, identifier_types)
            t2 = typecheck(node.right, identifier_types)

            if node.op == "=":
                return typecheck_equal_operator((t1, t2))
            else:
                for operator, func in operator_types:
                    if node.op in operator:
                        return func([t1, t2])

            raise UnknownOperator(f"Unknown operator: {node.op}")
        case FunctionExpression():
            types = [typecheck(arg, identifier_types) for arg in node.arguments]
            for operator, func in operator_types:
                if node.name in operator:
                    return func(types)
            else:
                # TODO: implement
                return Unit
                # return create_typecheck(types, [Int, Bool], Func)
        case IfExpression():
            t1 = typecheck(node.condition, identifier_types)
            if t1 is not Bool:
                raise IncompatibleTypeException(
                    f"Incompatible types. Expect Bool, got: {t1}"
                )
            t2 = typecheck(node.then_clause, identifier_types)
            if node.else_clause is None:
                return Unit
            else:
                t3 = typecheck(node.else_clause, identifier_types)
                if t2 is not t3:
                    raise IncompatibleTypeException(
                        f"Incompatible types. Got {t2} and {t3}"
                    )
            return t2
        case VariableDeclarationExpression():
            if identifier_types is None:
                identifier_types = {}

            identifier_types[node.name] = typecheck(node.value, identifier_types)

            if node.type is not None:
                for type_expression, _type in ast_types:
                    if isinstance(node.type_expression, type_expression):
                        if identifier_types[node.name] is not _type:
                            raise IncompatibleTypeException(
                                f"Incompatible types. Expect {_type}, got: {identifier_types[node.name]}"
                            )

            return identifier_types[node.name]
        case Identifier():
            if identifier_types is None:
                raise UnknownTypeException(f"Unknown identifier: {node.name}")

            if node.name not in identifier_types.keys():
                raise UnknownTypeException(f"Unknown identifier: {node.name}")

            return identifier_types[node.name]
        case BlockExpression():
            _identifier_types = identifier_types
            if identifier_types is None:
                _identifier_types = {}

            for expression in node.expressions:
                typecheck(expression, _identifier_types)

            return typecheck(node.result, _identifier_types)

    raise UnknownTypeException(f"Unknown type: {node}")
