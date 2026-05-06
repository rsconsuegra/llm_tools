from abc import ABC, abstractmethod
from pathlib import Path

from llm_tools.models import ChatSession


class BaseParser(ABC):
    @abstractmethod
    def parse(self, source: Path | str) -> ChatSession:
        ...
