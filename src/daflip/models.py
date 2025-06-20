"""
Data models and enums for daflip.

This module defines the supported input and output formats as enums,
providing a centralized location for format definitions and validation.
"""

from enum import Enum


class SupportedInputFormat(Enum):
    """Supported input file formats for data conversion.

    This enum defines all the file formats that can be read by the daflip package.
    Each enum value corresponds to the file extension or format identifier.

    Attributes:
        CSV: Comma-separated values format
        TSV: Tab-separated values format
        PSV: Pipe-separated values format
        FIXED: Fixed-width text format (not yet implemented)
        PARQUET: Apache Parquet columnar format
        ORC: Apache ORC columnar format
        FEATHER: Apache Arrow Feather format
        SAS: SAS7BDAT binary format
        STATA: Stata binary format
        SPSS: SPSS binary format
        EXCEL: Microsoft Excel format (.xlsx, .xls)
        HTML: HTML table format
    """

    CSV = "csv"
    TSV = "tsv"
    PSV = "psv"
    FIXED = "fixed"
    PARQUET = "parquet"
    ORC = "orc"
    FEATHER = "feather"
    SAS = "sas7bdat"
    STATA = "stata"
    SPSS = "spss"
    EXCEL = "excel"
    HTML = "html"


class SupportedOutputFormat(Enum):
    """Supported output file formats for data conversion.

    This enum defines all the file formats that can be written by the daflip package.
    Note that not all input formats are supported as output formats.

    Attributes:
        CSV: Comma-separated values format
        PARQUET: Apache Parquet columnar format
        ORC: Apache ORC columnar format
        FEATHER: Apache Arrow Feather format
        EXCEL: Microsoft Excel format (.xlsx)
        STATA: Stata binary format
    """

    CSV = "csv"
    PARQUET = "parquet"
    ORC = "orc"
    FEATHER = "feather"
    EXCEL = "excel"
    STATA = "stata"
