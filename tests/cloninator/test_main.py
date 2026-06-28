import os
from argparse import Namespace
from pathlib import Path
from unittest import mock

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
