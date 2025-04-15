import re
from .base import SpecParserBase

class FeatureSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return any(keyword in fragment for keyword in ["기능", "형태", "용도", "방식", "이동식바퀴", "손잡이", "충전포트", "온도표시", "냉장+냉동"])

    def key(self) -> str:
        return "feature"
