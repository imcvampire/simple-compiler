from dataclasses import dataclass
from typing import Optional

from compiler.location import Location
from enum import Enum


class TokenType(Enum):
    IDENTIFIER = 1
    INT_LITERAL = 2
    OPERATOR = 3


@dataclass
class Token:
    type: TokenType
    text: str
    location: Optional[Location] = None
