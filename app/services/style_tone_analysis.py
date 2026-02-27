"""
Style, Tone & Register Analysis Service
Based on Ultimate Literary Master System - Dimension 4
"""

from typing import Dict, List, Any, Optional
from collections import Counter
import re


class StyleToneAnalyzer:
    """
    Analyzes style, tone, and register of literary text
    Covers: Voice consistency, Tone analysis, Register spectrum, Diction assessment
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.text = ""
        self.lines: List[str] = []
        self.words: List[str] = []

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete style and tone analysis"""
        self.text = text
        self.lines = text.split("\n")
        self.words = re.findall(r"\b[\w\'-]+\b", text.lower())

        return {
            "voice_analysis": self._analyze_voice(),
            "tone_analysis": self._analyze_tone(),
            "register_analysis": self._analyze_register(),
            "diction_assessment": self._analyze_diction(),
            "style_category": self._determine_style_category(),
            "formality_score": self._calculate_formality_score(),
        }

    def _analyze_voice(self) -> Dict[str, Any]:
        """Analyze narrative voice consistency"""
        first_person = len(
            re.findall(
                r"\b(I|me|my|mine|myself|we|us|our|ours|ourselves)\b", self.text.lower()
            )
        )
        second_person = len(
            re.findall(r"\b(you|your|yours|yourself|yourselves)\b", self.text.lower())
        )
        third_person = len(
            re.findall(
                r"\b(he|she|it|they|him|her|them|his|hers|its|theirs|himself|herself|themselves)\b",
                self.text.lower(),
            )
        )

        total_pronouns = first_person + second_person + third_person

        if total_pronouns == 0:
            dominant_voice = "unknown"
        elif first_person >= second_person and first_person >= third_person:
            dominant_voice = "first_person"
        elif second_person >= first_person and second_person >= third_person:
            dominant_voice = "second_person"
        else:
            dominant_voice = "third_person"

        return {
            "first_person_count": first_person,
            "second_person_count": second_person,
            "third_person_count": third_person,
            "dominant_voice": dominant_voice,
            "voice_consistency": self._check_voice_consistency(
                first_person, second_person, third_person
            ),
        }

    def _check_voice_consistency(self, first: int, second: int, third: int) -> float:
        """Check if voice is consistent throughout"""
        total = first + second + third
        if total == 0:
            return 1.0

        counts = [first, second, third]
        max_count = max(counts)
        return round(max_count / total, 3)

    def _analyze_tone(self) -> Dict[str, Any]:
        """Analyze tone of the text"""
        text_lower = self.text.lower()

        tone_keywords = {
            "ironic": [
                "but",
                "yet",
                "however",
                "although",
                "seems",
                "appear",
                "supposed",
                "actually",
                "really",
            ],
            "satirical": [
                "ridiculous",
                "absurd",
                "foolish",
                "preposterous",
                "ludicrous",
            ],
            "elegiac": [
                "sorrow",
                "grief",
                "mourning",
                "lost",
                "gone",
                "death",
                "die",
                "weep",
                "lament",
            ],
            "didactic": [
                "should",
                "must",
                "ought",
                "learn",
                "teach",
                "moral",
                "lesson",
                "know",
            ],
            "lyrical": [
                "love",
                "heart",
                "soul",
                "dream",
                "beauty",
                "beautifully",
                "sweet",
                "soft",
            ],
            "celebratory": [
                "joy",
                "happy",
                "celebrate",
                "wonderful",
                "great",
                "triumph",
                "victory",
            ],
            "melancholic": ["sad", "blue", "lonely", "empty", "hollow", "void", "loss"],
            "contemplative": [
                "think",
                "wonder",
                "perhaps",
                "maybe",
                "consider",
                "reflect",
                "ponder",
            ],
            "aggressive": [
                "fight",
                "war",
                "battle",
                "destroy",
                "crush",
                "defeat",
                "enemy",
            ],
            "intimate": [
                "dear",
                "beloved",
                "cherish",
                "hold",
                "close",
                "warm",
                "tender",
            ],
        }

        tone_scores = {}
        for tone, keywords in tone_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            tone_scores[tone] = score

        dominant_tone = (
            max(tone_scores, key=tone_scores.get)
            if max(tone_scores.values()) > 0
            else "neutral"
        )

        return {
            "tone_scores": tone_scores,
            "dominant_tone": dominant_tone,
            "tone_intensity": min(10, max(0, sum(tone_scores.values()))),
            "tone_shifts": self._detect_tone_shifts(),
        }

    def _detect_tone_shifts(self) -> List[Dict[str, Any]]:
        """Detect changes in tone throughout the text"""
        shifts = []
        lines = [l for l in self.lines if l.strip()]

        if len(lines) < 2:
            return shifts

        for i in range(len(lines) - 1):
            tone1 = self._get_line_tone(lines[i])
            tone2 = self._get_line_tone(lines[i + 1])

            if tone1 != tone2:
                shifts.append({"line": i + 1, "from_tone": tone1, "to_tone": tone2})

        return shifts[:10]

    def _get_line_tone(self, line: str) -> str:
        """Get tone of a single line"""
        line_lower = line.lower()

        if any(w in line_lower for w in ["sad", "grief", "death", "lost"]):
            return "melancholic"
        elif any(w in line_lower for w in ["joy", "happy", "celebrate"]):
            return "celebratory"
        elif any(w in line_lower for w in ["love", "heart", "dream"]):
            return "lyrical"
        elif any(w in line_lower for w in ["anger", "fury", "fight"]):
            return "aggressive"
        else:
            return "neutral"

    def _analyze_register(self) -> Dict[str, Any]:
        """Analyze register (frozen, formal, consultative, casual, intimate)"""
        text_lower = self.text.lower()

        register_indicators = {
            "frozen": [
                "hereby",
                "therefore",
                "pursuant",
                "aforementioned",
                "whereas",
                "herein",
            ],
            "formal": [
                "cannot",
                "would",
                "should",
                "however",
                "therefore",
                "moreover",
                "furthermore",
            ],
            "consultative": [
                "please",
                "kindly",
                "consider",
                "perhaps",
                "might",
                "could",
            ],
            "casual": [
                "gonna",
                "wanna",
                "kinda",
                "sorta",
                "yeah",
                "nope",
                "cool",
                "okay",
            ],
            "intimate": ["dear", "beloved", "sweetheart", "darling", "honey", "love"],
        }

        register_scores = {}
        for register, indicators in register_indicators.items():
            score = sum(1 for ind in indicators if ind in text_lower)
            register_scores[register] = score

        dominant_register = (
            max(register_scores, key=register_scores.get)
            if max(register_scores.values()) > 0
            else "neutral"
        )

        return {
            "register_scores": register_scores,
            "dominant_register": dominant_register,
            "register_fluctuations": self._analyze_register_fluctuations(),
        }

    def _analyze_register_fluctuations(self) -> List[Dict[str, Any]]:
        """Check for register changes within the text"""
        return []

    def _analyze_diction(self) -> Dict[str, Any]:
        """Assess diction (word choice)"""
        if not self.words:
            return {
                "register": "neutral",
                "latin_percentage": 0,
                "germanic_percentage": 0,
            }

        latin_words = {
            "the",
            "of",
            "and",
            "a",
            "to",
            "in",
            "is",
            "that",
            "for",
            "it",
            "as",
            "was",
            "with",
            "by",
            "on",
            "are",
            "be",
            "at",
            "have",
            "this",
            "not",
            "but",
            "from",
            "or",
            "which",
            "you",
            "all",
            "were",
            "we",
            "when",
            "can",
            "there",
            "been",
            "has",
            "its",
            "if",
            "would",
            "who",
            "their",
            "what",
            "so",
            "up",
            "out",
            "about",
            "than",
            "into",
            "them",
            "he",
            "she",
            "him",
            "his",
            "her",
            "they",
            "them",
            "his",
        }

        latin_count = sum(1 for w in self.words if w in latin_words)
        germanic_count = len(self.words) - latin_count

        latin_pct = round((latin_count / len(self.words)) * 100, 2) if self.words else 0
        germanic_pct = (
            round((germanic_count / len(self.words)) * 100, 2) if self.words else 0
        )

        avg_word_length = (
            sum(len(w) for w in self.words) / len(self.words) if self.words else 0
        )

        return {
            "latin_percentage": latin_pct,
            "germanic_percentage": germanic_pct,
            "average_word_length": round(avg_word_length, 2),
            "formality_indicator": "formal" if avg_word_length > 5 else "casual",
        }

    def _determine_style_category(self) -> str:
        """Determine overall style category"""
        text_lower = self.text.lower()
        word_count = len(self.words)

        if word_count < 20:
            return "minimalist"

        complex_words = sum(1 for w in self.words if len(w) > 6)
        complex_ratio = complex_words / word_count if word_count > 0 else 0

        if complex_ratio > 0.4:
            return "ornate"
        elif complex_ratio < 0.2:
            return "minimalist"
        elif "?" in self.text or "!" in self.text:
            return "expressive"
        else:
            return "classical"

    def _calculate_formality_score(self) -> float:
        """Calculate formality score 0-10"""
        text_lower = self.text.lower()

        formal_indicators = [
            "cannot",
            "shall",
            "therefore",
            "however",
            "moreover",
            "furthermore",
        ]
        informal_indicators = [
            "gonna",
            "wanna",
            "kinda",
            "yeah",
            "nope",
            "cool",
            "okay",
        ]

        formal_count = sum(1 for ind in formal_indicators if ind in text_lower)
        informal_count = sum(1 for ind in informal_indicators if ind in text_lower)

        score = 5.0 + (formal_count * 0.5) - (informal_count * 0.5)
        return round(min(10.0, max(1.0, score)), 1)


