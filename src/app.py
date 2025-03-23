from github import Github, PaginatedList
from os import getenv

def app() -> None:
    # Authenticate to GitHub
    auth_token = getenv("GITHUB_TOKEN")
    if not auth_token:
        raise ValueError("GITHUB_TOKEN environment variable not set.")

    github_class = Github(auth_token)

    pulls = get_pull_requests(github_class, "JackPlowman/DependabotTrigger")
    close_group_pull_requests(pulls)
    github_class.close()

def get_pull_requests(github_class: Github, repo_name: str) -> PaginatedList:
    # Get the repository
    repo = github_class.get_repo(repo_name)

    # Get all pull requests
    pulls = repo.get_pulls(state="open")

    print(f"Found {pulls.totalCount} open pull requests in {repo_name}.")
    # Print the title and number of each pull request
    for pull in pulls:
        print(f"Pull request #{pull.number}: {pull.title}")

    return pulls


def close_group_pull_requests(pulls: PaginatedList) -> None:
    # Close all pull requests in the group
    count = 0
    for pull in pulls:
        if "group" not in pull.title:
            continue
        pull.edit(state="closed")
        count += 1
        print(f"Closed pull request #{pull.number}: {pull.title}")
    print(f"Closed {count} pull requests in the group.")
