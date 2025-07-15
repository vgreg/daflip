# Contributing to Daflip

Thank you for your interest in contributing to Daflip! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- uv

### Getting Started

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/daflip.git
   cd daflip
   ```

2. **Install dependencies**
   ```bash
   # With uv (recommended)
   uv sync --dev

   # With pip
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Verify setup**
   ```bash
   pytest
   ruff check .
   pre-commit run --all-files
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write your code
- Add tests for new functionality
- Update documentation if needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/daflip

# Run specific test file
pytest tests/test_services.py

# Run linting
ruff check .
ruff format .
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

### 5. Push and Create Pull Request

```bashq
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

### Running Ruff

```bash
# Check for issues
ruff check .

# Fix auto-fixable issues
ruff check . --fix

# Format code
ruff format .
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality and consistency. The hooks run automatically before each commit and include:

- **Code formatting** with Ruff
- **Linting** with Ruff
- **Type checking** with MyPy
- **Basic file checks** (trailing whitespace, YAML validation, etc.)

### Setup

```bash
# Install pre-commit
uv add pre-commit

# Install the git hooks
uv run pre-commit install
```

### Usage

The hooks run automatically on commit, but you can also run them manually:

```bash
# Run all hooks on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files

# Run hooks on staged files only
pre-commit run

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src/daflip --cov-report=html

# Specific test
uv run pytest tests/test_services.py::test_convert_roundtrip

# Verbose output
uv run pytest -v
```

### Writing Tests

- Tests should be in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Use pytest fixtures for common setup

### Test Structure

```python
def test_feature_name():
    """Test description."""
    # Arrange
    input_data = "test"

    # Act
    result = function_to_test(input_data)

    # Assert
    assert result == expected_output
```

## Documentation

### Building Documentation

```bash
# Install docs dependencies
uv add mkdocs mkdocs-material

# Build docs
uv run mkdocs build

# Serve docs locally
uv run mkdocs serve
```

### Documentation Guidelines

- Write clear, concise documentation
- Include examples for all features
- Update API documentation when changing functions
- Use proper markdown formatting

## Pull Request Guidelines

### Before Submitting

1. **Tests pass**: All tests should pass
2. **Linting passes**: No ruff errors
3. **Documentation updated**: Update docs for new features
4. **Commit messages**: Use conventional commit format

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:
```
feat(services): add support for new file format
fix(cli): handle missing input file gracefully
docs(api): update CLI reference with new options
```

### Pull Request Template

When creating a PR, include:

- Description of changes
- Related issue (if any)
- Testing performed
- Breaking changes (if any)

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: All PRs require review before merging

## Release Process

The project uses automated semantic releases based on commit messages:

### Automated Releases

1. **Commit messages determine version bump**:
   - `feat:` → minor version bump (0.1.0 → 0.2.0)
   - `fix:` → patch version bump (0.1.0 → 0.1.1)
   - `BREAKING CHANGE` or `!:` → major version bump (0.1.0 → 1.0.0)

2. **GitHub Actions automatically**:
   - Analyzes commit messages since last release
   - Updates version in `pyproject.toml` and `src/daflip/__init__.py`
   - Generates changelog
   - Creates and pushes a git tag
   - Creates a GitHub release
   - Publishes to PyPI

3. **Requirements for automated releases**:
   - Repository admin or PAT token with admin privileges
   - Branch protection rules configured to allow admin bypass
   - Conventional commit messages

### Manual Release (if needed)

If automated releases fail:

1. Update version in `pyproject.toml`
2. Update version in `src/daflip/__init__.py`
3. Update changelog
4. Create release tag: `git tag v0.1.0`
5. Push tag: `git push origin v0.1.0`
6. GitHub Actions will build and publish

Thank you for contributing to Daflip! 🚀
