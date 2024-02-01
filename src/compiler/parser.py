from contextlib import contextmanager
from enum import Enum
from typing import Iterator

from compiler.ast import (
    Literal,
    BlockExpression,
    Expression,
    IfExpression,
    FunctionExpression,
    BinaryOp,
    VariableDeclarationExpression,
    Identifier,
)
from compiler.parser_exception import (
    EndOfInputException,
    VariableCannotBeDeclaredException,
    MissingSemicolonException,
)
from compiler.token import TokenType, Tokens

left_associative_binary_operators = [
    ["or"],
    ["and"],
    ["==", "!="],
    ["<", "<=", ">", ">="],
    ["+", "-"],
    ["*", "/"],
]


class Scope(Enum):
    TOP_LEVEL = 0
    BLOCK = 1
    LOCAL = 2


def parse(tokens: Tokens) -> Expression:
    current_scope = Scope.TOP_LEVEL

    @contextmanager
    def scope(new_scope: Scope) -> Iterator[None]:
        nonlocal current_scope
        prev_scope = current_scope

        try:
            current_scope = new_scope
            yield
        finally:
            current_scope = prev_scope

    def parse_int_literal() -> Literal:
        if tokens.peek().type != TokenType.INT_LITERAL:
            raise Exception(f"{tokens.peek().location}: expected an integer literal")
        token = tokens.consume()
        return Literal(int(token.text))

    def parse_bool_literal() -> Literal:
        if tokens.peek().type != TokenType.BOOL_LITERAL:
            raise Exception(f"{tokens.peek().location}: expected a bool literal")
        token = tokens.consume()
        return Literal(bool(token.text))

    def parse_identifier() -> Identifier:
        if tokens.peek().type != TokenType.IDENTIFIER:
            raise Exception(f"{tokens.peek().location}: expected an identifier")
        token = tokens.consume()
        return Identifier(token.text)

    def parse_parenthesized_expression() -> Expression:
        with scope(Scope.LOCAL):
            tokens.consume("(")
            expr = parse_expression()
            tokens.consume(")")
            return expr

    def parse_block_expression() -> Expression:
        tokens.consume("{")

        nested_expressions = []
        result: Expression = Literal(None)

        with scope(Scope.BLOCK):
            while tokens.peek().text != "}":
                nested_expression = parse_expression()
                nested_expressions.append(nested_expression)

                if (
                    isinstance(nested_expression, BlockExpression)
                    or isinstance(nested_expression, FunctionExpression)
                    or isinstance(nested_expression, IfExpression)
                ):
                    if tokens.peek().text == ";":
                        tokens.consume(";")
                    elif tokens.peek().text == "}":
                        result = nested_expressions.pop()
                else:
                    if tokens.peek().text == ";":
                        tokens.consume(";")
                    else:
                        result = nested_expressions.pop()
                        break

        if tokens.peek().text != "}":
            raise MissingSemicolonException(
                f"{tokens.peek().location}: expected a semicolon"
            )

        tokens.consume("}")

        return BlockExpression(nested_expressions, result)

    def parse_variable_declaration_expression() -> Expression:
        if current_scope not in [Scope.TOP_LEVEL, Scope.BLOCK]:
            raise VariableCannotBeDeclaredException(
                f"{tokens.peek().location}: variable declaration is not in local scope here"
            )

        tokens.consume("var")
        name = tokens.consume().text
        tokens.consume("=")
        value = parse_leaf_construct()
        return VariableDeclarationExpression(name, value)

    def parse_if_expression() -> Expression:
        with scope(Scope.LOCAL):
            tokens.consume("if")
            condition = parse_expression()
            tokens.consume("then")
            then_clause = parse_expression()
            if tokens.peek().text == "else":
                tokens.consume("else")
                else_clause = parse_expression()
            else:
                else_clause = None
            return IfExpression(condition, then_clause, else_clause)

    def parse_function_call() -> Expression:
        with scope(Scope.LOCAL):
            function_name = tokens.peek().text
            tokens.consume(function_name)
            tokens.consume("(")
            arguments = []
            while tokens.peek().text != ")":
                arguments.append(parse_expression())
                if tokens.peek().text == ",":
                    tokens.consume(",")
                elif tokens.peek().text == ")":
                    break
                else:
                    raise Exception(f"{tokens.peek().location}: expected a comma")
            tokens.consume(")")

            return FunctionExpression(function_name, arguments)

    def parse_leaf_construct() -> Expression:
        if tokens.peek().text == "(":
            return parse_parenthesized_expression()
        elif tokens.peek().text == "{":
            return parse_block_expression()
        elif tokens.peek().text == "var":
            return parse_variable_declaration_expression()
        elif tokens.peek().text == "if":
            return parse_if_expression()
        elif tokens.peek().type == TokenType.INT_LITERAL:
            return parse_int_literal()
        elif tokens.peek().type == TokenType.BOOL_LITERAL:
            return parse_bool_literal()
        elif (
            tokens.peek().type == TokenType.IDENTIFIER
            and tokens.next_token().text == "("
        ):
            return parse_function_call()
        elif tokens.peek().type == TokenType.IDENTIFIER:
            return parse_identifier()
        else:
            raise Exception(
                f"{tokens.peek().location}: wrong token, got: {tokens.peek().type}: {tokens.peek().text}"
            )

    def parse_left_associative_binary_operators(level: int) -> Expression:
        if level == len(left_associative_binary_operators):
            return parse_leaf_construct()

        left = parse_left_associative_binary_operators(level + 1)
        while tokens.peek().text in left_associative_binary_operators[level]:
            operator_token = tokens.consume()
            operator = operator_token.text
            right = parse_left_associative_binary_operators(level + 1)
            left = BinaryOp(left, operator, right)
        return left

    def parse_expression() -> Expression:
        left = parse_left_associative_binary_operators(1)

        while True:
            if tokens.peek().text in ["="]:  # right-associative
                operator_token = tokens.consume()
                operator = operator_token.text
                right = parse_expression()
                left = BinaryOp(left, operator, right)
            elif tokens.peek().text in left_associative_binary_operators[0]:
                operator_token = tokens.consume()
                operator = operator_token.text
                right = parse_left_associative_binary_operators(1)
                left = BinaryOp(left, operator, right)
            elif current_scope is Scope.TOP_LEVEL and tokens.peek().text == ";":
                consume = tokens.consume(";")
                left = BlockExpression([left, parse_expression()], Literal(None))
            else:
                return left

    if tokens.empty():
        return Literal(None)

    expression = parse_expression()

    if (
        current_scope is Scope.TOP_LEVEL
        and isinstance(expression, BlockExpression)
        and (
            tokens.prev_token().text not in [";", "}"]
            and len(expression.expressions) > 0
        )
    ):
        expression.result = expression.expressions.pop()

    if tokens.peek().type != TokenType.END:
        raise EndOfInputException()

    return expression
