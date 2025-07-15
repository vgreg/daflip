# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daflip is a modern Python CLI tool for converting data files between formats. It leverages pandas and pyarrow for robust data processing and supports both chunked and non-chunked processing for large datasets.

## Development Commands

### Testing
```bash
pytest
pytest tests/ -v --tb=short
pytest tests/test_services.py::test_specific_function
```

### Code Quality
```bash
ruff check                    # Lint code
ruff format                   # Format code
ruff check --fix              # Auto-fix linting issues
```

### Pre-commit
```bash
pre-commit install            # Install pre-commit hooks
pre-commit run --all-files    # Run all hooks manually
```

### Documentation
```bash
mkdocs serve                  # Serve docs locally
mkdocs build                  # Build static docs
```

### Package Management
Uses `uv` for dependency management:
```bash
uv add <package>              # Add new dependency
uv remove <package>           # Remove dependency
uv sync                       # Sync dependencies
```

## Architecture

### Core Components

- **CLI Entry Point** (`src/daflip/cli.py`): Typer-based CLI interface with two main commands: `convert` and `schema`
- **Controllers** (`src/daflip/controllers.py`): Command handlers that bridge CLI arguments to services
- **Services** (`src/daflip/services.py`): Core conversion logic with support for chunked processing
- **Models** (`src/daflip/models.py`): Enums defining supported input/output formats
- **Utils** (`src/daflip/utils.py`): Format inference and helper functions
- **Config** (`src/daflip/config.py`): Configuration management

### Data Flow

1. CLI receives command → Controllers validate and parse arguments
2. Controllers call Services with processed parameters
3. Services handle format detection, reading, processing, and writing
4. Utils provide format inference and helper functionality

### Supported Formats

**Input**: CSV, TSV, PSV, fixed-width, Parquet, ORC, Feather, SAS, Stata, SPSS, Excel, HTML
**Output**: CSV, Parquet, ORC, Feather, Excel, Stata

### Key Features

- **Chunked Processing**: Supports large file processing via `input_chunk_size` parameter
- **Schema Management**: Can infer and export schemas, plus use predefined schemas
- **Format Detection**: Automatic format inference from file extensions with override support
- **Flexible Options**: Row selection, sheet/table selection, compression settings

## Development Guidelines

### Code Style
- Uses Ruff for linting and formatting
- Type hints throughout codebase
- Descriptive variable and function names
- Comprehensive docstrings following Google style

### Project Structure
- Source code in `src/daflip/`
- Tests in `tests/` with corresponding test files
- Documentation in `docs/` (MkDocs format)
- CI/CD via GitHub Actions

### Testing
- Uses pytest with coverage reporting
- Test files mirror source structure
- Integration tests in `test_integration.py`

### Dependencies
- Core: pandas, pyarrow, typer, rich
- Dev: pytest, ruff, mkdocs, pre-commit
- Managed via `uv` (see `pyproject.toml`)
