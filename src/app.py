from github import Github, PaginatedList
from structlog import get_logger, stdlib
from os import getenv

logger: stdlib.BoundLogger = get_logger()

def app() -> None:
    """Main application function."""
    # Authenticate to GitHub
    auth_token = getenv("GITHUB_TOKEN")
    if not auth_token:
        raise ValueError("GITHUB_TOKEN environment variable not set.")

    # Create a Github instance
    github_class = Github(auth_token)

    repo_name = "JackPlowman/DependabotTrigger"
    pulls = get_pull_requests(github_class, repo_name)
    comment_on_pull_request(pulls)
    log_all_pull_requests(repo_name, pulls)
    github_class.close()

def get_pull_requests(github_class: Github, repo_name: str) -> PaginatedList:
    """Fetches all open pull requests from the specified GitHub repository.

    Args:
        github_class (Github): An authenticated Github instance.
        repo_name (str): The name of the repository in the format "owner/repo".
    """
    # Get the repository
    repo = github_class.get_repo(repo_name)

    # Get all open pull requests
    pulls = repo.get_pulls(state="open")
    logger.info("get_pull_requests", repo=repo_name, count=pulls.totalCount)

    # Print the title and number of each pull request
    for pull in pulls:
        logger.debug("pull_request", number=pull.number, title=pull.title)

    return pulls

def comment_on_pull_request(pulls: PaginatedList) -> None:
    """Adds a comment to each pull request in the provided list, requesting a rebase.

    Args:
        pulls (PaginatedList): A list of pull request objects to comment on.
    """
    for pull in pulls:
        pull.create_issue_comment("@dependabot rebase")

def log_all_pull_requests( repo_name: str,
        pulls: PaginatedList) -> None:
    """Logs the title and number of each pull request in the provided list.

    Args:
        repo_name (str): The name of the repository in the format "owner/repo".
        pulls (PaginatedList): A list of pull request objects to log.
    """
    logger.info(repo_name, pull_request_count=pulls.totalCount, pull_request_links=[pull.html_url for pull in pulls])

