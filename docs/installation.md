# Installation

## Requirements

- Python 3.10 or higher (Python 3.13 recommended)

## Recommended: Using uv

We recommend using [uv](https://github.com/astral-sh/uv) for installation as it provides an isolated environment, preventing dependency conflicts.

```bash
uv tool install --python 3.13 cloninator
```

This installs `cloninator` as a standalone tool with its own Python environment.

## Alternative Methods

### Using pip

```bash
pip install cloninator
```

### From Source

```bash
git clone https://github.com/spapanik/cloninator.git
cd cloninator
uv sync
uv run cloninator --help
```

## Verify Installation

```bash
cloninator --version
```

## Next Steps

After installation, see the [Usage Guide](usage.md) to create your first configuration.
