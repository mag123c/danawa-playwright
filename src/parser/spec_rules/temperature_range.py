import re
from .base import SpecParserBase

class TemperatureRangeSpecParser(SpecParserBase):
    def match(self, fragment: str) -> bool:
        return any(t in fragment for t in ["냉장온도", "냉동온도", "온도", "ºC", "°C"])

    def key(self) -> str:
        return "temperature_range"

    def normalize(self, value: str) -> str:
        cleaned = value.replace("ºC", "°C").replace("℃", "°C").strip()

        temps = []
        if "냉장" in cleaned:
            match = re.search(r"냉장(?:온도)?[:：]?\s*(-?\d+)(?:~(-?\d+))?", cleaned)
            if match:
                if match.group(2):
                    temps.append(f"냉장: {match.group(1)}~{match.group(2)}°C")
                else:
                    temps.append(f"냉장: {match.group(1)}°C")

        if "냉동" in cleaned:
            match = re.search(r"냉동(?:온도)?[:：]?\s*(-?\d+)(?:~(-?\d+))?", cleaned)
            if match:
                if match.group(2):
                    temps.append(f"냉동: {match.group(1)}~{match.group(2)}°C")
                else:
                    temps.append(f"냉동: {match.group(1)}°C")

        # 단일 온도값만 있는 경우
        if not temps:
            only_temp = re.findall(r"-?\d{1,3}(?:\.\d+)?(?=°C)", cleaned)
            if only_temp:
                temps.append(" / ".join(f"{t}°C" for t in only_temp))

        return " / ".join(temps) if temps else cleaned
