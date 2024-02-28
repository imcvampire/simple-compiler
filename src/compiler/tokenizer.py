import re
from typing import Optional

from compiler.location import Location
from compiler.token import Token, TokenType

whitespace_re = re.compile(r"\s+")
identifier_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
operator_re = re.compile(r"(==?)|(!=)|(<=?)|(>=?)|\+|-|\*|/|%")
int_literal_re = re.compile(r"\d+")
bool_literal_re = re.compile(r"true|false")
punctuation_re = re.compile(r"[(){},;:]")
comment_re = re.compile(r"#.*$|//.*$|/\*[\S\s]*?\*/", re.MULTILINE)
type_re = re.compile(r"Int|Bool")


def tokenize(source_code: str) -> list[Token]:
    result = []

    i = 0

    while i < len(source_code):
        match: Optional[re.Match[str]] = None

        if match := whitespace_re.match(source_code, i):
            pass
        else:
            if match := comment_re.match(source_code, i):
                result.append(Token(text=match.group(), type=TokenType.COMMENT))
            elif match := type_re.match(source_code, i):
                result.append(Token(text=match.group(), type=TokenType.TYPE))
            elif match := bool_literal_re.match(source_code, i):
                result.append(Token(text=match.group(), type=TokenType.BOOL_LITERAL))
            elif match := int_literal_re.match(source_code, i):
                result.append(Token(text=match.group(), type=TokenType.INT_LITERAL))
            elif match := identifier_re.match(source_code, i):
                result.append(Token(text=match.group(), type=TokenType.IDENTIFIER))
            elif match := operator_re.match(source_code, i):
                result.append(Token(text=match.group(), type=TokenType.OPERATOR))
            elif match := punctuation_re.match(source_code, i):
                result.append(Token(text=match.group(), type=TokenType.PUNCTUATION))
            else:
                raise Exception("wrong source code")

            start, stop = match.span()
            last_new_line = source_code[:start].rfind("\n")
            if last_new_line == -1:
                start_column = start + 1
            else:
                start_column = start - source_code[:start].rfind("\n")
            start_line = source_code[:start].count("\n")

            result[-1].location = Location(
                line=start_line, column=start_column, file=""
            )

        i = match.end()

    return result
