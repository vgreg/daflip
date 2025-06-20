# Quick Start

Get up and running with Daflip in minutes.

## Basic Conversion

The simplest way to use Daflip is to convert between formats:

```bash
# Convert CSV to Parquet
daflip data.csv data.parquet

# Convert Excel to CSV
daflip data.xlsx data.csv

# Convert Parquet to Excel
daflip data.parquet data.xlsx
```

## Working with Excel Files

Excel files can have multiple sheets. Specify which sheet to use:

```bash
# Convert a specific sheet
daflip data.xlsx data.csv --sheet-name "Sheet1"

# Convert the first sheet (default)
daflip data.xlsx data.csv
```

## Adding Compression

Many formats support compression to reduce file size:

```bash
# Compress with Snappy (fast)
daflip data.csv data.parquet --compression snappy

# Compress with Gzip (smaller)
daflip data.csv data.parquet --compression gzip --compression-level 6
```

## Processing Large Files

For large files, use chunked processing to manage memory:

```bash
# Process in chunks of 10,000 rows
daflip large.csv large.parquet --input-chunk-size 10000
```

## Row Selection

Select specific rows from your data:

```bash
# Select rows 0-100 (first 100 rows)
daflip data.csv data.parquet --rows "0:100"

# Select rows 1000-2000
daflip data.csv data.parquet --rows "1000:2000"
```

## Working with Schemas

Export a schema from your data:

```bash
# Export schema to JSON
daflip --export-schema data.csv schema.json
```

Apply a schema when converting:

```bash
# Convert with custom schema
daflip data.csv data.parquet --schema-file schema.json
```

## Python API

You can also use Daflip programmatically:

```python
from daflip.services import convert_data

# Basic conversion
convert_data("input.csv", "output.parquet")

# With options
convert_data(
    "input.csv",
    "output.parquet",
    compression="snappy",
    input_chunk_size=10000
)
```

## What's Next?

- [Basic Usage](user-guide/basic-usage.md) - Detailed usage instructions
- [Supported Formats](user-guide/supported-formats.md) - Complete format reference
- [Advanced Features](user-guide/advanced-features.md) - Advanced usage patterns
