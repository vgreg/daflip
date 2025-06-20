"""
Utility functions for daflip.

This module contains utility functions used throughout the daflip package,
including format inference and other helper functions.
"""

import os
from typing import Optional


def infer_format(file_path: str, override: Optional[str] = None) -> str:
    """Infer file format from file extension or use override.

    This function determines the file format either from the file extension
    or from an explicit override parameter. The override takes precedence
    if provided.

    Args:
        file_path: Path to the file (used to extract extension)
        override: Optional format override (e.g., "csv", "parquet")

    Returns:
        str: The inferred format in lowercase

    Example:
        >>> infer_format("data.csv")
        'csv'
        >>> infer_format("data.txt", override="csv")
        'csv'
        >>> infer_format("data.parquet")
        'parquet'
    """
    if override:
        return override.lower()
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    return ext
