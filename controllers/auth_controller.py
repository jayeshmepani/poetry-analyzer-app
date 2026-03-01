"""
Auth Controller
Handles user authentication: login, register, logout 
"""

from fastapi import Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from controllers.base_controller import BaseController
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal
from app.models.db_models import User
import hashlib

class AuthController(BaseController):
    """
    Controller for Authentication routes
    """
    def __init__(self, templates: Jinja2Templates):
        super().__init__(templates)

    def _hash_password(self, password: str) -> str:
        """Simple SHA-256 hash (in a massive production app this would use bcrypt)"""
        return hashlib.sha256(password.encode()).hexdigest()

    async def login_view(self, request: Request):
        """GET /login"""
        return self.view("auth/login.html", request)

    async def register_view(self, request: Request):
        """GET /register"""
        return self.view("auth/register.html", request)

    async def login_post(self, request: Request, email: str = Form(...), password: str = Form(...)):
        """POST /login"""
        db = SessionLocal()
        try:
            hashed_pw = self._hash_password(password)
            user = db.query(User).filter(User.email == email, User.password == hashed_pw).first()
            
            if not user:
                return self.view("auth/login.html", request, {"error": "Invalid email or password"})
                
            if user.status == 0:
                return self.view("auth/login.html", request, {"error": "This account has been deactivated (403 Forbidden)"})

            # Create session via Cookie (Simple Monolithic Auth)
            response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
            response.set_cookie(key="auth_uuid", value=user.uuid, httponly=True)
            return response
        except Exception as e:
            return self.view("auth/login.html", request, {"error": str(e)})
        finally:
            db.close()

    async def register_post(self, request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), password_confirm: str = Form(...)):
        """POST /register"""
        if password != password_confirm:
            return self.view("auth/register.html", request, {"error": "Passwords do not match"})
            
        db = SessionLocal()
        try:
            # Check existing
            if db.query(User).filter(User.email == email).first():
                return self.view("auth/register.html", request, {"error": "Email already exists"})
                
            hashed_pw = self._hash_password(password)
            new_user = User(name=name, email=email, password=hashed_pw, role=1, status=1)
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Auto-login
            response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
            response.set_cookie(key="auth_uuid", value=new_user.uuid, httponly=True)
            return response
        except Exception as e:
            db.rollback()
            return self.view("auth/register.html", request, {"error": str(e)})
        finally:
            db.close()

    async def logout(self, request: Request):
        """GET /logout"""
        response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        response.delete_cookie(key="auth_uuid")
        return response
