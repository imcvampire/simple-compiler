
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
./compiler.sh COMMAND path/to/source/code
```

where `COMMAND` may be one of these:

```asciidoc
asm     ::  Compile to assembly
compile ::  Compile to binary
```
