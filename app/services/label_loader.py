import json
from pathlib import Path
from functools import lru_cache
from typing import List, Optional, Dict, Any

_LABELS_PATH = Path(__file__).resolve().parents[2] / "data" / "labels" / "labels.json"


@lru_cache(maxsize=1)
def _load_labels() -> Dict[str, Any]:
    try:
        return json.loads(_LABELS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_labels(key: str, default: Optional[List[str]] = None) -> List[str]:
    labels = _load_labels().get(key)
    if isinstance(labels, list) and labels:
        return labels
    return default or []
