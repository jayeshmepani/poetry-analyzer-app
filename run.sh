#!/bin/bash
# Poetry Analyzer Application - Run Script
# Supports both FastAPI and Flask

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default settings
FRAMEWORK="${FRAMEWORK:-fastapi}"  # fastapi or flask
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-9000}"
DEBUG="${DEBUG:-false}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --framework)
            FRAMEWORK="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --debug)
            DEBUG="true"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --framework FRAMEWORK  Use FRAMEWORK (fastapi or flask, default: fastapi)"
            echo "  --host HOST            Host to bind to (default: 0.0.0.0)"
            echo "  --port PORT            Port to bind to (default: 9000)"
            echo "  --debug                Enable debug mode"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  FRAMEWORK              Set framework (fastapi or flask)"
            echo "  HOST                   Set host"
            echo "  PORT                   Set port"
            echo "  DEBUG                  Enable debug mode"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo ""
echo "=============================================================="
echo "  Poetry Analyzer Application"
echo "=============================================================="
echo ""
echo "Configuration:"
echo "  Framework: ${FRAMEWORK}"
echo "  Host: ${HOST}"
echo "  Port: ${PORT}"
echo "  Debug: ${DEBUG}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Check/install dependencies
echo "📦 Checking dependencies..."
if ! python -c "import flask" 2>/dev/null; then
    echo "   Installing Flask..."
    pip install flask flask-cors
fi

if ! python -c "import fastapi" 2>/dev/null; then
    echo "   Installing FastAPI..."
    pip install fastapi uvicorn
fi

# Initialize database if needed
echo ""
echo "📊 Checking database..."
if [ ! -f "poetry_analyzer.db" ]; then
    echo "   Initializing database..."
    python init_db.py || true
else
    echo "   ✅ Database found"
fi

# Start the application
echo ""
echo "=============================================================="
echo "  Starting ${FRAMEWORK^} Server..."
echo "=============================================================="
echo ""

if [ "${FRAMEWORK}" = "flask" ]; then
    # Flask
    echo "🌐 Web Interface: http://${HOST}:${PORT}/dashboard"
    echo "❤️  Health Check: http://${HOST}:${PORT}/health"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    
    export FLASK_APP=flask_app.py
    export FLASK_ENV=${DEBUG:+development}${DEBUG:-production}
    
    python flask_app.py --host "${HOST}" --port "${PORT}" ${DEBUG:+--debug}
else
    # FastAPI
    echo "🌐 Web Interface: http://${HOST}:${PORT}/dashboard"
    echo "📖 API Documentation: http://${HOST}:${PORT}/docs"
    echo "📄 Redoc: http://${HOST}:${PORT}/redoc"
    echo "❤️  Health Check: http://${HOST}:${PORT}/health"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    
    if [ "${DEBUG}" = "true" ]; then
        uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
    else
        uvicorn app.main:app --host "${HOST}" --port "${PORT}"
    fi
fi
