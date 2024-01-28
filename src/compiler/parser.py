from compiler import ast
from compiler.ast import Literal
from compiler.token import Token, TokenType

left_associative_binary_operators = [
    ["or"],
    ["and"],
    ["==", "!="],
    ["<", "<=", ">", ">="],
    ["+", "-"],
    ["*", "/"],
]


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

    def parse_term() -> ast.Literal:
        if peek().type == TokenType.END:
            return Literal(None)

        if peek().text == "=":
            return parse_equal()
        elif peek().type == TokenType.INT_LITERAL:
            return parse_int_literal()
        elif peek().type == TokenType.IDENTIFIER:
            return parse_identifier()
        else:
            raise Exception(
                f"{peek().location}: wrong token, got: {peek().type}: {peek().text}"
            )

    def parse_factor() -> ast.Expression:
        if peek().text == "(":
            return parse_parenthesized()
        elif peek().type == TokenType.INT_LITERAL:
            return parse_int_literal()
        elif peek().type == TokenType.IDENTIFIER:
            return parse_identifier()
        else:
            raise Exception(
                f'{peek().location}: expected "(", an integer literal or an identifier'
            )

    def parse_parenthesized() -> ast.Expression:
        consume("(")
        expr = parse_expression()
        consume(")")
        return expr

    def parse_expression() -> ast.BinaryOp:
        left = parse_term()

        while peek().type != TokenType.END:
            if peek().text in ["="]:
                operator_token = consume()
                operator = operator_token.text

                right = parse_expression()

                left = ast.BinaryOp(left, operator, right)
            elif peek().text in ["+", "-"]:
                operator_token = consume()
                operator = operator_token.text

                right = parse_term()

                left = ast.BinaryOp(left, operator, right)
            else:
                raise Exception(f"{peek().location}: wrong token: {peek().text}")

        return left

    return parse_expression()