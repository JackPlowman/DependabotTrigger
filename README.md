# DependabotTrigger

DependabotTrigger is a Python script that automates the process of triggering Dependabot version update jobs for GitHub repositories. It uses Playwright to interact with the GitHub web interface and trigger updates for all repositories for a give user.

## Table of Contents

- [DependabotTrigger](#dependabottrigger)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/JackPlowman/DependabotTrigger.git
cd DependabotTrigger
```

2. To use DependabotTrigger you need to have some prerequisites installed. Install the following tools:

Required:

- [Just](https://just.systems/man/en/packages.html)
- [uv](https://docs.astral.sh/uv/#installation)

Development Dependencies:

- [Lefthook](https://lefthook.dev/installation/index.html) - for managing Git hooks
- [Zizmor](https://docs.zizmor.sh/installation/) - for managing project dependencies
- [Editorconfig-checker](https://editorconfig-checker.github.io/) - for maintaining consistent coding styles
- [prettier](https://prettier.io/docs/install) - for code formatting
- [actionlint](https://github.com/rhysd/actionlint/blob/main/docs/install.md) - for GitHub Actions linting
- [gitleaks](https://github.com/gitleaks/gitleaks?tab=readme-ov-file#installing) - for finding secrets in the codebase
- [trufflehog](https://github.com/trufflesecurity/trufflehog?tab=readme-ov-file#floppy_disk-installation) - for finding secrets in the codebase


1. Install the python dependencies:

```bash
just install
```

4. Install playwright browsers:

```bash
just install-browsers
```

## Usage

1. Export the following environment variables:

```bash
export GITHUB_TOKEN=<your_github_token>
```

2. Run the script:

```bash
just run
```



## Contributing

We welcome contributions to the project. Please read the [Contributing Guidelines](docs/CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENCE](LICENCE) file for details.
