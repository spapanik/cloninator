from pathlib import Path
from typing import Any

from yaml import safe_dump

from cloninator.utils import get_config, get_repos


def generate() -> None:
    config = get_config(soft_info=False)
    root = config.root
    repos = get_repos(root=root)
    missing_repos = repos.repos - config.repos
    repos_dict: dict[str, Any] = {}
    for missing_repo in missing_repos:
        current_dict = repos_dict
        path = missing_repo.path.relative_to(root)
        for directory in reversed(path.parents[:-1]):
            current_dict.setdefault(directory.name, {})
            current_dict = current_dict[directory.name]
        current_dict[path.name] = {
            "/remotes": [
                {
                    "name": remote.name,
                    "url": remote.url,
                }
                for remote in missing_repo.remotes
            ]
        }
    with Path("repos.yaml").open("w") as file:
        safe_dump(repos_dict, file)
