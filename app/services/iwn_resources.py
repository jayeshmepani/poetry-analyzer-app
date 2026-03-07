"""
IndoWordNet resource helpers.
Guards IndoWordNet usage behind actual on-disk language data checks.
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Optional

from app.config import settings

_IWN_LANG_FILE_MAP = {
    "hi": "hindi",
    "gu": "gujarati",
    "ur": "urdu",
    "mr": "marathi",
    "bn": "bengali",
    "sa": "sanskrit",
    "ta": "tamil",
    "te": "telugu",
    "kn": "kannada",
    "ml": "malayalam",
    "pa": "punjabi",
}


def iwn_data_exists_for_language(language: str) -> bool:
    iwn_root = resolve_iwn_data_dir()
    synsets_dir = iwn_root / "synsets"
    file_stub = _IWN_LANG_FILE_MAP.get(language, language)
    candidates = (
        synsets_dir / f"all.{file_stub}",
        synsets_dir / f"all.{language}",
    )
    return any(path.exists() for path in candidates)


def _candidate_iwn_files(language: str) -> tuple[Path, Path]:
    iwn_root = resolve_iwn_data_dir()
    synsets_dir = iwn_root / "synsets"
    file_stub = _IWN_LANG_FILE_MAP.get(language, language)
    return (
        synsets_dir / f"all.{file_stub}",
        synsets_dir / f"all.{language}",
    )


def iwn_runtime_supported(language: str) -> bool:
    """
    True when IndoWordNet can be safely used in this runtime.
    Prevents Windows non-UTF8 decode failures inside pyiwn.
    """
    if not iwn_data_exists_for_language(language):
        return False
    # pyiwn uses default text encoding on some read paths; on Windows this
    # can be cp1252 and trigger charmap decode errors for Indic corpora.
    if os.name == "nt" and getattr(sys.flags, "utf8_mode", 0) != 1:
        return False
    try:
        for path in _candidate_iwn_files(language):
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    f.read(4096)
                return True
    except Exception:
        return False
    return False


def silence_pyiwn_info_logs() -> None:
    logging.getLogger("pyiwn.iwn").setLevel(logging.WARNING)


def resolve_iwn_data_dir() -> Path:
    configured = Path(os.path.abspath(settings.lexical.iwn_data_dir))
    user_home_iwn = Path(os.path.expanduser("~")) / "iwn_data"
    candidates = [configured, user_home_iwn]
    for base in candidates:
        synsets = base / "synsets"
        if synsets.exists() and any(synsets.glob("all.*")):
            return base
    return configured


def get_iwn_language_enum(language: str) -> Optional[object]:
    try:
        from pyiwn import Language
    except Exception:
        return None
    return {
        "hi": Language.HINDI,
        "gu": Language.GUJARATI,
        "ur": Language.URDU,
        "mr": Language.MARATHI,
        "bn": Language.BENGALI,
        "sa": Language.SANSKRIT,
        "ta": Language.TAMIL,
        "te": Language.TELUGU,
        "kn": Language.KANNADA,
        "ml": Language.MALAYALAM,
        "pa": Language.PUNJABI,
    }.get(language, Language.HINDI)
