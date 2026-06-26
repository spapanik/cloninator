from abc import ABC, abstractmethod


class BaseSubcommand(ABC):
    @abstractmethod
    def run(self) -> None: ...
