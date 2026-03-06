"""
Touchstone passage loader
Uses real literary corpora (NLTK Gutenberg) to avoid hardcoded passages.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import List


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


@lru_cache(maxsize=1)
def _gutenberg_sentences() -> List[str]:
    try:
        import nltk
        from nltk.corpus import gutenberg
        from nltk.tokenize import sent_tokenize
    except Exception:
        return []

    sentences: List[str] = []
    try:
        for fileid in gutenberg.fileids():
            raw = gutenberg.raw(fileid)
            for sent in sent_tokenize(raw):
                words = _tokenize(sent)
                if 6 <= len(words) <= 30:
                    sentences.append(sent.strip())
    except Exception:
        return []

    return sentences


def select_touchstone_passages(text: str, limit: int = 4) -> List[str]:
    """
    Select touchstone passages dynamically from Gutenberg corpus
    using Jaccard similarity to the input text.
    """
    candidates = _gutenberg_sentences()
    if not candidates:
        return []

    target = set(_tokenize(text))
    if not target:
        return candidates[:limit]

    scored = []
    for sent in candidates:
        words = set(_tokenize(sent))
        if not words:
            continue
        overlap = len(words & target) / max(1, len(words | target))
        scored.append((overlap, sent))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:limit]]
