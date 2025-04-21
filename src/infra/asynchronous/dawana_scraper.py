from datetime import datetime
from typing import Optional
from urllib.parse import urlencode
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from src.service.reveiw_batch_collector import collect_reviews_concurrently
from src.parser.asynchronous.product_parser import ProductAsyncParser
from src.infra.asynchronous.dawana_additional_fetcher import DanawaAdditionalAsyncFetcher
import re

class DanawaAsyncScraper:
    def __init__(self, group_code: str, category_code: str, referer_code: str, sub_category: str, depth: str = "3", end_page: int = 100, base_dir: Optional[str] = None):
        self.group_code = group_code
        self.category_code = category_code
        self.referer_code = referer_code
        self.sub_category = sub_category
        self.depth = depth
        self.end_page = end_page
        self.base_dir = base_dir or f"danawa_{datetime.now().strftime('%Y%m%d')}"

    async def scrape(self) -> list:
        url = "https://prod.danawa.com/list/ajax/getProductList.ajax.php"
        all_results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            fetcher = DanawaAdditionalAsyncFetcher(page, self.referer_code)

            try:
                for page_num in range(1, self.end_page + 1):
                    print(f"📄 페이지 {page_num} 수집 중...")

                    params = {
                        "btnAllOptUse": "false",
                        "page": str(page_num),
                        "listCategoryCode": self.category_code,
                        "categoryCode": self.category_code,
                        "viewMethod": "LIST",
                        "sortMethod": "BoardCount",
                        "listCount": "90",
                        "group": self.group_code,
                        "depth": self.depth,
                    }

                    response = await page.request.post(
                        url,
                        data=urlencode(params),
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Referer": f"https://prod.danawa.com/list/?cate={self.referer_code}",
                            "X-Requested-With": "XMLHttpRequest"
                        },
                        timeout=10000 
                    )

                    if response.status != 200:
                        print(f"❗ 페이지 {page_num} 요청 실패: status {response.status}")
                        break

                    soup = BeautifulSoup(await response.text(), "html.parser")
                    items = soup.select(".prod_item")
                    if not items:
                        print(f"❗ 페이지 {page_num}에서 항목 없음. 종료")
                        break

                    equipment_map = {}
                    product_ids = []

                    for item in items:
                        try:
                            equipment = ProductAsyncParser.parse_product_item(item, self.sub_category)
                            pid = re.sub(r"^productItem", "", equipment.id)
                            equipment_map[pid] = equipment
                            product_ids.append(pid)
                        except Exception as e:
                            print(f"⚠️ 파싱 오류: {e}")
                            
                        
                    review_data = await fetcher.fetch(product_ids, self.group_code)

                    # 병합
                    for pid, equipment in equipment_map.items():
                        stripped_id = equipment.id.replace("productItem", "")
                        info = review_data.get(stripped_id, {})

                        if info.get("review_count") is not None:
                            equipment.review_count = info["review_count"]
                        if info.get("score_count") is not None:
                            equipment.score_count = info["score_count"]

                    # ✅ 리뷰 수 있는 애만 병렬 수집
                    review_targets = [e for e in equipment_map.values() if (e.review_count or 0) > 0]

                    if review_targets:
                        review_results = await collect_reviews_concurrently(
                            product_list=review_targets,
                            sub_category=self.sub_category,
                            base_dir=self.base_dir
                        )

                        for pid, equipment in equipment_map.items():
                            stripped_id = equipment.id.replace("productItem", "")
                            if stripped_id in review_results:
                                equipment.reviews = review_results[stripped_id]
                    else:
                        print(f"🔍 리뷰 수집 대상 없음 (페이지 내 전부 review_count == 0)")
                        
                    all_results.extend(equipment_map.values());

            finally:
                await page.close()
                await context.close()
                await browser.close()

        return all_results
