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
    material: Optional[str] = None 
    color: Optional[str] = None
    usage: Optional[str] = None
    insulation: Optional[str] = None
    inner_volume: Optional[str] = None
    extra: Optional[str] = None
    
    
    # Boolean 속성 (description_bool 기반)    
    has_wheel: Optional[str] = None              # 바퀴 포함 여부
    has_drain: Optional[str] = None              # 물배출구 포함 여부
    has_table: Optional[str] = None              # 테이블 기능 포함 여부
    has_inner_basket: Optional[str] = None       # 내부수납 구조 포함 여부
    has_lid_open: Optional[str] = None            # 뚜껑부분 개폐 여부
    has_shoulder_strap: Optional[str] = None     # 어깨끈 포함 여부

    # 쿨러백 / 차량용냉온냉장고 전용 추가 속성
    has_smartphone_connect: Optional[str] = None # 스마트폰 연동 기능
    has_movable_wheel: Optional[str] = None      # 이동식 바퀴 포함 여부
    has_handle: Optional[str] = None             # 손잡이 포함 여부
    has_charging_port: Optional[str] = None      # 충전 포트 포함 여부
    has_temp_display: Optional[str] = None       # 온도 표시 기능 여부
    has_inner_led: Optional[str] = None          # 내부 LED 포함 여부
    has_cup_holder: Optional[str] = None         # 컵홀더 포함 여부