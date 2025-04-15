import re
from .base import SpecParserBase

class VoltageSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return "전압" in fragment or "소비전력" in fragment or "소모전력" in fragment or any(v in fragment for v in ["12V", "24V", "220V"])
    
    def key(self) -> str:
        return "voltage"