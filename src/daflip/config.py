"""
Configuration management for daflip.
"""

import os

from dotenv import load_dotenv


def get_config() -> dict:
    """Load configuration from environment variables."""
    load_dotenv()
    return {
        # Add config keys as needed
        "LOG_LEVEL": os.getenv("DAFLIP_LOG_LEVEL", "INFO"),
    }
