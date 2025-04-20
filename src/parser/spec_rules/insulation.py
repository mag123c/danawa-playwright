import re
from .base import SpecParserBase

class InsulationSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(보온|보냉|단열|보냉력|보온력)", fragment, re.IGNORECASE))

    def key(self) -> str:
        return "insulation"
