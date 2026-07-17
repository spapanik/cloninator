# cloninator

[![build][build_badge]][build_url]
[![lint][lint_badge]][lint_url]
[![tests][tests_badge]][tests_url]
[![license][licence_badge]][licence_url]
[![codecov][codecov_badge]][codecov_url]
[![readthedocs][readthedocs_badge]][readthedocs_url]
[![pypi][pypi_badge]][pypi_url]
[![downloads][pepy_badge]][pepy_url]

**A CLI tool to manage Git repositories through YAML configuration.**

`cloninator` allows you to define your Git repositories once in a YAML configuration file, then clone them all with a single command. Perfect for setting up development environments across multiple machines or managing large collections of repositories.

## Features

- **Bulk cloning**: Clone all configured repositories with one command
- **Multiple remotes**: Automatically configure origin, upstream, and other remotes
- **Post-checkout automation**: Run setup commands after cloning (e.g., `pip install`, `npm install`)
- **Nested organization**: Mirror your desired directory structure in config
- **Split configurations**: Organize configs across multiple files (personal, work, etc.)
- **Config generation**: Scan existing repos to auto-generate configuration
- **Idempotent**: Safe to run repeatedly; skips already-cloned repos

## Quick Example

```yaml
# ~/.config/cloninator/config.yaml
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

```bash
$ cloninator clone
🟡 Cloning git@github.com:user/myproject.git at ~/projects/personal/myproject...
🟢 Cloned git@github.com:user/myproject.git at ~/projects/personal/myproject.
🟡 Cloning git@gitlab.com:company/repo.git at ~/projects/work/company-repo...
🟡 Adding remote upstream at git@gitlab.com:upstream/repo.git for ~/projects/work/company-repo...
🟡 Running post-checkout commands ['pip install -r requirements.txt'] for ~/projects/work/company-repo...
🟢 Cloned git@gitlab.com:company/repo.git at ~/projects/work/company-repo.
```

The 🟡 messages mark work in progress; 🟢 confirms that cloning, remote
setup, and post-checkout commands all completed. On failure, cloninator reports
the repository and error with 🔴, stops processing, and exits with status code
`1`.

## Getting Started

- [Installation](getting-started/installation.md) - Install cloninator
- [Quick Start](getting-started/quick-start.md) - Your first configuration

## User Guide

- [Configuration](guide/configuration.md) - Learn how to configure cloninator
- [Commands](guide/commands.md) - Available commands and options
- [Examples](guide/examples.md) - Real-world usage examples
- [Workflows](guide/workflows.md) - Common workflows and patterns

## Reference

- [Configuration Reference](reference/configuration.md) - Complete configuration reference
- [CLI Reference](reference/cli.md) - Command-line interface reference

## Links

- [GitHub Repository](https://github.com/spapanik/cloninator)
- [PyPI Package](https://pypi.org/project/cloninator/)
- [Contributing](contributing.md)

[build_badge]: https://github.com/spapanik/cloninator/actions/workflows/build.yml/badge.svg
[build_url]: https://github.com/spapanik/cloninator/actions/workflows/build.yml
[lint_badge]: https://github.com/spapanik/cloninator/actions/workflows/lint.yml/badge.svg
[lint_url]: https://github.com/spapanik/cloninator/actions/workflows/lint.yml
[tests_badge]: https://github.com/spapanik/cloninator/actions/workflows/tests.yml/badge.svg
[tests_url]: https://github.com/spapanik/cloninator/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/pypi/l/cloninator
[licence_url]: license.md
[codecov_badge]: https://codecov.io/github/spapanik/cloninator/graph/badge.svg?token=Q20F84BW72
[codecov_url]: https://codecov.io/github/spapanik/cloninator
[readthedocs_badge]: https://readthedocs.org/projects/cloninator/badge/?version=latest
[readthedocs_url]: https://cloninator.readthedocs.io/en/latest/
[pypi_badge]: https://img.shields.io/pypi/v/cloninator
[pypi_url]: https://pypi.org/project/cloninator
[pepy_badge]: https://pepy.tech/badge/cloninator
[pepy_url]: https://pepy.tech/project/cloninator
