import pytest

from compiler.location import L
from compiler.token import Token, TokenType
from compiler.tokenizer import tokenize


def cases() -> list[tuple[str, list[Token]]]:
    return [
        (
            "if  3\nwhile",
            [
                Token(text="if", type=TokenType.IDENTIFIER, location=L),
                Token(text="3", type=TokenType.INT_LITERAL, location=L),
                Token(text="while", type=TokenType.IDENTIFIER, location=L),
            ],
        ),
        (
            "1 - 10 >= 1 / 1;",
            [
                Token(text="1", type=TokenType.INT_LITERAL, location=L),
                Token(text="-", type=TokenType.OPERATOR, location=L),
                Token(text="10", type=TokenType.INT_LITERAL, location=L),
                Token(text=">=", type=TokenType.OPERATOR, location=L),
                Token(text="1", type=TokenType.INT_LITERAL, location=L),
                Token(text="/", type=TokenType.OPERATOR, location=L),
                Token(text="1", type=TokenType.INT_LITERAL, location=L),
                Token(text=";", type=TokenType.PUNCTUATION, location=L),
            ],
        ),
        (
            "(1 == 1) <= 1",
            [
                Token(text="(", type=TokenType.PUNCTUATION, location=L),
                Token(text="1", type=TokenType.INT_LITERAL, location=L),
                Token(text="==", type=TokenType.OPERATOR, location=L),
                Token(text="1", type=TokenType.INT_LITERAL, location=L),
                Token(text=")", type=TokenType.PUNCTUATION, location=L),
                Token(text="<=", type=TokenType.OPERATOR, location=L),
                Token(text="1", type=TokenType.INT_LITERAL, location=L),
            ],
        ),
        (
            "true != false",
            [
                Token(text="true", type=TokenType.BOOL_LITERAL, location=L),
                Token(text="!=", type=TokenType.OPERATOR, location=L),
                Token(text="false", type=TokenType.BOOL_LITERAL, location=L),
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
                    location=L,
                ),
                Token(text="1", type=TokenType.INT_LITERAL, location=L),
                Token(text="# dfgdfgreter", type=TokenType.COMMENT, location=L),
                Token(text="2", type=TokenType.INT_LITERAL, location=L),
                Token(text="// dfgfdgdfgfdggfd", type=TokenType.COMMENT, location=L),
            ],
        ),
        (
            "var a: Int = 1",
            [
                Token(text="var", type=TokenType.IDENTIFIER, location=L),
                Token(text="a", type=TokenType.IDENTIFIER, location=L),
                Token(text=":", type=TokenType.PUNCTUATION, location=L),
                Token(text="Int", type=TokenType.TYPE, location=L),
                Token(text="=", type=TokenType.OPERATOR, location=L),
                Token(text="1", type=TokenType.INT_LITERAL, location=L),
            ],
        ),
        (
            """
            var a = false;
            """,
            [
                Token(text="var", type=TokenType.IDENTIFIER, location=L),
                Token(text="a", type=TokenType.IDENTIFIER, location=L),
                Token(text="=", type=TokenType.OPERATOR, location=L),
                Token(text="false", type=TokenType.BOOL_LITERAL, location=L),
                Token(text=";", type=TokenType.PUNCTUATION, location=L),
            ],
        ),
    ]


@pytest.mark.parametrize("test_input,expected", cases())
def test_tokenize(test_input: str, expected: list[Token]) -> None:
    got = tokenize(test_input)

    assert got == expected
