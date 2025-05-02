import asyncio
from urllib.parse import quote
from playwright.async_api import async_playwright
from src.parser.asynchronous.coupang_product_parser import CoupangProductParser
from src.service.coupang_product_matcher import CoupangProductMatcher
# from src.service.affiliate_link_generator import AffiliateLinkGenerator


class CoupangHtmlFetcher:
    BASE_URL = "https://www.coupang.com/np/search?q="

    def __init__(self, keyword: str):
        self.keyword = keyword

    async def fetch_html(self) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--disable-web-security'])
            context = await browser.new_context(ignore_https_errors=True)
            api_request = context.request

            encoded = quote(self.keyword)
            url = f"{self.BASE_URL}{encoded}"
            print(f"🔍 요청 URL: {url}")

            response = await api_request.get(
                url,
                timeout=60000,
                headers={
                    "Host": "www.coupang.com",
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Content-Type": "text/plain",
                    "Origin": "https://www.coupang.com",
                    "Referer": "https://www.coupang.com/",
                    "Sec-CH-UA": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                    "Sec-CH-UA-Mobile": "?0",
                    "Sec-CH-UA-Platform": '"macOS"',
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                    "Priority": "u=1, i"
                }
            )

            html = await response.text()
            print(f"📄 HTML 길이: {len(html)}")

            await browser.close()
            return html   



async def main():
    keyword = "올리빙 도트 아이스박스 21L 민트"
    html = await CoupangHtmlFetcher(keyword).fetch_html()

    products = CoupangProductParser.parse_products(html)
    if not products:
        print("❌ 실제 상품이 하나도 없습니다.")
        return

    matcher = CoupangProductMatcher(target_name=keyword)
    best = matcher.find_best_match(products)
    if not best:
        print("❌ 유사도가 기준 이하인 상품만 있습니다.")
        return

    print(f"🎯 매칭 상품: {best}")
    print(f"https://www.coupang.com/vp/products/{best.product_id}?itemId={best.item_id}&vendorItemId={best.vendor_item_id}")

    # gen = AffiliateLinkGenerator("YOUR_AFFILIATE_ID")
    # link = gen.generate(best)
    # print(f"✅ 매칭된 상품: {best}")
    # print(f"🔗 어필리에이트 링크: {link}")


if __name__ == "__main__":
    asyncio.run(main())