import argparse
import sys

from cloninator.__version__ import __version__
from cloninator.clone import clone
from cloninator.generate import generate

sys.tracebacklimit = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="print the version and exit",
    )

    parent_parser = argparse.ArgumentParser(add_help=False)
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
    subparsers.add_parser(
        "generate", parents=[parent_parser], help="generate a repository"
    )

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return args


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "clone":
            clone()
        case "generate":
            generate()
