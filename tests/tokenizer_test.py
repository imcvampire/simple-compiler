import pytest

from compiler.token import Token, TokenType
from compiler.tokenizer import tokenize


def cases() -> list[tuple[str, list[Token]]]:
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
            "true != false",
            [
                Token(text="true", type=TokenType.BOOL_LITERAL),
                Token(text="!=", type=TokenType.OPERATOR),
                Token(text="false", type=TokenType.BOOL_LITERAL),
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
        (
            "var a: Int = 1",
            [
                Token(text="var", type=TokenType.IDENTIFIER),
                Token(text="a", type=TokenType.IDENTIFIER),
                Token(text=":", type=TokenType.PUNCTUATION),
                Token(text="Int", type=TokenType.TYPE),
                Token(text="=", type=TokenType.OPERATOR),
                Token(text="1", type=TokenType.INT_LITERAL),
            ],
        ),
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_tokenize(test_input: str, expected: list[Token]) -> None:
    assert tokenize(test_input) == expected
