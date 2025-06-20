"""
Daflip - Data Format Conversion Tool

A Python package for converting data between different formats using pandas and pyarrow.
Supports both chunked and non-chunked processing for large datasets.

Main features:
- Convert between CSV, TSV, PSV, Parquet, ORC, Feather, Excel, Stata, SPSS, SAS, and HTML formats
- Chunked processing for large files
- Schema inference and export
- Row selection and filtering
- Compression support
- Command-line interface

Example usage:
    >>> from daflip.services import convert_data
    >>> convert_data("input.csv", "output.parquet", compression="snappy")
"""

__version__ = "0.1.2"
__author__ = "Daflip Team"
