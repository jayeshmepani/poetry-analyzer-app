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
    from controllers.admin_controller import AdminController
    
    # Initialize controllers
    web = WebController(templates)
    admin = AdminController(templates)
    
    # ==================== HOME & REDIRECTS ====================
    route.redirect('/', '/admin', name='home')
    route.redirect('/analyze', '/admin/analyze', name='analyze_redirect')
    
    # ==================== ADMIN ROUTES ====================
    # Using group prefix like Laravel: Route::group(['prefix' => 'admin'], function...)
    route.group('/admin', lambda r, p: None)  # Group marker
    
    route.get('/admin', admin.dashboard, name='admin.dashboard')
    route.get('/admin/analyze', admin.analyze, name='admin.analyze')
    route.get('/admin/batch', admin.batch, name='admin.batch')
    route.get('/admin/results', admin.results, name='admin.results')
    route.get('/admin/database', admin.database_status, name='admin.database')  # ⭐ NEW
    route.get('/admin/visualize', admin.visualize, name='admin.visualize')
    route.get('/admin/forms', admin.forms, name='admin.forms')
    route.get('/admin/meters', admin.meters, name='admin.meters')
    route.get('/admin/rasas', admin.rasas, name='admin.rasas')
    route.get('/admin/settings', admin.settings, name='admin.settings')
    
    # ==================== API ROUTES (Internal) ====================
    # These are used by AJAX calls from frontend
    route.post('/api/analyze', admin.analyze_post, name='api.analyze')
    route.post('/api/analyze/batch', admin.batch_analyze_post, name='api.analyze.batch')
    route.get('/api/stats', admin.stats, name='api.stats')
    route.get('/api/results', admin.list_results, name='api.results.list')
    route.get('/api/result/{result_id}', admin.get_result, name='api.result.get')
    route.get('/api/visualize/{result_id}', admin.get_visualization, name='api.visualize')
    route.delete('/api/result/{result_id}', admin.delete_result, name='api.result.delete')
    route.post('/api/clear-results', admin.clear_results, name='api.results.clear')
    
    # ⭐ Database API endpoints
    route.get('/api/database/status', admin.database_status_api, name='api.database.status')
    route.post('/api/database/initialize', admin.database_init, name='api.database.init')
    
    # ⭐ Settings API endpoints
    route.get('/api/settings', admin.get_settings, name='api.settings.get')
    route.post('/api/settings', admin.save_settings, name='api.settings.save')
    
    # ==================== REFERENCE ROUTES ====================
    route.get('/api/forms', admin.get_forms, name='api.forms')
    route.get('/api/meters', admin.get_meters, name='api.meters')
    route.get('/api/rasas', admin.get_rasas, name='api.rasas')
    
    return route
