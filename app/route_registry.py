"""
Named route registry for template helpers.
Provides Laravel-style route(name) indirection for templates and shared UI code.
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
    "api.analyze": "/api/analyze",
    "api.analyze.batch": "/api/analyze/batch",
    "api.stats": "/api/stats",
    "api.results.list": "/api/results",
    "api.result.get": "/api/result/{result_id}",
    "api.visualize": "/api/visualize/{result_id}",
    "api.result.delete": "/api/result/{result_id}",
    "api.results.clear": "/api/clear-results",
    "api.constraints.apply": "/api/constraints/apply",
    "api.theory.recommendations": "/api/theory/recommendations",
    "api.theory.analyze": "/api/analysis/theory",
    "api.touchstone.analyze": "/api/analysis/touchstone",
    "api.performance.analyze": "/api/analysis/performance",
    "api.versions.generate": "/api/analysis/versions",
    "api.database.status": "/api/database/status",
    "api.database.init": "/api/database/initialize",
    "api.settings.get": "/api/settings",
    "api.settings.save": "/api/settings",
    "api.forms": "/api/forms",
    "api.meters": "/api/meters",
    "api.rasas": "/api/rasas",
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
