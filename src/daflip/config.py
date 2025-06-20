"""
Configuration management for daflip.

This module handles configuration loading from environment variables
and provides a centralized configuration interface for the daflip package.
"""

import os

from dotenv import load_dotenv


def get_config() -> dict:
    """Load configuration from environment variables.

    This function loads configuration settings from environment variables,
    with support for .env files. It provides default values for required
    configuration keys.

    Returns:
        dict: Configuration dictionary with loaded settings

    Environment Variables:
        DAFLIP_LOG_LEVEL: Logging level (default: "INFO")

    Example:
        >>> config = get_config()
        >>> print(config["LOG_LEVEL"])
        'INFO'
    """
    load_dotenv()

    # Get environment variables with proper handling of empty values
    log_level = os.getenv("DAFLIP_LOG_LEVEL")
    if not log_level or log_level.strip() == "":
        log_level = "INFO"

    return {
        # Add config keys as needed
        "LOG_LEVEL": log_level,
    }
