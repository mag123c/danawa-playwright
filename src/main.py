from src.infra.danawa_scraper import DanawaScraper
from src.storage.file_storage import save_as_json

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
    print(f"📦 {category['cate_name']} 수집 시작")
    scraper = DanawaScraper(
        group_code=category["group_code"],
        category_code=category["cate_code"],
        referer_code=category["ref_cate_code"],
        sub_category=category["cate_name"],
        depth=category["depth"]
    )
    items = scraper.scrape()
    save_as_json(items, category["cate_name"])
