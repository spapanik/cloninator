from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from subprocess import run
from typing import Any

from dj_settings import ConfigParser

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


def validate_repo(path: Path, data: dict[str, Any]) -> str:
    if not all(key.startswith("/") for key in data):
        return f"❌ Repo info for {path} has keys that don't start with /, skipping..."
    if "/remotes" not in data:
        return f"❌ Repo info for {path} is missing remotes info, skipping..."
    if not data["/remotes"]:
        return f"❌ Repo info for {path} has no remotes, skipping..."
    for remote in data["/remotes"]:
        if "name" not in remote:
            return f"❌ Repo info for {path} has a remote without name, skipping..."
        if "url" not in remote:
            return f"❌ Repo info for {path} has a remote without a url, skipping..."
    return ""


def _get_config(
    path: Path, data: dict[str, Any]
) -> Iterator[tuple[Path, dict[str, Any]]]:
    for key, value in data.items():
        if isinstance(value, dict):
            if any(key.startswith("/") for key in value):
                yield path.joinpath(key), value
            else:
                yield from _get_config(path.joinpath(key), value)


def get_config(*, soft_info: bool = True) -> Config:
    data = ConfigParser([CONF]).data
    try:
        root = Path(data["/root"])
    except KeyError as exc:
        msg = "Root key is missing from the config file."
        raise ValueError(msg) from exc

    repos = set()
    for path, path_data in _get_config(root, data):
        if error_message := validate_repo(path, path_data):
            print(error_message)
        else:
            if soft_info:
                post_checkout = tuple(path_data.get("/post_checkout", []))
            else:
                post_checkout = ()
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
        response = run(
            [  # noqa: S603, S607
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
            print(f"🔵 Repo {path} is local, skipping...")
            continue
        remotes_info = output.splitlines()
        remotes = []
        for remote in remotes_info:
            full_name, url = remote.split()
            _, name, _ = full_name.split(".")
            remotes.append(Remote(name=name, url=url))
        repos.add(Repo(path=path, remotes=tuple(remotes), post_checkout=()))

    return Config(root=root, repos=frozenset(repos))
