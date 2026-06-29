#!/usr/bin/env sh
set -e
cd "$(dirname "$0")/.."
python -m ruff check .
python -m black --check .
python -m mypy app
python -m pytest -v
