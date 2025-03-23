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

    pulls = get_pull_requests(github_class, "JackPlowman/DependabotTrigger")
    close_group_pull_requests(pulls)
    github_class.close()

def get_pull_requests(github_class: Github, repo_name: str) -> PaginatedList:
    # Get the repository
    repo = github_class.get_repo(repo_name)

    # Get all pull requests
    pulls = repo.get_pulls(state="open")
    logger.info("get_pull_requests", repo=repo_name, count=pulls.totalCount)

    # Print the title and number of each pull request
    for pull in pulls:
        logger.info("pull_request", number=pull.number, title=pull.title)

    return pulls


def close_group_pull_requests(pulls: PaginatedList) -> None:
    # Close all pull requests in the group
    count = 0
    for pull in pulls:
        if "group" not in pull.title:
            continue
        pull.edit(state="closed")
        count += 1
        logger.debug("close_pull_request", number=pull.number, title=pull.title)

    logger.info("close_group_pull_requests", count=count)

