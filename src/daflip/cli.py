"""
CLI entrypoint for daflip.
"""

import typer

from .controllers import main_controller


def main():
    typer.run(main_controller)


if __name__ == "__main__":
    main()
