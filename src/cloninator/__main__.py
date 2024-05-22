import sys

from cloninator.clone import clone
from cloninator.generate import generate
from cloninator.lib.parser import parse_args

sys.tracebacklimit = 0


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "clone":
            clone()
        case "generate":
            generate()
