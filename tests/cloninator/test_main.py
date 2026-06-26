from unittest import mock

from cloninator.__main__ import main
from cloninator.lib.cli import CliArgs, CloneCliArgs, GenerateCliArgs


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
            verbosity=0, clone_subcommand=None, generate_subcommand=GenerateCliArgs()
        )
    ),
)
@mock.patch("cloninator.subcommands.generate.Generate.run")
def test_generate(mock_run: mock.MagicMock) -> None:
    main()
    assert mock_run.call_count == 1
    calls = [mock.call()]
    assert mock_run.call_args_list == calls
