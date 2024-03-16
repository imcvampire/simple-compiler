## Setup

### Requirements:

- [Poetry](https://python-poetry.org/) for installing dependencies
    - Recommended installation method: the "official installer"
      i.e. `curl -sSL https://install.python-poetry.org | python3 -`

### Install dependencies specified in `pyproject.toml`:

```shell
poetry install
```

If you have trouble with Poetry not picking up pyenv's python installation,
try `poetry env remove --all` and then `poetry install` again.

### Typecheck and run tests:

```shell
./check.sh
```

or individually:

```shell
poetry run mypy .
poetry run pytest -vv
```

### Run the compiler on a source code file:

```shell
./compiler.sh COMMAND [path/to/source/code] [path/to/output]
```

where `COMMAND` may be one of these:

```asciidoc
asm     ::  Compile to assembly
compile ::  Compile to binary
```

If no source code file is specified, the compiler will read from stdin.
If no output file is specified, the compiler will write to stdout (for `asm`) or to `compiled_program` (for `compile`).

### Language spec

An expression is defined recursively as follows, where E, E1, E2, … En represent some other arbitrary expression.

- Integer literal: a whole number between -264 and 263 - 1.
- Boolean literal: either true or false.
- Identifier: a word consisting of letters, underscores or digits, but the first character must not be a digit.
- Unary operator: either -E or not E.
- Binary operator: E1 op E2 where op is one of the following: +, -, *, /, %, ==, !=, <, <=, >, >=, and, or, =.
    - Operator = is right-associative.
    - All other operators are left-associative.
    - Precedences are defined below.
- Parentheses: (E), used to override precedence.
- Block: { E1; E2; ...; En } or { E1; E2; ...; En; } (may be empty, last semicolon optional).
    - Semicolons after subexpressions that end in } are optional.
- Untyped variable declaration: var ID = E where ID is an identifier.
- Typed variable declaration: var ID: T = E where ID is an identifier and T is a type expression (defined below).
- Constant declaration: const ID = E where ID is an identifier.
- Typed constant declaration: const ID: T = E where ID is an identifier and T is a type expression.
- If-then conditional: if E1 then E2
- If-then-else conditional: if E1 then E2 else E3
- While-loop: while E1 do E2
  - break and continue are supported.
  - break exits the innermost active loop, and continue goes back to its beginning.

