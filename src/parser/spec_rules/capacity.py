import re
from .base import SpecParserBase

class CapacitySpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return "용량" in fragment or "리터" in fragment or "L" in fragment

    def key(self) -> str:
        return "capacity"

    def normalize(self, value: str) -> str:
        value = re.sub(r"[()~약]|약|\s+", "", value, flags=re.IGNORECASE) 
        value = value.replace("리터", "L").replace("ℓ", "L")

        nums = re.findall(r"(\d+(?:\.\d+)?)", value)

        if not nums:
            return value.strip()

        capacity = float(nums[0])
        return f"{capacity:.2f}"