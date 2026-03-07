"""
Literary Theory & Criticism Frameworks
Complete implementation of all major literary criticism approaches
Based on quantitative_poetry_metrics.md Section 5 & ultimate_literary_master_system.md
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re

from app.services.rule_loader import get_literary_theory_rules
from app.config import Settings


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
        self._rules = get_literary_theory_rules()
        self._summary_rules = self._rules["summary"]
        self._settings = Settings()
        self._zero_shot = None

    def _ensure_zero_shot(self):
        """Lazily load and cache the zero-shot classification pipeline."""
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            from transformers import pipeline
            model_name = self._settings.transformer.generalist_zero_shot_model
            self._zero_shot = pipeline("zero-shot-classification", model=model_name, device=-1)
        except Exception:
            self._zero_shot = None
        return self._zero_shot

    def _zsc(self, labels: List[str]) -> Optional[Dict[str, Any]]:
        """Run zero-shot classification on self.text with the given label list.
        Returns sorted (label, score) pairs or None on failure."""
        zs = self._ensure_zero_shot()
        if zs is None:
            return None
        try:
            # ZSC models have a token limit; clip to 512 words to be safe
            clipped = " ".join(self.text.split()[:512])
            out = zs(clipped, labels, multi_label=True)
            return dict(zip(out["labels"], out["scores"]))
        except Exception:
            return None

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

        for framework, payload in results.items():
            self._enrich_framework_result(framework, payload)

        return {
            "frameworks_applied": list(results.keys()),
            "results": results,
            "synthesis": self._synthesize_results(results)
        }

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
        return [tok for tok, _ in ranked[: self._summary_rules["keyword_top_k"]]]

    def _extract_evidence_lines(self, keywords: List[str], max_items: int = 3) -> List[str]:
        if not self.lines:
            return []

        if max_items is None:
            max_items = self._summary_rules["evidence_max_items"]
        lower_keywords = [k.lower() for k in (keywords or []) if k]
        scored: List[tuple[float, int]] = []
        for idx, line in enumerate(self.lines):
            line_l = line.lower()
            hit_score = sum(1 for k in lower_keywords if k and k in line_l)
            token_count = len(line.split())
            punctuation_count = sum(1 for ch in line if ch in self._summary_rules["punctuation_chars"])
            density = punctuation_count / max(1, len(line))
            novelty_bonus = 1 if idx not in self._used_evidence_indices else 0
            total = (
                hit_score * self._summary_rules["hit_weight"]
                + min(self._summary_rules["token_count_cap"], token_count / self._summary_rules["token_count_scale"])
                + min(self._summary_rules["punctuation_cap"], density * self._summary_rules["punctuation_scale"])
                + novelty_bonus * self._summary_rules["novelty_bonus"]
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
        deva = len(re.findall(self._summary_rules["script_devanagari"], text))
        arabic = len(re.findall(self._summary_rules["script_arabic"], text))
        latin = len(re.findall(self._summary_rules["script_latin"], text))
        if deva >= arabic and deva >= latin and deva > 0:
            return self._summary_rules["script_labels"]["devanagari"]
        if arabic >= deva and arabic >= latin and arabic > 0:
            return self._summary_rules["script_labels"]["arabic"]
        if latin > 0:
            return self._summary_rules["script_labels"]["latin"]
        return self._summary_rules["script_labels"]["mixed"]

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
        if score >= self._summary_rules["score_band_strong"]:
            return "Strong"
        if score >= self._summary_rules["score_band_moderate"]:
            return "Moderate"
        if score >= self._summary_rules["score_band_emergent"]:
            return "Emergent"
        return "Low-signal"

    def _confidence_bucket(self, signal_count: int, score: float) -> str:
        if signal_count >= self._summary_rules["confidence_high_signal"] and score >= self._summary_rules["confidence_high_score"]:
            return "High"
        if signal_count >= self._summary_rules["confidence_medium_signal"]:
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
        top_findings = "; ".join(cleaned_findings[: self._summary_rules["summary_findings_top"]]) if cleaned_findings else self._summary_rules["findings_default"]
        evidence_hint = "; ".join(evidence_points[: self._summary_rules["summary_evidence_top"]]) if evidence_points else self._summary_rules["evidence_default"]
        return self._summary_rules["narrative_template"].format(
            analysis=analysis,
            score=score,
            confidence=confidence.lower(),
            findings=top_findings,
            evidence=evidence_hint,
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
        rules = self._rules["new_criticism"]
        weights = rules["score_weights"]
        score = (
            unity_score * weights["unity"] +
            imagery_coherence * weights["imagery"] +
            (len(paradoxes) > 0) * weights["paradox_presence"] +
            (len(ironies) > 0) * weights["irony_presence"]
        ) * weights["scale"]

        return {
            "framework": rules["framework"],
            "score": round(min(10, score), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["paradoxes"].format(count=len(paradoxes)),
                rules["key_findings"]["ironies"].format(count=len(ironies)),
                rules["key_findings"]["ambiguities"].format(count=len(ambiguities)),
                rules["key_findings"]["unity"].format(score=unity_score),
                rules["key_findings"]["imagery"].format(score=imagery_coherence),
            ],
            "recommendations": rules["recommendations"],
            "fallacies_avoided": rules["fallacies_avoided"],
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
            "framework": self._rules["formalism"]["framework"],
            "score": new_crit["score"],
            "analysis": self._rules["formalism"]["analysis"],
            "key_findings": new_crit["key_findings"],
            "form_elements": self._rules["formalism"]["form_elements"]
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

        rules = self._rules["structuralism"]
        weights = rules["score_weights"]
        score = (
            (len(binaries) > 0) * weights["binary_presence"] +
            (narrative_structure["has_structure"] * weights["structure_presence"]) +
            (language_patterns["coherence"] * weights["language_coherence"])
        ) * weights["scale"]

        return {
            "framework": rules["framework"],
            "score": round(min(10, score), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["binaries"].format(count=len(binaries)),
                rules["key_findings"]["narrative"].format(
                    state=rules["narrative_present"] if narrative_structure["has_structure"] else rules["narrative_absent"]
                ),
                rules["key_findings"]["coherence"].format(score=language_patterns["coherence"])
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

        rules = self._rules["deconstruction"]
        weights = rules["score_weights"]

        score = (
            (len(contradictions) > 0) * weights["contradictions"] +
            (len(suppressed) > 0) * weights["suppressed"] +
            instability * weights["instability"]
        ) * weights["scale"]

        return {
            "framework": rules["framework"],
            "score": round(min(10, score), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["contradictions"].format(count=len(contradictions)),
                rules["key_findings"]["suppressed"].format(count=len(suppressed)),
                rules["key_findings"]["instability"].format(score=instability),
            ],
            "contradictions": contradictions,
            "suppressed_meanings": suppressed,
            "language_instability": instability,
            "derridean_concepts": rules.get("derridean_concepts", [])
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
        intrinsic_affect = self._intrinsic_affective_markers()

        # Analyze context dependence
        context_dependence = self._analyze_context_dependence()

        rules = self._rules["reader_response"]
        weights = rules["score_weights"]
        blend = rules.get("engagement_blend", {})

        # Value formula: V = T × R × C (all derived from live signals)
        text_potential = self._text_quality_signal()
        # Blend explicit emotion triggers with intrinsic affective markers and interpretive openness.
        emotional_divisor = float(blend.get("emotional_divisor", 5.0))
        intrinsic_divisor = float(blend.get("intrinsic_divisor", 4.0))
        gap_divisor = float(blend.get("gap_divisor", 3.0))
        emotional_weight = float(blend.get("emotional_weight", 0.45))
        intrinsic_weight = float(blend.get("intrinsic_weight", 0.35))
        gap_weight = float(blend.get("gap_weight", 0.20))
        emotional_signal = min(1.0, len(emotional_triggers) / max(1.0, emotional_divisor))
        intrinsic_signal = min(1.0, len(intrinsic_affect) / max(1.0, intrinsic_divisor))
        gap_signal = min(1.0, len(gaps) / max(1.0, gap_divisor))
        reader_engagement = min(
            1.0,
            emotional_weight * emotional_signal
            + intrinsic_weight * intrinsic_signal
            + gap_weight * gap_signal,
        )
        context_relevance = max(0.0, min(1.0, context_dependence))

        value = (
            text_potential * weights["text_potential_base"] *
            (weights["reader_engagement_base"] + weights["reader_engagement_mul"] * reader_engagement) *
            (weights["context_relevance_base"] + weights["context_relevance_mul"] * context_relevance)
        )

        return {
            "framework": rules["framework"],
            "value_formula": rules["value_formula"],
            "score": round(min(10, value * weights["scale"]), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["gaps"].format(count=len(gaps)),
                rules["key_findings"]["triggers"].format(count=len(emotional_triggers)),
                rules["key_findings"]["context"].format(score=context_dependence)
            ],
            "transaction_elements": {
                "text_potential": text_potential,
                "reader_engagement": reader_engagement,
                "context_relevance": context_relevance
            },
            "interpretive_gaps": gaps,
            "emotional_triggers": emotional_triggers,
            "intrinsic_affective_markers": intrinsic_affect,
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

        rules = self._rules["feminist"]
        weights = rules["score_weights"]

        score = (
            gender_analysis["score"] * weights["gender"] +
            power_dynamics["score"] * weights["power"] +
            language_analysis["score"] * weights["language"]
        ) * weights["scale"]

        return {
            "framework": rules["framework"],
            "score": round(min(10, score), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["gender"].format(summary=gender_analysis['summary']),
                rules["key_findings"]["power"].format(summary=power_dynamics['summary']),
                rules["key_findings"]["language"].format(summary=language_analysis['summary'])
            ],
            "gender_analysis": gender_analysis,
            "power_dynamics": power_dynamics,
            "language_critique": language_analysis,
            "feminist_concepts": rules.get("feminist_concepts", [])
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

        rules = self._rules["marxist"]
        weights = rules["score_weights"]

        score = (
            class_analysis["score"] * weights["class"] +
            ideology_analysis["score"] * weights["ideology"] +
            economic_themes["score"] * weights["economic"]
        ) * weights["scale"]

        return {
            "framework": rules["framework"],
            "score": round(min(10, score), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["class"].format(summary=class_analysis['summary']),
                rules["key_findings"]["ideology"].format(summary=ideology_analysis['summary']),
                rules["key_findings"]["economic"].format(summary=economic_themes['summary'])
            ],
            "class_analysis": class_analysis,
            "ideology_analysis": ideology_analysis,
            "economic_themes": economic_themes,
            "marxist_concepts": rules.get("marxist_concepts", [])
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

        rules = self._rules["psychoanalytic"]
        weights = rules["score_weights"]

        score = (
            unconscious["score"] * weights["unconscious"] +
            defense_mechanisms["score"] * weights["defense"] +
            psychosexual["score"] * weights["psychosexual"]
        ) * weights["scale"]

        return {
            "framework": rules["framework"],
            "score": round(min(10, score), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["unconscious"].format(summary=unconscious['summary']),
                rules["key_findings"]["defense"].format(summary=defense_mechanisms['summary']),
                rules["key_findings"]["psychosexual"].format(summary=psychosexual['summary'])
            ],
            "unconscious_analysis": unconscious,
            "defense_mechanisms": defense_mechanisms,
            "psychosexual_themes": psychosexual,
            "freudian_concepts": rules.get("freudian_concepts", [])
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

        rules = self._rules["ecocriticism"]
        weights = rules["score_weights"]

        score = (
            nature_analysis["score"] * weights["nature"] +
            environmental_themes["score"] * weights["environmental"] +
            human_nature["score"] * weights["human_nature"]
        ) * weights["scale"]

        return {
            "framework": rules["framework"],
            "score": round(min(10, score), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["nature"].format(summary=nature_analysis['summary']),
                rules["key_findings"]["environmental"].format(summary=environmental_themes['summary']),
                rules["key_findings"]["human_nature"].format(summary=human_nature['summary'])
            ],
            "nature_analysis": nature_analysis,
            "environmental_themes": environmental_themes,
            "human_nature_relationship": human_nature,
            "ecocritical_concepts": rules.get("ecocritical_concepts", [])
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

        rules = self._rules["aristotelian"]
        weights = rules["score_weights"]

        score = (
            unity["score"] * weights["unity"] +
            mimesis["score"] * weights["mimesis"] +
            catharsis["score"] * weights["catharsis"]
        ) * weights["scale"]

        return {
            "framework": rules["framework"],
            "score": round(min(10, score), 1),
            "analysis": rules["analysis"],
            "key_findings": [
                rules["key_findings"]["genre"].format(genre=genre),
                rules["key_findings"]["unity"].format(summary=unity['summary']),
                rules["key_findings"]["mimesis"].format(summary=mimesis['summary']),
                rules["key_findings"]["catharsis"].format(summary=catharsis['summary'])
            ],
            "genre_classification": genre,
            "unity_analysis": unity,
            "mimesis_analysis": mimesis,
            "catharsis_analysis": catharsis,
            "aristotelian_concepts": rules.get("aristotelian_concepts", [])
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

        h_weights = self._rules.get("horatian_weights", {})
        w_decorum = float(h_weights.get("decorum", 0.4))
        w_unity = float(h_weights.get("unity", 0.3))
        w_instruction = float(h_weights.get("instruction_delight", 0.3))
        score = (
            decorum["score"] * w_decorum +
            unity["score"] * w_unity +
            instruction_delight["score"] * w_instruction
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

        scales = self._rules.get("scales", {})
        lex_w = float(scales.get("unity_lexical_weight", 0.55))
        ref_w = float(scales.get("unity_refrain_weight", 0.45))
        score = min(1.0, lex_w * lexical_recurrence + ref_w * refrain_density)
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
        scales = self._rules.get("scales", {})
        richness_scale = float(scales.get("imagery_richness_scale", 10.0))
        focus_w = float(scales.get("imagery_focus_weight", 0.6))
        richness_w = float(scales.get("imagery_richness_weight", 0.4))
        richness = min(1.0, total / max(1.0, richness_scale))
        focus = dominant / max(1, total)
        return round(min(1.0, focus_w * focus + richness_w * richness), 2)

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
            emotions = {}
        ranked = sorted(
            [(k, float(v)) for k, v in emotions.items() if isinstance(v, (int, float))],
            key=lambda x: x[1],
            reverse=True,
        )
        detected = [f"{k}:{v:.2f}" for k, v in ranked[:5] if v > 0.05]
        for marker in self._intrinsic_affective_markers():
            if marker not in detected:
                detected.append(marker)
        return detected[:6]

    def _intrinsic_affective_markers(self) -> List[str]:
        """
        Dynamic affective cues from the poem itself (no fixed lexicon).
        Uses repetition, punctuation pressure, and emotionally weighted model outputs.
        """
        cues: List[str] = []

        # High-salience repeated tokens are strong reader-affect anchors.
        freq: Dict[str, int] = {}
        for tok in self.tokens:
            t = str(tok).strip()
            if len(t) < 2:
                continue
            freq[t] = freq.get(t, 0) + 1
        repeated = [t for t, c in sorted(freq.items(), key=lambda x: (-x[1], x[0])) if c >= 2]
        cues.extend(repeated[:4])

        # Pull strongest emotion labels from model outputs when present.
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        if isinstance(emotions, dict):
            min_conf = float(self._rules.get("reader_response", {}).get("engagement_blend", {}).get("emotion_confidence_min", 0.1))
            ranked = sorted(
                [(str(k), float(v)) for k, v in emotions.items() if isinstance(v, (int, float))],
                key=lambda x: x[1],
                reverse=True,
            )
            cues.extend([f"emotion:{k}" for k, v in ranked[:3] if v > min_conf])

        # Punctuation pressure can signal affective intensity.
        qn = self.text.count("?")
        ex = self.text.count("!")
        if qn > 0:
            cues.append(f"question_density:{qn}")
        if ex > 0:
            cues.append(f"exclamation_density:{ex}")

        # Deduplicate while preserving order.
        deduped: List[str] = []
        seen = set()
        for c in cues:
            if c and c not in seen:
                seen.add(c)
                deduped.append(c)
        return deduped[:6]

    def _analyze_context_dependence(self) -> float:
        """Analyze how much meaning depends on context"""
        sentence_count = max(1.0, self._to_float(self._sig("linguistic", "text_metrics", "descriptive_stats", "sentence_count", default=1), 1.0))
        line_count = max(1.0, float(len(self.lines)))
        dependency_nodes = len(self._sig("linguistic", "dependency_tree", default=[]))
        ratio = min(1.0, (line_count / sentence_count) * self._rules["scales"]["line_sentence_ratio_scale"] + dependency_nodes / self._rules["scales"]["dependency_node_scale"])
        return round(max(0.0, ratio), self._rules["scales"]["quality_rounding"])

    def _text_quality_signal(self) -> float:
        """Compute a dynamic text quality signal from live metrics."""
        lex = self._to_float(self._sig("quantitative", "lexical_metrics", "lexical_density", default=0.0), 0.0)
        ttr = self._to_float(self._sig("quantitative", "lexical_metrics", "type_token_ratio", default=0.0), 0.0)
        rhyme = self._to_float(self._sig("prosody", "rhyme", "rhyme_density", default=0.0), 0.0)
        readability = self._to_float(
            self._sig("linguistic", "text_metrics", "readability", "flesch_reading_ease", default=60.0),
            60.0,
        )

        if lex > 1.0:
            lex = lex / 100.0
        if ttr > 1.0:
            ttr = ttr / 100.0
        if rhyme > 1.0:
            rhyme = rhyme / 100.0

        imagery = self._sig("literary_devices", "imagery", default={})
        imagery_total = 0.0
        if isinstance(imagery, dict):
            imagery_total = sum(float(v) for v in imagery.values() if isinstance(v, (int, float)))
        imagery_score = min(1.0, imagery_total / self._rules["scales"]["imagery_total_scale"]) if imagery_total else 0.0

        # If upstream metrics are sparse, derive signal directly from text.
        if lex == 0.0 and ttr == 0.0:
            alpha_tokens = [t for t in self.tokens if re.search(r"\w", t)]
            if alpha_tokens:
                unique_ratio = len(set(alpha_tokens)) / max(1, len(alpha_tokens))
                avg_len = sum(len(t) for t in alpha_tokens) / max(1, len(alpha_tokens))
                lex = max(0.0, min(1.0, 0.6 * unique_ratio + 0.4 * min(1.0, avg_len / 8.0)))
                ttr = unique_ratio
        if rhyme == 0.0 and len(self.lines) >= 2:
            endings = []
            for line in self.lines:
                toks = [tok for tok in re.findall(r"[\w\u0900-\u097F\u0600-\u06FF]+", line) if tok]
                if toks:
                    endings.append(toks[-1][-2:].lower())
            if endings:
                rhyme = len(endings) - len(set(endings))
                rhyme = max(0.0, min(1.0, rhyme / max(1.0, len(endings) - 1)))
        if imagery_score == 0.0 and self.lines:
            metaphor_like = sum(
                1
                for ln in self.lines
                if any(sym in ln for sym in (",", ":", "—", "-", " जैसे ", " सा ", " सी "))
            )
            imagery_score = max(0.0, min(1.0, metaphor_like / max(1.0, len(self.lines))))

        readability_score = max(0.0, min(1.0, readability / self._rules["scales"]["readability_scale"]))
        quality = (
            self._rules["quality_weights"]["lex"] * max(0.0, min(1.0, lex)) +
            self._rules["quality_weights"]["ttr"] * max(0.0, min(1.0, ttr)) +
            self._rules["quality_weights"]["imagery"] * imagery_score +
            self._rules["quality_weights"]["rhyme"] * max(0.0, min(1.0, rhyme)) +
            self._rules["quality_weights"]["readability"] * readability_score
        )
        return round(max(0.0, min(1.0, quality)), self._rules["scales"]["quality_rounding"])

    def _analyze_gender_representation(self) -> Dict[str, Any]:
        """Analyze gender representation using NER and zero-shot thematic classification."""
        # NER-based pronoun and entity gender signals
        ner = self._sig("linguistic", "named_entities", default=[])
        male_count = sum(1 for n in ner if isinstance(n, dict) and "male" in str(n.get("label", "")).lower())
        female_count = sum(1 for n in ner if isinstance(n, dict) and "female" in str(n.get("label", "")).lower())

        # Augment with ZSC: detect whether the poem foregrounds feminine or masculine experience
        scores = self._zsc(["feminine perspective", "masculine perspective", "gender-neutral perspective"]) or {}
        fem_zsc = scores.get("feminine perspective", 0.0)
        masc_zsc = scores.get("masculine perspective", 0.0)
        neutral_zsc = scores.get("gender-neutral perspective", 0.0)

        total_ner = male_count + female_count
        ratio = female_count / total_ner if total_ner > 0 else float(self._rules.get("blend_weights", {}).get("gender_default_ratio", 0.5))
        # Blend NER ratio with ZSC signal for final score
        zsc_fem_ratio = fem_zsc / max(fem_zsc + masc_zsc, 1e-6)
        blended_ratio = 0.4 * ratio + 0.6 * zsc_fem_ratio

        return {
            "male_count": male_count,
            "female_count": female_count,
            "ner_ratio": round(ratio, 3),
            "zsc_feminine": round(fem_zsc, 3),
            "zsc_masculine": round(masc_zsc, 3),
            "zsc_neutral": round(neutral_zsc, 3),
            "score": round(min(1.0, blended_ratio), 3),
            "summary": f"Feminine ZSC: {fem_zsc:.2f}, Masculine ZSC: {masc_zsc:.2f}, NER Male: {male_count}, Female: {female_count}"
        }

    def _analyze_power_dynamics(self) -> Dict[str, Any]:
        """Analyze power dynamics using speech act data and zero-shot classification."""
        speech_acts = self._sig("additional", "pragmatics", "speech_acts", "counts", default={})
        directive = self._to_int(speech_acts.get("directive", 0))
        declarative = self._to_int(speech_acts.get("declarative", 0))

        # ZSC for ideological power signals
        scores = self._zsc([
            "poem about power and control",
            "poem about submission and powerlessness",
            "poem about equality and liberation"
        ]) or {}
        power_score = scores.get("poem about power and control", 0.0)
        submission_score = scores.get("poem about submission and powerlessness", 0.0)
        liberation_score = scores.get("poem about equality and liberation", 0.0)
        # Combined score: high power OR high submission = power imbalance present
        authority_signal = max(power_score, submission_score)

        return {
            "directive_acts": directive,
            "declarative_acts": declarative,
            "zsc_power": round(power_score, 3),
            "zsc_submission": round(submission_score, 3),
            "zsc_liberation": round(liberation_score, 3),
            "score": round(min(1.0, 0.4 * min(1.0, (directive + declarative) / 10.0) + 0.6 * authority_signal), 3),
            "summary": f"Directive speech acts: {directive}, ZSC power: {power_score:.2f}, liberation: {liberation_score:.2f}"
        }

    def _analyze_language_patriarchy(self) -> Dict[str, Any]:
        """Analyze patriarchal language structures via zero-shot classification."""
        scores = self._zsc([
            "patriarchal language and male dominance",
            "feminist and gender-equal language",
            "objectification of women"
        ]) or {}
        patriarchal_score = scores.get("patriarchal language and male dominance", 0.0)
        feminist_score = scores.get("feminist and gender-equal language", 0.0)
        objectification_score = scores.get("objectification of women", 0.0)
        composite = max(patriarchal_score, objectification_score)

        return {
            "zsc_patriarchal": round(patriarchal_score, 3),
            "zsc_feminist": round(feminist_score, 3),
            "zsc_objectification": round(objectification_score, 3),
            "score": round(composite, 3),
            "summary": f"Patriarchal ZSC: {patriarchal_score:.2f}, Feminist ZSC: {feminist_score:.2f}"
        }

    def _analyze_class_representation(self) -> Dict[str, Any]:
        """Analyze class representation via ZSC and dialect/lexical signals."""
        # Dialect markers as working-class proxy
        dialect_count = self._to_int(self._sig("additional", "dialect_detection", "marker_count", default=0))
        # Diction score as educated/upper-class proxy (0-10 scale from evaluation)
        diction_score = self._to_float(self._sig("evaluation", "ratings", "language_diction", default=5.0), 5.0)

        # ZSC for class themes
        scores = self._zsc([
            "class struggle and economic inequality",
            "working class experience and labor",
            "bourgeois values and privilege",
            "revolutionary and socialist themes"
        ]) or {}
        working_class_zsc = max(
            scores.get("class struggle and economic inequality", 0.0),
            scores.get("working class experience and labor", 0.0),
        )
        upper_class_zsc = scores.get("bourgeois values and privilege", 0.0)
        revolutionary_zsc = scores.get("revolutionary and socialist themes", 0.0)

        # Aggregate score: presence of any class-conscious themes
        composite = max(working_class_zsc, upper_class_zsc, revolutionary_zsc)

        return {
            "dialect_markers": dialect_count,
            "diction_score": round(diction_score, 2),
            "zsc_working_class": round(working_class_zsc, 3),
            "zsc_upper_class": round(upper_class_zsc, 3),
            "zsc_revolutionary": round(revolutionary_zsc, 3),
            "score": round(composite, 3),
            "summary": f"Working class ZSC: {working_class_zsc:.2f}, Upper class ZSC: {upper_class_zsc:.2f}, Revolutionary ZSC: {revolutionary_zsc:.2f}"
        }

    def _analyze_ideology(self) -> Dict[str, Any]:
        """Analyze ideological content via ZSC."""
        # Structural signal: proliferation of rhetorical schemes indicates polemic intent
        schemes = self._sig("literary_devices", "schemes", default={})
        scheme_count = sum(len(v) for v in schemes.values() if isinstance(v, list))

        scores = self._zsc([
            "political ideology and manifesto",
            "religious or spiritual ideology",
            "hegemonic values and conformity",
            "counter-hegemonic resistance",
            "nationalistic or patriotic themes"
        ]) or {}
        political = scores.get("political ideology and manifesto", 0.0)
        religious = scores.get("religious or spiritual ideology", 0.0)
        hegemonic = scores.get("hegemonic values and conformity", 0.0)
        counter = scores.get("counter-hegemonic resistance", 0.0)
        nationalist = scores.get("nationalistic or patriotic themes", 0.0)

        # Composite: any strong ideological signal
        composite = max(political, religious, hegemonic, counter, nationalist)
        # Blend with structural signal (heavy scheme use ↑ rhetorical/ideological density)
        blended = 0.6 * composite + 0.4 * min(1.0, scheme_count / 10.0)

        return {
            "rhetorical_scheme_count": scheme_count,
            "zsc_political": round(political, 3),
            "zsc_religious": round(religious, 3),
            "zsc_hegemonic": round(hegemonic, 3),
            "zsc_counter_hegemonic": round(counter, 3),
            "zsc_nationalist": round(nationalist, 3),
            "score": round(min(1.0, blended), 3),
            "summary": f"Ideology ZSC dominant: {max(scores, key=scores.get, default='none')} ({composite:.2f}), schemes: {scheme_count}"
        }

    def _analyze_economic_themes(self) -> Dict[str, Any]:
        """Analyze economic themes using ZSC."""
        scores = self._zsc([
            "poverty and economic hardship",
            "wealth and capitalism",
            "labor and exploitation",
            "commodity and materialism"
        ]) or {}
        poverty = scores.get("poverty and economic hardship", 0.0)
        wealth = scores.get("wealth and capitalism", 0.0)
        labor = scores.get("labor and exploitation", 0.0)
        material = scores.get("commodity and materialism", 0.0)

        composite = max(poverty, wealth, labor, material)
        dominant = max(scores, key=scores.get, default="none") if scores else "none"

        return {
            "zsc_poverty": round(poverty, 3),
            "zsc_wealth": round(wealth, 3),
            "zsc_labor": round(labor, 3),
            "zsc_material": round(material, 3),
            "dominant_theme": dominant,
            "score": round(composite, 3),
            "summary": f"Economic theme ZSC: {dominant} ({composite:.2f})"
        }

    def _analyze_unconscious_content(self) -> Dict[str, Any]:
        """Analyze unconscious / repressed content via emotion signals + ZSC."""
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        fear = self._to_float(emotions.get("fear", 0.0), 0.0) if isinstance(emotions, dict) else 0.0
        sadness = self._to_float(emotions.get("sadness", 0.0), 0.0) if isinstance(emotions, dict) else 0.0
        disgust = self._to_float(emotions.get("disgust", 0.0), 0.0) if isinstance(emotions, dict) else 0.0
        emotion_signal = min(1.0, (fear + sadness + disgust))

        scores = self._zsc([
            "repressed desires and unconscious mind",
            "anxieties and psychological tension",
            "dream imagery and surrealism",
            "trauma and suppressed memory"
        ]) or {}
        repression = scores.get("repressed desires and unconscious mind", 0.0)
        anxiety = scores.get("anxieties and psychological tension", 0.0)
        dream = scores.get("dream imagery and surrealism", 0.0)
        trauma = scores.get("trauma and suppressed memory", 0.0)

        max_zsc = max(repression, anxiety, dream, trauma)
        blend = self._rules.get("blend_weights", {})
        blended = (
            float(blend.get("psycho_emotion", 0.5)) * emotion_signal
            + float(blend.get("psycho_zsc", 0.5)) * max_zsc
        )
        dominant = max(scores, key=scores.get, default="none") if scores else "none"

        return {
            "emotion_fear": round(fear, 3),
            "emotion_sadness": round(sadness, 3),
            "emotion_disgust": round(disgust, 3),
            "zsc_repression": round(repression, 3),
            "zsc_anxiety": round(anxiety, 3),
            "zsc_dream": round(dream, 3),
            "zsc_trauma": round(trauma, 3),
            "dominant_mode": dominant,
            "score": round(min(1.0, blended), 3),
            "summary": f"Unconscious ZSC dominant: {dominant} ({max_zsc:.2f}), emotion signal: {emotion_signal:.2f}"
        }

    def _analyze_defense_mechanisms(self) -> Dict[str, Any]:
        """Analyze psychological defense mechanisms via ZSC."""
        scores = self._zsc([
            "denial and psychological repression",
            "displacement of emotions",
            "rationalization and intellectualization",
            "sublimation of urges into art",
            "projection of inner conflict"
        ]) or {}
        denial = scores.get("denial and psychological repression", 0.0)
        displacement = scores.get("displacement of emotions", 0.0)
        rationalization = scores.get("rationalization and intellectualization", 0.0)
        sublimation = scores.get("sublimation of urges into art", 0.0)
        projection = scores.get("projection of inner conflict", 0.0)

        # The dominant mechanism signals the defensive mode
        dominant = max(scores, key=scores.get, default="none") if scores else "none"
        composite = max(denial, displacement, rationalization, sublimation, projection)

        return {
            "zsc_denial": round(denial, 3),
            "zsc_displacement": round(displacement, 3),
            "zsc_rationalization": round(rationalization, 3),
            "zsc_sublimation": round(sublimation, 3),
            "zsc_projection": round(projection, 3),
            "dominant_mechanism": dominant,
            "score": round(composite, 3),
            "summary": f"Defense mechanism ZSC: {dominant} ({composite:.2f})"
        }

    def _analyze_psychosexual_themes(self) -> Dict[str, Any]:
        """Analyze psychosexual themes via ZSC and emotion signals."""
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        love = self._to_float(emotions.get("love", 0.0), 0.0) if isinstance(emotions, dict) else 0.0

        scores = self._zsc([
            "erotic desire and sensuality",
            "romantic love and longing",
            "taboo and transgression",
            "body and physicality"
        ]) or {}
        erotic = scores.get("erotic desire and sensuality", 0.0)
        romantic = scores.get("romantic love and longing", 0.0)
        taboo = scores.get("taboo and transgression", 0.0)
        body = scores.get("body and physicality", 0.0)

        composite = max(erotic, romantic, taboo, body, love)
        dominant = max(scores, key=scores.get, default="none") if scores else "none"

        return {
            "emotion_love": round(love, 3),
            "zsc_erotic": round(erotic, 3),
            "zsc_romantic": round(romantic, 3),
            "zsc_taboo": round(taboo, 3),
            "zsc_body": round(body, 3),
            "dominant_mode": dominant,
            "score": round(min(1.0, composite), 3),
            "summary": f"Psychosexual ZSC: {dominant} ({max(erotic, taboo):.2f}), love emotion: {love:.2f}"
        }

    def _analyze_nature_representation(self) -> Dict[str, Any]:
        """Analyze nature representation via imagery signals + ZSC."""
        imagery = self._sig("literary_devices", "imagery", default={})
        organic_count = self._to_int(imagery.get("organic", 0)) if isinstance(imagery, dict) else 0
        nature_imagery_total = organic_count

        scores = self._zsc([
            "nature and landscape imagery",
            "animals and wildlife",
            "plants and vegetation",
            "seasons and weather"
        ]) or {}
        landscape = scores.get("nature and landscape imagery", 0.0)
        animals = scores.get("animals and wildlife", 0.0)
        plants = scores.get("plants and vegetation", 0.0)
        seasons = scores.get("seasons and weather", 0.0)

        composite = max(landscape, animals, plants, seasons)
        imagery_signal = min(1.0, nature_imagery_total / 5.0)
        blend = self._rules.get("blend_weights", {})
        blended = (
            float(blend.get("ecocrit_imagery", 0.5)) * imagery_signal
            + float(blend.get("ecocrit_zsc", 0.5)) * composite
        )

        return {
            "organic_imagery_count": organic_count,
            "zsc_landscape": round(landscape, 3),
            "zsc_animals": round(animals, 3),
            "zsc_plants": round(plants, 3),
            "zsc_seasons": round(seasons, 3),
            "score": round(min(1.0, blended), 3),
            "summary": f"Nature ZSC: {composite:.2f}, imagery organic count: {organic_count}"
        }

    def _analyze_environmental_themes(self) -> Dict[str, Any]:
        """Analyze environmental themes and eco-consciousness via ZSC."""
        scores = self._zsc([
            "ecological crisis and environmental destruction",
            "harmony with nature and sustainability",
            "climate change and global warming",
            "human impact on environment"
        ]) or {}
        crisis = scores.get("ecological crisis and environmental destruction", 0.0)
        harmony = scores.get("harmony with nature and sustainability", 0.0)
        climate = scores.get("climate change and global warming", 0.0)
        impact = scores.get("human impact on environment", 0.0)

        composite = max(crisis, harmony, climate, impact)
        dominant = max(scores, key=scores.get, default="none") if scores else "none"

        return {
            "zsc_crisis": round(crisis, 3),
            "zsc_harmony": round(harmony, 3),
            "zsc_climate": round(climate, 3),
            "zsc_human_impact": round(impact, 3),
            "dominant_theme": dominant,
            "score": round(composite, 3),
            "summary": f"Environmental ZSC: {dominant} ({composite:.2f})"
        }

    def _analyze_human_nature_relationship(self) -> Dict[str, Any]:
        """Analyze the human-nature relationship via sentiment + ZSC."""
        # Primary: ZSC
        scores = self._zsc([
            "reverence and awe for nature",
            "alienation from nature",
            "domination and exploitation of nature",
            "symbiosis and coexistence with nature"
        ]) or {}
        reverence = scores.get("reverence and awe for nature", 0.0)
        alienation = scores.get("alienation from nature", 0.0)
        domination = scores.get("domination and exploitation of nature", 0.0)
        symbiosis = scores.get("symbiosis and coexistence with nature", 0.0)

        # Secondary fallback: existing sentiment signal
        sentiment = self._sig("additional", "transformer_analysis", "sentiment", default={})
        if isinstance(sentiment, dict) and sentiment:
            sent_default = float(self._rules.get("blend_weights", {}).get("human_nature_sentiment_default", 0.0))
            sent_score = self._to_float(sentiment.get("score", sent_default), sent_default)
        else:
            emotions = self._sig("additional", "transformer_analysis", "emotions", default={}) or {}
            pos = self._to_float(emotions.get("joy", 0.0), 0.0) + self._to_float(emotions.get("love", 0.0), 0.0)
            neg = self._to_float(emotions.get("sadness", 0.0), 0.0) + self._to_float(emotions.get("fear", 0.0), 0.0)
            sent_score = pos / max(1e-6, pos + neg)

        positive_relationship = max(reverence, symbiosis)
        negative_relationship = max(alienation, domination)
        dominant = max(scores, key=scores.get, default="none") if scores else "none"

        # Blend ZSC + sentiment
        blend = self._rules.get("blend_weights", {})
        blended_score = (
            float(blend.get("human_nature_positive", 0.7)) * positive_relationship
            + float(blend.get("human_nature_sentiment", 0.3)) * sent_score
        )

        return {
            "zsc_reverence": round(reverence, 3),
            "zsc_alienation": round(alienation, 3),
            "zsc_domination": round(domination, 3),
            "zsc_symbiosis": round(symbiosis, 3),
            "sentiment_positivity": round(sent_score, 3),
            "dominant_mode": dominant,
            "score": round(min(1.0, blended_score), 3),
            "summary": f"Human-nature ZSC: {dominant} ({max(positive_relationship, negative_relationship):.2f})"
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
            "has_unity": unity >= float(self._rules.get("scales", {}).get("aristotelian_unity_threshold", 0.55)),
            "score": round(unity, 2),
            "summary": f"Unity of action score: {unity:.2f}"
        }

    def _analyze_mimesis(self) -> Dict[str, Any]:
        """Analyze mimesis (imitation of reality)"""
        entities = self._sig("linguistic", "named_entities", default=[])
        count = len(entities) if isinstance(entities, list) else 0
        
        return {
            "realism_marker_count": count,
            "score": min(1.0, count / max(1.0, float(self._rules.get("scales", {}).get("mimesis_count_scale", 5.0)))),
            "summary": f"Mimesis: {count} realism markers"
        }

    def _analyze_catharsis_potential(self) -> Dict[str, Any]:
        """Analyze catharsis potential"""
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        emotion_multiplier = float(self._rules.get("scales", {}).get("catharsis_emotion_multiplier", 15.0))
        count = int(
            (
                self._to_float(emotions.get("sadness", 0.0), 0.0)
                + self._to_float(emotions.get("fear", 0.0), 0.0)
                + self._to_float(emotions.get("love", 0.0), 0.0)
            )
            * emotion_multiplier
        ) if isinstance(emotions, dict) else 0
        
        return {
            "emotional_word_count": count,
            "score": min(
                1.0,
                count / max(1.0, float(self._rules.get("scales", {}).get("catharsis_count_scale", 5.0))),
            ),
            "summary": f"Catharsis potential: {count} emotional markers"
        }

    def _analyze_decorum(self) -> Dict[str, Any]:
        """Analyze decorum (appropriateness)"""
        readability = self._to_float(self._sig("quantitative", "readability_metrics", "flesch_reading_ease", default=60.0), 60.0)
        score = max(0.0, min(1.0, readability / 100.0))
        return {
            "appropriate": score >= float(self._rules.get("scales", {}).get("decorum_threshold", 0.45)),
            "score": round(score, 2),
            "summary": f"Decorum score from readability alignment: {score:.2f}"
        }

    def _analyze_unity_horatian(self) -> Dict[str, Any]:
        """Analyze unity (Horatian)"""
        coherence = self._to_float(self._sig("linguistic", "text_metrics", "readability", "flesch_reading_ease", default=60.0), 60.0)
        score = max(0.0, min(1.0, coherence / 100.0))
        return {
            "has_unity": score >= float(self._rules.get("scales", {}).get("unity_horatian_threshold", 0.5)),
            "score": round(score, 2),
            "summary": f"Unity/coherence score: {score:.2f}"
        }

    def _analyze_instruction_delight(self) -> Dict[str, Any]:
        """Analyze balance of instruction and delight"""
        speech_acts = self._sig("additional", "pragmatics", "speech_acts", "counts", default={})
        emotions = self._sig("additional", "transformer_analysis", "emotions", default={})
        inst_count = self._to_int(speech_acts.get("assertive", 0)) + self._to_int(speech_acts.get("directive", 0))
        delight_mul = float(self._rules.get("scales", {}).get("instruction_delight_emotion_multiplier", 10.0))
        del_count = int(self._to_float(emotions.get("joy", 0.0), 0.0) * delight_mul) + int(self._to_float(emotions.get("love", 0.0), 0.0) * delight_mul)
        
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
            return self._summary_rules["synthesis_empty"]
        
        scored = [(k, float(v.get("score", 0) or 0)) for k, v in results.items()]
        avg_score = sum(v for _, v in scored) / max(1, len(scored))
        top = max(scored, key=lambda x: x[1]) if scored else ("n/a", 0.0)
        low = min(scored, key=lambda x: x[1]) if scored else ("n/a", 0.0)
        return self._summary_rules["synthesis_template"].format(
            count=len(results),
            avg=avg_score,
            top_name=top[0],
            top_score=top[1],
            low_name=low[0],
            low_score=low[1],
        )
