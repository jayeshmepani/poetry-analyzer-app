"""
Ultimate Literary & Linguistic Master System
Structured MVC Architecture

Directory Structure:
├── routes/          - All route definitions
│   └── web.py       - Web routes
├── controllers/     - Request handlers
│   ├── BaseController.py
│   ├── WorkspaceController.py
│   └── WebController.py
├── middleware/      - HTTP middleware
├── config/          - Configuration files
├── app/             - Application logic
│   ├── models/      - Database models
│   ├── services/    - Business logic
│   └── database.py  - DB connection
├── templates/       - Views
└── static/          - Assets
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import logging

from app.config import settings
from app.database import init_db
from app.route_registry import route_url, WEB_ROUTE_PATHS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.version,
    description="Comprehensive literary and poetry analysis system",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals["route"] = route_url
templates.env.globals["app_routes"] = WEB_ROUTE_PATHS

# Mount static files
static_path = BASE_DIR / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# ==================== ROUTE REGISTRATION ====================
# All routes are defined in routes/web.py
# Like: Route::group([], function() { require base_path('routes/web.php'); });

from routes.web import register_web_routes

# Register all web routes
route_manager = register_web_routes(app, templates)

# Ensure the database schema matches the current models on startup/import.
init_db()

logger.info(f"✅ Registered {len(route_manager.all())} web routes")

# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return templates.TemplateResponse(
        "errors/404.html" if (BASE_DIR / "templates" / "errors" / "404.html").exists() else "workspace/dashboard.html",
        {"request": request},
        status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    return templates.TemplateResponse(
        "errors/500.html" if (BASE_DIR / "templates" / "errors" / "500.html").exists() else "workspace/dashboard.html",
        {"request": request},
        status_code=500
    )


# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"🚀 Starting {settings.app.app_name} v{settings.app.version}")
    logger.info(f"📦 Total routes registered: {len(route_manager.all())}")
    
    # Log all registered routes (like `php artisan route:list`)
    logger.info("📍 Registered routes:")
    for route in route_manager.all():
        logger.info(f"   {route['method']:6} {route['path']:30} → {route['name']}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down application...")


# ==================== HEALTH CHECK ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app.version,
        "app": settings.app.app_name
    }
