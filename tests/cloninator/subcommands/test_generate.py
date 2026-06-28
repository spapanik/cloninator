from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import pytest

from cloninator.lib.utils import Config, Remote, Repo, RepoGroup, RepoGroupKey
from cloninator.subcommands.generate import Generate


def test_generate_get_repos_with_valid_git_repo(tmp_path: Path) -> None:
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()
    git_dir = repo_dir / ".git"
    git_dir.mkdir()

    repo_group_key = RepoGroupKey(name="test", root=tmp_path)

    mock_result = CompletedProcess(
        args=[],
        returncode=0,
        stdout=b"remote.origin.url git@github.com:user/repo.git\n",
        stderr=b"",
    )

    with mock.patch("cloninator.subcommands.generate.run", return_value=mock_result):
        gen = Generate(verbosity=0, repo_groups=(repo_group_key,), split_groups=False)
        repos_list = list(gen._get_repos(repo_group_key))

    assert len(repos_list) == 1
    assert repos_list[0]["repo"].path == repo_dir
    assert len(repos_list[0]["repo"].remotes) == 1
    assert repos_list[0]["repo"].remotes[0].name == "origin"
    assert repos_list[0]["repo"].remotes[0].url == "git@github.com:user/repo.git"
    assert repos_list[0]["repo_group_key"] == repo_group_key


def test_generate_get_repos_with_multiple_remotes(tmp_path: Path) -> None:
    repo_dir = tmp_path / "multi-remote-repo"
    repo_dir.mkdir()
    git_dir = repo_dir / ".git"
    git_dir.mkdir()

    repo_group_key = RepoGroupKey(name="test", root=tmp_path)

    mock_result = CompletedProcess(
        args=[],
        returncode=0,
        stdout=(
            b"remote.origin.url git@github.com:user/repo.git\n"
            b"remote.upstream.url git@github.com:upstream/repo.git\n"
        ),
        stderr=b"",
    )

    with mock.patch("cloninator.subcommands.generate.run", return_value=mock_result):
        gen = Generate(verbosity=0, repo_groups=(repo_group_key,), split_groups=False)
        repos_list = list(gen._get_repos(repo_group_key))

    assert len(repos_list) == 1
    assert len(repos_list[0]["repo"].remotes) == 2
    assert repos_list[0]["repo"].remotes[0].name == "origin"
    assert repos_list[0]["repo"].remotes[1].name == "upstream"


def test_generate_get_repos_skips_local_repos(tmp_path: Path) -> None:
    repo_dir = tmp_path / "local-repo"
    repo_dir.mkdir()
    git_dir = repo_dir / ".git"
    git_dir.mkdir()

    repo_group_key = RepoGroupKey(name="test", root=tmp_path)

    mock_result = CompletedProcess(
        args=[],
        returncode=0,
        stdout=b"",
        stderr=b"",
    )

    with mock.patch("cloninator.subcommands.generate.run", return_value=mock_result):
        gen = Generate(verbosity=0, repo_groups=(repo_group_key,), split_groups=False)
        repos_list = list(gen._get_repos(repo_group_key))

    assert len(repos_list) == 0


def test_generate_get_repos_raises_on_error(tmp_path: Path) -> None:
    repo_dir = tmp_path / "error-repo"
    repo_dir.mkdir()
    git_dir = repo_dir / ".git"
    git_dir.mkdir()

    repo_group_key = RepoGroupKey(name="test", root=tmp_path)

    with mock.patch(
        "cloninator.subcommands.generate.run",
        return_value=CompletedProcess(
            args=[],
            returncode=1,
            stdout=b"",
            stderr=b"fatal: not a git repository\n",
        ),
    ):
        gen = Generate(verbosity=0, repo_groups=(repo_group_key,), split_groups=False)
        with pytest.raises(ValueError, match="fatal: not a git repository"):
            list(gen._get_repos(repo_group_key))


