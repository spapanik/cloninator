from __future__ import annotations

import os
from pathlib import Path
from subprocess import CalledProcessError
from unittest import mock

import pytest

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


def test_clone_add_repo_reports_attempt_then_success(tmp_path: Path) -> None:
    repo_path = tmp_path / "successful-repo"
    repo = Repo(
        path=repo_path,
        remotes=(Remote(name="origin", url="git@github.com:user/repo.git"),),
        post_checkout=("make build",),
    )

    with (
        mock.patch("cloninator.subcommands.clone.run"),
        mock.patch("cloninator.subcommands.clone.SGRString") as mock_sgr_string,
    ):
        Clone(verbosity=0).add_repo(repo)

    assert mock_sgr_string.call_args_list == [
        mock.call(
            f"Cloning git@github.com:user/repo.git at {repo_path}...",
            prefix="🟡 ",
        ),
        mock.call(
            f"Running post-checkout commands ['make build'] for {repo_path}...",
            prefix="🟡 ",
        ),
        mock.call(
            f"Cloned git@github.com:user/repo.git at {repo_path}.",
            prefix="🟢 ",
        ),
    ]


def test_clone_add_repo_does_not_report_success_when_post_checkout_fails(
    tmp_path: Path,
) -> None:
    repo_path = tmp_path / "failed-repo"
    repo = Repo(
        path=repo_path,
        remotes=(Remote(name="origin", url="git@github.com:user/repo.git"),),
        post_checkout=("make build",),
    )

    with (
        mock.patch(
            "cloninator.subcommands.clone.run",
            side_effect=(mock.DEFAULT, CalledProcessError(1, "make build")),
        ),
        mock.patch("cloninator.subcommands.clone.SGRString") as mock_sgr_string,
        pytest.raises(CalledProcessError),
    ):
        Clone(verbosity=0).add_repo(repo)

    prefixes = [call.kwargs["prefix"] for call in mock_sgr_string.call_args_list]
    assert "🟢 " not in prefixes


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
def test_clone_run_reports_failure_and_exits(
    mock_get_config: mock.MagicMock, tmp_path: Path
) -> None:
    repo = Repo(
        path=tmp_path / "failed-repo",
        remotes=(Remote(name="origin", url="url"),),
    )
    mock_get_config.return_value = Config(
        groups=(
            RepoGroup(
                name="test-group",
                root=tmp_path,
                prefix="",
                raw_repos=(repo,),
            ),
        )
    )
    clone = Clone(verbosity=0)

    with (
        mock.patch.object(
            clone, "add_repo", side_effect=CalledProcessError(1, "git clone")
        ),
        mock.patch("cloninator.subcommands.clone.SGRString") as mock_sgr_string,
        pytest.raises(SystemExit) as system_exit,
    ):
        clone.run()

    assert system_exit.value.code == 1
    mock_sgr_string.assert_called_once_with(
        f"Failed to add repo {repo.path}: "
        "Command 'git clone' returned non-zero exit status 1.",
        prefix="🔴 ",
    )
    mock_sgr_string.return_value.print.assert_called_once_with()


@mock.patch("cloninator.subcommands.clone.get_config")
def test_clone_run_verbosity_passed(mock_get_config: mock.MagicMock) -> None:
    mock_get_config.return_value = Config(groups=())

    clone = Clone(verbosity=2)
    assert clone.verbosity == 2

    with mock.patch.object(clone, "add_repo"):
        clone.run()
