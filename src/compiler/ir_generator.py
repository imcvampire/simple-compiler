import compiler.ast as ast
import compiler.ir as ir
from compiler.ir import IRVar, SymTab, Label, Return
from compiler.type import Bool, Int, Type, Unit


def generate_ir(
    # 'root_types' parameter should map all global names
    # like 'print_int' and '+' to their types.
    root_types: dict[IRVar, Type],
    root_expr: ast.Expression,
) -> list[ir.Instruction]:
    return [Label(name="Start"), *_generate_ir(root_types, root_expr), Return()]


def _generate_ir(
    # 'root_types' parameter should map all global names
    # like 'print_int' and '+' to their types.
    root_types: dict[IRVar, Type],
    root_expr: ast.Expression,
) -> list[ir.Instruction]:
    var_types: dict[IRVar, Type] = root_types.copy()

    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar("unit")
    var_types[var_unit] = Unit

    next_var_number = 0
    next_label_number = 0

    def new_var(t: Type) -> IRVar:
        nonlocal next_var_number
        var = IRVar(f"v{next_var_number}")
        next_var_number += 1
        var_types[var] = t
        return var

    def new_label() -> ir.Label:
        nonlocal next_label_number
        label = ir.Label(f"L_{next_label_number}")
        next_label_number += 1
        return label

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[ir.Instruction] = []

    # This function visits an AST node,
    # appends IR instructions to 'ins',
    # and returns the IR variable where
    # the emitted IR instructions put the result.
    #
    # It uses a symbol table to map local variables
    # (which may be shadowed) to unique IR variables.
    # The symbol table will be updated in the same way as
    # in the interpreter and type checker.
    def visit(st: SymTab, expr: ast.Expression) -> IRVar:
        # loc = expr.location
        loc = None

        match expr:
            case ast.Literal():
                # Create an IR variable to hold the value,
                # and emit the correct instruction to
                # load the constant value.
                match expr.value:
                    case bool():
                        var = new_var(Bool)
                        ins.append(
                            ir.LoadBoolConst(
                                # loc,
                                expr.value,
                                var,
                            )
                        )
                    case int():
                        var = new_var(Int)
                        ins.append(
                            ir.LoadIntConst(
                                # loc,
                                expr.value,
                                var,
                            )
                        )
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(
                            f"{loc}: unsupported literal: {type(expr.value)}"
                        )

                # Return the variable that holds
                # the loaded value.
                return var

            case ast.Identifier():
                # Look up the IR variable that corresponds to
                # the source code variable.
                return st.require(expr.name)

            case ast.BinaryOp():
                # Ask the symbol table to return the variable that refers
                # to the operator to call.
                var_op = st.require(expr.op)
                # Recursively emit instructions to calculate the operands.
                var_left = visit(st, expr.left)
                var_right = visit(st, expr.right)
                # Generate variable to hold the result.
                var_result = new_var(expr.type)
                # Emit a Call instruction that writes to that variable.
                ins.append(
                    ir.Call(
                        # loc,
                        var_op,
                        [var_left, var_right],
                        var_result,
                    )
                )
                return var_result

            case ast.IfExpression():
                if expr.else_clause is None:
                    l_then = new_label()
                    l_end = new_label()

                    var_cond = visit(st, expr.condition)
                    ins.append(
                        ir.CondJump(
                            # loc,
                            var_cond,
                            l_then,
                            l_end,
                        )
                    )

                    ins.append(l_then)

                    visit(st, expr.then_clause)

                    ins.append(l_end)
                    return var_unit
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_cond = visit(st, expr.condition)
                    ins.append(
                        ir.CondJump(
                            # loc,
                            var_cond,
                            l_then,
                            l_else,
                        )
                    )
                    ins.append(l_then)

                    var_then = visit(st, expr.then_clause)
                    ins.append(
                        ir.Jump(
                            l_end,
                        )
                    )

                    ins.append(l_else)
                    var_else = visit(st, expr.else_clause)

                    ins.append(l_end)

                    return var_unit

            case _:
                raise Exception(f"{loc}: unsupported expression: {type(expr)}")

        # Other AST node cases (see below)

    # Convert 'root_types' into a SymTab
    # that maps all available global names to
    # IR variables of the same name.
    # In the Assembly generator stage, we will give
    # definitions for these globals. For now,
    # they just need to exist.
    root_symtab = SymTab([k for k in root_types.keys()])

    # Start visiting the AST from the root.
    var_final_result = visit(root_symtab, root_expr)

    if var_types[var_final_result] == Int:
        ins.append(
            ir.Call(
                # loc,
                IRVar("print_int"),
                [var_final_result],
                new_var(Int),
            )
        )
    elif var_types[var_final_result] == Bool:
        ins.append(
            ir.Call(
                # loc,
                IRVar("print_bool"),
                [var_final_result],
                new_var(Bool),
            )
        )

    return ins
