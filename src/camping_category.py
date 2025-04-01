from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

def extract_category_data(li):
    a_tag = li.select_one("a[href*='cate=']")
    if not a_tag:
        return None
    href = a_tag['href']
    url = href if href.startswith("http") else f"https://prod.danawa.com{href}"
    cate_code = href.split("cate=")[-1].split("&")[0]
    name = a_tag.get_text(strip=True).replace("신규메뉴", "").replace("인기메뉴", "").strip()
    group_code = li.get("group-code", "")
    category_code = li.get("category-code", "")
    depth = "1" if "depth1" in li.get("class", []) else "2" if "depth2" in li.get("class", []) else "3"

    return {
        "name": name,
        "cate": cate_code,
        "url": url,
        "group": group_code,
        "category_code": category_code,
        "depth": depth
    }

def get_camping_categories():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://prod.danawa.com/globaljs/com/danawa/common/category/CategoryInfoByGroupLayer.php?group=13")
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # 모든 depth1을 순회하며 캠핑을 찾기
    camping_root = None
    for li in soup.select("li.category__depth__row.depth1"):
        txt_tag = li.select_one(".category__depth__txt")
        if txt_tag and txt_tag.get_text(strip=True) == "캠핑":
            camping_root = li
            break

    if not camping_root:
        return []

    camping_root_name = "캠핑"
    depth2_items = camping_root.select("li.category__depth__row.depth2")

    results = []
    for d2 in depth2_items:
        d2_data = extract_category_data(d2)
        if not d2_data:
            continue

        d2_data["children"] = []
        d3_items = d2.select("li.category__depth__row")
        for d3 in d3_items:
            d3_data = extract_category_data(d3)
            if d3_data:
                d2_data["children"].append(d3_data)

        results.append(d2_data)

    return {
        "root": camping_root_name,
        "categories": results
    }

if __name__ == "__main__":
    camping_data = get_camping_categories()
    print(json.dumps(camping_data, ensure_ascii=False, indent=2))
    with open("camping_categories.json", "w", encoding="utf-8") as f:
        json.dump(camping_data, f, ensure_ascii=False, indent=2)