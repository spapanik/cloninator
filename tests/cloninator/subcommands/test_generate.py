from pathlib import Path
from unittest import mock

from cloninator.subcommands.generate import generate


@mock.patch("cloninator.subcommands.generate.get_config")
@mock.patch("cloninator.subcommands.generate.get_repos")
@mock.patch("cloninator.subcommands.generate.Path.open")
@mock.patch("cloninator.subcommands.generate.YAML")
def test_generate(
    mock_yaml_cls: mock.MagicMock,
    mock_open: mock.MagicMock,
    mock_get_repos: mock.MagicMock,
    mock_get_config: mock.MagicMock,
) -> None:
    mock_root = Path("/root")
    mock_config = mock.MagicMock()
    mock_config.root = mock_root
    mock_config.repos = set()
    mock_get_config.return_value = mock_config

    mock_repo = mock.MagicMock()
    mock_repo.path = mock_root.joinpath("group", "repo")
    mock_remote = mock.MagicMock()
    mock_remote.name = "origin"
    mock_remote.url = "https://github.com/user/repo.git"
    mock_repo.remotes = [mock_remote]

    mock_repos_obj = mock.MagicMock()
    mock_repos_obj.repos = {mock_repo}
    mock_get_repos.return_value = mock_repos_obj

    mock_file = mock.MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    mock_yaml = mock.MagicMock()
    mock_yaml_cls.return_value = mock_yaml

    generate()

    assert mock_get_config.call_count == 1
    assert mock_get_config.call_args_list == [mock.call(soft_info=False)]

    assert mock_get_repos.call_count == 1
    assert mock_get_repos.call_args_list == [mock.call(root=mock_root)]

    expected_data = {
        "group": {
            "repo": {
                "/remotes": [
                    {
                        "name": "origin",
                        "url": "https://github.com/user/repo.git",
                    }
                ]
            }
        }
    }
    assert mock_yaml.dump.call_count == 1
    assert mock_yaml.dump.call_args_list == [mock.call(expected_data, mock_file)]
