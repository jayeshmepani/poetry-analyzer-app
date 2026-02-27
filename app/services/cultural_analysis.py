"""
Cultural & Historical Analysis Module
Covers Dimension 6 of the Ultimate Literary Master System
"""

import re
from typing import Dict, List, Any, Optional

class CulturalAnalyzer:
    """
    Analyze period accuracy, cultural authenticity, and anachronisms
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.period_markers = {
            "medieval": ["thou", "thee", "thy", "hath", "doth", "shalt", "knave", "knight"],
            "victorian": ["propriety", "earnest", "gentleman", "lady", "virtue", "industry"],
            "modern": ["internet", "phone", "car", "city", "street", "modern", "fast"],
            "internet_age": ["lol", "app", "click", "web", "online", "post", "social"]
        }
        
        self.cultural_contexts = {
            "western": ["logic", "individual", "liberty", "freedom", "hero"],
            "indic": ["dharma", "karma", "rasa", "bhakti", "shanti", "yoga"],
            "persian_arabic": ["ishq", "junoon", "shayeri", "dil", "mehefil"]
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete cultural and historical analysis"""
        text_lower = text.lower()
        
        return {
            "period_accuracy": self._detect_period(text_lower),
            "cultural_authenticity": self._detect_culture(text_lower),
            "anachronism_detection": self._check_anachronisms(text_lower),
            "sociolinguistic_accuracy": self._analyze_sociolinguistics(text_lower)
        }

    def _detect_period(self, text: str) -> Dict[str, Any]:
        """Detect historical period of language"""
        scores = {p: sum(text.count(m) for m in markers) for p, markers in self.period_markers.items()}
        detected = max(scores, key=scores.get) if any(scores.values()) else "contemporary"
        
        return {
            "detected_period": detected,
            "scores": scores,
            "historical_language_usage": "high" if scores.get("medieval", 0) > 0 else "low"
        }

    def _detect_culture(self, text: str) -> Dict[str, Any]:
        """Detect cultural context and authenticity"""
        scores = {c: sum(text.count(m) for m in markers) for c, markers in self.cultural_contexts.items()}
        primary = max(scores, key=scores.get) if any(scores.values()) else "universal"
        
        return {
            "primary_cultural_context": primary,
            "scores": scores,
            "cultural_reference_precision": "consistent" if any(scores.values()) else "general"
        }

    def _check_anachronisms(self, text: str) -> List[Dict[str, str]]:
        """Detect potential anachronisms"""
        anachronisms = []
        # If medieval but contains modern words
        medieval_score = sum(text.count(m) for m in self.period_markers["medieval"])
        if medieval_score > 2:
            modern_words = self.period_markers["modern"] + self.period_markers["internet_age"]
            for word in modern_words:
                if word in text:
                    anachronisms.append({"word": word, "type": "modern_term_in_archaic_context"})
        
        return anachronisms

    def _analyze_sociolinguistics(self, text: str) -> Dict[str, Any]:
        """Analyze sociolinguistic markers"""
        has_code_switching = False
        if self.language == "hi" and any(w in text.lower() for w in ["the", "is", "a", "of"]):
            has_code_switching = True
            
        return {
            "code_switching_detected": has_code_switching,
            "register_match": "appropriate" if len(text.split()) > 10 else "needs_context"
        }
