"""
Tests for data conversion services.

This module contains comprehensive tests for the data conversion services,
including format roundtrip tests, edge cases, and error handling.
"""

import json

import pandas as pd
import pytest

from src.daflip.services import convert_data, infer_and_export_schema


@pytest.mark.parametrize(
    "fmt,ext,read_func,write_func",
    [
        ("csv", ".csv", pd.read_csv, pd.DataFrame.to_csv),
        ("parquet", ".parquet", pd.read_parquet, pd.DataFrame.to_parquet),
        ("feather", ".feather", pd.read_feather, pd.DataFrame.to_feather),
    ],
)
def test_convert_roundtrip(fmt, ext, read_func, write_func, tmp_path):
    """Test roundtrip conversion between different formats.

    This test verifies that data can be converted from one format to another
    and back without loss of information. It creates a simple DataFrame,
    writes it to a file, converts it to another format, and then verifies
    that the data is preserved.

    Args:
        fmt: Format identifier (e.g., "csv", "parquet")
        ext: File extension (e.g., ".csv", ".parquet")
        read_func: Function to read the format
        write_func: Function to write the format
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create a simple DataFrame
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / f"input{ext}"
    output_file = tmp_path / f"output{ext}"
    # Write input file
    if fmt == "csv":
        df.to_csv(input_file, index=False)
    elif fmt == "parquet":
        df.to_parquet(input_file, index=False)
    elif fmt == "feather":
        df.to_feather(input_file)
    # Convert
    convert_data(str(input_file), str(output_file))
    # Read output and compare
    df2 = read_func(output_file)
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)


@pytest.mark.parametrize(
    "fmt,ext,read_func,write_func",
    [
        ("tsv", ".tsv", pd.read_csv, pd.DataFrame.to_csv),
        ("psv", ".psv", pd.read_csv, pd.DataFrame.to_csv),
        ("orc", ".orc", pd.read_orc, pd.DataFrame.to_orc),
        # Skip Excel and Stata due to dependency issues in test environment
        # ("excel", ".xlsx", pd.read_excel, pd.DataFrame.to_excel),
        # ("stata", ".dta", pd.read_stata, pd.DataFrame.to_stata),
    ],
)
def test_convert_additional_formats(fmt, ext, read_func, write_func, tmp_path):
    """Test conversion for additional supported formats.

    Args:
        fmt: Format identifier
        ext: File extension
        read_func: Function to read the format
        write_func: Function to write the format
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create a simple DataFrame
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / f"input{ext}"
    output_file = tmp_path / "output.csv"

    # Write input file with appropriate parameters
    if fmt == "tsv":
        df.to_csv(input_file, sep="\t", index=False)
    elif fmt == "psv":
        df.to_csv(input_file, sep="|", index=False)
    elif fmt == "orc":
        df.to_orc(input_file, index=False)
    # Skip Excel and Stata due to dependency issues
    # elif fmt == "excel":
    #     df.to_excel(input_file, index=False)
    # elif fmt == "stata":
    #     df.to_stata(input_file)

    # Convert to CSV
    convert_data(str(input_file), str(output_file))

    # Read back and verify
    df_result = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(df, df_result, check_dtype=False)


def test_convert_with_compression(tmp_path):
    """Test conversion with compression options.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.parquet"

    df.to_csv(input_file, index=False)

    # Test with compression
    convert_data(str(input_file), str(output_file), compression="snappy")

    # Verify file was created and can be read
    df2 = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)


def test_convert_with_compression_level(tmp_path):
    """Test conversion with compression level settings.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.parquet"

    df.to_csv(input_file, index=False)

    # Test with compression and compression level
    convert_data(
        str(input_file), str(output_file), compression="gzip", compression_level=6
    )

    # Verify file was created and can be read
    df2 = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)


