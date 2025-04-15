from dataclasses import dataclass
from typing import Optional

@dataclass
class EquipmentSpecs:
    size: Optional[str] = None
    capacity: Optional[str] = None
    weight: Optional[str] = None
    voltage: Optional[str] = None
    features: Optional[str] = None
    temperature_range: Optional[str] = None
    power_consumption: Optional[str] = None
    description: Optional[str] = None
    extra: Optional[str] = None
