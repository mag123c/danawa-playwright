from typing import List
from bs4 import BeautifulSoup, Tag

class CoupangProduct:
    def __init__(
        self,
        product_id: str,
        item_id: str,
        vendor_item_id: str,
        name: str,
        price: int,
        review_count: int,
        rating: float
    ):
        self.product_id = product_id
        self.item_id = item_id
        self.vendor_item_id = vendor_item_id
        self.name = name
        self.price = price
        self.review_count = review_count
        self.rating = rating

    def __repr__(self):
        return f"<{self.name} | {self.price}원 | 리뷰{self.review_count} | 평점{self.rating}>"

class CoupangProductParser:
    @staticmethod
    def parse_products(html: str) -> List[CoupangProduct]:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        # ul#productList > li.search-product 요소 전부 순회
        for li in soup.select("ul#productList > li.search-product"):
            # 1) 광고 배너(li에 'search-product__ad-badge' 클래스) 제외
            # 2) data-adsplatform 어트리뷰트가 있으면 광고
            if "search-product__ad-badge" in li.get("class", []) or li.has_attr("data-adsplatform"):
                continue

            try:
                a = li.select_one("a.search-product-link")
                name = li.select_one(".name").get_text(strip=True)
                price = int(li.select_one(".price .price-value").get_text(strip=True).replace(",", ""))

                review_tag = li.select_one(".rating-total-count")
                review_count = int(review_tag.get_text(strip=True).strip("()").replace(",", "")) if review_tag else 0

                style = li.select_one(".star .rating").get("style", "")
                rating = round(int(style.strip().rstrip("%").split(":")[-1]) / 20, 1) if "width" in style else 0.0

                pid = a["data-product-id"]
                iid = a["data-item-id"]
                vid = a["data-vendor-item-id"]

                items.append(CoupangProduct(pid, iid, vid, name, price, review_count, rating))
            except Exception:
                # 파싱 실패한 항목은 무시
                continue
        return items