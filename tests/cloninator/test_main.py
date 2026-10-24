import os
from argparse import Namespace
from pathlib import Path
from unittest import mock

import pytest

from cloninator.__main__ import main
from cloninator.lib.cli import CliArgs, CloneCliArgs, GenerateCliArgs
from cloninator.lib.utils import RepoGroupKey


@mock.patch(
    "cloninator.__main__.parse_args",
    new=mock.MagicMock(
        return_value=CliArgs(
            verbosity=0, clone_subcommand=CloneCliArgs(), generate_subcommand=None
        )
    ),
)
@mock.patch("cloninator.subcommands.clone.Clone.run")
def test_clone(mock_run: mock.MagicMock) -> None:
    main()
    assert mock_run.call_count == 1
    calls = [mock.call()]
    assert mock_run.call_args_list == calls


@mock.patch(
    "cloninator.__main__.parse_args",
    new=mock.MagicMock(
        return_value=CliArgs(
            verbosity=0,
            clone_subcommand=None,
            generate_subcommand=GenerateCliArgs(
                repo_groups=(RepoGroupKey(name="", root=Path(os.devnull)),),
                split_groups=True,
            ),
        )
    ),
)
@mock.patch("cloninator.subcommands.generate.Generate.run")
def test_generate(mock_run: mock.MagicMock) -> None:
    main()
    assert mock_run.call_count == 1
    calls = [mock.call()]
    assert mock_run.call_args_list == calls


def test_cli_args_from_args_with_unknown_subcommand() -> None:
    args = Namespace(subcommand="unknown", verbosity=0)
    cli_args = CliArgs.from_args(args)
    assert cli_args.clone_subcommand is None
    assert cli_args.generate_subcommand is None
    assert cli_args.verbosity == 0


@mock.patch(
    "cloninator.__main__.parse_args",
    new=mock.MagicMock(
        return_value=CliArgs(
            verbosity=0, clone_subcommand=None, generate_subcommand=None
        )
    ),
)
def test_main_with_no_subcommand() -> None:
    # This tests the implicit else branch in main()
    # In practice this shouldn't happen due to argparse validation
    main()  # Should just return without doing anything


@pytest.mark.parametrize("subcommand", ["clone", "generate"])
@pytest.mark.parametrize("flag", ["--dry-run", "-n"])
def test_main_dry_run_without_config(
    tmp_path: Path, subcommand: str, flag: str
) -> None:
    conf_dir = tmp_path / "config"
    argv = ["cloninator", subcommand, flag]
    if subcommand == "generate":
        argv.extend(["-r", f"group::{tmp_path}"])
    with (
        mock.patch("sys.argv", argv),
        mock.patch("cloninator.lib.utils.CONF_DIR", conf_dir),
        mock.patch("cloninator.lib.utils.CONF", conf_dir / "config.yaml"),
        mock.patch("cloninator.lib.utils.OVERRIDE_DIR", conf_dir / "config.yaml.d"),
    ):
        main()
    assert not conf_dir.exists()


@pytest.mark.parametrize("subcommand", ["clone", "generate"])
def test_main_passes_dry_run(subcommand: str) -> None:
    argv = ["cloninator", subcommand, "-n"]
    if subcommand == "generate":
        argv.extend(["-r", "group::/repos"])
    with (
        mock.patch("sys.argv", argv),
        mock.patch(f"cloninator.__main__.{subcommand.title()}") as mock_command,
    ):
        main()
    assert mock_command.call_args.kwargs["dry_run"] is True
    mock_command.return_value.run.assert_called_once_with()
