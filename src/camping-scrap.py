# camping-run.py
from camping_category import get_camping_categories
from camping_prod import scrape_products
import json

def run_all():
    categories = get_camping_categories()
    all_products = []

    for cate in categories:
        print(f"[카테고리] {cate['name']} / {cate['cate']}")
        products = scrape_products(
            cate["cate"],
            name=cate["name"],
            group=cate.get("group"),
            depth=cate.get("depth"),
            category_code=cate.get("category_code")
        )
        for p in products:
            p["cate_name"] = cate["name"]
        all_products.extend(products)

    with open("camping_products.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 총 {len(all_products)}개의 상품을 수집했습니다.")

if __name__ == "__main__":
    run_all()
