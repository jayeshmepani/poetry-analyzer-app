#!/bin/bash
# Ultimate Literary & Linguistic Master System
# Run script for Poetry Analyzer Application

set -e

echo "========================================"
echo "  Ultimate Literary Master System"
echo "  Poetry & Literary Analysis Backend"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".env" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv .env
    echo "✅ Virtual environment created"
    echo ""
    echo "⚠️  Now installing dependencies..."
    source .env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    echo ""
    echo "✅ Installation complete!"
    echo ""
fi

# Activate virtual environment
echo "✅ Using virtual environment: .env"
source .env/bin/activate

# Initialize database if needed
echo "📊 Checking database..."
python -c "from app.database_verifier import init_database; init_database()" 2>/dev/null || true

# Run the application
echo ""
echo "========================================"
echo "  Starting FastAPI Server..."
echo "========================================"
echo ""
echo "🌐 Web Interface: http://localhost:8000/admin"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📄 Redoc: http://localhost:8000/redoc"
echo "❤️  Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
