import sys
from argparse import ArgumentParser, Namespace

from cloninator.__version__ import __version__

sys.tracebacklimit = 0


def parse_args() -> Namespace:
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
    subparsers.add_parser(
        "generate", parents=[parent_parser], help="generate repository config"
    )

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return args
