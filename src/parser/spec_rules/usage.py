import re
from .base import SpecParserBase

class UsageSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return bool(re.search(r"(사용처|용도|캠핑|차량용|피크닉|레저용|낚시)", fragment, re.IGNORECASE))

    def key(self) -> str:
        return "usage"