from bs4 import Tag
from src.domain.equipment import Equipment, EquipmentSpecs
from src.parser.spec_rules_registry import SpecRuleRegistry

class ProductParser:
    spec_registry = SpecRuleRegistry()

    @staticmethod
    def parse_product_item(item: Tag, sub_category: str) -> Equipment:
        id = item.get("id")
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

        parsed_specs = ProductParser._parse_specs(specs_text)

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
            specs=parsed_specs
        )

    @staticmethod
    def _parse_specs(spec_text: str) -> EquipmentSpecs:
        specs = EquipmentSpecs()
        fragments = [frag.strip() for frag in spec_text.split("/") if frag.strip()]
        for frag in fragments:
            result = ProductParser.spec_registry.parse_fragment(frag)
            if result:
                key, value = result
                setattr(specs, key, value)
            else:
                specs.extra = f"{specs.extra} / {frag}" if specs.extra else frag
        return specs
