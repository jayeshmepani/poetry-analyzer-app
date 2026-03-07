"""
Evolutionary Algorithms Module for Poetry Evaluation

Measures 'poetic intensity' and structural/semantic fitness using
principles derived from simulated evolutionary fitness landscapes.

All weights and configuration are loaded from
data/rules/competition_rubrics_rules.json — no magic numbers in code.
"""

from typing import Dict, Any
from app.services.rule_loader import _load_json
from pathlib import Path

_RULES_PATH = Path(__file__).parent.parent.parent / "data" / "rules" / "competition_rubrics_rules.json"


class EvolutionaryFitnessAnalyzer:
    """
    Evaluates poem fitness: edit distance to perfect meter,
    structural alignment, and lexical survival score (poetic intensity).
    """

    def __init__(self):
        self._rules = _load_json(_RULES_PATH)

    def analyze(self, text: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates fitness scores based on real aggregated metrics."""
        rules = self._rules
        weights = rules["weights"]
        thresholds = rules["fitness_thresholds"]
        descriptions = rules["descriptions"]

        metrical_regularity = metrics.get("metrical_regularity", 0.0)
        rhyme_density = metrics.get("rhyme_density", 0.0)
        lexical_diversity = metrics.get("lexical_diversity", 0.0)
        imagery_score = metrics.get("imagery_score", 0.0)
        sentiment_intensity = metrics.get("sentiment_intensity", 0.0)

        # 1. Edit distance ratio to perfect meter: fraction of lines deviating from meter
        #    (1.0 - regularity) = proportion still requiring structural edits
        edit_distance_ratio = round(1.0 - metrical_regularity, 3)

        # 2. Poetic Intensity = lexical-imagery-sentiment combinatorial fitness
        poetic_intensity = (
            lexical_diversity * weights["lexical_diversity"]
            + imagery_score * weights["imagery"]
            + sentiment_intensity * weights["sentiment_intensity"]
        )

        # 3. Overall Fitness weighted combination
        overall_fitness = (
            metrical_regularity * weights["structural_alignment"]
            + rhyme_density * weights["rhyme_density"]
            + poetic_intensity * weights["poetic_intensity"]
        )

        # Fitness landscape classification from JSON thresholds
        if overall_fitness > thresholds["high"]:
            fitness_band = "High"
            fitness_desc = descriptions["fitness_high"]
        elif overall_fitness > thresholds["medium"]:
            fitness_band = "Medium"
            fitness_desc = descriptions["fitness_medium"]
        else:
            fitness_band = "Low"
            fitness_desc = descriptions["fitness_low"]

        return {
            "evolutionary_metrics": {
                "overall_fitness_score": round(overall_fitness, 3),
                "poetic_intensity_score": round(poetic_intensity, 3),
                "structural_alignment": round(metrical_regularity, 3),
                "edit_distance_to_perfect_meter": edit_distance_ratio,
                "rhyme_density_contribution": round(rhyme_density * weights["rhyme_density"], 3),
            },
            "interpretation": {
                "fitness_landscape": fitness_band,
                "description": fitness_desc,
            },
        }


def analyze_evolutionary_fitness(text: str, aggregated_metrics: Dict[str, Any]) -> Dict[str, Any]:
    analyzer = EvolutionaryFitnessAnalyzer()
    return analyzer.analyze(text, aggregated_metrics)