def test_chunked_conversion_csv_to_csv(tmp_path):
    """Test chunked conversion from CSV to CSV.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create a larger DataFrame for chunked processing
    df = pd.DataFrame({"a": range(100), "b": [f"row_{i}" for i in range(100)]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    df.to_csv(input_file, index=False)

    # Convert with chunking
    convert_data(str(input_file), str(output_file), input_chunk_size=25)

    # Verify result
    df2 = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)


def test_chunked_conversion_csv_to_parquet(tmp_path):
    """Test chunked conversion from CSV to Parquet.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create a larger DataFrame for chunked processing
    df = pd.DataFrame({"a": range(100), "b": [f"row_{i}" for i in range(100)]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.parquet"

    df.to_csv(input_file, index=False)

    # Convert with chunking
    convert_data(str(input_file), str(output_file), input_chunk_size=25)

    # Verify result
    df2 = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)


def test_chunked_conversion_validation(tmp_path):
    """Test chunking validation for unsupported formats.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.parquet"
    output_file = tmp_path / "output.csv"

    df.to_parquet(input_file, index=False)

    # Test that chunked reading raises error for unsupported format
    with pytest.raises(NotImplementedError, match="Chunked reading is not supported"):
        convert_data(str(input_file), str(output_file), input_chunk_size=1000)


def test_convert_row_selection(tmp_path):
    """Test row selection functionality during conversion.

    This test verifies that the row selection feature works correctly
    by converting only a subset of rows from the input file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": range(10)})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    df.to_csv(input_file, index=False)
    convert_data(str(input_file), str(output_file), rows="2:5")
    df2 = pd.read_csv(output_file)
    assert df2.shape[0] == 3
    assert df2["a"].tolist() == [2, 3, 4]


def test_row_selection_invalid_format(tmp_path):
    """Test row selection with invalid format.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": range(10)})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    df.to_csv(input_file, index=False)

    # Test invalid row format - should continue without row selection
    convert_data(str(input_file), str(output_file), rows="invalid")

    # Should convert all rows
    df2 = pd.read_csv(output_file)
    assert df2.shape[0] == 10


def test_row_selection_out_of_bounds(tmp_path):
    """Test row selection with out-of-bounds indices.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": range(5)})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    df.to_csv(input_file, index=False)

    # Test out-of-bounds selection
    convert_data(str(input_file), str(output_file), rows="10:20")

    # Should result in empty dataframe
    df2 = pd.read_csv(output_file)
    assert df2.shape[0] == 0


def test_row_selection_empty_result(tmp_path):
    """Test row selection that results in empty dataframe.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": range(5)})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    df.to_csv(input_file, index=False)

    # Test selection that results in empty result
    convert_data(str(input_file), str(output_file), rows="3:3")

    # Should result in empty dataframe
    df2 = pd.read_csv(output_file)
    assert df2.shape[0] == 0


def test_convert_with_schema_file(tmp_path):
    """Test conversion with custom schema file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create schema file
    schema_data = {
        "fields": [{"name": "a", "type": "int64"}, {"name": "b", "type": "string"}]
    }
    schema_file = tmp_path / "schema.json"
    with open(schema_file, "w") as f:
        json.dump(schema_data, f)

    # Create input data
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.parquet"

    df.to_csv(input_file, index=False)

    # Convert with schema
    convert_data(str(input_file), str(output_file), schema_file=str(schema_file))

    # Verify result
    df2 = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)


