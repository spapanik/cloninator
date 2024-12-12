import sys

from cloninator.lib.parser import parse_args
from cloninator.subcommands.clone import clone
from cloninator.subcommands.generate import generate

sys.tracebacklimit = 0


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "clone":
            clone()
        case "generate":  # pragma: no branch
            generate()
