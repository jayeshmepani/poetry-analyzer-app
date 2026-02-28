"""
Rating & Evaluation Engine
Complete 7-category scoring, publishability assessment, performance assessment
Based on Ultimate Literary Master System
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class EvaluationConfig:
    """Configuration for evaluation weights"""
    technical_craft: float = 0.15
    language_diction: float = 0.15
    imagery_voice: float = 0.15
    emotional_impact: float = 0.15
    cultural_fidelity: float = 0.15
    originality: float = 0.15
    computational_greatness: float = 0.10


class EvaluationEngine:
    """
    Comprehensive evaluation and rating system
    7-category scoring with detailed justifications
    """

    def __init__(self, config: Optional[EvaluationConfig] = None):
        self.config = config or EvaluationConfig()
        self.text = ""
        self.metrics: Dict[str, Any] = {}
        self.language = "en"

    def evaluate(self, text: str, metrics: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Complete evaluation of a literary work
        """
        self.text = text
        self.metrics = metrics
        self.language = language

        # Calculate ratings
        ratings = self._calculate_ratings()

        # Identify strengths
        strengths = self._identify_strengths()

        # Identify issues
        issues = self._identify_issues()

        # Generate suggestions
        suggestions = self._generate_suggestions()

        # Publishability assessment
        publishability = self._assess_publishability()

        # Performance assessment (for spoken word)
        performance = self._assess_performance_detailed(self.text, self.metrics)

        # Generate corrected versions
        minimal_corrected = self._generate_minimal_corrected()
        polished_version = self._generate_polished_version()

        return {
            "ratings": ratings,
            "strengths": strengths,
            "issues": issues,
            "suggestions": suggestions,
            "publishability": publishability,
            "performance": performance,
            "minimal_corrected_version": minimal_corrected,
            "polished_version": polished_version
        }

    def _calculate_ratings(self) -> Dict[str, float]:
        """Calculate 7-category ratings (0-10 scale)"""
        ratings = {}

        # 1. Technical Craft (meter, rhyme, structure)
        ratings["technical_craft"] = self._rate_technical_craft()

        # 2. Language & Diction
        ratings["language_diction"] = self._rate_language_diction()

        # 3. Imagery & Voice
        ratings["imagery_voice"] = self._rate_imagery_voice()

        # 4. Emotional Impact
        ratings["emotional_impact"] = self._rate_emotional_impact()

        # 5. Cultural Fidelity
        ratings["cultural_fidelity"] = self._rate_cultural_fidelity()

        # 6. Originality
        ratings["originality"] = self._rate_originality()

        # 7. Computational Greatness (if available)
        cg_score = self.metrics.get("quantitative", {}).get("computational_greatness_score")
        if cg_score is None:
            cg_score = 5.0
        ratings["computational_greatness"] = cg_score if cg_score is not None else 5.0

        # Overall quality (weighted average)
        overall = (
            ratings["technical_craft"] * self.config.technical_craft +
            ratings["language_diction"] * self.config.language_diction +
            ratings["imagery_voice"] * self.config.imagery_voice +
            ratings["emotional_impact"] * self.config.emotional_impact +
            ratings["cultural_fidelity"] * self.config.cultural_fidelity +
            ratings["originality"] * self.config.originality +
            ratings["computational_greatness"] * self.config.computational_greatness
        )

        ratings["overall_quality"] = round(overall, 1)

        # Round all ratings
        for key in ratings:
            ratings[key] = round(ratings[key], 1)

        return ratings

    def _rate_technical_craft(self) -> float:
        """Rate technical craft (meter, rhyme, structure)"""
        score = 5.0  # Base score

        prosody = self.metrics.get("prosody", {})
        quantitative = self.metrics.get("quantitative", {})

        # Meter regularity
        meter = prosody.get("meter", {})
        if meter.get("metrical_regularity", 0) > 0.7:
            score += 2.0
        elif meter.get("metrical_regularity", 0) > 0.5:
            score += 1.0

        # Rhyme quality
        rhyme = prosody.get("rhyme", {})
        if rhyme.get("rhyme_density", 0) > 0.8:
            score += 2.0
        elif rhyme.get("rhyme_density", 0) > 0.5:
            score += 1.0

        # Structure
        structural = quantitative.get("structural_metrics", {})
        if structural.get("total_lines", 0) > 0:
            score += 1.0

        return min(10, max(0, score))

    def _rate_language_diction(self) -> float:
        """Rate language and diction"""
        score = 5.0

        linguistic = self.metrics.get("linguistic", {})
        quantitative = self.metrics.get("quantitative", {})

        # Lexical diversity
        lexical = quantitative.get("lexical_metrics", {})
        ttr = lexical.get("type_token_ratio", 0)
        if ttr > 0.6:
            score += 2.5
        elif ttr > 0.4:
            score += 1.5

        # Lexical density
        density = lexical.get("lexical_density", 0)
        if density > 60:
            score += 1.5
        elif density > 40:
            score += 0.5

        # POS distribution (good balance)
        pos = linguistic.get("pos_distribution", {})
        if pos.get("noun", 0) > 0 and pos.get("verb", 0) > 0:
            score += 1.0

        return min(10, max(0, score))

    def _rate_imagery_voice(self) -> float:
        """Rate imagery and voice"""
        score = 5.0

        literary = self.metrics.get("literary_devices", {})
        imagery = literary.get("imagery", {})

        # Count imagery types
        imagery_count = sum(len(v) for v in imagery.values())
        if imagery_count > 10:
            score += 3.0
        elif imagery_count > 5:
            score += 2.0
        elif imagery_count > 2:
            score += 1.0

        # Figurative language
        tropes = literary.get("tropes", {})
        trope_count = sum(len(v) for v in tropes.values())
        if trope_count > 8:
            score += 2.0
        elif trope_count > 3:
            score += 1.0

        return min(10, max(0, score))

    def _rate_emotional_impact(self) -> float:
        """Rate emotional impact"""
        score = 5.0

        advanced = self.metrics.get("advanced", {})
        sentiment = advanced.get("sentiment", {})

        # Sentiment intensity
        valence = abs(sentiment.get("valence", 0))
        if valence > 0.5:
            score += 3.0
        elif valence > 0.3:
            score += 2.0
        elif valence > 0.1:
            score += 1.0

        # Arousal (intensity)
        arousal = sentiment.get("arousal", 0)
        if arousal > 0.5:
            score += 2.0

        return min(10, max(0, score))

    def _rate_cultural_fidelity(self) -> float:
        """Rate cultural and historical fidelity"""
        score = 6.0  # Base score - assume neutral

        # Check for appropriate cultural elements
        literary = self.metrics.get("literary_devices", {})
        
        # Alankar usage for Indic languages
        alankar = literary.get("sanskrit_alankar", {})
        alankar_count = sum(len(v) for v in alankar.values())
        if alankar_count > 3:
            score += 2.0
        elif alankar_count > 0:
            score += 1.0

        # Rasa presence
        rasa = literary.get("rasa_vector", {})
        if rasa and rasa.get("dominant_rasa"):
            score += 2.0

        return min(10, max(0, score))

    def _rate_originality(self) -> float:
        """Rate originality and creativity"""
        score = 5.0

        quantitative = self.metrics.get("quantitative", {})
        lexical = quantitative.get("lexical_metrics", {})

        # Unique word ratio
        ttr = lexical.get("type_token_ratio", 0)
        if ttr > 0.7:
            score += 3.0
        elif ttr > 0.5:
            score += 2.0

        # Hapax legomena (words used once - indicates vocabulary richness)
        hapax = lexical.get("hapax_legomena", 0)
        total = lexical.get("total_words", 1)
        hapax_ratio = hapax / total if total > 0 else 0
        if hapax_ratio > 0.6:
            score += 2.0
        elif hapax_ratio > 0.4:
            score += 1.0

        return min(10, max(0, score))

    def _identify_strengths(self) -> List[Dict[str, Any]]:
        """Identify strengths in the work"""
        strengths = []

        quantitative = self.metrics.get("quantitative", {})
        literary = self.metrics.get("literary_devices", {})
        prosody = self.metrics.get("prosody", {})

        # Check lexical diversity
        lexical = quantitative.get("lexical_metrics", {})
        if lexical.get("type_token_ratio", 0) > 0.5:
            strengths.append({
                "category": "Vocabulary",
                "description": "Strong vocabulary diversity with high type-token ratio",
                "evidence": f"TTR: {lexical.get('type_token_ratio', 0):.2f}",
                "impact": "Demonstrates rich language use and avoids repetition"
            })

        # Check imagery
        imagery = literary.get("imagery", {})
        imagery_count = sum(len(v) for v in imagery.values())
        if imagery_count > 5:
            strengths.append({
                "category": "Imagery",
                "description": "Effective use of sensory imagery",
                "evidence": f"{imagery_count} instances of sensory language detected",
                "impact": "Creates vivid mental pictures for the reader"
            })

        # Check figurative language
        tropes = literary.get("tropes", {})
        trope_count = sum(len(v) for v in tropes.values())
        if trope_count > 5:
            strengths.append({
                "category": "Figurative Language",
                "description": "Strong use of metaphors, similes, and other tropes",
                "evidence": f"{trope_count} instances of figurative language",
                "impact": "Adds depth and layers of meaning"
            })

        # Check meter
        meter = prosody.get("meter", {})
        if meter.get("metrical_regularity", 0) > 0.6:
            strengths.append({
                "category": "Prosody",
                "description": f"Consistent {meter.get('detected_meter', 'meter')} pattern",
                "evidence": f"Regularity score: {meter.get('metrical_regularity', 0):.2f}",
                "impact": "Creates musical rhythm and flow"
            })

        # Check Alankar (for Indic)
        alankar = literary.get("sanskrit_alankar", {})
        alankar_count = sum(len(v) for v in alankar.values())
        if alankar_count > 2:
            strengths.append({
                "category": "Classical Devices",
                "description": "Rich use of Sanskrit/Hindi Alankars (figures of speech)",
                "evidence": f"{alankar_count} Alankars detected",
                "impact": "Demonstrates mastery of classical poetic ornamentation"
            })

        # Check Rasa
        rasa = literary.get("rasa_vector", {})
        if rasa and rasa.get("dominant_rasa"):
            strengths.append({
                "category": "Emotional Essence",
                "description": f"Strong presence of {rasa.get('dominant_rasa').capitalize()} Rasa",
                "evidence": "Consistent emotional tone detected via Navarasa theory",
                "impact": "Evokes a powerful aesthetic experience (rasanubhuti)"
            })

        return strengths[:6]

    def _identify_issues(self) -> List[Dict[str, Any]]:
        """Identify issues in the work"""
        issues = []

        quantitative = self.metrics.get("quantitative", {})
        prosody = self.metrics.get("prosody", {})

        # Check for low lexical diversity
        lexical = quantitative.get("lexical_metrics", {})
        if lexical.get("type_token_ratio", 0) < 0.3:
            issues.append({
                "location": "Throughout text",
                "issue_type": "DICTION",
                "severity": "moderate",
                "technical_explanation": "Low type-token ratio indicates excessive word repetition",
                "impact_analysis": "Reduces vocabulary richness and reader engagement",
                "evidence": f"TTR: {lexical.get('type_token_ratio', 0):.2f} (ideal: >0.4)",
                "suggested_fix": "Vary word choice using synonyms and related terms",
                "why_it_matters": "Vocabulary diversity enhances literary quality"
            })

        # Check for inconsistent meter
        meter = prosody.get("meter", {})
        if meter.get("detected_meter") == "free_verse" and meter.get("metrical_regularity", 0) < 0.3:
            issues.append({
                "location": "Throughout text",
                "issue_type": "METER",
                "severity": "minor",
                "technical_explanation": "No consistent metrical pattern detected",
                "impact_analysis": "May lack musical rhythm expected in formal poetry",
                "evidence": "Free verse with low regularity",
                "suggested_fix": "Either embrace free verse fully or establish consistent meter",
                "why_it_matters": "Metrical consistency contributes to prosodic quality"
            })

        return issues[:10]

    def _generate_suggestions(self) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        suggestions = []

        ratings = self._calculate_ratings()

        if ratings.get("technical_craft", 5) < 6:
            suggestions.append({
                "priority": 1,
                "category": "Technical Craft",
                "description": "Consider establishing a consistent metrical pattern or embracing free verse fully",
                "example": "Study exemplary poems in your chosen form for guidance"
            })

        if ratings.get("imagery_voice", 5) < 6:
            suggestions.append({
                "priority": 2,
                "category": "Imagery",
                "description": "Add more vivid sensory details across multiple senses",
                "example": "Incorporate visual, auditory, and tactile imagery"
            })

        if ratings.get("originality", 5) < 6:
            suggestions.append({
                "priority": 3,
                "category": "Originality",
                "description": "Explore more unique word choices and fresh metaphors",
                "example": "Avoid clichés and seek unexpected comparisons"
            })

        # Rasa suggestions
        if ratings.get("emotional_impact", 5) < 6:
            suggestions.append({
                "priority": 2,
                "category": "Emotional Resonance",
                "description": "Deepen the dominant Rasa (emotional essence) using appropriate Bhavas",
                "example": "Use Vibhavas (stimuli) and Anubhavas (reactions) to evoke specific emotions"
            })

        return suggestions[:6]

    def _assess_publishability(self) -> Dict[str, Any]:
        """Assess publishability"""
        ratings = self._calculate_ratings()
        overall = ratings.get("overall_quality", 5)

        if overall >= 8.5:
            return {
                "ready": True,
                "needs_light_edits": False,
                "needs_heavy_revision": False,
                "major_rework_required": False,
                "assessment": "Professional-grade work ready for submission after light copyediting",
                "recommended_venues": ["Literary journals", "Poetry magazines", "Anthologies"]
            }
        elif overall >= 7.0:
            return {
                "ready": False,
                "needs_light_edits": True,
                "needs_heavy_revision": False,
                "major_rework_required": False,
                "assessment": "Strong work requiring targeted edits before submission",
                "recommended_venues": ["Regional journals", "Online poetry platforms", "Writing contests"]
            }
        elif overall >= 5.0:
            return {
                "ready": False,
                "needs_light_edits": False,
                "needs_heavy_revision": True,
                "major_rework_required": False,
                "assessment": "Promising work requiring substantial revision",
                "recommended_venues": ["Workshop feedback", "Writing groups", "Revision-focused programs"]
            }
        else:
            return {
                "ready": False,
                "needs_light_edits": False,
                "needs_heavy_revision": False,
                "major_rework_required": True,
                "assessment": "Early draft requiring major rework and development",
                "recommended_venues": ["Writing workshops", "Mentorship programs", "Practice and revision"]
            }

    def _assess_performance_detailed(self, text: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detailed assessment for spoken word/performance based on real metrics
        """
        lines = [l for l in text.split('\n') if l.strip()]
        prosody = metrics.get("prosody", {})
        literary = metrics.get("literary_devices", {})
        
        # Calculate scores based on linguistic features
        vocal_score = 5.0
        if literary.get("schemes", {}).get("alliteration"): vocal_score += 2.0
        if prosody.get("meter", {}).get("metrical_regularity", 0) > 0.6: vocal_score += 2.0
        
        breath_score = 7.0
        avg_len = sum(len(l.split()) for l in lines) / len(lines) if lines else 0
        if avg_len > 12: breath_score -= 2.0 # Challenging long lines
        
        dramatic_score = metrics.get("advanced", {}).get("sentiment", {}).get("valence", 0) * 5 + 5
        
        overall = (vocal_score + breath_score + dramatic_score) / 3
        
        return {
            "overall": round(overall, 1),
            "vocal": round(min(10, vocal_score), 1),
            "breath": round(min(10, breath_score), 1),
            "dramatic": round(min(10, dramatic_score), 1),
            "engagement": round(metrics.get("evaluation", {}).get("ratings", {}).get("emotional_impact", 5), 1),
            "vocal_notes": "Rich sound patterns detected suggest dynamic delivery." if vocal_score > 7 else "Simple structure for clear delivery.",
            "breath_notes": f"Average line length of {avg_len:.1f} words allows for natural breathing." if breath_score > 6 else "Long complex lines require advanced breath control.",
            "dramatic_notes": "Significant emotional variance detected." if dramatic_score > 7 else "Steady emotional tone.",
            "engagement_notes": "Strong imagery facilitates audience connection.",
            "recommendations": [
                "Vary tempo during highly alliterative passages",
                "Use the natural line breaks for strategic pauses",
                "Emphasize sensory imagery to anchor audience attention"
            ]
        }

    def _generate_minimal_corrected(self) -> Optional[str]:
        """Generate minimally corrected version"""
        from app.services.additional_analysis import TextCorrector
        corrector = TextCorrector()
        result = corrector.correct(self.text)
        return result.get("corrected_text", self.text)

    def _generate_polished_version(self) -> Optional[str]:
        """Generate polished/enhanced version"""
        from app.services.additional_analysis import TextCorrector
        corrector = TextCorrector()
        result = corrector.enhance(self.text)
        return result.get("enhanced_text", self.text)


def generate_executive_summary(metrics: Dict[str, Any], ratings: Dict[str, Any]) -> str:
    """Generate executive summary of analysis"""
    quantitative = metrics.get("quantitative", {})
    structural = quantitative.get("structural_metrics", {})
    overall = ratings.get("overall_quality", 5)

    total_lines = structural.get("total_lines", "several")

    if overall >= 8:
        quality = "polished and publishable quality"
    elif overall >= 6:
        quality = "promising with room for improvement"
    else:
        quality = "requiring significant revision"

    return (f"This is a {total_lines}-line literary work with an overall quality score of {overall}/10. "
            f"The work is of {quality}. "
            f"Technical craft scores {ratings.get('technical_craft', 0)}/10, "
            f"while imagery and voice score {ratings.get('imagery_voice', 0)}/10.")


def generate_educational_insight(metrics: Dict[str, Any]) -> str:
    """Generate educational insight based on analysis"""
    prosody = metrics.get("prosody", {})
    meter = prosody.get("meter", {})

    detected = meter.get("detected_meter", "free verse")
    regularity = meter.get("metrical_regularity", 0)

    if detected != "free verse" and regularity < 0.5:
        return (f"**Metrical Consistency**: Your poem shows elements of {detected} meter, "
                f"but with irregular execution (regularity: {regularity:.2f}). "
                f"Study the pattern: {'da-DUM' if 'iamb' in detected else 'DUM-da'} "
                f"and practice scanning lines to improve consistency.")
    else:
        return ("**Poetic Craft**: Continue developing your unique voice while studying "
                "established forms. Read widely in your chosen genre to internalize "
                "successful techniques.")
