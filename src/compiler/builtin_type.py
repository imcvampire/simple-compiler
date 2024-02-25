from compiler.ir import IRVar
from compiler.type import Unit, Type, Int

builtin_unit_types: dict[IRVar, Type] = {
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

builtin_types: dict[IRVar, Type] = {
    **builtin_unit_types,
    IRVar("read_int"): Int
}
