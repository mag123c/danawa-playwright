from abc import ABC, abstractmethod

class SpecParserBase(ABC):
    @abstractmethod
    def match(self, fragment: str) -> bool:
        pass

    @abstractmethod
    def parse(self, fragment: str) -> tuple[str, str]:
        pass
