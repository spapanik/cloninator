# cloninator: A CLI Tool to Manage Your Repos

[![build][build_badge]][build_url]
[![lint][lint_badge]][lint_url]
[![tests][tests_badge]][tests_url]
[![license][licence_badge]][licence_url]
[![codecov][codecov_badge]][codecov_url]
[![readthedocs][readthedocs_badge]][readthedocs_url]
[![pypi][pypi_badge]][pypi_url]
[![downloads][pepy_badge]][pepy_url]
[![build automation: yam][yam_badge]][yam_url]
[![Lint: ruff][ruff_badge]][ruff_url]

`cloninator` is a command-line tool that manages Git repositories through YAML configuration. Define your repositories once, then clone them all with a single command. Perfect for setting up development environments across multiple machines or managing large collections of repositories.

## Features

- **Bulk cloning**: Clone all configured repositories with one command
- **Multiple remotes**: Automatically configure origin, upstream, and other remotes
- **Post-checkout automation**: Run setup commands after cloning (e.g., `pip install`, `npm install`)
- **Nested organization**: Mirror your desired directory structure in config
- **Split configurations**: Organize configs across multiple files (personal, work, etc.)
- **Config generation**: Scan existing repos to auto-generate configuration
- **Idempotent**: Safe to run repeatedly; skips already-cloned repos

## Quick Start

### 1. Install

```bash
uv tool install --python 3.13 cloninator
```

### 2. Configure

Create `~/.config/cloninator/config.yaml`:

```yaml
/root: ~/projects

personal:
    myproject:
        /remotes:
            - name: origin
              url: git@github.com:user/myproject.git

work:
    company-repo:
        /remotes:
            - name: origin
              url: git@gitlab.com:company/repo.git
            - name: upstream
              url: git@gitlab.com:upstream/repo.git
        /post_checkout:
            - pip install -r requirements.txt
```

### 3. Clone

```bash
cloninator clone
```

Clone operations display 🟡 while work is in progress and 🟢 only after the
clone, remote setup, and post-checkout commands all succeed. If any step fails,
cloninator displays a 🔴 error, stops processing repositories, and exits with
status code `1`.

## Commands

- **`clone`**: Clone all repositories from configuration
- **`generate`**: Scan existing repos and generate configuration

See the [Usage Guide](usage.md) for detailed examples and workflows.

## Documentation

- [Installation Guide](installation.md)
- [Usage Guide](usage.md)
- [Changelog](CHANGELOG.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [License](LICENSE.md)

[build_badge]: https://github.com/spapanik/cloninator/actions/workflows/build.yml/badge.svg
[build_url]: https://github.com/spapanik/cloninator/actions/workflows/build.yml
[lint_badge]: https://github.com/spapanik/cloninator/actions/workflows/lint.yml/badge.svg
[lint_url]: https://github.com/spapanik/cloninator/actions/workflows/lint.yml
[tests_badge]: https://github.com/spapanik/cloninator/actions/workflows/tests.yml/badge.svg
[tests_url]: https://github.com/spapanik/cloninator/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/pypi/l/cloninator
[licence_url]: https://cloninator.readthedocs.io/en/stable/LICENSE/
[codecov_badge]: https://codecov.io/github/spapanik/cloninator/graph/badge.svg?token=Q20F84BW72
[codecov_url]: https://codecov.io/github/spapanik/cloninator
[readthedocs_badge]: https://readthedocs.org/projects/cloninator/badge/?version=latest
[readthedocs_url]: https://cloninator.readthedocs.io/en/latest/
[pypi_badge]: https://img.shields.io/pypi/v/cloninator
[pypi_url]: https://pypi.org/project/cloninator
[pepy_badge]: https://pepy.tech/badge/cloninator
[pepy_url]: https://pepy.tech/project/cloninator
[yam_badge]: https://img.shields.io/badge/build%20automation-yamk-success
[yam_url]: https://github.com/spapanik/yamk
[ruff_badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[ruff_url]: https://github.com/charliermarsh/ruff
[Documentation]: https://cloninator.readthedocs.io/en/stable/
[Changelog]: https://cloninator.readthedocs.io/en/stable/CHANGELOG/
