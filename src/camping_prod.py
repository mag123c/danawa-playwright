import os
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup, Tag
import json
import re

def categorize_spec_items(parsed: list, spec_raw: str) -> dict:
    categories = {
        "크기": "크기",
        "크": "크기",
        "사이즈": "크기",
        "무게": "무게",
        "중량": "무게",
        "용량": "용량",
        "소비전력": "소비전력",
        "소모전력": "소비전력",
        "전력": "소비전력",
        "전압": "전압",
        "전원": "전원",
        "온도": "온도범위",
        "냉장온도": "온도범위",
        "냉동온도": "온도범위",
        "보냉효력": "보냉효력",
        "내냉효력": "보냉효력",
        "색상": "색상",
        "기능": "기능",
        "특징": "특징",
        "재질": "재질",
        "소음": "소음"
    }

    result = {}
    seen = set()
    globally_seen_values = set()

    for key, value in parsed:
        values = [v.strip() for v in re.split(r'[,/]', value) if v.strip()]
        for val in values:
            if not val:
                continue

            # 크기 패턴 직접 파악 (내부-, 외부-, 괄호 없는 케이스 포함)
            if re.search(r'(내부|외부)?[-\s]*\d{2,4}[\sxX\*]\d{2,4}[\sxX\*]\d{2,4}\s*(mm|cm)?', val, re.IGNORECASE):
                result.setdefault("크기", []).append(val)
                seen.add(("크기", val))
                globally_seen_values.add(val)
                continue

            # 온도 범위: -20~80도, 15도 이하 등
            if re.search(r'[\-\d]{1,3}\s*[~\-]\s*\d{1,3}\s*[℃°Cº]', val) or re.search(r'\d{1,3}\s*[℃°Cº]\s*(이하|이상)', val):
                result.setdefault("보냉효력", []).append(val)
                seen.add(("보냉효력", val))
                globally_seen_values.add(val)
                continue

            # 소비전력 단독 처리 (W 단위 포함, label 없이도 처리)
            if re.search(r'\d{1,4}\s*(w|W)', val):
                result.setdefault("소비전력", []).append(val)
                seen.add(("소비전력", val))
                globally_seen_values.add(val)
                continue

            # 소음 처리 (dB 단위 포함, label 없이도 처리)
            if re.search(r'\d{1,3}\s*dB', val, re.IGNORECASE):
                result.setdefault("소음", []).append(val)
                seen.add(("소음", val))
                globally_seen_values.add(val)
                continue

            # colon 기반 분리
            if ":" in val:
                sub_key, sub_val = map(str.strip, val.split(":", 1))
                for keyword, category in categories.items():
                    if keyword in sub_key and (category, sub_val) not in seen:
                        result.setdefault(category, []).append(sub_val)
                        seen.add((category, sub_val))
                        globally_seen_values.add(sub_val)
                        break
                else:
                    if val not in globally_seen_values:
                        result.setdefault("기타", []).append(val)
                        globally_seen_values.add(val)
            else:
                categorized = False
                for keyword, category in categories.items():
                    if keyword in key and (category, val) not in seen:
                        result.setdefault(category, []).append(val)
                        seen.add((category, val))
                        globally_seen_values.add(val)
                        categorized = True
                        break
                if not categorized and val not in globally_seen_values:
                    result.setdefault("기타", []).append(val)
                    globally_seen_values.add(val)

    return result

def remove_redundant_from_etc(spec_structured: dict) -> dict:
    labeled_values = set()
    for key, values in spec_structured.items():
        if key != "기타":
            for val in values:
                labeled_values.add(val.strip().lower())

    filtered_etc = []
    for val in spec_structured.get("기타", []):
        val_clean = val.strip().lower()
        if ":" in val_clean:
            try:
                _, sub_val = map(str.strip, val_clean.split(":", 1))
                if sub_val.lower() in labeled_values:
                    continue
            except:
                pass
        if val_clean not in labeled_values:
            filtered_etc.append(val)

    cleaned = {k: v for k, v in spec_structured.items() if k != "기타"}
    if filtered_etc:
        cleaned["기타"] = filtered_etc

    return cleaned



def extract_spec_html(spec_root: Tag) -> tuple[list[tuple[str, str]], str]:
    specs = []
    current_key = "기타"
    buffer = []

    text = spec_root.get_text(" / ", strip=True)

    # 1차: colon 있는 항목 먼저 분리
    matches = re.findall(r'([^:/\n]+):\s*([^:/\n]+)', text)
    for k, v in matches:
        specs.append((k.strip(), v.strip()))

    # 2차: <span class="cm_mark"> 기반 구조 파싱
    for node in spec_root.children:
        if isinstance(node, str):
            buffer.append(node.strip())
        elif node.name == "span" and "cm_mark" in node.get("class", []):
            if buffer:
                joined = " / ".join(buffer).strip()
                if joined:
                    specs.append((current_key, joined))
                buffer = []
            current_key = node.get_text(strip=True).strip("[]")
        elif node.name in ["a", "b", "span"]:
            buffer.append(node.get_text(strip=True))

    if buffer:
        joined = " / ".join(buffer).strip()
        if joined:
            specs.append((current_key, joined))

    # 3차: "L" 단위 보완 추출
    capacity_matches = re.findall(r'(\d{1,4}\.?\d*)\s*L', text, re.IGNORECASE)
    for cm in set(capacity_matches):
        specs.append(("용량", f"{cm}L"))

    return specs, text


