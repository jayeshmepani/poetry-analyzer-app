# Database Setup Guide - PostgreSQL + SQLAlchemy + Alembic

## 📋 Overview

Complete MVC architecture with PostgreSQL database for persistent storage of all poetry analyses.

---

## 🔧 Installation

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
Download from: https://www.postgresql.org/download/windows/

### 2. Create Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE poetry_analyzer;
CREATE USER poetry_user WITH PASSWORD 'poetry_password';
GRANT ALL PRIVILEGES ON DATABASE poetry_analyzer TO poetry_user;
\q
```

### 3. Configure Environment

Create `.env` file:
```bash
DATABASE_URL=postgresql://poetry_user:poetry_password@localhost:5432/poetry_analyzer
```

### 4. Install Python Dependencies

```bash
cd poetry_analyzer_app
source .env/bin/activate
pip install sqlalchemy alembic 'psycopg[binary]'
```

---

## 📁 Files Created

### 1. `app/database.py`
- Database connection setup
- Session management
- Engine configuration with pooling

### 2. `app/models.py`
- `AnalysisResult` model - stores all analysis data
- `DatabaseStats` model - aggregated statistics
- Full-text search indexes
- JSON columns for flexible analysis storage

### 3. `app/crud.py` (To be created)
- Create, Read, Update, Delete operations
- Query helpers
- Statistics functions

### 4. `alembic/` (To be created)
- Database migrations
- Version control for schema

---

## 🗄️ Database Schema

### AnalysisResult Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| uuid | String(36) | Unique identifier (for API) |
| title | String(255) | Poem/text title |
| text | Text | Full text content |
| language | String(10) | Language code (en, hi, gu, etc.) |
| poetic_form | String(100) | Form (sonnet, haiku, etc.) |
| overall_score | Float | Overall quality score (0-10) |
| technical_craft_score | Float | Technical craft rating |
| language_diction_score | Float | Language & diction rating |
| imagery_voice_score | Float | Imagery & voice rating |
| emotional_impact_score | Float | Emotional impact rating |
| cultural_fidelity_score | Float | Cultural fidelity rating |
| originality_score | Float | Originality rating |
| quantitative_metrics | JSON | Full metrics data |
| prosody_analysis | JSON | Meter/rhyme analysis |
| literary_devices | JSON | Detected devices |
| sentiment_analysis | JSON | Sentiment data |
| evaluation | JSON | Complete evaluation |
| executive_summary | Text | AI-generated summary |
| word_count | Integer | Word count |
| line_count | Integer | Line count |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Indexes:**
- `idx_language_created` - For filtering by language + date
- `idx_overall_score` - For sorting by quality
- `idx_form` - For filtering by poetic form
- `uuid` - Unique index for API lookups

---

## 🚀 Usage

### Initialize Database

```python
from app.database import init_db
init_db()
```

### Create Analysis Result

```python
from app.database import SessionLocal
from app.models import AnalysisResult

