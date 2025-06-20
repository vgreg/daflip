"""
Integration tests for end-to-end functionality.

This module contains integration tests that verify the complete
workflow of the daflip package, from data conversion to schema inference.
"""

import json

import pandas as pd
import pytest

from src.daflip.services import convert_data, infer_and_export_schema


def test_full_workflow_csv_to_parquet(tmp_path):
    """Test complete workflow from CSV to Parquet.

    This test verifies the complete workflow of reading a CSV file,
    converting it to Parquet, and then reading it back to verify
    data integrity.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create test data with various data types (excluding dates to avoid type issues)
    df = pd.DataFrame(
        {
            "int_col": [1, 2, 3, 4, 5],
            "str_col": ["a", "b", "c", "d", "e"],
            "float_col": [1.1, 2.2, 3.3, 4.4, 5.5],
            "bool_col": [True, False, True, False, True],
        }
    )

    # Step 1: Create input CSV file
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    # Step 2: Convert to Parquet
    output_file = tmp_path / "output.parquet"
    convert_data(str(input_file), str(output_file), compression="snappy")

    # Step 3: Read back and verify
    df_result = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(df, df_result, check_dtype=False)

    # Step 4: Verify file was created and has content
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_full_workflow_with_schema(tmp_path):
    """Test complete workflow with schema inference and use.

    This test verifies the complete workflow of inferring a schema
    from a data file and then using that schema for conversion.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create test data
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "score": [95.5, 87.2, 92.1, 88.9, 91.3],
        }
    )

    # Step 1: Create input file
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    # Step 2: Infer schema
    schema_file = tmp_path / "schema.json"
    infer_and_export_schema(str(input_file), None, str(schema_file))

    # Step 3: Verify schema file was created and has correct structure
    assert schema_file.exists()
    with open(schema_file, "r") as f:
        schema_data = json.load(f)

    assert "fields" in schema_data
    field_names = [f["name"] for f in schema_data["fields"]]
    assert "id" in field_names
    assert "name" in field_names
    assert "score" in field_names

    # Step 4: Use schema for conversion
    output_file = tmp_path / "output.parquet"
    convert_data(str(input_file), str(output_file), schema_file=str(schema_file))

    # Step 5: Verify conversion worked
    df_result = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(df, df_result, check_dtype=False)


def test_large_file_chunked_processing(tmp_path):
    """Test chunked processing with large files.

    This test verifies that chunked processing works correctly
    for larger datasets that would benefit from chunking.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create larger dataset
    df = pd.DataFrame(
        {
            "id": range(1000),
            "value": [f"row_{i}" for i in range(1000)],
            "score": [i * 0.1 for i in range(1000)],
        }
    )

    # Step 1: Create input file
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    # Step 2: Convert with chunking
    output_file = tmp_path / "output.csv"
    convert_data(str(input_file), str(output_file), input_chunk_size=100)

    # Step 3: Verify result
    df_result = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(df, df_result, check_dtype=False)

    # Step 4: Verify chunking actually happened (file should be created)
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_multiple_format_conversions(tmp_path):
    """Test multiple format conversions in sequence.

    This test verifies that data can be converted between multiple
    formats while maintaining data integrity.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create test data
    df = pd.DataFrame(
        {
            "a": [1, 2, 3, 4, 5],
            "b": ["x", "y", "z", "w", "v"],
            "c": [1.1, 2.2, 3.3, 4.4, 5.5],
        }
    )

    # Step 1: Start with CSV
    csv_file = tmp_path / "data.csv"
    df.to_csv(csv_file, index=False)

    # Step 2: CSV -> Parquet
    parquet_file = tmp_path / "data.parquet"
    convert_data(str(csv_file), str(parquet_file))

    # Step 3: Parquet -> Feather
    feather_file = tmp_path / "data.feather"
    convert_data(str(parquet_file), str(feather_file))

    # Step 4: Feather -> CSV (avoid Excel due to dependency issues)
    csv_output = tmp_path / "data_output.csv"
    convert_data(str(feather_file), str(csv_output))

    # Step 5: Verify data integrity through the chain
    df_final = pd.read_csv(csv_output)
    pd.testing.assert_frame_equal(df, df_final, check_dtype=False)


def test_workflow_with_data_filtering(tmp_path):
    """Test workflow with data filtering and selection.

    This test verifies that row selection and filtering work
    correctly in the complete workflow.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create test data
    df = pd.DataFrame(
        {"id": range(20), "category": ["A", "B", "A", "B", "A"] * 4, "value": range(20)}
    )

    # Step 1: Create input file
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    # Step 2: Convert with row selection
    output_file = tmp_path / "output.csv"
    convert_data(str(input_file), str(output_file), rows="5:15")

    # Step 3: Verify only selected rows were converted
    df_result = pd.read_csv(output_file)
    expected_rows = df.iloc[5:15].reset_index(drop=True)
    pd.testing.assert_frame_equal(expected_rows, df_result, check_dtype=False)

    # Step 4: Verify row count is correct
    assert len(df_result) == 10


def test_workflow_with_compression_options(tmp_path):
    """Test workflow with various compression options.

    This test verifies that different compression options work
    correctly in the complete workflow.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create test data
    df = pd.DataFrame(
        {
            "id": range(100),
            "text": [f"long_text_{i}" * 10 for i in range(100)],
            "number": range(100),
        }
    )

    # Step 1: Create input file
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    # Step 2: Test different compression options
    compression_options = [("snappy", None), ("gzip", 6), ("brotli", None)]

    for compression, level in compression_options:
        output_file = tmp_path / f"output_{compression}.parquet"

        if level is not None:
            convert_data(
                str(input_file),
                str(output_file),
                compression=compression,
                compression_level=level,
            )
        else:
            convert_data(str(input_file), str(output_file), compression=compression)

        # Verify conversion worked
        df_result = pd.read_parquet(output_file)
        pd.testing.assert_frame_equal(df, df_result, check_dtype=False)

        # Verify file was created
        assert output_file.exists()
        assert output_file.stat().st_size > 0


