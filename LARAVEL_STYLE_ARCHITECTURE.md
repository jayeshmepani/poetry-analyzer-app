# Laravel-Style MVC Architecture

## 📁 Complete Restructure

Your Poetry Analyzer App now has a **proper Laravel-style structure** with centralized routing, controllers, and MVC architecture.

---

## 🎯 Key Features

### 1. **Centralized Routing** (Like `routes/web.php`)
All routes are defined in **`routes/web.py`** - one place to manage all URLs!

```python
# routes/web.py
route.get('/admin', admin.dashboard, name='admin.dashboard')
route.get('/admin/analyze', admin.analyze, name='admin.analyze')
```

### 2. **Controllers** (Like `App/Http/Controllers/`)
All business logic in controllers, organized by domain:

```
controllers/
├── BaseController.py       # Base controller (like Laravel's Controller)
├── AdminController.py      # Admin dashboard logic
└── WebController.py        # Public pages
```

### 3. **Route Names** (Like `Route::name()`)
Every route has a name for easy reference:

```python
# Define
route.get('/admin', admin.dashboard, name='admin.dashboard')

# Use in templates (future)
# redirect()->route('admin.dashboard')
```

### 4. **Route Groups** (Like `Route::group()`)
Prefix routes easily:

```python
route.group('/admin', lambda r, p: None)  # Group marker
```

---

## 📂 New Directory Structure

```
poetry_analyzer_app/
├── routes/                      # ⭐ NEW - Like Laravel routes/
│   └── web.py                   # All web routes (like routes/web.php)
│
├── controllers/                 # ⭐ NEW - Like Laravel app/Http/Controllers/
│   ├── __init__.py
│   ├── base_controller.py       # Base controller
│   ├── admin_controller.py      # Admin logic
│   └── web_controller.py        # Web logic
│
├── middleware/                  # ⭐ NEW - Like Laravel app/Http/Middleware/
│   └── (future middleware)
│
├── config/                      # ⭐ NEW - Like Laravel config/
│   └── (future configs)
│
├── app/                         # Application core
│   ├── main.py                  # Entry point (like bootstrap/app.php)
│   ├── models/                  # Database models (like app/Models/)
│   ├── services/                # Business logic (like app/Services/)
│   └── database.py              # DB connection
│
├── templates/                   # Views (like resources/views/)
│   └── admin/                   # Admin views
│
└── static/                      # Assets (like public/)
```

---

## 🔧 How It Works

### 1. **Route Registration** (`routes/web.py`)

```python
from typing import Callable, Dict, Any

class Route:
    """Laravel-style Route class"""
    
    def get(self, path: str, endpoint: Callable, name: str = None):
        """Register GET route"""
        self.app.get(path, response_class=HTMLResponse, name=name)(endpoint)
        return self
    
    def post(self, path: str, endpoint: Callable, name: str = None):
        """Register POST route"""
        self.app.post(path, name=name)(endpoint)
        return self
    
    def redirect(self, path: str, to: str, name: str = None):
        """Register redirect route"""
        # Like: Route::redirect('/old', '/new')
        pass
    
    def view(self, path: str, template: str, name: str = None):
        """Direct template rendering"""
        # Like: Route::view('/about', 'about')
        pass
```

### 2. **Controllers** (`controllers/admin_controller.py`)

```python
class AdminController(BaseController):
    """Like Laravel's AdminController"""
    
    async def dashboard(self, request: Request):
        """GET /admin"""
        return self.view('admin/dashboard.html', request)
    
    async def analyze(self, request: Request):
        """GET /admin/analyze"""
        return self.view('admin/analyze.html', request)
```

### 3. **Main App** (`app/main.py`)

```python
# Like bootstrap/app.php in Laravel
from routes.web import register_web_routes

# Register all routes
route_manager = register_web_routes(app, templates)

# That's it! All routes auto-registered
```

---

## 📝 Usage Examples

### Adding a New Route

**Step 1: Add to `routes/web.py`**
```python
route.get('/admin/new-page', admin.new_page, name='admin.new_page')
```

**Step 2: Add Controller Method**
```python
# controllers/admin_controller.py
async def new_page(self, request: Request):
    return self.view('admin/new_page.html', request)
```

**Step 3: Create Template**
```html
<!-- templates/admin/new_page.html -->
{% extends "admin/base_admin.html" %}
{% block content %}
<h1>New Page</h1>
{% endblock %}
```

**Done!** Route is live at `/admin/new-page`

---

### Changing URLs (Centralized!)

Want to change `/admin` to `/dashboard`?

