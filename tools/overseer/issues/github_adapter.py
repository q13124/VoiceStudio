"""
GitHub Issue Adapter for external issue ingestion.

Fetches issues from GitHub repositories and converts them to the
internal Issue model for unified tracking.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Lazy import httpx to avoid hard dependency
_httpx = None


def _get_httpx():
    """Lazy import httpx for API requests."""
    global _httpx
    if _httpx is None:
        try:
            import httpx
            _httpx = httpx
        except ImportError:
            raise ImportError(
                "httpx is required for GitHub integration. "
                "Install with: pip install httpx"
            )
    return _httpx


from tools.overseer.issues.models import (
    InstanceType,
    Issue,
    IssuePriority,
    IssueSeverity,
    IssueStatus,
)


@dataclass
class GitHubIssue:
    """Represents a GitHub issue before conversion."""

    number: int
    title: str
    body: str
    state: str  # "open" or "closed"
    labels: list[str]
    created_at: datetime
    updated_at: datetime
    url: str
    author: str
    assignees: list[str]
    milestone: str | None
    repository: str
    comments_count: int


class GitHubAdapter:
    """
    Adapter for fetching and converting GitHub issues.

    Supports both public and private repositories (with token).
    Uses the GitHub REST API v3.
    """

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        owner: str,
        repo: str,
        token: str | None = None,
    ):
        """
        Initialize the adapter.

        Args:
            owner: Repository owner (organization or user)
            repo: Repository name
            token: GitHub personal access token (optional for public repos)
        """
        self.owner = owner
        self.repo = repo
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self._client = None

    def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            httpx = _get_httpx()
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "VoiceStudio-IssueAdapter/1.0",
            }
            if self.token:
                headers["Authorization"] = f"token {self.token}"
            self._client = httpx.Client(headers=headers, timeout=30.0)
        return self._client

    def fetch_issues(
        self,
        state: str = "open",
        labels: list[str] | None = None,
        since: datetime | None = None,
        max_issues: int = 100,
    ) -> list[GitHubIssue]:
        """
        Fetch issues from GitHub.

        Args:
            state: Issue state ("open", "closed", "all")
            labels: Filter by labels
            since: Only issues updated after this date
            max_issues: Maximum number of issues to fetch

        Returns:
            List of GitHubIssue objects
        """
        client = self._get_client()
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/issues"

        params: dict[str, Any] = {
            "state": state,
            "per_page": min(max_issues, 100),
            "sort": "updated",
            "direction": "desc",
        }

        if labels:
            params["labels"] = ",".join(labels)

        if since:
            params["since"] = since.isoformat()

        issues = []
        page = 1

        while len(issues) < max_issues:
            params["page"] = page
            response = client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if not data:
                break

            for item in data:
                # Skip pull requests (they appear in issues endpoint)
                if "pull_request" in item:
                    continue

                github_issue = self._parse_github_issue(item)
                issues.append(github_issue)

                if len(issues) >= max_issues:
                    break

            page += 1

        return issues

    def fetch_issue(self, issue_number: int) -> GitHubIssue | None:
        """
        Fetch a single issue by number.

        Args:
            issue_number: The issue number

        Returns:
            GitHubIssue or None if not found
        """
        client = self._get_client()
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/issues/{issue_number}"

        try:
            response = client.get(url)
            response.raise_for_status()
            return self._parse_github_issue(response.json())
        except Exception:
            return None

    def _parse_github_issue(self, data: dict[str, Any]) -> GitHubIssue:
        """Parse GitHub API response into GitHubIssue."""
        return GitHubIssue(
            number=data["number"],
            title=data["title"],
            body=data.get("body") or "",
            state=data["state"],
            labels=[label["name"] for label in data.get("labels", [])],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            url=data["html_url"],
            author=data["user"]["login"] if data.get("user") else "unknown",
            assignees=[a["login"] for a in data.get("assignees", [])],
            milestone=data["milestone"]["title"] if data.get("milestone") else None,
            repository=f"{self.owner}/{self.repo}",
            comments_count=data.get("comments", 0),
        )

    def convert_to_issue(self, github_issue: GitHubIssue) -> Issue:
        """
        Convert a GitHub issue to the internal Issue model.

        Args:
            github_issue: The GitHub issue to convert

        Returns:
            Internal Issue object
        """
        # Generate unique ID
        issue_id = f"gh-{self.owner}-{self.repo}-{github_issue.number}"

        # Determine severity from labels
        severity = self._infer_severity(github_issue.labels)

        # Determine category from labels
        category = self._infer_category(github_issue.labels, github_issue.title)

        # Determine status
        status = IssueStatus.RESOLVED if github_issue.state == "closed" else IssueStatus.NEW

        # Determine priority from labels
        priority = self._infer_priority(github_issue.labels)

        # Generate pattern hash from title
        pattern_hash = hashlib.md5(
            f"{github_issue.repository}:{github_issue.title}".encode()
        ).hexdigest()[:12]

        # Build context
        context = {
            "github_url": github_issue.url,
            "github_number": github_issue.number,
            "github_author": github_issue.author,
            "github_assignees": github_issue.assignees,
            "github_labels": github_issue.labels,
            "github_milestone": github_issue.milestone,
            "github_comments": github_issue.comments_count,
            "body_preview": github_issue.body[:500] if github_issue.body else "",
        }

        # Extract error type from title or body
        error_type = self._extract_error_type(github_issue.title, github_issue.body)

        return Issue(
            id=issue_id,
            timestamp=github_issue.created_at,
            instance_type=InstanceType.AGENT,  # External source
            instance_id=f"github:{self.owner}/{self.repo}",
            correlation_id=f"gh:{github_issue.number}",
            severity=severity,
            category=category,
            error_type=error_type,
            message=github_issue.title,
            context=context,
            pattern_hash=pattern_hash,
            status=status,
            labels=github_issue.labels,
            priority=priority,
        )

    def _infer_severity(self, labels: list[str]) -> IssueSeverity:
        """Infer severity from GitHub labels."""
        labels_lower = [l.lower() for l in labels]

        if any(l in labels_lower for l in ["critical", "severity: critical", "p0"]):
            return IssueSeverity.CRITICAL
        if any(l in labels_lower for l in ["high", "severity: high", "p1", "urgent"]):
            return IssueSeverity.HIGH
        if any(l in labels_lower for l in ["medium", "severity: medium", "p2"]):
            return IssueSeverity.MEDIUM
        return IssueSeverity.LOW

    def _infer_priority(self, labels: list[str]) -> IssuePriority | None:
        """Infer priority from GitHub labels."""
        labels_lower = [l.lower() for l in labels]

        if any(l in labels_lower for l in ["urgent", "priority: urgent", "p0"]):
            return IssuePriority.URGENT
        if any(l in labels_lower for l in ["high priority", "priority: high", "p1"]):
            return IssuePriority.HIGH
        if any(l in labels_lower for l in ["medium priority", "priority: medium", "p2"]):
            return IssuePriority.MEDIUM
        if any(l in labels_lower for l in ["low priority", "priority: low", "p3"]):
            return IssuePriority.LOW
        return None

    def _infer_category(self, labels: list[str], title: str) -> str:
        """Infer category from labels and title."""
        labels_lower = [l.lower() for l in labels]
        title_lower = title.lower()

        # Check labels first
        category_labels = {
            "bug": "error",
            "enhancement": "feature",
            "documentation": "docs",
            "ui": "ui",
            "frontend": "ui",
            "backend": "backend",
            "api": "api",
            "engine": "engine",
            "build": "build",
            "ci": "build",
            "test": "test",
            "performance": "performance",
            "security": "security",
        }

        for label in labels_lower:
            for key, category in category_labels.items():
                if key in label:
                    return category

        # Check title keywords
        title_keywords = {
            "crash": "crash",
            "error": "error",
            "fail": "error",
            "bug": "error",
            "feature": "feature",
            "request": "feature",
            "ui": "ui",
            "build": "build",
            "test": "test",
            "docs": "docs",
        }

        for keyword, category in title_keywords.items():
            if keyword in title_lower:
                return category

        return "general"

    def _extract_error_type(self, title: str, body: str) -> str:
        """Extract error type from issue content."""
        content = f"{title} {body}".lower()

        # Look for common error patterns
        error_patterns = [
            (r"(exception|error):\s*(\w+)", "exception"),
            (r"(\w+error)\b", "error"),
            (r"(\w+exception)\b", "exception"),
            (r"crash", "crash"),
            (r"timeout", "timeout"),
            (r"null\s*(reference|pointer)?", "null_reference"),
            (r"memory\s*leak", "memory_leak"),
            (r"regression", "regression"),
        ]

        for pattern, error_type in error_patterns:
            if re.search(pattern, content):
                return error_type

        return "issue"

    def sync_issues(
        self,
        state: str = "open",
        labels: list[str] | None = None,
        since: datetime | None = None,
        max_issues: int = 100,
    ) -> list[Issue]:
        """
        Fetch and convert GitHub issues to internal format.

        Convenience method that combines fetch and convert.

        Args:
            state: Issue state filter
            labels: Label filter
            since: Only issues updated after this date
            max_issues: Maximum issues to sync

        Returns:
            List of converted Issue objects
        """
        github_issues = self.fetch_issues(
            state=state,
            labels=labels,
            since=since,
            max_issues=max_issues,
        )

        return [self.convert_to_issue(gi) for gi in github_issues]

    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
