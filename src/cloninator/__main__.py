from cloninator.lib.cli import parse_args
from cloninator.subcommands.clone import Clone
from cloninator.subcommands.generate import Generate


def main() -> None:
    args = parse_args()
    if args.clone_subcommand is not None:
        Clone(args.verbosity).run()
    elif args.generate_subcommand is not None:
        Generate(args.verbosity).run()
