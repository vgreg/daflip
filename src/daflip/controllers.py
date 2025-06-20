"""
Controllers for CLI logic and orchestration.

This module contains the controller functions that handle CLI command logic,
providing the interface between the command-line arguments and the underlying
services. It handles error reporting and user feedback.
"""

import typer
from rich.console import Console

from .config import get_config
from .services import convert_data

console = Console()


def convert(
    input_file: str = typer.Argument(..., help="Input data file path"),
    output_file: str = typer.Argument(..., help="Output file path"),
    input_format: str = typer.Option(None, help="Override input format (optional)"),
    output_format: str = typer.Option(None, help="Override output format (optional)"),
    compression: str = typer.Option(None, help="Compression type (optional)"),
    compression_level: int = typer.Option(None, help="Compression level (optional)"),
    rows: str = typer.Option(None, help="Row selection (e.g., 0:100)"),
    sheet_name: str = typer.Option(None, help="Excel sheet name (optional)"),
    table_number: int = typer.Option(None, help="HTML table number (optional)"),
    sas_keep_bytes: bool = typer.Option(
        False, help="Keep SAS string columns as bytes (default: convert to string)"
    ),
    input_chunk_size: int = typer.Option(
        None, help="Number of rows per chunk to read (default: all at once)"
    ),
    output_chunk_size: int = typer.Option(
        None, help="Number of rows per chunk to write (default: all at once)"
    ),
    schema_file: str = typer.Option(
        None, help="Optional JSON file specifying schema to use for reading/writing."
    ),
):
    """Convert data between different formats.

    This command converts data files between supported formats. It automatically
    detects input and output formats from file extensions unless overridden.

    The command supports various options for customization:
    - Format overrides for input and output
    - Compression settings for output files
    - Row selection for partial data conversion
    - Sheet selection for Excel files
    - Table selection for HTML files
    - Chunked processing for large files
    - Custom schemas for reading/writing

    Args:
        input_file: Path to the input data file
        output_file: Path for the output file
        input_format: Override for input format detection
        output_format: Override for output format detection
        compression: Compression type (e.g., "gzip", "snappy")
        compression_level: Compression level (1-9 for gzip)
        rows: Row selection range (e.g., "0:100")
        sheet_name: Excel sheet name
        table_number: HTML table number (0-indexed)
        sas_keep_bytes: Keep SAS data as bytes
        input_chunk_size: Chunk size for reading large files
        output_chunk_size: Chunk size for writing (currently unused)
        schema_file: JSON schema file path

    Example:
        $ daflip convert data.csv output.parquet --compression snappy
        $ daflip convert large.csv output.csv --input-chunk-size 10000
        $ daflip convert data.xlsx output.csv --sheet-name "Sheet1" --rows "0:100"
    """
    try:
        config = get_config()
        convert_data(
            input_file=input_file,
            output_file=output_file,
            input_format=input_format,
            output_format=output_format,
            compression=compression,
            compression_level=compression_level,
            rows=rows,
            sheet_name=sheet_name,
            table_number=table_number,
            sas_keep_bytes=sas_keep_bytes,
            input_chunk_size=input_chunk_size,
            output_chunk_size=output_chunk_size,
            schema_file=schema_file,
            config=config,
        )
        console.print(f"[green]Conversion successful! Output written to {output_file}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        # Optionally: show first few rows if available
        raise typer.Exit(1)


def schema(
    input_file: str = typer.Argument(..., help="Input data file path"),
    input_format: str = typer.Option(None, help="Override input format (optional)"),
    output_file: str = typer.Argument(..., help="Output schema JSON file path"),
    nrows: int = typer.Option(
        10000, help="Number of rows to use for schema inference (default: 10000)"
    ),
    sheet_name: str = typer.Option(None, help="Excel sheet name (optional)"),
    table_number: int = typer.Option(None, help="HTML table number (optional)"),
):
    """Infer schema from input file and export as JSON.

    This command analyzes a data file to infer its schema and exports it
    as a JSON file. The schema can be used for data validation or as input
    to the convert command.

    For large files, only the first nrows are read to speed up schema inference.
    The inferred schema includes field names and data types.

    Args:
        input_file: Path to the input data file
        input_format: Override for input format detection
        output_file: Path for the output JSON schema file
        nrows: Number of rows to read for schema inference
        sheet_name: Excel sheet name
        table_number: HTML table number (0-indexed)

    Example:
        $ daflip schema data.csv schema.json
        $ daflip schema data.xlsx schema.json --sheet-name "Sheet1"
        $ daflip schema large.csv schema.json --nrows 1000
    """
    from .services import infer_and_export_schema

    try:
        infer_and_export_schema(
            input_file=input_file,
            input_format=input_format,
            output_file=output_file,
            nrows=nrows,
            sheet_name=sheet_name,
            table_number=table_number,
        )
        console.print(f"[green]Schema exported to {output_file}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
