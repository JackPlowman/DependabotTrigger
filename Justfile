# ------------------------------------------------------------------------------
# Common commands
# ------------------------------------------------------------------------------

# Install all dependencies
install:
    uv sync --all-extras

# Install playwright browsers
install-browsers:
    uv run playwright install --with-deps

# Run DependabotTrigger
run:
    uv run python -m src

# ------------------------------------------------------------------------------
# Ruff - Python Linting and Formatting
# ------------------------------------------------------------------------------

# Fix all Ruff issues
ruff-fix:
    just ruff-format-fix
    just ruff-lint-fix

# Check for all Ruff issues
ruff-checks:
    just ruff-format-check
    just ruff-lint-check

# Check for Ruff issues
ruff-lint-check:
    uv run ruff check .

# Fix Ruff lint issues
ruff-lint-fix:
    uv run ruff check . --fix

# Check for Ruff format issues
ruff-format-check:
    uv run ruff format --check .

# Fix Ruff format issues
ruff-format-fix:
    uv run ruff format .

# ------------------------------------------------------------------------------
# Ty - Python Type Checking
# ------------------------------------------------------------------------------

# Check for type issues with Ty
ty-check:
    uv run ty check .

# ------------------------------------------------------------------------------
# Other Python Tools
# ------------------------------------------------------------------------------

# Check for unused code
vulture:
    uv run vulture src

uv-lock-check:
    uv lock --check

# ------------------------------------------------------------------------------
# Prettier
# ------------------------------------------------------------------------------

# Check all files with prettier
prettier-check:
    prettier . --check

# Format all files with prettier
prettier-format:
    prettier . --check --write

# ------------------------------------------------------------------------------
# Justfile
# ------------------------------------------------------------------------------

# Format Justfile
format:
    just --fmt --unstable

# Check Justfile formatting
format-check:
    just --fmt --check --unstable

# ------------------------------------------------------------------------------
# Gitleaks
# ------------------------------------------------------------------------------

# Run gitleaks detection
gitleaks-detect:
    gitleaks detect --source .

# ------------------------------------------------------------------------------
# Lefthook
# ------------------------------------------------------------------------------

# Validate lefthook config
lefthook-validate:
    lefthook validate

# ------------------------------------------------------------------------------
# Zizmor
# ------------------------------------------------------------------------------

# Run zizmor checking
zizmor-check:
    uvx zizmor . --persona=auditor

# ------------------------------------------------------------------------------
# Actionlint
# ------------------------------------------------------------------------------

# Run actionlint checks
actionlint-check:
    actionlint

# ------------------------------------------------------------------------------
# Pinact
# ------------------------------------------------------------------------------

# Run pinact
pinact-run:
    pinact run

# Run pinact checking
pinact-check:
    pinact run --verify --check

# Run pinact update
pinact-update:
    pinact run --update

# ------------------------------------------------------------------------------
# EditorConfig
# ------------------------------------------------------------------------------

# Check files format with EditorConfig
editorconfig-check:
    editorconfig-checker

# ------------------------------------------------------------------------------
# Git Hooks
# ------------------------------------------------------------------------------

# Install pre commit hook to run on all commits
install-git-hooks:
    lefthook install -f
