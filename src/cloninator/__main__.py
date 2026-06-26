from cloninator.lib.cli import parse_args
from cloninator.subcommands.clone import clone
from cloninator.subcommands.generate import generate


def main() -> None:
    args = parse_args()
    if args.clone_subcommand is not None:
        clone()
    elif args.generate_subcommand is not None:
        generate()
