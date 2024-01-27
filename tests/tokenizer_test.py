import pytest

from compiler.token import Token, TokenType
from compiler.tokenizer import tokenize


def basic_input():
    return [
        (
            "if  3\nwhile",
            [
                Token(text="if", type=TokenType.IDENTIFIER),
                Token(text="3", type=TokenType.INT_LITERAL),
                Token(text="while", type=TokenType.IDENTIFIER),
            ],
        ),
        (
            "1 - 10 >= 1 / 1",
            [
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text="-", type=TokenType.OPERATOR),
                Token(text="10", type=TokenType.INT_LITERAL),
                Token(text=">=", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text="/", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
            ],
        ),
        (
            "1 == 1 <= 1",
            [
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text="==", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text="<=", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
            ],
        ),
    ]


@pytest.mark.parametrize("test_input,expected", basic_input())
def test_tokenizer_basics(test_input: str, expected: list[str]):
    assert tokenize(test_input) == expected
