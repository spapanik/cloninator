# Examples

This page provides real-world examples of cloninator configurations.

## Example 1: Simple Personal Project

A basic configuration for a single repository:

```yaml
/root: ~/projects

myapp:
    /remotes:
        - name: origin
          url: git@github.com:user/myapp.git
```

This creates: `~/projects/myapp`

## Example 2: Multiple Remotes (Fork Workflow)

Configure both your fork and the upstream repository:

```yaml
/root: ~/projects

forked-project:
    /remotes:
        - name: origin
          url: git@github.com:user/fork.git
        - name: upstream
          url: git@github.com:original/project.git
```

This allows you to easily push to your fork and pull from upstream:

```bash
cd ~/projects/forked-project
git push origin main      # Push to your fork
git pull upstream main    # Pull from original repo
```

## Example 3: With Post-Checkout Commands

Automate dependency installation after cloning:

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

Post-checkout commands are useful for:

- Installing dependencies (`pip install`, `npm install`, `bundle install`)
- Setting up virtual environments
- Running build scripts
- Initializing submodules

## Example 4: Nested Directory Structure

Organize repositories hierarchically:

```yaml
/root: ~/projects

work:
    backend:
        api-service:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/api.git
        auth-service:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/auth.git
    frontend:
        web-app:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/web.git
        mobile-app:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/mobile.git

personal:
    side-project:
        /remotes:
            - name: origin
              url: git@github.com:user/side-project.git
```

This creates the following structure:

```
~/projects/
├── work/
│   ├── backend/
│   │   ├── api-service/
│   │   └── auth-service/
│   └── frontend/
│       ├── web-app/
│       └── mobile-app/
└── personal/
    └── side-project/
```

## Example 5: Split Configuration

Split your configuration across multiple files for better organization:

**Main config** (`~/.config/cloninator/config.yaml`):

```yaml
/root: ~/projects
```

**Personal repos** (`~/.config/cloninator/config.yaml.d/personal.yaml`):

```yaml
personal:
    myproject:
        /remotes:
            - name: origin
              url: git@github.com:user/myproject.git
    blog:
        /remotes:
            - name: origin
              url: git@github.com:user/blog.git
```

**Work repos** (`~/.config/cloninator/config.yaml.d/work.yaml`):

```yaml
work:
    company-repo:
        /remotes:
            - name: origin
              url: git@gitlab.com:company/repo.git
```

All YAML files are automatically merged, allowing you to:

- Keep personal and work configs separate
- Use different files for different projects
- Share common configs across machines

## Example 6: Using Prefix for URL Shortening

Use the `/prefix` feature to shorten remote URLs:

```yaml
/root: ~/projects
/prefix: "git@gitlab.com:"

work:
    company-repo:
        /remotes:
            - name: origin
              url: username/repo.git # Becomes git@gitlab.com:username/repo.git
            - name: upstream
              url: team/repo.git # Becomes git@gitlab.com:team/repo.git
```

This is especially useful when all your repositories are on the same hosting service.

## Example 7: Complex Real-World Setup

A comprehensive configuration combining multiple features:

```yaml
/root: ~/dev
/prefix: "https://github.com/"

open-source:
    contributions:
        framework-pr:
            /remotes:
                - name: origin
                  url: user/framework.git
                - name: upstream
                  url: framework/framework.git
            /post_checkout:
                - npm install
                - npm run build

    own-projects:
        mylib:
            /remotes:
                - name: origin
                  url: user/mylib.git
            /post_checkout:
                - python -m venv .venv
                - . .venv/bin/activate && pip install -e ".[dev]"

work:
    microservices:
        api-gateway:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/api-gateway.git
                - name: staging
                  url: git@gitlab.com:company-staging/api-gateway.git
            /post_checkout:
                - docker-compose up -d

        user-service:
            /remotes:
                - name: origin
                  url: git@gitlab.com:company/user-service.git
```

## Tips

- **Start simple**: Begin with a basic config and add complexity as needed
- **Use split configs**: Separate personal and work repos into different files
- **Leverage generate**: Use `cloninator generate` to bootstrap configs from existing repos
- **Test post-checkout**: Ensure commands work before adding them to config
- **Use prefix**: If all repos share a common URL prefix, use `/prefix` to avoid repetition
