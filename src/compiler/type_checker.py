from compiler.type import Int, Type, Bool, Unit, Function

from compiler.ast import Expression, BinaryOp, Literal, IfExpression, FunctionExpression
from compiler.type_checker_exception import (
    UnknownTypeException,
    IncompatibleTypeException,
)


def typecheck(node: Expression) -> Type:
    match node:
        case Literal():
            match node.value:
                case bool():
                    return Bool
                case int():
                    return Int
                case _:
                    raise UnknownTypeException(f"Unknown type: {node.value}")
        case BinaryOp():
            t1 = typecheck(node.left)
            t2 = typecheck(node.right)
            if node.op in ["+", "-", "*", "/"]:
                if t1 is not Int or t2 is not Int:
                    raise IncompatibleTypeException(
                        f"Incompatible types. Expect Int, got: {t1} and {t2}"
                    )
                return Int
            elif node.op in ["<", ">", "<=", ">=", "==", "!="]:
                if t1 is not Int or t2 is not Int:
                    raise IncompatibleTypeException(
                        f"Incompatible types. Expect Int, got: {t1} and {t2}"
                    )
                return Bool
            elif node.op in ["and", "or"]:
                if t1 is not Bool or t2 is not Bool:
                    raise IncompatibleTypeException(
                        f"Incompatible types. Expect Bool, got: {t1} and {t2}"
                    )
                return Bool
            else:
                pass
        case IfExpression():
            t1 = typecheck(node.condition)
            if t1 is not Bool:
                raise IncompatibleTypeException(
                    f"Incompatible types. Expect Bool, got: {t1}"
                )
            t2 = typecheck(node.then_clause)
            if node.else_clause is None:
                return Unit
            else:
                t3 = typecheck(node.else_clause)
                if t2 is not t3:
                    raise IncompatibleTypeException(
                        f"Incompatible types. Got {t2} and {t3}"
                    )
            return t2
        case FunctionExpression():
            return Function

    raise UnknownTypeException(f"Unknown type: {node}")
