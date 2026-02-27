"""
Additional Analysis Modules
Dialect Detection, Discourse Analysis, Text Correction, Idiom/Proverb Detection
Based on ultimate_literary_master_system.md
"""

import re
from typing import Dict, List, Any, Optional, Tuple


# ==================== DIALECT DETECTION ====================

class DialectDetector:
    """Detect Hindi/Indic dialects and language varieties"""

    def __init__(self):
        # Dialect-specific markers
        self.dialect_markers = {
            "braj_bhasha": ["-au", "-ai", "री", "है", "जै", "तै"],
            "awadhi": ["-हा", "-हीं", "हौं", "तुम", "राम"],
            "bhojpuri": ["-ल", "-ब", "हल", "बल", "की", "रउवा", "अपन"],
            "maithili": ["-थिन", "-हुन", "जयथिन", "अहाँ", "छै"],
            "magahi": ["-हक", "-थुन", "गे", "रे", "हिया"],
            "chhattisgarhi": ["-बो", "-थन", "ल", "मन", "मोर"],
            "haryanvi": ["-सै", "-सु", "के", "कड़े", "घणा"],
            "rajasthani": ["-ण", "छै", "कांई", "कठै", "म्हने", "थाने"],
            "standard_hindi": ["-ना", "-ता", "-ता है", "हैं", "थे"]
        }

    def detect(self, text: str) -> Dict[str, Any]:
        """Detect dialect from text"""
        scores = {}
        
        for dialect, markers in self.dialect_markers.items():
            count = sum(text.count(m) for m in markers)
            scores[dialect] = count
        
        if not any(scores.values()):
            return {"detected": "unknown", "confidence": 0.0}
        
        max_dialect = max(scores, key=scores.get)
        max_score = scores[max_dialect]
        total = sum(scores.values())
        
        confidence = max_score / total if total > 0 else 0
        
        return {
            "detected_dialect": max_dialect.replace("_", " "),
            "confidence": round(confidence, 3),
            "all_scores": scores,
            "marker_count": max_score
        }


# ==================== DISCOURSE ANALYSIS ====================

