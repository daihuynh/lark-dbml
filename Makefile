test:
	uv sync --all-extras
	uv run pytest

format:
	uv sync --all-extras
	uv run ruff check --select I --fix
	uv run ruff format .