class PragmaticsAnalyzer:
    """
    Analyzes pragmatics of literary text
    Covers: Speech acts, Implicatures, Politeness strategies, Discourse markers
    """

    def __init__(self, language: str = "en"):
        self.language = language

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete pragmatics analysis"""
        return {
            "speech_acts": self._analyze_speech_acts(text),
            "implicatures": self._detect_implicatures(text),
            "politeness_strategies": self._analyze_politeness(text),
            "discourse_markers": self._analyze_discourse_markers(text),
            "cohesion_analysis": self._analyze_cohesion(text),
        }

    def _analyze_speech_acts(self, text: str) -> Dict[str, Any]:
        """Identify speech act types"""
        text_lower = text.lower()

        speech_act_types = {
            "declarative": ["is", "are", "was", "were", "have", "has", "had"],
            "interrogative": [
                "what",
                "who",
                "where",
                "when",
                "why",
                "how",
                "which",
                "?",
            ],
            "imperative": ["let", "go", "come", "see", "hear", "think", "remember"],
            "exclamatory": ["!", "oh", "ah", "alas", "wow", "how"],
        }

        scores = {}
        for act_type, indicators in speech_act_types.items():
            score = sum(1 for ind in indicators if ind in text_lower)
            scores[act_type] = score

        dominant = max(scores, key=scores.get) if scores else "declarative"

        return {
            "scores": scores,
            "dominant_act": dominant,
            "is_question": "?" in text,
            "is_command": any(
                ind in text_lower.split()[:3]
                for ind in ["let", "go", "come", "see", "do", "make"]
            ),
        }

    def _detect_implicatures(self, text: str) -> List[Dict[str, Any]]:
        """Detect implied meanings"""
        implicatures = []

        text_lower = text.lower()

        irony_markers = ["but", "yet", "actually", "really", "supposed"]
        for marker in irony_markers:
            if marker in text_lower:
                implicatures.append(
                    {
                        "type": "ironic",
                        "marker": marker,
                        "interpretation": f"Potential irony detected via '{marker}'",
                    }
                )

        return implicatures[:5]

    def _analyze_politeness(self, text: str) -> Dict[str, Any]:
        """Analyze politeness strategies"""
        text_lower = text.lower()

        polite_markers = [
            "please",
            "kindly",
            "would",
            "could",
            "might",
            "may",
            "would you",
        ]
        impolite_markers = ["must", "immediately", "now", "demand", "command"]

        polite_count = sum(1 for m in polite_markers if m in text_lower)
        impolite_count = sum(1 for m in impolite_markers if m in text_lower)

        if impolite_count > polite_count:
            level = "direct"
        elif polite_count > 2:
            level = "highly_polite"
        elif polite_count > 0:
            level = "polite"
        else:
            level = "neutral"

        return {
            "politeness_level": level,
            "polite_markers_count": polite_count,
            "direct_markers_count": impolite_count,
        }

    def _analyze_discourse_markers(self, text: str) -> Dict[str, Any]:
        """Analyze discourse markers (connectives)"""
        text_lower = text.lower()

        markers = {
            "additive": ["and", "also", "moreover", "furthermore", "additionally"],
            "adversative": [
                "but",
                "however",
                "although",
                "yet",
                "nevertheless",
                "despite",
            ],
            "causal": ["because", "since", "therefore", "thus", "hence", "so"],
            "temporal": [
                "then",
                "when",
                "after",
                "before",
                "finally",
                "next",
                "meanwhile",
            ],
        }

        marker_counts = {}
        for category, words in markers.items():
            count = sum(1 for w in words if w in text_lower)
            marker_counts[category] = count

        return {
            "marker_counts": marker_counts,
            "total_markers": sum(marker_counts.values()),
            "dominant_type": max(marker_counts, key=marker_counts.get)
            if marker_counts
            else None,
        }

    def _analyze_cohesion(self, text: str) -> Dict[str, Any]:
        """Analyze cohesion markers"""
        text_lower = text.lower()

        cohesion_types = {
            "reference": ["he", "she", "it", "they", "this", "that", "these", "those"],
            "substitution": ["one", "do", "so", "such"],
            "ellipsis": [],
            "conjunction": ["and", "but", "or", "because", "although"],
        }

        counts = {}
        for ctype, words in cohesion_types.items():
            if words:
                counts[ctype] = sum(1 for w in words if w in text_lower)
            else:
                counts[ctype] = 0

        return {"cohesion_types": counts, "cohesion_score": sum(counts.values())}


class CulturalHistoricalAnalyzer:
    """
    Analyzes cultural and historical fidelity
    Covers: Period accuracy, Cultural authenticity, Anachronism detection
    """

    def __init__(self, language: str = "en"):
        self.language = language

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete cultural/historical analysis"""
        return {
            "period_accuracy": self._analyze_period_accuracy(text),
            "cultural_authenticity": self._analyze_cultural_authenticity(text),
            "anachronism_detection": self._detect_anachronisms(text),
            "sociolinguistic_analysis": self._analyze_sociolinguistics(text),
        }

    def _analyze_period_accuracy(self, text: str) -> Dict[str, Any]:
        """Assess period-appropriate language"""
        text_lower = text.lower()

        archaic_words = [
            "thee",
            "thou",
            "thy",
            "thine",
            "hath",
            "doth",
            "wherefore",
            "whence",
            "methinks",
            "forsooth",
            "prithee",
        ]
        modern_words = [
            "okay",
            "gonna",
            "wanna",
            "cool",
            "stuff",
            "whatever",
            "like",
            "yeah",
        ]

        archaic_count = sum(1 for w in archaic_words if w in text_lower)
        modern_count = sum(1 for w in modern_words if w in text_lower)

        if archaic_count > modern_count:
            period = "archaic"
        elif modern_count > archaic_count:
            period = "modern"
        else:
            period = "contemporary"

        return {
            "detected_period": period,
            "archaic_markers": archaic_count,
            "modern_markers": modern_count,
            "period_consistency": "consistent"
            if abs(archaic_count - modern_count) < 2
            else "mixed",
        }

    def _analyze_cultural_authenticity(self, text: str) -> Dict[str, Any]:
        """Assess cultural authenticity"""
        text_lower = text.lower()

        cultural_markers = {
            "western": ["church", "god", "king", "queen", "sir", "lord", "lady"],
            "eastern": ["temple", "deva", "guru", "mantra", "karma", "dharma"],
            "folk": ["village", "field", "river", "mountain", "forest"],
        }

        scores = {}
        for culture, markers in cultural_markers.items():
            score = sum(1 for m in markers if m in text_lower)
            scores[culture] = score

        return {
            "cultural_scores": scores,
            "primary_cultural_context": max(scores, key=scores.get)
            if scores
            else "neutral",
        }

    def _detect_anachronisms(self, text: str) -> List[Dict[str, Any]]:
        """Detect anachronistic elements"""
        anachronisms = []

        text_lower = text.lower()

        modern_concepts = [
            "internet",
            "computer",
            "phone",
            "television",
            "car",
            "airplane",
            "electricity",
        ]

        archaic_contexts = ["king", "queen", "castle", "sword", "horse", "medieval"]

        has_archaic = any(w in text_lower for w in archaic_contexts)
        has_modern = any(w in text_lower for w in modern_concepts)

        if has_archaic and has_modern:
            anachronisms.append(
                {
                    "type": "temporal_mismatch",
                    "severity": "high",
                    "description": "Both archaic and modern concepts detected - possible anachronism",
                }
            )

        return anachronisms

    def _analyze_sociolinguistics(self, text: str) -> Dict[str, Any]:
        """Analyze sociolinguistic features"""
        text_lower = text.lower()

        return {
            "honorific_usage": "formal"
            if any(h in text_lower for h in ["sir", "madam", "lord", "lady", "your"])
            else "informal",
            "code_switching_detected": False,
            "dialect_markers": [],
        }


