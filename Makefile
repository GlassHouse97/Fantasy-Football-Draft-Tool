.PHONY: install test lint typecheck check app

install:
	python -m pip install -e ".[modeling,dev]"

test:
	python -m pytest

lint:
	python -m ruff check .

typecheck:
	python -m mypy

check: lint typecheck test

app:
	python -m streamlit run app.py
