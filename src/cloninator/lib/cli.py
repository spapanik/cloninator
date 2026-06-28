from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from cloninator.__version__ import __version__
from cloninator.lib.utils import RepoGroupKey

if TYPE_CHECKING:
    from typing_extensions import Self  # upgrade: py3.10: import from typing

sys.tracebacklimit = 0


@dataclass(frozen=True, slots=True)
class CloneCliArgs:
    @classmethod
    def from_args(cls, _args: Namespace, /) -> Self:
        return cls()


@dataclass(frozen=True, slots=True)
class GenerateCliArgs:
    repo_groups: tuple[RepoGroupKey, ...]
    split_groups: bool

    @classmethod
    def from_args(cls, args: Namespace, /) -> Self:
        repo_groups = []
        for group in args.repo_groups:
            name, root = group.split("::")
            repo_groups.append(
                RepoGroupKey(name=name, root=Path(root).expanduser().absolute())
            )
        return cls(repo_groups=tuple(repo_groups), split_groups=args.split_groups)


@dataclass(frozen=True, slots=True)
class CliArgs:
    verbosity: int
    clone_subcommand: CloneCliArgs | None
    generate_subcommand: GenerateCliArgs | None

    @classmethod
    def from_args(cls, args: Namespace, /) -> Self:
        clone_subcommand = None
        generate_subcommand = None

        match args.subcommand:
            case "clone":
                clone_subcommand = CloneCliArgs.from_args(args)
            case "generate":
                generate_subcommand = GenerateCliArgs.from_args(args)

        return cls(
            verbosity=args.verbosity,
            clone_subcommand=clone_subcommand,
            generate_subcommand=generate_subcommand,
        )


def parse_args() -> CliArgs:
    parser = ArgumentParser(prog="cloninator", description="Git repo cloner")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="print the version and exit",
    )

    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help="increase the level of verbosity",
    )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    subparsers.add_parser("clone", parents=[parent_parser], help="clone a repository")

    generate_parser = subparsers.add_parser(
        "generate", parents=[parent_parser], help="generate repository config"
    )
    generate_parser.add_argument(
        "-r", "--repo-groups", nargs="+", required=True, help="add a repo group"
    )
    generate_parser.add_argument(
        "-s",
        "--split-groups",
        action="store_true",
        help="save each group to a separate file",
    )

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return CliArgs.from_args(args)
