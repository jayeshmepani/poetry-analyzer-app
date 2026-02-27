# Database Verification Guide

## 🔍 How to Check Database Status

### Method 1: Admin Dashboard (Visual)

1. **Go to Database Status Page**
   ```
   http://localhost:9000/admin/database
   ```

2. **You'll See:**
   - ✅ Connection status (connected/failed)
   - 📊 List of tables
   - 📈 Statistics (total analyses, avg score, etc.)
   - 📋 Recent analyses
   - 🔧 Action buttons (Initialize, Clear Data)

### Method 2: Command Line

```bash
cd poetry_analyzer_app
source .env/bin/activate
python -m app.database_verifier
```

**Output:**
```
============================================================
DATABASE VERIFICATION
============================================================

🔌 CONNECTION
   Status: ✅ connected
   Database: poetry_analyzer
   Host: localhost:5432

📊 TABLES
   Status: ✅ ok
   Found: 2 tables
      - analysis_results
      - database_stats

📈 STATISTICS
   Total Analyses: 10
   Average Score: 7.5
   Recent (24h): 3
   Storage: 0.05 MB

📋 RECENT ANALYSES
   • My Poem (en) - Score: 8.5
   • Hindi Kavita (hi) - Score: 7.0

============================================================
```

### Method 3: Python Code

```python
from app.database_verifier import DatabaseVerifier

# Get full status
status = DatabaseVerifier.full_status()
print(status['connection']['status'])  # ✅ connected
print(status['statistics']['total_analyses'])  # 10

# Check connection only
conn = DatabaseVerifier.check_connection()
print(conn['status'])  # ✅ connected or ❌ failed

# Check tables
tables = DatabaseVerifier.check_tables()
print(tables['status'])  # ✅ ok
print(tables['missing'])  # [] if all tables exist
```

---

## 🎯 Quick Checks

### Is Database Connected?

**Visual:** Green "Connected" badge on `/admin/database`

**CLI:** 
```bash
python -c "from app.database_verifier import DatabaseVerifier; print(DatabaseVerifier.check_connection()['status'])"
```

**Expected:** `✅ connected`

### Are Tables Created?

**Visual:** List of tables with green checkmarks

**CLI:**
```bash
python -c "from app.database_verifier import DatabaseVerifier; print(DatabaseVerifier.check_tables()['status'])"
```

**Expected:** `✅ ok`

### Is Data Being Saved?

**Visual:** "Total Analyses" count > 0

**CLI:**
```bash
python -c "from app.database_verifier import DatabaseVerifier; print(DatabaseVerifier.get_statistics()['total_analyses'])"
```

**Expected:** Number > 0 (e.g., `10`)

---

## 🔧 Initialize Database

If tables are missing:

### Via Admin Panel
1. Go to `/admin/database`
2. Click **"Initialize Database"** button
3. Confirm
4. Tables will be created

### Via Command Line
```bash
python -c "from app.database_verifier import init_database; init_database()"
```

**Expected Output:**
```
🔧 Initializing database...
✅ Database tables created successfully
📊 Tables status: ✅ ok
✅ All expected tables exist
```

---

## 📊 What Gets Saved

When you analyze a poem, this data is saved:

```python
{
    'title': 'My Poem',
    'text': 'Roses are red...',
    'language': 'en',
    'overall_score': 8.5,
    'technical_craft_score': 8.0,
    'language_diction_score': 7.5,
    'quantitative_metrics': {...},
    'prosody_analysis': {...},
    'literary_devices': {...},
    'word_count': 50,
    'line_count': 12,
    'created_at': datetime.utcnow()
}
```

---

## 🎨 Visual Indicators

| Status | Icon | Color | Meaning |
|--------|------|-------|---------|
| Connected | ✅ | Green | Database working |
| Disconnected | ❌ | Red | Connection failed |
| Incomplete | ⚠️ | Yellow | Some tables missing |
| Error | ❌ | Red | Something went wrong |

---

## 🐛 Troubleshooting

### "❌ failed" Connection

**Problem:** Can't connect to database

**Solution:**
1. Check PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```
2. Check DATABASE_URL in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/poetry_analyzer
   ```
3. Test connection:
   ```bash
   psql -U user -d poetry_analyzer
   ```

### "⚠️ incomplete" Tables

**Problem:** Some tables missing

**Solution:**
1. Go to `/admin/database`
2. Click **"Initialize Database"**
3. Or run:
   ```bash
   python -c "from app.database_verifier import init_database; init_database()"
   ```

### "0" Total Analyses

**Problem:** No data saved yet

**Solution:**
1. This is normal for new installations
2. Analyze a poem at `/admin/analyze`
3. Data will be saved automatically
4. Check count updates at `/admin/database`

---

## 📈 Monitor Database

### Check Before/After Analysis

**Before:**
```bash
python -c "from app.database_verifier import DatabaseVerifier; print('Before:', DatabaseVerifier.get_statistics()['total_analyses'])"
# Output: Before: 0
```

**Analyze a poem** (via `/admin/analyze`)

**After:**
```bash
python -c "from app.database_verifier import DatabaseVerifier; print('After:', DatabaseVerifier.get_statistics()['total_analyses'])"
# Output: After: 1
```

✅ **Data is being saved!**

---

## 🎯 Summary

| Check | Command | Expected |
|-------|---------|----------|
| **Connection** | `check_connection()` | `✅ connected` |
| **Tables** | `check_tables()` | `✅ ok` |
| **Total** | `get_statistics()` | `total_analyses > 0` |
| **Visual** | `/admin/database` | All green ✅ |

**Your database is working when you see green checkmarks everywhere!** ✅

---

**Status**: ✅ Ready  
**Version**: 3.0.0  
**Last Updated**: February 27, 2026
