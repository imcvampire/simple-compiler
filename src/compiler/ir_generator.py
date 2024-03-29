import sys
import typing
from contextlib import contextmanager

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
from compiler.ir_generator_state import IrGeneratorState, WhileIrGeneratorState
from compiler.type import Bool, Int, Type, Unit, ConstInt, ConstBool


def generate_ir(
    root_types: dict[IRVar, Type],
    root_expr: ast.Expression,
) -> list[ir.Instruction]:
    return [Label(name="Start"), *__generate_ir(root_types, root_expr), Return()]


def __generate_ir(
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
        if var_types[var_final] in [Int, ConstInt]:
            ins.append(
                Call(
                    # loc,
                    IRVar("print_int"),
                    [var_final],
                    new_var(Int),
                )
            )
        elif var_types[var_final] in [Bool, ConstBool]:
            ins.append(
                Call(
                    # loc,
                    IRVar("print_bool"),
                    [var_final],
                    new_var(Bool),
                )
            )

    def visit_logical_operation(
        st: SymTab, expr: ast.BinaryOp, operation: typing.Literal["and", "or"]
    ) -> IRVar:
        if expr.left is None:
            raise Exception(
                "Wrong left-hand side of binary operation. It should not be None."
            )

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

    __current_states = []

    @contextmanager
    def state(new_state: IrGeneratorState) -> typing.Iterator[None]:
        nonlocal __current_states
        try:
            __current_states.append(new_state)
            yield
        finally:
            __current_states.pop()

    def get_state(state_type: type[IrGeneratorState]) -> IrGeneratorState | None:
        for s in reversed(__current_states):
            if isinstance(s, state_type):
                return s
        return None

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
                var_op = (
                    st.require(expr.op)
                    if expr.left is not None
                    else st.require(f"unary_{expr.op}")
                )

                match var_op.name:
                    case "=":
                        if not isinstance(expr.left, ast.Identifier):
                            raise Exception(
                                f"{loc}: left-hand side of assignment must be an identifier"
                            )

                        var_left = st.require(expr.left.name)
                        var_right = visit(st, expr.right)

                        ins.append(Copy(var_right, var_left))

                        return var_left
                    case "and":
                        return visit_logical_operation(st, expr, "and")
                    case "or":
                        return visit_logical_operation(st, expr, "or")
                    case _:
                        if expr.left is None:
                            var_right = visit(st, expr.right)

                            var_result = new_var(expr.type)

                            ins.append(
                                ir.Call(
                                    # loc,
                                    var_op,
                                    [var_right],
                                    var_result,
                                )
                            )

                            return var_result

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

                    var_result = new_var(expr.type)

                    ins.append(l_then)

                    var_then = visit(st, expr.then_clause)
                    ins.append(Copy(var_then, var_result))
                    ins.append(
                        Jump(
                            l_end,
                        )
                    )

                    ins.append(l_else)
                    var_else = visit(st, expr.else_clause)
                    ins.append(Copy(var_else, var_result))

                    ins.append(l_end)

                    return var_result

            case ast.BlockExpression():
                child_st = SymTab(symbols=[], parent=st)

                for subexpr in expr.expressions:
                    visit(child_st, subexpr)

                if expr.result is not None:
                    return visit(child_st, expr.result)

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

            case ast.WhileExpression():
                label_start = new_label()
                label_body = new_label()
                label_end = new_label()

                ins.append(label_start)

                var_condition = visit(st, expr.condition)

                ins.append(CondJump(var_condition, label_body, label_end))

                ins.append(label_body)

                with state(WhileIrGeneratorState(label_start, label_end)):
                    visit(SymTab(symbols=[], parent=st), expr.body)

                ins.append(Jump(label_start))

                ins.append(label_end)

                return var_unit

            case ast.BreakExpression() | ast.ContinueExpression():
                s = get_state(WhileIrGeneratorState)

                if s is None:
                    raise Exception(f"{loc}: break/continue outside of a loop")
                else:
                    match expr:
                        case ast.BreakExpression():
                            ins.append(Jump(s.label_end))
                        case ast.ContinueExpression():
                            ins.append(Jump(s.label_start))
                        case _:
                            sys.exit("Unreachable code")

                    return var_unit

            case _:
                raise Exception(f"{loc}: unsupported expression: {type(expr)}")

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
        case ast.WhileExpression() | ast.VariableDeclarationExpression():
            pass
        case _:
            add_ending_print_ir(var_final_result)

    return ins
