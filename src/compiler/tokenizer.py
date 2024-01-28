import re
from typing import Optional

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
            raise Exception("wrong source code")

        i = match.end()

    return result
