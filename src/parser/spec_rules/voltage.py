
import re
from .base import SpecParserBase

class VoltageSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(전압|전력|Volt)", fragment, re.IGNORECASE))

    def parse(self, fragment: str) -> tuple[str, str]:
        return "voltage", fragment
