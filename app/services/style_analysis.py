"""
Style, Tone, Register & Narrative Analysis Module
Covers Dimension 4 and 5 of the Ultimate Literary Master System
"""

import re
from typing import Dict, List, Any, Optional
from collections import Counter
from transformers import pipeline
from app.config import Settings
from app.services.label_loader import get_labels
from app.services.rule_loader import get_style_rules, get_thresholds, get_performance_rules
from app.services.text_chunker import aggregate_zero_shot
import spacy

class StyleToneAnalyzer:
    """
    Analyze voice consistency, tone, register, and style categories
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self._settings = Settings()
        self._zero_shot = None
        self._nlp = None

        self.style_rules = get_style_rules()
        self.perf_rules = get_performance_rules()

    def _ensure_zero_shot(self):
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            model_name = self._settings.transformer.generalist_zero_shot_model
            self._zero_shot = pipeline("zero-shot-classification", model=model_name, device=-1)
        except Exception:
            self._zero_shot = None
        return self._zero_shot

    def _ensure_nlp(self):
        if self._nlp is not None:
            return self._nlp
        try:
            model = self._settings.spacy.english_model if self.language == "en" else self._settings.spacy.multilingual_model
            self._nlp = spacy.load(model)
        except Exception:
            self._nlp = None
        return self._nlp

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete style, tone, and register analysis"""
        words = text.lower().split()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        return {
            "voice_analysis": self._analyze_voice(text, lines),
            "tone_analysis": self._analyze_tone(words),
            "register_analysis": self._analyze_register(words),
            "style_category": self._identify_style(text),
            "narrative_elements": self._analyze_narrative(text, lines),
            "formality_score": self._calculate_formality(words)
        }

    def _analyze_voice(self, text: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze point of view and consistency"""
        first_person = second_person = third_person = 0
        nlp = self._ensure_nlp()
        if nlp:
            doc = nlp(text)
            for token in doc:
                if token.pos_ == "PRON":
                    person = token.morph.get("Person")
                    if "1" in person:
                        first_person += 1
                    elif "2" in person:
                        second_person += 1
                    elif "3" in person:
                        third_person += 1

        total = first_person + second_person + third_person
        if total == 0:
            dominant = "third_person"  # Default
        else:
            if first_person >= second_person and first_person >= third_person:
                dominant = "first_person"
            elif second_person >= first_person and second_person >= third_person:
                dominant = "second_person"
            else:
                dominant = "third_person"

        return {
            "dominant_voice": dominant,
            "counts": {"1st": first_person, "2nd": second_person, "3rd": third_person},
            "voice_consistency": 0.8 if total > 0 else 1.0,
            "narrative_distance": "intimate" if dominant == "first_person" else "distant"
        }

    def _analyze_tone(self, words: List[str]) -> Dict[str, Any]:
        """Analyze emotional tone"""
        zs = self._ensure_zero_shot()
        labels = get_labels("style_tone")
        if not labels:
            return {"scores": {}, "dominant_tone": "neutral", "tonal_shifts": "low"}
        scores = {l: 0.0 for l in labels}
        if zs:
            try:
                chunk_size = self.perf_rules.get("zero_shot_chunk_words")
                out = aggregate_zero_shot(zs, labels, " ".join(words), chunk_size)
                scores = {label: float(score) for label, score in zip(out["labels"], out["scores"])}
            except Exception:
                pass
        dominant_tone = max(scores, key=scores.get) if any(scores.values()) else "neutral"
        
        return {
            "scores": scores,
            "dominant_tone": dominant_tone,
            "tonal_shifts": "low" if len(set(scores.values())) < 3 else "high"
        }

    def _analyze_register(self, words: List[str]) -> Dict[str, Any]:
        """Analyze language register"""
        avg_len = sum(len(w) for w in words) / max(1, len(words))
        
        if avg_len > 6:
            reg = "frozen/formal"
        elif avg_len > 5:
            reg = "consultative"
        elif avg_len > 4:
            reg = "casual"
        else:
            reg = "intimate"
            
        return {
            "dominant_register": reg,
            "avg_word_length": round(avg_len, 2)
        }

    def _identify_style(self, text: str) -> str:
        """Identify literary style category"""
        rules = self.style_rules or {}
        if not rules:
            return "classical/balanced"

        lines = max(1, len(text.split("\n")))
        words = text.split()
        avg_words_per_line = len(words) / lines if lines else 0

        for cat, rule in rules.items():
            rtype = rule.get("type")
            threshold = float(rule.get("threshold", 0))
            if rtype == "avg_words_per_line_lt":
                if avg_words_per_line < threshold:
                    return cat
            elif rtype == "any_word_length_gt":
                if any(len(w) > threshold for w in words):
                    return cat
            elif rtype == "comma_per_line_gt":
                if (text.count(",") / lines) > threshold:
                    return cat
            elif rtype == "period_per_line_lt":
                if (text.count(".") / lines) < threshold:
                    return cat
        return "classical/balanced"

    def _analyze_narrative(self, text: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze narrative architecture and techniques"""
        zs = self._ensure_zero_shot()
        plot_arch = "linear"
        if zs:
            try:
                plot_labels = get_labels("plot_arch")
                if not plot_labels:
                    return {
                        "plot_architecture": plot_arch,
                        "pacing": "fast" if len(lines) > 20 else "slow",
                        "narrative_techniques": techniques,
                        "character_presence": "implied" if len(lines) < 10 else "distinct",
                    }
                chunk_size = self.perf_rules.get("zero_shot_chunk_words")
                out = aggregate_zero_shot(zs, plot_labels, text, chunk_size)
                plot_arch = "nonlinear" if out["labels"][0] == "nonlinear narrative" else "linear"
            except Exception:
                pass

        techniques = []
        if zs:
            try:
                narrative_labels = get_labels("narrative_mode")
                if not narrative_labels:
                    return {
                        "plot_architecture": plot_arch,
                        "pacing": "fast" if len(lines) > 20 else "slow",
                        "narrative_techniques": techniques,
                        "character_presence": "implied" if len(lines) < 10 else "distinct",
                    }
                chunk_size = self.perf_rules.get("zero_shot_chunk_words")
                out = aggregate_zero_shot(zs, narrative_labels, text, chunk_size)
                thresholds = get_thresholds()
                min_conf = thresholds.get("zero_shot_min_confidence")
                if min_conf is None:
                    return {
                        "plot_architecture": plot_arch,
                        "pacing": "fast" if len(lines) > 20 else "slow",
                        "narrative_techniques": techniques,
                        "character_presence": "implied" if len(lines) < 10 else "distinct",
                    }
                for label, score in zip(out["labels"], out["scores"]):
                    if score >= min_conf:
                        techniques.append(label)
            except Exception:
                pass

        return {
            "plot_architecture": plot_arch,
            "pacing": "fast" if len(lines) > 20 else "slow",
            "narrative_techniques": techniques,
            "character_presence": "implied" if len(lines) < 10 else "distinct"
        }

    def _calculate_formality(self, words: List[str]) -> float:
        """Calculate formality score (0-1)"""
        zs = self._ensure_zero_shot()
        if zs:
            try:
                register_labels = get_labels("register")
                if not register_labels:
                    return 0.5
                chunk_size = self.perf_rules.get("zero_shot_chunk_words")
                out = aggregate_zero_shot(zs, register_labels, " ".join(words), chunk_size)
                if out["labels"][0] == "formal register":
                    return float(out["scores"][0])
                return 1.0 - float(out["scores"][0])
            except Exception:
                pass
        return 0.5
