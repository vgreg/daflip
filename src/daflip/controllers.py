"""
Controllers for CLI logic and orchestration.
"""

import typer
from rich.console import Console

from .config import get_config
from .services import convert_data

console = Console()


def main_controller(
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
):
    """Main CLI controller."""
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
            config=config,
        )
        console.print(f"[green]Conversion successful! Output written to {output_file}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        # Optionally: show first few rows if available
