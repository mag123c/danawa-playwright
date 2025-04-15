

import re
from .base import SpecParserBase

class CapacitySpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(용량)", fragment, re.IGNORECASE))

    def parse(self, fragment: str) -> tuple[str, str]:
        return "capacity", fragment
