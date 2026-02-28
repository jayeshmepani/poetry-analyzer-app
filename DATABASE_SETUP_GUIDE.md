# Database Setup Guide

Complete guide for setting up databases with Poetry Analyzer App.

## Quick Start

### Option 1: SQLite (Easiest - Recommended for Development)

SQLite is already configured by default. No setup required!

```bash
# Just run the initialization script
python init_db.py

# Start the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

**Pros:**
- ✅ No installation required
- ✅ Zero configuration
- ✅ Perfect for development/testing
- ✅ Single file database

**Cons:**
- ❌ Not suitable for production
- ❌ Limited concurrency
- ❌ No client-server architecture

---

### Option 2: MySQL/MariaDB (Production-Ready)

#### Step 1: Install MySQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server mysql-client

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### Step 2: Run Setup Script

```bash
chmod +x setup_mysql.sh
./setup_mysql.sh
```

#### Step 3: Update .env File

Edit `.env` and change `DATABASE_URL`:

```bash
# Comment out SQLite
# DATABASE_URL="sqlite:///./poetry_analyzer.db"

# Enable MySQL
DATABASE_URL="mysql+pymysql://poetry_user:poetry_password@localhost:3306/poetry_analyzer"
```

#### Step 4: Install MySQL Driver

```bash
pip install pymysql cryptography
```

#### Step 5: Initialize Database

```bash
python init_db.py
```

---

### Option 3: PostgreSQL (Recommended for Production)

#### Step 1: Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Step 2: Run Setup Script

```bash
chmod +x setup_postgresql.sh
./setup_postgresql.sh
```

#### Step 3: Update .env File

Edit `.env` and change `DATABASE_URL`:

```bash
# Comment out SQLite
# DATABASE_URL="sqlite:///./poetry_analyzer.db"

# Enable PostgreSQL
DATABASE_URL="postgresql://poetry_user:poetry_password@localhost:5432/poetry_analyzer"
```

#### Step 4: Initialize Database

```bash
python init_db.py
```

---

## Database Configuration Reference

### SQLite
```env
DATABASE_URL="sqlite:///./poetry_analyzer.db"
```

### MySQL
```env
DATABASE_URL="mysql+pymysql://username:password@localhost:3306/database_name"
```

### PostgreSQL
```env
DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
```

---

## Migration Management (Alembic)

### Initialize Alembic (Already Done)

```bash
# The alembic configuration is already set up
# alembic.ini - Configuration file
# alembic/ - Migration scripts directory
```

### Create New Migration

```bash
# After making changes to models
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head
```

### Check Migration Status

```bash
# Show current revision and pending migrations
alembic current
alembic history
```

### Rollback Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

---

## Database Verification

### Test Connection

```bash
python -c "from app.database import test_connection; print('✅ Success!' if test_connection() else '❌ Failed')"
```

### Check Database Info

```python
from app.database import get_database_info
info = get_database_info()
print(info)
```

### View Database Stats

```bash
python init_db.py
```

---

## Troubleshooting

### MySQL Connection Issues

**Problem:** `Can't connect to MySQL server`

**Solutions:**
1. Check if MySQL is running:
   ```bash
   sudo systemctl status mysql
   ```

2. Verify credentials in `.env`

3. Test connection manually:
   ```bash
   mysql -u poetry_user -p poetry_password -e "SELECT 1;"
   ```

4. Check MySQL bind address in `/etc/mysql/mysql.conf.d/mysqld.cnf`:
   ```ini
   bind-address = 127.0.0.1
   ```

### PostgreSQL Connection Issues

**Problem:** `FATAL: password authentication failed`

**Solutions:**
1. Check `pg_hba.conf`:
   ```bash
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   ```
   Ensure this line exists:
   ```
   local   all             all                                     md5
   ```

2. Restart PostgreSQL:
   ```bash
   sudo systemctl restart postgresql
   ```

3. Reset password:
   ```bash
   sudo -u postgres psql -c "ALTER USER poetry_user WITH PASSWORD 'poetry_password';"
   ```

### SQLite Issues

**Problem:** `database is locked`

**Solutions:**
1. Close other applications using the database
2. Delete the database file and reinitialize:
   ```bash
   rm poetry_analyzer.db
   python init_db.py
   ```

---

## Performance Tuning

### MySQL

Add to `/etc/mysql/mysql.conf.d/mysqld.cnf`:
```ini
[mysqld]
# Optimize for better performance
innodb_buffer_pool_size = 128M
innodb_log_file_size = 64M
innodb_flush_log_at_trx_commit = 2
```

### PostgreSQL

Add to `/etc/postgresql/*/main/postgresql.conf`:
```conf
# Optimize for better performance
shared_buffers = 128MB
effective_cache_size = 512MB
work_mem = 10MB
```

---

## Backup & Restore

### MySQL Backup

```bash
# Backup
mysqldump -u poetry_user -p poetry_password poetry_analyzer > backup.sql

# Restore
mysql -u poetry_user -p poetry_password poetry_analyzer < backup.sql
```

### PostgreSQL Backup

```bash
# Backup
pg_dump -U poetry_user poetry_analyzer > backup.sql

# Restore
psql -U poetry_user poetry_analyzer < backup.sql
```

### SQLite Backup

```bash
# Backup
cp poetry_analyzer.db poetry_analyzer.backup.db

# Restore
cp poetry_analyzer.backup.db poetry_analyzer.db
```

---

## Security Best Practices

1. **Use Strong Passwords**
   - Change default password in setup scripts
   - Use at least 16 characters with mixed case, numbers, and symbols

2. **Restrict Database Access**
   - Only allow localhost connections in production
   - Use firewall rules to block external access

3. **Environment Variables**
   - Never commit `.env` file to version control
   - Use secrets management in production

4. **Regular Backups**
   - Set up automated daily backups
   - Test restore procedures regularly

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs: `logs/app.log`
3. Check database logs:
   - MySQL: `/var/log/mysql/error.log`
   - PostgreSQL: `/var/log/postgresql/postgresql-*.log`