**Just update ONE file** - `routes/web.py`:

```python
# Before
route.get('/admin', admin.dashboard, name='admin.dashboard')

# After
route.get('/dashboard', admin.dashboard, name='admin.dashboard')
```

✅ **Automatically updates everywhere!**
- No need to change templates
- No need to change controllers
- No need to change links

---

## 🎯 Benefits Over Old Structure

### Before (Scattered Routes)
```python
# app/main.py - 500+ lines
@app.get("/admin")
async def route1(): ...

@app.get("/admin/analyze")
async def route2(): ...

# More routes scattered everywhere...
```

❌ Hard to manage
❌ Duplicated code
❌ No organization
❌ URL changes in multiple places

### After (Laravel-Style)
```python
# routes/web.py - Clean, organized
route.get('/admin', admin.dashboard, name='admin.dashboard')
route.get('/admin/analyze', admin.analyze, name='admin.analyze')

# controllers/admin_controller.py
class AdminController:
    async def dashboard(self, request): ...
    async def analyze(self, request): ...
```

✅ **Centralized** - All routes in one file
✅ **Organized** - MVC pattern
✅ **Maintainable** - Change URL once
✅ **Scalable** - Easy to add more routes
✅ **Familiar** - Just like Laravel!

---

## 📊 Current Routes

```
GET    /                          → redirect to /admin
GET    /analyze                   → redirect to /admin/analyze
GET    /admin                     → admin.dashboard
GET    /admin/analyze             → admin.analyze
GET    /admin/batch               → admin.batch
GET    /admin/results             → admin.results
GET    /admin/forms               → admin.forms
GET    /admin/meters              → admin.meters
GET    /admin/rasas               → admin.rasas
GET    /admin/settings            → admin.settings
POST   /api/analyze               → api.analyze
POST   /api/analyze/batch         → api.analyze.batch
GET    /api/stats                 → api.stats
GET    /api/results               → api.results.list
GET    /api/result/{id}           → api.result.get
DELETE /api/result/{id}           → api.result.delete
POST   /api/clear-results         → api.results.clear
GET    /api/forms                 → api.forms
GET    /api/meters                → api.meters
GET    /api/rasas                 → api.rasas
GET    /health                    → health check
```

**Total: 20 web routes**

---

## 🔍 Route Management Commands (Future)

Like Laravel's `php artisan route:list`:

```bash
# List all routes
python -m routes list

# Check route exists
python -m routes check admin.dashboard

# Generate route cache
python -m routes cache
```

---

## 🎨 Template Integration (Future)

Like Laravel's `route()` helper:

```python
# In templates (with future helper)
<a href="{{ route('admin.analyze') }}">Analyze</a>

# In controllers
return redirect()->route('admin.dashboard')

# In Python code
from routes import route
url = route('admin.analyze')  # Returns '/admin/analyze'
```

---

## 🚀 Testing

### Test All Routes

```bash
cd poetry_analyzer_app
source .env/bin/activate
uvicorn app.main:app --reload

# Visit:
http://localhost:9000/admin
http://localhost:9000/admin/analyze
http://localhost:9000/admin/batch
# etc...
```

### Check Route List

```python
from app.main import route_manager

for route in route_manager.all():
    print(f"{route['method']:6} {route['path']:30} → {route['name']}")
```

---

## 📈 Next Steps

1. **Add Middleware** (`middleware/auth.py`, etc.)
2. **Add Form Requests** (like Laravel FormRequest)
3. **Add Route Model Binding** (auto-inject models)
4. **Add API Resource Routes** (if needed later)
5. **Add Route Caching** (for production)

---

## 🎉 Summary

| Feature | Laravel | Your App |
|---------|---------|----------|
| **Routes File** | `routes/web.php` | `routes/web.py` ✅ |
| **Controllers** | `app/Http/Controllers/` | `controllers/` ✅ |
| **Route Names** | `Route::name()` | `name=` parameter ✅ |
| **Route Groups** | `Route::group()` | `route.group()` ✅ |
| **Redirects** | `Route::redirect()` | `route.redirect()` ✅ |
| **View Routes** | `Route::view()` | `route.view()` ✅ |
| **Middleware** | `app/Http/Middleware/` | `middleware/` (ready) ✅ |
| **Base Controller** | `Controller` | `BaseController` ✅ |

**Your app now has Laravel-style organization! 🎉**

---

**Status**: ✅ **COMPLETE**  
**Version**: 3.0.0  
**Architecture**: Laravel-style MVC  
**Last Updated**: February 27, 2026
