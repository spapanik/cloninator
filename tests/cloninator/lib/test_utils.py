from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from cloninator.lib.utils import (
    Config,
    Remote,
    Repo,
    RepoGroup,
    RepoGroupKey,
    _get_data,
    _get_raw_repos,
    get_config,
)

if TYPE_CHECKING:
    from cloninator.lib.type_defs import RepoData


def test_repo_group_key_creation() -> None:
    key = RepoGroupKey(name="test-group", root=Path("/repos"))
    assert key.name == "test-group"
    assert key.root == Path("/repos")


def test_repo_group_key_immutability() -> None:
    key = RepoGroupKey(name="test", root=Path("/root"))
    with pytest.raises(AttributeError):
        key.name = "modified"  # type: ignore[misc]


def test_remote_creation() -> None:
    remote = Remote(name="origin", url="git@github.com:user/repo.git")
    assert remote.name == "origin"
    assert remote.url == "git@github.com:user/repo.git"


def test_remote_with_prefix() -> None:
    remote = Remote(name="origin", url="github.com:user/repo.git")
    prefixed = remote.with_prefix("https://")
    assert prefixed.name == "origin"
    assert prefixed.url == "https://github.com:user/repo.git"
    assert remote.url == "github.com:user/repo.git"


def test_remote_with_prefix_empty() -> None:
    remote = Remote(name="origin", url="git@github.com:user/repo.git")
    prefixed = remote.with_prefix("")
    assert prefixed.url == "git@github.com:user/repo.git"


def test_repo_creation() -> None:
    repo = Repo(
        path=Path("my-repo"),
        remotes=(Remote(name="origin", url="git@github.com:user/repo.git"),),
        post_checkout=("make build",),
    )
    assert repo.path == Path("my-repo")
    assert len(repo.remotes) == 1
    assert repo.post_checkout == ("make build",)


def test_repo_parsed() -> None:
    repo = Repo(
        path=Path("subdir/repo"),
        remotes=(
            Remote(name="origin", url="github.com:user/repo.git"),
            Remote(name="upstream", url="github.com:upstream/repo.git"),
        ),
        post_checkout=("echo done",),
    )
    root = Path("/home/user/repos")
    parsed = repo.parsed(root=root, prefix="https://")

    assert parsed.path == Path("/home/user/repos/subdir/repo")
    assert len(parsed.remotes) == 2
    assert parsed.remotes[0].url == "https://github.com:user/repo.git"
    assert parsed.remotes[1].url == "https://github.com:upstream/repo.git"
    assert parsed.post_checkout == ("echo done",)


def test_repo_parsed_no_remotes() -> None:
    repo = Repo(path=Path("repo"), remotes=(), post_checkout=())
    parsed = repo.parsed(root=Path("/root"), prefix="ssh://")
    assert parsed.remotes == ()


def test_repo_group_creation() -> None:
    group = RepoGroup(
        name="my-group",
        root=Path("/repos"),
        prefix="https://",
        raw_repos=(
            Repo(
                path=Path("repo1"),
                remotes=(Remote(name="origin", url="github.com:user/repo1.git"),),
                post_checkout=(),
            ),
        ),
    )
    assert group.name == "my-group"
    assert group.root == Path("/repos")
    assert group.prefix == "https://"


def test_repo_group_repos_property() -> None:
    raw_repo = Repo(
        path=Path("repo1"),
        remotes=(Remote(name="origin", url="github.com:user/repo1.git"),),
        post_checkout=("cd repo1 && make",),
    )
    group = RepoGroup(
        name="group",
        root=Path("/base"),
        prefix="https://",
        raw_repos=(raw_repo,),
    )

    repos_list = list(group.repos)
    assert len(repos_list) == 1
    assert repos_list[0].path == Path("/base/repo1")
    assert repos_list[0].remotes[0].url == "https://github.com:user/repo1.git"
    assert repos_list[0].post_checkout == ("cd repo1 && make",)


def test_repo_group_repos_multiple_groups() -> None:
    group = RepoGroup(
        name="group",
        root=Path("/base"),
        prefix="",
        raw_repos=(
            Repo(
                path=Path("repo1"),
                remotes=(Remote(name="origin", url="url1"),),
                post_checkout=(),
            ),
            Repo(
                path=Path("repo2"),
                remotes=(Remote(name="origin", url="url2"),),
                post_checkout=(),
            ),
        ),
    )
    repos_list = list(group.repos)
    assert len(repos_list) == 2
    assert repos_list[0].path == Path("/base/repo1")
    assert repos_list[1].path == Path("/base/repo2")


