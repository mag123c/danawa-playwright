import json
import os
from datetime import datetime
from dataclasses import asdict
from typing import Any, Optional

def save_as_json(
    data: list[Any] | dict[str, Any],
    category_name: str,
    file_prefix: str = "",
    base_dir: Optional[str] = None,
    sub_dir: Optional[str] = None 
):
    now = datetime.now()

    # 항상 루트는 고정
    root_dir = base_dir or "danawa_output"
    date_str = now.strftime("%Y%m%d")
    date_dir = f"{date_str}"

    # 실제 저장 디렉토리
    safe_category = "".join(c for c in category_name if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
    target_dir = os.path.join(root_dir, date_dir, safe_category)

    if sub_dir:
        target_dir = os.path.join(target_dir, sub_dir)

    os.makedirs(target_dir, exist_ok=True)

    timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp_str}_{file_prefix}.json" if file_prefix else f"{timestamp_str}.json"
    file_path = os.path.join(target_dir, filename)

    # 직렬화 처리
    if isinstance(data, list):
        serialized = [asdict(d) if hasattr(d, "__dataclass_fields__") else d for d in data]
    else:
        serialized = asdict(data) if hasattr(data, "__dataclass_fields__") else data

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=2, ensure_ascii=False)

    print(f"✅ 저장 완료: {file_path}")
