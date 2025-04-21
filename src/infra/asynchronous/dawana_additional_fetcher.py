from typing import List, Dict
from urllib.parse import urlencode
from playwright.async_api import Page

class DanawaAdditionalAsyncFetcher:
    def __init__(self, page: Page, referer_code: str):
        self.page = page
        self.referer_code = referer_code

    async def fetch(self, product_ids: List[str], group_code: str) -> Dict[str, dict]:
        product_code_list = ",".join(product_ids)

        url = "https://prod.danawa.com/list/ajax/getProductAdditionalList.ajax.php"
        body = urlencode({
            "productCodeList": product_code_list,
            "sortMethod": "BoardCount",
            "viewMethod": "LIST",
            "group": group_code
        })

        cookies = await self.page.context.cookies()
        cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"https://prod.danawa.com/list/?cate={self.referer_code}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": cookie_header
        }

        try:
            response = await self.page.request.post(url, data=body, headers=headers, timeout=10000) 
            if response.status != 200:
                print(f"⚠️ 응답 실패 status={response.status}")
                return {}
            data = await response.json()
        except Exception as e:
            print(f"❌ POST fetch 실패: {e}")
            return {}

        parsed = {}
        if isinstance(data, dict) and "productList" in data:
            for pid, pdata in data["productList"].items():
                if not pdata:
                    print(f"⚠️ 상품 {pid}는 데이터가 없습니다. 무시합니다.")
                    continue

                comment = pdata.get("productComment")
                if not isinstance(comment, dict): 
                    comment = {}

                parsed_item = {}

                review = comment.get("productCommentCount")
                if review and review.strip():
                    parsed_item["review_count"] = int(review.replace(",", ""))

                score = comment.get("starPoint")
                if score is not None:
                    try:
                        parsed_item["score_count"] = round(float(score), 1)
                    except:
                        pass

                parsed[pid] = parsed_item

        return parsed
