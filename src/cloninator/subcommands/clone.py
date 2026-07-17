import os
from subprocess import run

from pyutilkit.term import SGRString

from cloninator.lib.utils import Repo, get_config
from cloninator.subcommands.base import BaseSubcommand


class Clone(BaseSubcommand):
    @staticmethod
    def add_repo(repo: Repo) -> None:
        path = repo.path
        if path.exists():
            SGRString(f"Repo {path} already exists, skipping...", prefix="🔵 ").print()
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
        config = get_config()
        for repo in config.repos:
            self._add_repo_or_exit(repo)
