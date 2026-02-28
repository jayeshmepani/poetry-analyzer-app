# Quick Start - Database Setup

## 🚀 Fastest Setup (SQLite)

```bash
# Initialize database
python init_db.py

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000

# Open browser
# http://localhost:9000/admin
```

**Done! ✅**

---

## 🐘 Production Setup (PostgreSQL)

```bash
# 1. Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. Setup database
./setup_postgresql.sh

# 3. Edit .env file
nano .env
# Change: DATABASE_URL="postgresql://poetry_user:poetry_password@localhost:5432/poetry_analyzer"

# 4. Initialize
python init_db.py

# 5. Start server
python -m uvicorn app.main:app --reload
```

---

## 🐬 Production Setup (MySQL)

```bash
# 1. Install MySQL
sudo apt install mysql-server

# 2. Setup database
./setup_mysql.sh

# 3. Edit .env file
nano .env
# Change: DATABASE_URL="mysql+pymysql://poetry_user:poetry_password@localhost:3306/poetry_analyzer"

# 4. Install driver
pip install pymysql cryptography

# 5. Initialize
python init_db.py

# 6. Start server
python -m uvicorn app.main:app --reload
```

---

## 📋 Common Commands

```bash
# Test database connection
python -c "from app.database import test_connection; print('✅ OK' if test_connection() else '❌ FAIL')"

# View database stats
python init_db.py

# Reset database (SQLite)
rm poetry_analyzer.db && python init_db.py

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

---

## 🔧 Troubleshooting

### Results page shows error
- ✅ Check browser console for errors
- ✅ Verify backend is running
- ✅ Check API endpoint: `curl http://localhost:9000/api/results`

### Database connection failed
- ✅ Check `.env` file has correct DATABASE_URL
- ✅ Verify database service is running
- ✅ Check credentials in `.env`

### MySQL issues
```bash
# Check status
sudo systemctl status mysql

# Restart
sudo systemctl restart mysql

# Test connection
mysql -u poetry_user -p poetry_password -e "SELECT 1;"
```

### PostgreSQL issues
```bash
# Check status
sudo systemctl status postgresql

# Restart
sudo systemctl restart postgresql

# Test connection
PGPASSWORD=poetry_password psql -h localhost -U poetry_user -d poetry_analyzer -c "SELECT 1;"
```

---

## 📚 Full Documentation

- **Complete Setup Guide:** `DATABASE_SETUP_GUIDE.md`
- **Fixes Summary:** `DATABASE_FIXES_COMPLETE.md`
- **Environment Config:** `.env`

---

**Need Help?** Check `DATABASE_SETUP_GUIDE.md` for detailed troubleshooting.
