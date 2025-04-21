from .base import SpecParserBase

class DescriptionBooleanSpecParser(SpecParserBase):
    keyword_map = {
        "아이스박스": {
            "바퀴": "has_wheel",
            "물배출구": "has_drain",
            "테이블": "has_table",
            "내부수납": "has_inner_basket",
            "뚜껑부분컵": "has_lid_cup",
            "뚜껑부분개폐": "has_lid_open",
            "어깨끈": "has_shoulder_strap",
        },
        "쿨러백": {
            "바퀴": "has_wheel",
            "테이블": "has_table",
            "어깨끈": "has_shoulder_strap",
            "내부수납": "has_inner_basket",
        },
        "차량용냉온냉장고": {
            "스마트폰연동": "has_smartphone_connect",
            "이동식바퀴": "has_movable_wheel",
            "손잡이": "has_handle",
            "충전포트": "has_charging_port",
            "온도표시": "has_temp_display",
            "내부LED": "has_inner_led",
            "컵홀더": "has_cup_holder",
            "어깨끈": "has_shoulder_strap",
        }
    }

    def __init__(self, sub_category: str):
        self.sub_category = sub_category
        self.active_keywords = self.keyword_map.get(sub_category, {})

    def match(self, fragment: str) -> bool:
        return any(k in fragment for k in self.active_keywords.keys())

    def key(self) -> str:
        return ""

    def parse(self, fragment: str) -> list[tuple[str, str]] | None:
        results = []
        for keyword, attr in self.active_keywords.items():
            if keyword in fragment:
                results.append((attr, "1"))
        return results if results else None
