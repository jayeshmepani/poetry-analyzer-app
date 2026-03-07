"""
Web Routes Configuration
Routing for Poetry Analyzer App
All routes are defined here and automatically registered
"""

from typing import Callable, Dict, Any, List
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.database import SessionLocal
from app.models.db_models import User

def get_current_user(request: Request):
    """
    Dependency to strictly enforce Session Authentication
    Requires an active cookie and validates the user status
    """
    auth_uuid = request.cookies.get("auth_uuid")
    if not auth_uuid:
        raise HTTPException(
            status_code=302, 
            detail="Not authenticated",
            headers={"Location": "/login"}
        )
        
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.uuid == auth_uuid).first()
        if not user:
            raise HTTPException(
                status_code=302, 
                detail="Invalid session",
                headers={"Location": "/login"}
            )
        if user.status == 0:
            raise HTTPException(status_code=403, detail="Account deactivated")
        return user
    finally:
        db.close()


class Route:
    """
    Route class
    Usage: Route.get('/path', controller_method)
    """
    
    def __init__(self, app: FastAPI, templates: Jinja2Templates):
        self.app = app
        self.templates = templates
        self.routes: List[Dict[str, Any]] = []
    
    def get(self, path: str, endpoint: Callable, name: str = None, protected: bool = False):
        """Register GET route"""
        self.routes.append({
            'method': 'GET',
            'path': path,
            'endpoint': endpoint,
            'name': name or endpoint.__name__,
            'protected': protected
        })
        
        dependencies = [Depends(get_current_user)] if protected else []
        self.app.get(path, response_class=HTMLResponse, name=name, dependencies=dependencies)(endpoint)
        return self
    
    def post(self, path: str, endpoint: Callable, name: str = None, protected: bool = False):
        """Register POST route"""
        self.routes.append({
            'method': 'POST',
            'path': path,
            'endpoint': endpoint,
            'name': name or endpoint.__name__,
            'protected': protected
        })
        
        dependencies = [Depends(get_current_user)] if protected else []
        self.app.post(path, name=name, dependencies=dependencies)(endpoint)
        return self
    
    def delete(self, path: str, endpoint: Callable, name: str = None, protected: bool = False):
        """Register DELETE route"""
        self.routes.append({
            'method': 'DELETE',
            'path': path,
            'endpoint': endpoint,
            'name': name or endpoint.__name__,
            'protected': protected
        })
        
        dependencies = [Depends(get_current_user)] if protected else []
        self.app.delete(path, name=name, dependencies=dependencies)(endpoint)
        return self

    def put(self, path: str, endpoint: Callable, name: str = None, protected: bool = False):
        """Register PUT route"""
        self.routes.append({
            'method': 'PUT',
            'path': path,
            'endpoint': endpoint,
            'name': name or endpoint.__name__,
            'protected': protected
        })
        dependencies = [Depends(get_current_user)] if protected else []
        self.app.put(path, name=name, dependencies=dependencies)(endpoint)
        return self

    def patch(self, path: str, endpoint: Callable, name: str = None, protected: bool = False):
        """Register PATCH route"""
        self.routes.append({
            'method': 'PATCH',
            'path': path,
            'endpoint': endpoint,
            'name': name or endpoint.__name__,
            'protected': protected
        })
        dependencies = [Depends(get_current_user)] if protected else []
        self.app.patch(path, name=name, dependencies=dependencies)(endpoint)
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
        """Create route group with prefix"""
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
    from controllers.auth_controller import AuthController
    from controllers.admin_controller import AdminController
    
    # Initialize controllers
    web = WebController(templates)
    workspace = WorkspaceController(templates)
    auth = AuthController(templates)
    admin = AdminController(templates)
    
    # ==================== ADMIN ROUTES (ROLE 0 ONLY) ====================
    route.get('/admin', admin.index, name='admin.index')
    route.get('/admin/users', admin.index, name='admin.users.index')
    route.get('/admin/users/data', admin.data, name='admin.users.data')
    route.post('/admin/users', admin.store, name='admin.users.store')
    route.post('/admin/users/delete-multiple', admin.destroy_multiple, name='admin.users.destroy_multiple')
    route.get('/admin/users/{user_uuid}/edit', admin.edit, name='admin.users.edit')
    route.put('/admin/users/{user_uuid}', admin.update, name='admin.users.update')
    route.delete('/admin/users/{user_uuid}', admin.destroy, name='admin.users.destroy')
    route.patch('/admin/users/{user_uuid}/toggle', admin.toggle_status, name='admin.users.toggle_status')
    
    # ==================== AUTH ROUTES ====================
    route.get('/login', auth.login_view, name='login')
    route.post('/login', auth.login_post, name='login.post')
    route.get('/register', auth.register_view, name='register')
    route.post('/register', auth.register_post, name='register.post')
    route.get('/logout', auth.logout, name='logout')
    
    # ==================== PUBLIC ROUTES ====================
    route.get('/', web.home, name='home')

    # ==================== PROTECTED WORKSPACE ROUTES ====================
    # All of these routes require get_current_user
    route.get('/dashboard', workspace.dashboard, name='dashboard', protected=True)
    route.get('/analyze', workspace.analyze, name='analyze', protected=True)
    route.get('/batch', workspace.batch, name='batch', protected=True)
    route.get('/results', workspace.results, name='results', protected=True)
    route.get('/results/{result_id}', workspace.result_report, name='results.detail', protected=True)
    route.get('/database', workspace.database_status, name='database', protected=True)
    route.get('/forms', workspace.forms, name='forms', protected=True)
    route.get('/meters', workspace.meters, name='meters', protected=True)
    route.get('/rasas', workspace.rasas, name='rasas', protected=True)
    route.get('/settings', workspace.settings, name='settings', protected=True)
    route.get('/theory', workspace.theory, name='theory', protected=True)
    route.get('/touchstone', workspace.touchstone, name='touchstone', protected=True)
    route.get('/constraints', workspace.constraints, name='constraints', protected=True)
    route.get('/performance', workspace.performance, name='performance', protected=True)
    route.get('/rubrics', workspace.rubrics, name='rubrics', protected=True)
    route.get('/comparator', workspace.comparator, name='comparator', protected=True)

    # ==================== DATA ROUTES (AJAX) ====================
    # These are used by AJAX calls from frontend but operate monolithically
    route.post('/analyze-run', workspace.analyze_post, name='data.analyze', protected=True)
    route.post('/batch-run', workspace.batch_analyze_post, name='data.analyze.batch', protected=True)
    route.get('/stats', workspace.stats, name='data.stats', protected=True)
    route.get('/results-data', workspace.list_results, name='data.results.list', protected=True)
    route.get('/result/{result_id}', workspace.get_result, name='data.result.get', protected=True)
    route.delete('/result/{result_id}', workspace.delete_result, name='data.result.delete', protected=True)
    route.post('/results-delete-multiple', workspace.delete_results_multiple, name='data.results.destroy_multiple', protected=True)
    route.post('/results-clear', workspace.clear_results, name='data.results.clear', protected=True)
    
    # ⭐ Advanced Tools
    route.post('/constraints-apply', workspace.apply_constraint_api, name='data.constraints.apply', protected=True)
    route.get('/theory-recommendations', workspace.get_theory_recommendations, name='data.theory.recommendations', protected=True)
    route.post('/theory-analyze', workspace.analyze_with_theory_api, name='data.theory.analyze', protected=True)
    route.post('/touchstone-analyze', workspace.analyze_touchstone_api, name='data.touchstone.analyze', protected=True)
    route.post('/performance-analyze', workspace.analyze_performance_api, name='data.performance.analyze', protected=True)
    route.post('/versions-generate', workspace.generate_versions_api, name='data.versions.generate', protected=True)
    
    # ⭐ Database 
    route.get('/database-status', workspace.database_status_api, name='data.database.status', protected=True)
    route.get('/backend-symbols', workspace.backend_symbols_api, name='data.backend.symbols', protected=True)
    route.post('/database-init', workspace.database_init, name='data.database.init', protected=True)
    
    # ⭐ Settings 
    route.get('/settings-data', workspace.get_settings, name='data.settings.get', protected=True)
    route.post('/settings-data', workspace.save_settings, name='data.settings.save', protected=True)
    
    # ==================== REFERENCE ROUTES ====================
    route.get('/forms-data', workspace.get_forms, name='data.forms', protected=True)
    route.get('/meters-data', workspace.get_meters, name='data.meters', protected=True)
    route.get('/rasas-data', workspace.get_rasas, name='data.rasas', protected=True)

    return route
