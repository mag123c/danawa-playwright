class AffiliateLinkGenerator:
    def __init__(self, affiliate_id: str):
        self.affiliate_id = affiliate_id

    def generate(self, prod: CoupangProduct) -> str:
        base = f"https://www.coupang.com/vp/products/{prod.product_id}"
        params = {
            "itemId": prod.item_id,
            "vendorItemId": prod.vendor_item_id,
            "subId": self.affiliate_id  # 제휴코드
        }
        return f"{base}?{urlencode(params)}"