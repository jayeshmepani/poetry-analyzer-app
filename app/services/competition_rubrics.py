"""
Competition Rubrics Module
Standardized competition scoring aggregation:
- Poetry Out Loud (Adapted for text-first analysis)
- Slam Poetry (Emotion, Intensity, Originality)
- 100-Point Academic Rubric

All weights, scales, and text templates are loaded from
data/rules/competition_rubrics_rules.json — no magic numbers.
"""

from typing import Dict, Any
from app.services.rule_loader import _load_json
from pathlib import Path

_RULES_PATH = Path(__file__).parent.parent.parent / "data" / "rules" / "competition_rubrics_rules.json"


class CompetitionRubricsAnalyzer:
    """Aggregates real analysis metrics to emit competition rubric scores."""

    def __init__(self):
        self._rules = _load_json(_RULES_PATH)

    def analyze(self, text: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes pre-calculated metrics (quantitative, prosody, stylometry, etc.)
        and outputs competition rubric approximations using externalized weights.
        """
        rules = self._rules
        slam_scales = rules["scales"]["slam"]
        pol_scales = rules["scales"]["pol"]
        acad_scales = rules["scales"]["academic"]
        weights = rules["weights"]
        descriptions = rules["descriptions"]

        rhyme_score = metrics.get("rhyme_density", 0.0) * 10.0
        readability = metrics.get("readability", 50.0)
        imagery = metrics.get("imagery_score", 0.0) * 10.0
        # Complexity: inverse of readability (harder text = higher complexity signal)
        complexity = min(10.0, max(0.0, (100.0 - readability) / 10.0))

        # ── Slam Poetry ──────────────────────────────────────────────────────────
        # Emotional intensity: blend imagery + sentiment intensity
        slam_emotion = min(
            slam_scales["max_score"],
            imagery * slam_scales["emotion_weight"]
            + metrics.get("sentiment_intensity", 0.0) * 10.0 * slam_scales["sentiment_weight"],
        )
        slam_originality = min(
            slam_scales["max_score"],
            metrics.get("lexical_diversity", 0.0) * slam_scales["originality_multiplier"],
        )
        slam_rhythm = min(
            slam_scales["max_score"],
            metrics.get("metrical_regularity", 0.0) * slam_scales["rhythm_multiplier"],
        )
        total_slam = round((slam_emotion + slam_originality + slam_rhythm) / 3.0, 1)

        # ── Poetry Out Loud (text-adapted) ───────────────────────────────────────
        pol_voice = min(
            pol_scales["max_score"],
            rhyme_score * pol_scales["voice_rhyme_weight"]
            + slam_rhythm * pol_scales["voice_rhythm_weight"],
        )
        pol_understanding = min(
            pol_scales["max_score"],
            complexity * pol_scales["understanding_multiplier"],
        )
        total_pol = round((pol_voice + pol_understanding) / 2.0, 1)

        # ── 100-Point Academic Rubric ─────────────────────────────────────────────
        # Structure (max 20): rhythmic + rhyme coherence
        acad_structure = min(
            acad_scales["max_structure"],
            (slam_rhythm + rhyme_score) * acad_scales["structure_scale"],
        )
        # Vocabulary (max 20): lexical originality
        acad_vocab = min(
            acad_scales["max_vocab"],
            (slam_originality / slam_scales["max_score"]) * acad_scales["max_vocab"],
        )
        # Theme/Content (max 30): thematic depth signal
        acad_theme = min(
            acad_scales["max_theme"],
            metrics.get("thematic_depth", 0.0) * acad_scales["max_theme"],
        )
        # Originality (max 30): lexical diversity
        acad_original = min(
            acad_scales["max_original"],
            (slam_originality / slam_scales["max_score"]) * acad_scales["max_original"],
        )
        total_acad = round(acad_structure + acad_vocab + acad_theme + acad_original)

        return {
            "slam_poetry": {
                "score_out_of_10": total_slam,
                "breakdown": {
                    "emotional_intensity": round(slam_emotion, 1),
                    "originality_impact": round(slam_originality, 1),
                    "rhythmic_drive": round(slam_rhythm, 1),
                },
                "analysis": descriptions["slam"],
            },
            "poetry_out_loud_adapted": {
                "score_out_of_10": total_pol,
                "breakdown": {
                    "voice_and_articulation_potential": round(pol_voice, 1),
                    "evidence_of_complexity": round(pol_understanding, 1),
                },
                "analysis": descriptions["pol"],
            },
            "academic_100_point": {
                "score_out_of_100": total_acad,
                "breakdown": {
                    "structure_form": round(acad_structure, 1),
                    "vocabulary_diction": round(acad_vocab, 1),
                    "theme_content": round(acad_theme, 1),
                    "originality": round(acad_original, 1),
                },
                "analysis": descriptions["academic"],
            },
        }


def analyze_competition_rubrics(text: str, aggregated_metrics: Dict[str, Any]) -> Dict[str, Any]:
    analyzer = CompetitionRubricsAnalyzer()
    return analyzer.analyze(text, aggregated_metrics)
