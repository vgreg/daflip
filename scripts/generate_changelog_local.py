#!/usr/bin/env python3
"""
Local changelog generator for testing.

This script can be run locally to test changelog generation without needing
GitHub Actions.
"""

import os
import sys

# Add the parent directory to the path so we can import the main script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from generate_changelog import main

if __name__ == "__main__":
    # Set default values for local testing
    if len(sys.argv) == 1:
        sys.argv.extend(
            [
                "--version",
                "0.2.0",
                "--repo",
                "vincentgregoire/daflip",
                "--output",
                "docs/changelog.md",
            ]
        )

    main()
