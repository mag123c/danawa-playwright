import re
from .base import SpecParserBase

class SizeSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return (
            "크기" in fragment or 
            "사이즈" in fragment or 
            any(keyword in fragment for keyword in ["가로", "세로", "높이"])
        )


    def key(self) -> str:
        return "size"

    def normalize(self, value: str) -> str:
        value = re.sub(r"[()]", "", value)
        
        # 단위 감지
        is_mm = bool(re.search(r"\bmm\b|밀리미터", value.lower()))
        
        nums = re.findall(r"(\d+(?:\.\d+)?)", value)

        if len(nums) >= 2:
            if is_mm:
                nums = [round(float(x) / 10, 1) for x in nums]  # mm → cm
            else:
                nums = [round(float(x), 1) for x in nums]

            return "x".join(f"{n:.1f}" for n in nums) + "cm"

        return value.strip()
