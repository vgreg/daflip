"""
Tests for utility functions.

This module contains tests for the utility functions in the daflip package,
including format inference and other helper functions.
"""

from src.daflip.utils import infer_format


def test_infer_format():
    """Test the format inference functionality.

    This test verifies that the infer_format function correctly:
    - Extracts format from file extensions
    - Handles format overrides
    - Returns lowercase format strings

    Test cases:
    - CSV file extension detection
    - TSV file extension detection
    - Format override functionality
    """
    from src.daflip.utils import infer_format

    assert infer_format("file.csv") == "csv"
    assert infer_format("file.tsv") == "tsv"
    assert infer_format("file.txt", override="fixed") == "fixed"


def test_infer_format_edge_cases():
    """Test format inference with edge cases.

    This test covers various edge cases for format inference:
    - Files without extensions
    - Files with multiple dots
    - Uppercase extensions
    - Empty overrides
    - Special characters in filenames
    """
    # Test files without extensions
    assert infer_format("file", override="csv") == "csv"

    # Test files with multiple dots
    assert infer_format("file.data.csv") == "csv"
    assert infer_format("archive.tar.gz", override="csv") == "csv"

    # Test uppercase extensions
    assert infer_format("file.CSV") == "csv"
    assert infer_format("file.PARQUET") == "parquet"
    assert infer_format("file.XLSX") == "xlsx"

    # Test empty override
    assert infer_format("file.csv", override="") == "csv"

    # Test special characters in filenames
    assert infer_format("my-file.csv") == "csv"
    assert infer_format("file_with_underscores.tsv") == "tsv"
    assert infer_format("file with spaces.parquet") == "parquet"


def test_infer_format_override_precedence():
    """Test that override takes precedence over file extension.

    This test verifies that when an override is provided, it takes
    precedence over the file extension, regardless of the extension.
    """
    # Override should take precedence
    assert infer_format("file.csv", override="parquet") == "parquet"
    assert infer_format("file.parquet", override="csv") == "csv"
    assert infer_format("file.txt", override="excel") == "excel"
    assert infer_format("file.unknown", override="stata") == "stata"


def test_infer_format_case_insensitive():
    """Test that format inference is case insensitive.

    This test verifies that both file extensions and overrides
    are handled case-insensitively.
    """
    # File extensions should be case insensitive
    assert infer_format("file.CSV") == "csv"
    assert infer_format("file.Csv") == "csv"
    assert infer_format("file.csv") == "csv"

    # Overrides should be case insensitive
    assert infer_format("file.txt", override="CSV") == "csv"
    assert infer_format("file.txt", override="Csv") == "csv"
    assert infer_format("file.txt", override="csv") == "csv"


def test_infer_format_common_extensions():
    """Test format inference for all supported extensions.

    This test verifies that all supported file extensions are
    correctly identified.
    """
    # Test all supported input formats
    assert infer_format("file.csv") == "csv"
    assert infer_format("file.tsv") == "tsv"
    assert infer_format("file.psv") == "psv"
    assert infer_format("file.parquet") == "parquet"
    assert infer_format("file.orc") == "orc"
    assert infer_format("file.feather") == "feather"
    assert infer_format("file.sas7bdat") == "sas7bdat"
    assert infer_format("file.dta") == "dta"
    assert infer_format("file.sav") == "sav"
    assert infer_format("file.xlsx") == "xlsx"
    assert infer_format("file.xls") == "xls"
    assert infer_format("file.html") == "html"
    assert infer_format("file.htm") == "htm"


def test_infer_format_unknown_extensions():
    """Test format inference for unknown extensions.

    This test verifies that unknown extensions are handled correctly
    and return the extension as-is.
    """
    # Unknown extensions should return the extension
    assert infer_format("file.unknown") == "unknown"
    assert infer_format("file.custom") == "custom"
    assert infer_format("file.data") == "data"

    # But override should still work
    assert infer_format("file.unknown", override="csv") == "csv"


def test_infer_format_no_extension():
    """Test format inference for files without extensions.

    This test verifies that files without extensions are handled
    correctly, returning empty string when no override is provided.
    """
    # Files without extensions should return empty string
    assert infer_format("file") == ""
    assert infer_format("data") == ""
    assert infer_format("input") == ""

    # But override should work
    assert infer_format("file", override="csv") == "csv"
    assert infer_format("data", override="parquet") == "parquet"


def test_infer_format_path_with_directories():
    """Test format inference with file paths containing directories.

    This test verifies that format inference works correctly with
    full file paths containing directories.
    """
    # Paths with directories should work
    assert infer_format("/path/to/file.csv") == "csv"
    assert infer_format("relative/path/data.parquet") == "parquet"
    assert infer_format("C:\\Windows\\Path\\file.xlsx") == "xlsx"

    # Override should still work with paths
    assert infer_format("/path/to/file.txt", override="csv") == "csv"


def test_infer_format_hidden_files():
    """Test format inference with hidden files.

    This test verifies that format inference works correctly with
    hidden files (files starting with a dot).
    """
    # Hidden files should work
    assert infer_format(".hidden.csv") == "csv"
    assert infer_format(".config.parquet") == "parquet"

    # Override should work with hidden files
    assert infer_format(".hidden.txt", override="csv") == "csv"


def test_infer_format_return_type():
    """Test that infer_format returns the correct type.

    This test verifies that the function always returns a string
    and that the return value is always lowercase.
    """
    # Should always return string
    assert isinstance(infer_format("file.csv"), str)
    assert isinstance(infer_format("file", override="csv"), str)
    assert isinstance(infer_format("file.unknown"), str)

    # Should always return lowercase
    assert infer_format("file.CSV") == "csv"
    assert infer_format("file.PARQUET") == "parquet"
    assert infer_format("file.txt", override="CSV") == "csv"
