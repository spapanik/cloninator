# Common Workflows

This guide covers common workflows and patterns when using cloninator.

## Initial Setup

Setting up cloninator on a new machine:

```bash
# 1. Install cloninator
uv tool install --python 3.13 cloninator

# 2. Create config directory
mkdir -p ~/.config/cloninator

# 3. Create initial config
cat > ~/.config/cloninator/config.yaml <<EOF
/root: ~/projects

personal:
  myproject:
    /remotes:
      - name: origin
        url: git@github.com:user/myproject.git
EOF

# 4. Clone all repos
cloninator clone
```

## Discovering Existing Repositories

If you already have repositories cloned, use `generate` to create configuration:

```bash
# 1. Set up basic config with root directory
cat > ~/.config/cloninator/config.yaml <<EOF
/root: ~/projects
EOF

# 2. Generate config for existing repos
cloninator generate

# 3. Review the generated output
cat ~/.config/cloninator/config.yaml.d/new_repos_*.yaml

# 4. Rename or edit the generated split config as needed
```

!!! tip
The `generate` command only outputs missing repositories. Run it periodically to keep your config up to date.

## Adding New Repositories

When you want to add a new repository to your setup:

```bash
# 1. Edit config.yaml to add the new repo
# Add your new repository configuration

# 2. Run clone (will skip existing repos, clone new ones)
cloninator clone
```

Cloninator is idempotent - it's safe to run repeatedly.

## Updating After Manual Changes

If you manually add remotes or make changes to repositories:

```bash
# 1. Make manual changes
cd ~/projects/myrepo
git remote add upstream git@github.com:upstream/repo.git

# 2. Regenerate config to capture changes
cloninator generate

# 3. Review and merge changes
cat ~/.config/cloninator/config.yaml.d/new_repos_*.yaml
# Rename or edit the generated split config as needed
```

## Managing Multiple Environments

Use split configurations to manage different environments:

### Development vs Production

**Development** (`~/.config/cloninator/config.yaml.d/dev.yaml`):

```yaml
dev:
    experimental-project:
        /remotes:
            - name: origin
              url: git@github.com:user/experimental.git
```

**Production** (`~/.config/cloninator/config.yaml.d/prod.yaml`):

```yaml
prod:
    stable-project:
        /remotes:
            - name: origin
              url: git@github.com:user/stable.git
```

Enable/disable environments by renaming files:

```bash
# Disable dev environment
mv config.yaml.d/dev.yaml config.yaml.d/dev.yaml.disabled

# Enable dev environment
mv config.yaml.d/dev.yaml.disabled config.yaml.d/dev.yaml
```

## Syncing Configuration Across Machines

Share your cloninator configuration across multiple machines:

### Option 1: Dotfiles Repository

Store your config in a dotfiles repository:

```bash
# On machine 1
cp ~/.config/cloninator/config.yaml ~/dotfiles/cloninator/
git add ~/dotfiles/cloninator/config.yaml
git commit -m "Update cloninator config"
git push

# On machine 2
git pull
cp ~/dotfiles/cloninator/config.yaml ~/.config/cloninator/
cloninator clone
```

### Option 2: Cloud Storage

Sync via cloud storage (Dropbox, iCloud, etc.):

```bash
# Link config to cloud storage
ln -s ~/Dropbox/config/cloninator/config.yaml ~/.config/cloninator/config.yaml
```

## Working with Forks

Manage forked repositories with upstream tracking:

```yaml
/root: ~/projects

forked-lib:
    /remotes:
        - name: origin
          url: git@github.com:yourusername/lib.git
        - name: upstream
          url: git@github.com:originalauthor/lib.git
    /post_checkout:
        - git fetch upstream
```

Workflow:

```bash
cd ~/projects/forked-lib

# Create feature branch from upstream
git checkout -b feature upstream/main

# Push to your fork
git push origin feature

# Create PR on GitHub
```

## Bulk Operations

Run the same command across all cloned repositories:

```bash
# Update all repos
find ~/projects -name ".git" -type d -exec dirname {} \; | while read dir; do
    echo "Updating $dir..."
    git -C "$dir" pull
done

# Check status of all repos
find ~/projects -name ".git" -type d -exec dirname {} \; | while read dir; do
    echo "=== $dir ==="
    git -C "$dir" status -s
done
```

## Troubleshooting

### Repository Already Exists

If a repository exists but is empty or corrupted:

```bash
# Remove the problematic directory
rm -rf ~/projects/problematic-repo

# Re-run clone
cloninator clone
```

### Network Issues

If cloning fails due to network issues:

```bash
# Use verbose mode to see detailed errors
cloninator clone -vv

# Check your SSH/Git credentials
ssh -T git@github.com
git ls-remote git@github.com:user/repo.git
```

### Invalid Configuration

If you get validation errors:

```bash
# Use verbose mode to see which entries are invalid
cloninator clone -vv

# Check your YAML syntax
python -c "import yaml; yaml.safe_load(open('~/.config/cloninator/config.yaml'))"
```

## Best Practices

1. **Keep configs DRY**: Use `/prefix` to avoid repeating common URL parts
2. **Split large configs**: Use `config.yaml.d/` for organization
3. **Version control configs**: Store configs in a dotfiles repo
4. **Test post-checkout commands**: Verify they work before adding to config
5. **Use descriptive names**: Name remotes clearly (origin, upstream, staging)
6. **Document complex setups**: Add comments in your YAML files
7. **Regular updates**: Periodically run `generate` to sync config with reality
