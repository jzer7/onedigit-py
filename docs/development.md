# Development

This document describes how to set up a development environment for this project, the conventions used, and how to run tests and checks.

VS Code is the main IDE used, but any editor is suitable.

## Conventions

### Environment

- Python 3.12 or higher.

### Code Style

- This project follows [PEP 8](https://peps.python.org/pep-0008/) for Python code style and [PEP 257](https://peps.python.org/pep-0257/) for docstrings whenever practical.

### Dependency Management

- [`uv`](https://github.com/astral-sh/uv) is used for dependency and virtual environment management. Dependencies are written to [pyproject.toml](https://packaging.python.org/en/latest/specifications/pyproject-toml/), following the standard Python packaging format.

### Documentation

- Markdown is used for all documentation.

### Static Checkers and Linters

This project uses several tools for code quality:

- [ruff](https://docs.astral.sh/ruff/) for main checks
- [mypy](https://mypy-lang.org/) for type checking
- [bandit](https://bandit.readthedocs.io/) for security
- [vulture](https://vulture.readthedocs.io/) for dead code detection

### Tests

- [pytest](https://docs.pytest.org/) is used for testing.
- [hypothesis](https://hypothesis.readthedocs.io/) is used to generate test inputs and improve coverage.

### Formatters

- File formatting settings are specified in [.editorconfig](../.editorconfig), which is supported by most editors.
- [ruff](https://docs.astral.sh/ruff/) is used for Python code formatting.
- [prettier](https://prettier.io/) is used for Markdown files.

### Continuous Integration

- GitHub Actions is used for CI. See the workflow definition in [ci-python.yml](../.github/workflows/ci-python.yml).

### Branching and Commit Conventions

- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow) is used for branching.
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) is used for commit messages.

## Setting up the development environment

### Prerequisites

- Install preferred tools:
  - [`task`](https://taskfile.dev/) for task automation.
    [Installation instructions](https://taskfile.dev/docs/installation).

  - [`uv`](https://github.com/astral-sh/uv) for virtual environment management.
    [Installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

### Setup

- Clone the repository

  ```sh
  git clone https://github.com/jzer7/onedigit-py.git
  cd onedigit-py
  ```

- Setup the environment

  ```sh
  task setup
  ```

## Common tasks

Development tasks are automated using `task`.
Here are the main ones:

| Action                  | Command         |
| ----------------------- | --------------- |
| Setup the environment   | `task setup`    |
| Run tests               | `task test`     |
| Run tests with coverage | `task coverage` |
| Run static checkers     | `task check`    |
| Format the code         | `task format`   |
| Build the package       | `task build`    |
| Clean up artifacts      | `task clean`    |

Additional tasks are available for running individual checks and operations.
Use `task --list` to see available tasks.

## Development flow

## Development Flow

Once the development environment is set up, follow these steps:

1. Create a new branch for your changes:

   ```sh
   git checkout -b my-feature-branch
   ```

2. Make your changes.
3. Run tests to verify your changes:

   ```sh
   task test
   ```

4. Before committing, run all static checks and format the code:

   ```sh
   task check
   task format
   ```

5. Commit your changes with a descriptive message:

   ```sh
   git add .
   git commit -m "feat: new feature description"
   ```

6. (Optional) Before submitting your PR, you can verify that CI checks will pass by simulating the GitHub Actions workflow locally.
   You will need [act](https://nektosact.com/):

   ```sh
   task actions
   ```

   This will run the `test` job defined in the GitHub Actions workflow.

   To run a different job, use:

   ```sh
   task actions:list-jobs            # lists available jobs
   task actions ACT_JOB=<job_name>   # overrides the job to run
   ```
