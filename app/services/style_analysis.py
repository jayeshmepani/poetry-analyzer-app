"""
Style, Tone, Register & Narrative Analysis Module
Covers Dimension 4 and 5 of the Ultimate Literary Master System
"""

import re
from typing import Dict, List, Any, Optional
from collections import Counter

class StyleToneAnalyzer:
    """
    Analyze voice consistency, tone, register, and style categories
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.tone_lexicon = {
            "melancholic": ["sad", "dark", "death", "lost", "gone", "sorrow", "tear", "mourn"],
            "lyrical": ["soft", "beauty", "light", "gentle", "sweet", "sing", "flow", "grace"],
            "contemplative": ["think", "mind", "soul", "wonder", "deep", "quiet", "still", "nature"],
            "celebratory": ["joy", "praise", "great", "wonderful", "bright", "glory", "triumph"],
            "satirical": ["ironic", "mock", "fool", "ridiculous", "absurd", "clever", "sharp"],
            "aggressive": ["war", "strike", "blood", "kill", "fierce", "rage", "hard", "sharp"]
        }
        
        self.style_categories = {
            "minimalist": lambda text: len(text.split()) / max(1, len(text.split('\n'))) < 5,
            "ornate": lambda text: any(len(w) > 10 for w in text.split()),
            "baroque": lambda text: text.count(',') > len(text.split('\n')) * 2,
            "stream_of_consciousness": lambda text: text.count('.') < len(text.split('\n')) / 2
        }

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
        first_person = len(re.findall(r'\b(i|me|my|mine|we|us|our)\b', text.lower()))
        second_person = len(re.findall(r'\b(you|your|yours)\b', text.lower()))
        third_person = len(re.findall(r'\b(he|she|it|they|him|her|them|his|hers|their)\b', text.lower()))

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
        scores = {tone: sum(1 for w in words if w in lexicon) for tone, lexicon in self.tone_lexicon.items()}
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
        for cat, check in self.style_categories.items():
            if check(text):
                return cat
        return "classical/balanced"

    def _analyze_narrative(self, text: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze narrative architecture and techniques"""
        # Look for plot markers
        has_intro = any(w in text.lower()[:100] for w in ["once", "when", "first", "in the"])
        has_climax = "!" in text or any(w in text.lower() for w in ["suddenly", "finally", "moment"])

        return {
            "plot_architecture": "linear" if not "remembered" in text.lower() else "nonlinear",
            "pacing": "fast" if len(lines) > 20 else "slow",
            "narrative_techniques": ["focalization"] if len(lines) > 10 else [],
            "character_presence": "implied" if len(lines) < 10 else "distinct"
        }

    def _calculate_formality(self, words: List[str]) -> float:
        """Calculate formality score (0-1)"""
        formal_markers = ["therefore", "thus", "shall", "moreover", "consequently"]
        count = sum(1 for w in words if w in formal_markers)
        return min(1.0, count / 5.0)