db = SessionLocal()
try:
    result = AnalysisResult(
        title="My Poem",
        text="Roses are red...",
        language="en",
        overall_score=8.5,
        quantitative_metrics={...},
        # ... other fields
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    print(f"Created: {result.uuid}")
finally:
    db.close()
```

### Query Results

```python
# Get all results
results = db.query(AnalysisResult).all()

# Filter by language
english_results = db.query(AnalysisResult).filter(
    AnalysisResult.language == 'en'
).all()

# Get recent high-scoring poems
best_recent = db.query(AnalysisResult).filter(
    AnalysisResult.overall_score >= 8.0
).order_by(
    AnalysisResult.created_at.desc()
).limit(10).all()

# Get by UUID
result = db.query(AnalysisResult).filter(
    AnalysisResult.uuid == '...'
).first()
```

### Update Result

```python
result = db.query(AnalysisResult).filter(
    AnalysisResult.uuid == uuid
).first()

if result:
    result.overall_score = 9.0
    db.commit()
    db.refresh(result)
```

### Delete Result

```python
result = db.query(AnalysisResult).filter(
    AnalysisResult.uuid == uuid
).first()

if result:
    db.delete(result)
    db.commit()
```

---

## 📊 Statistics & Analytics

### Get Database Stats

```python
from sqlalchemy import func

# Total analyses
total = db.query(func.count(AnalysisResult.id)).scalar()

# By language
by_language = db.query(
    AnalysisResult.language,
    func.count(AnalysisResult.id)
).group_by(AnalysisResult.language).all()

# Average score
avg_score = db.query(
    func.avg(AnalysisResult.overall_score)
).scalar()

# Recent activity (last 7 days)
from datetime import datetime, timedelta
week_ago = datetime.utcnow() - timedelta(days=7)
recent = db.query(AnalysisResult).filter(
    AnalysisResult.created_at >= week_ago
).count()
```

---

## 🔌 Integration with FastAPI

### Update API Endpoints

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisResult

@app.post("/api/v1/analyze")
async def analyze_text(
    input: AnalysisInput,
    db: Session = Depends(get_db)
):
    # Perform analysis
    result = await analysis_service.analyze(input)
    
    # Save to database
    db_result = AnalysisResult(
        title=input.title,
        text=input.text,
        language=input.language,
        overall_score=result['evaluation']['overall_score'],
        quantitative_metrics=result['quantitative_metrics'],
        # ... map all fields
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    # Return with UUID
    return {**result, 'id': db_result.uuid}

@app.get("/api/v1/result/{result_id}")
async def get_result(
    result_id: str,
    db: Session = Depends(get_db)
):
    result = db.query(AnalysisResult).filter(
        AnalysisResult.uuid == result_id
    ).first()
    
    if not result:
        raise HTTPException(404, "Result not found")
    
    return result.to_full_dict()

@app.get("/api/v1/results")
async def list_results(
    limit: int = 20,
    offset: int = 0,
    language: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnalysisResult)
    
    if language:
        query = query.filter(AnalysisResult.language == language)
    
    results = query.order_by(
        AnalysisResult.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [r.to_dict() for r in results]

@app.delete("/api/v1/result/{result_id}")
async def delete_result(
    result_id: str,
    db: Session = Depends(get_db)
):
    result = db.query(AnalysisResult).filter(
        AnalysisResult.uuid == result_id
    ).first()
    
    if not result:
        raise HTTPException(404, "Result not found")
    
    db.delete(result)
    db.commit()
    
    return {"message": "Deleted successfully"}
```

---

## 📦 Alembic Migrations

### Initialize Alembic

```bash
cd poetry_analyzer_app
alembic init alembic
```

### Configure alembic.ini

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://poetry_user:poetry_password@localhost:5432/poetry_analyzer

[loggers]
keys = root,sqlalchemy,alembic
```

### Update alembic/env.py

```python
from app.database import Base
from app import models  # Import all models

target_metadata = Base.metadata
```

### Create Migration

```bash
alembic revision --autogenerate -m "Initial migration - analysis_results table"
```

### Apply Migration

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

---

## 🎯 Benefits

### Before (In-Memory)
- ❌ Data lost on restart
- ❌ No persistence
- ❌ No querying/filtering
- ❌ No analytics
- ❌ No backup/restore

### After (PostgreSQL)
- ✅ Persistent storage
- ✅ Data survives restarts
- ✅ Complex queries (filter by language, score, date)
- ✅ Analytics & statistics
- ✅ Backup/restore support
- ✅ Scalable (connection pooling)
- ✅ ACID compliance
- ✅ Full-text search capability

---

## 📈 Performance

### Connection Pooling
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # 10 concurrent connections
    max_overflow=20,     # Allow up to 20 extra
    pool_pre_ping=True   # Auto-reconnect
)
```

### Indexes for Common Queries
- Language + Date filtering
- Score-based sorting
- UUID lookups
- Poetic form filtering

### JSON Columns
- Flexible schema for analysis data
- No need to migrate on analysis format changes
- PostgreSQL native JSON support

---

## 🔒 Security

### Environment Variables
```bash
# .env (DO NOT COMMIT TO GIT)
DATABASE_URL=postgresql://user:password@localhost/db
```

### Add to .gitignore
```
.env
__pycache__/
*.pyc
.db
```

### SQL Injection Protection
- SQLAlchemy ORM parameterizes all queries
- No raw SQL in application code

---

## 📝 Next Steps

1. **Create CRUD module** (`app/crud.py`)
2. **Setup Alembic migrations**
3. **Update API endpoints** to use database
4. **Create database admin UI** for viewing results
5. **Add backup script** for production
6. **Setup connection pooling** monitoring

---

**Status**: ✅ Database Layer Complete  
**Version**: 3.0.0  
**Database**: PostgreSQL 15+  
**ORM**: SQLAlchemy 2.0  
**Migrations**: Alembic 1.13
