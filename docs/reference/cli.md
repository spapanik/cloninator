# CLI Reference

Complete reference for the cloninator command-line interface.

## Synopsis

```bash
cloninator <command> [options]
```

## Global Options

These options work with any command:

| Option          | Description                         |
| --------------- | ----------------------------------- |
| `-v, --verbose` | Increase verbosity (can be stacked) |
| `--version`     | Print version number and exit       |
| `-h, --help`    | Show help message and exit          |

### Verbosity Levels

- No flag: Basic output with emoji indicators
- `-v`: Additional progress information
- `-vv`: Detailed debug information
- `-vvv`: Full tracebacks on errors

## Commands

### clone

Clone all repositories from configuration.

```bash
cloninator clone [-v]
```

**Description**: Reads configuration and clones all defined repositories. Skips repositories that already exist.

**Options**:

| Option          | Description              |
| --------------- | ------------------------ |
| `-v, --verbose` | Increase verbosity level |

**Exit Codes**:

- `0`: Success (all repos cloned or skipped)
- `1`: Repository setup or configuration error. Processing stops at the first
  repository failure.

**Examples**:

```bash
# Basic usage
cloninator clone

# With verbose output
cloninator clone -v

# Maximum verbosity with tracebacks
cloninator clone -vvv
```

**Output Indicators**:

- 🟡 Attempt/progress messages
- 🟢 Success messages
- 🔵 Info/skip messages
- 🔴 Error messages

For a new repository, cloning, additional remote setup, and post-checkout
commands are one operation. The 🟢 message is emitted only when every step
succeeds. If any step fails, cloninator emits a 🔴 message containing the
repository path and underlying error, then exits with status code `1` without
processing the remaining repositories.

### generate

Scan existing repositories and generate configuration.

```bash
cloninator generate [-v]
```

**Description**: Scans the configured root directory for Git repositories and generates a configuration file.

**Options**:

| Option          | Description              |
| --------------- | ------------------------ |
| `-v, --verbose` | Increase verbosity level |

**Exit Codes**:

- `0`: Success
- `1`: Error

**Output**: Creates a
`~/.config/cloninator/config.yaml.d/new_repos_<random>.yaml` file containing the
discovered repositories.

**Examples**:

```bash
# Generate config for existing repos
cloninator generate

# With verbose output
cloninator generate -v
```

**Notes**:

- Only discovers repositories under the configured `/root` directory
- Compares against existing config to find missing repos
- Generated files are loaded automatically as split configuration
- Does not capture `/post_checkout` commands (these must be added manually)
- Without `--split-groups`, the output filename starts with `new_repos_`
- With `--split-groups`, each output filename starts with its repository group
  name (for example, `all_new_repos_<random>.yaml`)

## Configuration Files

Cloninator reads configuration from:

1. **Primary**: `~/.config/cloninator/config.yaml`
2. **Additional**: `~/.config/cloninator/config.yaml.d/*.yaml`

All YAML files are automatically merged. See [Configuration Reference](configuration.md) for details.

## Environment Variables

| Variable | Description                             |
| -------- | --------------------------------------- |
| `HOME`   | User's home directory (for config path) |

Configuration paths support environment variable expansion in YAML files.

## Return Values

All commands return standard Unix exit codes:

- **0**: Success
- **1**: General error
- **2**: Invalid arguments or usage error

## Examples

### Basic Workflow

```bash
# Clone all configured repositories
cloninator clone

# Discover new repositories
cloninator generate

# Review generated config
cat ~/.config/cloninator/config.yaml.d/new_repos_*.yaml

# The generated split config is loaded automatically; clone again
cloninator clone
```

### Debugging

```bash
# See what's happening
cloninator clone -vv

# Get full error details
cloninator clone -vvv
```

### Version Check

```bash
cloninator --version
```

## Tips

- Use `-v` flag for more detailed output during troubleshooting
- Run `generate` periodically to keep config synchronized with reality
- Use split configs (`config.yaml.d/`) for better organization
- Post-checkout commands only run during initial clone, not on subsequent runs
