# DependabotTrigger

DependabotTrigger is a Python script that automates the process of triggering Dependabot version update jobs for GitHub repositories. It uses Playwright to interact with the GitHub web interface and trigger updates for all repositories for a give user.

## Table of Contents

- [DependabotTrigger](#dependabottrigger)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/JackPlowman/DependabotTrigger.git
cd DependabotTrigger
```

2. To use DependabotTrigger you need to have some prerequisites installed. Install the following tools:

- [Just](https://just.systems/man/en/packages.html)
- [uv](https://docs.astral.sh/uv/#installation)

3. Install the python dependencies:

```bash
just install
```

4. Install playwright browsers:

```bash
just install-browsers
```

5. Export the following environment variables:

```bash
export GITHUB_TOKEN=<your_github_token>
export GITHUB_USER=<your_github_user>
```

6. Run the script:

```bash
just run
```

## Contributing

We welcome contributions to the project. Please read the [Contributing Guidelines](docs/CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENCE](LICENCE) file for details.
