from .base import SpecParserBase

class CapacitySpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return "용량" in fragment or "리터" in fragment or "L" in fragment

    def key(self) -> str:
        return "capacity"