# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing and linting.

## Workflows

### Tests (`test.yml`)
- **Triggers**: Pull requests to `main` branch and pushes to `main`
- **Runs on**: Ubuntu with Python 3.9, 3.10, 3.11, and 3.12
- **Actions**:
  - Installs uv package manager
  - Installs dependencies with `uv sync --dev`
  - Runs tests with pytest and coverage
  - Uploads coverage to Codecov

### Lint (`lint.yml`)
- **Triggers**: Pull requests to `main` branch and pushes to `main`
- **Runs on**: Ubuntu with Python 3.12
- **Actions**:
  - Installs uv package manager
  - Installs dependencies with `uv sync --dev`
  - Runs ruff format check
  - Runs ruff linting
  - Attempts to fix issues with `ruff check --fix`
  - Verifies all issues are resolved

## Local Development

To run the same checks locally:

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check .

# Run formatting check
uv run ruff format --check .

# Fix formatting issues
uv run ruff format .

# Fix linting issues
uv run ruff check --fix .
```

## Requirements

- Python 3.12+
- uv package manager
- pytest and pytest-cov for testing
- ruff for linting and formatting 