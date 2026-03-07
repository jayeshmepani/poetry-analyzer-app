"""
Named route registry for template helpers.
Provides route(name) indirection for templates and shared UI code.
"""

from typing import Dict, Any


WEB_ROUTE_PATHS: Dict[str, str] = {
    "home": "/",
    "login": "/login",
    "login.post": "/login",
    "register": "/register",
    "register.post": "/register",
    "logout": "/logout",
    "admin.index": "/admin",
    "admin.users.index": "/admin/users",
    "admin.users.data": "/admin/users/data",
    "admin.users.store": "/admin/users",
    "admin.users.destroy_multiple": "/admin/users/delete-multiple",
    "admin.users.edit": "/admin/users/{user_uuid}/edit",
    "admin.users.update": "/admin/users/{user_uuid}",
    "admin.users.destroy": "/admin/users/{user_uuid}",
    "admin.users.toggle_status": "/admin/users/{user_uuid}/toggle",
    "dashboard": "/dashboard",
    "analyze": "/analyze",
    "batch": "/batch",
    "results": "/results",
    "results.detail": "/results/{result_id}",
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
    "data.results.destroy_multiple": "/results-delete-multiple",
    "data.results.clear": "/results-clear",
    "data.constraints.apply": "/constraints-apply",
    "data.theory.recommendations": "/theory-recommendations",
    "data.theory.analyze": "/theory-analyze",
    "data.touchstone.analyze": "/touchstone-analyze",
    "data.performance.analyze": "/performance-analyze",
    "data.versions.generate": "/versions-generate",
    "data.database.status": "/database-status",
    "data.backend.symbols": "/backend-symbols",
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
