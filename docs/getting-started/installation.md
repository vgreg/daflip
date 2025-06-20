# Installation

Daflip can be installed using pip, uv, or from source.

## Prerequisites

- Python 3.9 or higher
- pip or uv package manager

## Install with pip

```bash
pip install daflip
```

## Install with uv (Recommended)

```bash
uv add daflip
```

## Install with optional dependencies

For full functionality including Excel support:

```bash
# With pip
pip install "daflip[excel]"

# With uv
uv add "daflip[excel]"
```

## Install from source

```bash
# Clone the repository
git clone https://github.com/vgreg/daflip.git
cd daflip

# Install in development mode
pip install -e .

# Or with uv
uv sync --dev
```

## Verify Installation

Check that Daflip is installed correctly:

```bash
daflip --help
```

You should see the help output with available commands and options.

## Optional Dependencies

Some formats require additional dependencies:

### Excel Support
```bash
pip install openpyxl xlrd xlsxwriter
```

### SAS Support
```bash
pip install sas7bdat
```

### SPSS Support
```bash
pip install pyreadstat
```

### Stata Support
```bash
pip install pandas-stata
```

## Development Setup

For contributing to Daflip:

```bash
# Clone and setup
git clone https://github.com/vgreg/daflip.git
cd daflip

# Install with development dependencies
uv sync --dev

# Run tests
pytest

# Run linting
ruff check .
```

## Next Steps

Now that you have Daflip installed, check out the [Quick Start Guide](quick-start.md) to make your first conversion! 