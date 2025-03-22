from github import Github, PaginatedList

def app() -> None:

    print("Hello from DependabotTrigger!")
    get_pull_requests("JackPlowman/DependabotTrigger")
    # get_pull_requests("octocat/Hello-World")


def get_pull_requests(repo_name:str) -> PaginatedList:
    # Authenticate to GitHub
    github_class = Github()

    # Get the repository
    repo = github_class.get_repo(repo_name)

    # Get all pull requests
    pulls = repo.get_pulls(state='active')

    return pulls
