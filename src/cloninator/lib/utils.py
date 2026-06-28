from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dj_settings import ConfigParser

if TYPE_CHECKING:
    from collections.abc import Iterator

    from typing_extensions import Self  # upgrade: py3.10: import from typing

    from cloninator.lib.type_defs import RepoData

CONF_DIR = Path.home().joinpath(".config", "cloninator")
CONF = CONF_DIR.joinpath("config.yaml")
CONF_SUFFIX = CONF.suffix
OVERRIDE_DIR = CONF.with_suffix(f"{CONF_SUFFIX}.d")


@dataclass(frozen=True, slots=True)
class RepoGroupKey:
    name: str
    root: Path


@dataclass(frozen=True, slots=True)
class Remote:
    name: str
    url: str

    def with_prefix(self, prefix: str) -> Self:
        return self.__class__(
            name=self.name,
            url=f"{prefix}{self.url}",
        )


@dataclass(frozen=True, slots=True)
class Repo:
    path: Path
    remotes: tuple[Remote, ...]
    post_checkout: tuple[str, ...]

    def parsed(self, root: Path, prefix: str) -> Self:
        return self.__class__(
            path=root / self.path,
            remotes=tuple(remote.with_prefix(prefix) for remote in self.remotes),
            post_checkout=self.post_checkout,
        )


@dataclass(frozen=True, slots=True)
class RepoGroup:
    name: str
    root: Path
    prefix: str
    raw_repos: tuple[Repo, ...]

    @property
    def repos(self) -> Iterator[Repo]:
        yield from (
            repo.parsed(root=self.root, prefix=self.prefix) for repo in self.raw_repos
        )


@dataclass(frozen=True, slots=True)
class Config:
    groups: tuple[RepoGroup, ...]

    @property
    def repos(self) -> Iterator[Repo]:
        for group in self.groups:
            yield from group.repos


def _get_data() -> dict[str, Any]:  # type: ignore[explicit-any]
    if not CONF_DIR.exists():
        CONF_DIR.mkdir(parents=True)
    if not OVERRIDE_DIR.exists():
        OVERRIDE_DIR.mkdir()
    parsed_config = ConfigParser([CONF])
    try:
        return parsed_config.data
    except AttributeError:
        return {}


def _get_raw_repos(group_data: dict[str, RepoData]) -> Iterator[Repo]:
    for path, repo_config in group_data.items():
        if path.startswith("/"):
            continue
        yield Repo(
            path=Path(path),
            remotes=tuple(
                Remote(**remote_data) for remote_data in repo_config["/remotes"]
            ),
            post_checkout=tuple(repo_config.get("/post_checkout", [])),
        )


def get_config() -> Config:
    data = _get_data()
    repos = [
        RepoGroup(
            name=name,
            root=group_data["/root"],
            prefix=group_data.get("prefix", ""),
            raw_repos=tuple(_get_raw_repos(group_data)),
        )
        for name, group_data in data.items()
    ]

    return Config(groups=tuple(repos))
