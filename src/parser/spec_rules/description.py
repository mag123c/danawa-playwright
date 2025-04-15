from .base import SpecParserBase

class DescriptionSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return "특징" in fragment or fragment.startswith("특징:")

    def key(self) -> str:
        return "description"