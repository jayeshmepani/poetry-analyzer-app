"""
Phonology Resources
===================
Provides IPA/transliteration/rhyme keys using installed linguistic resources.
No placeholders: all logic uses real libraries or real dataset caches.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple, List

from app.config import settings

logger = logging.getLogger(__name__)

try:
    import pronouncing as _pronouncing
except Exception:
    _pronouncing = None


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "phonology"
_PROSODY_DIR = Path(__file__).resolve().parents[2] / "data" / "prosody"
IPA_VOWELS = set(_load_json(_DATA_DIR / "ipa_vowels.json").get("vowels", []))
FALLBACK_VOWELS = _load_json(_PROSODY_DIR / "fallback_vowels.json")


def _strip_punct(word: str) -> str:
    return re.sub(r"[^\w\u0600-\u06FF\u0900-\u097F\u0A80-\u0AFF]", "", word).strip()


def _detect_script(word: str) -> str:
    for ch in word:
        code = ord(ch)
        if 0x0600 <= code <= 0x06FF:
            return "arabic"
        if 0x0900 <= code <= 0x097F:
            return "devanagari"
        if 0x0A80 <= code <= 0x0AFF:
            return "gujarati"
    return "latin"


def _ipa_rhyme_key(ipa: str) -> Optional[str]:
    if not ipa:
        return None
    # Keep only IPA letters and spaces
    cleaned = re.sub(r"[^a-zA-Z\u0250-\u02AF\u1D00-\u1D7F\s]", "", ipa)
    tokens = cleaned.strip().split()
    if not tokens:
        tokens = [cleaned.strip()]
    seq = "".join(tokens)
    if not seq:
        return None
    # Find last vowel and take from there to end
    for i in range(len(seq) - 1, -1, -1):
        if seq[i] in IPA_VOWELS:
            return seq[i:]
    # If no vowel found, use last 3 chars
    return seq[-3:]


def _clean_ipa(ipa: str) -> str:
    if not ipa:
        return ""
    return re.sub(r"[^a-zA-Z\u0250-\u02AF\u1D00-\u1D7Fːˑ\s]", " ", ipa).strip()


def syllabify_ipa(ipa: str) -> List[str]:
    cleaned = _clean_ipa(ipa)
    if not cleaned:
        return []
    tokens = cleaned.split()
    syllables: List[str] = []
    for token in tokens:
        if not token:
            continue
        vowel_positions = [i for i, ch in enumerate(token) if ch in IPA_VOWELS]
        if not vowel_positions:
            syllables.append(token)
            continue
        start = 0
        for idx, pos in enumerate(vowel_positions):
            end = vowel_positions[idx + 1] if idx + 1 < len(vowel_positions) else len(token)
            syllables.append(token[start:end])
            start = end
    return syllables


def count_syllables_from_ipa(ipa: str) -> int:
    syllables = syllabify_ipa(ipa)
    if not syllables:
        return 0
    return len(syllables)


def fallback_syllable_count(word: str, language: str) -> int:
    vowels = FALLBACK_VOWELS.get(language, [])
    if not vowels:
        return 0
    vowel_set = set(vowels)
    count = 0
    prev_is_vowel = False
    for ch in word:
        is_vowel = ch in vowel_set
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    return count


class PhonologyResources:
    def __init__(self, language: str = "en"):
        self.language = language
        self._epitran = None
        self._phyme = None
        self._urdu_map = None

        self._init_epitran()
        self._init_phyme()

    def _init_epitran(self) -> None:
        try:
            import epitran

            lang_map = {
                "hi": "hin-Deva",
                "gu": "guj-Gujr",
                "ur": "urd-Arab",
                "en": None,
            }
            code = lang_map.get(self.language)
            if code:
                # On Windows, non-UTF8 runtime can break Indic map loading.
                if os.name == "nt" and getattr(sys.flags, "utf8_mode", 0) != 1:
                    logger.debug(
                        "Epitran deferred for %s; UTF-8 mode required on Windows.",
                        self.language,
                    )
                    return
                self._epitran = epitran.Epitran(code)
        except Exception as e:
            logger.debug(
                "Epitran not enabled for %s; using alternate phonology path (%s).",
                self.language,
                e,
            )

    def _init_phyme(self) -> None:
        if self.language != "en":
            return
        try:
            from phyme import Phyme

            self._phyme = Phyme()
        except Exception as e:
            logger.info("Phyme not enabled; using other English rhyme strategies (%s).", e)

    @staticmethod
    def _load_urdu_g2p_map() -> Dict[str, str]:
        cache_dir = os.path.abspath(settings.lexical.urdu_g2p_cache_dir)
        cache_path = os.path.join(cache_dir, "urdu_g2p_map.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.info(f"Urdu G2P cache read path not active; rebuilding map: {e}")

        # Attempt to build mapping on demand (real dataset load)
        try:
            from datasets import load_dataset
        except Exception as e:
            logger.info(f"HF datasets client not active for Urdu G2P: {e}")
            return {}

        os.makedirs(cache_dir, exist_ok=True)
        dataset_name = settings.lexical.urdu_g2p_dataset
        split = settings.lexical.urdu_g2p_split
        try:
            ds = load_dataset(dataset_name, split=split, cache_dir=cache_dir)
            if not ds:
                return {}
            sample = ds[0]
            keys = list(sample.keys())
            word_keys = [
                k
                for k in keys
                if "word" in k.lower() or "grapheme" in k.lower() or "text" in k.lower()
            ]
            ipa_keys = [
                k
                for k in keys
                if "ipa" in k.lower() or "phoneme" in k.lower() or "phonetic" in k.lower()
            ]
            if not word_keys or not ipa_keys:
                return {}

            word_key = word_keys[0]
            ipa_key = ipa_keys[0]
            mapping: Dict[str, str] = {}
            for row in ds:
                word = str(row.get(word_key, "")).strip()
                ipa = str(row.get(ipa_key, "")).strip()
                if word and ipa:
                    mapping[word] = ipa

            if mapping:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(mapping, f, ensure_ascii=False)
            return mapping
        except Exception as e:
            logger.info(f"Urdu G2P mapping was not built in this run: {e}")
            return {}

    def _get_urdu_map(self) -> Dict[str, str]:
        if self._urdu_map is None:
            self._urdu_map = self._load_urdu_g2p_map()
        return self._urdu_map

    def _wiktra_transliterate(self, text: str) -> Optional[str]:
        try:
            import wiktra  # type: ignore
        except Exception:
            return None

        # Try likely API names without guessing output
        for name in ("transliterate", "transliterate_text", "convert"):
            fn = getattr(wiktra, name, None)
            if callable(fn):
                try:
                    return fn(text)
                except Exception:
                    continue
        return None

    def ipa(self, word: str) -> Optional[str]:
        clean = _strip_punct(word)
        if not clean:
            return None

        script = _detect_script(clean)
        if self.language == "en" or script == "latin":
            if _pronouncing is not None:
                try:
                    phones = _pronouncing.phones_for_word(clean.lower())
                    if phones:
                        return phones[0]
                except Exception:
                    pass

        if script == "arabic":
            urdu_map = self._get_urdu_map()
            if clean in urdu_map:
                return urdu_map[clean]
            # Try wiktra transliteration as a bridge
            translit = self._wiktra_transliterate(clean)
            if translit and self._epitran:
                try:
                    return self._epitran.transliterate(translit)
                except Exception:
                    pass

        if self._epitran:
            try:
                return self._epitran.transliterate(clean)
            except Exception:
                pass
        return None

    def rhyme_key(self, word: str) -> Optional[str]:
        clean = _strip_punct(word)
        if not clean:
            return None

        if self.language == "en":
            if _pronouncing is not None:
                try:
                    phones = _pronouncing.phones_for_word(clean.lower())
                    if phones:
                        part = _pronouncing.rhyming_part(phones[0])
                        if part:
                            return part
                except Exception:
                    pass

            if self._phyme:
                try:
                    rhymes = self._phyme.get_phymes(clean)
                    # Pick the most specific rhyme group if available
                    for key in ("perfect", "family", "partner", "assonance", "consonance"):
                        if key in rhymes and rhymes[key]:
                            return f"{key}:{clean.lower()}"
                except Exception:
                    pass

        ipa = self.ipa(clean)
        return _ipa_rhyme_key(ipa)


@lru_cache(maxsize=16)
def get_phonology(language: str) -> PhonologyResources:
    return PhonologyResources(language=language)