def test_schema_file_not_found(tmp_path):
    """Test error handling for missing schema file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    schema_file = tmp_path / "nonexistent.json"

    df.to_csv(input_file, index=False)

    with pytest.raises(FileNotFoundError):
        convert_data(str(input_file), str(output_file), schema_file=str(schema_file))


def test_schema_file_invalid_json(tmp_path):
    """Test error handling for invalid JSON schema.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create invalid JSON schema file
    schema_file = tmp_path / "schema.json"
    with open(schema_file, "w") as f:
        f.write("invalid json content")

    df = pd.DataFrame({"a": [1, 2, 3]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    df.to_csv(input_file, index=False)

    with pytest.raises(json.JSONDecodeError):
        convert_data(str(input_file), str(output_file), schema_file=str(schema_file))


def test_convert_excel_with_sheet_name(tmp_path):
    """Test Excel conversion with specific sheet.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create Excel file with multiple sheets
    df1 = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    df2 = pd.DataFrame({"c": [4, 5, 6], "d": ["a", "b", "c"]})

    input_file = tmp_path / "input.xlsx"
    output_file = tmp_path / "output.csv"

    with pd.ExcelWriter(input_file) as writer:
        df1.to_excel(writer, sheet_name="Sheet1", index=False)
        df2.to_excel(writer, sheet_name="Sheet2", index=False)

    # Convert specific sheet
    convert_data(str(input_file), str(output_file), sheet_name="Sheet1")

    # Verify correct sheet was converted
    df_result = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(df1, df_result, check_dtype=False)


def test_convert_excel_invalid_sheet(tmp_path):
    """Test Excel conversion with invalid sheet name.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """

    df = pd.DataFrame({"a": [1, 2, 3]})
    input_file = tmp_path / "input.xlsx"
    output_file = tmp_path / "output.csv"

    df.to_excel(input_file, index=False)

    # Should raise an error for invalid sheet
    with pytest.raises(Exception):
        convert_data(str(input_file), str(output_file), sheet_name="InvalidSheet")


def test_convert_unsupported_format(tmp_path):
    """Test error handling for unsupported input formats.

    This test verifies that the convert_data function raises a ValueError
    when attempting to convert from an unsupported format.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    input_file = tmp_path / "input.unsupported"
    output_file = tmp_path / "output.csv"
    with open(input_file, "w") as f:
        f.write("dummy")
    with pytest.raises(ValueError):
        convert_data(str(input_file), str(output_file))


def test_convert_fixed_not_implemented(tmp_path):
    """Test error handling for not-yet-implemented formats.

    This test verifies that the convert_data function raises a NotImplementedError
    when attempting to convert from a format that is declared but not yet
    implemented (like fixed-width files).

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    input_file = tmp_path / "input.fixed"
    output_file = tmp_path / "output.csv"
    with open(input_file, "w") as f:
        f.write("dummy")
    with pytest.raises(NotImplementedError):
        convert_data(str(input_file), str(output_file))


def test_file_not_found_error(tmp_path):
    """Test error handling for missing input files.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    input_file = tmp_path / "nonexistent.csv"
    output_file = tmp_path / "output.csv"

    with pytest.raises(FileNotFoundError):
        convert_data(str(input_file), str(output_file))


def test_unsupported_output_format(tmp_path):
    """Test error handling for unsupported output formats.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3]})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.unsupported"

    df.to_csv(input_file, index=False)

    with pytest.raises(ValueError, match="Unsupported output format"):
        convert_data(str(input_file), str(output_file))


# Schema inference tests
def test_schema_inference_csv(tmp_path):
    """Test schema inference from CSV file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame(
        {"int_col": [1, 2, 3], "str_col": ["a", "b", "c"], "float_col": [1.1, 2.2, 3.3]}
    )
    input_file = tmp_path / "input.csv"
    schema_file = tmp_path / "schema.json"

    df.to_csv(input_file, index=False)

    infer_and_export_schema(str(input_file), None, str(schema_file))

    # Verify schema file was created and has correct structure
    with open(schema_file, "r") as f:
        schema_data = json.load(f)

    assert "fields" in schema_data
    field_names = [f["name"] for f in schema_data["fields"]]
    assert "int_col" in field_names
    assert "str_col" in field_names
    assert "float_col" in field_names


def test_schema_inference_parquet(tmp_path):
    """Test schema inference from Parquet file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"int_col": [1, 2, 3], "str_col": ["a", "b", "c"]})
    input_file = tmp_path / "input.parquet"
    schema_file = tmp_path / "schema.json"

    df.to_parquet(input_file, index=False)

    infer_and_export_schema(str(input_file), None, str(schema_file))

    # Verify schema file was created
    with open(schema_file, "r") as f:
        schema_data = json.load(f)

    assert "fields" in schema_data
    assert len(schema_data["fields"]) == 2


def test_schema_inference_with_nrows(tmp_path):
    """Test schema inference with row limit.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create large dataframe
    df = pd.DataFrame({"col1": range(1000), "col2": [f"row_{i}" for i in range(1000)]})
    input_file = tmp_path / "input.csv"
    schema_file = tmp_path / "schema.json"

    df.to_csv(input_file, index=False)

    # Infer schema with limited rows
    infer_and_export_schema(str(input_file), None, str(schema_file), nrows=100)

    # Verify schema file was created
    with open(schema_file, "r") as f:
        schema_data = json.load(f)

    assert "fields" in schema_data
    assert len(schema_data["fields"]) == 2


def test_schema_export_format(tmp_path):
    """Test that exported schema has correct JSON format.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"test_col": [1, 2, 3]})
    input_file = tmp_path / "input.csv"
    schema_file = tmp_path / "schema.json"

    df.to_csv(input_file, index=False)

    infer_and_export_schema(str(input_file), None, str(schema_file))

    # Verify JSON structure
    with open(schema_file, "r") as f:
        schema_data = json.load(f)

    assert isinstance(schema_data, dict)
    assert "fields" in schema_data
    assert isinstance(schema_data["fields"], list)

    for field in schema_data["fields"]:
        assert "name" in field
        assert "type" in field
        assert isinstance(field["name"], str)
        assert isinstance(field["type"], str)


@pytest.mark.skipif(
    not (
        pytest.importorskip("xlrd", reason="xlrd required for .xls")
        and pytest.importorskip("xlwt", reason="xlwt required for .xls")
    ),
    reason="xlrd and xlwt required for .xls support",
)
def test_convert_xls_roundtrip(tmp_path):
    """Test roundtrip conversion for .xls format."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.xls"
    output_file = tmp_path / "output.xls"
    # Write input file
    df.to_excel(input_file, index=False, engine="xlwt")
    # Convert to .xls (should use xlrd/xlwt)
    convert_data(str(input_file), str(output_file))
    # Read output and compare
    df2 = pd.read_excel(output_file, engine="xlrd")
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)


@pytest.mark.skipif(
    not (
        pytest.importorskip("xlrd", reason="xlrd required for .xls")
        and pytest.importorskip("xlwt", reason="xlwt required for .xls")
    ),
    reason="xlrd and xlwt required for .xls support",
)
def test_convert_xls_with_sheet_name(tmp_path):
    """Test .xls conversion with a specific sheet name."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.xls"
    output_file = tmp_path / "output.xls"
    # Write input file with a custom sheet name
    df.to_excel(input_file, index=False, sheet_name="MySheet", engine="xlwt")
    # Convert, specifying the sheet name
    convert_data(str(input_file), str(output_file), sheet_name="MySheet")
    # Read output and compare
    df2 = pd.read_excel(output_file, sheet_name="MySheet", engine="xlrd")
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)
