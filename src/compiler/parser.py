import sys
from contextlib import contextmanager
from enum import Enum
from typing import Iterator, Optional

from compiler.ast import (
    Literal,
    BlockExpression,
    Expression,
    IfExpression,
    FunctionExpression,
    BinaryOp,
    VariableDeclarationExpression,
    Identifier,
    BoolTypeExpression,
    IntTypeExpression,
    WhileExpression,
    BreakExpression,
    ContinueExpression,
)
from compiler.parser_exception import (
    EndOfInputException,
    VariableCannotBeDeclaredException,
    MissingSemicolonException,
    MissingTypeException,
    UnknownTypeException,
    WrongTokenException,
    WrongScopeException,
)
from compiler.token import TokenType, Tokens

left_associative_binary_operators = [
    ["or"],
    ["and"],
    ["==", "!="],
    ["<", "<=", ">", ">="],
    ["+", "-"],
    ["*", "/", "%"],
]


# TODO: Change to class seems clearer
class Scope(Enum):
    TOP_LEVEL = 0
    TOP_LEVEL_EXPRESSION = 1
    BLOCK = 2
    LOCAL = 3
    WHILE = 4


def parse(tokens: Tokens) -> Expression:
    __current_scopes = [Scope.TOP_LEVEL]

    @contextmanager
    def scope(new_scope: Scope) -> Iterator[None]:
        nonlocal __current_scopes
        try:
            __current_scopes.append(new_scope)
            yield
        finally:
            __current_scopes.pop()

    def has_scope(
        scopes: list[Scope] | Scope, recurrsive: Optional[bool] = False
    ) -> bool:
        if recurrsive:
            if isinstance(scopes, list):
                return any(s in __current_scopes for s in scopes)
            else:
                return scopes in __current_scopes
        else:
            if isinstance(scopes, list):
                return __current_scopes[-1] in scopes
            else:
                return __current_scopes[-1] == scopes

    def parse_int_literal() -> Literal:
        if tokens.peek().type != TokenType.INT_LITERAL:
            raise Exception(f"{tokens.peek().location}: expected an integer literal")
        token = tokens.consume()
        return Literal(int(token.text))

    def parse_bool_literal() -> Literal:
        if tokens.peek().type != TokenType.BOOL_LITERAL:
            raise Exception(f"{tokens.peek().location}: expected a bool literal")
        token = tokens.consume()
        return Literal(True if token.text == "true" else False)

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

    def parse_block_expression() -> BlockExpression:
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
                    elif isinstance(nested_expression, BlockExpression|WhileExpression):
                        pass
                    else:
                        result = nested_expressions.pop()
                        break

        if tokens.peek().text != "}":
            raise MissingSemicolonException(
                f"{tokens.peek().location}: expected a closing brace"
            )

        tokens.consume("}")

        return BlockExpression(nested_expressions, result)

    def parse_variable_declaration_expression() -> Expression:
        if not has_scope(
            [
                Scope.TOP_LEVEL,
                Scope.TOP_LEVEL_EXPRESSION,
                Scope.BLOCK,
            ]
        ):
            raise VariableCannotBeDeclaredException(
                f"{tokens.peek().location}: variable declaration is not in local scope here"
            )

        if (kind := tokens.peek().text) not in ["var", "const"]:
            raise Exception(
                f"{tokens.peek().location}: expected a var or const keyword"
            )

        tokens.consume(kind)

        name = tokens.consume().text
        var_type: Optional[IntTypeExpression | BoolTypeExpression] = None
        if tokens.peek().text == ":":
            tokens.consume(":")

            if tokens.peek().type != TokenType.TYPE:
                raise MissingTypeException(f"{tokens.peek().location}: expected a type")
            elif tokens.peek().text not in ["Int", "Bool"]:
                raise UnknownTypeException(f"{tokens.peek().location}: unknown type")

            match tokens.consume().text:
                case "Int":
                    var_type = IntTypeExpression()
                case "Bool":
                    var_type = BoolTypeExpression()

        tokens.consume("=")
        value = parse_left_associative_binary_operators(1)
        return VariableDeclarationExpression(name, value, var_type, kind == "const")

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

    def parse_while_expression() -> Expression:
        with scope(Scope.WHILE):
            tokens.consume("while")
            condition = parse_expression()
            tokens.consume("do")
            body = parse_block_expression()
            return WhileExpression(condition, body)

    def parse_leaf_construct() -> Expression:
        if tokens.peek().text == "(":
            return parse_parenthesized_expression()
        elif tokens.peek().text == "{":
            return parse_block_expression()
        elif tokens.peek().text in ["var", "const"]:
            return parse_variable_declaration_expression()
        elif tokens.peek().text == "if":
            return parse_if_expression()
        elif tokens.peek().text == "while":
            return parse_while_expression()
        elif tokens.peek().text in ["-", "not"]:
            token = tokens.consume(tokens.peek().text)
            return BinaryOp(None, token.text, parse_leaf_construct())
        elif tokens.peek().type == TokenType.INT_LITERAL:
            return parse_int_literal()
        elif tokens.peek().type == TokenType.BOOL_LITERAL:
            return parse_bool_literal()
        elif tokens.peek().text in ["break", "continue"]:
            if not has_scope(Scope.WHILE, True):
                raise WrongScopeException(
                    f"{tokens.peek().location}: {tokens.peek().text} statement must be used inside a while loop"
                )

            tokens.consume(tokens.peek().text)

            match tokens.prev_token().text:
                case "break":
                    return BreakExpression()
                case "continue":
                    return ContinueExpression()
                case _:
                    sys.exit("Unreachable code")
        elif (
            tokens.peek().type == TokenType.IDENTIFIER
            and tokens.next_token().text == "("
        ):
            return parse_function_call()
        elif tokens.peek().type == TokenType.IDENTIFIER:
            return parse_identifier()
        else:
            raise WrongTokenException(
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

    # TODO: refactor this function to parse top level expression
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
            elif has_scope(Scope.TOP_LEVEL) and tokens.peek().text == ";":
                tokens.consume(";")

                if tokens.peek().type == TokenType.END:
                    return BlockExpression([left], Literal(None))

                expressions = [left]

                with scope(Scope.TOP_LEVEL_EXPRESSION):
                    while not (
                        tokens.peek().text == "}" or tokens.peek().type == TokenType.END
                    ):
                        expressions.append(parse_expression())

                left = BlockExpression(expressions, Literal(None))
            elif has_scope(Scope.TOP_LEVEL_EXPRESSION) and tokens.peek().text == ";":
                tokens.consume(";")
                return left
            else:
                return left

    if tokens.empty():
        return Literal(None)

    expression = parse_expression()

    if (
        isinstance(expression, BlockExpression)
        and tokens.prev_token().text not in [";", "}"]
        and len(expression.expressions) > 0
    ):
        expression.result = expression.expressions.pop()

    if tokens.peek().type != TokenType.END:
        raise EndOfInputException()

    return expression
