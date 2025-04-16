import os
import json
import csv
from datetime import datetime

def convert_json_to_csv(json_path: str):
    csv_path = json_path.replace(".json", ".csv")

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    base_fields = [
        ("id", "제품 ID"),
        ("name", "제품명"),
        ("main_category", "메인카테고리"),
        ("sub_category", "서브카테고리"),
        ("price", "가격"),
        ("maker", "제조사"),
        ("registered_date", "등록일"),
        ("review_count", "리뷰 수"),
        ("score_count", "평점"),
        ("detail_url", "상세 페이지"),
        ("image_url", "이미지 URL"),
        ("raw_specs", "원시 스펙 정보"),
    ]

    spec_fields = [
        ("size", "크기"),
        ("capacity", "용량"),
        ("weight", "무게"),
        ("voltage", "전압"),
        ("features", "기능"),
        ("temperature_range", "온도 범위"),
        ("power_consumption", "소비전력"),
        ("description", "기타 설명"),
        ("material", "재질"),
        ("color", "색상"),
        ("usage", "용도"),
        ("insulation", "보냉효력"),
        ("inner_volume", "내부용량"),
        ("extra", "기타"),
    ]

    all_fields = base_fields + spec_fields
    field_keys = [key for key, _ in all_fields]
    field_labels = [label for _, label in all_fields]

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=field_labels)
        writer.writeheader()

        for item in items:
            row = {}
            for key, label in base_fields:
                row[label] = item.get(key, "")

            specs = item.get("specs", {})
            for key, label in spec_fields:
                row[label] = specs.get(key, "")

            writer.writerow(row)

    print(f"✅ 변환 완료: {csv_path}")

def main():
    today_str = datetime.now().strftime("%Y%m%d")
    base_dir = f"danawa_{today_str}"

    if not os.path.exists(base_dir):
        print(f"❗ 디렉토리 없음: {base_dir}")
        return

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                full_path = os.path.join(root, file)
                convert_json_to_csv(full_path)

if __name__ == "__main__":
    main()
