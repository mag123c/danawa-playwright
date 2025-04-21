from dataclasses import dataclass, field
from typing import Optional
from .equipment_spec import EquipmentSpecs

@dataclass
class Equipment:
    id: str
    name: str
    main_category: str
    sub_category: str
    detail_url: str
    image_url: str
    raw_specs: str
    price: str
    maker: str
    registered_date: Optional[str]
    review_count: Optional[int] = None
    score_count: Optional[float] = None
    specs: EquipmentSpecs = field(default_factory=EquipmentSpecs)
    reviews: Optional[list] = field(default_factory=list)
