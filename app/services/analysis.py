"""
Main Analysis Service
Orchestrates all analysis modules
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

from app.services.quantitative import QuantitativeMetricsCalculator
from app.services.prosody import ProsodyAnalyzer, HindiProsodyAnalyzer, detect_poem_form
from app.services.linguistic import LinguisticAnalyzer
from app.services.literary_devices import LiteraryDevicesAnalyzer


class AnalysisService:
    """Main service that orchestrates all analysis modules"""

    def __init__(self):
        self.quantitative_calc = QuantitativeMetricsCalculator()
        self.prosody_analyzer = ProsodyAnalyzer()
        self.hindi_prosody = HindiProsodyAnalyzer()
        self.linguistic_analyzer = LinguisticAnalyzer()
        self.literary_devices = LiteraryDevicesAnalyzer()

    def analyze(self, text: str, language: str = "en", strictness: int = 7) -> Dict:
        """Run complete analysis on text"""

        # Run all analysis modules
        quantitative = self.quantitative_calc.analyze(text)

        if language in ["hi", "sa", "mr"]:
            prosody = self.hindi_prosody.analyze(text)
        else:
            prosody = self.prosody_analyzer.analyze(text)

        linguistic = self.linguistic_analyzer.analyze(text)
        literary = self.literary_devices.analyze(text)

        # Detect poem form
        form_info = detect_poem_form(text)

        # Calculate ratings based on strictness
        ratings = self._calculate_ratings(
            quantitative, linguistic, literary, strictness
        )

        # Generate executive summary
        summary = self._generate_summary(quantitative, linguistic, literary, ratings)

        # Identify strengths
        strengths = self._identify_strengths(quantitative, linguistic, literary)

        # Generate suggestions
        suggestions = self._generate_suggestions(
            quantitative, linguistic, literary, ratings
        )

        return {
            "quantitative": quantitative,
            "prosody": prosody,
            "linguistic": linguistic,
            "literary_devices": literary,
            "form_detected": form_info,
            "ratings": ratings,
            "executive_summary": summary,
            "strengths": strengths,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat(),
        }

    def _calculate_ratings(
        self, quantitative: Dict, linguistic: Dict, literary: Dict, strictness: int
    ) -> Dict:
        """Calculate quality ratings"""

        # Technical Craft (based on syntax complexity and structure)
        tech_score = self._calculate_technical_score(quantitative, linguistic)

        # Language & Diction
        lang_score = self._calculate_language_score(linguistic)

        # Imagery & Voice
        imagery_score = self._calculate_imagery_score(literary, linguistic)

        # Emotional Impact
        emotion_score = self._calculate_emotional_score(literary, quantitative)

        # Cultural Fidelity (simplified)
        cultural_score = 7.0  # Default assumption

        # Originality
        originality_score = self._calculate_originality_score(quantitative, linguistic)

        # Calculate overall
        overall = (
            tech_score
            + lang_score
            + imagery_score
            + emotion_score
            + cultural_score
            + originality_score
        ) / 6

        return {
            "technical_craft": round(tech_score, 1),
            "language_diction": round(lang_score, 1),
            "imagery_voice": round(imagery_score, 1),
            "emotional_impact": round(emotion_score, 1),
            "cultural_fidelity": round(cultural_score, 1),
            "originality": round(originality_score, 1),
            "overall_quality": round(overall, 1),
        }

    def _calculate_technical_score(self, quantitative: Dict, linguistic: Dict) -> float:
        """Calculate technical craft score"""
        score = 5.0

        # Adjust based on sentence complexity
        if linguistic.get("syntax", {}).get("clauses", {}).get("has_complex_sentences"):
            score += 1.0

        # Adjust based on sentence variety
        sentence_types = linguistic.get("syntax", {}).get("sentence_types", {})
        if sum(sentence_types.values()) > 1:
            score += 0.5

        # Adjust based on morphological complexity
        morph = linguistic.get("morphology", {})
        if morph.get("prefix_count", 0) + morph.get("suffix_count", 0) > 5:
            score += 0.5

        return min(10.0, max(1.0, score))

    def _calculate_language_score(self, linguistic: Dict) -> float:
        """Calculate language and diction score"""
        score = 5.0

        # Check for varied vocabulary
        lexical = linguistic.get("semantics", {})
        if lexical.get("semantic_density", 0) > 0.5:
            score += 1.0

        # Check for rich synonyms
        lex_relations = linguistic.get("lexical_relations", {})
        if len(lex_relations.get("synonyms", {})) > 2:
            score += 1.0

        return min(10.0, max(1.0, score))

    def _calculate_imagery_score(self, literary: Dict, linguistic: Dict) -> float:
        """Calculate imagery and voice score"""
        score = 5.0

        # Check for imagery variety
        imagery = literary.get("imagery", {})
        imagery_types = sum(len(v) for v in imagery.values())

        if imagery_types > 5:
            score += 1.5
        elif imagery_types > 2:
            score += 0.5

        # Check for figurative language
        tropes = literary.get("tropes", {})
        tropes_count = sum(len(v) for v in tropes.values())

        if tropes_count > 5:
            score += 1.5
        elif tropes_count > 2:
            score += 0.5

        return min(10.0, max(1.0, score))

    def _calculate_emotional_score(self, literary: Dict, quantitative: Dict) -> float:
        """Calculate emotional impact score"""
        score = 5.0

        # Check for emotional imagery
        imagery = literary.get("imagery", {})
        emotional_types = ["sadness", "joy", "fear", "anger", "love"]

        # Simple heuristic based on word choice
        text_lower = str(literary).lower()
        emotional_words = sum(1 for t in emotional_types if t in text_lower)

        if emotional_words > 3:
            score += 1.5
        elif emotional_words > 1:
            score += 0.5

        return min(10.0, max(1.0, score))

    def _calculate_originality_score(
        self, quantitative: Dict, linguistic: Dict
    ) -> float:
        """Calculate originality score"""
        score = 5.0

        # Check lexical diversity
        lex = quantitative.get("lexical_metrics", {})
        ttr = lex.get("type_token_ratio", 0)

        if ttr > 0.6:
            score += 1.5
        elif ttr > 0.4:
            score += 0.5

        return min(10.0, max(1.0, score))

    def _generate_summary(
        self, quantitative: Dict, linguistic: Dict, literary: Dict, ratings: Dict
    ) -> str:
        """Generate executive summary"""

        summary_parts = []

        # Language detection
        summary_parts.append(
            f"This is a piece of literary writing with {quantitative.get('structural_metrics', {}).get('total_lines', 'several')} lines."
        )

        # Technical assessment
        tech = ratings.get("technical_craft", 5)
        if tech >= 8:
            summary_parts.append(
                "The technical craft is excellent, with sophisticated sentence structure and good grammatical control."
            )
        elif tech >= 6:
            summary_parts.append(
                "The technical execution is solid, showing competent use of language and structure."
            )
        else:
            summary_parts.append(
                "The technical execution shows room for improvement in sentence structure and grammatical precision."
            )

        # Imagery assessment
        img = ratings.get("imagery_voice", 5)
        if img >= 8:
            summary_parts.append(
                "Rich imagery and figurative language create a vivid sensory experience."
            )
        elif img >= 6:
            summary_parts.append(
                "The imagery and figurative language add depth to the writing."
            )

        # Overall assessment
        overall = ratings.get("overall_quality", 5)
        if overall >= 8:
            summary_parts.append(
                "This is a polished, publishable work with strong artistic merit."
            )
        elif overall >= 6:
            summary_parts.append(
                "This is a promising piece that would benefit from targeted refinement."
            )
        else:
            summary_parts.append(
                "This is a developing work with significant potential for improvement."
            )

        return " ".join(summary_parts)

    def _identify_strengths(
        self, quantitative: Dict, linguistic: Dict, literary: Dict
    ) -> List[str]:
        """Identify strengths in the text"""
        strengths = []

        # Check lexical diversity
        lex = quantitative.get("lexical_metrics", {})
        if lex.get("type_token_ratio", 0) > 0.5:
            strengths.append("Good vocabulary diversity showing author's lexical range")

        # Check imagery
        imagery = literary.get("imagery", {})
        if sum(len(v) for v in imagery.values()) > 3:
            strengths.append(
                "Effective use of sensory imagery to create vivid descriptions"
            )

        # Check figurative language
        tropes = literary.get("tropes", {})
        tropes_count = sum(len(v) for v in tropes.values())
        if tropes_count > 3:
            strengths.append(
                "Strong use of figurative language (metaphors, similes, etc.)"
            )

        # Check sound devices
        phon = linguistic.get("phonetics", {})
        if phon.get("alliteration") or phon.get("assonance"):
            strengths.append("Good attention to sound patterns and phonetic effects")

        # Check emotional resonance
        if tropes.get("personification") or tropes.get("metaphor"):
            strengths.append("Emotional resonance through personification and metaphor")

        return strengths[:5]

    def _generate_suggestions(
        self, quantitative: Dict, linguistic: Dict, literary: Dict, ratings: Dict
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        # Technical suggestions
        if ratings.get("technical_craft", 5) < 7:
            suggestions.append(
                "Consider varying sentence length and structure for better flow"
            )

        # Language suggestions
        if ratings.get("language_diction", 5) < 7:
            suggestions.append(
                "Explore more precise word choices to enhance clarity and impact"
            )

        # Imagery suggestions
        if ratings.get("imagery_voice", 5) < 7:
            suggestions.append("Add more vivid sensory imagery to engage readers")

        # Structural suggestions
        prosody = quantitative.get("structural_metrics", {})
        if prosody.get("line_length_variance", 0) < 2:
            suggestions.append("Consider varying line lengths for rhythmic interest")

        return suggestions[:5]


def analyze_batch(inputs: List[Dict]) -> List[Dict]:
    """Analyze multiple texts"""
    service = AnalysisService()
    results = []

    for item in inputs:
        result = service.analyze(
            text=item.get("text", ""),
            language=item.get("language", "en"),
            strictness=item.get("strictness", 7),
        )
        result["id"] = item.get("id")
        result["title"] = item.get("title")
        results.append(result)

    return results
