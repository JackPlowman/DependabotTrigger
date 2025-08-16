# DependabotTrigger

Automate triggering Dependabot “Check for updates” jobs across repositories. This tool uses Playwright to open GitHub in a real browser session and PyGitHub (pygithub) to fetch/close PRs where needed.

## What it does

- Signs into GitHub in a browser window you control (you get 120 seconds to complete login/2FA).
- Lists public repositories for a specific user and visits each repo’s Dependabot page.
- Closes Dependabot “group” PRs (titles containing “updates”).
- Warns on stale Dependabot PRs older than 30 days.
- Creates a Markdown report summarising the actions taken.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/#installation)
- [just](https://just.systems/man/en/packages.html)

For development (optional):

- [lefthook](https://lefthook.dev/installation/index.html)
- [zizmor](https://docs.zizmor.sh/installation/)
- [editorconfig-checker](https://editorconfig-checker.github.io/)
- [prettier](https://prettier.io/docs/install)
- [actionlint](https://github.com/rhysd/actionlint/blob/main/docs/install.md)
- [gitleaks](https://github.com/gitleaks/gitleaks?tab=readme-ov-file#installing)
- [trufflehog](https://github.com/trufflesecurity/trufflehog?tab=readme-ov-file#floppy_disk-installation)

## Quick start

1. Clone the repository

```bash
git clone https://github.com/JackPlowman/DependabotTrigger.git
cd DependabotTrigger
```

2. Install Python deps and Playwright browsers

```bash
just install
just install-browsers
```

3. Set a GitHub token with permission to read repositories and close PRs

- PowerShell (Windows):

```powershell
$env:GITHUB_TOKEN = "<your_token>"
```

- Bash (macOS/Linux):

```bash
export GITHUB_TOKEN="<your_token>"
```

4. Run it

```bash
just run
```

When the Chromium window opens, complete GitHub sign-in (including 2FA) within 120 seconds. The tool will then iterate repositories and trigger Dependabot jobs.

## Output

- A Markdown report is written to `dependabot_summary.md` in the project root after each run.

## Contributing

We welcome contributions to the project. Please read the [Contributing Guidelines](docs/CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENCE](LICENCE) file for details.
