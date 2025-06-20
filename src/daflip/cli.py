"""
CLI entrypoint for daflip.

This module provides the command-line interface for the daflip package,
using Typer for argument parsing and command management.
"""

import typer

from .controllers import convert, schema

app = typer.Typer()

app.command()(convert)
app.command()(schema)


def main():
    """Main CLI entry point.

    This function serves as the main entry point for the daflip command-line
    interface. It initializes the Typer app and handles command execution.

    The CLI provides two main commands:
    - convert: Convert data between different formats
    - schema: Infer and export schema from data files
    """
    app()


if __name__ == "__main__":
    main()
