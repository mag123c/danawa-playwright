import asyncio
import random
from urllib.parse import quote
from playwright_stealth import stealth_async
from playwright.async_api import async_playwright
from src.parser.asynchronous.coupang_product_parser import CoupangProductParser
from src.service.coupang_product_matcher import CoupangProductMatcher
# from src.service.affiliate_link_generator import AffiliateLinkGenerator


class CoupangHtmlFetcher:
    BASE_URL = "https://www.coupang.com/np/search?&q="

    def __init__(self, keyword: str):
        self.keyword = keyword
        self.user_agents = [
            {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36", "platform": '"Windows"'},
            {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36", "platform": '"macOS"'},
        ]

    async def fetch_html(self) -> str:
        async with async_playwright() as p:
            user_agent_info = random.choice(self.user_agents)
            selected_user_agent = user_agent_info["ua"]
            platform = user_agent_info["platform"]
            print(f"🤖 선택된 User-Agent: {selected_user_agent}")
            print(f"🖥️ 선택된 Platform: {platform}")

            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--lang=ko-KR'
                    # '--disable-web-security',
                    '--disable-http2',                                    # HTTP/2 비활성화
                    '--disable-quic',                                     # QUIC 비활성화
                    # '--disable-features=NetworkService,NetworkServiceInProcess',  
                    '--disable-blink-features=AutomationControlled',      # 자동화 탐지 차단
                    '--start-maximized', # 브라우저를 최대화하여 실행 (더 사람처럼 보이게)
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )

            context = await browser.new_context(
                locale="ko-KR",
                timezone_id="Asia/Seoul",
                geolocation={"latitude": 37.5665, "longitude": 126.9780},
                permissions=["geolocation"],
                ignore_https_errors=True,
                user_agent=selected_user_agent,
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://www.coupang.com/",
                    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="136", "Not-A.Brand";v="99"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": platform,
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none", # 직접 접속 시 "none", 내부 이동 시 "same-origin" 등
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                }
            )

            # await context.add_cookies([
            #     {"name": "PCID", "value": "17418684436306169692218", "domain": ".coupang.com", "path": "/"},
            #     {"name": "MARKETID", "value": "17418684436306169692218", "domain": ".coupang.com", "path": "/"},
            #     {"name": "x-coupang-accept-language", "value": "ko-KR", "domain": ".coupang.com", "path": "/"},
            #     {"name": "_fbp", "value": "fb.1.1741868445075.25325014701425710", "domain": ".coupang.com", "path": "/"},
            #     {"name": "delivery_toggle", "value": "false", "domain": ".coupang.com", "path": "/"},
            #     {"name": "sid", "value": "672c99cebb674a31b5d29dc6bf026cccfd0cf26d", "domain": ".coupang.com", "path": "/"},
            #     {"name": "x-coupang-target-market", "value": "KR", "domain": ".coupang.com", "path": "/"},
            # ])

            page = await context.new_page()
            
            await stealth_async(page)    # 스텔스 플러그인 적용

            url = f"{self.BASE_URL}{self.keyword}"
            print(f"🔍 요청 URL: {url}")

            try:
                response = await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                if not response or response.status != 200:
                    print(f"❌ [GOTO 실패] URL: {url} | 응답 없음 또는 상태코드 {response.status}")
                    return ""

                print(f"📄 [페이지 응답] 상태: {response.status}, 최종 URL: {response.url}")

                # 페이지 로드 후 인간적인 행동 시뮬레이션 (예: 약간의 스크롤)
                for _ in range(random.randint(1, 3)):
                    scroll_amount = random.randint(300, 800)
                    await page.mouse.wheel(0, scroll_amount)
                    await page.wait_for_timeout(random.randint(500, 1500))

                # 상태 코드가 200이 아니면 차단 페이지일 가능성 확인
                if response.status != 200:
                    error_html = await page.content()
                    print(f"❌ [GOTO 실패] URL: {url} | 상태 코드 {response.status}")
                    print(f"📄 [에러 페이지 내용 일부]: {error_html[:500]}...") # 디버깅 시 확인
                    if "보안 문자" in error_html or "자동 수집" in error_html or "CAPTCHA" in error_html:
                        print("🚫 봇 차단 페이지 또는 CAPTCHA 감지됨.")
                    await browser.close()
                    return "" # 또는 error_html을 반환하여 분석

                # 검색 결과 목록 선택자가 나타날 때까지 대기
                # 실제 쿠팡의 선택자는 변경될 수 있으므로, 주기적인 확인 필요
                await page.wait_for_selector('ul.search-product-list', timeout=30000)
                
                # 모든 콘텐츠가 로드될 때까지 추가 대기 (선택 사항)
                await page.wait_for_timeout(random.randint(2000, 5000))

                html_content = await page.content()
                # print(f"📄 [페이지 내용 일부]: {html_content[:200]}...") # 디버깅 시 확인
                await browser.close()
                return html_content

            except Exception as e:
                print(f"🔥 [예외 발생] {type(e).__name__}: {e}")
                try:
                    # 예외 발생 시 현재 페이지 스크린샷 저장 (디버깅용)
                    await page.screenshot(path=f"error_screenshot_{self.keyword.replace('%', '_')}.png")
                    print(f"📸 예외 발생 스크린샷 저장: error_screenshot_{self.keyword.replace('%', '_')}.png")
                except Exception as screenshot_error:
                    print(f"⚠️ 스크린샷 저장 실패: {screenshot_error}")
                await browser.close()
                return ""



async def main():
    keyword = "올리빙 도트 아이스박스 21L 민트"
    html = await CoupangHtmlFetcher(quote(keyword)).fetch_html()

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