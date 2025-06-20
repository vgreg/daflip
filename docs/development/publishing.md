# Publishing to PyPI

Daflip is automatically published to PyPI whenever a new release is created. This ensures that users can easily install the latest version using `pip` or `uv`.

## Automatic Publishing

### How It Works

1. **Release Creation**: When you merge to `main` with semantic commits, the semantic release workflow creates a new GitHub release
2. **PyPI Trigger**: The PyPI publish workflow is automatically triggered by the release
3. **Build & Test**: The package is built, tested, and linted
4. **Publish**: The package is published to PyPI with the new version

### Workflow Steps

1. **Tests & Linting**: Ensures code quality before publishing
2. **Build Package**: Creates distribution files using `python -m build`
3. **Publish to PyPI**: Uploads to the main PyPI repository
4. **Publish to TestPyPI** (optional): Also publishes to TestPyPI for testing

## Installation Methods

Once published, users can install Daflip using various methods:

### Basic Installation

```bash
# Using pip
pip install daflip

# Using uv
uv add daflip

# Using uvx (run without installing)
uvx daflip --help
```

### Using uvx (Recommended for One-off Use)

```bash
# Convert a file without installing
uvx daflip input.csv output.parquet

# With compression
uvx daflip input.csv output.parquet --compression snappy

# Show help
uvx daflip --help
```

## PyPI Setup

### 1. Create PyPI Account

1. Go to [PyPI](https://pypi.org/account/register/)
2. Create an account with a unique username
3. Verify your email address

### 2. Create API Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Click **Add API token**
3. Give it a name like "Daflip GitHub Actions"
4. Select **Entire account (all projects)**
5. Click **Create token**
6. **Copy the token** (you won't see it again!)

### 3. Add Token to GitHub Secrets

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `PYPI_API_TOKEN`
4. Value: Paste your PyPI token
5. Click **Add secret**

### 4. Optional: TestPyPI Setup

For testing before publishing to main PyPI:

1. Create account at [TestPyPI](https://test.pypi.org/account/register/)
2. Create API token (same process as PyPI)
3. Add as secret: `TEST_PYPI_API_TOKEN`

## Manual Publishing

### Local Testing

```bash
# Install build tools
uv add build twine

# Build package
uv build

# Check distribution
uv run twine check dist/*

# Upload to TestPyPI (for testing)
uv run twine upload --repository testpypi dist/*

# Upload to PyPI
uv run twine upload dist/*
```

### Using GitHub Actions Manually

1. Go to **Actions** tab
2. Select **Publish to PyPI**
3. Click **Run workflow**
4. Choose the release to publish from

## Package Configuration

### pyproject.toml Structure

The package is configured for optimal compatibility with all format support included by default:

```toml
[project]
name = "daflip"
version = "0.1.0"
description = "A CLI tool for converting data files between formats."
# ... other metadata

dependencies = [
    "openpyxl>=3.1.5",    # Excel support (.xlsx, .xls)
    "pandas>=2.3.0",      # Core data processing
    "pyarrow>=20.0.0",    # Parquet, Feather, ORC support
    "rich>=14.0.0",       # CLI interface
    "typer>=0.16.0",      # CLI framework
    "xlrd>=2.0.2",        # Excel .xls support
    "xlsxwriter>=3.2.5",  # Excel writing support
]

[project.scripts]
daflip = "daflip.cli:main"
```

### Key Features

- **All Formats Included**: No need for optional dependencies - all supported formats work out of the box
- **Type Hints**: Package includes `py.typed` for type support
- **CLI Entry Point**: `daflip` command available after installation
- **Comprehensive Metadata**: Proper classifiers, URLs, and descriptions

## Version Management

### Semantic Versioning

- **Major** (1.0.0): Breaking changes
- **Minor** (0.2.0): New features
- **Patch** (0.1.1): Bug fixes

### Automatic Version Bumping

The semantic release workflow automatically:
1. Analyzes commit messages
2. Determines version bump type
3. Updates `pyproject.toml` and `__init__.py`
4. Creates GitHub release
5. Triggers PyPI publish

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Check PyPI API token is correct
   - Ensure token has proper permissions
   - Verify token is added to GitHub secrets

2. **Package Already Exists**
   - The workflow uses `skip-existing: true`
   - This prevents errors if package already exists
   - Check PyPI for existing version

3. **Build Failures**
   - Check `pyproject.toml` syntax
   - Ensure all dependencies are listed
   - Verify package structure is correct

4. **Test Failures**
   - All tests must pass before publishing
   - Check test output in Actions tab
   - Fix failing tests locally first

### Debugging

```bash
# Test build locally
uv build

# Check package contents
tar -tzf dist/daflip-*.tar.gz

# Validate package
uv run twine check dist/*

# Test installation
pip install dist/daflip-*.whl
```

## Best Practices

### Before Publishing

1. **Test Locally**: Always test build and installation locally
2. **Update Documentation**: Ensure docs reflect new features
3. **Check Dependencies**: Verify all dependencies are correctly specified
4. **Test Installation**: Test with both pip and uv

### Release Process

1. **Feature Branch**: Develop features in branches
2. **Pull Request**: Create PR with semantic commit messages
3. **Code Review**: Ensure quality and tests pass
4. **Merge to Main**: Triggers automatic release and publish
5. **Verify**: Check PyPI and test installation

### Commit Messages

Use semantic commit messages for automatic versioning:

```bash
feat: add new file format support      # Minor version bump
fix: resolve parsing issue             # Patch version bump
feat!: remove deprecated API           # Major version bump
docs: update installation guide        # No version bump
```

## Monitoring

### PyPI Statistics

- Check [PyPI project page](https://pypi.org/project/daflip/)
- Monitor download statistics
- Review user feedback and issues

### GitHub Actions

- Monitor workflow runs in Actions tab
- Check for any failures or warnings
- Review release notes and changelog

## Security

### API Token Security

- **Never commit tokens** to version control
- **Use GitHub secrets** for all sensitive data
- **Rotate tokens** periodically
- **Use minimal permissions** when possible

### Package Security

- **Sign releases** (optional but recommended)
- **Use HTTPS** for all downloads
- **Verify dependencies** regularly
- **Monitor for vulnerabilities**
