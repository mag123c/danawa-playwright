from typing import List
from difflib import SequenceMatcher
from src.parser.asynchronous.coupang_product_parser import CoupangProduct
from typing import Optional


class CoupangProductMatcher:
    def __init__(self, target_name: str):
        self.target_name = target_name

    def find_best_match(self, products: List[CoupangProduct], min_score: float = 0.6) -> Optional[CoupangProduct]:
        best, best_score = None, 0.0
        for p in products:
            score = SequenceMatcher(None, self.target_name, p.name).ratio()
            if score > best_score and score >= min_score:
                best, best_score = p, score
        return best