from bs4 import Tag
from playwright.sync_api import Page

from src.domain.equipment import Equipment, EquipmentSpecs
from src.parser.spec_rules_registry import SpecRuleRegistry
from src.service.review_score_calculator import calculate_review_scores
from src.parser.review_parser import DanawaReviewParser
from src.storage.file_storage import save_as_json

class ProductParser:
    @staticmethod
    def parse_product_item(item: Tag, sub_category: str, page: Page, base_dir: str) -> Equipment:
        id = item.get("id")
        product_no = id.replace("productItem", "")

        name = item.select_one(".prod_name a").get_text(strip=True)
        main_category = item.select_one("input[id^=productItem_categoryInfo]").get("value", "")
        detail_url = item.select_one(".prod_name a").get("href")
        image_url = item.select_one(".thumb_image img").get("src")
        if image_url and not image_url.startswith("http"):
            image_url = "https:" + image_url
        specs_text = item.select_one(".spec_list").get_text(" / ", strip=True) if item.select_one(".spec_list") else ""
        price = item.select_one(".price_sect strong").get_text(strip=True)
        maker = item.select_one(".price_sect button[data-maker-name]").get("data-maker-name", "")
        registered_date = item.select_one(".meta_item.mt_date dd").get_text(strip=True) if item.select_one(".meta_item.mt_date dd") else None

        parsed_specs = ProductParser._parse_specs(specs_text, sub_category)

        # 리뷰 수집
        review_parser = DanawaReviewParser(page)
        reviews = review_parser.get_reviews(product_code=product_no)

        if reviews:
            print(f"📝 리뷰 수집 완료: {len(reviews)}개 → {product_no} ({name})")            
            save_as_json(
                {"no": product_no, "reviews": reviews, "url": detail_url},
                category_name=sub_category,
                file_prefix=f"{product_no}-review",
                base_dir=base_dir
            )
            review_texts = [r["content"] for r in reviews if r.get("content")]
        else:
            print(f"📝 리뷰 없음 → {product_no} ({name})")
            review_texts = []

        return Equipment(
            id=id,
            name=name,
            main_category=main_category,
            sub_category=sub_category,
            detail_url=detail_url,
            image_url=image_url,
            raw_specs=specs_text,
            price=price,
            maker=maker,
            registered_date=registered_date,
            specs=parsed_specs,
            reviews=review_texts,
        )

    @staticmethod
    def _parse_specs(spec_text: str, sub_category: str) -> EquipmentSpecs:
        specs = EquipmentSpecs()
        registry = SpecRuleRegistry(sub_category=sub_category)
        fragments = [frag.strip() for frag in spec_text.split("/") if frag.strip()]

        for frag in fragments:
            sub_fragments = [s.strip() for s in frag.split(",")] if "," in frag else [frag]

            for sub_frag in sub_fragments:
                results = registry.parse_fragment(sub_frag)
                if results:
                    for key, value in results:
                        setattr(specs, key, value)

                        if key != "description" and key.startswith("has_"):
                            specs.description = (
                                f"{specs.description}, {sub_frag}" if specs.description else sub_frag
                            )
                else:
                    specs.extra = f"{specs.extra} / {sub_frag}" if specs.extra else sub_frag

        return specs
