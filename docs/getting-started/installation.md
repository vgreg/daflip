# Installation

Daflip can be installed using pip, uv, or from source.

## Prerequisites

- Python 3.9 or higher
- pip or uv package manager

## Use as a uvx tool (recommended)

If you have uv installed, you can call daflip directly with the `uvx` command.

```bash
uvx daflip --help
```

## Install with pip

```bash
pip install daflip
```

## Install with uv

```bash
uv add daflip
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

## Next Steps

Now that you have Daflip installed, check out the [Quick Start Guide](quick-start.md) to make your first conversion!
