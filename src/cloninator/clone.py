from subprocess import run

from cloninator.utils import Repo, get_config


def add_repo(repo: Repo) -> None:
    path = repo.path
    path.mkdir(parents=True, exist_ok=True)
    origin = repo.remotes[0]
    print(f"🟢 Cloning {origin.url} at {path}...")
    run(
        ["git", "clone", origin.url, path, "--origin", origin.name],  # noqa: S603, S607
        check=True,
    )
    for remote in repo.remotes[1:]:
        print(f"🟢 Adding remote {remote.name} at {remote.url} for {path}...")
        run(
            [  # noqa: S603, S607
                "git",
                "-C",
                path,
                "remote",
                "add",
                remote.name,
                remote.url,
            ],
            check=True,
        )
    post_checkout = repo.post_checkout
    print(f"🟢 Running post-checkout commands {list(post_checkout)} for {path}...")
    for command in post_checkout:
        run(command, cwd=path, shell=True, check=True)  # noqa: S602


def clone() -> None:
    config = get_config()
    for repo in config.repos:
        path = repo.path
        if path.exists() and any(path.iterdir()):
            print(f"🔵 Repo {path} already exists, skipping...")
        else:
            add_repo(repo)
