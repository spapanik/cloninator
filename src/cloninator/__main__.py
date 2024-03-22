from argparse import ArgumentParser

from cloninator.clone import clone


def get_parser() -> ArgumentParser:
    parser = ArgumentParser()
    usage = parser.add_mutually_exclusive_group(required=True)
    usage.add_argument("--clone", action="store_true")

    return parser


def main() -> None:
    args = get_parser().parse_args()
    if args.clone:
        clone()
    else:
        msg = "Invalid usage"
        raise ValueError(msg)
