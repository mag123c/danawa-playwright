import re
from typing import List, Dict

def calculate_review_scores(reviews: List[Dict], price: int, weight: float, volume: float,
                            price_min: int, price_max: int,
                            weight_min: float, weight_max: float,
                            volume_min: float, volume_max: float) -> Dict:
    """
    리뷰 기반 점수 계산
    - 기능성: 리뷰 수와 평점을 바탕으로 계산
    - 휴대성: 무게, 부피를 기준으로 정규화
    - 내구성/디자인: 키워드 카운트 기반 정규화
    - 가성비: 가격 정규화
    """
    review_count = len(reviews)
    avg_score = sum([r["score"] for r in reviews if r.get("score")]) / review_count if review_count else 0
    
    # 기능성 점수
    func_score = ((min(review_count, 100) * avg_score) / 500) * 40 + 60

    # 휴대성 점수
    weight_norm = (weight - weight_min) / (weight_max - weight_min) if weight_max != weight_min else 0
    volume_norm = (volume - volume_min) / (volume_max - volume_min) if volume_max != volume_min else 0
    portability_score = ((1 - weight_norm) * 20 + (1 - volume_norm) * 20) + 60

    # 키워드 카운트
    text_all = " ".join([f"{r.get('title', '')} {r.get('content', '')}" for r in reviews])
    durable_count = len(re.findall(r"튼튼", text_all))
    design_count = len(re.findall(r"감성", text_all))
    
    durability_score = min(durable_count / review_count, 1.0) * 40 + 60 if review_count else 60
    design_score = min(design_count / review_count, 1.0) * 40 + 60 if review_count else 60

    # 가성비 점수
    price_norm = (price - price_min) / (price_max - price_min) if price_max != price_min else 0
    value_score = (1 - price_norm) * 40 + 60

    # 종합 점수 평균
    total = round((func_score + portability_score + durability_score + design_score + value_score) / 5)

    return {
        "total": total,
        "functionality": round(func_score),
        "portability": round(portability_score),
        "durability": round(durability_score),
        "design": round(design_score),
        "value": round(value_score),
    }