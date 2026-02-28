#!/bin/bash
# =============================================================================
# PostgreSQL Database Setup Script
# Poetry Analyzer App
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=============================================================="
echo "  Poetry Analyzer App - PostgreSQL Database Setup"
echo "=============================================================="
echo ""

# Configuration
DB_NAME="poetry_analyzer"
DB_USER="poetry_user"
DB_PASS="poetry_password"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not installed${NC}"
    echo ""
    echo "Install PostgreSQL first:"
    echo "  sudo apt update"
    echo "  sudo apt install postgresql postgresql-contrib"
    echo ""
    exit 1
fi

echo "✅ PostgreSQL found"
echo ""

# Get PostgreSQL user
PG_USER="${SUDO_USER:-$USER}"
if [ -z "$PG_USER" ]; then
    PG_USER="postgres"
fi

echo "📋 Setting up PostgreSQL database..."
echo ""

# Create database and user
sudo -u postgres psql -e <<EOF
-- Create database
CREATE DATABASE ${DB_NAME};

-- Create user
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- Set ownership
ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};

-- Grant schema privileges (PostgreSQL 15+)
\\c ${DB_NAME}
GRANT ALL ON SCHEMA public TO ${DB_USER};
EOF

echo ""
echo "✅ Database '${DB_NAME}' created"
echo "✅ User '${DB_USER}' created"
echo "✅ Privileges granted"

echo ""
echo "=============================================================="
echo "  ✅ PostgreSQL database setup completed!"
echo "=============================================================="
echo ""
echo "Database Configuration:"
echo "   Host: localhost"
echo "   Database: ${DB_NAME}"
echo "   User: ${DB_USER}"
echo "   Password: ${DB_PASS}"
echo "   Port: 5432"
echo ""
echo "Next steps:"
echo "   1. Update .env file with:"
echo "      DATABASE_URL=\"postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}\""
echo ""
echo "   2. Initialize database:"
echo "      python init_db.py"
echo ""
echo "   3. Start the application:"
echo "      python -m uvicorn app.main:app --reload"
echo ""

# Test connection
echo "🔍 Testing connection..."
if PGPASSWORD=${DB_PASS} psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "SELECT 1;" &> /dev/null; then
    echo -e "${GREEN}✅ Connection test successful${NC}"
else
    echo -e "${RED}❌ Connection test failed${NC}"
    echo "Please check the credentials and try again"
    echo ""
    echo "Troubleshooting:"
    echo "   1. Make sure PostgreSQL is running: sudo systemctl status postgresql"
    echo "   2. Check pg_hba.conf allows password authentication"
    echo "   3. Restart PostgreSQL: sudo systemctl restart postgresql"
fi

echo ""
