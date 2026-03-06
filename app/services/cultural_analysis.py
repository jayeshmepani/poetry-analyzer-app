"""
Cultural & Historical Analysis Module
Covers Dimension 6 of the Ultimate Literary Master System
"""

import re
from typing import Dict, List, Any, Optional
from transformers import pipeline
from app.config import Settings
from app.services.label_loader import get_labels
from app.services.rule_loader import get_thresholds

class CulturalAnalyzer:
    """
    Analyze period accuracy, cultural authenticity, and anachronisms
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self._settings = Settings()
        self._zero_shot = None

    def _ensure_zero_shot(self):
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            model_name = self._settings.transformer.generalist_zero_shot_model
            self._zero_shot = pipeline("zero-shot-classification", model=model_name, device=-1)
        except Exception:
            self._zero_shot = None
        return self._zero_shot

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
        zs = self._ensure_zero_shot()
        labels = get_labels("cultural_period")
        if not labels:
            return {
                "detected_period": "contemporary",
                "scores": {},
                "historical_language_usage": "low",
            }
        scores = {l: 0.0 for l in labels}
        if zs:
            try:
                out = zs(text, labels)
                scores = {label: float(score) for label, score in zip(out["labels"], out["scores"])}
            except Exception:
                pass
        detected = max(scores, key=scores.get) if any(scores.values()) else "contemporary"

        return {
            "detected_period": detected,
            "scores": scores,
            "historical_language_usage": "high" if "medieval" in detected else "low"
        }

    def _detect_culture(self, text: str) -> Dict[str, Any]:
        """Detect cultural context and authenticity"""
        zs = self._ensure_zero_shot()
        labels = get_labels("cultural_context")
        if not labels:
            return {
                "primary_cultural_context": "universal",
                "scores": {},
                "cultural_reference_precision": "general",
            }
        scores = {l: 0.0 for l in labels}
        if zs:
            try:
                out = zs(text, labels)
                scores = {label: float(score) for label, score in zip(out["labels"], out["scores"])}
            except Exception:
                pass
        primary = max(scores, key=scores.get) if any(scores.values()) else "universal"

        return {
            "primary_cultural_context": primary,
            "scores": scores,
            "cultural_reference_precision": "consistent" if any(scores.values()) else "general"
        }

    def _check_anachronisms(self, text: str) -> List[Dict[str, str]]:
        """Detect potential anachronisms"""
        anachronisms = []
        zs = self._ensure_zero_shot()
        thresholds = get_thresholds()
        min_conf = thresholds.get("zero_shot_min_confidence")
        if min_conf is None:
            return anachronisms
        if zs:
            try:
                period = self._detect_period(text).get("detected_period", "")
                if "medieval" in period:
                    for line in text.split("\n"):
                        if not line.strip():
                            continue
                        anachronism_labels = get_labels("anachronism")
                        if not anachronism_labels:
                            continue
                        out = zs(line, anachronism_labels)
                        if out["labels"][0] == "modern term" and float(out["scores"][0]) >= min_conf:
                            anachronisms.append({"line": line.strip(), "type": "modern_term_in_archaic_context"})
            except Exception:
                pass
        
        return anachronisms

    def _analyze_sociolinguistics(self, text: str) -> Dict[str, Any]:
        """Analyze sociolinguistic markers"""
        has_code_switching = False
        zs = self._ensure_zero_shot()
        thresholds = get_thresholds()
        min_conf = thresholds.get("zero_shot_min_confidence")
        if min_conf is None:
            return {
                "code_switching_detected": False,
                "register_match": "appropriate" if len(text.split()) > 10 else "needs_context",
            }
        if zs:
            try:
                code_switching_labels = get_labels("code_switching")
                if not code_switching_labels:
                    return {
                        "code_switching_detected": False,
                        "register_match": "appropriate" if len(text.split()) > 10 else "needs_context",
                    }
                out = zs(text, code_switching_labels)
                has_code_switching = out["labels"][0] == "code-switching" and float(out["scores"][0]) >= min_conf
            except Exception:
                pass
            
        return {
            "code_switching_detected": has_code_switching,
            "register_match": "appropriate" if len(text.split()) > 10 else "needs_context"
        }
