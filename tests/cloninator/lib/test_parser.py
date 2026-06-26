from unittest import mock

import pytest

from cloninator.lib.cli import parse_args


@pytest.mark.parametrize(
    ("subcommand", "verbose", "expected_command", "expected_verbosity"),
    [
        ("clone", "-v", "clone_subcommand", 1),
        ("generate", "-vv", "generate_subcommand", 2),
        ("generate", "-vvvvv", "generate_subcommand", 5),
    ],
)
def test_cloninator_verbose(
    subcommand: str, verbose: str, expected_command: str, expected_verbosity: int
) -> None:
    with mock.patch("sys.argv", ["cloninator", subcommand, verbose]):
        args = parse_args()

    assert getattr(args, expected_command) is not None
    assert args.verbosity == expected_verbosity


@pytest.mark.parametrize(
    ("subcommand", "expected_command"),
    [
        ("clone", "clone_subcommand"),
        ("generate", "generate_subcommand"),
    ],
)
def test_cloninator(subcommand: str, expected_command: str) -> None:
    with mock.patch("sys.argv", ["cloninator", subcommand]):
        args = parse_args()
    assert getattr(args, expected_command) is not None
    assert args.verbosity == 0


@mock.patch("sys.argv", ["cloninator", "new_subcommand"])
def test_cloninator_unknown_subcommand() -> None:
    with pytest.raises(SystemExit, match="2"):
        parse_args()
