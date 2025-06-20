# CLI Reference

Complete reference for the Daflip command-line interface.

## Command Overview

```bash
daflip [OPTIONS] INPUT_FILE OUTPUT_FILE
daflip --export-schema INPUT_FILE OUTPUT_SCHEMA_FILE [OPTIONS]
```

## Global Options

| Option         | Description              | Default |
| -------------- | ------------------------ | ------- |
| `--help`, `-h` | Show help message        |         |
| `--version`    | Show version information |         |

## Conversion Options

### Input/Output Format

| Option            | Description                      | Default                           |
| ----------------- | -------------------------------- | --------------------------------- |
| `--input-format`  | Specify input format explicitly  | Auto-detected from file extension |
| `--output-format` | Specify output format explicitly | Auto-detected from file extension |

### Compression

| Option                | Description                           | Default            |
| --------------------- | ------------------------------------- | ------------------ |
| `--compression`       | Compression type (gzip, snappy, none) | None               |
| `--compression-level` | Compression level (1-9 for gzip)      | Default for format |

### Data Selection

| Option                | Description                            | Default     |
| --------------------- | -------------------------------------- | ----------- |
| `--rows`              | Row selection in format "start:end"    | All rows    |
| `--input-chunk-size`  | Size of chunks for reading large files | No chunking |
| `--output-chunk-size` | Size of chunks for writing (unused)    | No chunking |

### Format-Specific Options

| Option             | Description                             | Default     |
| ------------------ | --------------------------------------- | ----------- |
| `--sheet-name`     | Sheet name for Excel files              | First sheet |
| `--table-number`   | Table number for HTML files (0-indexed) | First table |
| `--sas-keep-bytes` | Keep SAS data as bytes instead of UTF-8 | False       |

### Schema Management

| Option            | Description                         | Default |
| ----------------- | ----------------------------------- | ------- |
| `--schema-file`   | JSON file specifying schema to use  | None    |
| `--export-schema` | Export schema to JSON file          | False   |
| `--nrows`         | Number of rows for schema inference | 10000   |

## Supported Formats

### Input Formats

| Format   | Extension       | Notes                  |
| -------- | --------------- | ---------------------- |
| CSV      | `.csv`          | With custom separators |
| TSV      | `.tsv`          | Tab-separated values   |
| PSV      | `.psv`          | Pipe-separated values  |
| Parquet  | `.parquet`      |                        |
| Excel    | `.xlsx`, `.xls` | Requires openpyxl/xlrd |
| Feather  | `.feather`      |                        |
| ORC      | `.orc`          |                        |
| SAS7BDAT | `.sas7bdat`     |                        |
| Stata    | `.dta`          |                        |
| SPSS     | `.sav`          |                        |
| HTML     | `.html`         |                        |

### Output Formats

| Format  | Extension       | Compression  | Notes |
| ------- | --------------- | ------------ | ----- |
| CSV     | `.csv`          | None         |       |
| Parquet | `.parquet`      | Snappy, Gzip |       |
| Excel   | `.xlsx`, `.xls` | None         |       |
| Feather | `.feather`      | None         |       |
| ORC     | `.orc`          | None         |       |
| Stata   | `.dta`          | None         |       |

## Examples

### Basic Conversion

```bash
# Convert CSV to Parquet
daflip data.csv data.parquet

# Convert Excel to CSV
daflip data.xlsx data.csv

# Convert with explicit formats
daflip data.csv data.parquet --input-format csv --output-format parquet
```

### Compression Examples

```bash
# Snappy compression (fast)
daflip data.csv data.parquet --compression snappy

# Gzip compression with level
daflip data.csv data.parquet --compression gzip --compression-level 9

# No compression
daflip data.csv data.parquet --compression none
```

### Row Selection

```bash
# First 100 rows
daflip data.csv data.parquet --rows "0:100"

# Rows 1000-2000
daflip data.csv data.parquet --rows "1000:2000"

# Last 500 rows (if you know total)
daflip data.csv data.parquet --rows "9500:10000"
```

### Excel Files

```bash
# Specific sheet
daflip data.xlsx data.csv --sheet-name "Sheet1"

# Different sheet names
daflip data.xlsx data.csv --sheet-name "Sales Data"
```

### Large Files

```bash
# Chunked processing
daflip large.csv large.parquet --input-chunk-size 10000

# With compression
daflip large.csv large.parquet --input-chunk-size 10000 --compression snappy
```

### Schema Management

```bash
# Export schema
daflip --export-schema data.csv schema.json

# Export with custom row count
daflip --export-schema data.csv schema.json --nrows 5000

# Apply schema
daflip data.csv data.parquet --schema-file schema.json
```

### HTML Files

```bash
# First table
daflip data.html data.csv --table-number 0

# Second table
daflip data.html data.csv --table-number 1
```

### SAS Files

```bash
# Keep as bytes
daflip data.sas7bdat data.csv --sas-keep-bytes

# Convert to UTF-8 (default)
daflip data.sas7bdat data.csv
```

## Exit Codes

| Code | Description        |
| ---- | ------------------ |
| 0    | Success            |
| 1    | General error      |
| 2    | Invalid arguments  |
| 3    | File not found     |
| 4    | Unsupported format |

## Environment Variables

| Variable           | Description                                 | Default |
| ------------------ | ------------------------------------------- | ------- |
| `DAFLIP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO    |

## Configuration Files

Daflip currently doesn't support configuration files, but this feature is planned for future releases.
