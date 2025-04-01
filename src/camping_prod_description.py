from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

def fetch_product_detail(pcode: str, cate_code: str) -> dict:
    url = f"https://prod.danawa.com/info/?pcode={pcode}&cate={cate_code}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    maker = None
    date = None

    made_info_div = soup.select_one("div.made_info")
    
    if made_info_div:
        spans = made_info_div.select("span.txt")
        
        for span in spans:
            text = span.get_text(strip=True)
            
            if "등록월" in text:
                date = re.sub(r'등록월\s*:\s*', '', text).strip()
            
            if span.get('id') == 'makerTxtArea' or "제조사" in text:
                maker_link = span.select_one("a")
                if maker_link:
                    maker = maker_link.get_text(strip=True)
                else:
                    maker = re.sub(r'제조사\s*:\s*', '', text).strip()

    if not maker or not date:
        spec_list = soup.select("div.spec_list")
        for spec in spec_list:
            rows = spec.select("tr")
            for row in rows:
                th = row.select_one("th")
                td = row.select_one("td")
                
                if th and td:
                    label = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    
                    if "제조" in label and not maker:
                        maker = value
                    elif "등록" in label and "월" in label and not date:
                        date = value
    
    return {
        "manufacturer": maker,
        "manufactured_date": date
    }

if __name__ == "__main__":
    test_pcode = "17610188"
    cate_code = "132437"
    result = fetch_product_detail(test_pcode, cate_code)
    print(result)