from unittest import mock

import pytest

from cloninator.lib.cli import parse_args


@pytest.mark.parametrize(
    ("subcommand", "verbose", "extra_args", "expected_command", "expected_verbosity"),
    [
        ("clone", "-v", [], "clone_subcommand", 1),
        ("generate", "-vv", ["-r", "name::path"], "generate_subcommand", 2),
        ("generate", "-vvvvv", ["-r", "name::path"], "generate_subcommand", 5),
    ],
)
def test_cloninator_verbose(
    subcommand: str,
    verbose: str,
    extra_args: list[str],
    expected_command: str,
    expected_verbosity: int,
) -> None:
    with mock.patch("sys.argv", ["cloninator", subcommand, *extra_args, verbose]):
        args = parse_args()

    assert getattr(args, expected_command) is not None
    assert args.verbosity == expected_verbosity


@pytest.mark.parametrize(
    ("subcommand", "expected_command", "extra_args"),
    [
        ("clone", "clone_subcommand", []),
        ("generate", "generate_subcommand", ["-r", "name::path"]),
    ],
)
def test_cloninator(
    subcommand: str, expected_command: str, extra_args: list[str]
) -> None:
    with mock.patch("sys.argv", ["cloninator", subcommand, *extra_args]):
        args = parse_args()
    assert getattr(args, expected_command) is not None
    assert args.verbosity == 0


@mock.patch("sys.argv", ["cloninator", "new_subcommand"])
def test_cloninator_unknown_subcommand() -> None:
    with pytest.raises(SystemExit, match="2"):
        parse_args()


@mock.patch("sys.argv", ["cloninator", "--version"])
def test_version_flag() -> None:
    with pytest.raises(SystemExit, match="0"):
        parse_args()


@mock.patch("sys.argv", ["cloninator", "-V"])
def test_version_flag_short() -> None:
    with pytest.raises(SystemExit, match="0"):
        parse_args()


@pytest.mark.parametrize(
    ("verbose_count", "expected_verbosity"),
    [
        ("-v", 1),
        ("-vv", 2),
        ("-vvv", 3),
        ("-vvvv", 4),
        ("-vvvvv", 5),
        ("-vvvvvvvvvv", 10),
    ],
)
def test_verbosity_levels(verbose_count: str, expected_verbosity: int) -> None:
    with mock.patch("sys.argv", ["cloninator", "clone", verbose_count]):
        args = parse_args()
    assert args.verbosity == expected_verbosity


def test_generate_with_split_groups() -> None:
    with mock.patch(
        "sys.argv",
        ["cloninator", "generate", "-r", "group::/path", "-s"],
    ):
        args = parse_args()
    assert args.generate_subcommand is not None
    assert args.generate_subcommand.split_groups is True


def test_generate_without_split_groups() -> None:
    with mock.patch(
        "sys.argv",
        ["cloninator", "generate", "-r", "group::/path"],
    ):
        args = parse_args()
    assert args.generate_subcommand is not None
    assert args.generate_subcommand.split_groups is False


def test_generate_multiple_repo_groups() -> None:
    with mock.patch(
        "sys.argv",
        [
            "cloninator",
            "generate",
            "-r",
            "group1::/path1",
            "group2::/path2",
            "group3::/path3",
        ],
    ):
        args = parse_args()
    assert args.generate_subcommand is not None
    assert len(args.generate_subcommand.repo_groups) == 3
    assert args.generate_subcommand.repo_groups[0].name == "group1"
    assert args.generate_subcommand.repo_groups[1].name == "group2"
    assert args.generate_subcommand.repo_groups[2].name == "group3"


def test_invalid_repo_group_format_missing_separator() -> None:
    with (
        mock.patch("sys.argv", ["cloninator", "generate", "-r", "invalidpath"]),
        pytest.raises(ValueError, match="not enough values to unpack"),
    ):
        parse_args()


def test_clone_default_verbosity() -> None:
    with mock.patch("sys.argv", ["cloninator", "clone"]):
        args = parse_args()
    assert args.clone_subcommand is not None
    assert args.verbosity == 0


def test_clone_with_high_verbosity() -> None:
    with mock.patch(
        "sys.argv",
        ["cloninator", "clone", "-vvvvvvvvvvvvvvvvvvvv"],
    ):
        args = parse_args()
    assert args.clone_subcommand is not None
    assert args.verbosity == 20
