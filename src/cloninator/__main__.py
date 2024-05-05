from argparse import ArgumentParser

from cloninator.__version__ import __version__
from cloninator.clone import clone
from cloninator.generate import generate


def get_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="print the version and exit",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    subparsers.add_parser("clone", help="clone a repository")
    subparsers.add_parser("generate", help="generate a repository")

    return parser


def main() -> None:
    args = get_parser().parse_args()
    match args.subcommand:
        case "clone":
            clone()
        case "generate":
            generate()
