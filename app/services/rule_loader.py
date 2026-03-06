import json
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any

_RULES_DIR = Path(__file__).resolve().parents[2] / "data" / "rules"


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


@lru_cache(maxsize=1)
def get_style_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "style_categories.json")


@lru_cache(maxsize=1)
def get_form_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "form_detection.json")


@lru_cache(maxsize=1)
def get_thresholds() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "thresholds.json")


@lru_cache(maxsize=1)
def get_ghazal_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "ghazal_verifier.json")


@lru_cache(maxsize=1)
def get_structural_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "structural_rules.json")


@lru_cache(maxsize=1)
def get_literary_device_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "literary_device_rules.json")


@lru_cache(maxsize=1)
def get_performance_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "performance_rules.json")


@lru_cache(maxsize=1)
def get_output_limits() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "output_limits.json")


@lru_cache(maxsize=1)
def get_evaluation_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "evaluation_rules.json")


@lru_cache(maxsize=1)
def get_analysis_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "analysis_rules.json")


@lru_cache(maxsize=1)
def get_advanced_analysis_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "advanced_analysis_rules.json")


def get_quantitative_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "quantitative_rules.json")


@lru_cache(maxsize=1)
def get_constraints_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "constraints_rules.json")


@lru_cache(maxsize=1)
def get_literary_theory_rules() -> Dict[str, Any]:
    return _load_json(_RULES_DIR / "literary_theory_rules.json")
