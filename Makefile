.PHONY: install test lint run

install:
	uv sync

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/

lint-fix:
	uv run ruff check --fix src/ tests/

run:
	uv run llm-tools --help
