"""
Advanced Analysis Module
TP-CASTT, SWIFT, Touchstone Method, Sentiment Analysis
Based on quantitative_poetry_metrics.md & ultimate_literary_master_system.md
"""

import re
from typing import Dict, List, Any, Optional
from collections import Counter


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

    def analyze(self, text: str, methods: List[str] = None) -> Dict[str, Any]:
        """Run advanced analysis with specified methods"""
        self.text = text
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]
        self.words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        if methods is None:
            methods = ["tp_castt", "swift", "sentiment"]

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
            "theme": self._tp_theme()
        }

    def _tp_title_prediction(self) -> str:
        """Predict poem meaning from title (first line if no title)"""
        if self.lines:
            first_line = self.lines[0]
            return f"Based on the opening line '{first_line[:50]}...', the poem appears to explore themes related to this initial imagery."
        return "No title or opening line available for prediction."

    def _tp_paraphrase(self) -> str:
        """Paraphrase the literal meaning"""
        # Simple paraphrase - in production, use NLP summarization
        if len(self.lines) <= 4:
            return " ".join(self.lines)
        else:
            return f"This {len(self.lines)}-line poem describes a sequence of images and ideas, moving from {self.lines[0][:30] if self.lines else 'unknown'} to {self.lines[-1][:30] if self.lines else 'unknown'}."

    def _tp_connotation(self) -> Dict[str, List[str]]:
        """Identify figurative devices and connotations"""
        connotation = {
            "metaphors": [],
            "similes": [],
            "personification": [],
            "symbols": [],
            "imagery": []
        }

        text_lower = self.text.lower()

        # Detect metaphors
        if any(word in text_lower for word in ["is a", "was a", "becomes", "are"]):
            connotation["metaphors"].append("Direct comparisons detected")

        # Detect similes
        if "like" in text_lower or "as" in text_lower:
            connotation["similes"].append("Comparisons using 'like' or 'as'")

        # Detect personification
        human_verbs = ["whisper", "sing", "dance", "cry", "laugh", "smile"]
        if any(v in text_lower for v in human_verbs):
            connotation["personification"].append("Human attributes given to non-human entities")

        # Detect symbols
        symbols = ["rose", "dove", "eagle", "sun", "moon", "star", "ocean", "mountain"]
        found_symbols = [s for s in symbols if s in text_lower]
        if found_symbols:
            connotation["symbols"] = found_symbols

        # Detect imagery types
        if any(w in text_lower for w in ["see", "look", "bright", "dark", "color"]):
            connotation["imagery"].append("Visual")
        if any(w in text_lower for w in ["hear", "sound", "loud", "quiet"]):
            connotation["imagery"].append("Auditory")
        if any(w in text_lower for w in ["touch", "feel", "warm", "cold"]):
            connotation["imagery"].append("Tactile")

        return connotation

    def _tp_attitude(self) -> str:
        """Determine speaker's attitude/tone"""
        positive_words = ["love", "joy", "beautiful", "wonderful", "happy", "bright", "hope"]
        negative_words = ["hate", "sad", "ugly", "terrible", "dark", "despair", "death"]

        pos_count = sum(self.text.lower().count(w) for w in positive_words)
        neg_count = sum(self.text.lower().count(w) for w in negative_words)

        if pos_count > neg_count * 1.5:
            return "Positive/Optimistic - The speaker expresses hope, joy, or appreciation"
        elif neg_count > pos_count * 1.5:
            return "Negative/Pessimistic - The speaker expresses sorrow, anger, or despair"
        else:
            return "Neutral/Contemplative - The speaker maintains a balanced or reflective tone"

    def _tp_shifts(self) -> List[Dict[str, Any]]:
        """Detect shifts in tone, perspective, or logic"""
        shifts = []

        # Look for shift markers
        shift_markers = ["but", "yet", "however", "although", "suddenly", "then", "now", "once"]
        
        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for marker in shift_markers:
                if marker in line_lower:
                    shifts.append({
                        "line_number": i + 1,
                        "marker": marker,
                        "type": "logical_shift",
                        "description": f"Shift indicated by '{marker}'"
                    })

        # Check for stanza breaks
        if len(self.lines) > 4:
            mid_point = len(self.lines) // 2
            shifts.append({
                "line_number": mid_point,
                "marker": "structural",
                "type": "structural_shift",
                "description": "Potential volta/turn at poem's midpoint"
            })

        return shifts[:5]

    def _tp_title_revisited(self) -> str:
        """Reinterpret title after full analysis"""
        if self.lines:
            return f"After analyzing the complete poem, the opening '{self.lines[0][:30]}...' takes on deeper meaning in the context of the work's overall themes."
        return "Title reinterpretation requires text analysis."

    def _tp_theme(self) -> str:
        """Produce thematic statement"""
        # Simple theme detection based on word frequency
        theme_words = {
            "love": ["love", "heart", "passion", "romance", "beloved"],
            "death": ["death", "die", "dead", "mortal", "grave"],
            "nature": ["nature", "tree", "flower", "bird", "river", "mountain"],
            "time": ["time", "clock", "hour", "moment", "eternal"],
            "hope": ["hope", "dream", "wish", "faith", "believe"],
            "loss": ["loss", "gone", "missing", "farewell", "parting"]
        }

        text_lower = self.text.lower()
        theme_scores = {
            theme: sum(text_lower.count(w) for w in words)
            for theme, words in theme_words.items()
        }

        dominant_theme = max(theme_scores, key=theme_scores.get) if any(v > 0 for v in theme_scores.values()) else "universal human experience"

        return f"The poem explores the theme of {dominant_theme}, examining its complexities through imagery and figurative language."

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
            "theme": self._swift_theme()
        }

    def _analyze_t_swift(self) -> Dict[str, Any]:
        """
        T-SWIFT Method: Title, Speaker, Structure, Word Choice, Imagery, Figurative Language, Theme
        """
        base_swift = self._analyze_swift()
        base_swift["title"] = self._tp_title_prediction()
        base_swift["speaker"] = "A contemplative observer" # Basic fallback, usually requires deep persona analysis
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
            "theme": self._swift_theme()
        }

    def _swift_structure(self) -> Dict[str, Any]:
        """Analyze structure (form, stanza, line breaks)"""
        return {
            "total_lines": len(self.lines),
            "form": "free_verse" if not any(len(line.split()) == 5 for line in self.lines[:3]) else "structured",
            "line_variation": "varied" if len(set(len(l) for l in self.lines)) > 3 else "uniform",
            "stanza_pattern": "continuous" if "\n\n" not in self.text else "stanzac"
        }

    def _swift_word_choice(self) -> Dict[str, Any]:
        """Analyze diction and word choice"""
        word_freq = Counter(self.words)
        avg_word_length = sum(len(w) for w in self.words) / max(1, len(self.words))

        return {
            "vocabulary_level": "advanced" if avg_word_length > 5 else "accessible",
            "unique_words": len(word_freq),
            "repeated_words": [w for w, c in word_freq.most_common(5)],
            "diction_type": "formal" if avg_word_length > 5.5 else "conversational"
        }

    def _swift_imagery(self) -> Dict[str, int]:
        """Analyze sensory imagery"""
        imagery_counts = {"visual": 0, "auditory": 0, "tactile": 0, "gustatory": 0, "olfactory": 0}

        text_lower = self.text.lower()
        visual_words = ["see", "look", "bright", "dark", "color", "shine"]
        auditory_words = ["hear", "sound", "loud", "quiet", "music"]
        tactile_words = ["touch", "feel", "warm", "cold", "soft"]

        imagery_counts["visual"] = sum(text_lower.count(w) for w in visual_words)
        imagery_counts["auditory"] = sum(text_lower.count(w) for w in auditory_words)
        imagery_counts["tactile"] = sum(text_lower.count(w) for w in tactile_words)

        return imagery_counts

    def _swift_figurative(self) -> List[str]:
        """Identify figurative language"""
        devices = []
        text_lower = self.text.lower()

        if "like" in text_lower or "as" in text_lower:
            devices.append("Simile")
        if any(w in text_lower for w in ["is a", "was a", "becomes"]):
            devices.append("Metaphor")
        if any(w in text_lower for w in ["whisper", "sing", "dance"]):
            devices.append("Personification")
        if any(w in text_lower for w in ["boom", "crash", "buzz"]):
            devices.append("Onomatopoeia")

        return devices if devices else ["Literal language dominant"]

    def _swift_theme(self) -> str:
        """Identify central theme"""
        return self._tp_theme()

    # ==================== TOUCHSTONE METHOD ====================

    def _analyze_touchstone(self) -> Dict[str, Any]:
        """
        Matthew Arnold's Touchstone Method
        Compare against canonical passages
        """
        touchstones = [
            {
                "author": "Milton",
                "passage": "And courage never to submit or yield",
                "quality": "high_seriousness"
            },
            {
                "author": "Shakespeare",
                "passage": "Shall I compare thee to a summer's day",
                "quality": "beauty_and_truth"
            },
            {
                "author": "Homer",
                "passage": "Sing goddess the anger of Peleus son Achilles",
                "quality": "epic_grandeur"
            },
            {
                "author": "Dante",
                "passage": "In the middle of the journey of our life",
                "quality": "spiritual_depth"
            }
        ]

        # Simple comparison based on word overlap and sentiment
        comparisons = []
        text_lower = self.text.lower()

        for touchstone in touchstones:
            touchstone_lower = touchstone["passage"].lower()
            # Calculate word overlap
            touchstone_words = set(touchstone_lower.split())
            text_words = set(text_lower.split())
            overlap = len(touchstone_words & text_words) / max(1, len(touchstone_words))

            comparisons.append({
                "author": touchstone["author"],
                "quality": touchstone["quality"],
                "similarity": round(overlap, 3),
                "assessment": "strong" if overlap > 0.3 else "moderate" if overlap > 0.1 else "minimal"
            })

        return {
            "method": "Matthew Arnold's Touchstone Method",
            "comparisons": comparisons,
            "overall_assessment": self._touchstone_overall(comparisons)
        }

    def _touchstone_overall(self, comparisons: List[Dict]) -> str:
        """Overall touchstone assessment"""
        strong_count = sum(1 for c in comparisons if c["assessment"] == "strong")
        
        if strong_count >= 2:
            return "The work demonstrates qualities comparable to canonical masters, showing high seriousness and artistic merit."
        elif strong_count == 1:
            return "The work shows promise with some qualities approaching canonical standards, though further development is needed."
        else:
            return "The work shows individual voice but lacks the universal qualities found in touchstone passages from established masters."

    # ==================== SENTIMENT ANALYSIS ====================

    def _analyze_sentiment(self) -> Dict[str, Any]:
        """
        Sentiment analysis with VAD (Valence, Arousal, Dominance)
        """
        # Simple lexicon-based sentiment
        positive_words = {
            "love": 0.8, "joy": 0.9, "happy": 0.8, "beautiful": 0.7, "wonderful": 0.8,
            "hope": 0.6, "bright": 0.5, "peace": 0.7, "gentle": 0.5, "sweet": 0.6,
            "delight": 0.8, "pleasure": 0.7, "bliss": 0.9, "grace": 0.6, "glory": 0.7
        }

        negative_words = {
            "hate": -0.8, "sad": -0.7, "death": -0.6, "pain": -0.8, "sorrow": -0.8,
            "fear": -0.7, "anger": -0.7, "dark": -0.4, "despair": -0.9, "grief": -0.8,
            "tear": -0.6, "mourn": -0.8, "suffer": -0.8, "agony": -0.9, "torment": -0.9
        }

        text_lower = self.text.lower()
        words = text_lower.split()

        # Calculate valence (positive/negative)
        valence_score = 0
        for word in words:
            if word in positive_words:
                valence_score += positive_words[word]
            elif word in negative_words:
                valence_score += negative_words[word]

        total_words = len(words)
        valence = valence_score / max(1, total_words) * 10

        # Normalize to -1 to 1
        valence = max(-1, min(1, valence))

        # Arousal (intensity) - based on exclamation marks and intense words
        intense_words = ["very", "extremely", "absolutely", "totally", "completely", "never", "always"]
        arousal = min(1, (text_lower.count("!") * 0.2 + sum(1 for w in words if w in intense_words) / max(1, total_words) * 5))

        # Dominance (control) - based on active vs passive voice indicators
        active_words = ["will", "shall", "must", "can", "do", "make", "create"]
        passive_words = ["was", "were", "been", "might", "could", "would"]
        dominance = (sum(1 for w in words if w in active_words) - sum(1 for w in words if w in passive_words)) / max(1, total_words) * 2
        dominance = max(-1, min(1, dominance))

        # Determine dominant emotion
        if valence > 0.3:
            dominant_emotion = "joy/love" if valence > 0.6 else "contentment"
        elif valence < -0.3:
            dominant_emotion = "sorrow/fear" if valence < -0.6 else "melancholy"
        else:
            dominant_emotion = "neutral/contemplative"

        # Sentiment arc (line by line)
        sentiment_arc = []
        for line in self.lines:
            line_lower = line.lower()
            line_score = sum(positive_words.get(w, 0) for w in line_lower.split())
            line_score -= sum(negative_words.get(w, 0) for w in line_lower.split())
            sentiment_arc.append(round(line_score / max(1, len(line.split())), 3))

        return {
            "valence": round(valence, 3),
            "arousal": round(arousal, 3),
            "dominance": round(dominance, 3),
            "sentiment_arc": sentiment_arc[:20],  # First 20 lines
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": self._calculate_emotion_distribution(text_lower)
        }

    def _calculate_emotion_distribution(self, text: str) -> Dict[str, float]:
        """Calculate distribution of basic emotions"""
        emotions = {
            "joy": ["joy", "happy", "delight", "pleasure", "glad", "merry"],
            "sadness": ["sad", "sorrow", "grief", "tear", "mourn", "weep"],
            "anger": ["anger", "rage", "fury", "hate", "wrath", "fierce"],
            "fear": ["fear", "terror", "dread", "fright", "panic", "tremble"],
            "love": ["love", "beloved", "passion", "romance", "heart", "adore"],
            "surprise": ["surprise", "wonder", "amazement", "shock", "astonish"]
        }

        distribution = {}
        total_words = len(text.split())

        for emotion, words in emotions.items():
            count = sum(text.count(w) for w in words)
            distribution[emotion] = round(count / max(1, total_words) * 100, 2)

        return distribution


def analyze_with_multiple_methods(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Convenience function to run all advanced analysis methods
    """
    engine = AdvancedAnalysisEngine(language)
    return engine.analyze(text, methods=["tp_castt", "swift", "touchstone", "sentiment"])
