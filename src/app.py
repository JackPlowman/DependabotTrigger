from playwright.sync_api import sync_playwright, Page
from os import getenv
from structlog import get_logger, stdlib
from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository

logger: stdlib.BoundLogger = get_logger()


def app() -> None:
    """Main application function."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        sign_into_github(page)
        get_all_repos()


def sign_into_github(page: Page) -> None:
    """Sign into GitHub using Playwright."""
    page.goto("https://www.github.com/login")
    # Wait 30 seconds for user to enter credentials
    page.wait_for_url("https://github.com/", timeout=30000)


def get_all_repos() -> PaginatedList[Repository]:
    """Retrieve the list of repositories to analyse.

    Returns:
        PaginatedList[Repository]: The list of repositories.
    """
    # Authenticate to GitHub
    auth_token = getenv("GITHUB_TOKEN")
    if not auth_token:
        raise ValueError("GITHUB_TOKEN environment variable not set.")
    github = Github()
    repositories = github.search_repositories(
        query="user:JackPlowman archived:false is:public",
    )
    logger.info(
        "Retrieved repositories to analyse",
        repositories_count=repositories.totalCount,
        repositories=[repository.full_name for repository in repositories],
    )
    return repositories
