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
)
from compiler.parser_exception import (
    EndOfInputException,
    VariableCannotBeDeclaredException,
    MissingSemicolonException,
)
from compiler.token import Token, TokenType, Tokens

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
    LOCAL = 1


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

    def parse_identifier() -> Literal:
        if tokens.peek().type != TokenType.IDENTIFIER:
            raise Exception(f"{tokens.peek().location}: expected an identifier")
        token = tokens.consume()
        return Literal(token.text)

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
        has_result = False

        while tokens.peek().text != "}":
            nested_expression = parse_expression()
            nested_expressions.append(nested_expression)

            if not isinstance(nested_expression, Literal):
                if tokens.peek().text == ";":
                    tokens.consume(";")
                elif tokens.peek().text == "}":
                    result = nested_expressions.pop()
            else:
                if tokens.peek().text == ";":
                    tokens.consume(";")
                elif not has_result:
                    result = nested_expressions.pop()
                    has_result = True
                else:
                    raise MissingSemicolonException(
                        f"{tokens.peek().location}: expected a semicolon"
                    )

        tokens.consume("}")

        return BlockExpression(nested_expressions, result)

    def parse_variable_declaration_expression() -> Expression:
        if current_scope != Scope.TOP_LEVEL:
            raise VariableCannotBeDeclaredException(
                f"{tokens.peek().location}: variable declaration is not in local scope here"
            )

        tokens.consume("var")
        name = tokens.consume().text
        tokens.consume("=")
        value = parse_expression()
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
            else:
                return left

    if tokens.empty():
        return Literal(None)

    expression = parse_expression()

    if tokens.peek().type != TokenType.END:
        raise EndOfInputException()

    return expression
