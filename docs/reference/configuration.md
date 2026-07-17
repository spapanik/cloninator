# Configuration Reference

Complete reference for cloninator configuration files.

## File Locations

- **Primary config**: `~/.config/cloninator/config.yaml`
- **Additional configs**: `~/.config/cloninator/config.yaml.d/*.yaml`

All YAML files are automatically merged, allowing you to split configuration across multiple files.

## Top-Level Keys

### `/root` (Required)

The base directory where all repositories will be cloned.

```yaml
/root: ~/projects
```

**Type**: String (path)
**Required**: Yes
**Example**: `~/projects`, `/home/user/repos`, `C:\Users\user\projects`

### `/prefix` (Optional)

A prefix to prepend to all remote URLs in the configuration group.

```yaml
/prefix: "git@github.com:"

myrepo:
    /remotes:
        - name: origin
          url: user/repo.git # Becomes git@github.com:user/repo.git
```

**Type**: String
**Required**: No
**Default**: Empty string
**Use case**: Shorten URLs when all repos share a common hosting service

## Repository Configuration

Repositories are defined using nested directory structures. Each leaf node represents a repository.

### Structure

```yaml
group_name:
    subgroup:
        repo_name:
            /remotes: [...]
            /post_checkout: [...]
```

The path is constructed by joining all parent keys with the `/root` directory.

### `/remotes` (Required)

List of Git remotes for the repository.

```yaml
/remotes:
    - name: origin
      url: git@github.com:user/repo.git
    - name: upstream
      url: git@github.com:upstream/repo.git
```

**Type**: List of objects
**Required**: Yes
**Constraints**:

- Must be present and non-empty
- Each remote must have both `name` and `url` fields

#### Remote Object Properties

| Property | Type   | Required | Description        |
| -------- | ------ | -------- | ------------------ |
| `name`   | String | Yes      | Name of the remote |
| `url`    | String | Yes      | URL of the remote  |

**Note**: The first remote in the list is used as the initial clone origin. Additional remotes are added after cloning.

### `/post_checkout` (Optional)

List of shell commands to execute after cloning the repository.

```yaml
/post_checkout:
    - pip install -r requirements.txt
    - npm install
    - make build
```

**Type**: List of strings
**Required**: No
**Default**: Empty list

**Security Note**: Commands run with `shell=True`. Only include trusted commands.

**Common use cases**:

- Installing dependencies (`pip install`, `npm install`, `bundle install`)
- Setting up virtual environments
- Running build scripts
- Initializing submodules
- Creating symlinks

## Validation Rules

1. All special keys must start with `/` (e.g., `/remotes`, `/post_checkout`, `/root`, `/prefix`)
2. `/remotes` must be present and non-empty for each repository
3. `/remotes` must be a list
4. Each remote must have both `name` and `url` fields
5. Directory keys (non-special) cannot contain non-string keys
6. Invalid configurations are skipped with error messages

## Complete Example

```yaml
# ~/.config/cloninator/config.yaml
/root: ~/projects
/prefix: "https://github.com/"

personal:
    blog:
        /remotes:
            - name: origin
              url: user/blog.git
        /post_checkout:
            - bundle install

work:
    backend:
        api-service:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/api.git
                - name: staging
                  url: git@gitlab.com:company-staging/api.git
            /post_checkout:
                - docker-compose up -d
                - pip install -r requirements.txt

    frontend:
        web-app:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/web.git
```

This configuration creates:

- `~/projects/personal/blog` with remote `origin` at `https://github.com/user/blog.git`
- `~/projects/work/backend/api-service` with remotes `origin` and `staging`
- `~/projects/work/frontend/web-app` with remote `origin`

## Split Configuration Example

**Main config** (`config.yaml`):

```yaml
/root: ~/projects
```

**Personal repos** (`config.yaml.d/personal.yaml`):

```yaml
personal:
    myproject:
        /remotes:
            - name: origin
              url: git@github.com:user/myproject.git
```

**Work repos** (`config.yaml.d/work.yaml`):

```yaml
work:
    company-repo:
        /remotes:
            - name: origin
              url: git@gitlab.com:company/repo.git
```

All three files are automatically merged into a single configuration.

## Environment Variables

Configuration paths support environment variable expansion:

```yaml
/root: ${HOME}/projects
```

## Merge Order

When multiple configuration files exist:

1. Main config (`config.yaml`) is loaded first
2. Additional configs from `config.yaml.d/` are loaded in alphabetical order
3. Later values override earlier values for the same keys
4. Nested structures are merged recursively

## Troubleshooting

### Common Errors

**"Missing required field: /remotes"**

- Ensure every repository has a `/remotes` key with at least one remote

**"Invalid remote configuration"**

- Check that each remote has both `name` and `url` fields
- Verify YAML syntax

**"Directory already exists"**

- Cloninator skips existing directories
- Remove the directory if you want to reclone

### Debugging

Use verbose mode to see detailed information:

```bash
cloninator clone -vvv
```

This shows:

- Which configuration files are being loaded
- Validation errors with specific line numbers
- Full tracebacks for unexpected errors
