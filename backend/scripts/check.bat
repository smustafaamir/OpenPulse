@echo off
cd /d %~dp0\..
python -m ruff check .
python -m black --check .
python -m mypy app
python -m pytest -v
