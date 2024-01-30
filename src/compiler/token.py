from dataclasses import dataclass
from typing import Optional

from compiler.location import Location
from enum import Enum


class TokenType(Enum):
    END = 0
    IDENTIFIER = 1
    INT_LITERAL = 2
    BOOL_LITERAL = 3
    OPERATOR = 4
    PUNCTUATION = 5
    COMMENT = 6


@dataclass
class Token:
    type: TokenType
    text: str
    location: Optional[Location] = None


@dataclass
class Tokens:
    tokens: list[Token]
    pos = 0

    def peek(self) -> Token:
        return self._get(self.pos)

    def next_token(self) -> Token:
        next_pos = self.pos + 1

        return self._get(next_pos)

    def consume(self, expected: str | list[str] | None = None) -> Token:
        token = self.peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.location}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f"{token.location}: expected one of: {comma_separated}")

        self.pos += 1

        return token

    def empty(self) -> bool:
        return len(self.tokens) == 0

    def _get(self, pos: int) -> Token:
        if pos < len(self.tokens):
            return self.tokens[pos]
        elif len(self.tokens) == 0:
            return Token(
                type=TokenType.END,
                text="",
            )
        else:
            return Token(
                location=self.tokens[-1].location,
                type=TokenType.END,
                text="",
            )
