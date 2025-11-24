from pathlib import Path
from unittest import mock

from cloninator.subcommands.clone import add_repo, clone


@mock.patch("cloninator.subcommands.clone.get_config")
@mock.patch("cloninator.subcommands.clone.add_repo")
@mock.patch("cloninator.subcommands.clone.SGRString")
def test_clone_new_repo(
    mock_sgr: mock.MagicMock,
    mock_add_repo: mock.MagicMock,
    mock_get_config: mock.MagicMock,
) -> None:
    mock_repo = mock.MagicMock()

    mock_path = mock.MagicMock(spec=Path)
    mock_path.exists.return_value = False
    mock_repo.path = mock_path

    mock_get_config.return_value.repos = [mock_repo]

    clone()

    assert mock_add_repo.call_count == 1
    assert mock_add_repo.call_args_list == [mock.call(mock_repo)]
    assert mock_sgr.call_count == 0


@mock.patch("cloninator.subcommands.clone.get_config")
@mock.patch("cloninator.subcommands.clone.add_repo")
@mock.patch("cloninator.subcommands.clone.SGRString")
def test_clone_existing_repo(
    mock_sgr: mock.MagicMock,
    mock_add_repo: mock.MagicMock,
    mock_get_config: mock.MagicMock,
) -> None:
    mock_repo = mock.MagicMock()

    mock_path = mock.MagicMock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.iterdir.return_value = [Path("file")]
    mock_repo.path = mock_path

    mock_get_config.return_value.repos = [mock_repo]

    clone()

    assert mock_add_repo.call_count == 0
    assert mock_sgr.call_count == 1
    assert mock_sgr.return_value.print.call_count == 1


@mock.patch("cloninator.subcommands.clone.run")
@mock.patch("cloninator.subcommands.clone.SGRString", new=mock.MagicMock())
def test_add_repo(mock_run: mock.MagicMock) -> None:
    mock_repo = mock.MagicMock()
    mock_path = mock.MagicMock(spec=Path)
    mock_repo.path = mock_path
    mock_origin = mock.MagicMock()
    mock_origin.name = "origin"
    mock_origin.url = "https://github.com/user/repo.git"
    mock_upstream = mock.MagicMock()
    mock_upstream.name = "upstream"
    mock_upstream.url = "https://github.com/upstream/repo.git"
    mock_repo.remotes = [mock_origin, mock_upstream]
    mock_repo.post_checkout = ["echo hello"]

    add_repo(mock_repo)

    assert mock_path.mkdir.call_count == 1
    assert mock_path.mkdir.call_args_list == [mock.call(parents=True, exist_ok=True)]

    assert mock_run.call_count == 3
    expected_calls = [
        mock.call(
            [
                "git",
                "clone",
                "https://github.com/user/repo.git",
                mock_path,
                "--origin",
                "origin",
            ],
            check=True,
        ),
        mock.call(
            [
                "git",
                "-C",
                mock_path,
                "remote",
                "add",
                "upstream",
                "https://github.com/upstream/repo.git",
            ],
            check=True,
        ),
        mock.call(  # noqa: S604
            "echo hello", cwd=mock_path, shell=True, check=True
        ),
    ]
    assert mock_run.call_args_list == expected_calls
