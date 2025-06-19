"""
Controllers for CLI logic and orchestration.
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
    """Convert data between formats."""
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
    """Infer schema from input file and export as JSON."""
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
