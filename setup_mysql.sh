#!/bin/bash
# =============================================================================
# MySQL Database Setup Script
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
echo "  Poetry Analyzer App - MySQL Database Setup"
echo "=============================================================="
echo ""

# Configuration
DB_NAME="poetry_analyzer"
DB_USER="poetry_user"
DB_PASS="poetry_password"
DB_HOST="localhost"

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo -e "${RED}❌ MySQL is not installed${NC}"
    echo ""
    echo "Install MySQL first:"
    echo "  sudo apt update"
    echo "  sudo apt install mysql-server"
    echo ""
    exit 1
fi

echo "✅ MySQL found"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠️  This script needs sudo privileges${NC}"
    echo "Please enter your password when prompted"
    echo ""
fi

# Create database and user
echo "📋 Setting up MySQL database..."
echo ""

sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "✅ Database '${DB_NAME}' created"

sudo mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_PASS}';"
echo "✅ User '${DB_USER}' created"

sudo mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'${DB_HOST}';"
echo "✅ Privileges granted"

sudo mysql -e "FLUSH PRIVILEGES;"
echo "✅ Privileges flushed"

echo ""
echo "=============================================================="
echo "  ✅ MySQL database setup completed!"
echo "=============================================================="
echo ""
echo "Database Configuration:"
echo "   Host: ${DB_HOST}"
echo "   Database: ${DB_NAME}"
echo "   User: ${DB_USER}"
echo "   Password: ${DB_PASS}"
echo ""
echo "Next steps:"
echo "   1. Update .env file with:"
echo "      DATABASE_URL=\"mysql+pymysql://${DB_USER}:${DB_PASS}@${DB_HOST}:3306/${DB_NAME}\""
echo ""
echo "   2. Install PyMySQL:"
echo "      pip install pymysql"
echo ""
echo "   3. Initialize database:"
echo "      python init_db.py"
echo ""
echo "   4. Start the application:"
echo "      python -m uvicorn app.main:app --reload"
echo ""

# Test connection
echo "🔍 Testing connection..."
if mysql -u ${DB_USER} -p${DB_PASS} -e "USE ${DB_NAME}; SELECT 1;" &> /dev/null; then
    echo -e "${GREEN}✅ Connection test successful${NC}"
else
    echo -e "${RED}❌ Connection test failed${NC}"
    echo "Please check the credentials and try again"
fi

echo ""
