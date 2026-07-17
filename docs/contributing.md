# Contributing to cloninator

Thank you for your interest in contributing to cloninator! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating in this project.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the behavior
- Expected behavior vs actual behavior
- Your environment (OS, Python version, cloninator version)
- Configuration files (if relevant)
- Error messages or tracebacks

**Example:**

```markdown
**Describe the bug**
Cloninator fails to clone repositories when using /prefix with SSH URLs.

**To Reproduce**

1. Create config with /prefix: "git@github.com:"
2. Run cloninator clone
3. See error: "Invalid URL format"

**Expected behavior**
Repository should clone successfully with prefixed URL.

**Environment**

- OS: macOS 14.0
- Python: 3.13
- cloninator: 0.1.0
```

### Suggesting Features

Feature suggestions are welcome! Please include:

- A clear and descriptive title
- Detailed description of the proposed feature
- Use cases and examples
- Any potential drawbacks or alternatives considered

### Pull Requests

1. **Fork** the repository
2. **Create a branch** for your feature or fix
    ```bash
    git checkout -b feature/your-feature-name
    # or
    git checkout -b fix/issue-description
    ```
3. **Make your changes** following the coding guidelines
4. **Add tests** for new functionality
5. **Ensure all tests pass**
    ```bash
    pytest
    ```
6. **Run linting**
    ```bash
    ruff check .
    mypy src/
    ```
7. **Update documentation** if needed
8. **Commit your changes** with clear, descriptive messages
9. **Push** to your fork
10. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/cloninator.git
cd cloninator

# Install dependencies
uv sync --all-groups

# Install in development mode
uv run cloninator --help
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/cloninator

# Run specific test file
pytest tests/test_clone.py
```

### Linting and Type Checking

```bash
# Check code style
ruff check .

# Format code
ruff format .

# Type checking
mypy src/
```

## Coding Guidelines

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for public functions and classes
- Keep functions small and focused
- Use meaningful variable names

### Code Organization

- Keep related functionality together
- Use dataclasses for structured data
- Avoid global state where possible
- Write pure functions when feasible

### Testing

- Write tests for all new functionality
- Aim for 100% code coverage
- Test edge cases and error conditions
- Use descriptive test names

**Example:**

```python
def test_remote_with_empty_prefix() -> None:
    """Remote name should remain unchanged when prefix is empty."""
    remote = Remote(name="origin", url="github.com:user/repo.git")
    prefixed = remote.with_prefix("")
    assert prefixed.name == "origin"
    assert prefixed.url == "github.com:user/repo.git"
```

### Commit Messages

Follow conventional commit format with emoji prefixes:

- `✨` New feature
- `🐛` Bug fix
- `♻️` Refactoring
- `📚` Documentation
- `⬆️` Dependencies
- `🔧` Configuration
- `✅` Tests

**Examples:**

```
✨ Add support for multiple config directories

🐛 Fix remote URL prefix handling

♻️ Refactor configuration parsing logic
```

## Documentation

### Writing Documentation

- Use clear, concise language
- Include code examples
- Provide context and use cases
- Update docs when changing functionality

### Building Documentation Locally

```bash
# Install docs dependencies
uv sync --group docs

# Build and serve docs
mkdocs serve

# Build static site
mkdocs build
```

View the documentation at `http://localhost:8000`.

## Release Process

Releases are managed by the maintainers. The process includes:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. Publish to PyPI
5. Deploy documentation

## Questions?

If you have questions about contributing:

- Open an issue with the "question" label
- Check existing issues and discussions
- Read the documentation

## Recognition

Contributors are recognized in:

- The CHANGELOG.md file
- GitHub contributors list
- Release notes

Thank you for contributing to cloninator!
