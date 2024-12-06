from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from subprocess import run
from typing import TYPE_CHECKING, TypeGuard

from dj_settings import ConfigParser
from pyutilkit.term import SGRString

if TYPE_CHECKING:
    from collections.abc import Iterator

    from cloninator.lib.types import RepoData

CONF_DIR = Path.home().joinpath(".config", "cloninator")
CONF = CONF_DIR.joinpath("config.yaml")


@dataclass(frozen=True)
class Remote:
    name: str
    url: str


@dataclass(frozen=True)
class Repo:
    path: Path
    remotes: tuple[Remote, ...]
    post_checkout: tuple[str, ...]


@dataclass(frozen=True)
class Config:
    root: Path
    repos: frozenset[Repo]


def validate_repo(data: dict[str, object], path: Path) -> TypeGuard[RepoData]:
    error_prefix = "❌ "
    if not all(key.startswith("/") for key in data):
        SGRString(
            f"Repo info for {path} has keys that don't start with /, skipping...",
            prefix=error_prefix,
        ).print()
        return False
    if "/remotes" not in data:
        SGRString(
            f"Repo info for {path} is missing remotes info, skipping...",
            prefix=error_prefix,
        ).print()
        return False
    if not data["/remotes"]:
        SGRString(
            f"Repo info for {path} has no remotes, skipping...", prefix=error_prefix
        ).print()
        return False
    if not isinstance(data["/remotes"], list):
        SGRString(
            f"Repo info for {path} remotes are not a list, skipping...",
            prefix=error_prefix,
        ).print()
        return False
    for remote in data["/remotes"]:
        if "name" not in remote:
            SGRString(
                f"Repo info for {path} has a remote without name, skipping...",
                prefix=error_prefix,
            ).print()
            return False
        if "url" not in remote:
            SGRString(
                f"Repo info for {path} has a remote without a url, skipping...",
                prefix=error_prefix,
            ).print()
            return False
    return True


def _get_config(path: Path, data: dict[str, object]) -> Iterator[tuple[Path, RepoData]]:
    for key, value in data.items():
        if isinstance(value, dict):
            if not all(isinstance(key, str) for key in value):
                SGRString(
                    f"Repo info for {path} has a non-string key, skipping...",
                    prefix="❌ ",
                ).print()
                continue

            current_path = path.joinpath(key)
            if any(key.startswith("/") for key in value):
                if validate_repo(value, path):
                    yield current_path, value
            else:
                yield from _get_config(current_path, value)


def get_config(*, soft_info: bool = True) -> Config:
    data = ConfigParser([CONF]).data
    try:
        root = Path(data["/root"])
    except KeyError as exc:
        msg = "Root key is missing from the config file."
        raise ValueError(msg) from exc

    repos = set()
    for path, path_data in _get_config(root, data):
        post_checkout = tuple(path_data.get("/post_checkout", [])) if soft_info else ()
        repos.add(
            Repo(
                path=path,
                remotes=tuple(Remote(**remote) for remote in path_data["/remotes"]),
                post_checkout=post_checkout,
            )
        )

    return Config(root=root, repos=frozenset(repos))


def get_repos(root: Path | None = None) -> Config:
    data = ConfigParser([CONF]).data
    if root is None:
        try:
            root = Path(data["/root"])
        except KeyError as exc:
            msg = "Root key is missing from the config file."
            raise ValueError(msg) from exc

    repos = set()
    for git_dir in root.rglob(".git/"):
        path = git_dir.parent
        response = run(  # noqa: S603
            [  # noqa: S607
                "git",
                "-C",
                path,
                "config",
                "--get-regex",
                r"remote\..*\.url",
            ],
            capture_output=True,
            check=False,
        )
        if response.stderr:
            error = response.stderr.decode()
            raise ValueError(error)
        output = response.stdout.decode()
        if not output:
            SGRString(f"Repo {path} is local, skipping...", prefix="🔵 ").print()
            continue
        remotes_info = output.splitlines()
        remotes = []
        for remote in remotes_info:
            full_name, url = remote.split()
            _, name, _ = full_name.split(".")
            remotes.append(Remote(name=name, url=url))
        repos.add(Repo(path=path, remotes=tuple(remotes), post_checkout=()))

    return Config(root=root, repos=frozenset(repos))
