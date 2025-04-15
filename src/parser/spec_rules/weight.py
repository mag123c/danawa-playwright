import re
from .base import SpecParserBase

class WeightSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return "무게" in fragment or "중량" in fragment

    def key(self) -> str:
        return "weight"
