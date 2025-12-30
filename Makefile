ACT_IMAGE := catthehacker/ubuntu:act-latest
ACT_JOB   := Testing
ACT_ARGS  := -P ubuntu-latest=$(ACT_IMAGE) --rm

CODEBASE  ?= src tests

# ----------------------------------------------------------
all:

.PHONY: all

# ----------------------------------------------------------
# TESTS
# ----------------------------------------------------------

tests: static unittest integration

.PHONY: tests

static: static-ruff static-mypy static-bandit

static-ruff:
	@echo "INFO: Running ruff static analysis"
	uv run ruff check $(CODEBASE)

static-mypy:
	@echo "INFO: Running mypy static analysis"
	uv run mypy $(CODEBASE)

static-bandit:
	@echo "INFO: Running bandit static analysis"
	uv run bandit -c pyproject.toml -q -r $(CODEBASE)

.PHONY: static static-ruff static-mypy static-bandit

unittest:
	@echo "INFO: Running unit tests"
	uv run pytest

unittest-verbose:
	@echo "INFO: Running unit tests (verbose)"
	uv run pytest -v

unittest-coverage:
	@echo "INFO: Running unit tests with coverage"
	uv run pytest --cov=$(CODEBASE) --cov-report=term-missing --cov-report=xml
	uv run coverage xml
	uv run coverage report -m --fail-under=80

.PHONY: unittest unittest-verbose unittest-coverage

integration:
	@echo "INFO: Running integration tests"

act:
	@echo "INFO: Running CI workflow locally with act"
	act $(ACT_ARGS) -j $(ACT_JOB)

.PHONY: integration act

# ----------------------------------------------------------
# FORMAT
# ----------------------------------------------------------
# Goal is to be consistent, and stop bike-shedding
# Check order of imports, and format code

format-check:
	@echo "INFO: Checking code format"
	uv run ruff check --select I $(CODEBASE)
	uv run ruff format --check $(CODEBASE)

format-fix:
	@echo "INFO: Fixing code format"
	uv run ruff check --select I --fix $(CODEBASE)
	uv run ruff format $(CODEBASE)

.PHONY: format-check format-fix

# ----------------------------------------------------------
# MANAGEMENT
# ----------------------------------------------------------

clean:
	@echo "INFO: Cleaning up project"
	-mv foo model*.json *.log* data
	uv run ruff clean
	rm -rf .pytest_cache .coverage .mypy_cache .hypothesis
	find . -name __pycache__ -not -path '*/.venv*/*' -exec rm -rf {} \;

update-check:
	@echo "INFO: Checking for dependency updates"
	uv lock --upgrade --dry-run
	uv sync --all-groups --dry-run

update-do:
	@echo "INFO: Updating dependencies"
	uv lock --upgrade
	uv sync --all-groups

.PHONY: clean
.PHONY: update-check update-do
