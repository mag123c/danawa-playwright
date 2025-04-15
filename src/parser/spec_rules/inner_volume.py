import re
from .base import SpecParserBase

class InnerVolumeSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(내부\s?용량|수납\s?용량|내부공간|수납공간|내용물공간)", fragment, re.IGNORECASE))

    def key(self) -> str:
        return "inner_volume"