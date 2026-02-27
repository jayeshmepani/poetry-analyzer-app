"""
Web Controller
Handles public/home page routes
"""

from fastapi import Request
from controllers.base_controller import BaseController
from fastapi.templating import Jinja2Templates


class WebController(BaseController):
    """
    Controller for public/web routes
    """
    
    def __init__(self, templates: Jinja2Templates):
        super().__init__(templates)
    
    async def home(self, request: Request):
        """
        Home page
        GET /
        """
        # This is now just a redirect (handled in routes)
        # Kept for backwards compatibility
        return self.redirect('/admin')
