from compiler.ir import IRVar
from compiler.type import Unit, Type

builtin_types: dict[IRVar, Type] = {
    IRVar(name): Unit
    for name in [
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
        "unary_-",
        "unary_not",
        "print_int",
        "print_bool",
    ]
}
