import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus

def fetch_coupang_product_titles():
    keyword = "올리빙 도트 아이스박스 21L"
    encoded_keyword = quote_plus(keyword)
    url = f"https://www.coupang.com/np/search?q={encoded_keyword}"

    options = Options()
    options.add_argument("--disable-http2")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-features=UseBlinkFeatures")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("--headless=new")  # 필요 시 헤드리스

    # User-Agent 설정
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        # 동적 로딩 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ul#productList > li:not(.search-product__ad-badge) div.name")
            )
        )

        time.sleep(1)  # 추가 대기

        elements = driver.find_elements(By.CSS_SELECTOR, "ul#productList > li:not(.search-product__ad-badge) div.name")
        product_titles = [el.text.strip() for el in elements if el.text.strip()]

        print(f"🔍 요청 URL: {url}")
        print(f"상품 수: {len(product_titles)}개")
        print(f"상품명: {product_titles}")
        return product_titles

    finally:
        driver.quit()


if __name__ == "__main__":
    titles = fetch_coupang_product_titles()
    for idx, title in enumerate(titles, 1):
        print(f"{idx}. {title}")
