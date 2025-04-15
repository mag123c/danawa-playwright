


import re
from .base import SpecParserBase

class DescriptionSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(특징|옵션)", fragment, re.IGNORECASE))

    def parse(self, fragment: str) -> tuple[str, str]:
        return "description", fragment
