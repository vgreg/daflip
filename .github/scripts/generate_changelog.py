#!/usr/bin/env python3
"""
Generate changelog from GitHub issues and pull requests.

This script analyzes GitHub issues and pull requests since the last minor version
and generates a comprehensive changelog.
"""

import argparse
import re
import sys
from datetime import datetime
from typing import Tuple

try:
    from github import Github
except ImportError:
    print("PyGithub is required. Install with: pip install PyGithub")
    sys.exit(1)


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into major, minor, patch components."""
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(map(int, match.groups()))


def get_previous_minor_version(major: int, minor: int) -> str:
    """Get the previous minor version tag."""
    if minor == 0:
        # If this is the first minor version, look for the last major version
        return f"v{major - 1}.0.0" if major > 0 else None
    return f"v{major}.{minor - 1}.0"


def categorize_issue(issue) -> str:
    """Categorize an issue based on labels and title."""
    labels = [label.name.lower() for label in issue.labels]

    # Check for specific labels first
    if any(label in labels for label in ["bug", "fix"]):
        return "bug"
    elif any(label in labels for label in ["enhancement", "feature", "new-feature"]):
        return "feature"
    elif any(label in labels for label in ["breaking-change", "breaking"]):
        return "breaking"
    elif any(label in labels for label in ["documentation", "docs"]):
        return "documentation"
    elif any(label in labels for label in ["performance", "optimization"]):
        return "performance"
    elif any(label in labels for label in ["security"]):
        return "security"

    # Fallback to title analysis
    title_lower = issue.title.lower()
    if any(word in title_lower for word in ["fix", "bug", "issue", "error", "crash"]):
        return "bug"
    elif any(
        word in title_lower
        for word in ["add", "new", "feature", "support", "implement"]
    ):
        return "feature"
    elif any(word in title_lower for word in ["doc", "readme", "guide"]):
        return "documentation"
    elif any(word in title_lower for word in ["performance", "speed", "optimize"]):
        return "performance"
    elif any(word in title_lower for word in ["security", "vulnerability"]):
        return "security"

    return "other"


def categorize_pr(pr) -> str:
    """Categorize a pull request based on labels and title."""
    labels = [label.name.lower() for label in pr.labels]

    # Check for specific labels first
    if any(label in labels for label in ["bug", "fix"]):
        return "bug"
    elif any(label in labels for label in ["enhancement", "feature", "new-feature"]):
        return "feature"
    elif any(label in labels for label in ["breaking-change", "breaking"]):
        return "breaking"
    elif any(label in labels for label in ["documentation", "docs"]):
        return "documentation"
    elif any(label in labels for label in ["performance", "optimization"]):
        return "performance"
    elif any(label in labels for label in ["security"]):
        return "security"

    # Fallback to title analysis
    title_lower = pr.title.lower()
    if any(word in title_lower for word in ["fix", "bug", "issue", "error", "crash"]):
        return "bug"
    elif any(
        word in title_lower
        for word in ["add", "new", "feature", "support", "implement"]
    ):
        return "feature"
    elif any(word in title_lower for word in ["doc", "readme", "guide"]):
        return "documentation"
    elif any(word in title_lower for word in ["performance", "speed", "optimize"]):
        return "performance"
    elif any(word in title_lower for word in ["security", "vulnerability"]):
        return "security"

    return "other"


def format_issue_entry(issue) -> str:
    """Format an issue entry for the changelog."""
    category = categorize_issue(issue)
    emoji = {
        "bug": "🐛",
        "feature": "✨",
        "breaking": "💥",
        "documentation": "📚",
        "performance": "⚡",
        "security": "🔒",
        "other": "🔧",
    }.get(category, "🔧")

    return f"- {emoji} **{issue.title}** ([#{issue.number}]({issue.html_url}))"


def format_pr_entry(pr) -> str:
    """Format a pull request entry for the changelog."""
    category = categorize_pr(pr)
    emoji = {
        "bug": "🐛",
        "feature": "✨",
        "breaking": "💥",
        "documentation": "📚",
        "performance": "⚡",
        "security": "🔒",
        "other": "🔧",
    }.get(category, "🔧")

    # Add contributor info
    contributor = f"by @{pr.user.login}" if pr.user else ""

    return f"- {emoji} **{pr.title}** ([#{pr.number}]({pr.html_url})) {contributor}"


def generate_changelog(
    github_token: str, repo_name: str, version: str, output_file: str
):
    """Generate changelog for the specified version."""
    g = Github(github_token)
    repo = g.get_repo(repo_name)

    # Parse version
    major, minor, patch = parse_version(version)
    current_tag = f"v{version}" if not version.startswith("v") else version

    # Get previous minor version
    previous_tag = get_previous_minor_version(major, minor)

    print(f"Generating changelog for {current_tag}")
    if previous_tag:
        print(f"Since {previous_tag}")
    else:
        print("Since repository creation")

    # Get issues and PRs since the previous version
    since_date = None
    if previous_tag:
        try:
            previous_release = repo.get_release(previous_tag)
            since_date = previous_release.created_at
        except Exception:
            # If release doesn't exist, try to find the tag
            try:
                tag = repo.get_git_ref(f"tags/{previous_tag}")
                commit = repo.get_commit(tag.object.sha)
                since_date = commit.commit.author.date
            except Exception as e:
                print(f"Error: {e}")
                print(f"Warning: Could not find {previous_tag}, using all issues/PRs")

    # Collect issues and PRs
    issues = []
    pull_requests = []

    # Get issues
    query = f"repo:{repo_name} is:issue is:closed"
    if since_date:
        query += f" closed:>={since_date.isoformat()}"

    for issue in g.search_issues(query=query, sort="created", order="desc"):
        if issue.pull_request:  # Skip PRs in issue search
            continue
        issues.append(issue)

    # Get pull requests
    query = f"repo:{repo_name} is:pr is:merged"
    if since_date:
        query += f" merged:>={since_date.isoformat()}"

    for pr in g.search_issues(query=query, sort="created", order="desc"):
        pull_requests.append(pr.as_pull_request())

    # Categorize and organize
    categorized_issues = {}
    categorized_prs = {}

    for issue in issues:
        category = categorize_issue(issue)
        if category not in categorized_issues:
            categorized_issues[category] = []
        categorized_issues[category].append(issue)

    for pr in pull_requests:
        category = categorize_pr(pr)
        if category not in categorized_prs:
            categorized_prs[category] = []
        categorized_prs[category].append(pr)

    # Generate changelog content
    changelog = []
    changelog.append(f"# Changelog for {current_tag}")
    changelog.append("")
    changelog.append(f"*Released on {datetime.now().strftime('%Y-%m-%d')}*")
    changelog.append("")

    # Breaking changes
    if "breaking" in categorized_prs:
        changelog.append("## 💥 Breaking Changes")
        changelog.append("")
        for pr in categorized_prs["breaking"]:
            changelog.append(format_pr_entry(pr))
        changelog.append("")

    # Features
    if "feature" in categorized_prs:
        changelog.append("## ✨ New Features")
        changelog.append("")
        for pr in categorized_prs["feature"]:
            changelog.append(format_pr_entry(pr))
        changelog.append("")

    # Bug fixes
    if "bug" in categorized_prs:
        changelog.append("## 🐛 Bug Fixes")
        changelog.append("")
        for pr in categorized_prs["bug"]:
            changelog.append(format_pr_entry(pr))
        changelog.append("")

    # Performance improvements
    if "performance" in categorized_prs:
        changelog.append("## ⚡ Performance Improvements")
        changelog.append("")
        for pr in categorized_prs["performance"]:
            changelog.append(format_pr_entry(pr))
        changelog.append("")

    # Documentation
    if "documentation" in categorized_prs:
        changelog.append("## 📚 Documentation")
        changelog.append("")
        for pr in categorized_prs["documentation"]:
            changelog.append(format_pr_entry(pr))
        changelog.append("")

    # Security
    if "security" in categorized_prs:
        changelog.append("## 🔒 Security")
        changelog.append("")
        for pr in categorized_prs["security"]:
            changelog.append(format_pr_entry(pr))
        changelog.append("")

    # Other changes
    if "other" in categorized_prs:
        changelog.append("## 🔧 Other Changes")
        changelog.append("")
        for pr in categorized_prs["other"]:
            changelog.append(format_pr_entry(pr))
        changelog.append("")

    # Issues (non-PRs)
    if any(categorized_issues.values()):
        changelog.append("## 📋 Issues")
        changelog.append("")
        for category, issues_list in categorized_issues.items():
            if category == "bug":
                changelog.append("### 🐛 Bug Reports")
            elif category == "feature":
                changelog.append("### ✨ Feature Requests")
            elif category == "documentation":
                changelog.append("### 📚 Documentation")
            else:
                changelog.append("### 🔧 Other Issues")
            changelog.append("")
            for issue in issues_list:
                changelog.append(format_issue_entry(issue))
            changelog.append("")

    # Statistics
    total_prs = sum(len(prs) for prs in categorized_prs.values())
    total_issues = sum(len(issues) for issues in categorized_issues.values())

    changelog.append("## 📊 Statistics")
    changelog.append("")
    changelog.append(f"- **Pull Requests**: {total_prs}")
    changelog.append(f"- **Issues**: {total_issues}")
    changelog.append(f"- **Total Changes**: {total_prs + total_issues}")
    changelog.append("")

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(changelog))

    print(f"Changelog written to {output_file}")
    print(f"Total PRs: {total_prs}, Total Issues: {total_issues}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate changelog from GitHub issues and PRs"
    )
    parser.add_argument(
        "--version", required=True, help="Version to generate changelog for"
    )
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    parser.add_argument("--output", default="CHANGELOG.md", help="Output file path")
    parser.add_argument("--token", help="GitHub token (or use GITHUB_TOKEN env var)")

    args = parser.parse_args()

    # Get GitHub token
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print(
            "Error: GitHub token required. Set GITHUB_TOKEN environment variable or use --token"
        )
        sys.exit(1)

    try:
        generate_changelog(token, args.repo, args.version, args.output)
    except Exception as e:
        print(f"Error generating changelog: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import os

    main()