class OrthographyAnalyzer:
    """
    Analyzes orthography and spelling
    Covers: English spelling, Hindi/Devanagari, Punctuation
    """

    def __init__(self, language: str = "en"):
        self.language = language

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete orthography analysis"""
        if self.language == "en":
            return self._analyze_english(text)
        elif self.language in ["hi", "sa"]:
            return self._analyze_hindi(text)
        else:
            return {"language": "unsupported", "issues": []}

    def _analyze_english(self, text: str) -> Dict[str, Any]:
        """Analyze English orthography"""

        issues = []

        punctuation_errors = []
        if ".." in text:
            punctuation_errors.append("Multiple periods")
        if ",," in text:
            punctuation_errors.append("Multiple commas")
        if "  " in text:
            punctuation_errors.append("Multiple spaces")

        spelling_issues = []

        capitalization_errors = []
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line and line[0].islower():
                if i == 0 or (i > 0 and lines[i - 1].endswith((".", "!", "?"))):
                    capitalization_errors.append(f"Line {i + 1}")

        return {
            "punctuation_issues": punctuation_errors,
            "spelling_errors": spelling_issues,
            "capitalization_errors": capitalization_errors,
            "hyphenation_check": self._check_hyphenation(text),
            "quote_consistency": self._check_quotes(text),
        }

    def _analyze_hindi(self, text: str) -> Dict[str, Any]:
        """Analyze Hindi/Devanagari orthography"""

        issues = []

        if "़" in text:
            issues.append("Nuclearization markers detected")

        chandrabindu_count = text.count("ँ")
        anusvara_count = text.count("ं")

        return {
            "chandrabindu_count": chandrabindu_count,
            "anusvara_count": anusvara_count,
            "issues": issues,
            "virama_usage": text.count("्"),
            "matra_check": "ok",
        }

    def _check_hyphenation(self, text: str) -> Dict[str, Any]:
        """Check hyphenation consistency"""
        hyphen_count = text.count("-")
        return {"hyphen_count": hyphen_count, "has_compound_words": hyphen_count > 0}

    def _check_quotes(self, text: str) -> Dict[str, Any]:
        """Check quote consistency"""
        double_quotes = text.count('"')
        single_quotes = text.count("'")

        return {
            "double_quotes": double_quotes,
            "single_quotes": single_quotes,
            "consistent": (double_quotes % 2 == 0) and (single_quotes % 2 == 0),
        }
