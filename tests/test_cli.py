"""
Tests for CLI functionality.

This module contains tests for the command-line interface functionality
of the daflip package.
"""

from typer.testing import CliRunner

from src.daflip.cli import app


def test_cli_runs():
    """Test that the CLI can be imported and runs without errors.

    This is a placeholder test to ensure the CLI module can be imported
    and basic functionality works. More comprehensive CLI tests should be
    added as the CLI functionality expands.
    """
    assert True  # Placeholder


def test_cli_help():
    """Test CLI help output.

    This test verifies that the CLI provides help information
    and lists available commands.
    """
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "convert" in result.output
    assert "schema" in result.output
    # The output might not contain "daflip" directly, so check for command structure
    assert "Usage:" in result.output


def test_cli_convert_help():
    """Test convert command help.

    This test verifies that the convert command provides
    detailed help information with all available options.
    """
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--help"])

    assert result.exit_code == 0
    # Check for argument names in the help output
    assert "INPUT_FILE" in result.output or "input-file" in result.output
    assert "OUTPUT_FILE" in result.output or "output-file" in result.output


def test_cli_schema_help():
    """Test schema command help.

    This test verifies that the schema command provides
    detailed help information with all available options.
    """
    runner = CliRunner()
    result = runner.invoke(app, ["schema", "--help"])

    assert result.exit_code == 0
    # Check for argument names in the help output
    assert "INPUT_FILE" in result.output or "input-file" in result.output
    assert "OUTPUT_FILE" in result.output or "output-file" in result.output


def test_cli_convert_basic(tmp_path):
    """Test basic convert command functionality.

    This test verifies that the convert command can perform
    a basic file conversion.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import pandas as pd

    # Create test data
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.parquet"

    df.to_csv(input_file, index=False)

    runner = CliRunner()
    result = runner.invoke(app, ["convert", str(input_file), str(output_file)])

    assert result.exit_code == 0
    assert "Conversion successful" in result.output
    # Check that the output file path is mentioned (handle newlines)
    assert str(output_file).replace("/", "") in result.output.replace("\n", "").replace(
        "/", ""
    )


def test_cli_convert_with_options(tmp_path):
    """Test convert command with various options.

    This test verifies that the convert command accepts
    and processes various command-line options correctly.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import pandas as pd

    # Create test data
    df = pd.DataFrame({"a": range(10), "b": [f"row_{i}" for i in range(10)]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    df.to_csv(input_file, index=False)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "convert",
            str(input_file),
            str(output_file),
            "--rows",
            "2:5",
            "--compression",
            "gzip",
        ],
    )

    assert result.exit_code == 0
    assert "Conversion successful" in result.output


def test_cli_convert_missing_input_file(tmp_path):
    """Test convert command with missing input file.

    This test verifies that the convert command provides
    appropriate error messages when the input file doesn't exist.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    output_file = tmp_path / "output.csv"

    runner = CliRunner()
    result = runner.invoke(app, ["convert", "nonexistent.csv", str(output_file)])

    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_convert_invalid_format(tmp_path):
    """Test convert command with invalid format.

    This test verifies that the convert command provides
    appropriate error messages when an invalid format is specified.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import pandas as pd

    # Create test data
    df = pd.DataFrame({"a": [1, 2, 3]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.unsupported"

    df.to_csv(input_file, index=False)

    runner = CliRunner()
    result = runner.invoke(app, ["convert", str(input_file), str(output_file)])

    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_schema_basic(tmp_path):
    """Test basic schema command functionality.

    This test verifies that the schema command can infer
    and export schema from a data file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import pandas as pd

    # Create test data
    df = pd.DataFrame(
        {"int_col": [1, 2, 3], "str_col": ["a", "b", "c"], "float_col": [1.1, 2.2, 3.3]}
    )
    input_file = tmp_path / "input.csv"
    schema_file = tmp_path / "schema.json"

    df.to_csv(input_file, index=False)

    runner = CliRunner()
    result = runner.invoke(app, ["schema", str(input_file), str(schema_file)])

    assert result.exit_code == 0
    assert "Schema exported" in result.output
    # Check that the output file path is mentioned (handle newlines)
    assert str(schema_file).replace("/", "") in result.output.replace("\n", "").replace(
        "/", ""
    )


def test_cli_schema_with_options(tmp_path):
    """Test schema command with various options.

    This test verifies that the schema command accepts
    and processes various command-line options correctly.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import pandas as pd

    # Create test data
    df = pd.DataFrame({"col1": range(100), "col2": [f"row_{i}" for i in range(100)]})
    input_file = tmp_path / "input.csv"
    schema_file = tmp_path / "schema.json"

    df.to_csv(input_file, index=False)

    runner = CliRunner()
    result = runner.invoke(
        app, ["schema", str(input_file), str(schema_file), "--nrows", "50"]
    )

    assert result.exit_code == 0
    assert "Schema exported" in result.output


def test_cli_schema_missing_input_file(tmp_path):
    """Test schema command with missing input file.

    This test verifies that the schema command provides
    appropriate error messages when the input file doesn't exist.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    schema_file = tmp_path / "schema.json"

    runner = CliRunner()
    result = runner.invoke(app, ["schema", "nonexistent.csv", str(schema_file)])

    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_invalid_command():
    """Test CLI with invalid command.

    This test verifies that the CLI provides appropriate
    error messages when an invalid command is provided.
    """
    runner = CliRunner()
    result = runner.invoke(app, ["invalid-command"])

    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_missing_arguments():
    """Test CLI commands with missing required arguments.

    This test verifies that the CLI provides appropriate
    error messages when required arguments are missing.
    """
    runner = CliRunner()

    # Test convert with missing arguments
    result = runner.invoke(app, ["convert"])
    assert result.exit_code != 0

    # Test schema with missing arguments
    result = runner.invoke(app, ["schema"])
    assert result.exit_code != 0


def test_cli_convert_with_chunking(tmp_path):
    """Test convert command with chunking option.

    This test verifies that the convert command can handle
    chunked processing for large files.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import pandas as pd

    # Create larger test data
    df = pd.DataFrame({"a": range(100), "b": [f"row_{i}" for i in range(100)]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    df.to_csv(input_file, index=False)

    runner = CliRunner()
    result = runner.invoke(
        app, ["convert", str(input_file), str(output_file), "--input-chunk-size", "25"]
    )

    assert result.exit_code == 0
    assert "Conversion successful" in result.output


def test_cli_convert_with_schema_file(tmp_path):
    """Test convert command with schema file.

    This test verifies that the convert command can use
    a custom schema file for conversion.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import json

    import pandas as pd

    # Create schema file
    schema_data = {
        "fields": [{"name": "a", "type": "int64"}, {"name": "b", "type": "string"}]
    }
    schema_file = tmp_path / "schema.json"
    with open(schema_file, "w") as f:
        json.dump(schema_data, f)

    # Create test data
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.parquet"

    df.to_csv(input_file, index=False)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "convert",
            str(input_file),
            str(output_file),
            "--schema-file",
            str(schema_file),
        ],
    )

    assert result.exit_code == 0
    assert "Conversion successful" in result.output
