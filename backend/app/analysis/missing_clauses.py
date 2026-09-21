import os
import yaml
from typing import List, Dict

def load_checklist(doc_type: str, checklists_dir: str | None = None) -> List[Dict[str, str]]:
    if checklists_dir is None:
        from app.core.settings import settings
        checklists_dir = str(settings.data_dir / "checklists")
    path = os.path.join(checklists_dir, f"{doc_type}.yaml")
    if not os.path.exists(path):
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("checklist", [])
