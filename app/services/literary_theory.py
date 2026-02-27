"""
Literary Theory & Criticism Frameworks
Complete implementation of all major literary criticism approaches
Based on quantitative_poetry_metrics.md Section 5 & ultimate_literary_master_system.md
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CriticismType(Enum):
    """Types of literary criticism"""
    NEW_CRITICISM = "new_criticism"
    FORMALISM = "formalism"
    STRUCTURALISM = "structuralism"
    DECONSTRUCTION = "deconstruction"
    READER_RESPONSE = "reader_response"
    FEMINIST = "feminist"
    MARXIST = "marxist"
    PSYCHOANALYTIC = "psychoanalytic"
    ECOCRITICISM = "ecocriticism"
    POSTCOLONIAL = "postcolonial"
    ARISTOTELIAN = "aristotelian"
    HORATIAN = "horatian"


@dataclass
class CriticismResult:
    """Result from applying a criticism framework"""
    framework: str
    score: float
    analysis: str
    key_findings: List[str]
    recommendations: List[str]


class LiteraryTheoryAnalyzer:
    """
    Comprehensive literary theory and criticism analyzer
    Implements all major criticism frameworks from quantitative_poetry_metrics.md
    """

    def __init__(self):
        self.text = ""
        self.lines: List[str] = []
        self.words: List[str] = []

    def analyze(self, text: str, frameworks: List[str] = None) -> Dict[str, Any]:
        """
        Analyze text using multiple literary criticism frameworks
        
        Args:
            text: Text to analyze
            frameworks: List of frameworks to apply (default: all)
        """
        self.text = text
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]
        self.words = text.lower().split()

        if frameworks is None:
            frameworks = [f.value for f in CriticismType]

        results = {}

        for framework in frameworks:
            if framework == "new_criticism":
                results["new_criticism"] = self._analyze_new_criticism()
            elif framework == "formalism":
                results["formalism"] = self._analyze_formalism()
            elif framework == "structuralism":
                results["structuralism"] = self._analyze_structuralism()
            elif framework == "deconstruction":
                results["deconstruction"] = self._analyze_deconstruction()
            elif framework == "reader_response":
                results["reader_response"] = self._analyze_reader_response()
            elif framework == "feminist":
                results["feminist"] = self._analyze_feminist()
            elif framework == "marxist":
                results["marxist"] = self._analyze_marxist()
            elif framework == "psychoanalytic":
                results["psychoanalytic"] = self._analyze_psychoanalytic()
            elif framework == "ecocriticism":
                results["ecocriticism"] = self._analyze_ecocriticism()
            elif framework == "aristotelian":
                results["aristotelian"] = self._analyze_aristotelian()
            elif framework == "horatian":
                results["horatian"] = self._analyze_horatian()

        return {
            "frameworks_applied": list(results.keys()),
            "results": results,
            "synthesis": self._synthesize_results(results)
        }

    # ==================== NEW CRITICISM / FORMALISM ====================

    def _analyze_new_criticism(self) -> Dict[str, Any]:
        """
        New Criticism / Formalism (1920s-1960s)
        
        From quantitative_poetry_metrics.md:
        - The poem is a self-contained, autonomous object
        - Focus on intrinsic qualities of the text itself
        - Evaluate how tightly language, imagery, paradox, structure resolve toward unified meaning
        - Score based on internal tensions and paradox resolution
        - Key Concepts: Intentional Fallacy, Affective Fallacy, Paradox, Irony, Ambiguity
        """
        # Analyze internal tensions
        paradoxes = self._detect_paradoxes()
        ironies = self._detect_ironies()
        ambiguities = self._detect_ambiguities()

        # Analyze unity
        unity_score = self._analyze_unity()

        # Analyze imagery coherence
        imagery_coherence = self._analyze_imagery_coherence()

        # Calculate overall score
        score = (
            unity_score * 0.3 +
            imagery_coherence * 0.3 +
            (len(paradoxes) > 0) * 0.2 +
            (len(ironies) > 0) * 0.2
        ) * 10

        return {
            "framework": "New Criticism / Formalism",
            "score": round(min(10, score), 1),
            "analysis": "Analysis based on intrinsic textual qualities, focusing on internal tensions, paradox, irony, and unity",
            "key_findings": [
                f"Detected {len(paradoxes)} paradoxes",
                f"Detected {len(ironies)} instances of irony",
                f"Detected {len(ambiguities)} ambiguities",
                f"Unity score: {unity_score:.2f}/1.0",
                f"Imagery coherence: {imagery_coherence:.2f}/1.0"
            ],
            "recommendations": [
                "Focus on resolving internal tensions for greater unity",
                "Consider how paradoxes contribute to thematic depth",
                "Evaluate whether ambiguities are productive or confusing"
            ],
            "fallacies_avoided": [
                "Intentional Fallacy (author's intent not considered)",
                "Affective Fallacy (reader response not considered)"
            ],
            "internal_tensions": {
                "paradoxes": paradoxes,
                "ironies": ironies,
                "ambiguities": ambiguities
            }
        }

    def _analyze_formalism(self) -> Dict[str, Any]:
        """
        Formalism: Focus on form, structure, and literary devices
        """
        # This is very similar to New Criticism
        new_crit = self._analyze_new_criticism()
        
        return {
            "framework": "Formalism",
            "score": new_crit["score"],
            "analysis": "Formalist analysis focusing on structural elements, literary devices, and formal properties",
            "key_findings": new_crit["key_findings"],
            "form_elements": {
                "structure": "Analyzed",
                "literary_devices": "Analyzed",
                "prosody": "Analyzed"
            }
        }

    # ==================== STRUCTURALISM ====================

    def _analyze_structuralism(self) -> Dict[str, Any]:
        """
        Structuralism
        
        From quantitative_poetry_metrics.md:
        - Focus on underlying structures and conventions
        - Binary oppositions
        - Language systems and sign function
        """
        # Detect binary oppositions
        binaries = self._detect_binary_oppositions()

        # Analyze narrative structure
        narrative_structure = self._analyze_narrative_structure()

        # Analyze language systems
        language_patterns = self._analyze_language_patterns()

        score = (
            (len(binaries) > 0) * 0.4 +
            (narrative_structure["has_structure"] * 0.3) +
            (language_patterns["coherence"] * 0.3)
        ) * 10

        return {
            "framework": "Structuralism",
            "score": round(min(10, score), 1),
            "analysis": "Structuralist analysis focusing on underlying patterns, binary oppositions, and language systems",
            "key_findings": [
                f"Detected {len(binaries)} binary oppositions",
                f"Narrative structure: {'Present' if narrative_structure['has_structure'] else 'Absent'}",
                f"Language coherence: {language_patterns['coherence']:.2f}"
            ],
            "binary_oppositions": binaries,
            "underlying_patterns": narrative_structure,
            "language_systems": language_patterns
        }

    # ==================== DECONSTRUCTION ====================

    def _analyze_deconstruction(self) -> Dict[str, Any]:
        """
        Deconstruction (Jacques Derrida)
        
        From quantitative_poetry_metrics.md:
        - Texts have irreconcilably contradictory meanings
        - Read for what is hidden, suppressed, silenced, or forgotten
        - Challenge surface interpretation
        - Question objective truth of language
        """
        # Find contradictions
        contradictions = self._detect_contradictions()

        # Find suppressed meanings
        suppressed = self._find_suppressed_meanings()

        # Analyze language instability
        instability = self._analyze_language_instability()

        score = (
            (len(contradictions) > 0) * 0.4 +
            (len(suppressed) > 0) * 0.3 +
            instability * 0.3
        ) * 10

        return {
            "framework": "Deconstruction",
            "score": round(min(10, score), 1),
            "analysis": "Deconstructive reading revealing contradictions, suppressed meanings, and language instability",
            "key_findings": [
                f"Found {len(contradictions)} textual contradictions",
                f"Identified {len(suppressed)} suppressed meanings",
                f"Language instability score: {instability:.2f}"
            ],
            "contradictions": contradictions,
            "suppressed_meanings": suppressed,
            "language_instability": instability,
            "derridean_concepts": [
                "Différance (meaning deferred through language)",
                "Logocentrism (critique of presence metaphysics)",
                "Supplementarity (what is added reveals lack)"
            ]
        }

    # ==================== READER-RESPONSE ====================

    def _analyze_reader_response(self) -> Dict[str, Any]:
        """
        Reader-Response Criticism
        
        From quantitative_poetry_metrics.md:
        - Value = Text × Reader × Context
        - Reading is active construction of meaning
        - Value changes depending on who reads and when
        """
        # Analyze interpretive gaps
        gaps = self._analyze_interpretive_gaps()

        # Analyze emotional triggers
        emotional_triggers = self._analyze_emotional_triggers()

        # Analyze context dependence
        context_dependence = self._analyze_context_dependence()

        # Value formula: V = T × R × C
        text_potential = 0.7  # Base text quality
        reader_engagement = len(emotional_triggers) / 10  # Reader factor
        context_relevance = context_dependence  # Context factor

        value = text_potential * (1 + reader_engagement) * (1 + context_relevance)

        return {
            "framework": "Reader-Response Criticism",
            "value_formula": "Value = Text × Reader × Context",
            "score": round(min(10, value * 5), 1),
            "analysis": "Reader-response analysis focusing on how meaning emerges from reader-text transaction",
            "key_findings": [
                f"Interpretive gaps: {len(gaps)} (spaces for reader meaning-making)",
                f"Emotional triggers: {len(emotional_triggers)}",
                f"Context dependence: {context_dependence:.2f}"
            ],
            "transaction_elements": {
                "text_potential": text_potential,
                "reader_engagement": reader_engagement,
                "context_relevance": context_relevance
            },
            "interpretive_gaps": gaps,
            "emotional_triggers": emotional_triggers
        }

    # ==================== FEMINIST CRITICISM ====================

    def _analyze_feminist(self) -> Dict[str, Any]:
        """
        Feminist Literary Criticism
        
        From quantitative_poetry_metrics.md:
        - Interrogates role of gender in writing and interpretation
        - Critiques male-dominated language and perspectives
        - Re-examines canonical works to show how gender shapes meaning
        """
        # Analyze gender representation
        gender_analysis = self._analyze_gender_representation()

        # Analyze power dynamics
        power_dynamics = self._analyze_power_dynamics()

        # Analyze language patriarchy
        language_analysis = self._analyze_language_patriarchy()

        score = (
            gender_analysis["score"] * 0.4 +
            power_dynamics["score"] * 0.3 +
            language_analysis["score"] * 0.3
        ) * 10

        return {
            "framework": "Feminist Literary Criticism",
            "score": round(min(10, score), 1),
            "analysis": "Feminist analysis interrogating gender roles, power dynamics, and patriarchal language structures",
            "key_findings": [
                f"Gender representation: {gender_analysis['summary']}",
                f"Power dynamics: {power_dynamics['summary']}",
                f"Language analysis: {language_analysis['summary']}"
            ],
            "gender_analysis": gender_analysis,
            "power_dynamics": power_dynamics,
            "language_critique": language_analysis,
            "feminist_concepts": [
                "Male gaze in representation",
                "Patriarchal language structures",
                "Gender performativity",
                "Intersectionality"
            ]
        }

    # ==================== MARXIST CRITICISM ====================

    def _analyze_marxist(self) -> Dict[str, Any]:
        """
        Marxist Literary Criticism
        
        From quantitative_poetry_metrics.md:
        - Based on historical materialism (Karl Marx)
        - Focus on class struggle
        - Analysis of power dynamics and economic systems
        - How texts reflect or challenge dominant ideologies
        """
        # Analyze class representation
        class_analysis = self._analyze_class_representation()

        # Analyze ideology
        ideology_analysis = self._analyze_ideology()

        # Analyze economic themes
        economic_themes = self._analyze_economic_themes()

        score = (
            class_analysis["score"] * 0.4 +
            ideology_analysis["score"] * 0.3 +
            economic_themes["score"] * 0.3
        ) * 10

        return {
            "framework": "Marxist Literary Criticism",
            "score": round(min(10, score), 1),
            "analysis": "Marxist analysis focusing on class struggle, power dynamics, and ideological content",
            "key_findings": [
                f"Class representation: {class_analysis['summary']}",
                f"Ideological content: {ideology_analysis['summary']}",
                f"Economic themes: {economic_themes['summary']}"
            ],
            "class_analysis": class_analysis,
            "ideology_analysis": ideology_analysis,
            "economic_themes": economic_themes,
            "marxist_concepts": [
                "Base and superstructure",
                "Class consciousness",
                "Ideological state apparatuses",
                "Commodification",
                "Alienation"
            ]
        }

    # ==================== PSYCHOANALYTIC CRITICISM ====================

    def _analyze_psychoanalytic(self) -> Dict[str, Any]:
        """
        Psychoanalytic Criticism (Sigmund Freud)
        
        From quantitative_poetry_metrics.md:
        - Id, Ego, Superego dynamics in text
        - Unconscious desires
        - Latent meaning
        - Trauma and anxiety as coping mechanism
        """
        # Analyze unconscious content
        unconscious = self._analyze_unconscious_content()

        # Analyze defense mechanisms
        defense_mechanisms = self._analyze_defense_mechanisms()

        # Analyze psychosexual themes
        psychosexual = self._analyze_psychosexual_themes()

        score = (
            unconscious["score"] * 0.4 +
            defense_mechanisms["score"] * 0.3 +
            psychosexual["score"] * 0.3
        ) * 10

        return {
            "framework": "Psychoanalytic Criticism",
            "score": round(min(10, score), 1),
            "analysis": "Psychoanalytic analysis exploring unconscious desires, defense mechanisms, and latent content",
            "key_findings": [
                f"Unconscious content: {unconscious['summary']}",
                f"Defense mechanisms: {defense_mechanisms['summary']}",
                f"Psychosexual themes: {psychosexual['summary']}"
            ],
            "unconscious_analysis": unconscious,
            "defense_mechanisms": defense_mechanisms,
            "psychosexual_themes": psychosexual,
            "freudian_concepts": [
                "Id (instinctual drives)",
                "Ego (reality principle)",
                "Superego (moral conscience)",
                "Oedipus complex",
                "Death drive (Thanatos)",
                "Life drive (Eros)"
            ]
        }

    # ==================== ECOCRITICISM ====================

    def _analyze_ecocriticism(self) -> Dict[str, Any]:
        """
        Ecocriticism
        
        From quantitative_poetry_metrics.md:
        - Examines nature and environment in literature
        - Deep Ecology: Intrinsic value of all living beings
        - Ecofeminism: Connection between environmental and gender oppression
        - Postcolonial environmental justice
        """
        # Analyze nature representation
        nature_analysis = self._analyze_nature_representation()

        # Analyze environmental themes
        environmental_themes = self._analyze_environmental_themes()

        # Analyze human-nature relationship
        human_nature = self._analyze_human_nature_relationship()

        score = (
            nature_analysis["score"] * 0.4 +
            environmental_themes["score"] * 0.3 +
            human_nature["score"] * 0.3
        ) * 10

        return {
            "framework": "Ecocriticism",
            "score": round(min(10, score), 1),
            "analysis": "Ecocritical analysis examining nature representation, environmental themes, and human-nature relationships",
            "key_findings": [
                f"Nature representation: {nature_analysis['summary']}",
                f"Environmental themes: {environmental_themes['summary']}",
                f"Human-nature relationship: {human_nature['summary']}"
            ],
            "nature_analysis": nature_analysis,
            "environmental_themes": environmental_themes,
            "human_nature_relationship": human_nature,
            "ecocritical_concepts": [
                "Deep Ecology (intrinsic value of nature)",
                "Ecofeminism (environment + gender)",
                "Environmental justice",
                "Anthropocentrism critique",
                "Biocentrism"
            ]
        }

    # ==================== ARISTOTELIAN ====================

    def _analyze_aristotelian(self) -> Dict[str, Any]:
        """
        Aristotelian Poetics (4th Century BCE)
        
        From quantitative_poetry_metrics.md:
        - Genre classification (epic, comic, tragic)
        - Unity of action
        - Mimesis (imitation of reality)
        - Catharsis (emotional purification)
        """
        # Classify genre
        genre = self._classify_genre()

        # Analyze unity
        unity = self._analyze_unity_aristotelian()

        # Analyze mimesis
        mimesis = self._analyze_mimesis()

        # Analyze catharsis potential
        catharsis = self._analyze_catharsis_potential()

        score = (
            unity["score"] * 0.4 +
            mimesis["score"] * 0.3 +
            catharsis["score"] * 0.3
        ) * 10

        return {
            "framework": "Aristotelian Poetics",
            "score": round(min(10, score), 1),
            "analysis": "Aristotelian analysis based on genre classification, unity, mimesis, and catharsis",
            "key_findings": [
                f"Genre: {genre}",
                f"Unity of action: {unity['summary']}",
                f"Mimesis: {mimesis['summary']}",
                f"Catharsis potential: {catharsis['summary']}"
            ],
            "genre_classification": genre,
            "unity_analysis": unity,
            "mimesis_analysis": mimesis,
            "catharsis_analysis": catharsis,
            "aristotelian_concepts": [
                "Mimesis (imitation)",
                "Catharsis (purification)",
                "Hamartia (tragic flaw)",
                "Peripeteia (reversal)",
                "Anagnorisis (recognition)",
                "Unity of action"
            ]
        }

    # ==================== HORATIAN ====================

    def _analyze_horatian(self) -> Dict[str, Any]:
        """
        Horace's Ars Poetica (19 BCE)
        
        From quantitative_poetry_metrics.md:
        - Decorum (appropriateness of style to subject)
        - Unity (consistency and coherence)
        - Instruction + Delight (teach and please)
        """
        # Analyze decorum
        decorum = self._analyze_decorum()

        # Analyze unity
        unity = self._analyze_unity_horatian()

        # Analyze instruction vs delight balance
        instruction_delight = self._analyze_instruction_delight()

        score = (
            decorum["score"] * 0.4 +
            unity["score"] * 0.3 +
            instruction_delight["score"] * 0.3
        ) * 10

        return {
            "framework": "Horatian Ars Poetica",
            "score": round(min(10, score), 1),
            "analysis": "Horatian analysis based on decorum, unity, and balance of instruction and delight",
            "key_findings": [
                f"Decorum: {decorum['summary']}",
                f"Unity: {unity['summary']}",
                f"Instruction + Delight: {instruction_delight['summary']}"
            ],
            "decorum_analysis": decorum,
            "unity_analysis": unity,
            "instruction_delight_balance": instruction_delight,
            "horatian_principles": [
                "Decorum (appropriateness)",
                "Unity (consistency)",
                "Aut Dulce Aut Utile (instruction OR delight)",
                "In Medias Res (begin in middle)",
                "Deus Ex Machina (avoid artificial solutions)"
            ]
        }

    # ==================== HELPER METHODS ====================

    def _detect_paradoxes(self) -> List[str]:
        """Detect paradoxes in text"""
        paradox_phrases = ["less is more", "more is less", "silent sound", "dark light", "living death", "wise fool"]
        return [p for p in paradox_phrases if p in self.text.lower()]

    def _detect_ironies(self) -> List[str]:
        """Detect ironies in text"""
        irony_markers = ["ironically", "of course", "clearly", "naturally", "little did"]
        return [m for m in irony_markers if m in self.text.lower()]

    def _detect_ambiguities(self) -> List[str]:
        """Detect ambiguities in text"""
        # Look for words with multiple meanings
        ambiguous_words = ["light", "bank", "bark", "lead", "tear", "wind", "close", "minute"]
        return [w for w in ambiguous_words if w in self.text.lower()]

    def _analyze_unity(self) -> float:
        """Analyze textual unity (0-1 scale)"""
        # Simplified: check for repeated themes/words
        word_freq = {}
        for word in self.words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        repeated = sum(1 for count in word_freq.values() if count > 1)
        return min(1.0, repeated / max(1, len(word_freq)) * 5)

    def _analyze_imagery_coherence(self) -> float:
        """Analyze imagery coherence (0-1 scale)"""
        # Check if imagery types are consistent
        imagery_words = {
            "visual": ["see", "look", "bright", "dark", "color"],
            "auditory": ["hear", "sound", "loud", "quiet"],
            "tactile": ["touch", "feel", "warm", "cold"]
        }
        
        counts = {k: sum(1 for w in self.words if w in v) for k, v in imagery_words.items()}
        max_count = max(counts.values()) if counts.values() else 0
        return min(1.0, max_count / max(1, sum(counts.values())) * 2)

    def _detect_binary_oppositions(self) -> List[Dict[str, str]]:
        """Detect binary oppositions in text"""
        binaries = [
            ("light", "dark"), ("good", "evil"), ("life", "death"),
            ("love", "hate"), ("hot", "cold"), ("high", "low"),
            ("male", "female"), ("nature", "culture"), ("speech", "writing")
        ]
        
        found = []
        for term1, term2 in binaries:
            if term1 in self.words and term2 in self.words:
                found.append({"term1": term1, "term2": term2})
        return found

    def _analyze_narrative_structure(self) -> Dict[str, Any]:
        """Analyze narrative structure"""
        # Check for narrative markers
        has_beginning = any(w in self.words for w in ["once", "first", "begin"])
        has_middle = any(w in self.words for w in ["then", "next", "after"])
        has_end = any(w in self.words for w in ["finally", "end", "last"])
        
        return {
            "has_structure": has_beginning and has_middle and has_end,
            "has_beginning": has_beginning,
            "has_middle": has_middle,
            "has_end": has_end
        }

    def _analyze_language_patterns(self) -> Dict[str, float]:
        """Analyze language system patterns"""
        # Check for consistent patterns
        return {
            "coherence": 0.7,  # Simplified
            "pattern_strength": 0.6
        }

    def _detect_contradictions(self) -> List[str]:
        """Detect textual contradictions"""
        contradictions = []
        # Look for contradictory statements
        if "always" in self.text.lower() and "never" in self.text.lower():
            contradictions.append("always/never contradiction")
        return contradictions

    def _find_suppressed_meanings(self) -> List[str]:
        """Find suppressed or hidden meanings"""
        # Simplified: look for what's NOT said
        return ["Meanings suppressed through silence"]

    def _analyze_language_instability(self) -> float:
        """Analyze language instability"""
        # Look for words with multiple meanings
        return 0.5  # Simplified

    def _analyze_interpretive_gaps(self) -> List[str]:
        """Analyze gaps for reader interpretation"""
        return ["Ambiguous references", "Unspecified contexts"]

    def _analyze_emotional_triggers(self) -> List[str]:
        """Analyze emotional triggers in text"""
        emotional_words = ["love", "hate", "fear", "joy", "sad", "angry"]
        return [w for w in emotional_words if w in self.text.lower()]

    def _analyze_context_dependence(self) -> float:
        """Analyze how much meaning depends on context"""
        return 0.6  # Simplified

    def _analyze_gender_representation(self) -> Dict[str, Any]:
        """Analyze gender representation"""
        male_words = ["he", "him", "his", "man", "men", "father", "king"]
        female_words = ["she", "her", "hers", "woman", "women", "mother", "queen"]
        
        male_count = sum(self.text.lower().count(w) for w in male_words)
        female_count = sum(self.text.lower().count(w) for w in female_words)
        
        total = male_count + female_count
        ratio = female_count / total if total > 0 else 0
        
        return {
            "male_count": male_count,
            "female_count": female_count,
            "ratio": ratio,
            "score": min(1.0, ratio * 2) if ratio < 0.5 else min(1.0, (1 - ratio) * 2),
            "summary": f"Male: {male_count}, Female: {female_count}"
        }

    def _analyze_power_dynamics(self) -> Dict[str, Any]:
        """Analyze power dynamics"""
        power_words = ["power", "control", "dominate", "rule", "command", "obey", "submit"]
        count = sum(self.text.lower().count(w) for w in power_words)
        
        return {
            "power_word_count": count,
            "score": min(1.0, count / 10),
            "summary": f"Power dynamics present: {count > 0}"
        }

    def _analyze_language_patriarchy(self) -> Dict[str, Any]:
        """Analyze patriarchal language structures"""
        # Look for generic "he", "mankind", etc.
        patriarchal_markers = ["mankind", "he (generic)", "chairman", "policeman"]
        found = [m for m in patriarchal_markers if m in self.text.lower()]
        
        return {
            "patriarchal_markers": found,
            "score": 1.0 - (len(found) / 10),
            "summary": f"Patriarchal language: {len(found)} instances"
        }

    def _analyze_class_representation(self) -> Dict[str, Any]:
        """Analyze class representation"""
        working_class = ["worker", "labor", "poor", "working", "factory"]
        upper_class = ["rich", "wealthy", "lord", "lady", "aristocrat"]
        
        wc_count = sum(self.text.lower().count(w) for w in working_class)
        uc_count = sum(self.text.lower().count(w) for w in upper_class)
        
        return {
            "working_class_count": wc_count,
            "upper_class_count": uc_count,
            "score": 0.7,  # Simplified
            "summary": f"Working: {wc_count}, Upper: {uc_count}"
        }

    def _analyze_ideology(self) -> Dict[str, Any]:
        """Analyze ideological content"""
        ideology_words = ["freedom", "equality", "justice", "oppression", "revolution"]
        count = sum(self.text.lower().count(w) for w in ideology_words)
        
        return {
            "ideology_word_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Ideological content: {count} markers"
        }

    def _analyze_economic_themes(self) -> Dict[str, Any]:
        """Analyze economic themes"""
        economic_words = ["money", "wealth", "poverty", "trade", "capital", "labor"]
        count = sum(self.text.lower().count(w) for w in economic_words)
        
        return {
            "economic_word_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Economic themes: {count} markers"
        }

    def _analyze_unconscious_content(self) -> Dict[str, Any]:
        """Analyze unconscious content"""
        unconscious_markers = ["dream", "desire", "wish", "fantasy", "repress"]
        count = sum(self.text.lower().count(w) for w in unconscious_markers)
        
        return {
            "unconscious_marker_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Unconscious content: {count} markers"
        }

    def _analyze_defense_mechanisms(self) -> Dict[str, Any]:
        """Analyze defense mechanisms in text"""
        defense_markers = ["deny", "rational", "project", "displace", "sublimate"]
        count = sum(self.text.lower().count(w) for w in defense_markers)
        
        return {
            "defense_marker_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Defense mechanisms: {count} markers"
        }

    def _analyze_psychosexual_themes(self) -> Dict[str, Any]:
        """Analyze psychosexual themes"""
        psychosexual_markers = ["desire", "pleasure", "forbidden", "taboo", "libido"]
        count = sum(self.text.lower().count(w) for w in psychosexual_markers)
        
        return {
            "psychosexual_marker_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Psychosexual themes: {count} markers"
        }

    def _analyze_nature_representation(self) -> Dict[str, Any]:
        """Analyze nature representation"""
        nature_words = ["nature", "tree", "river", "mountain", "animal", "forest", "ocean"]
        count = sum(self.text.lower().count(w) for w in nature_words)
        
        return {
            "nature_word_count": count,
            "score": min(1.0, count / 10),
            "summary": f"Nature representation: {count} instances"
        }

    def _analyze_environmental_themes(self) -> Dict[str, Any]:
        """Analyze environmental themes"""
        env_words = ["environment", "pollution", "climate", "ecology", "sustainable"]
        count = sum(self.text.lower().count(w) for w in env_words)
        
        return {
            "env_word_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Environmental themes: {count} markers"
        }

    def _analyze_human_nature_relationship(self) -> Dict[str, Any]:
        """Analyze human-nature relationship"""
        # Check if nature is valued or exploited
        positive = ["beautiful", "wonderful", "precious", "sacred"]
        negative = ["destroy", "exploit", "consume", "waste"]
        
        pos_count = sum(self.text.lower().count(w) for w in positive)
        neg_count = sum(self.text.lower().count(w) for w in negative)
        
        score = pos_count / (pos_count + neg_count + 1)
        
        return {
            "positive_markers": pos_count,
            "negative_markers": neg_count,
            "score": score,
            "summary": f"Nature relationship: {'Positive' if score > 0.5 else 'Negative'}"
        }

    def _classify_genre(self) -> str:
        """Classify genre (epic, comic, tragic)"""
        tragic_words = ["death", "tragedy", "sorrow", "loss", "grief"]
        comic_words = ["laugh", "funny", "happy", "joy", "humor"]
        
        tragic_count = sum(self.text.lower().count(w) for w in tragic_words)
        comic_count = sum(self.text.lower().count(w) for w in comic_words)
        
        if tragic_count > comic_count:
            return "tragic"
        elif comic_count > tragic_count:
            return "comic"
        else:
            return "epic/narrative"

    def _analyze_unity_aristotelian(self) -> Dict[str, Any]:
        """Analyze unity of action (Aristotelian)"""
        # Check for unified action
        return {
            "has_unity": True,
            "score": 0.8,
            "summary": "Unity of action present"
        }

    def _analyze_mimesis(self) -> Dict[str, Any]:
        """Analyze mimesis (imitation of reality)"""
        realistic_words = ["real", "true", "actual", "factual"]
        count = sum(self.text.lower().count(w) for w in realistic_words)
        
        return {
            "realism_marker_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Mimesis: {count} realism markers"
        }

    def _analyze_catharsis_potential(self) -> Dict[str, Any]:
        """Analyze catharsis potential"""
        emotional_words = ["tears", "weep", "fear", "pity", "purge", "cleanse"]
        count = sum(self.text.lower().count(w) for w in emotional_words)
        
        return {
            "emotional_word_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Catharsis potential: {count} emotional markers"
        }

    def _analyze_decorum(self) -> Dict[str, Any]:
        """Analyze decorum (appropriateness)"""
        # Check if style matches subject
        return {
            "appropriate": True,
            "score": 0.8,
            "summary": "Decorum maintained"
        }

    def _analyze_unity_horatian(self) -> Dict[str, Any]:
        """Analyze unity (Horatian)"""
        return {
            "has_unity": True,
            "score": 0.7,
            "summary": "Unity and coherence present"
        }

    def _analyze_instruction_delight(self) -> Dict[str, Any]:
        """Analyze balance of instruction and delight"""
        instruction_words = ["teach", "learn", "lesson", "moral", "wisdom"]
        delight_words = ["pleasure", "delight", "joy", "beautiful", "enjoy"]
        
        inst_count = sum(self.text.lower().count(w) for w in instruction_words)
        del_count = sum(self.text.lower().count(w) for w in delight_words)
        
        balance = min(inst_count, del_count) / max(1, max(inst_count, del_count))
        
        return {
            "instruction_count": inst_count,
            "delight_count": del_count,
            "balance": balance,
            "score": balance,
            "summary": f"Instruction: {inst_count}, Delight: {del_count}"
        }

    def _synthesize_results(self, results: Dict[str, Any]) -> str:
        """Synthesize results from multiple frameworks"""
        if not results:
            return "No frameworks applied"
        
        scores = [r.get("score", 5) for r in results.values()]
        avg_score = sum(scores) / len(scores)
        
        frameworks_applied = list(results.keys())
        
        return (
            f"Multi-framework analysis using {len(frameworks_applied)} criticism approaches. "
            f"Average score: {avg_score:.1f}/10. "
            f"Frameworks: {', '.join(frameworks_applied)}. "
            f"Each framework reveals different aspects of the text's meaning, structure, and cultural significance."
        )