def test_config_creation() -> None:
    config = Config(groups=())
    assert config.groups == ()


def test_config_repos_property_empty() -> None:
    config = Config(groups=())
    repos_list = list(config.repos)
    assert repos_list == []


def test_config_repos_property_with_groups() -> None:
    group1 = RepoGroup(
        name="g1",
        root=Path("/r1"),
        prefix="",
        raw_repos=(
            Repo(
                path=Path("repo1"),
                remotes=(Remote(name="origin", url="url1"),),
                post_checkout=(),
            ),
        ),
    )
    group2 = RepoGroup(
        name="g2",
        root=Path("/r2"),
        prefix="",
        raw_repos=(
            Repo(
                path=Path("repo2"),
                remotes=(Remote(name="origin", url="url2"),),
                post_checkout=(),
            ),
        ),
    )
    config = Config(groups=(group1, group2))
    repos_list = list(config.repos)
    assert len(repos_list) == 2
    assert repos_list[0].path == Path("/r1/repo1")
    assert repos_list[1].path == Path("/r2/repo2")


def test_get_raw_repos_basic_repo_creation() -> None:
    group_data: dict[str, RepoData] = {
        "my-repo": {
            "/remotes": [{"name": "origin", "url": "git@github.com:user/repo.git"}],
        },
    }
    repos = list(_get_raw_repos(group_data))
    assert len(repos) == 1
    assert repos[0].path == Path("my-repo")
    assert repos[0].remotes[0].name == "origin"
    assert repos[0].post_checkout == ()


def test_get_raw_repos_skip_absolute_paths() -> None:
    group_data: dict[str, RepoData] = {
        "/absolute/path": {
            "/remotes": [{"name": "origin", "url": "url"}],
        },
        "relative/path": {
            "/remotes": [{"name": "origin", "url": "url"}],
        },
    }
    repos = list(_get_raw_repos(group_data))
    assert len(repos) == 1
    assert repos[0].path == Path("relative/path")


def test_get_raw_repos_multiple_remotes() -> None:
    group_data: dict[str, RepoData] = {
        "repo": {
            "/remotes": [
                {"name": "origin", "url": "url1"},
                {"name": "upstream", "url": "url2"},
            ],
        },
    }
    repos = list(_get_raw_repos(group_data))
    assert len(repos) == 1
    assert len(repos[0].remotes) == 2
    assert repos[0].remotes[0].name == "origin"
    assert repos[0].remotes[1].name == "upstream"


def test_get_raw_repos_with_post_checkout() -> None:
    group_data: dict[str, RepoData] = {
        "repo": {
            "/remotes": [{"name": "origin", "url": "url"}],
            "/post_checkout": ["make build", "pytest"],
        },
    }
    repos = list(_get_raw_repos(group_data))
    assert len(repos) == 1
    assert repos[0].post_checkout == ("make build", "pytest")


def test_get_raw_repos_empty_post_checkout() -> None:
    group_data: dict[str, RepoData] = {
        "repo": {
            "/remotes": [{"name": "origin", "url": "url"}],
        },
    }
    repos = list(_get_raw_repos(group_data))
    assert repos[0].post_checkout == ()


def test_get_raw_repos_multiple_repos() -> None:
    group_data: dict[str, RepoData] = {
        "repo1": {
            "/remotes": [{"name": "origin", "url": "url1"}],
        },
        "repo2": {
            "/remotes": [{"name": "origin", "url": "url2"}],
        },
    }
    repos = list(_get_raw_repos(group_data))
    assert len(repos) == 2
    assert repos[0].path == Path("repo1")
    assert repos[1].path == Path("repo2")


@mock.patch("cloninator.lib.utils._get_data")
def test_get_config_empty_config(mock_get_data: mock.MagicMock) -> None:
    mock_get_data.return_value = {}
    config = get_config()
    assert config.groups == ()
    assert list(config.repos) == []


@mock.patch("cloninator.lib.utils._get_data")
def test_get_config_single_group(mock_get_data: mock.MagicMock) -> None:
    repo_data: RepoData = {
        "/remotes": [{"name": "origin", "url": "git@github.com:user/repo1.git"}],
    }
    mock_get_data.return_value = {
        "my-group": {
            "/root": Path("/home/user/repos"),
            "repo1": repo_data,
        },
    }
    config = get_config()
    assert len(config.groups) == 1
    assert config.groups[0].name == "my-group"
    assert config.groups[0].root == Path("/home/user/repos")
    assert len(list(config.groups[0].raw_repos)) == 1


