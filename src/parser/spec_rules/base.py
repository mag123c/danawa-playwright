from abc import ABC, abstractmethod

class SpecParserBase(ABC):
    @abstractmethod
    def match(self, fragment: str) -> bool:
        pass

    def parse(self, fragment: str) -> tuple[str, str]:
        # 공통 파싱 처리
        if ":" in fragment:
            _, value = fragment.split(":", 1)
            return self.key(), self.normalize(value.strip())
        return self.key(), self.normalize(fragment.strip())

    @abstractmethod
    def key(self) -> str:
        pass
    
    def normalize(self, value: str) -> str:
        return value
