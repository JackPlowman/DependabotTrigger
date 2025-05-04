from playwright.sync_api import Page, sync_playwright
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
        github = setup_github()
        for repo in get_all_repos(github):
            close_group_pull_requests(github, repo.full_name)
            trigger_dependabot(page, repo.full_name)


def sign_into_github(page: Page) -> None:
    """Sign into GitHub using Playwright."""
    page.goto("https://www.github.com/login")
    # Wait 30 seconds for user to enter credentials
    page.wait_for_url("https://github.com/", timeout=30000)


def setup_github() -> Github:
    """Set up the GitHub client.

    Returns:
        Github: An authenticated GitHub client.
    """
    auth_token = getenv("GITHUB_TOKEN")
    if not auth_token:
        raise ValueError("GITHUB_TOKEN environment variable not set.")
    github = Github(auth_token)
    return github


def get_all_repos(github: Github) -> PaginatedList[Repository]:
    """Retrieve the list of repositories to analyse.

    Returns:
        PaginatedList[Repository]: The list of repositories.
    """
    # Authenticate to GitHub
    repositories = github.search_repositories(
        query="user:JackPlowman archived:false is:public",
    )
    logger.info(
        "Retrieved repositories to analyse",
        repositories_count=repositories.totalCount,
        repositories=[repository.full_name for repository in repositories],
    )
    return repositories


def close_group_pull_requests(github_class: Github, repo_name: str) -> PaginatedList:
    """Fetches all open pull requests from the specified GitHub repository.

    Args:
        github_class (Github): An authenticated Github instance.
        repo_name (str): The name of the repository in the format "owner/repo".
    """
    # Get the repository
    repo = github_class.get_repo(repo_name)

    # Get all open pull requests
    pulls = repo.get_pulls(state="open")
    logger.info(
        "Retrieved open pull requests",
        repository=repo_name,
        pull_requests_count=pulls.totalCount,
    )
    prs_to_close = [pull for pull in pulls if "updates" in pull.title]

    for pull in prs_to_close:
        logger.debug(
            "Closing pull request",
            repository=repo_name,
            pull_request_number=pull.number,
            pull_request_title=pull.title,
        )
        pull.create_issue_comment("This PR is being closed as it is a group PR.")
        pull.edit(state="closed")

    logger.info(
        "Closed group pull requests",
        repository=repo_name,
        closed_pull_requests_count=len(prs_to_close),
    )
    return pulls


def trigger_dependabot(page: Page, repository_name: str) -> None:
    """Trigger Dependabot to scan the repository for updates.

    Args:
        page (Page): The Playwright page object.
        repository_name (str): The name of the repository in the format "owner/repo".
    """
    page.goto(f"https://github.com/{repository_name}/network/updates")
    dependabot_urls = [
        f"https://github.com{link.get_attribute('href')}"
        for link in page.query_selector_all("text=Recent update jobs")
    ]
    logger.info(
        "Retrieved Dependabot URLs",
        repository=repository_name,
        dependabot_urls=dependabot_urls,
    )
    for url in dependabot_urls:
        page.goto(url)
        page.click("text=Check for updates")
