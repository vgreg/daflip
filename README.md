# daflip

A modern Python CLI tool for converting data files between formats. Built with pyarrow and pandas.

## Features
- Supported input formats: CSV, TSV, PSV, fixed-width, Parquet, ORC, Feather, SAS, Stata, SPSS, Excel, HTML
- Supported output formats: CSV, Parquet, ORC, Feather, Excel, Stata
- Format inference from file extension (with override).
- Compression and row/sheet/table selection options.
- Solid foundation: Uses pandas and pyarrow to read and write data.

## Installation and usage

```sh
pip install daflip
daflip convert input.csv output.parquet
```

or 

```sh
uvx daflip convert input.csv output.parquet
```

See `daflip --help` for all options.

## Development
- Dependencies managed with [uv](https://github.com/astral-sh/uv)
- Linting with [Ruff](https://github.com/astral-sh/ruff)
- Testing with [pytest](https://docs.pytest.org/)

## License
MIT
