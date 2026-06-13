
all: format lint

lint:
    ruff check --select I --fix */*.py

format:
    ruff format */*.py
