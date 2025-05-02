import asyncio
from typing import List, Dict
from playwright.async_api import async_playwright
from src.parser.asynchronous.review_parser import DanawaReviewAsyncParser
from src.storage.file_storage import save_as_json

async def limited_collect_review(semaphore, *args, **kwargs):
    async with semaphore:
        return await collect_review(*args, **kwargs)

async def collect_review(page, product_no: str, sub_category: str, base_dir: str) -> dict:
    parser = DanawaReviewAsyncParser(page)
    reviews = await parser.get_reviews(product_no)

    if reviews:
        print(f"📝 리뷰 수집 완료: {len(reviews)}개 → {product_no}")
        review_texts = [r["content"] for r in reviews if r.get("content")]
        save_as_json({"no": product_no, "reviews": review_texts}, sub_category, f"{product_no}-review", base_dir, "reviews")
    else:
        print(f"📝 리뷰 없음 → {product_no}")
        review_texts = []

    return product_no, review_texts

async def collect_reviews_concurrently(product_list: List[dict], sub_category: str, base_dir: str) -> Dict[str, List[str]]:
    result = {}
    semaphore = asyncio.Semaphore(10)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        tasks = []
        for prod in product_list:
            page = await context.new_page()
            product_no = prod.id.replace("productItem", "")
            tasks.append(collect_review(page, product_no, sub_category, base_dir))
            tasks.append(
                limited_collect_review(semaphore, page, product_no, sub_category, base_dir)
            )

        results = await asyncio.gather(*tasks)
        await browser.close()

        for pid, texts in results:
            result[pid] = texts
        return result