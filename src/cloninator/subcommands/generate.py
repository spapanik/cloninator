from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from yaml import safe_dump

from cloninator.lib.utils import get_config, get_repos

if TYPE_CHECKING:
    from cloninator.lib.types import DirectoryData, RepoData


def generate() -> None:
    config = get_config(soft_info=False)
    root = config.root
    repos = get_repos(root=root)
    missing_repos = repos.repos - config.repos
    repos_dict: DirectoryData = {}
    for missing_repo in missing_repos:
        current_dict = repos_dict
        path = missing_repo.path.relative_to(root)
        for directory in reversed(path.parents[:-1]):
            current_dict.setdefault(directory.name, {})
            current_dict = current_dict[directory.name]  # type: ignore[assignment]
        repo_data: RepoData = {
            "/remotes": [
                {
                    "name": remote.name,
                    "url": remote.url,
                }
                for remote in missing_repo.remotes
            ]
        }
        current_dict[path.name] = repo_data
    with Path("repos.yaml").open("w") as file:
        safe_dump(repos_dict, file)
