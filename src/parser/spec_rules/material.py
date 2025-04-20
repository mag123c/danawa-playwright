import re
from .base import SpecParserBase

class MaterialSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(재질|소재|내부소재|외부소재)", fragment, re.IGNORECASE))

    def key(self) -> str:
        return "material"