def scrape_products(group_code: str, cate_name: str, category_code: str, referer_cate_code: str,
                    depth: str = "2", end_page: int = 100, output_dir: str = "."):
    url = "https://prod.danawa.com/list/ajax/getProductList.ajax.php"
    all_items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for page_num in range(1, end_page + 1):
            print(f"📄 페이지 {page_num} 수집 중...")

            params = {
                "btnAllOptUse": "false",
                "page": str(page_num),
                "listCategoryCode": category_code,
                "categoryCode": category_code,
                "viewMethod": "LIST",
                "sortMethod": "BEST",
                "listCount": "90",
                "group": group_code,
                "depth": depth,
            }

            form_data = urlencode(params)

            response = page.request.post(
                url,
                data=form_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": f"https://prod.danawa.com/list/?cate={referer_cate_code}",
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            html = response.text()
            soup = BeautifulSoup(html, "html.parser")

            items = []
            for item in soup.select(".prod_item"):
                try:
                    if not item.get("id"):
                        continue

                    image_tag = item.select_one(".thumb_image img")
                    image_url = image_tag.get("src") or image_tag.get("data-original")
                    if image_url and not image_url.startswith("http"):
                        image_url = "https:" + image_url

                    spec_node = item.select_one(".spec-box .spec_list") or item.select_one(".spec_list")
                    spec_raw = spec_node.get_text(" / ", strip=True) if spec_node else ""
                    parsed_spec, _ = extract_spec_html(spec_node) if spec_node else ([], "")
                    categorized_spec = categorize_spec_items(parsed_spec, spec_raw)
                    categorized_spec = remove_redundant_from_etc(categorized_spec)
                    options = item.select(".spec_list a, .spec_list span, .spec_list div")
                    option_texts = [opt.get_text(strip=True) for opt in options]

                    items.append({
                        "id": item.get("id"),
                        "main_category": item.select_one("input[id^=productItem_categoryInfo]").get("value", ""),
                        "sub_category": cate_name,
                        "name": item.select_one(".prod_name a").get_text(strip=True),
                        "url": item.select_one(".prod_name a").get("href"),
                        "image": image_url,
                        "spec_raw": spec_raw,
                        "spec_structured": categorized_spec,
                        "price": item.select_one(".price_sect strong").get_text(strip=True),
                        "date": item.select_one(".meta_item.mt_date dd").get_text(strip=True) if item.select_one(".meta_item.mt_date dd") else None,
                        "option": option_texts,
                        "maker": item.select_one(".price_sect button[data-maker-name]").get("data-maker-name", "") if item.select_one(".price_sect button[data-maker-name]") else None,
                    })
                except Exception as e:
                    print(f"⚠️ 파싱 실패: {e}")

            if not items:
                print("🚩 더 이상 상품이 없습니다. 중단합니다.")
                break

            all_items.extend(items)

        browser.close()

    safe_name = "".join(c for c in cate_name if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
    filename = f"products_{safe_name}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"✅ {cate_name} → {len(all_items)}개 저장 완료: {filepath}")
    return all_items


if __name__ == "__main__":
    # group_code = "14"
    # cate_name = "차량용냉온냉장고"
    # cate_code = "36799"
    # ref_cate_code = "14236799"
    # end_page = 100
    # scrape_products(group_code, cate_name, cate_code, ref_cate_code, end_page=end_page)
    
    categories = [
        {
            "group_code": "13",
            "cate_name": "아이스박스",
            "cate_code": "42018",
            "ref_cate_code": "13342018",
            "depth": "3",
        },
        {
            "group_code": "13",
            "cate_name": "쿨러백",
            "cate_code": "42019",
            "ref_cate_code": "13342019",
            "depth": "3",
        },
        {
            "group_code": "14",
            "cate_name": "차량용냉온냉장고",
            "cate_code": "36799",
            "ref_cate_code": "14236799",
            "depth": "3",
        },
    ]

    for category in categories:
        print(f"\n📦 {category['cate_name']} 수집 시작")
        scrape_products(
            group_code=category["group_code"],
            cate_name=category["cate_name"],
            category_code=category["cate_code"],
            referer_cate_code=category["ref_cate_code"],
            depth=category["depth"],
            end_page=100,
        )
    
    # group + depth + main_category = cate;
