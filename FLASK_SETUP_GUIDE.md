# Flask Application Setup Guide

## Overview

The Poetry Analyzer application now supports **both FastAPI and Flask** web frameworks. Both versions are fully synchronized and share the same database, models, and analysis services. You can choose whichever framework you prefer.

---

## Quick Start

### Option 1: FastAPI (Recommended - Default)

```bash
# Using the run script
./run.sh --framework fastapi --port 8000

# Or directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Access:**
- Web Interface: http://localhost:8000/admin
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

### Option 2: Flask (Alternative)

```bash
# Using the run script
./run.sh --framework flask --port 9000

# Or directly
python flask_app.py --port 9000 --debug
```

**Access:**
- Web Interface: http://localhost:9000/admin
- Health: http://localhost:9000/health

---

## Framework Comparison

Both frameworks now provide identical functionality:
- ✅ Shared SQLite/PostgreSQL/MySQL database
- ✅ Shared SQLAlchemy models (`AnalysisResult`, `UserSettings`)
- ✅ Shared `CompleteAnalysisService`
- ✅ Shared Frontend templates & assets
- ✅ Identical API response structures

---

## Installation

### FastAPI Dependencies

```bash
pip install fastapi uvicorn[standard] python-multipart jinja2
```

### Flask Dependencies

```bash
pip install flask flask-cors
```

### All Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

### Environment Variables

```bash
# Choose framework
export FRAMEWORK=fastapi  # or flask

# Server settings
export HOST=0.0.0.0
export PORT=9000
export DEBUG=true

# Database
export DATABASE_URL="sqlite:///./poetry_analyzer.db"
```

### Using .env File

Create `.env` file:

```env
# Framework
FRAMEWORK=fastapi

# Server
HOST=0.0.0.0
PORT=9000
DEBUG=true

# Database
DATABASE_URL="sqlite:///./poetry_analyzer.db"
```

---

## Running the Application

### Method 1: Run Script (Recommended)

```bash
# Make executable
chmod +x run.sh

# Run with defaults
./run.sh

# Run with options
./run.sh --framework flask --port 9000 --debug

# Show help
./run.sh --help
```

### Method 2: Direct Command

**FastAPI:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

**Flask:**
```bash
python flask_app.py
```

### Method 3: Production Server

**FastAPI (with Gunicorn):**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:9000
```

**Flask (with Gunicorn):**
```bash
gunicorn flask_app:app -w 4 --bind 0.0.0.0:9000
```

---

## API Endpoints

Both frameworks support the same API endpoints:

### Analysis

```bash
# POST /api/analyze
curl -X POST http://localhost:9000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Poem",
    "text": "Roses are red\nViolets are blue",
    "language": "en",
    "strictness": 7
  }'
```

### Results

```bash
# GET /api/results
curl http://localhost:9000/api/results

# GET /api/result/{id}
curl http://localhost:9000/api/result/UUID_HERE

# DELETE /api/result/{id}
curl -X DELETE http://localhost:9000/api/result/UUID_HERE
```

### Statistics

```bash
# GET /api/stats
curl http://localhost:9000/api/stats
```

### Reference Data

```bash
# GET /api/forms
curl http://localhost:9000/api/forms

# GET /api/meters
curl http://localhost:9000/api/meters

# GET /api/rasas
curl http://localhost:9000/api/rasas
```

---

## Web Interface Routes

Both frameworks serve the same web interface:

- `/admin` - Dashboard
- `/admin/analyze` - Analysis form
- `/admin/results` - Results history
- `/admin/batch` - Batch analysis
- `/admin/forms` - Poetic forms reference
- `/admin/meters` - Metrical patterns
- `/admin/rasas` - Navarasa reference
- `/admin/settings` - Settings
- `/admin/database` - Database status
- `/admin/visualize` - Visualization

---

## Database Integration

Both frameworks use the same database layer:

```python
from app.database import SessionLocal, get_db
from app.models.db_models import AnalysisResult

# Get database session
db = SessionLocal()

# Query data
results = db.query(AnalysisResult).all()

# Close connection
db.close()
```

### Initialize Database

```bash
python init_db.py
```

---

## Production Deployment

### FastAPI (Recommended for Production)

**Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
```

**Systemd Service:**
```ini
[Unit]
Description=Poetry Analyzer (FastAPI)
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/poetry_analyzer_app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 9000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Flask

**Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "flask_app:app", "-w", "4", "--bind", "0.0.0.0:9000"]
```

**Systemd Service:**
```ini
[Unit]
Description=Poetry Analyzer (Flask)
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/poetry_analyzer_app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn flask_app:app -w 4 --bind 0.0.0.0:9000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Testing

### Health Check

```bash
# FastAPI
curl http://localhost:9000/health

# Flask
curl http://localhost:9000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "framework": "FastAPI"  // or "Flask"
}
```

### API Test

```bash
# Test analysis
curl -X POST http://localhost:9000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Test poem", "language": "en"}'
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 9000
lsof -i :9000

# Kill process
kill -9 <PID>

# Or use different port
./run.sh --port 9001
```

### Module Not Found

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors

```bash
# Reset database
rm poetry_analyzer.db
python init_db.py
```

### CORS Issues

Make sure CORS is enabled:

**FastAPI:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Flask:**
```python
from flask_cors import CORS
CORS(app)
```

---

## Switching Between Frameworks

### Temporary (Command Line)

```bash
# Use FastAPI for this session
./run.sh --framework fastapi

# Use Flask for this session
./run.sh --framework flask
```

### Permanent (.env file)

Edit `.env`:

```env
# FastAPI
FRAMEWORK=fastapi

# OR Flask
FRAMEWORK=flask
```

---

## Performance Comparison

### FastAPI
- ⚡ **10x faster** than Flask for API endpoints
- ⚡ **Async support** for concurrent requests
- ⚡ **Auto-validation** with Pydantic
- ⚡ **Auto-docs** with Swagger UI

### Flask
- 🐍 **Simpler** for beginners
- 🐍 **More extensions** available
- 🐍 **Better for** simple websites
- 🐍 **Easier debugging**

---

## Recommendation

**Use FastAPI if:**
- ✅ Building APIs
- ✅ Need high performance
- ✅ Want auto-generated docs
- ✅ Working with async code
- ✅ Need type validation

**Use Flask if:**
- ✅ Building simple websites
- ✅ Prefer synchronous code
- ✅ Need specific Flask extensions
- ✅ More comfortable with Flask
- ✅ Legacy system integration

**Default:** FastAPI (recommended for this application)

---

## Additional Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Flask Docs:** https://flask.palletsprojects.com/
- **Run Script:** `./run.sh --help`
- **Database Guide:** `DATABASE_SETUP_GUIDE.md`

---

## Support

For issues:
1. Check logs in console
2. Verify dependencies: `pip list`
3. Test health endpoint: `curl http://localhost:9000/health`
4. Check database: `python init_db.py`
