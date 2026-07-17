# Commands

Cloninator provides two main commands: `clone` and `generate`.

## clone

Clone all repositories defined in your configuration.

### Usage

```bash
cloninator clone [-v]
```

### Options

- `-v, --verbose`: Increase verbosity (can be stacked: `-vv`, `-vvv`)

### Behavior

The `clone` command:

1. Reads configuration from `~/.config/cloninator/config.yaml`
2. Merges additional configs from `~/.config/cloninator/config.yaml.d/*.yaml`
3. For each configured repository:
   - Skips if the directory already exists and is non-empty
   - Creates the directory structure based on the configuration
   - Clones using the first remote as origin
   - Adds additional remotes (if configured)
   - Runs post-checkout commands (if configured)
   - Reports 🟢 success only after every setup step succeeds
4. If a setup step fails, reports the error with 🔴, stops processing, and exits
   with status code `1`

### Examples

Basic usage:

```bash
cloninator clone
```

With verbose output:

```bash
cloninator clone -v
```

Extra verbose with full tracebacks:

```bash
cloninator clone -vvv
```

## generate

Scan existing cloned repositories and generate configuration.

### Usage

```bash
cloninator generate [-v]
```

### Options

- `-v, --verbose`: Increase verbosity (can be stacked: `-vv`, `-vvv`)

### Behavior

The `generate` command:

1. Scans the configured root directory for `.git` directories
2. Extracts remote information using `git config`
3. Compares against existing config to find missing repos
4. Outputs a `repos.yaml` file with nested directory structure

!!! note
    You must manually merge the generated output into your main configuration file.

### Example Workflow

```bash
# Generate config for existing repos
cloninator generate

# Review the output
cat repos.yaml

# Manually merge into ~/.config/cloninator/config.yaml
```

## Global Options

These options work with any command:

- `--version`: Print the version number
- `-v, --verbose`: Increase verbosity level

## Exit Codes

- `0`: Success
- `1`: Repository setup or configuration error. For `clone`, processing stops at
  the first failure.
- `2`: Invalid command-line arguments or usage