@mock.patch("cloninator.lib.utils._get_data")
def test_get_config_multiple_groups(mock_get_data: mock.MagicMock) -> None:
    repo_data1: RepoData = {"/remotes": [{"name": "origin", "url": "url1"}]}
    repo_data2: RepoData = {"/remotes": [{"name": "origin", "url": "url2"}]}
    mock_get_data.return_value = {
        "group1": {
            "/root": Path("/repos/group1"),
            "repo1": repo_data1,
        },
        "group2": {
            "/root": Path("/repos/group2"),
            "repo2": repo_data2,
        },
    }
    config = get_config()
    assert len(config.groups) == 2
    assert config.groups[0].name == "group1"
    assert config.groups[1].name == "group2"


@mock.patch("cloninator.lib.utils._get_data")
def test_get_config_group_with_prefix_in_repo_group(
    mock_get_data: mock.MagicMock,
) -> None:
    repo_data: RepoData = {
        "/remotes": [{"name": "origin", "url": "github.com:user/repo.git"}],
    }
    mock_get_data.return_value = {
        "group": {
            "/root": Path("/repos"),
            "/prefix": "https://",
            "repo": repo_data,
        },
    }
    config = get_config()
    assert config.groups[0].prefix == "https://"

    repos = list(config.repos)
    assert repos[0].remotes[0].url == "https://github.com:user/repo.git"


@mock.patch("cloninator.lib.utils._get_data")
def test_get_config_group_without_prefix(mock_get_data: mock.MagicMock) -> None:
    repo_data: RepoData = {"/remotes": [{"name": "origin", "url": "url"}]}
    mock_get_data.return_value = {
        "group": {
            "/root": Path("/repos"),
            "repo": repo_data,
        },
    }
    config = get_config()
    assert config.groups[0].prefix == ""


def test_get_data_conf_dir_creation(tmp_path: Path) -> None:
    conf_dir = tmp_path / ".config" / "cloninator"
    override_dir = conf_dir.with_suffix(f"{conf_dir.suffix}.d")

    with (
        mock.patch("cloninator.lib.utils.CONF_DIR", conf_dir),
        mock.patch("cloninator.lib.utils.OVERRIDE_DIR", override_dir),
        mock.patch("cloninator.lib.utils.CONF", conf_dir / "config.yaml"),
    ):
        result = _get_data()
        assert conf_dir.exists()
        assert override_dir.exists()
        assert result == {}


@mock.patch("cloninator.lib.utils.ConfigParser")
def test_get_data_with_config_data(
    mock_parser_class: mock.MagicMock, tmp_path: Path
) -> None:
    mock_instance = mock.MagicMock()
    mock_instance.data = {"group": {"/root": "/repos"}}
    mock_parser_class.return_value = mock_instance

    conf_dir = tmp_path / ".config" / "cloninator"
    conf_dir.mkdir(parents=True)
    override_dir = conf_dir.with_suffix(f"{conf_dir.suffix}.d")
    override_dir.mkdir()

    with (
        mock.patch("cloninator.lib.utils.CONF_DIR", conf_dir),
        mock.patch("cloninator.lib.utils.OVERRIDE_DIR", override_dir),
        mock.patch("cloninator.lib.utils.CONF", conf_dir / "config.yaml"),
    ):
        result = _get_data()
        assert result == {"group": {"/root": "/repos"}}


@mock.patch("cloninator.lib.utils.ConfigParser")
def test_get_data_attribute_error_returns_empty(
    mock_parser_class: mock.MagicMock, tmp_path: Path
) -> None:
    mock_instance = mock.MagicMock()
    del mock_instance.data
    mock_parser_class.return_value = mock_instance

    conf_dir = tmp_path / ".config" / "cloninator"
    conf_dir.mkdir(parents=True)
    override_dir = conf_dir.with_suffix(f"{conf_dir.suffix}.d")
    override_dir.mkdir()

    with (
        mock.patch("cloninator.lib.utils.CONF_DIR", conf_dir),
        mock.patch("cloninator.lib.utils.OVERRIDE_DIR", override_dir),
        mock.patch("cloninator.lib.utils.CONF", conf_dir / "config.yaml"),
    ):
        result = _get_data()
        assert result == {}
