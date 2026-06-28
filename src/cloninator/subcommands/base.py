from __future__ import annotations


class BaseSubcommand:
    __slots__ = ("verbosity",)

    def __init__(self, verbosity: int, **_kwargs: object) -> None:
        self.verbosity = verbosity

    def run(self) -> None:
        raise NotImplementedError
