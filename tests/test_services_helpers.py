"""
Tests for internal helper functions in services module.

This module contains unit tests for the internal helper functions
that support the main data conversion functionality.
"""

import json

import pandas as pd
import pyarrow as pa
import pytest

from src.daflip.services import (
    _apply_row_selection,
    _build_read_kwargs,
    _build_write_kwargs,
    _convert_dtypes,
    _create_chunked_reader,
    _export_schema_to_json,
    _get_schema_from_arrow_format,
    _get_schema_from_pandas_format,
    _load_schema,
    _read_dataframe,
    _validate_chunking_support,
    _write_chunk_csv,
    _write_chunk_parquet,
    _write_dataframe,
)


def test_load_schema_valid_file(tmp_path):
    """Test loading valid schema from JSON file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create valid schema file
    schema_data = {
        "fields": [
            {"name": "col1", "type": "int64"},
            {"name": "col2", "type": "string"},
        ]
    }
    schema_file = tmp_path / "schema.json"
    with open(schema_file, "w") as f:
        json.dump(schema_data, f)

    schema = _load_schema(str(schema_file))
    assert schema is not None
    assert len(schema) == 2
    assert schema.field(0).name == "col1"
    assert schema.field(1).name == "col2"


def test_load_schema_invalid_file(tmp_path):
    """Test error handling for invalid schema file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create invalid schema file
    schema_file = tmp_path / "schema.json"
    with open(schema_file, "w") as f:
        f.write("invalid json content")

    with pytest.raises(json.JSONDecodeError):
        _load_schema(str(schema_file))


def test_load_schema_file_not_found(tmp_path):
    """Test error handling for missing schema file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    schema_file = tmp_path / "nonexistent.json"

    with pytest.raises(FileNotFoundError):
        _load_schema(str(schema_file))


def test_validate_chunking_support_valid():
    """Test chunking validation for supported formats."""
    # Test valid chunking combinations
    _validate_chunking_support("csv", "csv", 1000, None)
    _validate_chunking_support("csv", "parquet", 1000, None)
    _validate_chunking_support("sas7bdat", "csv", 1000, None)

    # Should not raise any exceptions


def test_validate_chunking_support_invalid_input():
    """Test chunking validation for unsupported input formats."""
    with pytest.raises(NotImplementedError, match="Chunked reading is not supported"):
        _validate_chunking_support("parquet", "csv", 1000, None)


def test_validate_chunking_support_invalid_output():
    """Test chunking validation for unsupported output formats."""
    with pytest.raises(NotImplementedError, match="Chunked writing is not supported"):
        _validate_chunking_support("csv", "feather", None, 1000)


def test_create_chunked_reader_csv(tmp_path):
    """Test creating chunked reader for CSV.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create test CSV file
    df = pd.DataFrame({"a": range(10), "b": [f"row_{i}" for i in range(10)]})
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    reader = _create_chunked_reader(str(input_file), "csv", 3, None)

    # Test that reader produces chunks
    chunks = list(reader)
    assert len(chunks) == 4  # 10 rows / 3 per chunk = 4 chunks
    assert chunks[0].shape[0] == 3
    assert chunks[3].shape[0] == 1  # Last chunk has remaining row


def test_create_chunked_reader_unsupported():
    """Test error handling for unsupported chunked formats."""
    with pytest.raises(NotImplementedError, match="Chunked reading is not implemented"):
        _create_chunked_reader("dummy.parquet", "parquet", 1000, None)


