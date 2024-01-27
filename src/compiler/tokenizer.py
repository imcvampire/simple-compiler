import re

from compiler.location import Location
from compiler.token import Token, TokenType

whitespace_re = re.compile(r"\s+")
identifier_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
operator_re = re.compile(r"(==?)|(!=)|(<=?)|(>=?)|\+|-|\*|/")
int_literal_re = re.compile(r"\d+")


def tokenize(source_code: str) -> list[Token]:
    result = []

    i = 0

    while i < len(source_code):
        match: re.Match[str] | None = None
        if match := whitespace_re.match(source_code, i):
            pass
        elif match := identifier_re.match(source_code, i):
            result.append(Token(text=match.group(), type=TokenType.IDENTIFIER))
        elif match := operator_re.match(source_code, i):
            result.append(Token(text=match.group(), type=TokenType.OPERATOR))
        elif match := int_literal_re.match(source_code, i):
            result.append(Token(text=match.group(), type=TokenType.INT_LITERAL))
        else:
            raise ValueError("wrong source code")

        i = match.end()

    return result
