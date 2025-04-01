from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
import time

def fetch_product_detail(page, pcode: str, cate_code: str) -> dict:
    """상품 상세 페이지에서 제조사와 등록일 정보를 추출합니다."""
    url = f"https://prod.danawa.com/info/?pcode={pcode}&cate={cate_code}"
    
    try:
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        html = page.content()
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
    except Exception as e:
        print(f"⚠️ 상세 정보 수집 실패 (pcode: {pcode}): {e}")
        return {"manufacturer": None, "manufactured_date": None}

def extract_pcode_from_url(url):
    """URL에서 pcode를 추출합니다."""
    match = re.search(r'pcode=(\d+)', url)
    if match:
        return match.group(1)
    return None

def scrape_products(group_code: str, cate_name: str, category_code: str, referer_cate_code: str, depth: str = "2", end_page: int = 5, collect_details: bool = True):
    url = "https://prod.danawa.com/list/ajax/getProductList.ajax.php"
    all_items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 상세 정보를 수집할 별도의 페이지 생성
        detail_page = context.new_page() if collect_details else None

        for page_num in range(1, end_page + 1):
            print(f"\U0001F4C4 페이지 {page_num} 수집 중...")
            params = {
                "btnAllOptUse": "false",
                "priceRangeMinPrice": "",
                "priceRangeMaxPrice": "",
                "page": str(page_num),
                "listCategoryCode": category_code,
                "categoryCode": category_code,
                "viewMethod": "LIST",
                "sortMethod": "BEST",
                "listCount": "90",
                "group": group_code,
                "depth": depth,
            }

            form_data = urlencode(params)

            response = page.request.post(
                url,
                data=form_data,
                headers={
                    "Accept": "text/html, */*; q=0.01",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Host": "prod.danawa.com",
                    "Origin": "https://prod.danawa.com",
                    "Referer": f"https://prod.danawa.com/list/?cate={referer_cate_code}",
                    "Sec-Ch-Ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": "\"Windows\"",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            html = response.text()
            soup = BeautifulSoup(html, "html.parser")

            items = []
            for item in soup.select(".prod_item"):
                try:
                    image_tag = item.select_one(".thumb_image img")
                    image_url = image_tag.get("src") or image_tag.get("data-original")

                    options = item.select(".spec_list a, .spec_list span, .spec_list div")
                    option_texts = [opt.get_text(strip=True) for opt in options]
                    
                    product_url = item.select_one(".prod_name a").get("href")
                    
                    product_data = {
                        "id": item.get("id"),
                        "category_code": item.select_one("input[id^=productItem_categoryInfo]").get("value", ""),
                        "category": cate_name,
                        "name": item.select_one(".prod_name a").get_text(strip=True),
                        "url": product_url,
                        "image": image_url,
                        "spec": item.select_one(".spec_list").get_text(" / ", strip=True) if item.select_one(".spec_list") else "",
                        "price": item.select_one(".price_sect strong").get_text(strip=True),
                        "date": item.select_one(".meta_item.mt_date dd").get_text(strip=True) if item.select_one(".meta_item.mt_date dd") else "",
                        "option": option_texts,
                        "manufacturer": None,
                        "manufactured_date": None,
                    }
                    
                    # 상세 정보 수집 (제조사, 등록월)
                    if collect_details:
                        pcode = extract_pcode_from_url(product_url)
                        if pcode:
                            print(f"  📌 '{product_data['name']}' 상세 정보 수집 중...")
                            details = fetch_product_detail(detail_page, pcode, referer_cate_code)
                            product_data.update(details)
                            # 과도한 요청을 방지하기 위한 짧은 대기
                            time.sleep(0.5)
                        else:
                            print(f"  ⚠️ '{product_data['name']}' pcode를 찾을 수 없습니다.")
                    
                    items.append(product_data)
                except Exception as e:
                    print(f"⚠️ 파싱 실패: {e}")

            if not items:
                print("\U0001F6D1 더 이상 상품이 없습니다. 중단합니다.")
                break

            all_items.extend(items)
            print(f"  ✅ {len(items)}개 상품 정보 수집 완료 (총 {len(all_items)}개)")

        browser.close()

    # 저장
    safe_name = "".join(c for c in cate_name if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
    filename = f"products_{safe_name}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 총 {len(all_items)}개의 상품이 저장되었습니다: {filename}")
    return all_items


if __name__ == "__main__":
    group_code = "13"
    cate_name = "텐트"
    cate_code = "437"
    ref_cate_code = "132437"
    end_page = 2  # 테스트를 위해 페이지 수 감소 (운영 시 원하는 수로 변경)
    
    # 상세 정보(제조사, 등록월)까지 수집
    scrape_products(group_code, cate_name, cate_code, ref_cate_code, end_page=end_page, collect_details=True)