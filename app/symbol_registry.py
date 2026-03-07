"""Runtime backend symbol catalog with lazy resolution."""

from importlib import import_module
from typing import Dict, List, Tuple

SymbolSpec = Dict[str, List[str]]

SYMBOL_SPECS: SymbolSpec = {
    "app.database": [
        "set_sqlite_pragma",
        "drop_all_tables",
        "get_database_info",
    ],
    "app.database_verifier": [
        "init_database",
    ],
    "app.models.schemas": [
        "BatchAnalysisInput",
        "ConstraintGenerationInput",
        "TropeInstance",
        "SchemeInstance",
        "ImageryInstance",
        "BatchAnalysisResponse",
        "ConstraintGenerationResponse",
        "HealthResponse",
        "FormsResponse",
        "ErrorDetail",
        "VisualizationData",
        "ScansionVisualization",
        "RasaWheelData",
    ],
    "app.services.analysis": [
        "analyze_batch",
    ],
    "app.services.advanced_analysis": [
        "analyze_with_multiple_methods",
        "AdvancedAnalysisEngine._calculate_emotion_distribution",
    ],
    "app.services.analysis_service": [
        "CompleteAnalysisService.clear_cache",
    ],
    "app.services.competition_rubrics": [
        "analyze_competition_rubrics",
    ],
    "app.services.constraints": [
        "OulipoConstraintEngine.generate_sestina",
    ],
    "app.services.evolutionary": [
        "analyze_evolutionary_fitness",
    ],
    "app.services.literary_devices": [
        "LiteraryDevicesAnalyzer._calculate_rasa_score",
        "analyze_idioms_and_proverbs",
    ],
    "app.services.literary_theory": [
        "CriticismResult",
        "LiteraryTheoryAnalyzer._contains_marker",
        "LiteraryTheoryAnalyzer._count_markers",
    ],
    "app.services.quantitative": [
        "QuantitativeMetricsCalculator.get_all_metrics",
        "QuantitativeMetricsCalculator._calculate_entropy",
        "QuantitativeMetricsCalculator._calculate_character_entropy",
        "QuantitativeMetricsCalculator._calculate_conditional_entropy",
    ],
    "app.services.structural_analysis": [
        "StructuralAnalyzer._has_fibonacci_pattern",
    ],
    "app.services.stylometry": [
        "analyze_stylometry",
    ],
}


def _resolve_attr(module_obj, dotted_attr: str):
    current = module_obj
    for part in dotted_attr.split('.'):
        current = getattr(current, part)
    return current


def get_symbol_registry() -> Tuple[dict, dict]:
    """Return (resolved_registry, failures)."""
    resolved = {}
    failures = {}

    for module_name, names in SYMBOL_SPECS.items():
        module_entries = {}
        module_failures = []
        try:
            module_obj = import_module(module_name)
        except Exception as exc:
            failures[module_name] = [f"module import failed: {exc}"]
            continue

        for symbol_name in names:
            try:
                module_entries[symbol_name] = _resolve_attr(module_obj, symbol_name)
            except Exception as exc:
                module_failures.append(f"{symbol_name}: {exc}")

        if module_entries:
            resolved[module_name] = module_entries
        if module_failures:
            failures[module_name] = module_failures

    return resolved, failures


def summarize_symbol_registry() -> dict:
    resolved, failures = get_symbol_registry()
    return {
        "resolved_groups": {k: len(v) for k, v in resolved.items()},
        "resolved_total_symbols": sum(len(v) for v in resolved.values()),
        "failed_groups": {k: len(v) for k, v in failures.items()},
        "failed_total_symbols": sum(len(v) for v in failures.values()),
    }