def test_generate_get_repos_multiple_dirs(tmp_path: Path) -> None:
    repo1 = tmp_path / "repo1"
    repo1.mkdir()
    (repo1 / ".git").mkdir()

    repo2 = tmp_path / "repo2"
    repo2.mkdir()
    (repo2 / ".git").mkdir()

    repo_group_key = RepoGroupKey(name="test", root=tmp_path)

    def side_effect(*args: object, **kwargs: object) -> CompletedProcess[bytes]:
        path = args[1] if len(args) > 1 else kwargs.get("cwd")
        if "repo1" in str(path):
            return CompletedProcess(
                args=[],
                returncode=0,
                stdout=b"remote.origin.url url1\n",
                stderr=b"",
            )
        return CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"remote.origin.url url2\n",
            stderr=b"",
        )

    with mock.patch("cloninator.subcommands.generate.run", side_effect=side_effect):
        gen = Generate(verbosity=0, repo_groups=(repo_group_key,), split_groups=False)
        repos_list = list(gen._get_repos(repo_group_key))

    assert len(repos_list) == 2


def test_generate_write_repos_write_single_file(tmp_path: Path) -> None:
    override_dir = tmp_path / "config.d"
    override_dir.mkdir()

    repos_dict: dict[str, dict[str, object]] = {
        "group1": {
            "/root": "/repos/group1",
            "repo1": {"/remotes": [{"name": "origin", "url": "url1"}]},
        },
        "group2": {
            "/root": "/repos/group2",
            "repo2": {"/remotes": [{"name": "origin", "url": "url2"}]},
        },
    }

    with (
        mock.patch("cloninator.subcommands.generate.OVERRIDE_DIR", override_dir),
        mock.patch("cloninator.subcommands.generate.CONF_SUFFIX", ".yaml"),
    ):
        gen = Generate(verbosity=0, repo_groups=(), split_groups=False)
        gen._write_repos(repos_dict)

    yaml_files = list(override_dir.glob("*.yaml"))
    assert len(yaml_files) == 1


def test_generate_write_repos_write_separate_files_per_group(tmp_path: Path) -> None:
    override_dir = tmp_path / "config.d"
    override_dir.mkdir()

    repos_dict: dict[str, dict[str, object]] = {
        "group1": {
            "/root": "/repos/group1",
            "repo1": {"/remotes": [{"name": "origin", "url": "url1"}]},
        },
        "group2": {
            "/root": "/repos/group2",
            "repo2": {"/remotes": [{"name": "origin", "url": "url2"}]},
        },
    }

    with (
        mock.patch("cloninator.subcommands.generate.OVERRIDE_DIR", override_dir),
        mock.patch("cloninator.subcommands.generate.CONF_SUFFIX", ".yaml"),
    ):
        gen = Generate(verbosity=0, repo_groups=(), split_groups=True)
        gen._write_repos(repos_dict)

    yaml_files = list(override_dir.glob("*.yaml"))
    assert len(yaml_files) == 2


def test_generate_run_no_missing_repos() -> None:
    repo = Repo(
        path=Path("/existing/repo"),
        remotes=(Remote(name="origin", url="url"),),
        post_checkout=(),
    )
    group = RepoGroup(
        name="group",
        root=Path("/root"),
        prefix="",
        raw_repos=(repo,),
    )

    repo_group_key = RepoGroupKey(name="test", root=Path("/scan"))

    gen = Generate(
        verbosity=0,
        repo_groups=(repo_group_key,),
        split_groups=False,
    )

    with (
        mock.patch(
            "cloninator.subcommands.generate.get_config",
            return_value=Config(groups=(group,)),
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._get_repos", return_value=[]
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._write_repos"
        ) as mock_write,
    ):
        gen.run()

    mock_write.assert_not_called()


def test_generate_run_with_missing_repos(tmp_path: Path) -> None:
    existing_repo = Repo(
        path=tmp_path / "existing",
        remotes=(Remote(name="origin", url="url"),),
        post_checkout=(),
    )
    group = RepoGroup(
        name="group",
        root=tmp_path,
        prefix="",
        raw_repos=(existing_repo,),
    )

    missing_repo = Repo(
        path=tmp_path / "missing",
        remotes=(Remote(name="origin", url="new-url"),),
        post_checkout=(),
    )
    repo_group_key = RepoGroupKey(name="test-group", root=tmp_path)

    gen = Generate(
        verbosity=0,
        repo_groups=(repo_group_key,),
        split_groups=False,
    )

    mock_missing_data = [
        {"repo": missing_repo, "repo_group_key": repo_group_key},
    ]

    with (
        mock.patch(
            "cloninator.subcommands.generate.get_config",
            return_value=Config(groups=(group,)),
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._get_repos",
            return_value=mock_missing_data,
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._write_repos"
        ) as mock_write,
    ):
        gen.run()

    mock_write.assert_called_once()
    repos_dict = mock_write.call_args[0][0]
    assert "test-group" in repos_dict
    assert repos_dict["test-group"]["/root"] == str(tmp_path)


