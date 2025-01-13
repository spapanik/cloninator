from unittest import mock

import pytest

from cloninator.lib.cli import parse_args


@pytest.mark.parametrize(
    ("subcommand", "verbose", "expected_command", "expected_verbosity"),
    [
        ("clone", "-v", "clone", 1),
        ("generate", "-vv", "generate", 2),
        ("generate", "-vvvvv", "generate", 5),
    ],
)
def test_cloninator_verbose(
    subcommand: str, verbose: str, expected_command: str, expected_verbosity: int
) -> None:
    with mock.patch("sys.argv", ["cloninator", subcommand, verbose]):
        args = parse_args()

    assert args.subcommand == expected_command
    assert args.verbosity == expected_verbosity


@pytest.mark.parametrize(
    "subcommand",
    ["clone", "generate"],
)
def test_cloninator(subcommand: str) -> None:
    with mock.patch("sys.argv", ["cloninator", subcommand]):
        args = parse_args()
    assert args.subcommand == subcommand
    assert args.verbosity == 0


@mock.patch("sys.argv", ["cloninator", "new_subcommand"])
def test_cloninator_unknown_subcommand() -> None:
    with pytest.raises(SystemExit, match="2"):
        parse_args()
