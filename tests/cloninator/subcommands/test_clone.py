from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

from cloninator.lib.utils import Config, EnvVar, Remote, Repo, RepoGroup
from cloninator.subcommands.clone import Clone


def test_clone_add_repo_repo_already_exists(tmp_path: Path) -> None:
    repo_path = tmp_path / "existing-repo"
    repo_path.mkdir()

    repo = Repo(
        path=repo_path,
        remotes=(Remote(name="origin", url="git@github.com:user/repo.git"),),
    )

    with mock.patch("cloninator.subcommands.clone.run") as mock_run:
        Clone(verbosity=0).add_repo(repo)

    mock_run.assert_not_called()
    assert repo_path.exists()


def test_clone_add_repo_clone_new_repo(tmp_path: Path) -> None:
    repo_path = tmp_path / "new-repo"

    repo = Repo(
        path=repo_path,
        remotes=(Remote(name="origin", url="git@github.com:user/repo.git"),),
        env_vars=(EnvVar(key="KEY", value="value"),),
    )

    with mock.patch("cloninator.subcommands.clone.run") as mock_run:
        Clone(verbosity=0).add_repo(repo)

    assert mock_run.call_count == 1
    mock_run.assert_called_once_with(
        [
            "git",
            "clone",
            "git@github.com:user/repo.git",
            repo_path,
            "--origin",
            "origin",
        ],
        check=True,
        env=os.environ | {"KEY": "value"},
    )


def test_clone_add_repo_clone_with_multiple_remotes(tmp_path: Path) -> None:
    repo_path = tmp_path / "multi-remote-repo"

    repo = Repo(
        path=repo_path,
        remotes=(
            Remote(name="origin", url="git@github.com:user/repo.git"),
            Remote(name="upstream", url="git@github.com:upstream/repo.git"),
            Remote(name="fork", url="git@github.com:fork/repo.git"),
        ),
    )

    with mock.patch("cloninator.subcommands.clone.run") as mock_run:
        Clone(verbosity=0).add_repo(repo)

    assert mock_run.call_count == 3

    calls = mock_run.call_args_list
    assert calls[0] == mock.call(
        [
            "git",
            "clone",
            "git@github.com:user/repo.git",
            repo_path,
            "--origin",
            "origin",
        ],
        check=True,
        env=os.environ,
    )
    assert calls[1] == mock.call(
        [
            "git",
            "-C",
            repo_path,
            "remote",
            "add",
            "upstream",
            "git@github.com:upstream/repo.git",
        ],
        check=True,
    )
    assert calls[2] == mock.call(
        [
            "git",
            "-C",
            repo_path,
            "remote",
            "add",
            "fork",
            "git@github.com:fork/repo.git",
        ],
        check=True,
    )


def test_clone_add_repo_clone_with_post_checkout(tmp_path: Path) -> None:
    repo_path = tmp_path / "post-checkout-repo"

    repo = Repo(
        path=repo_path,
        remotes=(Remote(name="origin", url="git@github.com:user/repo.git"),),
        post_checkout=("make build", "pytest tests/"),
    )

    with mock.patch("cloninator.subcommands.clone.run") as mock_run:
        Clone(verbosity=0).add_repo(repo)

    assert mock_run.call_count == 3

    calls = mock_run.call_args_list
    assert calls[0][0][0][:2] == ["git", "clone"]

    assert calls[1] == mock.call(  # noqa: S604
        "make build", cwd=repo_path, shell=True, check=True
    )
    assert calls[2] == mock.call(  # noqa: S604
        "pytest tests/", cwd=repo_path, shell=True, check=True
    )


def test_clone_add_repo_clone_creates_parent_directories(tmp_path: Path) -> None:
    repo_path = tmp_path / "nested" / "deep" / "repo"

    repo = Repo(
        path=repo_path,
        remotes=(Remote(name="origin", url="git@github.com:user/repo.git"),),
    )

    with mock.patch("cloninator.subcommands.clone.run"):
        Clone(verbosity=0).add_repo(repo)

    assert repo_path.parent.exists()


@mock.patch("cloninator.subcommands.clone.get_config")
def test_clone_run_with_empty_config(mock_get_config: mock.MagicMock) -> None:
    mock_get_config.return_value = Config(groups=())

    clone = Clone(verbosity=0)
    with mock.patch.object(clone, "add_repo") as mock_add_repo:
        clone.run()

    mock_add_repo.assert_not_called()


@mock.patch("cloninator.subcommands.clone.get_config")
def test_clone_run_with_repos(mock_get_config: mock.MagicMock, tmp_path: Path) -> None:
    group = RepoGroup(
        name="test-group",
        root=tmp_path,
        prefix="",
        raw_repos=(
            Repo(
                path=Path("repo1"),
                remotes=(Remote(name="origin", url="url1"),),
            ),
            Repo(
                path=Path("repo2"),
                remotes=(Remote(name="origin", url="url2"),),
            ),
        ),
    )
    mock_get_config.return_value = Config(groups=(group,))

    clone = Clone(verbosity=0)
    with mock.patch.object(clone, "add_repo") as mock_add_repo:
        clone.run()

    assert mock_add_repo.call_count == 2
    assert mock_add_repo.call_args_list[0][0][0].path == tmp_path / "repo1"
    assert mock_add_repo.call_args_list[1][0][0].path == tmp_path / "repo2"


@mock.patch("cloninator.subcommands.clone.get_config")
def test_clone_run_verbosity_passed(mock_get_config: mock.MagicMock) -> None:
    mock_get_config.return_value = Config(groups=())

    clone = Clone(verbosity=2)
    assert clone.verbosity == 2

    with mock.patch.object(clone, "add_repo"):
        clone.run()
