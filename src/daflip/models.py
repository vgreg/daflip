"""
Data models and enums for daflip.
"""

from enum import Enum


class SupportedInputFormat(Enum):
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
    CSV = "csv"
    PARQUET = "parquet"
    ORC = "orc"
    FEATHER = "feather"
    EXCEL = "excel"
    STATA = "stata"