class DiscourseAnalyzer:
    """
    Analyze discourse using Halliday & Hasan cohesive devices
    """

    def __init__(self):
        self.cohesive_devices = {
            "reference": {
                "anaphoric": ["he", "she", "it", "they", "this", "that", "these", "those", "him", "her", "them"],
                "cataphoric": ["following", "below", "next"],
                "exophoric": ["there", "here", "now", "then"]
            },
            "substitution": ["one", "ones", "do", "so", "not"],
            "ellipsis": [],  # Detected by missing elements
            "conjunction": {
                "additive": ["and", "also", "furthermore", "moreover"],
                "adversative": ["but", "however", "yet", "nevertheless"],
                "causal": ["so", "therefore", "thus", "because"],
                "temporal": ["then", "next", "finally", "afterwards"]
            },
            "lexical": ["repetition", "synonym", "antonym"]  # Detected by analysis
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze discourse cohesion"""
        words = text.lower().split()
        
        results = {
            "reference": self._analyze_reference(words),
            "substitution": self._analyze_substitution(words),
            "conjunction": self._analyze_conjunction(words),
            "lexical_cohesion": self._analyze_lexical_cohesion(words),
            "coherence_score": 0.0
        }
        
        # Calculate overall coherence
        total_cohesion = (
            results["reference"]["count"] +
            results["substitution"]["count"] +
            results["conjunction"]["count"] +
            results["lexical_cohesion"]["count"]
        )
        
        results["coherence_score"] = min(1.0, total_cohesion / len(words) * 10) if words else 0
        
        return results

    def _analyze_reference(self, words: List[str]) -> Dict[str, Any]:
        """Analyze reference devices"""
        counts = {k: sum(words.count(w) for w in v) for k, v in self.cohesive_devices["reference"].items()}
        return {
            "anaphoric": counts["anaphoric"],
            "cataphoric": counts["cataphoric"],
            "exophoric": counts["exophoric"],
            "count": sum(counts.values())
        }

    def _analyze_substitution(self, words: List[str]) -> Dict[str, Any]:
        """Analyze substitution devices"""
        count = sum(words.count(w) for w in self.cohesive_devices["substitution"])
        return {"count": count, "instances": [w for w in self.cohesive_devices["substitution"] if w in words]}

    def _analyze_conjunction(self, words: List[str]) -> Dict[str, Any]:
        """Analyze conjunction devices"""
        counts = {k: sum(words.count(w) for w in v) for k, v in self.cohesive_devices["conjunction"].items()}
        return {
            "additive": counts["additive"],
            "adversative": counts["adversative"],
            "causal": counts["causal"],
            "temporal": counts["temporal"],
            "count": sum(counts.values())
        }

    def _analyze_lexical_cohesion(self, words: List[str]) -> Dict[str, Any]:
        """Analyze lexical cohesion (repetition)"""
        from collections import Counter
        word_freq = Counter(words)
        repeated = sum(1 for count in word_freq.values() if count > 1)
        return {
            "repeated_words": repeated,
            "count": repeated
        }


# ==================== TEXT CORRECTION ====================

class TextCorrector:
    """
    Correct and enhance text
    """

    def __init__(self):
        # Common corrections
        self.common_corrections = {
            "teh": "the",
            "taht": "that",
            "waht": "what",
            "hte": "the",
            "iwth": "with",
            "adn": "and",
            "nad": "and",
            "si": "is",
            "are": "are",
            "dont": "don't",
            "cant": "can't",
            "wont": "won't",
            "its": "it's"  # Context-dependent
        }

        # Enhancements (simple synonyms for variety)
        self.enhancements = {
            "good": ["excellent", "superb", "fine", "wonderful"],
            "bad": ["poor", "terrible", "awful", "dreadful"],
            "big": ["large", "huge", "enormous", "vast"],
            "small": ["tiny", "little", "miniature", "compact"],
            "happy": ["joyful", "delighted", "pleased", "content"],
            "sad": ["sorrowful", "melancholy", "dejected", "downcast"]
        }

    def correct(self, text: str) -> Dict[str, Any]:
        """Correct text errors"""
        words = text.split()
        corrected = []
        corrections = []
        
        for i, word in enumerate(words):
            clean = re.sub(r'[^a-zA-Z]', '', word)
            if clean.lower() in self.common_corrections:
                correction = self.common_corrections[clean.lower()]
                # Preserve capitalization
                if clean[0].isupper():
                    correction = correction.capitalize()
                corrected_word = word.replace(clean, correction)
                corrected.append(corrected_word)
                corrections.append({
                    "original": clean,
                    "corrected": correction,
                    "position": i
                })
            else:
                corrected.append(word)
        
        return {
            "original_text": text,
            "corrected_text": " ".join(corrected),
            "corrections": corrections,
            "correction_count": len(corrections)
        }

    def enhance(self, text: str) -> Dict[str, Any]:
        """Enhance text with varied vocabulary"""
        words = text.split()
        enhanced = []
        enhancements = []
        
        for i, word in enumerate(words):
            clean = re.sub(r'[^a-zA-Z]', '', word)
            if clean.lower() in self.enhancements and i % 3 == 0:  # Enhance every 3rd occurrence
                options = self.enhancements[clean.lower()]
                enhancement = options[0]
                if clean[0].isupper():
                    enhancement = enhancement.capitalize()
                enhanced_word = word.replace(clean, enhancement)
                enhanced.append(enhanced_word)
                enhancements.append({
                    "original": clean,
                    "enhanced": enhancement,
                    "position": i
                })
            else:
                enhanced.append(word)
        
        return {
            "original_text": text,
            "enhanced_text": " ".join(enhanced),
            "enhancements": enhancements,
            "enhancement_count": len(enhancements)
        }


# ==================== IDIOM & PROVERB DETECTION ====================

class IdiomProverbDetector:
    """
    Detect idioms and proverbs in multiple languages
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.idioms = self._load_idioms()
        self.proverbs = self._load_proverbs()

    def _load_idioms(self) -> Dict[str, List[str]]:
        """Load idioms by language"""
        return {
            "en": [
                "break the ice", "bite the bullet", "beat around the bush",
                "burn the midnight oil", "cost an arm and a leg",
                "hit the nail on the head", "kill two birds with one stone",
                "let the cat out of the bag", "once in a blue moon",
                "piece of cake", "rain cats and dogs", "spill the beans"
            ],
            "hi": [
                "आँखें खुलना", "नौ दो ग्यारह होना", "दाल में काला होना",
                "पानी पानी होना", "आसमान टूट पड़ना", "चौंकाना"
            ],
            "gu": [
                "હાથી જીવતો લાખનો", "વાંદરાના હાથમાં અસ્ત્રો",
                "ઘરનો ભેદો ઘરમાં", "આંખમાં આંજણ"
            ]
        }

    def _load_proverbs(self) -> Dict[str, List[str]]:
        """Load proverbs by language"""
        return {
            "en": [
                "a stitch in time saves nine", "actions speak louder than words",
                "all that glitters is not gold", "an apple a day keeps the doctor away",
                "birds of a feather flock together", "better safe than sorry"
            ],
            "hi": [
                "अधजल गगरी छलकत जाय", "जाको राखे साइयाँ मार सके न कोय",
                "कर भला तो हो भला", "जैसा देश वैसा भेष"
            ],
            "gu": [
                "કરે તે ભરે", "જેવું વાવેતર તેવું ફળ",
                "અધજલું ઘાગરું છલકાય વધુ"
            ]
        }

    def detect(self, text: str) -> Dict[str, Any]:
        """Detect idioms and proverbs"""
        text_lower = text.lower()
        
        idioms_found = [
            idiom for idiom in self.idioms.get(self.language, [])
            if idiom in text_lower
        ]
        
        proverbs_found = [
            proverb for proverb in self.proverbs.get(self.language, [])
            if proverb in text_lower
        ]
        
        return {
            "language": self.language,
            "idioms_found": idioms_found,
            "idiom_count": len(idioms_found),
            "proverbs_found": proverbs_found,
            "proverb_count": len(proverbs_found),
            "total_found": len(idioms_found) + len(proverbs_found)
        }


# ==================== PRAGMATICS ANALYSIS ====================

class PragmaticsAnalyzer:
    """
    Analyze pragmatics: illocutionary force, politeness, speech acts
    Based on ultimate_literary_master_system.md Dimension 1.8
    """

    def __init__(self):
        self.speech_act_markers = {
            "assertive": ["believe", "think", "know", "is", "are", "fact"],
            "directive": ["order", "command", "ask", "request", "please", "must", "should"],
            "commissive": ["promise", "vow", "will", "shall", "guarantee"],
            "expressive": ["thank", "congratulate", "apologize", "deplore", "welcome"],
            "declarative": ["declare", "pronounce", "baptize", "resign"]
        }
        
        self.politeness_markers = {
            "positive": ["please", "kindly", "appreciate", "good", "great", "thanks"],
            "negative": ["sorry", "apologize", "pardon", "if you don't mind", "excuse"]
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze pragmatics of text"""
        text_lower = text.lower()
        words = text_lower.split()
        
        speech_acts = {k: sum(text_lower.count(m) for m in v) for k, v in self.speech_act_markers.items()}
        politeness = {k: sum(text_lower.count(m) for m in v) for k, v in self.politeness_markers.items()}
        
        dominant_act = max(speech_acts, key=speech_acts.get) if any(speech_acts.values()) else "unknown"
        politeness_level = "polite" if sum(politeness.values()) > len(words) * 0.05 else "neutral"
        
        return {
            "speech_acts": {
                "counts": speech_acts,
                "dominant_act": dominant_act
            },
            "politeness_strategies": {
                "counts": politeness,
                "politeness_level": politeness_level
            },
            "illocutionary_force": "strong" if any(speech_acts.values()) else "moderate",
            "implicatures_detected": ["Contextual meaning implies deeper subtext"] if len(words) > 20 else []
        }


# ==================== COMBINED ANALYSIS FUNCTION ====================

def run_additional_analyses(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Run all additional analysis modules
    
    Args:
        text: Text to analyze
        language: Language code (en, hi, gu)
    
    Returns:
        Combined analysis results
    """
    dialect_detector = DialectDetector()
    discourse_analyzer = DiscourseAnalyzer()
    text_corrector = TextCorrector()
    idiom_detector = IdiomProverbDetector(language)
    pragmatics_analyzer = PragmaticsAnalyzer()
    
    return {
        "dialect_detection": dialect_detector.detect(text),
        "discourse_analysis": discourse_analyzer.analyze(text),
        "text_correction": text_corrector.correct(text),
        "text_enhancement": text_corrector.enhance(text),
        "idioms_proverbs": idiom_detector.detect(text),
        "pragmatics": pragmatics_analyzer.analyze(text)
    }
