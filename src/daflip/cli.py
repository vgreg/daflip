"""
CLI entrypoint for daflip.
"""

import typer

from .controllers import convert, schema

app = typer.Typer()

app.command()(convert)
app.command()(schema)


def main():
    app()


if __name__ == "__main__":
    main()
