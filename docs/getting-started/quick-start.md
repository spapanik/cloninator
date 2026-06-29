# Quick Start

This guide will help you get started with cloninator in just a few minutes.

## Step 1: Create Configuration Directory

```bash
mkdir -p ~/.config/cloninator
```

## Step 2: Create Your First Configuration

Create a file at `~/.config/cloninator/config.yaml`:

```yaml
/root: ~/projects

personal:
    myproject:
        /remotes:
            - name: origin
              url: git@github.com:user/myproject.git
```

Replace `user/myproject` with your actual GitHub username and repository.

## Step 3: Clone Your Repositories

```bash
cloninator clone
```

You should see output like:

```
🟢 Cloning git@github.com:user/myproject.git at ~/projects/personal/myproject...
```

## Step 4: Verify

Check that your repository was cloned:

```bash
ls ~/projects/personal/myproject
cd ~/projects/personal/myproject
git remote -v
```

## What's Next?

- Learn about [configuration options](../guide/configuration.md)
- See more [examples](../guide/examples.md)
- Explore [common workflows](../guide/workflows.md)
