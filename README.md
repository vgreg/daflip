# daflip

[![PyPI version](https://badge.fury.io/py/daflip.svg)](https://badge.fury.io/py/daflip)
[![Python versions](https://img.shields.io/pypi/pyversions/daflip.svg)](https://pypi.org/project/daflip/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/vgreg/daflip/actions/workflows/test.yml/badge.svg)](https://github.com/vgreg/daflip/actions/workflows/test.yml)
[![Lint](https://github.com/vgreg/daflip/actions/workflows/lint.yml/badge.svg)](https://github.com/vgreg/daflip/actions/workflows/lint.yml)
[![Coverage](https://codecov.io/gh/vgreg/daflip/branch/main/graph/badge.svg)](https://codecov.io/gh/vgreg/daflip)

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
