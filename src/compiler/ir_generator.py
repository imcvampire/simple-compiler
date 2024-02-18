import typing

import compiler.ast as ast
import compiler.ir as ir
from compiler.ir import (
    IRVar,
    SymTab,
    Label,
    Return,
    Call,
    CondJump,
    Jump,
    Copy,
    LoadBoolConst,
    LoadIntConst,
)
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
        label = ir.Label(f"L{next_label_number}")
        next_label_number += 1
        return label

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[ir.Instruction] = []

    def add_ending_print_ir(var_final: IRVar) -> None:
        # if var_final is None:
        #     return
        if var_types[var_final] == Int:
            ins.append(
                Call(
                    # loc,
                    IRVar("print_int"),
                    [var_final],
                    new_var(Int),
                )
            )
        elif var_types[var_final] == Bool:
            ins.append(
                Call(
                    # loc,
                    IRVar("print_bool"),
                    [var_final],
                    new_var(Bool),
                )
            )

    def handle_logical_operation(
        st: SymTab, expr: ast.Expression, operation: typing.Literal["and", "or"]
    ) -> IRVar:
        label_skip = new_label()
        label_right = new_label()
        label_end = new_label()

        var_result = new_var(Bool)

        var_left = visit(st, expr.left)

        match operation:
            case "and":
                ins.append(CondJump(var_left, label_right, label_skip))
            case "or":
                ins.append(CondJump(var_left, label_skip, label_right))

        ins.append(label_skip)
        ins.append(LoadBoolConst(operation == "or", var_result))
        ins.append(Jump(label_end))

        ins.append(label_right)
        var_right = visit(st, expr.right)
        ins.append(Copy(var_right, var_result))
        ins.append(Jump(label_end))

        ins.append(label_end)

        return var_result

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
                match expr.value:
                    case bool():
                        var = new_var(Bool)
                        ins.append(
                            LoadBoolConst(
                                # loc,
                                expr.value,
                                var,
                            )
                        )
                    case int():
                        var = new_var(Int)
                        ins.append(
                            LoadIntConst(
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
                var_op = st.require(expr.op)

                match var_op.name:
                    case "=":
                        if not isinstance(expr.left, ast.Identifier):
                            raise Exception(
                                f"{loc}: left-hand side of assignment must be an identifier"
                            )

                        var_left = st.require(expr.left.name)
                        var_right = visit(st, expr.right)

                        ins.append(Copy(var_right, var_left))

                        return var_unit
                    case "and":
                        return handle_logical_operation(st, expr, "and")
                    case "or":
                        return handle_logical_operation(st, expr, "or")
                    case _:
                        var_left = visit(st, expr.left)
                        var_right = visit(st, expr.right)

                        var_result = new_var(expr.type)

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
                        CondJump(
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
                        CondJump(
                            # loc,
                            var_cond,
                            l_then,
                            l_else,
                        )
                    )
                    ins.append(l_then)

                    var_then = visit(st, expr.then_clause)
                    ins.append(
                        Jump(
                            l_end,
                        )
                    )

                    ins.append(l_else)
                    var_else = visit(st, expr.else_clause)

                    ins.append(l_end)

                    return var_unit

            case ast.BlockExpression():
                for subexpr in expr.expressions:
                    visit(st, subexpr)

                if expr.result is not None:
                    return visit(st, expr.result)

            case ast.VariableDeclarationExpression():
                var_value = visit(st, expr.value)
                var = new_var(expr.type)

                ins.append(Copy(var_value, var))

                st.add_local(expr.name, var)

                return var

            case ast.FunctionExpression():
                var_op = st.require(expr.name)
                var_args = [visit(st, arg) for arg in expr.arguments]

                var_result = new_var(expr.type)

                ins.append(Call(var_op, var_args, var_result))

                return var_result

            case _:
                raise Exception(f"{loc}: unsupported expression: {type(expr)}")

        # Other AST node cases (see below)

    # Convert 'root_types' into a SymTab
    # that maps all available global names to
    # IR variables of the same name.
    # In the Assembly generator stage, we will give
    # definitions for these globals. For now,
    # they just need to exist.
    root_symtab = SymTab([(k.name, k) for k in root_types.keys()])

    # Start visiting the AST from the root.
    var_final_result = visit(root_symtab, root_expr)

    match root_expr:
        case ast.BlockExpression():
            if root_expr.result is not None:
                add_ending_print_ir(var_final_result)
        case _:
            add_ending_print_ir(var_final_result)

    return ins
