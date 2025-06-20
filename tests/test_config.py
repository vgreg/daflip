"""
Tests for configuration management.

This module contains tests for the configuration loading and management
functionality in the daflip package.
"""

import os
from unittest.mock import patch

from src.daflip.config import get_config


def test_get_config_default():
    """Test default configuration values.

    This test verifies that the get_config function returns the expected
    default values when no environment variables are set.
    """
    with patch.dict(os.environ, {}, clear=True):
        config = get_config()

        assert isinstance(config, dict)
        assert "LOG_LEVEL" in config
        assert config["LOG_LEVEL"] == "INFO"


def test_get_config_with_env_vars():
    """Test configuration with environment variables.

    This test verifies that environment variables are properly loaded
    and override default values.
    """
    with patch.dict(os.environ, {"DAFLIP_LOG_LEVEL": "DEBUG"}, clear=True):
        config = get_config()

        assert config["LOG_LEVEL"] == "DEBUG"


def test_get_config_with_dotenv(tmp_path):
    """Test configuration loading from .env file.

    This test verifies that configuration can be loaded from a .env file
    in the current directory.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create .env file
    env_content = "DAFLIP_LOG_LEVEL=WARNING\n"
    env_file = tmp_path / ".env"
    with open(env_file, "w") as f:
        f.write(env_content)

    # Mock os.getcwd to return our temp directory and ensure dotenv finds the file
    with patch("os.getcwd", return_value=str(tmp_path)):
        with patch.dict(os.environ, {}, clear=True):
            # Force reload of dotenv by patching the load_dotenv function
            with patch("src.daflip.config.load_dotenv") as mock_load_dotenv:
                # Configure the mock to actually load from our temp directory
                def side_effect():
                    import dotenv

                    dotenv.load_dotenv(env_file)

                mock_load_dotenv.side_effect = side_effect

                config = get_config()
                assert config["LOG_LEVEL"] == "WARNING"


def test_get_config_env_override_dotenv(tmp_path):
    """Test that environment variables override .env file values.

    This test verifies that environment variables take precedence over
    values in the .env file.

    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    # Create .env file with one value
    env_content = "DAFLIP_LOG_LEVEL=WARNING\n"
    env_file = tmp_path / ".env"
    with open(env_file, "w") as f:
        f.write(env_content)

    # Set environment variable with different value
    with patch("os.getcwd", return_value=str(tmp_path)):
        with patch.dict(os.environ, {"DAFLIP_LOG_LEVEL": "ERROR"}, clear=True):
            config = get_config()

            # Environment variable should override .env file
            assert config["LOG_LEVEL"] == "ERROR"


def test_get_config_missing_env_var():
    """Test configuration with missing environment variables.

    This test verifies that the function handles missing environment
    variables gracefully by using default values.
    """
    with patch.dict(os.environ, {}, clear=True):
        config = get_config()

        # Should use default value
        assert config["LOG_LEVEL"] == "INFO"


def test_get_config_empty_env_var():
    """Test configuration with empty environment variables.

    This test verifies that empty environment variables are handled
    correctly and default values are used.
    """
    with patch.dict(os.environ, {"DAFLIP_LOG_LEVEL": ""}, clear=True):
        config = get_config()

        # Should use default value when env var is empty
        assert config["LOG_LEVEL"] == "INFO"


def test_get_config_structure():
    """Test that configuration has the expected structure.

    This test verifies that the configuration dictionary has the
    expected keys and structure.
    """
    config = get_config()

    # Check structure
    assert isinstance(config, dict)
    assert "LOG_LEVEL" in config
    assert isinstance(config["LOG_LEVEL"], str)

    # Check that LOG_LEVEL has a valid value
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    assert config["LOG_LEVEL"] in valid_levels


def test_get_config_immutable():
    """Test that configuration is not affected by external changes.

    This test verifies that modifying the returned configuration
    doesn't affect subsequent calls to get_config.
    """
    config1 = get_config()
    original_level = config1["LOG_LEVEL"]

    # Modify the returned config
    config1["LOG_LEVEL"] = "MODIFIED"

    # Get config again
    config2 = get_config()

    # Second call should return original value
    assert config2["LOG_LEVEL"] == original_level
    assert config1["LOG_LEVEL"] == "MODIFIED"  # First config was modified


def test_get_config_multiple_calls():
    """Test that multiple calls to get_config return consistent results.

    This test verifies that get_config is deterministic and returns
    the same configuration on multiple calls.
    """
    config1 = get_config()
    config2 = get_config()

    assert config1 == config2
    assert config1["LOG_LEVEL"] == config2["LOG_LEVEL"]


def test_get_config_with_custom_env_vars():
    """Test configuration with custom environment variables.

    This test verifies that the function can handle additional
    environment variables that might be added in the future.
    """
    with patch.dict(
        os.environ,
        {"DAFLIP_LOG_LEVEL": "DEBUG", "DAFLIP_CUSTOM_VAR": "custom_value"},
        clear=True,
    ):
        config = get_config()

        # Should include the standard config
        assert config["LOG_LEVEL"] == "DEBUG"

        # Custom variables should not be included in current implementation
        # This test documents the current behavior
        assert "DAFLIP_CUSTOM_VAR" not in config
