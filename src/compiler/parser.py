from compiler import ast
from compiler.ast import Literal
from compiler.parser_exception import EndOfInputException
from compiler.token import Token, TokenType

left_associative_binary_operators = [
    ["or"],
    ["and"],
    ["==", "!="],
    ["<", "<=", ">", ">="],
    ["+", "-"],
    ["*", "/"],
]

# left_associative_binary_operators.reverse()


def get_left_associative_binary_operator_level(
    operator: str, current_level: int = 0
) -> int:
    for level, operators in enumerate(
        left_associative_binary_operators, start=current_level
    ):
        if operator in operators:
            return level
    return -1


def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        elif len(tokens) == 0:
            return Token(
                type=TokenType.END,
                text="",
            )
        else:
            return Token(
                location=tokens[-1].location,
                type=TokenType.END,
                text="",
            )

    def next_token() -> Token:
        nonlocal pos
        next_pos = pos + 1

        if next_pos < len(tokens):
            return tokens[next_pos]
        elif len(tokens) == 0:
            return Token(
                type=TokenType.END,
                text="",
            )
        else:
            return Token(
                location=tokens[-1].location,
                type=TokenType.END,
                text="",
            )

    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.location}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f"{token.location}: expected one of: {comma_separated}")

        nonlocal pos
        pos += 1

        return token

    def parse_int_literal() -> ast.Literal:
        if peek().type != TokenType.INT_LITERAL:
            raise Exception(f"{peek().location}: expected an integer literal")
        token = consume()
        return ast.Literal(int(token.text))

    def parse_identifier() -> Literal:
        if peek().type != TokenType.IDENTIFIER:
            raise Exception(f"{peek().location}: expected an identifier")
        token = consume()
        return ast.Literal(token.text)

    def parse_equal() -> Literal:
        if peek().text != "=":
            raise Exception(f"{peek().location}: expected an equal sign")
        token = consume()
        return ast.Literal(token.text)

    def parse_parenthesized_expression() -> ast.Expression:
        consume("(")
        expr = parse_expression()
        consume(")")
        return expr

    def parse_if_expression() -> ast.Expression:
        consume("if")
        condition = parse_expression()
        consume("then")
        then_clause = parse_expression()
        if peek().text == "else":
            consume("else")
            else_clause = parse_expression()
        else:
            else_clause = None
        return ast.IfExpression(condition, then_clause, else_clause)

    def parse_function_call() -> ast.Expression:
        function_name = peek().text
        consume(function_name)
        consume("(")
        arguments = []
        while peek().text != ")":
            arguments.append(parse_expression())
            if peek().text == ",":
                consume(",")
            elif peek().text == ")":
                break
            else:
                raise Exception(f"{peek().location}: expected a comma")
        consume(")")

        return ast.FunctionExpression(function_name, arguments)

    def parse_leaf_construct() -> ast.Expression:
        if peek().type == TokenType.END:
            return Literal(None)
        elif peek().text == "=":
            return parse_equal()
        elif peek().text == "(":
            return parse_parenthesized_expression()
        elif peek().text == "if":
            return parse_if_expression()
        elif peek().type == TokenType.INT_LITERAL:
            return parse_int_literal()
        elif peek().type == TokenType.IDENTIFIER and next_token().text == "(":
            return parse_function_call()
        elif peek().type == TokenType.IDENTIFIER:
            return parse_identifier()
        else:
            raise Exception(
                f"{peek().location}: wrong token, got: {peek().type}: {peek().text}"
            )

    def parse_left_associative_binary_operators(level: int) -> ast.Expression:
        if level == len(left_associative_binary_operators):
            return parse_leaf_construct()

        left = parse_left_associative_binary_operators(level + 1)
        while peek().text in left_associative_binary_operators[level]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_left_associative_binary_operators(level + 1)
            left = ast.BinaryOp(left, operator, right)
        return left

    def parse_expression() -> ast.Expression:
        left = parse_left_associative_binary_operators(1)

        while True:
            if peek().text in ["="]:  # right-associative
                operator_token = consume()
                operator = operator_token.text
                right = parse_expression()
                left = ast.BinaryOp(left, operator, right)
            elif peek().text in left_associative_binary_operators[0]:
                operator_token = consume()
                operator = operator_token.text
                right = parse_left_associative_binary_operators(1)
                left = ast.BinaryOp(left, operator, right)
            else:
                return left

    expression = parse_expression()

    if peek().type != TokenType.END:
        raise EndOfInputException()

    return expression
