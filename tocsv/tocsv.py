import os
import json
import csv
from glob import glob
from collections import OrderedDict

# 컬럼 매핑
BASE_COLUMNS_MAP = OrderedDict({
    'id': '상품코드',
    'name': '상품명',
    'main_category': '카테고리',
    'sub_category': '서브카테고리',
    'maker': '제조사',
    'date': '출시일',
    'price': '가격',
})

STRUCTURED_KEYS_ORDER = [
    '용량', '무게', '크기', '기능', '전압', '온도범위', '소비전력', '소음', '특징', '기타'
]

COLUMN_DESCRIPTIONS = {
    '상품코드': '제품 식별 ID',
    '상품명': '제품 이름',
    '카테고리': '대분류',
    '서브카테고리': '소분류',
    '제조사': '브랜드/제조사',
    '출시일': '출시 년월',
    '가격': '표시 가격 (원)',
    '용량': '제품 용량 (예: 86L)',
    '무게': '제품 무게 (예: 3.9kg)',
    '크기': '제품 크기 (가로x세로x높이 또는 깊이)',
    '기능': '냉장, 냉동 등 주요 기능',
    '전압': '지원 전압 (예: 12V, 220V 등)',
    '온도범위': '동작 온도 범위 (예: -20~10°C)',
    '소비전력': '소비 전력 (예: 40W)',
    '소음': '작동 소음 (예: 45dB)',
    '특징': '기타 기술적 특징',
    '기타': '기타 태그나 분류',
}

def normalize_spec(spec_structured):
    normalized = OrderedDict()
    for key in STRUCTURED_KEYS_ORDER:
        values = spec_structured.get(key, [])
        normalized[key] = ', '.join(values) if values else ''
    return normalized

def parse_json_to_csv(input_file):
    filename = os.path.basename(input_file)
    name_without_ext = os.path.splitext(filename)[0]
    output_file = f"{name_without_ext}.csv"

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    headers = list(BASE_COLUMNS_MAP.values()) + STRUCTURED_KEYS_ORDER

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerow({col: COLUMN_DESCRIPTIONS.get(col, '') for col in headers})

        for item in data:
            base_row = {BASE_COLUMNS_MAP[k]: item.get(k, '') for k in BASE_COLUMNS_MAP}
            structured = normalize_spec(item.get('spec_structured', {}))
            base_row.update(structured)
            writer.writerow(base_row)

    print(f"✅ 변환 완료 → {output_file}")

if __name__ == '__main__':
    for json_file in glob('./products_*.json'):
        parse_json_to_csv(json_file)
