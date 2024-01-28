import pytest

from compiler.token import Token, TokenType
from compiler.tokenizer import tokenize


def basic_input() -> list[tuple[str, list[Token]]]:
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
            "1 - 10 >= 1 / 1;",
            [
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text="-", type=TokenType.OPERATOR),
                Token(text="10", type=TokenType.INT_LITERAL),
                Token(text=">=", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text="/", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text=";", type=TokenType.PUNCTUATION),
            ],
        ),
        (
            "(1 == 1) <= 1",
            [
                Token(text="(", type=TokenType.PUNCTUATION),
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text="==", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text=")", type=TokenType.PUNCTUATION),
                Token(text="<=", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
            ],
        ),
        (
            """/* Another
comment. */

1 # dfgdfgreter

2 // dfgfdgdfgfdggfd""",
            [
                Token(
                    text="""/* Another
comment. */""",
                    type=TokenType.COMMENT,
                ),
                Token(text="1", type=TokenType.INT_LITERAL),
                Token(text="# dfgdfgreter", type=TokenType.COMMENT),
                Token(text="2", type=TokenType.INT_LITERAL),
                Token(text="// dfgfdgdfgfdggfd", type=TokenType.COMMENT),
            ],
        ),
    ]


@pytest.mark.parametrize("test_input,expected", basic_input())
def test_tokenizer_basics(test_input: str, expected: list[str]) -> None:
    assert tokenize(test_input) == expected
