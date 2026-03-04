"""
Named route registry for template helpers.
Provides route(name) indirection for templates and shared UI code.
"""

from typing import Dict, Any


WEB_ROUTE_PATHS: Dict[str, str] = {
    "home": "/dashboard",
    "dashboard": "/dashboard",
    "analyze": "/analyze",
    "batch": "/batch",
    "results": "/results",
    "database": "/database",
    "visualize": "/visualize",
    "forms": "/forms",
    "meters": "/meters",
    "rasas": "/rasas",
    "settings": "/settings",
    "theory": "/theory",
    "touchstone": "/touchstone",
    "constraints": "/constraints",
    "performance": "/performance",
    "rubrics": "/rubrics",
    "comparator": "/comparator",
    "data.analyze": "/analyze-run",
    "data.analyze.batch": "/batch-run",
    "data.stats": "/stats",
    "data.results.list": "/results-data",
    "data.result.get": "/result/{result_id}",
    "data.visualize": "/visualize-data/{result_id}",
    "data.result.delete": "/result/{result_id}",
    "data.results.clear": "/results-clear",
    "data.constraints.apply": "/constraints-apply",
    "data.theory.recommendations": "/theory-recommendations",
    "data.theory.analyze": "/theory-analyze",
    "data.touchstone.analyze": "/touchstone-analyze",
    "data.performance.analyze": "/performance-analyze",
    "data.versions.generate": "/versions-generate",
    "data.database.status": "/database-status",
    "data.database.init": "/database-init",
    "data.settings.get": "/settings-data",
    "data.settings.save": "/settings-data",
    "data.forms": "/forms-data",
    "data.meters": "/meters-data",
    "data.rasas": "/rasas-data",
}


def route_url(name: str, **params: Any) -> str:
    """
    Resolve a named route to its URL path.
    Supports simple `{param}` substitution for parameterized routes.
    """
    if name not in WEB_ROUTE_PATHS:
        raise KeyError(f"Unknown route name: {name}")

    path = WEB_ROUTE_PATHS[name]
    if params:
        return path.format(**params)
    return path
