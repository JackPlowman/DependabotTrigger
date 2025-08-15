from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from os import getenv
from pathlib import Path


@dataclass
class StalePR:
    """Represents a stale Dependabot pull request entry for reporting."""

    repository: str
    number: int
    title: str
    created_at: datetime


@dataclass
class JobSummary:
    """Collects actions taken and renders a GitHub Markdown summary."""

    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    # repo -> job_type -> count
    triggered_jobs: dict[str, dict[str, int]] = field(default_factory=dict)
    stale_prs: list[StalePR] = field(default_factory=list)

    def record_triggered_job(self, repository: str, job_type: str) -> None:
        """Record a triggered job for a given repository and job type.

        Args:
            repository (str): Full repository name (e.g., "owner/repo").
            job_type (str): Dependabot job type (e.g., "pip", "npm", or "unknown").
        """
        repo_map = self.triggered_jobs.setdefault(repository, {})
        repo_map[job_type] = repo_map.get(job_type, 0) + 1

    def record_stale_pr(
        self,
        repository: str,
        number: int,
        title: str,
        created_at: datetime,
    ) -> None:
        """Record a stale Dependabot PR for reporting.

        Args:
            repository (str): Full repository name (e.g., "owner/repo").
            number (int): Pull request number.
            title (str): Pull request title.
            created_at (datetime): PR creation time (timezone-aware preferred).
        """
        self.stale_prs.append(StalePR(repository, number, title, created_at))

    def _render_jobs_table(self) -> str:
        lines: list[str] = []
        lines.append("| Repository | Job Type | Jobs Triggered |")
        lines.append("|---|---|---:|")
        if not self.triggered_jobs:
            lines.append("| _None_ | _N/A_ | 0 |")
            return "\n".join(lines)

        # Sort by repo then job type for stable output
        grand_total = 0
        for repo in sorted(self.triggered_jobs.keys(), key=str.lower):
            repo_total = 0
            for job_type, count in sorted(
                self.triggered_jobs[repo].items(), key=lambda kv: kv[0].lower()
            ):
                lines.append(f"| {repo} | {job_type} | {count} |")
                repo_total += count
                grand_total += count
            # Repo subtotal row
            lines.append(f"| {repo} | Total | {repo_total} |")
        # Grand total row
        lines.append(f"| All repositories | Total | {grand_total} |")
        return "\n".join(lines)

    def _render_stale_prs_table(self) -> str:
        lines: list[str] = []
        lines.append("| Repository | PR # | Title | Created (UTC) | Age (days) |")
        lines.append("|---|---:|---|---|---:|")
        if not self.stale_prs:
            lines.append("| _None_ |  |  |  |  |")
            return "\n".join(lines)

        # Stable ordering: repo, then PR number
        now = datetime.now(UTC)
        for pr in sorted(
            self.stale_prs, key=lambda p: (p.repository.lower(), p.number)
        ):
            age_days = max(0, int((now - pr.created_at).total_seconds() // 86400))
            created_str = pr.created_at.strftime("%Y-%m-%d %H:%M:%S %Z")
            safe_title = pr.title.replace("|", "\\|")
            lines.append(
                "| "
                f"{pr.repository} | {pr.number} | {safe_title} | "
                f"{created_str} | {age_days}"
                " |"
            )
        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Render the complete markdown report.

        Returns:
            str: The rendered GitHub-flavoured Markdown content.
        """
        end_time = self.finished_at or datetime.now(UTC)
        header = [
            "# DependabotTrigger Summary",
            "",
            f"- Started: {self.started_at.strftime('%Y-%m-%d %H:%M:%S %Z')}",
            f"- Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
            f"- Total repositories with jobs: {len(self.triggered_jobs)}",
            f"- Total stale PR warnings: {len(self.stale_prs)}",
            "",
            "## Triggered Dependabot Jobs",
            self._render_jobs_table(),
            "",
            "## Stale Dependabot PR Warnings",
            self._render_stale_prs_table(),
            "",
        ]
        return "\n".join(header)

    def write_markdown(self, output_path: str | None = None) -> tuple[str, Path]:
        """Write markdown to a file.

        Args:
            output_path (str | None): Optional explicit output file path when not
                running in GitHub Actions. Defaults to "dependabot_summary.md".

        Returns:
            tuple[str, Path]: A tuple of write mode ("append" | "write") and file path.

        Notes:
            Prefers the GitHub Actions step summary if available.
        """
        self.finished_at = self.finished_at or datetime.now(UTC)
        content = self.to_markdown() + "\n"

        # Prefer GitHub Actions step summary file if available
        gha_summary_path = getenv("GITHUB_STEP_SUMMARY")
        if gha_summary_path:
            path = Path(gha_summary_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            mode = "append" if path.exists() else "write"
            with path.open("a", encoding="utf-8") as f:
                f.write(content)
            return (mode, path)

        # Fallback to local file in CWD
        file_name = output_path or "dependabot_summary.md"
        path = Path(file_name)
        path.write_text(content, encoding="utf-8")
        return ("write", path)
