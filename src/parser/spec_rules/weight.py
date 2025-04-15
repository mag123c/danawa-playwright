
import re
from .base import SpecParserBase

class WeightSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(무게)", fragment, re.IGNORECASE))

    def parse(self, fragment: str) -> tuple[str, str]:
        return "weight", fragment
