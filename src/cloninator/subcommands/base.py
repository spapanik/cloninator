from __future__ import annotations


class BaseSubcommand:
    __slots__ = ("verbosity",)
    verbosity: int

    def __init__(self, verbosity: int) -> None:
        self.verbosity = verbosity

    def run(self) -> None:
        raise NotImplementedError
