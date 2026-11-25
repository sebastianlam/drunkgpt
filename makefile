# Makefile

.PHONY: install test run

install:
	poetry install

test:
	poetry run pytest -q

run:
	poetry run python main.py
