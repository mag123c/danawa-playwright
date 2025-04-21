# src/parser/review_parser_async.py
import random
from typing import List
from bs4 import BeautifulSoup
from playwright.async_api import Page

class DanawaReviewAsyncParser:
    BASE_REVIEW_URL = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php"

    def __init__(self, page: Page):
        self.page = page

    async def get_reviews(self, product_code: str, limit: int = 100, max_pages: int = 30) -> List[dict]:
        reviews = []

        for page_num in range(1, max_pages + 1):
            print(f"📝 productItem{product_code}의 {page_num} 페이지 리뷰 수집중")

            t = f"{random.random()}"
            url = (
                f"{self.BASE_REVIEW_URL}?prodCode={product_code}"
                f"&page={page_num}&limit={limit}&score=0&t={t}"
            )
            cookies = await self.page.context.cookies()
            cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": f"https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
                "Cookie": cookie_header
            }

            response = await self.page.request.get(url, headers=headers, timeout=10000)
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            review_items = soup.select("li.danawa-prodBlog-companyReview-clazz-more")
            if not review_items:
                break

            for li in review_items:
                review = self._parse_review_item(li)
                reviews.append(review)

        return reviews

    def _parse_review_item(self, li) -> dict:
        score_raw = li.select_one(".star_mask")
        score_style = score_raw.get("style", "") if score_raw else ""
        score = int(score_style.replace("width:", "").replace("%", "").strip()) // 20 if score_style else None

        seller = None
        mall_elem = li.select_one(".mall")
        if mall_elem:
            img_tag = mall_elem.select_one("img[alt]")
            if img_tag and img_tag.get("alt"):
                seller = img_tag["alt"].strip()
            else:
                span = mall_elem.select_one("span")
                if span:
                    seller = span.get_text(strip=True)

        return {
            "score": score,
            "date": li.select_one(".date").text.strip() if li.select_one(".date") else None,
            "name": li.select_one(".name").text.strip() if li.select_one(".name") else None,
            "title": li.select_one(".tit").text.strip() if li.select_one(".tit") else None,
            "content": li.select_one(".atc").text.strip() if li.select_one(".atc") else None,
            "seller": seller
        }
