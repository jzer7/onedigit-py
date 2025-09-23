ACT_IMAGE := catthehacker/ubuntu:act-latest
ACT_JOB   := Testing
ACT_ARGS  := -P ubuntu-latest=$(ACT_IMAGE) --rm

CODEBASE  := src tests

all:

tests: static unittest integration

.PHONY: all tests

static: static_ruff static_mypy static_bandit

static_ruff:
	uv run ruff check $(CODEBASE)

static_mypy:
	uv run mypy $(CODEBASE)

static_bandit:
	uv run bandit -c pyproject.toml -q -r $(CODEBASE)

.PHONY: static static_ruff static_mypy static_bandit

unittest:
	uv run pytest

.PHONY: unittest

integration:

act:
	act $(ACT_ARGS) -j $(ACT_JOB)

.PHONY: integration act
