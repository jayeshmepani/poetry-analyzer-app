"""
Base Controller
All controllers extend this base class
"""

from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Dict, Any


class BaseController:
    """
    Base controller with common functionality
    """

    def __init__(self, templates: Jinja2Templates):
        self.templates = templates

    def view(self, template_name: str, request: Request, context: Dict[str, Any] = None):
        """
        Render a Jinja2 template
        """
        ctx = {"request": request}
        
        # Inject global authenticated user if present
        if hasattr(request.state, 'user'):
            ctx["user"] = request.state.user
            
        if context:
            ctx.update(context)
        
        return self.templates.TemplateResponse(template_name, ctx)

    def redirect(self, url: str):
        """
        Redirect to another URL
        """
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url=url)

    def json(self, data: dict, status_code: int = 200):
        """
        Return JSON response
        """
        from fastapi.responses import JSONResponse

        return JSONResponse(content=data, status_code=status_code)

    def error(self, message: str, status_code: int = 400):
        """
        Return error response
        """
        from fastapi.responses import JSONResponse

        return JSONResponse(content={"error": message}, status_code=status_code)

    def success(self, data: dict, message: str = None):
        """
        Return success response with data wrapped
        """
        from fastapi.responses import JSONResponse

        response = {"success": True, "data": data or {}}
        if message:
            response["message"] = message
        return JSONResponse(content=response)
