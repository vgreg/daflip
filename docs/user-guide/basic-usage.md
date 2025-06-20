# Basic Usage

Learn the fundamentals of using Daflip for data format conversion.

## Command Line Interface

Daflip provides a simple command-line interface for converting data files:

```bash
daflip <input_file> <output_file> [options]
```

### Basic Syntax

```bash
# Convert from one format to another
daflip input.csv output.parquet

# Specify input and output formats explicitly
daflip input.csv output.parquet --input-format csv --output-format parquet
```

## Common Options

### Compression

Control compression for output files:

```bash
# Use Snappy compression (fast, good compression)
daflip data.csv data.parquet --compression snappy

# Use Gzip compression (slower, better compression)
daflip data.csv data.parquet --compression gzip --compression-level 9

# No compression
daflip data.csv data.parquet --compression none
```

### Row Selection

Select specific rows from your data:

```bash
# Select first 100 rows
daflip data.csv data.parquet --rows "0:100"

# Select rows 1000-2000
daflip data.csv data.parquet --rows "1000:2000"

# Select last 500 rows (if you know total count)
daflip data.csv data.parquet --rows "9500:10000"
```

### Chunked Processing

For large files, process in chunks to manage memory:

```bash
# Process in chunks of 10,000 rows
daflip large.csv large.parquet --input-chunk-size 10000

# Smaller chunks for very large files
daflip huge.csv huge.parquet --input-chunk-size 1000
```

## Format-Specific Options

### Excel Files

```bash
# Specify sheet name
daflip data.xlsx data.csv --sheet-name "Sheet1"

# Convert specific sheet from multi-sheet file
daflip data.xlsx data.csv --sheet-name "Sales Data"
```

### HTML Files

```bash
# Select specific table from HTML
daflip data.html data.csv --table-number 0

# Convert second table (index 1)
daflip data.html data.csv --table-number 1
```

### SAS Files

```bash
# Keep SAS data as bytes (don't convert to UTF-8)
daflip data.sas7bdat data.csv --sas-keep-bytes

# Convert to UTF-8 (default)
daflip data.sas7bdat data.csv
```

## Schema Management

### Export Schema

```bash
# Export schema to JSON file
daflip --export-schema data.csv schema.json

# Export with specific number of rows for inference
daflip --export-schema data.csv schema.json --nrows 5000
```

### Apply Schema

```bash
# Convert with custom schema
daflip data.csv data.parquet --schema-file schema.json
```

## Examples

### Convert CSV to Parquet with Compression

```bash
daflip sales.csv sales.parquet --compression snappy
```

### Convert Excel to CSV with Sheet Selection

```bash
daflip report.xlsx report.csv --sheet-name "Q4 Data"
```

### Process Large File in Chunks

```bash
daflip large_dataset.csv large_dataset.parquet \
  --input-chunk-size 50000 \
  --compression gzip \
  --compression-level 6
```

### Convert with Row Selection and Schema

```bash
daflip data.csv subset.parquet \
  --rows "1000:2000" \
  --schema-file schema.json \
  --compression snappy
```

## Error Handling

Daflip provides helpful error messages and data previews:

```bash
# If conversion fails, you'll see a preview of the data
daflip problematic.csv output.parquet
# Output: Conversion failed: [error details]
# Partial data preview (error context)
# [data preview table]
```

## Next Steps

- [Supported Formats](supported-formats.md) - Complete format reference
- [Advanced Features](advanced-features.md) - Advanced usage patterns
- [CLI Reference](api/cli-reference.md) - Complete command reference
