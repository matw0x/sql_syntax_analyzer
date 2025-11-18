from abc import ABC, abstractmethod
from pglast.ast import Node

class BaseRule(ABC):
    @abstractmethod
    def validate(self, ast: tuple[Node, ...]) -> str | None:
        pass