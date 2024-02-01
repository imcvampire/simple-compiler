from typing import Optional

from compiler.ast import (
    Expression,
    BinaryOp,
    Literal,
    IfExpression,
    FunctionExpression,
    VariableDeclarationExpression,
    Identifier,
    BlockExpression,
)
from compiler.type import Int, Type, Bool, Unit
from compiler.type_checker_exception import (
    UnknownTypeException,
    IncompatibleTypeException,
    UnknownOperator,
)


def create_typecheck(
    types: list[Type], expected_types: list[Type], return_type: Type = None
):
    for i, t in enumerate(types):
        if t is not expected_types[i]:
            raise IncompatibleTypeException(
                f"Incompatible types. Expect {expected_types}, got: {types}"
            )

    return return_type if return_type is not None else expected_types[0]


def create_typecheck_binary_operator(
    operators: list[str], expected_type: Type, return_type: Type = None
):
    def _(operator: str, types: list[Type]) -> Type:
        if operator in operators:
            return create_typecheck(types, [expected_type, expected_type], return_type)
        raise UnknownOperator(f"Unknown operator: {operator}")

    return _


def typecheck_equal_operator(types: tuple[Type, Type]) -> Type:
    if types[0] is types[1]:
        return types[0]

    raise IncompatibleTypeException(
        f"Incompatible types. Expect {types[0]}, got: {types[1]}"
    )


operator_types = [
    (["+", "-", "*", "/"], create_typecheck_binary_operator(["+", "-", "*", "/"], Int)),
    (
        ["<", ">", "<=", ">=", "==", "!="],
        create_typecheck_binary_operator(["<", ">", "<=", ">=", "==", "!="], Int, Bool),
    ),
    (["and", "or"], create_typecheck_binary_operator(["and", "or"], Bool, Bool)),
    ("print_int", create_typecheck([Int], [Int])),
    ("print_bool", create_typecheck([Bool], [Bool])),
]


def typecheck(node: Expression) -> Type:
    identifier_types: Optional[dict[tuple[str, Type]]] = None

    def _typecheck(_node: Expression) -> Type:
        nonlocal identifier_types

        match _node:
            case Literal():
                match _node.value:
                    case bool():
                        return Bool
                    case int():
                        return Int
                    case None:
                        return Unit
                    case _:
                        raise UnknownTypeException(f"Unknown type: {_node.value}")
            case BinaryOp():
                t1 = _typecheck(_node.left)
                t2 = _typecheck(_node.right)

                if _node.op == "=":
                    return typecheck_equal_operator((t1, t2))
                else:
                    for operator, func in operator_types:
                        if _node.op in operator:
                            return func(_node.op, [t1, t2])

                raise UnknownOperator(f"Unknown operator: {_node.op}")
            case FunctionExpression():
                types = [_typecheck(arg) for arg in _node.arguments]
                if _node.name == "print_int":
                    return create_typecheck(types, [Int], Unit)
                elif _node.name == "print_bool":
                    return create_typecheck(types, [Bool], Unit)
                else:
                    # TODO: implement
                    return Unit
                    # return create_typecheck(types, [Int, Bool], Func)
            case IfExpression():
                t1 = _typecheck(_node.condition)
                if t1 is not Bool:
                    raise IncompatibleTypeException(
                        f"Incompatible types. Expect Bool, got: {t1}"
                    )
                t2 = _typecheck(_node.then_clause)
                if _node.else_clause is None:
                    return Unit
                else:
                    t3 = _typecheck(_node.else_clause)
                    if t2 is not t3:
                        raise IncompatibleTypeException(
                            f"Incompatible types. Got {t2} and {t3}"
                        )
                return t2
            case VariableDeclarationExpression():
                if identifier_types is None:
                    identifier_types = {}

                identifier_types[_node.name] = _typecheck(_node.value)
                return identifier_types[_node.name]
            case Identifier():
                if _node.name not in identifier_types.keys():
                    raise UnknownTypeException(f"Unknown identifier: {_node.name}")
                return identifier_types[_node.name]
            case BlockExpression():
                for expression in _node.expressions:
                    _typecheck(expression)
                return _typecheck(_node.result)

        raise UnknownTypeException(f"Unknown type: {_node}")

    return _typecheck(node)
