from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from src.parser.product_parser import ProductParser
from src.infra.danawa_additional_fetcher import DanawaAdditionalFetcher
import re

class DanawaScraper:
    def __init__(self, group_code: str, category_code: str, referer_code: str, sub_category: str, depth: str = "3", end_page: int = 100):
        self.group_code = group_code
        self.category_code = category_code
        self.referer_code = referer_code
        self.sub_category = sub_category
        self.depth = depth
        self.end_page = end_page

    def scrape(self) -> list:
        url = "https://prod.danawa.com/list/ajax/getProductList.ajax.php"
        all_results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            fetcher = DanawaAdditionalFetcher(page, self.referer_code)

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

                    response = page.request.post(
                        url,
                        data=urlencode(params),
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Referer": f"https://prod.danawa.com/list/?cate={self.referer_code}",
                            "X-Requested-With": "XMLHttpRequest"
                        },
                        timeout=10000  # 💡 응답 지연 방지용 타임아웃
                    )

                    if response.status != 200:
                        print(f"❗ 페이지 {page_num} 요청 실패: status {response.status}")
                        break

                    soup = BeautifulSoup(response.text(), "html.parser")
                    items = soup.select(".prod_item")
                    if not items:
                        print(f"❗ 페이지 {page_num}에서 항목 없음. 종료")
                        break

                    equipment_map = {}
                    product_ids = []

                    for item in items:
                        try:
                            equipment = ProductParser.parse_product_item(item, self.sub_category)
                            pid = re.sub(r"^productItem", "", equipment.id)
                            equipment_map[pid] = equipment
                            product_ids.append(pid)
                        except Exception as e:
                            print(f"⚠️ 파싱 오류: {e}")

                    review_data = fetcher.fetch(product_ids, self.group_code)

                    for pid, info in review_data.items():
                        if pid not in equipment_map:
                            continue
                        
                        try:
                            if info.get("review_count") is not None:
                                equipment_map[pid].review_count = info["review_count"]
                            if info.get("score_count") is not None:
                                equipment_map[pid].score_count = info["score_count"]
                        except Exception as e:
                            print(f"⚠️ 리뷰 데이터 파싱 오류: {e}")
                            
                    all_results.extend(equipment_map.values())

            except Exception as e:
                print(f"🔥 예외 발생: {e}")
            finally:
                page.close()
                context.close()
                browser.close()

        return all_results
