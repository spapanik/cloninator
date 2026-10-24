import os
from subprocess import run

from pyutilkit.term import SGRString

from cloninator.lib.utils import Repo, get_config
from cloninator.subcommands.base import BaseSubcommand


class Clone(BaseSubcommand):
    def __init__(self, verbosity: int, *, dry_run: bool = False) -> None:
        super().__init__(verbosity=verbosity)
        self.dry_run = dry_run

    def add_repo(self, repo: Repo) -> None:
        path = repo.path
        if path.exists():
            SGRString(f"Repo {path} already exists, skipping...", prefix="🔵 ").print()
            return

        if self.dry_run:
            origin = repo.remotes[0]
            SGRString(
                f"Would clone {origin.url} at {path} with origin {origin.name}.",
                prefix="🔵 ",
            ).print()
            for remote in repo.remotes[1:]:
                SGRString(
                    f"Would add remote {remote.name} at {remote.url} for {path}.",
                    prefix="🔵 ",
                ).print()
            for command in repo.post_checkout:
                SGRString(
                    f"Would run post-checkout command {command!r} for {path}.",
                    prefix="🔵 ",
                ).print()
            return

        path.mkdir(parents=True)
        origin = repo.remotes[0]
        env = os.environ | repo.get_env()
        SGRString(f"Cloning {origin.url} at {path}...", prefix="🟡 ").print()
        run(  # noqa: S603
            ["git", "clone", origin.url, path, "--origin", origin.name],  # noqa: S607
            check=True,
            env=env,
        )
        for remote in repo.remotes[1:]:
            SGRString(
                f"Adding remote {remote.name} at {remote.url} for {path}...",
                prefix="🟡 ",
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
            prefix="🟡 ",
        ).print()
        for command in post_checkout:
            run(command, cwd=path, shell=True, check=True)  # noqa: S602
        SGRString(f"Cloned {origin.url} at {path}.", prefix="🟢 ").print()

    def _add_repo_or_exit(self, repo: Repo) -> None:
        try:
            self.add_repo(repo)
        except Exception as error:
            SGRString(f"Failed to add repo {repo.path}: {error}", prefix="🔴 ").print()
            raise SystemExit(1) from error

    def run(self) -> None:
        config = get_config(dry_run=self.dry_run)
        for repo in config.repos:
            self._add_repo_or_exit(repo)