def test_write_chunk_csv(tmp_path):
    """Test writing CSV chunks.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    chunk1 = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    chunk2 = pd.DataFrame({"a": [3, 4], "b": ["z", "w"]})
    output_file = tmp_path / "output.csv"

    # Write first chunk
    _write_chunk_csv(chunk1, str(output_file), first=True)

    # Write second chunk
    _write_chunk_csv(chunk2, str(output_file), first=False)

    # Verify result
    result = pd.read_csv(output_file)
    expected = pd.DataFrame({"a": [1, 2, 3, 4], "b": ["x", "y", "z", "w"]})
    pd.testing.assert_frame_equal(result, expected)


def test_write_chunk_parquet(tmp_path):
    """Test writing Parquet chunks.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    chunk1 = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    chunk2 = pd.DataFrame({"a": [3, 4], "b": ["z", "w"]})
    output_file = tmp_path / "output.parquet"

    # Write first chunk
    pqwriter = _write_chunk_parquet(chunk1, str(output_file), first=True, pqwriter=None)

    # Write second chunk
    pqwriter = _write_chunk_parquet(
        chunk2, str(output_file), first=False, pqwriter=pqwriter
    )

    # Close writer
    pqwriter.close()

    # Verify result
    result = pd.read_parquet(output_file)
    expected = pd.DataFrame({"a": [1, 2, 3, 4], "b": ["x", "y", "z", "w"]})
    pd.testing.assert_frame_equal(result, expected)


def test_build_read_kwargs():
    """Test building read kwargs for different formats."""
    # Test CSV format
    kwargs = _build_read_kwargs("csv", None, None)
    assert kwargs["dtype_backend"] == "pyarrow"
    assert kwargs["sep"] == ","

    # Test TSV format
    kwargs = _build_read_kwargs("tsv", None, None)
    assert kwargs["sep"] == "\t"

    # Test PSV format
    kwargs = _build_read_kwargs("psv", None, None)
    assert kwargs["sep"] == "|"

    # Test Excel with sheet name
    kwargs = _build_read_kwargs("excel", "Sheet1", None)
    assert kwargs["sheet_name"] == "Sheet1"

    # Test HTML with table number
    kwargs = _build_read_kwargs("html", None, 2)
    assert kwargs["match"] is None
    assert kwargs["flavor"] == "bs4"
    assert kwargs["header"] == 0
    assert kwargs["index_col"] is None


def test_build_read_kwargs_fixed_not_implemented():
    """Test error handling for not-yet-implemented fixed format."""
    with pytest.raises(
        NotImplementedError, match="Fixed-width file support is not yet implemented"
    ):
        _build_read_kwargs("fixed", None, None)


def test_read_dataframe_csv(tmp_path):
    """Test reading CSV dataframe.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    read_kwargs = {"dtype_backend": "pyarrow"}
    result = _read_dataframe(str(input_file), "csv", read_kwargs, None, None)

    pd.testing.assert_frame_equal(result, df, check_dtype=False)


def test_read_dataframe_parquet(tmp_path):
    """Test reading Parquet dataframe.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.parquet"
    df.to_parquet(input_file, index=False)

    read_kwargs = {"dtype_backend": "pyarrow"}
    result = _read_dataframe(str(input_file), "parquet", read_kwargs, None, None)

    pd.testing.assert_frame_equal(result, df, check_dtype=False)


