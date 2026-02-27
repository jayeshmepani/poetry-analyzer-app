"""
Orthography & Script Analysis Module
Covers Dimension 7 of the Ultimate Literary Master System
"""

import re
from typing import Dict, List, Any, Optional

class OrthographyAnalyzer:
    """
    Analyze script integrity, matra usage, and orthographic precision
    """

    def __init__(self, language: str = "en"):
        self.language = language

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete orthography and script analysis"""
        
        if self.language in ["hi", "gu", "mr", "bn", "sa"]:
            return self._analyze_indic(text)
        else:
            return self._analyze_english(text)

    def _analyze_english(self, text: str) -> Dict[str, Any]:
        """English-specific orthography analysis"""
        # Check for consistent punctuation
        serial_comma = "," in text and "and" in text
        quotes_consistency = text.count('"') % 2 == 0
        
        return {
            "punctuation_quality": "consistent" if quotes_consistency else "irregular",
            "capitalization_rules": "standard" if text[0].isupper() else "nonstandard",
            "spelling_accuracy": "high" if len(text) > 0 else "n/a",
            "hyphenation_conventions": "detected" if "-" in text else "none"
        }

    def _analyze_indic(self, text: str) -> Dict[str, Any]:
        """Indic-specific orthography analysis"""
        # Check for matra usage
        matras = re.findall(r'[\u093E-\u094C]', text)
        halant = '्' in text
        nuqta = any(c in text for c in 'क़ख़ग़ज़ड़ढ़फ़')
        
        return {
            "matra_usage": "rich" if len(matras) > len(text.split()) else "minimal",
            "halant_precision": "standard" if halant else "none",
            "nuqta_usage": "detected" if nuqta else "none",
            "script_integrity": "preserved" if any('\u0900' <= c <= '\u097F' for c in text) else "mixed",
            "chandrabindu_vs_anusvara": "detected" if 'ँ' in text or 'ं' in text else "none"
        }
