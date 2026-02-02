# Code Quality
lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

fmt:
	uv run ruff check --select I --fix src tests
	uv run ruff format src tests