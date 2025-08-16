from datetime import UTC, datetime, timedelta
from os import getenv

from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from playwright.sync_api import Page, sync_playwright
from structlog import get_logger, stdlib

from .custom_logging import set_up_custom_logging
from .summary import JobSummary

logger: stdlib.BoundLogger = get_logger()
STALE_PR_THRESHOLD_DAYS = 30


def app() -> None:
    """Main application function."""
    set_up_custom_logging()
    github = setup_github()
    summary = JobSummary()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        sign_into_github(page)
        repos = get_all_repos(github)
        for index, repo in enumerate(repos, start=1):
            pull_requests = get_pull_requests(github, repo.full_name)
            close_group_pull_requests(pull_requests, repo.full_name)
            warn_on_stale_pull_requests(pull_requests, repo.full_name, summary)
            trigger_dependabot(page, repo.full_name, summary)
            logger.info(
                "Scanned repository",
                repository=repo.full_name,
                percentage_complete=f"{int(index / len(repos) * 100)}%",
            )

    # Write summary after run
    mode, path = summary.write_markdown()
    logger.info("Wrote summary", mode=mode, path=str(path))


def sign_into_github(page: Page) -> None:
    """Sign into GitHub using Playwright."""
    page.goto("https://www.github.com/login")
    # Wait 120 seconds for user to enter credentials
    page.wait_for_url("https://github.com/", timeout=120000)


def setup_github() -> Github:
    """Set up the GitHub client.

    Returns:
        Github: An authenticated GitHub client.
    """
    auth_token = getenv("GITHUB_TOKEN")
    if not auth_token:
        msg = "GITHUB_TOKEN environment variable not set."
        raise ValueError(msg)
    return Github(auth_token)


def get_all_repos(github: Github) -> list[Repository]:
    """Retrieve the list of public repositories.

    Returns:
        list[Repository]: A list of repositories
    """
    # Authenticate to GitHub
    repositories = github.search_repositories(
        query="user:JackPlowman archived:false is:public DependabotTrigger",
    )
    logger.info(
        "Retrieved repositories to analyse",
        repositories_count=repositories.totalCount,
        repositories=[repository.full_name for repository in repositories],
    )
    return sorted(
        repositories,
        key=lambda repo: repo.full_name.lower(),
    )


def get_pull_requests(github_class: Github, repo_name: str) -> PaginatedList:
    """Fetches all open pull requests from the specified GitHub repository.

    Returns:
        PaginatedList: A list of open pull requests.
    """
    # Get the repository
    repo = github_class.get_repo(repo_name)

    # Get all open pull requests
    pull_requests = repo.get_pulls(state="open")
    logger.debug(
        "Retrieved open pull requests",
        repository=repo_name,
        pull_requests_count=pull_requests.totalCount,
    )

    return pull_requests


def close_group_pull_requests(
    pull_requests: PaginatedList,
    repo_name: str,
) -> None:
    """Closes group pull requests in the specified GitHub repository.

    Args:
        pull_requests (PaginatedList): A list of open pull requests.
        repo_name (str): The name of the repository in the format "owner/repo".
    """
    prs_to_close = [pull for pull in pull_requests if "updates" in pull.title]
    for pull in prs_to_close:
        logger.debug(
            "Closing pull request",
            repository=repo_name,
            pull_request_number=pull.number,
            pull_request_title=pull.title,
        )
        pull.create_issue_comment(
            "This PR is being closed as it is a group PR. "
            "PR will be recreated by Dependabot."
        )
        pull.edit(state="closed")

    logger.debug(
        "Closed group pull requests",
        repository=repo_name,
        closed_pull_requests_count=len(prs_to_close),
    )


def warn_on_stale_pull_requests(
    pull_requests: PaginatedList,
    repo_name: str,
    summary: JobSummary,
) -> None:
    """Warns about stale pull requests in the specified GitHub repository.

    Args:
        pull_requests (PaginatedList): A list of open pull requests.
        repo_name (str): The name of the repository in the format "owner/repo".
        summary (JobSummary): Collector for job and warning summary output.
    """
    thirty_days_ago = datetime.now(UTC) - timedelta(days=STALE_PR_THRESHOLD_DAYS)
    stale_prs = [
        pull
        for pull in pull_requests
        if (
            "updates" not in pull.title
            and pull.created_at < thirty_days_ago
            and (
                "dependabot" in (pull.head.ref or "").lower()
                or "dependabot" in (pull.base.ref or "").lower()
            )
        )
    ]

    for pull in stale_prs:
        logger.warning(
            "Stale pull request found",
            repository=repo_name,
            pull_request_number=pull.number,
            pull_request_title=pull.title,
        )
        created = (
            pull.created_at
            if getattr(pull.created_at, "tzinfo", None)
            else pull.created_at.replace(tzinfo=UTC)
        )
        summary.record_stale_pr(
            repository=repo_name,
            number=pull.number,
            title=pull.title,
            created_at=created,
        )


def trigger_dependabot(page: Page, repository_name: str, summary: JobSummary) -> None:
    """Trigger Dependabot to scan the repository for updates.

    Args:
        page (Page): The Playwright page object.
        repository_name (str): The name of the repository in the format "owner/repo".
        summary (JobSummary): Collector for job and warning summary output.
    """
    page.goto(f"https://github.com/{repository_name}/network/updates")
    dependabot_urls: list[tuple[str, str]] = []
    dependabot_jobs = page.query_selector("id=dependabot-updates")
    if dependabot_jobs is not None:
        for job_box in dependabot_jobs.query_selector_all(".Box.mb-3"):
            # Find the "Recent update jobs" link
            link = job_box.query_selector("text=Recent update jobs")
            check_for_updates_link = (
                f"https://github.com{link.get_attribute('href')}"
                if link is not None
                else None
            )
            # Find the first SVG in the job_box (the job type icon)
            svg = job_box.query_selector("svg")
            if svg is None:
                dependabot_urls.append((check_for_updates_link, "error__svg_not_found"))
                continue
            title_element = svg.query_selector("title")
            job_type = (
                title_element.inner_html()
                if title_element
                else "error__title_element_not_found"
            )
            logger.debug(
                "Found Dependabot job",
                repository=repository_name,
                job_type=job_type,
                check_for_updates_link=check_for_updates_link,
            )
            dependabot_urls.append((check_for_updates_link, job_type))
    logger.debug(
        "Retrieved Dependabot URLs",
        repository=repository_name,
        dependabot_urls=[url for url, _ in dependabot_urls],
    )
    for url, job_type in dependabot_urls:
        page.goto(url)
        page.click("text=Check for updates")
        summary.record_triggered_job(repository_name, job_type)