def test_generate_run_groups_repos_by_key(tmp_path: Path) -> None:
    repo1 = Repo(
        path=tmp_path / "repo1",
        remotes=(Remote(name="origin", url="url1"),),
        post_checkout=(),
    )
    repo2 = Repo(
        path=tmp_path / "repo2",
        remotes=(Remote(name="origin", url="url2"),),
        post_checkout=(),
    )

    key1 = RepoGroupKey(name="group1", root=tmp_path / "g1")
    key2 = RepoGroupKey(name="group2", root=tmp_path / "g2")

    gen = Generate(
        verbosity=0,
        repo_groups=(key1, key2),
        split_groups=True,
    )

    mock_missing_data = [
        {"repo": repo1, "repo_group_key": key1},
        {"repo": repo2, "repo_group_key": key2},
    ]

    with (
        mock.patch(
            "cloninator.subcommands.generate.get_config",
            return_value=Config(groups=()),
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._get_repos",
            return_value=mock_missing_data,
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._write_repos"
        ) as mock_write,
    ):
        gen.run()

    repos_dict = mock_write.call_args[0][0]
    assert "group1" in repos_dict
    assert "group2" in repos_dict


def test_generate_run_handles_relative_paths(tmp_path: Path) -> None:
    repo = Repo(
        path=tmp_path / "subdir" / "repo",
        remotes=(Remote(name="origin", url="url"),),
        post_checkout=(),
    )
    key = RepoGroupKey(name="group", root=tmp_path)

    gen = Generate(
        verbosity=0,
        repo_groups=(key,),
        split_groups=False,
    )

    mock_missing_data = [
        {"repo": repo, "repo_group_key": key},
    ]

    with (
        mock.patch(
            "cloninator.subcommands.generate.get_config",
            return_value=Config(groups=()),
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._get_repos",
            return_value=mock_missing_data,
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._write_repos"
        ) as mock_write,
    ):
        gen.run()

    repos_dict = mock_write.call_args[0][0]
    assert "group" in repos_dict
    group_data = repos_dict["group"]
    assert str(Path("subdir") / "repo") in group_data


def test_generate_run_handles_absolute_repo_paths(tmp_path: Path) -> None:
    absolute_path = Path("/absolute/path/to/repo")
    repo = Repo(
        path=absolute_path,
        remotes=(Remote(name="origin", url="url"),),
        post_checkout=(),
    )
    key = RepoGroupKey(name="group", root=tmp_path)

    gen = Generate(
        verbosity=0,
        repo_groups=(key,),
        split_groups=False,
    )

    mock_missing_data = [
        {"repo": repo, "repo_group_key": key},
    ]

    with (
        mock.patch(
            "cloninator.subcommands.generate.get_config",
            return_value=Config(groups=()),
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._get_repos",
            return_value=mock_missing_data,
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._write_repos"
        ) as mock_write,
    ):
        gen.run()

    repos_dict = mock_write.call_args[0][0]
    assert "group" in repos_dict


def test_generate_run_with_post_checkout(tmp_path: Path) -> None:
    repo = Repo(
        path=tmp_path / "repo",
        remotes=(Remote(name="origin", url="url"),),
        post_checkout=("make build", "pytest"),
    )
    key = RepoGroupKey(name="group", root=tmp_path)

    gen = Generate(
        verbosity=0,
        repo_groups=(key,),
        split_groups=False,
    )

    mock_missing_data = [
        {"repo": repo, "repo_group_key": key},
    ]

    with (
        mock.patch(
            "cloninator.subcommands.generate.get_config",
            return_value=Config(groups=()),
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._get_repos",
            return_value=mock_missing_data,
        ),
        mock.patch(
            "cloninator.subcommands.generate.Generate._write_repos"
        ) as mock_write,
    ):
        gen.run()

    repos_dict = mock_write.call_args[0][0]
    group_data = repos_dict["group"]
    repo_key = str(Path("repo"))
    assert repo_key in group_data
    assert "/post_checkout" in group_data[repo_key]
    assert group_data[repo_key]["/post_checkout"] == ["make build", "pytest"]
