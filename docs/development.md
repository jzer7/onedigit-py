# Development

## Conventions

- File settings are specified in [.editorconfig](.editorconfig).
  I use VS Code for large projects, but use other editors on ocasion.
  Most understand the [editorconfig format](https://editorconfig.org/).

- Markdown for documentation.

- Python

- [`uv`](https://github.com/astral-sh/uv) for dependency management.
  It writes dependencies in the [pyproject.toml](https://packaging.python.org/en/latest/specifications/pyproject-toml/), which most modern build tools can understand.

- Static checkers and linters. I have not seen a single solution.
  [ruff](https://docs.astral.sh/ruff/) for main checks.
  [mypy](https://mypy-lang.org/) for type checking,
  [bandit](https://bandit.readthedocs.io/) for security, and

- Formatters: ruff for Python, [mdformat](https://mdformat.readthedocs.io/) for markdown, [taplo](https://taplo.tamasfe.dev/cli/introduction.html) for TOML.

- Tests with [pytest](https://docs.pytest.org/).
  To reduce effort, also use [hypothesis](https://hypothesis.readthedocs.io/) to generate test inputs.

## Basic

To get system up and running:

```sh
git clone https://github.com/jzer7/onedigit-py.git
cd digit
uv sync --all-groups
```

To check health of the codebase:

```sh
uv run ruff check
uv run pytest
```

To build package:

```sh
uv build
ls -lt dist
```

## Continuous Integration

CI is done by GitHub Actions.
Look at the definition on [ci.yml](../.github/workflows/ci.yml).

## Local checks

To check results of code on your work directory run these:

```sh
make tests
```

For convenience, there are also targets that split that.

Once you are ready to submit your PR, it helps to simulate the GitHub Actions work locally.
You will need [act](https://nektosact.com/).

```sh
act -P ubuntu-latest=catthehacker/ubuntu:act-latest -j Testing --rm
```
