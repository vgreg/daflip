# Releasing Daflip

Daflip uses automated releases with GitHub Actions. There are two release workflows available:

## Release Workflows

### 1. Simple Release (release.yml)
Automatically increments the **minor version** on every merge to main.

**When it runs:**
- Every push to the `main` branch
- Manual trigger via GitHub Actions

**What it does:**
- Runs tests and linting
- Increments minor version (e.g., 0.1.0 → 0.2.0)
- Updates `pyproject.toml` and `src/daflip/__init__.py`
- Creates a GitHub release
- Tags the release

### 2. Semantic Release (semantic-release.yml) ⭐ **Recommended**
Intelligently determines version bump based on commit messages and **automatically generates changelogs**.

**Version Bump Rules:**
- **Major** (1.0.0 → 2.0.0): Breaking changes
  - Commit messages with `BREAKING CHANGE` or `!:`
- **Minor** (0.1.0 → 0.2.0): New features
  - Commit messages starting with `feat:`
- **Patch** (0.1.0 → 0.1.1): Bug fixes and other changes
  - All other commits

**Example commit messages:**
```bash
feat: add support for new file format          # Minor bump
fix: handle missing input file gracefully      # Patch bump
feat!: remove deprecated API                   # Major bump
BREAKING CHANGE: change default behavior       # Major bump
```

## Automated Changelog Generation

The semantic release workflow automatically generates comprehensive changelogs from GitHub issues and pull requests.

### What Gets Included

**Pull Requests:**
- ✨ New Features
- 🐛 Bug Fixes
- 💥 Breaking Changes
- ⚡ Performance Improvements
- 📚 Documentation
- 🔒 Security Updates
- 🔧 Other Changes

**Issues:**
- Bug reports and feature requests
- Documentation requests
- Other user feedback

### Categorization

The changelog generator automatically categorizes changes based on:

1. **GitHub Labels** (highest priority):
   - `bug`, `fix` → Bug Fixes
   - `enhancement`, `feature`, `new-feature` → New Features
   - `breaking-change`, `breaking` → Breaking Changes
   - `documentation`, `docs` → Documentation
   - `performance`, `optimization` → Performance
   - `security` → Security

2. **Title Analysis** (fallback):
   - Keywords in titles are analyzed for categorization
   - "fix", "bug", "error" → Bug Fixes
   - "add", "new", "feature" → New Features
   - "doc", "readme" → Documentation
   - etc.

### Changelog Output

The generated changelog includes:
- **Categorized sections** with emojis for easy scanning
- **Links to issues and PRs** for detailed information
- **Contributor attribution** for pull requests
- **Statistics** (total PRs, issues, changes)
- **Release date** and version information

### Example Changelog

```markdown
# Changelog for v0.2.0

*Released on 2024-01-15*

## ✨ New Features

- ✨ **Add support for Excel .xls files** ([#45](https://github.com/vincentgregoire/daflip/pull/45)) by @contributor
- ✨ **Implement chunked processing for large files** ([#42](https://github.com/vincentgregoire/daflip/pull/42))

## 🐛 Bug Fixes

- 🐛 **Fix CSV parsing with custom separators** ([#38](https://github.com/vincentgregoire/daflip/pull/38))

## 📚 Documentation

- 📚 **Add comprehensive API documentation** ([#40](https://github.com/vincentgregoire/daflip/pull/40))

## 📊 Statistics

- **Pull Requests**: 5
- **Issues**: 3
- **Total Changes**: 8
```

## Setup

### 1. Choose Your Workflow

**For simple projects:** Use `release.yml`
- Rename `semantic-release.yml` to `semantic-release.yml.disabled`

**For semantic versioning with changelogs:** Use `semantic-release.yml` ⭐
- Rename `release.yml` to `release.yml.disabled`

### 2. Configure Permissions

Ensure your repository has the necessary permissions:
- Go to **Settings > Actions > General**
- Under "Workflow permissions", select "Read and write permissions"
- Check "Allow GitHub Actions to create and approve pull requests"

### 3. Initial Setup

For the first release:
```bash
# Create initial tag
git tag v0.1.0
git push origin v0.1.0
```

## Manual Changelog Generation

You can generate changelogs manually:

1. **Via GitHub Actions:**
   - Go to **Actions** tab
   - Select "Generate Changelog" workflow
   - Click **Run workflow**
   - Enter the version number
   - Click **Run workflow**

2. **Locally (for testing):**
   ```bash
   # Install dependencies
   pip install PyGithub

   # Generate changelog
   python .github/scripts/generate_changelog.py \
     --version 0.2.0 \
     --repo vincentgregoire/daflip \
     --output docs/changelog.md
   ```

## Release Process

1. **Trigger**: Push to main or manual trigger
2. **Validation**: Tests and linting run
3. **Version Bump**: Version is incremented automatically
4. **Files Updated**:
   - `pyproject.toml`
   - `src/daflip/__init__.py`
5. **Changelog Generated**: Automatic changelog from issues/PRs
6. **Release Created**: GitHub release with tag and changelog
7. **Commit**: Version bump and changelog committed back to main

## Customization

### Modify Changelog Categories

Edit `.github/scripts/generate_changelog.py` to customize categorization:

```python
def categorize_pr(pr) -> str:
    """Categorize a pull request based on labels and title."""
    labels = [label.name.lower() for label in pr.labels]

    # Add custom labels
    if any(label in labels for label in ['your-custom-label']):
        return 'your-category'

    # ... rest of function
```

### Custom Release Notes

Modify the release body in the workflow:

```yaml
body: |
  ## What's Changed

  Custom release notes here...

  ### Features
  - New feature 1
  - New feature 2

  ### Fixes
  - Bug fix 1
  - Bug fix 2
```

### Skip Release

To skip a release, include `[skip release]` in your commit message:

```bash
git commit -m "docs: update README [skip release]"
```

## Best Practices

### For Better Changelogs

1. **Use descriptive PR titles** that explain what changed
2. **Add appropriate labels** to issues and PRs
3. **Use conventional commit messages** for automatic categorization
4. **Link issues in PR descriptions** using `Fixes #123` or `Closes #123`
5. **Review generated changelogs** and adjust if needed

### Commit Message Examples

```bash
# Good - will be categorized as feature
feat: add support for Excel .xls files

# Good - will be categorized as bug fix
fix: handle missing input file gracefully

# Good - will trigger major version bump
feat!: remove deprecated API

# Good - will be categorized as documentation
docs: update installation guide

# Avoid - generic title, harder to categorize
update code
```

## Troubleshooting

### Changelog Issues

1. **Empty changelog**: Check if there are closed issues/merged PRs since last release
2. **Wrong categorization**: Add appropriate labels to issues/PRs
3. **Missing entries**: Ensure issues/PRs are properly closed/merged
4. **Permission errors**: Check GitHub token permissions

### Workflow Fails

1. **Check permissions**: Ensure the workflow has write permissions
2. **Check tests**: Make sure all tests pass locally
3. **Check linting**: Run `ruff check .` locally
4. **Check version format**: Ensure version in `pyproject.toml` is valid

### Version Not Updating

1. **Check file paths**: Ensure `pyproject.toml` and `__init__.py` exist
2. **Check version format**: Version should be in quotes: `"0.1.0"`
3. **Check permissions**: Workflow needs write access to repository

### Release Not Created

1. **Check GitHub token**: Ensure `GITHUB_TOKEN` is available
2. **Check branch**: Workflow only runs on `main` branch
3. **Check conditions**: Ensure `if: github.ref == 'refs/heads/main'` is met
