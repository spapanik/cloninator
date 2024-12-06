from subprocess import run

from pyutilkit.term import SGRString

from cloninator.lib.utils import Repo, get_config


def add_repo(repo: Repo) -> None:
    path = repo.path
    path.mkdir(parents=True, exist_ok=True)
    origin = repo.remotes[0]
    SGRString(f"Cloning {origin.url} at {path}...", prefix="🟢 ").print()
    run(  # noqa: S603
        ["git", "clone", origin.url, path, "--origin", origin.name],  # noqa: S607
        check=True,
    )
    for remote in repo.remotes[1:]:
        SGRString(
            f"Adding remote {remote.name} at {remote.url} for {path}...", prefix="🟢 "
        ).print()
        run(  # noqa: S603
            [  # noqa: S607
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
    SGRString(
        f"Running post-checkout commands {list(post_checkout)} for {path}...",
        prefix="🟢 ",
    ).print()
    for command in post_checkout:
        run(command, cwd=path, shell=True, check=True)  # noqa: S602


def clone() -> None:
    config = get_config()
    for repo in config.repos:
        path = repo.path
        if path.exists() and any(path.iterdir()):
            SGRString(f"Repo {path} already exists, skipping...", prefix="🔵 ").print()
        else:
            add_repo(repo)
