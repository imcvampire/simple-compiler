#!/bin/bash
set -euo pipefail
cd "$(dirname "${0}")"
poetry run mypy .
rm -Rf test_programs/workdir
poetry run coverage run -m pytest -vv tests/
poetry run coverage report -m --omit="tests/*"
