# Usage

## Quick Start

### 1. Create Configuration

Create a configuration file at `~/.config/cloninator/config.yaml`:

```yaml
personal:
    /root: ~/projects
    myproject:
        /remotes:
            - name: origin
              url: git@github.com:user/myproject.git

work:
    /root: ~/projects
    /prefix: "git@gitlab.com:"
    company-repo:
        /remotes:
            - name: upstream
              url: upstream/repo.git
            - name: origin
              url: username/repo.git
        /post_checkout:
            - pip install -r requirements.txt
```

### 2. Clone Repositories

```bash
cloninator clone
```

This will:

- Create directory structure under `/root`
- Clone each repository with configured remotes
- Run post-checkout commands (if specified)
- Skip repositories that already exist

## Commands

### `clone`

Clone all repositories defined in your configuration.

```bash
cloninator clone [-v]
```

**Options:**

- `-v, --verbose`: Increase verbosity (can be stacked: `-vv`, `-vvv`)

**Behavior:**

- Reads configuration from `~/.config/cloninator/config.yaml`
- Can also read additional configs from `~/.config/cloninator/config.yaml.d/*.yaml`
- Skips repositories that already exist and are non-empty
- For new repositories:
    1. Creates directory structure
    2. Clones using first remote as origin
    3. Adds additional remotes
    4. Runs post-checkout commands (if any)
    5. Reports 🟢 success only after every step succeeds
- If a repository setup step fails, reports the repository and error with 🔴,
  stops processing, and exits with status code `1`

### `generate`

Scan existing cloned repositories and generate configuration.

```bash
cloninator generate [-v]
```

**Options:**

- `-v, --verbose`: Increase verbosity (can be stacked: `-vv`, `-vvv`)

**Behavior:**

- Scans the configured root directory for `.git` directories
- Extracts remote information using git config
- Compares against existing config to find missing repos
- Outputs `repos.yaml` file with nested directory structure
- **Note:** You must manually merge the output into your main config

**Example workflow:**

```bash
# Generate config for existing repos
cloninator generate

# Review the output
cat repos.yaml

# Manually merge into ~/.config/cloninator/config.yaml
```

## Configuration Reference

### File Locations

- **Primary config:** `~/.config/cloninator/config.yaml`
- **Additional configs:** `~/.config/cloninator/config.yaml.d/*.yaml`

Multiple YAML files are automatically merged, allowing you to split configuration across files (e.g., separate files for personal and work repos).

### Structure

```yaml
/root: /path/to/repos/directory # REQUIRED: Base directory for all repos

# Nested directory structure representing repo organization
group_name:
    subgroup:
        repo_name:
            /remotes: # REQUIRED: List of git remotes
                - name: origin # Remote name
                  url: https://github.com/user/repo.git
                - name: upstream
                  url: https://github.com/upstream/repo.git
            /post_checkout: # OPTIONAL: Commands to run after checkout
                - pip install -r requirements.txt
                - npm install
```

### Required Fields

- **`/root`**: Top-level key specifying where repos should be cloned
- **`/remotes`**: At least one remote per repository (list of objects with `name` and `url`)

### Optional Fields

- **`/post_checkout`**: List of shell commands to execute after cloning (only used during `clone`, not during `generate`)

### Validation Rules

1. All special keys must start with `/` (e.g., `/remotes`, `/post_checkout`)
2. `/remotes` must be present and non-empty
3. `/remotes` must be a list
4. Each remote must have both `name` and `url` fields
5. Directory keys (non-special) cannot contain non-string keys

Invalid configurations are skipped with error messages.

## Examples

### Example 1: Simple Personal Project

```yaml
/root: ~/projects

myapp:
    /remotes:
        - name: origin
          url: git@github.com:user/myapp.git
```

### Example 2: Multiple Remotes

```yaml
/root: ~/projects

forked-project:
    /remotes:
        - name: origin
          url: git@github.com:user/fork.git
        - name: upstream
          url: git@github.com:original/project.git
```

### Example 3: With Post-Checkout Commands

```yaml
/root: ~/projects

webapp:
    /remotes:
        - name: origin
          url: git@github.com:user/webapp.git
    /post_checkout:
        - npm install
        - npm run build
```

### Example 4: Nested Directory Structure

```yaml
/root: ~/projects

work:
    backend:
        api-service:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/api.git
    frontend:
        web-app:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/web.git

personal:
    side-project:
        /remotes:
            - name: origin
              url: git@github.com:user/side-project.git
```

This creates:

- `~/projects/work/backend/api-service`
- `~/projects/work/frontend/web-app`
- `~/projects/personal/side-project`

### Example 5: Split Configuration

Create `~/.config/cloninator/config.yaml`:

```yaml
/root: ~/projects
```

Create `~/.config/cloninator/config.yaml.d/personal.yaml`:

```yaml
personal:
    myproject:
        /remotes:
            - name: origin
              url: git@github.com:user/myproject.git
```

Create `~/.config/cloninator/config.yaml.d/work.yaml`:

```yaml
work:
    company-repo:
        /remotes:
            - name: origin
              url: git@gitlab.com:company/repo.git
```

All three files are automatically merged.

## Common Workflows

### Initial Setup

```bash
# 1. Create config directory
mkdir -p ~/.config/cloninator

# 2. Create initial config
cat > ~/.config/cloninator/config.yaml <<EOF
/root: ~/projects

personal:
  myproject:
    /remotes:
      - name: origin
        url: git@github.com:user/myproject.git
EOF

# 3. Clone all repos
cloninator clone
```

### Discover Existing Repos

```bash
# 1. Set up basic config with root
cat > ~/.config/cloninator/config.yaml <<EOF
/root: ~/projects
EOF

# 2. Generate config for existing repos
cloninator generate

# 3. Review and merge
cat repos.yaml
# Manually add to config.yaml
```

### Add New Repository

```bash
# 1. Edit config.yaml to add new repo
# 2. Run clone (will skip existing repos, clone new ones)
cloninator clone
```

### Update After Adding Remotes

```bash
# 1. Add remote manually
cd ~/projects/myrepo && git remote add upstream git@github.com:upstream/repo.git

# 2. Regenerate config
cloninator generate

# 3. Merge changes into main config
```

## Status Indicators

Cloninator uses emoji indicators for status messages:

- 🟡 Attempt/progress messages
- 🟢 Success messages
- 🔵 Info/skip messages (existing repos, local-only repos)
- 🔴 Repository setup failures

## Tips

- **Idempotent:** Safe to run `clone` multiple times; existing repos are skipped
- **Verbosity:** Use `-v` flag for more detailed output and full tracebacks on errors
- **Split configs:** Use `config.yaml.d/` directory to organize large configurations
- **Generate first:** If you have many existing repos, use `generate` to bootstrap your config
- **Post-checkout security:** Commands run with `shell=True`; only include trusted commands
