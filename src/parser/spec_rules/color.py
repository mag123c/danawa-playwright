import re
from .base import SpecParserBase

class ColorSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(색상)", fragment, re.IGNORECASE))

    def key(self) -> str:
        return "color"
