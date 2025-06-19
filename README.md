# daflip

A modern, robust, and AI-friendly Python CLI tool for converting data files between formats. Built with Typer, pandas, and Rich.

## Features
- Supports CSV, TSV, PSV, fixed-width, Parquet, ORC, Feather, SAS, Stata, SPSS, Excel, HTML (input)
- Outputs: CSV, Parquet, ORC, Feather, Excel, Stata
- Format inference from file extension (with override)
- Compression and row/sheet/table selection options
- Uses pandas with pyarrow dtype backend when possible
- Rich error messages and DataFrame previews
- Modular, testable, and open source

## Installation

```sh
uv pip install .
```

## Usage

```sh
daflip input.csv output.parquet
```

See `daflip --help` for all options.

## Development
- Dependencies managed with [uv](https://github.com/astral-sh/uv)
- Linting with [Ruff](https://github.com/astral-sh/ruff)
- Testing with [pytest](https://docs.pytest.org/)
- CI with GitHub Actions

## License
MIT
