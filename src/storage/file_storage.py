import json
import os
from datetime import datetime
from dataclasses import asdict
from src.domain.equipment import Equipment

def save_as_json(equipments: list[Equipment], category_name: str):
    now = datetime.now()
    root_dir = f"danawa_{now.strftime('%Y%m%d')}"
    time_str = now.strftime("%H_%M_%S")

    safe_category = "".join(c for c in category_name if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
    target_dir = os.path.join(root_dir, safe_category)
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, f"{time_str}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in equipments], f, indent=2, ensure_ascii=False)

    print(f"✅ 저장 완료: {file_path}")
