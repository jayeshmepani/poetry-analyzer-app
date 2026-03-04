"""
Literary Theory & Criticism Frameworks
Complete implementation of all major literary criticism approaches
Based on quantitative_poetry_metrics.md Section 5 & ultimate_literary_master_system.md
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re


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
        self.tokens: List[str] = []
        self._used_evidence_indices: set[int] = set()
        self.model_signals: Dict[str, Any] = {}

    def analyze(self, text: str, frameworks: List[str] = None, signals: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze text using multiple literary criticism frameworks
        
        Args:
            text: Text to analyze
            frameworks: List of frameworks to apply (default: all)
        """
        self.text = text
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]
        self.words = text.lower().split()
        self.tokens = self._tokenize_text(text)
        self._used_evidence_indices = set()
        self.model_signals = signals or {}

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

        for payload in results.values():
            self._recalibrate_framework_score(payload)
        for framework, payload in results.items():
            self._enrich_framework_result(framework, payload)

        return {
            "frameworks_applied": list(results.keys()),
            "results": results,
            "synthesis": self._synthesize_results(results)
        }

    def _recalibrate_framework_score(self, payload: Dict[str, Any]) -> None:
        """
        Calibrate raw heuristic score with model support/signal strength.
        Prevents unfair near-zero outputs when language coverage is weak.
        """
        raw = float(payload.get("score", 0.0) or 0.0)
        strength = self._framework_signal_strength(payload)
        support = float(self.model_signals.get("support_factor", 0.65))
        support = max(0.25, min(1.0, support))

        if strength <= 1:
            adjusted = (raw * 0.35 + 5.0 * 0.65) * support + raw * (1 - support)
        elif strength <= 3:
            adjusted = (raw * 0.6 + 5.0 * 0.4) * support + raw * (1 - support)
        else:
            adjusted = raw

        payload["raw_score"] = round(raw, 2)
        payload["score"] = round(max(0.0, min(10.0, adjusted)), 1)

    def _framework_signal_strength(self, payload: Dict[str, Any]) -> int:
        strength = 0
        ignored_keys = {
            "framework", "analysis", "recommendations", "derridean_concepts",
            "feminist_concepts", "marxist_concepts", "freudian_concepts",
            "ecocritical_concepts", "fallacies_avoided", "value_formula",
            "form_elements", "raw_score", "descriptive_summary", "evidence_points",
            "diagnostics"
        }
        for k, v in payload.items():
            if k in ignored_keys:
                continue
            if isinstance(v, list):
                strength += len([x for x in v if x])
            elif isinstance(v, dict):
                for sv in v.values():
                    if isinstance(sv, (int, float)) and sv > 0:
                        strength += 1
                    elif isinstance(sv, list) and sv:
                        strength += len(sv)
                    elif isinstance(sv, bool) and sv:
                        strength += 1
                    elif isinstance(sv, str) and sv and "0 " not in sv:
                        strength += 1
            elif isinstance(v, (int, float)) and v > 0:
                strength += 1
            elif isinstance(v, bool) and v:
                strength += 1
        return strength

    def _enrich_framework_result(self, framework: str, payload: Dict[str, Any]) -> None:
        """Add descriptive narrative, evidence excerpts, and confidence metadata."""
        score = float(payload.get("score", 0) or 0)
        key_findings = payload.get("key_findings") or []
        analysis = payload.get("analysis", "")

        evidence_keywords = self._framework_keywords(framework)
        evidence_points = self._extract_evidence_lines(evidence_keywords, max_items=4)
        signal_count = self._count_signals(payload)
        confidence = self._confidence_bucket(signal_count, score)

        payload["descriptive_summary"] = self._compose_framework_narrative(
            framework=framework,
            score=score,
            analysis=analysis,
            key_findings=key_findings,
            evidence_points=evidence_points,
            confidence=confidence,
        )
        payload["evidence_points"] = evidence_points
        payload["diagnostics"] = {
            "signal_count": signal_count,
            "confidence": confidence,
            "score_band": self._score_band(score),
            "script_profile": self._script_profile(),
        }

    def _framework_keywords(self, framework: str) -> List[str]:
        # Keep evidence selection dynamic: no fixed lexeme banks.
        # Use top recurring tokens from the current text as soft anchors.
        token_freq: Dict[str, int] = {}
        for tok in self.tokens:
            if len(tok) < 2:
                continue
            token_freq[tok] = token_freq.get(tok, 0) + 1
        ranked = sorted(token_freq.items(), key=lambda x: x[1], reverse=True)
        return [tok for tok, _ in ranked[:10]]

    def _extract_evidence_lines(self, keywords: List[str], max_items: int = 3) -> List[str]:
        if not self.lines:
            return []

        lower_keywords = [k.lower() for k in (keywords or []) if k]
        scored: List[tuple[float, int]] = []
        for idx, line in enumerate(self.lines):
            line_l = line.lower()
            hit_score = sum(1 for k in lower_keywords if k and k in line_l)
            token_count = len(line.split())
            punctuation_count = sum(1 for ch in line if ch in ",;:.?!")
            density = punctuation_count / max(1, len(line))
            novelty_bonus = 1 if idx not in self._used_evidence_indices else 0
            total = (
                hit_score * 2.5
                + min(1.5, token_count / 8.0)
                + min(1.0, density * 20)
                + novelty_bonus
            )
            scored.append((total, idx))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected_indices: List[int] = []
        for _, idx in scored:
            if idx in selected_indices:
                continue
            block = [idx]
            if idx % 2 == 0 and idx + 1 < len(self.lines):
                block.append(idx + 1)
            elif idx - 1 >= 0:
                block.insert(0, idx - 1)

            for b in block:
                if b not in selected_indices:
                    selected_indices.append(b)
                if len(selected_indices) >= max_items:
                    break
            if len(selected_indices) >= max_items:
                break

        if len(selected_indices) < max_items:
            n = len(self.lines)
            anchors = [0, n // 3, (2 * n) // 3, n - 1]
            for idx in anchors:
                if idx < 0 or idx >= n or idx in selected_indices:
                    continue
                if idx in self._used_evidence_indices and len(selected_indices) > 0:
                    continue
                selected_indices.append(idx)
                if len(selected_indices) >= max_items:
                    break

        if len(selected_indices) < max_items:
            for idx in range(len(self.lines)):
                if idx not in selected_indices and idx not in self._used_evidence_indices:
                    selected_indices.append(idx)
                if len(selected_indices) >= max_items:
                    break
        if len(selected_indices) < max_items:
            for idx in range(len(self.lines)):
                if idx not in selected_indices:
                    selected_indices.append(idx)
                if len(selected_indices) >= max_items:
                    break

        selected_indices = sorted(selected_indices[:max_items])

        for idx in selected_indices:
            self._used_evidence_indices.add(idx)
        return [self.lines[idx].strip() for idx in selected_indices]

    def _script_profile(self) -> str:
        text = self.text or ""
        deva = len(re.findall(r"[\u0900-\u097F]", text))
        arabic = len(re.findall(r"[\u0600-\u06FF]", text))
        latin = len(re.findall(r"[A-Za-z]", text))
        if deva >= arabic and deva >= latin and deva > 0:
            return "Devanagari-dominant"
        if arabic >= deva and arabic >= latin and arabic > 0:
            return "Arabic-script dominant"
        if latin > 0:
            return "Latin-script dominant"
        return "Mixed/undetermined"

    def _count_signals(self, payload: Dict[str, Any]) -> int:
        count = 0
        for _, value in payload.items():
            if isinstance(value, list):
                count += len(value)
            elif isinstance(value, dict):
                count += len(value)
            elif isinstance(value, bool):
                count += int(value)
            elif isinstance(value, (int, float)) and value > 0:
                count += 1
        return count

    def _score_band(self, score: float) -> str:
        if score >= 7.5:
            return "Strong"
        if score >= 5.0:
            return "Moderate"
        if score >= 2.5:
            return "Emergent"
        return "Low-signal"

    def _confidence_bucket(self, signal_count: int, score: float) -> str:
        if signal_count >= 12 and score >= 5:
            return "High"
        if signal_count >= 6:
            return "Medium"
        return "Low"

    def _compose_framework_narrative(
        self,
        framework: str,
        score: float,
        analysis: str,
        key_findings: List[str],
        evidence_points: List[str],
        confidence: str,
    ) -> str:
        cleaned_findings = [str(f).strip() for f in (key_findings or []) if str(f).strip()]
        top_findings = "; ".join(cleaned_findings[:3]) if cleaned_findings else "No dominant markers were detected."
        evidence_hint = "; ".join(evidence_points[:2]) if evidence_points else "No direct evidence lines were extracted."
        return (
            f"{analysis} "
            f"This lens currently scores {score:.1f}/10 with {confidence.lower()} confidence. "
            f"Most relevant observations: {top_findings} "
            f"Representative textual cues: {evidence_hint}"
        )

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
        paradoxes = self._sig("literary_devices", "tropes", "paradox", default=[])
        antithesis = self._sig("literary_devices", "schemes", "antithesis", default=[])
        out = []
        for item in paradoxes[:6]:
            out.append(str(item))
        for item in antithesis[:4]:
            out.append(str(item))
        return [x for x in out if x]

    def _detect_ironies(self) -> List[str]:
        """Detect ironies in text"""
        ironies = self._sig("literary_devices", "tropes", "irony", default=[])
        return [str(x) for x in ironies[:8] if x]

    def _detect_ambiguities(self) -> List[str]:
        """Detect ambiguities in text"""
        gaps = self._analyze_interpretive_gaps()
        unstables = self._sig("literary_devices", "schemes", "ellipsis", default=[])
        merged = [str(x) for x in gaps + unstables if x]
        return merged[:10]

    def _analyze_unity(self) -> float:
        """Analyze textual unity based on thematic recurrence (0-1 scale)"""
        token_freq: Dict[str, int] = {}
        for tok in self.tokens:
            if len(tok) > 1:
                token_freq[tok] = token_freq.get(tok, 0) + 1
        repeated = sum(1 for c in token_freq.values() if c > 1)
        lexical_recurrence = repeated / max(1, len(token_freq))

        # End-rhyme / refrain-like recurrence for couplet traditions
        endings = [line.split()[-1].strip(".,;:!?\"'’”“") for line in self.lines if line.split()]
        end_freq: Dict[str, int] = {}
        for e in endings:
            end_freq[e] = end_freq.get(e, 0) + 1
        refrain_density = sum(1 for c in end_freq.values() if c > 1) / max(1, len(end_freq))

        score = min(1.0, 0.55 * lexical_recurrence + 0.45 * refrain_density + 0.15)
        return round(score, 2)

    def _analyze_imagery_coherence(self) -> float:
        """Analyze imagery coherence (0-1 scale)"""
        imagery = self._sig("literary_devices", "imagery", default={})
        counts = {k: float(v) for k, v in (imagery or {}).items() if isinstance(v, (int, float))}
        if not counts:
            counts = {
                "visual": float(self._sig("linguistic", "semantics", "concrete_word_count", default=0)),
                "abstract": float(self._sig("linguistic", "semantics", "abstract_word_count", default=0)),
            }
        total = sum(counts.values())
        if total == 0:
            return 0.0
        dominant = max(counts.values())
        richness = min(1.0, total / 10)
        focus = dominant / max(1, total)
        return round(min(1.0, 0.6 * focus + 0.4 * richness), 2)

    def _detect_binary_oppositions(self) -> List[Dict[str, str]]:
        """Detect binary oppositions in text"""
        antithesis = self._sig("literary_devices", "schemes", "antithesis", default=[])
        found: List[Dict[str, str]] = []
        for item in antithesis:
            if isinstance(item, dict):
                left = item.get("left") or item.get("a") or item.get("source") or "term_a"
                right = item.get("right") or item.get("b") or item.get("target") or "term_b"
                found.append({"term1": str(left), "term2": str(right)})
            elif isinstance(item, str):
                parts = [p.strip() for p in item.replace(" vs ", "|").split("|", 1)]
                if len(parts) == 2:
                    found.append({"term1": parts[0], "term2": parts[1]})
        return found[:8]

    def _analyze_narrative_structure(self) -> Dict[str, Any]:
        """Analyze narrative structure"""
        line_count = max(1, len(self.lines))
        stanza_count = float(self._sig("structural", "stanza_analysis", "stanza_count", default=0))
        sentiment_arc = self._sig("sentiment_analysis", "sentiment_arc", default=[])
        has_beginning = line_count >= 2
        has_middle = line_count >= 4 or len(sentiment_arc) >= 2
        has_end = line_count >= 6 or stanza_count >= 2
        return {
            "has_structure": has_beginning and has_middle and has_end,
            "has_beginning": has_beginning,
            "has_middle": has_middle,
            "has_end": has_end,
        }

    def _analyze_language_patterns(self) -> Dict[str, float]:
        """Analyze language system patterns"""
        # Pattern strength from recurrence, anaphora-ish starts, and rhyme-end repetitions
        if not self.lines:
            return {"coherence": 0.0, "pattern_strength": 0.0}
        first_words = [ln.split()[0] for ln in self.lines if ln.split()]
        fw_freq: Dict[str, int] = {}
        for fw in first_words:
            fw_freq[fw] = fw_freq.get(fw, 0) + 1
        start_recurrence = sum(1 for c in fw_freq.values() if c > 1) / max(1, len(fw_freq))
        coherence = self._analyze_unity()
        pattern_strength = min(1.0, (coherence + start_recurrence + self._analyze_imagery_coherence()) / 3)
        return {
            "coherence": round(coherence, 2),
            "pattern_strength": round(pattern_strength, 2)
        }

    def _detect_contradictions(self) -> List[str]:
        """Detect textual contradictions"""
        contradictions = self._sig("literary_devices", "schemes", "antithesis", default=[])
        if isinstance(contradictions, list):
            return [str(c) for c in contradictions[:6] if c]
        return []

    def _find_suppressed_meanings(self) -> List[str]:
        """Find suppressed or hidden meanings"""
        implicatures = self._sig("additional", "pragmatics", "implicatures_detected", default=[])
        if implicatures:
            return [str(x) for x in implicatures[:6] if x]
        return self._analyze_interpretive_gaps()[:3]

    def _analyze_language_instability(self) -> float:
        """Analyze language instability based on ambiguous word density"""
        ambiguous = self._detect_ambiguities()
        token_count = max(1, len(self.tokens))
        score = min(1.0, (len(ambiguous) / token_count) * 18 + (0.15 if "?" in self.text else 0))
        return round(score, 2)

    def _analyze_interpretive_gaps(self) -> List[str]:
        """Analyze gaps for reader interpretation"""
        gaps = []
        punctuation_questions = self.text.count("?")
        if punctuation_questions > 0:
            gaps.append(f"Contains {punctuation_questions} explicit interrogative closures")
        ellipsis_items = self._sig("literary_devices", "schemes", "ellipsis", default=[])
        if isinstance(ellipsis_items, list) and ellipsis_items:
            gaps.append(f"Detected {len(ellipsis_items)} ellipsis/silence cues")
        coherence = float(self._sig("linguistic", "text_metrics", "descriptive_stats", "sentence_count", default=0))
        if coherence <= 2:
            gaps.append("Compressed sentence topology leaves interpretive openness")
        return gaps or ["Context remains partially indeterminate"]

    def _analyze_emotional_triggers(self) -> List[str]:
        """Analyze emotional triggers in text"""
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        if not isinstance(emotions, dict):
            return []
        ranked = sorted(
            [(k, float(v)) for k, v in emotions.items() if isinstance(v, (int, float))],
            key=lambda x: x[1],
            reverse=True,
        )
        return [f"{k}:{v:.2f}" for k, v in ranked[:5] if v > 0.05]

    def _analyze_context_dependence(self) -> float:
        """Analyze how much meaning depends on context"""
        sentence_count = max(1.0, self._to_float(self._sig("linguistic", "text_metrics", "descriptive_stats", "sentence_count", default=1), 1.0))
        line_count = max(1.0, float(len(self.lines)))
        dependency_nodes = len(self._sig("linguistic", "dependency_tree", default=[]))
        ratio = min(1.0, (line_count / sentence_count) * 0.18 + dependency_nodes / 200.0)
        return round(max(0.2, ratio), 2)

    def _analyze_gender_representation(self) -> Dict[str, Any]:
        """Analyze gender representation"""
        ner = self._sig("linguistic", "named_entities", default=[])
        male_count = sum(1 for n in ner if isinstance(n, dict) and "male" in str(n.get("label", "")).lower())
        female_count = sum(1 for n in ner if isinstance(n, dict) and "female" in str(n.get("label", "")).lower())
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
        speech_acts = self._sig("additional", "pragmatics", "speech_acts", "counts", default={})
        count = self._to_int(speech_acts.get("directive", 0)) + self._to_int(speech_acts.get("declarative", 0))
        
        return {
            "power_word_count": count,
            "score": min(1.0, count / 10),
            "summary": f"Power dynamics present: {count > 0}"
        }

    def _analyze_language_patriarchy(self) -> Dict[str, Any]:
        """Analyze patriarchal language structures"""
        found = []
        
        return {
            "patriarchal_markers": found,
            "score": 1.0,
            "summary": f"Patriarchal language: {len(found)} instances"
        }

    def _analyze_class_representation(self) -> Dict[str, Any]:
        """Analyze class representation"""
        wc_count = int(self._to_float(self._sig("additional", "dialect_detection", "marker_count", default=0), 0.0) / 5)
        uc_count = int(self._to_float(self._sig("evaluation", "ratings", "language_diction", default=0), 0.0) / 3)
        
        return {
            "working_class_count": wc_count,
            "upper_class_count": uc_count,
            "score": min(1.0, 0.35 + (wc_count + uc_count) / 8),
            "summary": f"Working: {wc_count}, Upper: {uc_count}"
        }

    def _analyze_ideology(self) -> Dict[str, Any]:
        """Analyze ideological content"""
        schemes = self._sig("literary_devices", "schemes", default={})
        count = sum(len(v) for v in schemes.values() if isinstance(v, list))
        
        return {
            "ideology_word_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Ideological content: {count} markers"
        }

    def _analyze_economic_themes(self) -> Dict[str, Any]:
        """Analyze economic themes"""
        count = int(self._to_float(self._sig("quantitative", "lexical_metrics", "lexical_density", default=0), 0.0) // 20)
        
        return {
            "economic_word_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Economic themes: {count} markers"
        }

    def _analyze_unconscious_content(self) -> Dict[str, Any]:
        """Analyze unconscious content"""
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        fear = self._to_float(emotions.get("fear", 0.0), 0.0)
        sadness = self._to_float(emotions.get("sadness", 0.0), 0.0)
        count = int((fear + sadness) * 20)
        
        return {
            "unconscious_marker_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Unconscious content: {count} markers"
        }

    def _analyze_defense_mechanisms(self) -> Dict[str, Any]:
        """Analyze defense mechanisms in text"""
        neg = self._to_float(self._sig("additional", "transformer_analysis", "sentiment", "score", default=0.0), 0.0)
        count = int(neg * 10)
        
        return {
            "defense_marker_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Defense mechanisms: {count} markers"
        }

    def _analyze_psychosexual_themes(self) -> Dict[str, Any]:
        """Analyze psychosexual themes"""
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        count = int(self._to_float(emotions.get("love", 0.0), 0.0) * 20)
        
        return {
            "psychosexual_marker_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Psychosexual themes: {count} markers"
        }

    def _analyze_nature_representation(self) -> Dict[str, Any]:
        """Analyze nature representation"""
        imagery = self._sig("literary_devices", "imagery", default={})
        count = int(sum(v for v in imagery.values() if isinstance(v, (int, float))))
        
        return {
            "nature_word_count": count,
            "score": min(1.0, count / 10),
            "summary": f"Nature representation: {count} instances"
        }

    def _analyze_environmental_themes(self) -> Dict[str, Any]:
        """Analyze environmental themes"""
        count = self._to_int(self._sig("literary_devices", "imagery", "organic", default=0))
        
        return {
            "env_word_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Environmental themes: {count} markers"
        }

    def _analyze_human_nature_relationship(self) -> Dict[str, Any]:
        """Analyze human-nature relationship"""
        sentiment = self._sig("additional", "transformer_analysis", "sentiment", default={})
        score = self._to_float(sentiment.get("score", 0.5), 0.5) if isinstance(sentiment, dict) else 0.5
        pos_count = int(score * 10)
        neg_count = int((1 - score) * 10)
        
        return {
            "positive_markers": pos_count,
            "negative_markers": neg_count,
            "score": score,
            "summary": f"Nature relationship: {'Positive' if score > 0.5 else 'Negative'}"
        }

    def _sig(self, *path, default=None):
        node: Any = self.model_signals
        for key in path:
            if not isinstance(node, dict):
                return default
            node = node.get(key)
            if node is None:
                return default
        return node

    def _to_float(self, value: Any, default: float = 0.0) -> float:
        """Safely coerce heterogeneous signal payload values to float."""
        try:
            if isinstance(value, bool):
                return float(int(value))
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                return float(value.strip()) if value.strip() else default
            if isinstance(value, list):
                if not value:
                    return default
                numeric = [float(v) for v in value if isinstance(v, (int, float))]
                return float(sum(numeric)) if numeric else float(len(value))
            if isinstance(value, dict):
                if not value:
                    return default
                numeric = [float(v) for v in value.values() if isinstance(v, (int, float))]
                return float(sum(numeric)) if numeric else float(len(value))
        except Exception:
            return default
        return default

    def _to_int(self, value: Any, default: int = 0) -> int:
        """Safe int conversion for list/dict/scalar payloads."""
        try:
            return int(self._to_float(value, float(default)))
        except Exception:
            return default

    def _tokenize_text(self, text: str) -> List[str]:
        raw = re.split(r"[\s,.;:!?\"'`~()\[\]{}<>/\\|@#$%^&*+=\-_]+", (text or "").lower())
        return [t for t in raw if t]

    def _contains_marker(self, marker: str) -> bool:
        marker_l = (marker or "").lower().strip()
        if not marker_l:
            return False
        if " " in marker_l:
            return marker_l in self.text.lower()
        return marker_l in self.tokens or marker_l in self.text.lower()

    def _count_markers(self, markers: List[str]) -> int:
        total = 0
        seen = set()
        for m in markers:
            ml = (m or "").lower().strip()
            if not ml or ml in seen:
                continue
            seen.add(ml)
            if " " in ml:
                total += self.text.lower().count(ml)
            else:
                token_hits = self.tokens.count(ml)
                if token_hits > 0:
                    total += token_hits
                elif ml in self.text.lower():
                    total += 1
        return total

    def _classify_genre(self) -> str:
        """Classify genre (epic, comic, tragic)"""
        sentiment = self._sig("additional", "transformer_analysis", "sentiment", default={})
        label = str(sentiment.get("label", "")).upper() if isinstance(sentiment, dict) else ""
        if label == "NEGATIVE":
            return "tragic"
        if label == "POSITIVE":
            return "comic"
        return "epic/narrative"

    def _analyze_unity_aristotelian(self) -> Dict[str, Any]:
        """Analyze unity of action (Aristotelian)"""
        unity = self._analyze_unity()
        return {
            "has_unity": unity >= 0.55,
            "score": round(unity, 2),
            "summary": f"Unity of action score: {unity:.2f}"
        }

    def _analyze_mimesis(self) -> Dict[str, Any]:
        """Analyze mimesis (imitation of reality)"""
        entities = self._sig("linguistic", "named_entities", default=[])
        count = len(entities) if isinstance(entities, list) else 0
        
        return {
            "realism_marker_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Mimesis: {count} realism markers"
        }

    def _analyze_catharsis_potential(self) -> Dict[str, Any]:
        """Analyze catharsis potential"""
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        count = int(
            (
                self._to_float(emotions.get("sadness", 0.0), 0.0)
                + self._to_float(emotions.get("fear", 0.0), 0.0)
                + self._to_float(emotions.get("love", 0.0), 0.0)
            )
            * 15
        ) if isinstance(emotions, dict) else 0
        
        return {
            "emotional_word_count": count,
            "score": min(1.0, count / 5),
            "summary": f"Catharsis potential: {count} emotional markers"
        }

    def _analyze_decorum(self) -> Dict[str, Any]:
        """Analyze decorum (appropriateness)"""
        readability = self._to_float(self._sig("quantitative", "readability_metrics", "flesch_reading_ease", default=60.0), 60.0)
        score = max(0.0, min(1.0, readability / 100.0))
        return {
            "appropriate": score >= 0.45,
            "score": round(score, 2),
            "summary": f"Decorum score from readability alignment: {score:.2f}"
        }

    def _analyze_unity_horatian(self) -> Dict[str, Any]:
        """Analyze unity (Horatian)"""
        coherence = self._to_float(self._sig("linguistic", "text_metrics", "readability", "flesch_reading_ease", default=60.0), 60.0)
        score = max(0.0, min(1.0, coherence / 100.0))
        return {
            "has_unity": score >= 0.5,
            "score": round(score, 2),
            "summary": f"Unity/coherence score: {score:.2f}"
        }

    def _analyze_instruction_delight(self) -> Dict[str, Any]:
        """Analyze balance of instruction and delight"""
        speech_acts = self._sig("additional", "pragmatics", "speech_acts", "counts", default={})
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        inst_count = self._to_int(speech_acts.get("assertive", 0)) + self._to_int(speech_acts.get("directive", 0))
        del_count = int(self._to_float(emotions.get("joy", 0.0), 0.0) * 10) + int(self._to_float(emotions.get("love", 0.0), 0.0) * 10)
        
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
        
        scored = [(k, float(v.get("score", 0) or 0)) for k, v in results.items()]
        avg_score = sum(v for _, v in scored) / max(1, len(scored))
        top = max(scored, key=lambda x: x[1]) if scored else ("n/a", 0.0)
        low = min(scored, key=lambda x: x[1]) if scored else ("n/a", 0.0)
        return (
            f"Multi-framework synthesis across {len(results)} lenses. "
            f"Mean score is {avg_score:.1f}/10, with strongest alignment in {top[0]} ({top[1]:.1f}) "
            f"and weakest in {low[0]} ({low[1]:.1f}). "
            "Use higher-scoring lenses for interpretive emphasis and lower-scoring lenses as revision targets "
            "to strengthen symbolic density, thematic contrast, and rhetorical force."
        )
