"""
Advanced Analysis Module
TP-CASTT, SWIFT, Touchstone Method, Sentiment Analysis
Based on quantitative_poetry_metrics.md & ultimate_literary_master_system.md
"""

import re
from typing import Dict, List, Any, Optional
from collections import Counter

# Use VADER for robust sentiment analysis (handles negation, intensity, punctuation)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from app.config import Settings
from app.services.literary_devices import LiteraryDevicesAnalyzer
from app.services.touchstone_loader import select_touchstone_passages
from app.services.rule_loader import get_advanced_analysis_rules

# Lazy-load VADER analyzer
_vader_analyzer = None


def get_vader_analyzer():
    global _vader_analyzer
    if _vader_analyzer is None:
        _vader_analyzer = SentimentIntensityAnalyzer()
    return _vader_analyzer


class AdvancedAnalysisEngine:
    """
    Advanced literary analysis methods
    TP-CASTT, SWIFT, T-SWIFT, Touchstone, Sentiment
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.text = ""
        self.lines: List[str] = []
        self.words: List[str] = []
        self._settings = Settings()
        self._zero_shot = None
        self._rules = get_advanced_analysis_rules()
        self._templates = self._rules["templates"]

    def analyze(self, text: str, methods: List[str] = None) -> Dict[str, Any]:
        """Run advanced analysis with specified methods"""
        self.text = text
        self.lines = [l.strip() for l in text.split("\n") if l.strip()]
        self.words = re.findall(r"\b[a-zA-Z]+\b", text.lower())

        if methods is None:
            methods = list(self._rules["default_methods"])

        result = {}

        if "tp_castt" in methods:
            result["tp_castt"] = self._analyze_tp_castt()

        if "swift" in methods:
            result["swift"] = self._analyze_swift()

        if "t_swift" in methods:
            result["t_swift"] = self._analyze_t_swift()

        if "sift" in methods:
            result["sift"] = self._analyze_sift()

        if "touchstone" in methods:
            result["touchstone"] = self._analyze_touchstone()

        if "sentiment" in methods:
            result["sentiment"] = self._analyze_sentiment()

        return result

    # ==================== TP-CASTT METHOD ====================

    def _analyze_tp_castt(self) -> Dict[str, Any]:
        """
        TP-CASTT Method for poetry analysis
        Title, Paraphrase, Connotation, Attitude, Shift, Title (revisited), Theme
        """
        return {
            "title_prediction": self._tp_title_prediction(),
            "paraphrase": self._tp_paraphrase(),
            "connotation": self._tp_connotation(),
            "attitude": self._tp_attitude(),
            "shifts": self._tp_shifts(),
            "title_revisited": self._tp_title_revisited(),
            "theme": self._tp_theme(),
        }

    def _tp_title_prediction(self) -> str:
        """Predict poem meaning from title (first line if no title)"""
        if self.lines:
            first_line = self.lines[0]
            preview = first_line[: self._rules["opening_line_preview"]]
            return self._templates["title_prediction"].format(opening=preview)
        return self._templates["no_title"]

    def _tp_paraphrase(self) -> str:
        """Paraphrase the literal meaning"""
        if len(self.lines) <= self._rules["paraphrase_max_lines"]:
            return " ".join(self.lines)
        if self.lines:
            first = self.lines[0][: self._rules["summary_line_preview"]]
            last = self.lines[-1][: self._rules["summary_line_preview"]]
        else:
            first = self._templates["unknown_placeholder"]
            last = self._templates["unknown_placeholder"]
        return self._templates["paraphrase_summary"].format(
            line_count=len(self.lines),
            first=first,
            last=last
        )

    def _tp_connotation(self) -> Dict[str, List[str]]:
        """Identify figurative devices and connotations"""
        connotation = {"metaphors": [], "similes": [], "personification": [], "symbols": [], "imagery": []}

        analyzer = LiteraryDevicesAnalyzer(language=self.language)
        analysis = analyzer.analyze(self.text)
        tropes = analysis.get("tropes", {})
        imagery = analysis.get("imagery", {})

        if tropes.get("metaphor"):
            connotation["metaphors"].append(self._templates["connotation"]["metaphor"])
        if tropes.get("simile"):
            connotation["similes"].append(self._templates["connotation"]["simile"])
        if tropes.get("personification"):
            connotation["personification"].append(self._templates["connotation"]["personification"])
        if analysis.get("special_devices", {}).get("symbolism"):
            connotation["symbols"] = [self._templates["connotation"]["symbolism"]]

        for k, v in imagery.items():
            if v:
                connotation["imagery"].append(k)

        return connotation

    def _tp_attitude(self) -> str:
        """Determine speaker's attitude/tone"""
        sentiment = self._analyze_sentiment()
        valence = sentiment.get("valence", self._rules["defaults"]["valence"])
        if valence > self._rules["valence_pos"]:
            return self._templates["attitude"]["positive"]
        if valence < self._rules["valence_neg"]:
            return self._templates["attitude"]["negative"]
        return self._templates["attitude"]["neutral"]

    def _tp_shifts(self) -> List[Dict[str, Any]]:
        """Detect shifts in tone, perspective, or logic"""
        shifts = []
        zs = self._ensure_zero_shot()
        for i, line in enumerate(self.lines):
            if zs:
                try:
                    out = zs(line, [self._templates["shift"]["label"]])
                    if out["scores"][0] >= self._rules["shift_score_threshold"]:
                        shifts.append({
                            "line_number": i + 1,
                            "marker": self._templates["shift"]["semantic_marker"],
                            "type": self._templates["shift"]["semantic_type"],
                            "description": self._templates["shift"]["semantic_description"],
                        })
                except Exception:
                    pass
        if len(self.lines) > self._rules["shift_min_lines"]:
            mid_point = len(self.lines) // 2
            shifts.append({
                "line_number": mid_point,
                "marker": self._templates["shift"]["structural_marker"],
                "type": self._templates["shift"]["structural_type"],
                "description": self._templates["shift"]["structural_description"],
            })
        return shifts[: self._rules["shift_top_k"]]

    def _tp_title_revisited(self) -> str:
        """Reinterpret title after full analysis"""
        if self.lines:
            opening = self.lines[0][: self._rules["summary_line_preview"]]
            return self._templates["title_revisited"].format(opening=opening)
        return self._templates["title_revisited_no_text"]

    def _tp_theme(self) -> str:
        """Produce thematic statement"""
        try:
            import spacy
            nlp = spacy.load(self._settings.spacy.english_model if self.language == "en" else self._settings.spacy.multilingual_model)
            doc = nlp(self.text)
            content = [t.lemma_.lower() for t in doc if t.pos_ in {"NOUN", "VERB", "ADJ"} and t.is_alpha]
            freq = Counter(content)
            top = [w for w, _ in freq.most_common(self._rules["theme_top_k"])]
        except Exception:
            top = [w for w, _ in Counter(self.words).most_common(self._rules["theme_top_k"])]

        if not top:
            return self._templates["theme_default"]
        joined = ", ".join(top)
        return self._templates["theme_keywords"].format(keywords=joined)

    # ==================== SWIFT METHOD ====================

    def _analyze_swift(self) -> Dict[str, Any]:
        """
        SWIFT Method: Structure, Word Choice, Imagery, Figurative Language, Theme
        """
        return {
            "structure": self._swift_structure(),
            "word_choice": self._swift_word_choice(),
            "imagery": self._swift_imagery(),
            "figurative_language": self._swift_figurative(),
            "theme": self._swift_theme(),
        }

    def _analyze_t_swift(self) -> Dict[str, Any]:
        """
        T-SWIFT Method: Title, Speaker, Structure, Word Choice, Imagery, Figurative Language, Theme
        """
        base_swift = self._analyze_swift()
        base_swift["title"] = self._tp_title_prediction()
        base_swift["speaker"] = self._templates["t_swift_speaker"]
        return base_swift

    def _analyze_sift(self) -> Dict[str, Any]:
        """
        SIFT Method: Symbol, Images, Figurative Language, Tone/Theme
        """
        return {
            "symbol": self._tp_connotation().get("symbols", []),
            "images": self._swift_imagery(),
            "figurative_language": self._swift_figurative(),
            "tone": self._tp_attitude(),
            "theme": self._swift_theme(),
        }

    def _swift_structure(self) -> Dict[str, Any]:
        """Analyze structure (form, stanza, line breaks)"""
        return {
            "total_lines": len(self.lines),
            "form": self._templates["swift"]["form_free"]
            if not any(len(line.split()) == self._rules["haiku_line_check"] for line in self.lines[: self._rules["form_check_lines"]])
            else self._templates["swift"]["form_structured"],
            "line_variation": self._templates["swift"]["line_varied"]
            if len(set(len(l) for l in self.lines)) > self._rules["line_length_variance_threshold"]
            else self._templates["swift"]["line_uniform"],
            "stanza_pattern": self._templates["swift"]["stanza_continuous"] if "\n\n" not in self.text else self._templates["swift"]["stanza_split"],
        }

    def _swift_word_choice(self) -> Dict[str, Any]:
        """Analyze diction and word choice"""
        word_freq = Counter(self.words)
        avg_word_length = sum(len(w) for w in self.words) / max(self._rules["word_count_divisor_min"], len(self.words))

        return {
            "vocabulary_level": self._templates["swift"]["vocab_advanced"] if avg_word_length > self._rules["avg_word_length_advanced"] else self._templates["swift"]["vocab_accessible"],
            "unique_words": len(word_freq),
            "repeated_words": [w for w, c in word_freq.most_common(self._rules["repeated_words_top_k"])],
            "diction_type": self._templates["swift"]["diction_formal"] if avg_word_length > self._rules["avg_word_length_formal"] else self._templates["swift"]["diction_conversational"],
        }

    def _swift_imagery(self) -> Dict[str, int]:
        """Analyze sensory imagery"""
        analyzer = LiteraryDevicesAnalyzer(language=self.language)
        analysis = analyzer.analyze(self.text)
        imagery = analysis.get("imagery", {})
        return {k: len(v) for k, v in imagery.items()}

    def _swift_figurative(self) -> List[str]:
        """Identify figurative language"""
        analyzer = LiteraryDevicesAnalyzer(language=self.language)
        tropes = analyzer.analyze(self.text).get("tropes", {})
        devices = [k.capitalize() for k, v in tropes.items() if v]
        return devices if devices else [self._templates["swift"]["figurative_literal"]]

    def _swift_theme(self) -> str:
        """Identify central theme"""
        return self._tp_theme()

    # ==================== TOUCHSTONE METHOD ====================

    def _analyze_touchstone(self) -> Dict[str, Any]:
        """
        Matthew Arnold's Touchstone Method
        Compare against canonical passages
        """
        passages = select_touchstone_passages(self.text, limit=self._settings.touchstone.max_passages)
        comparisons = []
        text_lower = self.text.lower()

        for passage in passages:
            passage_lower = passage.lower()
            passage_words = set(passage_lower.split())
            text_words = set(text_lower.split())
            overlap = len(passage_words & text_words) / max(self._templates["touchstone"]["text_words_divisor_min"], len(passage_words))

            comparisons.append({
                "author": self._templates["touchstone"]["author"],
                "quality": self._templates["touchstone"]["quality"],
                "similarity": round(overlap, self._rules["rounding_digits"]),
                "assessment": self._templates["touchstone"]["assessment_strong"]
                if overlap > self._rules["overlap_strong"]
                else self._templates["touchstone"]["assessment_moderate"]
                if overlap > self._rules["overlap_moderate"]
                else self._templates["touchstone"]["assessment_minimal"],
                "passage": passage
            })

        return {
            "method": self._templates["touchstone"]["method"],
            "comparisons": comparisons,
            "overall_assessment": self._touchstone_overall(comparisons),
        }

    def _touchstone_overall(self, comparisons: List[Dict]) -> str:
        """Overall touchstone assessment"""
        strong_count = sum(1 for c in comparisons if c["assessment"] == self._templates["touchstone"]["assessment_strong"])

        if strong_count >= self._rules["overlap_strong_count_for_assessment"]:
            return self._templates["touchstone"]["overall_strong"]
        if strong_count == self._rules["overlap_single_count"]:
            return self._templates["touchstone"]["overall_moderate"]
        return self._templates["touchstone"]["overall_minimal"]

    # ==================== SENTIMENT ANALYSIS ====================

    def _analyze_sentiment(self) -> Dict[str, Any]:
        """
        Sentiment analysis using VADER (handles negation, intensity, punctuation)
        Falls back to manual for non-English or if VADER unavailable
        """
        # Use VADER for English (robust, handles "not happy", "very happy!!!", etc.)
        if self.language == "en":
            try:
                analyzer = get_vader_analyzer()
                scores = analyzer.polarity_scores(self.text)

                # VAD mapping from VADER scores
                valence = scores["compound"]  # -1 to 1
                arousal = min(
                    self._rules["arousal_max"],
                    (self.text.count("!") * self._rules["arousal_exclaim_weight"] + scores["pos"] + scores["neg"]) / self._rules["arousal_divisor"],
                )

                # Dominance from active vs passive voice signals (POS-based)
                dominance = self._rules["defaults"]["dominance"]
                try:
                    import spacy
                    nlp = spacy.load(self._settings.spacy.english_model)
                    doc = nlp(self.text)
                    active = sum(1 for t in doc if t.pos_ == "VERB")
                    passive = sum(1 for t in doc if t.dep_ == "auxpass")
                    dominance = ((active - passive) / max(self._rules["dominance_divisor_min"], len(doc))) * self._rules["dominance_scale"]
                    dominance = max(self._rules["dominance_min"], min(self._rules["dominance_max"], dominance))
                except Exception:
                    dominance = self._rules["defaults"]["dominance"]

                # Determine dominant emotion
                if valence > self._rules["valence_moderate"]:
                    dominant_emotion = self._templates["sentiment"]["dominant_positive"] if valence > self._rules["valence_strong"] else self._templates["sentiment"]["dominant_positive_moderate"]
                elif valence < -self._rules["valence_moderate"]:
                    dominant_emotion = self._templates["sentiment"]["dominant_negative"] if valence < -self._rules["valence_strong"] else self._templates["sentiment"]["dominant_negative_moderate"]
                else:
                    dominant_emotion = self._templates["sentiment"]["dominant_neutral"]

                # Line-by-line sentiment arc using VADER
                sentiment_arc = []
                for line in self.lines[: self._rules["sentiment_arc_lines"]]:
                    line_scores = analyzer.polarity_scores(line)
                    sentiment_arc.append(round(line_scores["compound"], self._rules["rounding_digits"]))

                return {
                    "valence": round(valence, self._rules["rounding_digits"]),
                    "arousal": round(arousal, self._rules["rounding_digits"]),
                    "dominance": round(dominance, self._rules["rounding_digits"]),
                    "sentiment_arc": sentiment_arc,
                    "dominant_emotion": dominant_emotion,
                    "emotion_distribution": self._calculate_emotion_distribution_vader(
                        self.text.lower(), analyzer
                    ),
                    "vader_scores": scores,  # Raw VADER output for reference
                }
            except Exception as e:
                # Fall back to manual if VADER fails
                pass

        # Multilingual transformer fallback
        return self._analyze_sentiment_transformer()

    def _analyze_sentiment_transformer(self) -> Dict[str, Any]:
        """Transformer-based sentiment for multilingual fallback"""
        try:
            model = self._settings.transformer.multilingual_sentiment_model
            clf = pipeline("sentiment-analysis", model=model, device=-1)
            out = clf(self.text[: self._rules["sentiment_model_max_chars"]])[0]
            label = out["label"]
            score = float(out["score"])
            mapped = self._settings.transformer.multilingual_sentiment_label_map.get(label, label).lower()
            valence = self._rules["defaults"]["valence"]
            if "pos" in mapped:
                valence = score
            elif "neg" in mapped:
                valence = -score

            return {
                "valence": round(valence, self._rules["rounding_digits"]),
                "arousal": self._rules["defaults"]["arousal"],
                "dominance": self._rules["defaults"]["dominance"],
                "sentiment_arc": [],
                "dominant_emotion": mapped,
                "emotion_distribution": {},
            }
        except Exception:
            return {
                "valence": self._rules["defaults"]["valence"],
                "arousal": self._rules["defaults"]["arousal"],
                "dominance": self._rules["defaults"]["dominance"],
                "sentiment_arc": [],
                "dominant_emotion": self._templates["sentiment"]["dominant_unknown"],
                "emotion_distribution": {},
            }

    def _calculate_emotion_distribution_vader(
        self, text: str, analyzer
    ) -> Dict[str, float]:
        """Calculate emotion distribution using VADER's pos/neg/neu scores"""
        scores = analyzer.polarity_scores(text)
        return {
            "positive": round(scores["pos"] * self._rules["percentage_scale"], self._rules["percentage_digits"]),
            "negative": round(scores["neg"] * self._rules["percentage_scale"], self._rules["percentage_digits"]),
            "neutral": round(scores["neu"] * self._rules["percentage_scale"], self._rules["percentage_digits"]),
        }

    def _calculate_emotion_distribution(self, text: str) -> Dict[str, float]:
        """Calculate distribution of basic emotions"""
        try:
            model = self._settings.transformer.emotion_model
            clf = pipeline("text-classification", model=model, device=-1, top_k=None)
            out = clf(text[: self._rules["classifier_max_chars"]])
            distribution = {}
            for item in out:
                label = item["label"].lower()
                distribution[label] = round(float(item["score"]) * self._rules["percentage_scale"], self._rules["percentage_digits"])
            return distribution
        except Exception:
            return {}

    def _ensure_zero_shot(self):
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            model_name = self._settings.transformer.generalist_zero_shot_model
            self._zero_shot = pipeline("zero-shot-classification", model=model_name, device=-1)
        except Exception:
            self._zero_shot = None
        return self._zero_shot


def analyze_with_multiple_methods(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Convenience function to run all advanced analysis methods
    """
    engine = AdvancedAnalysisEngine(language)
    rules = get_advanced_analysis_rules()
    return engine.analyze(text, methods=list(rules["full_methods"]))
