import re
from typing import Optional

from compiler import ast
from compiler.ast import Literal
from compiler.location import Location
from compiler.token import Token, TokenType

whitespace_re = re.compile(r"\s+")
identifier_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
operator_re = re.compile(r"(==?)|(!=)|(<=?)|(>=?)|\+|-|\*|/")
int_literal_re = re.compile(r"\d+")
punctuation_re = re.compile(r"[(){},;]")
comment_re = re.compile(r"#.*$|//.*$|/\*[\S\s]*?\*/", re.MULTILINE)


def tokenize(source_code: str) -> list[Token]:
    result = []

    i = 0

    while i < len(source_code):
        match: Optional[re.Match[str]] = None

        if match := whitespace_re.match(source_code, i):
            pass
        elif match := comment_re.match(source_code, i):
            result.append(Token(text=match.group(), type=TokenType.COMMENT))
        elif match := identifier_re.match(source_code, i):
            result.append(Token(text=match.group(), type=TokenType.IDENTIFIER))
        elif match := operator_re.match(source_code, i):
            result.append(Token(text=match.group(), type=TokenType.OPERATOR))
        elif match := int_literal_re.match(source_code, i):
            result.append(Token(text=match.group(), type=TokenType.INT_LITERAL))
        elif match := punctuation_re.match(source_code, i):
            result.append(Token(text=match.group(), type=TokenType.PUNCTUATION))
        else:
            raise ValueError("wrong source code")

        i = match.end()

    return result


def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
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

    def parse_term() -> ast.Expression:
        if peek().type == TokenType.INT_LITERAL:
            return parse_int_literal()
        elif peek().type == TokenType.IDENTIFIER:
            return parse_identifier()
        else:
            raise Exception(
                f"{peek().location}: expected an integer literal or an identifier"
            )

    def parse_expression() -> ast.Expression:
        left = parse_term()
        operator_token = consume(["+", "-"])
        right = parse_term()
        return ast.BinaryOp(left, operator_token.text, right)

    return parse_expression()
