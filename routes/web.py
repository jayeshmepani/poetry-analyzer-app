"""
Web Routes Configuration
Laravel-style routing for Poetry Analyzer App
All routes are defined here and automatically registered
"""

from typing import Callable, Dict, Any, List
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path


class Route:
    """
    Laravel-style Route class
    Usage: Route.get('/path', controller_method)
    """
    
    def __init__(self, app: FastAPI, templates: Jinja2Templates):
        self.app = app
        self.templates = templates
        self.routes: List[Dict[str, Any]] = []
    
    def get(self, path: str, endpoint: Callable, name: str = None):
        """Register GET route"""
        self.routes.append({
            'method': 'GET',
            'path': path,
            'endpoint': endpoint,
            'name': name or endpoint.__name__
        })
        self.app.get(path, response_class=HTMLResponse, name=name)(endpoint)
        return self
    
    def post(self, path: str, endpoint: Callable, name: str = None):
        """Register POST route"""
        self.routes.append({
            'method': 'POST',
            'path': path,
            'endpoint': endpoint,
            'name': name or endpoint.__name__
        })
        self.app.post(path, name=name)(endpoint)
        return self
    
    def delete(self, path: str, endpoint: Callable, name: str = None):
        """Register DELETE route"""
        self.routes.append({
            'method': 'DELETE',
            'path': path,
            'endpoint': endpoint,
            'name': name or endpoint.__name__
        })
        self.app.delete(path, name=name)(endpoint)
        return self
    
    def redirect(self, path: str, to: str, name: str = None):
        """Register redirect route"""
        def redirect_endpoint(request: Request):
            return RedirectResponse(url=to)
        
        self.routes.append({
            'method': 'GET',
            'path': path,
            'endpoint': redirect_endpoint,
            'name': name or f'redirect_{path.replace("/", "_")}',
            'type': 'redirect',
            'to': to
        })
        self.app.get(path, response_class=RedirectResponse, name=name)(redirect_endpoint)
        return self
    
    def view(self, path: str, template: str, data: Dict[str, Any] = None, name: str = None):
        """Register view route (direct template rendering)"""
        def view_endpoint(request: Request):
            return self.templates.TemplateResponse(template, {
                "request": request,
                **(data or {})
            })
        
        self.routes.append({
            'method': 'GET',
            'path': path,
            'endpoint': view_endpoint,
            'name': name or template.replace('.', '_').replace('/', '_'),
            'type': 'view',
            'template': template
        })
        self.app.get(path, response_class=HTMLResponse, name=name)(view_endpoint)
        return self
    
    def group(self, prefix: str, callback: Callable):
        """Create route group with prefix (like Laravel Route::group)"""
        callback(self, prefix)
        return self
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all registered routes"""
        return self.routes


def register_web_routes(app: FastAPI, templates: Jinja2Templates):
    """
    Register all web routes
    This is the main entry point for route registration
    """
    route = Route(app, templates)
    
    # Import controllers
    from controllers.web_controller import WebController
    from controllers.workspace_controller import WorkspaceController
    
    # Initialize controllers
    web = WebController(templates)
    workspace = WorkspaceController(templates)
    
    # ==================== PAGE ROUTES ====================
    route.redirect('/', '/dashboard', name='home')

    route.get('/dashboard', workspace.dashboard, name='dashboard')
    route.get('/analyze', workspace.analyze, name='analyze')
    route.get('/batch', workspace.batch, name='batch')
    route.get('/results', workspace.results, name='results')
    route.get('/database', workspace.database_status, name='database')
    route.get('/visualize', workspace.visualize, name='visualize')
    route.get('/forms', workspace.forms, name='forms')
    route.get('/meters', workspace.meters, name='meters')
    route.get('/rasas', workspace.rasas, name='rasas')
    route.get('/settings', workspace.settings, name='settings')
    route.get('/theory', workspace.theory, name='theory')
    route.get('/touchstone', workspace.touchstone, name='touchstone')
    route.get('/constraints', workspace.constraints, name='constraints')
    route.get('/performance', workspace.performance, name='performance')
    route.get('/rubrics', workspace.rubrics, name='rubrics')
    route.get('/comparator', workspace.comparator, name='comparator')

    # ==================== API ROUTES (Internal) ====================
    # These are used by AJAX calls from frontend
    route.post('/api/analyze', workspace.analyze_post, name='api.analyze')
    route.post('/api/analyze/batch', workspace.batch_analyze_post, name='api.analyze.batch')
    route.get('/api/stats', workspace.stats, name='api.stats')
    route.get('/api/results', workspace.list_results, name='api.results.list')
    route.get('/api/result/{result_id}', workspace.get_result, name='api.result.get')
    route.get('/api/visualize/{result_id}', workspace.get_visualization, name='api.visualize')
    route.delete('/api/result/{result_id}', workspace.delete_result, name='api.result.delete')
    route.post('/api/clear-results', workspace.clear_results, name='api.results.clear')
    
    # ⭐ Advanced API endpoints
    route.post('/api/constraints/apply', workspace.apply_constraint_api, name='api.constraints.apply')
    route.get('/api/theory/recommendations', workspace.get_theory_recommendations, name='api.theory.recommendations')
    route.post('/api/analysis/theory', workspace.analyze_with_theory_api, name='api.theory.analyze')
    route.post('/api/analysis/touchstone', workspace.analyze_touchstone_api, name='api.touchstone.analyze')
    route.post('/api/analysis/performance', workspace.analyze_performance_api, name='api.performance.analyze')
    route.post('/api/analysis/versions', workspace.generate_versions_api, name='api.versions.generate')
    
    # ⭐ Database API endpoints
    route.get('/api/database/status', workspace.database_status_api, name='api.database.status')
    route.post('/api/database/initialize', workspace.database_init, name='api.database.init')
    
    # ⭐ Settings API endpoints
    route.get('/api/settings', workspace.get_settings, name='api.settings.get')
    route.post('/api/settings', workspace.save_settings, name='api.settings.save')
    
    # ==================== REFERENCE ROUTES ====================
    route.get('/api/forms', workspace.get_forms, name='api.forms')
    route.get('/api/meters', workspace.get_meters, name='api.meters')
    route.get('/api/rasas', workspace.get_rasas, name='api.rasas')
    
    return route
