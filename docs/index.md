# Daflip

A fast and flexible data format conversion tool built with Python, pandas, and PyArrow.

## Features

- **Multiple Format Support**: Convert between CSV, Parquet, Excel, Feather, ORC, and more
- **High Performance**: Leverages pandas and PyArrow for efficient data processing
- **Chunked Processing**: Handle large files with memory-efficient chunked processing
- **Schema Management**: Export and apply custom schemas for data validation
- **Compression Support**: Built-in compression for output formats
- **Command Line Interface**: Simple CLI for quick conversions
- **Python API**: Full Python API for programmatic use

## Quick Start

```bash
# Install Daflip
pip install daflip

# Convert a CSV file to Parquet
daflip data.csv data.parquet

# Convert with compression
daflip data.csv data.parquet --compression snappy

# Convert large files with chunking
daflip large.csv large.parquet --input-chunk-size 10000
```

## Supported Formats

| Input               | Output | Notes                  |
| ------------------- | ------ | ---------------------- |
| CSV                 | ✅      | With custom separators |
| Parquet             | ✅      | With compression       |
| Excel (.xlsx, .xls) | ✅      | With sheet selection   |
| Feather             | ✅      |                        |
| ORC                 | ✅      |                        |
| SAS7BDAT            | ✅      |                        |
| Stata               | ✅      |                        |
| SPSS                | ✅      |                        |
| HTML                | ✅      | With table selection   |

## Why Daflip?

- **Simple**: One command to convert between any supported format
- **Fast**: Optimized for performance with pandas and PyArrow
- **Flexible**: Support for compression, chunking, and custom schemas
- **Reliable**: Comprehensive test suite and error handling

## Get Started

Choose your path:

- [Installation](getting-started/installation.md) - How to install Daflip
- [Quick Start](getting-started/quick-start.md) - Your first conversion
- [User Guide](user-guide/basic-usage.md) - Detailed usage instructions
- [API Reference](api/cli-reference.md) - Complete CLI and Python API docs

## Contributing

We welcome contributions! See our [Contributing Guide](development/contributing.md) for details. 