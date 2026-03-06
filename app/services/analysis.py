"""
Main Analysis Service
Orchestrates all analysis modules
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter

from app.services.quantitative import QuantitativeMetricsCalculator
from app.services.prosody import ProsodyAnalyzer, HindiProsodyAnalyzer, detect_poem_form
from app.services.linguistic import LinguisticAnalyzer
from app.services.literary_devices import LiteraryDevicesAnalyzer
from app.services.rule_loader import get_analysis_rules


class AnalysisService:
    """Main service that orchestrates all analysis modules"""

    def __init__(self):
        self.quantitative_calc = QuantitativeMetricsCalculator()
        self.prosody_analyzer = ProsodyAnalyzer()
        self.hindi_prosody = HindiProsodyAnalyzer()
        self.linguistic_analyzer = LinguisticAnalyzer()
        self.literary_devices = LiteraryDevicesAnalyzer()
        self._rules = get_analysis_rules()

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

        # TP-CASTT analysis
        tp_castt = self._tp_castt(self.text, linguistic)

        # Pritchard Scale + Transaction Formula
        pritchard = self._pritchard_scale(ratings)
        transaction = self._transaction_value(ratings, linguistic)

        return {
            "quantitative": quantitative,
            "prosody": prosody,
            "linguistic": linguistic,
            "literary_devices": literary,
            "form_detected": form_info,
            "ratings": ratings,
            "pritchard_scale": pritchard,
            "transaction_formula": transaction,
            "tp_castt": tp_castt,
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
        emotion_score = self._calculate_emotional_score(literary, linguistic)

        # Cultural Fidelity (based on language-specific devices)
        cultural_score = self._calculate_cultural_score(literary, linguistic)

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

    def _calculate_cultural_score(self, literary: Dict, linguistic: Dict) -> float:
        rules = self._rules
        score = 5.0
        sanskrit = literary.get("sanskrit_alankar", {})
        rasa = literary.get("rasa", {})
        alankar_count = sum(len(v) for v in sanskrit.values()) if isinstance(sanskrit, dict) else 0
        rasa_strength = sum(rasa.values()) if isinstance(rasa, dict) else 0
        if alankar_count > 5:
            score += 2.0
        elif alankar_count > 0:
            score += 1.0
        if rasa_strength > 0:
            score += 1.0
        return min(10.0, max(1.0, score))

    def _calculate_technical_score(self, quantitative: Dict, linguistic: Dict) -> float:
        """Calculate technical craft score"""
        score = 5.0

        # Adjust based on sentence complexity
        if linguistic.get("syntax", {}).get("clauses", {}).get("has_complex_sentences"):
            score += 1.0

        # Adjust based on sentence variety
        sentence_types = linguistic.get("syntax", {}).get("sentence_types", {})
        min_variety = rules.get("technical_sentence_variety_min") if rules else None
        if min_variety is not None and sum(sentence_types.values()) > int(min_variety):
            score += 0.5

        # Adjust based on morphological complexity
        morph = linguistic.get("morphology", {})
        morph_min = rules.get("technical_morph_complexity_min") if rules else None
        if morph_min is not None and (morph.get("prefix_count", 0) + morph.get("suffix_count", 0) > int(morph_min)):
            score += 0.5

        if not rules:
            return score
        return min(float(rules.get("score_max", 10.0)), max(float(rules.get("score_min", 1.0)), score))

    def _calculate_language_score(self, linguistic: Dict) -> float:
        """Calculate language and diction score"""
        score = 5.0

        # Check for varied vocabulary
        lexical = linguistic.get("semantics", {})
        sem_min = rules.get("language_semantic_density_min") if rules else None
        if sem_min is not None and lexical.get("semantic_density", 0) > float(sem_min):
            score += 1.0

        # Check for rich synonyms
        lex_relations = linguistic.get("lexical_relations", {})
        syn_min = rules.get("language_synonym_min") if rules else None
        if syn_min is not None and len(lex_relations.get("synonyms", {})) > int(syn_min):
            score += 1.0

        if not rules:
            return score
        return min(float(rules.get("score_max", 10.0)), max(float(rules.get("score_min", 1.0)), score))

    def _calculate_imagery_score(self, literary: Dict, linguistic: Dict) -> float:
        """Calculate imagery and voice score"""
        score = 5.0

        # Check for imagery variety
        imagery = literary.get("imagery", {})
        imagery_types = sum(len(v) for v in imagery.values())

        high = rules.get("imagery_types_high") if rules else None
        mid = rules.get("imagery_types_mid") if rules else None
        if high is not None and imagery_types > int(high):
            score += 1.5
        elif mid is not None and imagery_types > int(mid):
            score += 0.5

        # Check for figurative language
        tropes = literary.get("tropes", {})
        tropes_count = sum(len(v) for v in tropes.values())

        th = rules.get("tropes_count_high") if rules else None
        tm = rules.get("tropes_count_mid") if rules else None
        if th is not None and tropes_count > int(th):
            score += 1.5
        elif tm is not None and tropes_count > int(tm):
            score += 0.5

        if not rules:
            return score
        return min(float(rules.get("score_max", 10.0)), max(float(rules.get("score_min", 1.0)), score))

    def _calculate_emotional_score(self, literary: Dict, linguistic: Dict) -> float:
        """Calculate emotional impact score"""
        score = 5.0
        sentiment = linguistic.get("sentiment", {})
        compound = sentiment.get("compound", 0)
        strong = rules.get("compound_strong") if rules else None
        mid = rules.get("compound_mid") if rules else None
        if strong is not None and (compound >= float(strong) or compound <= -float(strong)):
            score += 1.5
        elif mid is not None and (compound >= float(mid) or compound <= -float(mid)):
            score += 0.5

        if not rules:
            return score
        return min(float(rules.get("score_max", 10.0)), max(float(rules.get("score_min", 1.0)), score))

    def _pritchard_scale(self, ratings: Dict[str, float]) -> Dict[str, float]:
        """Pritchard Scale: Greatness = Perfection × Importance."""
        perfection = (
            ratings.get("technical_craft", 5.0)
            + ratings.get("language_diction", 5.0)
            + ratings.get("imagery_voice", 5.0)
        ) / 3.0
        importance = (
            ratings.get("emotional_impact", 5.0)
            + ratings.get("cultural_fidelity", 5.0)
            + ratings.get("originality", 5.0)
        ) / 3.0
        greatness = perfection * importance
        return {
            "perfection": round(perfection, 2),
            "importance": round(importance, 2),
            "greatness": round(greatness, 2),
        }

    def _transaction_value(self, ratings: Dict[str, float], linguistic: Dict) -> Dict[str, float]:
        """Transaction Formula: Value = Text × Reader × Context."""
        text_score = ratings.get("technical_craft", 5.0)
        reader_score = ratings.get("emotional_impact", 5.0)
        context_score = ratings.get("cultural_fidelity", 5.0)
        value = text_score * reader_score * context_score
        return {
            "text": round(text_score, 2),
            "reader": round(reader_score, 2),
            "context": round(context_score, 2),
            "value": round(value, 2),
        }

    def _tp_castt(self, text: str, linguistic: Dict) -> Dict[str, Any]:
        """TP-CASTT analysis (Title, Paraphrase, Connotation, Attitude, Shifts, Title, Theme)."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        title_limit = rules.get("tp_castt_title_preview_chars") if rules else None
        title = lines[0][: int(title_limit)] if lines and title_limit is not None else (lines[0] if lines else "")
        sentences = re.split(r"[.!?।]", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        para_limit = rules.get("tp_castt_paraphrase_sentences") if rules else None
        paraphrase = " ".join(sentences[: int(para_limit)]) if sentences and para_limit is not None else (" ".join(sentences) if sentences else "")

        # Connotation: top content words
        content_words = []
        try:
            import spacy
            nlp = spacy.load("en_core_web_trf")
            doc = nlp(text)
            content_words = [t.lemma_.lower() for t in doc if t.pos_ in {"NOUN","VERB","ADJ","ADV"}]
        except Exception:
            content_words = re.findall(r"[A-Za-z']+", text.lower())
        top_limit = rules.get("tp_castt_top_content_words") if rules else None
        top = [w for w, _ in Counter(content_words).most_common(int(top_limit))] if top_limit is not None else [w for w, _ in Counter(content_words).most_common()]

        # Attitude: sentiment
        sentiment = linguistic.get("sentiment", {})
        attitude = sentiment.get("sentiment_label", "neutral")

        # Shifts: line-level sentiment changes (VADER)
        shifts = []
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            prev = None
            for i, line in enumerate(lines):
                c = analyzer.polarity_scores(line)["compound"]
                shift_threshold = rules.get("tp_castt_shift_threshold") if rules else None
                if shift_threshold is not None and prev is not None and abs(c - prev) >= float(shift_threshold):
                    shifts.append({"line": i + 1, "from": prev, "to": c})
                prev = c
        except Exception:
            shifts = []

        # Title again: overlap with top keywords
        title_keywords = set(re.findall(r"[A-Za-z']+", title.lower()))
        overlap = sorted(list(title_keywords.intersection(top)))

        theme_limit = rules.get("tp_castt_theme_top_k") if rules else None
        theme = " / ".join(top[: int(theme_limit)]) if top and theme_limit is not None else (" / ".join(top) if top else "")

        return {
            "title": title,
            "paraphrase": paraphrase,
            "connotation_keywords": top,
            "attitude": attitude,
            "shifts": shifts,
            "title_again_keywords": overlap,
            "theme": theme,
        }

    def _calculate_originality_score(
        self, quantitative: Dict, linguistic: Dict
    ) -> float:
        """Calculate originality score"""
        score = 5.0

        # Check lexical diversity
        lex = quantitative.get("lexical_metrics", {})
        ttr = lex.get("type_token_ratio", 0)

        ttr_high = rules.get("ttr_high") if rules else None
        ttr_mid = rules.get("ttr_mid") if rules else None
        if ttr_high is not None and ttr > float(ttr_high):
            score += 1.5
        elif ttr_mid is not None and ttr > float(ttr_mid):
            score += 0.5

        if not rules:
            return score
        return min(float(rules.get("score_max", 10.0)), max(float(rules.get("score_min", 1.0)), score))

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