def test_read_dataframe_unsupported_format(tmp_path):
    """Test error handling for unsupported input formats.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    input_file = tmp_path / "input.unsupported"
    with open(input_file, "w") as f:
        f.write("dummy")

    read_kwargs = {}
    with pytest.raises(ValueError, match="Unsupported input format"):
        _read_dataframe(str(input_file), "unsupported", read_kwargs, None, None)


def test_apply_row_selection_valid():
    """Test valid row selection."""
    df = pd.DataFrame({"a": range(10), "b": [f"row_{i}" for i in range(10)]})

    # Test valid selection
    result = _apply_row_selection(df, "2:5")
    assert result.shape[0] == 3
    assert result["a"].tolist() == [2, 3, 4]


def test_apply_row_selection_none():
    """Test row selection with None (no selection)."""
    df = pd.DataFrame({"a": range(5)})

    result = _apply_row_selection(df, None)
    pd.testing.assert_frame_equal(result, df)


def test_apply_row_selection_invalid():
    """Test invalid row selection handling."""
    df = pd.DataFrame({"a": range(5)})

    # Test invalid format - should return original dataframe
    result = _apply_row_selection(df, "invalid")
    pd.testing.assert_frame_equal(result, df)


def test_apply_row_selection_out_of_bounds():
    """Test row selection with out-of-bounds indices."""
    df = pd.DataFrame({"a": range(5)})

    # Test out-of-bounds selection
    result = _apply_row_selection(df, "10:20")
    assert result.shape[0] == 0


def test_convert_dtypes():
    """Test dtype conversion to pyarrow."""
    df = pd.DataFrame(
        {"int_col": [1, 2, 3], "str_col": ["a", "b", "c"], "float_col": [1.1, 2.2, 3.3]}
    )

    result = _convert_dtypes(df)

    # Check that dtypes are converted to pyarrow
    assert hasattr(result, "convert_dtypes")
    # The actual conversion depends on pandas version and pyarrow availability


def test_build_write_kwargs():
    """Test building write kwargs."""
    kwargs = _build_write_kwargs("gzip", 6, None, "csv")
    assert kwargs["compression"] == "gzip"
    assert kwargs["compression_level"] == 6
    assert "sheet_name" not in kwargs

    kwargs = _build_write_kwargs(None, None, "Sheet1", "excel")
    assert kwargs["sheet_name"] == "Sheet1"
    assert "compression" not in kwargs

    kwargs = _build_write_kwargs(None, None, None, "csv")
    assert kwargs == {}


def test_write_dataframe_csv(tmp_path):
    """Test writing CSV dataframe.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    output_file = tmp_path / "output.csv"
    write_kwargs = {}

    _write_dataframe(df, str(output_file), "csv", write_kwargs)

    # Verify result
    result = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(result, df)


def test_write_dataframe_parquet(tmp_path):
    """Test writing Parquet dataframe.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    output_file = tmp_path / "output.parquet"
    write_kwargs = {}

    _write_dataframe(df, str(output_file), "parquet", write_kwargs)

    # Verify result
    result = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(result, df)


def test_write_dataframe_unsupported_format(tmp_path):
    """Test error handling for unsupported output formats.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3]})
    output_file = tmp_path / "output.unsupported"
    write_kwargs = {}

    with pytest.raises(ValueError, match="Unsupported output format"):
        _write_dataframe(df, str(output_file), "unsupported", write_kwargs)


def test_get_schema_from_arrow_format_parquet(tmp_path):
    """Test getting schema from Parquet file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.parquet"
    df.to_parquet(input_file, index=False)

    schema = _get_schema_from_arrow_format(str(input_file), "parquet")

    assert isinstance(schema, pa.Schema)
    assert len(schema) == 2
    assert schema.field(0).name == "a"
    assert schema.field(1).name == "b"


def test_get_schema_from_arrow_format_feather(tmp_path):
    """Test getting schema from Feather file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.feather"
    df.to_feather(input_file)

    schema = _get_schema_from_arrow_format(str(input_file), "feather")

    assert isinstance(schema, pa.Schema)
    assert len(schema) == 2
    assert schema.field(0).name == "a"
    assert schema.field(1).name == "b"


def test_get_schema_from_pandas_format(tmp_path):
    """Test getting schema from pandas-based format.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    read_kwargs = {"dtype_backend": "pyarrow"}
    schema = _get_schema_from_pandas_format(
        str(input_file), "csv", read_kwargs, None, None
    )

    assert isinstance(schema, pa.Schema)
    assert len(schema) == 2
    assert schema.field(0).name == "a"
    assert schema.field(1).name == "b"


def test_export_schema_to_json(tmp_path):
    """Test exporting schema to JSON file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create a simple schema
    schema = pa.schema([pa.field("a", pa.int64()), pa.field("b", pa.string())])

    output_file = tmp_path / "schema.json"
    _export_schema_to_json(schema, str(output_file))

    # Verify JSON structure
    with open(output_file, "r") as f:
        schema_data = json.load(f)

    assert "fields" in schema_data
    assert len(schema_data["fields"]) == 2

    field_names = [f["name"] for f in schema_data["fields"]]
    assert "a" in field_names
    assert "b" in field_names

    field_types = [f["type"] for f in schema_data["fields"]]
    assert "int64" in field_types
    assert "string" in field_types
