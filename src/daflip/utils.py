"""
Utility functions for daflip.
"""

import os
from typing import Optional


def infer_format(file_path: str, override: Optional[str] = None) -> str:
    """Infer file format from extension or override."""
    if override:
        return override.lower()
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    return ext