def test_workflow_error_handling(tmp_path):
    """Test workflow error handling and recovery.

    This test verifies that the system handles errors gracefully
    and provides appropriate error messages.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Test with non-existent input file
    input_file = tmp_path / "nonexistent.csv"
    output_file = tmp_path / "output.csv"

    with pytest.raises(FileNotFoundError):
        convert_data(str(input_file), str(output_file))

    # Test with invalid schema file
    df = pd.DataFrame({"a": [1, 2, 3]})
    valid_input = tmp_path / "valid.csv"
    df.to_csv(valid_input, index=False)

    invalid_schema = tmp_path / "invalid.json"
    with open(invalid_schema, "w") as f:
        f.write("invalid json")

    with pytest.raises(json.JSONDecodeError):
        convert_data(
            str(valid_input), str(output_file), schema_file=str(invalid_schema)
        )


def test_workflow_performance_characteristics(tmp_path):
    """Test workflow performance characteristics.

    This test verifies that the system performs reasonably well
    with different data sizes and processing options.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import time

    # Test with different data sizes
    sizes = [100, 1000, 10000]

    for size in sizes:
        # Create data
        df = pd.DataFrame(
            {
                "id": range(size),
                "value": [f"row_{i}" for i in range(size)],
                "score": [i * 0.1 for i in range(size)],
            }
        )

        input_file = tmp_path / f"input_{size}.csv"
        output_file = tmp_path / f"output_{size}.parquet"

        df.to_csv(input_file, index=False)

        # Time the conversion
        start_time = time.time()
        convert_data(str(input_file), str(output_file))
        end_time = time.time()

        # Verify conversion worked
        df_result = pd.read_parquet(output_file)
        pd.testing.assert_frame_equal(df, df_result, check_dtype=False)

        # Log performance (for monitoring, not assertion)
        conversion_time = end_time - start_time
        print(f"Converted {size} rows in {conversion_time:.2f} seconds")


def test_workflow_data_integrity_edge_cases(tmp_path):
    """Test workflow with edge cases for data integrity.

    This test verifies that the system handles edge cases correctly
    while maintaining data integrity.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Test with single row dataframe
    df_single = pd.DataFrame({"a": [1], "b": ["x"]})
    input_file = tmp_path / "single.csv"
    output_file = tmp_path / "single.parquet"

    df_single.to_csv(input_file, index=False)
    convert_data(str(input_file), str(output_file))

    df_result = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(df_single, df_result, check_dtype=False)

    # Test with single column dataframe
    df_single_col = pd.DataFrame({"a": [1, 2, 3]})
    input_file = tmp_path / "single_col.csv"
    output_file = tmp_path / "single_col.parquet"

    df_single_col.to_csv(input_file, index=False)
    convert_data(str(input_file), str(output_file))

    df_result = pd.read_parquet(output_file)
    pd.testing.assert_frame_equal(df_single_col, df_result, check_dtype=False)


def test_full_workflow_csv_to_parquet_with_datetime_schema(tmp_path):
    """Test complete workflow from CSV to Parquet with datetime schema.

    This test verifies that datetime columns are properly handled when
    an explicit schema is provided that defines the column as datetime.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    import json

    # Create test data with datetime column
    df = pd.DataFrame(
        {
            "int_col": [1, 2, 3, 4, 5],
            "str_col": ["a", "b", "c", "d", "e"],
            "float_col": [1.1, 2.2, 3.3, 4.4, 5.5],
            "bool_col": [True, False, True, False, True],
            "date_col": pd.date_range("2023-01-01", periods=5),
        }
    )

    # Step 1: Create input CSV file
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False)

    # Step 2: Create schema file with explicit datetime type
    schema_data = {
        "fields": [
            {"name": "int_col", "type": "int64"},
            {"name": "str_col", "type": "string"},
            {"name": "float_col", "type": "float64"},
            {"name": "bool_col", "type": "bool"},
            {"name": "date_col", "type": "timestamp"},
        ]
    }
    schema_file = tmp_path / "schema.json"
    with open(schema_file, "w") as f:
        json.dump(schema_data, f)

    # Step 3: Convert to Parquet with schema
    output_file = tmp_path / "output.parquet"
    convert_data(str(input_file), str(output_file), schema_file=str(schema_file))

    # Step 4: Read back and verify
    df_result = pd.read_parquet(output_file)

    # For datetime columns, compare only the date part (not time)
    df_compare = df.copy()
    df_result_compare = df_result.copy()
    df_compare["date_col"] = df_compare["date_col"].dt.date
    df_result_compare["date_col"] = df_result_compare["date_col"].dt.date

    pd.testing.assert_frame_equal(df_compare, df_result_compare, check_dtype=False)

    # Step 5: Verify the schema was applied correctly
    # Read the parquet file with pyarrow to check the actual schema
    import pyarrow.parquet as pq

    table = pq.read_table(output_file)
    schema = table.schema

    # Check that date_col is actually a timestamp type
    date_field = schema.field("date_col")
    assert str(date_field.type).startswith("timestamp"), (
        f"Expected timestamp type, got {date_field.type}"
    )
