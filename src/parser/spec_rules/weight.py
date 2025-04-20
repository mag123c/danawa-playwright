import re
from .base import SpecParserBase

class WeightSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return "무게" in fragment or "중량" in fragment

    def key(self) -> str:
        return "weight"

    def normalize(self, value: str) -> str:
        value = re.sub(r"[()~약]|약|\s+", "", value, flags=re.IGNORECASE)  # 약, ~, 공백 제거
        value = value.replace("킬로그램", "kg").replace("그램", "g").replace("㎏", "kg").replace("KG", "kg")

        nums = re.findall(r"(\d+(?:\.\d+)?)", value)

        if not nums:
            return value.strip()

        weight = float(nums[0])

        if "g" in value.lower() and "kg" not in value.lower():
            weight = round(weight / 1000, 2)

        return f"{weight:.2f}"
