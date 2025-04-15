



import re
from .base import SpecParserBase

class FeatureSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(기능|형태|용도|방식)", fragment, re.IGNORECASE))

    def parse(self, fragment: str) -> tuple[str, str]:
        return "feature", fragment
