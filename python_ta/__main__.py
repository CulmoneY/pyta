from __future__ import annotations

import sys
from os import path
from typing import Optional

import click

from python_ta import __version__, check_all, check_errors
from python_ta.config import DEFAULT_CONFIG_LOCATION

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-v", "--version", is_flag=True, help="Print current version of PythonTA.", default=False
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="python_ta configuration file",
)
@click.option("-E", "--errors-only", is_flag=True, help="Displays errors only", default=False)
@click.argument(
    "filenames", nargs=-1, type=click.Path(exists=True, dir_okay=True, resolve_path=True)
)
@click.option("--exit-zero", is_flag=True, help="Always return with status code 0", default=False)
@click.option(
    "-g",
    "--generate-config",
    is_flag=True,
    help="Print out default PythonTA configuration file",
    default=False,
)
@click.option(
    "--output-format",
    help="Specify the format of output report. This option is ignored if a --config argument is specified.",
    default="pyta-html",
)
def main(
    version: bool,
    config: Optional[str],
    errors_only: bool,
    filenames: list[str],
    exit_zero: bool,
    generate_config: bool,
    output_format: str,
) -> None:
    """A code checking tool for teaching Python.
    FILENAMES can be a string of a directory, or file to check (`.py` extension optional) or
    a list of strings of directories or files.
    """
    if version:
        print(__version__)
        return

    # `config` is None if `-c` flag is not set
    if generate_config:
        pylintrc_location = path.join(path.dirname(__file__), DEFAULT_CONFIG_LOCATION)
        with open(pylintrc_location, "r") as f:
            contents = f.read()
            print(contents)
            sys.exit(0)

    checker = check_errors if errors_only else check_all
    paths = [click.format_filename(fn) for fn in filenames]

    if config is None:
        reporter = checker(module_name=paths, config={"output-format": output_format})
    else:
        reporter = checker(module_name=paths, config=config)

    if not exit_zero and reporter.has_messages():
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
