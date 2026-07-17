from __future__ import annotations

from subprocess import run
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from pyutilkit.term import SGRString
from ruamel.yaml import YAML

from cloninator.lib.utils import (
    CONF_SUFFIX,
    OVERRIDE_DIR,
    Remote,
    Repo,
    RepoGroupKey,
    get_config,
)
from cloninator.subcommands.base import BaseSubcommand

if TYPE_CHECKING:
    from collections.abc import Iterator

    from cloninator.lib.type_defs import RepoData, RepoGroupData


class Generate(BaseSubcommand):
    __slots__ = ("repo_groups", "split_groups")

    def __init__(
        self,
        verbosity: int,
        *,
        repo_groups: tuple[RepoGroupKey, ...],
        split_groups: bool,
    ) -> None:
        super().__init__(verbosity=verbosity)
        self.repo_groups = repo_groups
        self.split_groups = split_groups

    @staticmethod
    def _get_repos(repo_group: RepoGroupKey) -> Iterator[RepoGroupData]:
        for git_dir in repo_group.root.rglob(".git/"):
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
            yield {
                "repo": Repo(path=path, remotes=tuple(remotes)),
                "repo_group_key": repo_group,
            }

    def _write_repos(self, repos_dict: dict[str, dict[str, object]]) -> None:
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)

        if not self.split_groups:
            # Write all repos to a single file
            with NamedTemporaryFile(
                mode="w",
                dir=OVERRIDE_DIR,
                prefix="new_repos_",
                suffix=CONF_SUFFIX,
                delete=False,
            ) as f:
                yaml.dump(repos_dict, f)
                SGRString(f"Generated config: {f.name}", prefix="✅ ").print()
        else:
            # Write separate file per repo group
            for group_name, group_data in repos_dict.items():
                with NamedTemporaryFile(
                    mode="w",
                    dir=OVERRIDE_DIR,
                    prefix=f"{group_name}_",
                    suffix=CONF_SUFFIX,
                    delete=False,
                ) as f:
                    yaml.dump({group_name: group_data}, f)
                    SGRString(
                        f"Generated config for '{group_name}': {f.name}",
                        prefix="✅ ",
                    ).print()

    def run(self) -> None:
        config = get_config()
        repos = {repo.path for repo in config.repos}

        missing_repos = [
            repo_group_data
            for repo_group_key in self.repo_groups
            for repo_group_data in self._get_repos(repo_group_key)
            if repo_group_data["repo"].path not in repos
        ]

        if not missing_repos:
            SGRString("All scanned repos are already in config.", prefix="🔵 ").print()
            return

        # Group missing repos by their repo_group_key
        grouped_repos: dict[RepoGroupKey, list[Repo]] = {}
        for missing_repo in missing_repos:
            key = missing_repo["repo_group_key"]
            if key not in grouped_repos:
                grouped_repos[key] = []
            grouped_repos[key].append(missing_repo["repo"])

        # Build repos_dict with proper structure for YAML output
        repos_dict: dict[str, dict[str, object]] = {}
        for group_key, repo_list in grouped_repos.items():
            repos_dict[group_key.name] = {
                "/root": str(group_key.root),
            }
            for repo in repo_list:
                try:
                    rel_path = repo.path.relative_to(group_key.root)
                except ValueError:
                    rel_path = repo.path

                repo_data: RepoData = {
                    "/remotes": [
                        {"name": remote.name, "url": remote.url}
                        for remote in repo.remotes
                    ]
                }
                if repo.post_checkout:
                    repo_data["/post_checkout"] = list(repo.post_checkout)

                repos_dict[group_key.name][str(rel_path)] = repo_data

        self._write_repos(repos_dict)
