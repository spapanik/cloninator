from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import Required  # upgrade: py3.10: import from typing

if TYPE_CHECKING:
    from cloninator.lib.utils import Repo, RepoGroupKey


class RemoteData(TypedDict):
    name: str
    url: str


RepoData = TypedDict(
    "RepoData",
    {
        "/remotes": Required[list[RemoteData]],
        "/post_checkout": list[str],
        "/checkout_env_vars": dict[str, str],
    },
    total=False,
)


class RepoGroupData(TypedDict):
    repo: Repo
    repo_group_key: RepoGroupKey
