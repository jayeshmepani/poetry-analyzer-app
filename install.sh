#!/bin/bash
# Poetry Analyzer App - Installation Script for Linux/macOS
# Usage: ./install.sh

set -e  # Exit on error

echo "=========================================="
echo "  Poetry Analyzer App - Installation"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    print_info "Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    print_info "Detected Linux"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Check Python version
print_info "Checking Python version..."
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    print_success "Python 3.13 found"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    if [[ "$PYTHON_VERSION" == "3.13"* ]]; then
        PYTHON_CMD="python3"
        print_success "Python 3.13 found"
    else
        print_error "Python 3.13 required, found Python $PYTHON_VERSION"
        print_info "Please install Python 3.13 first"
        exit 1
    fi
else
    print_error "Python 3.13 not found"
    print_info "Please install Python 3.13 first"
    exit 1
fi

# Install system dependencies
print_info "Installing system dependencies..."

if [ "$OS" == "linux" ]; then
    # Check for apt
    if command -v apt &> /dev/null; then
        print_info "Installing dependencies via apt..."
        sudo apt update
        sudo apt install -y \
            build-essential \
            gcc \
            g++ \
            gfortran \
            libopenblas-dev \
            liblapack-dev \
            pkg-config \
            python3-dev \
            python3-pip \
            python3-venv \
            cmake \
            git
        print_success "System dependencies installed"
    else
        print_error "Unsupported Linux distribution (only Debian/Ubuntu supported)"
        print_info "Please install dependencies manually (see INSTALLATION.md)"
        exit 1
    fi
elif [ "$OS" == "macos" ]; then
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew not found"
        print_info "Please install Homebrew first: https://brew.sh"
        exit 1
    fi
    
    print_info "Installing dependencies via Homebrew..."
    brew install python@3.13
    brew install openblas
    brew install pkg-config
    brew install cmake
    brew install git
    print_success "System dependencies installed"
fi

# Create virtual environment
print_info "Creating virtual environment..."
if [ -d ".env" ]; then
    print_info "Virtual environment already exists, removing..."
    rm -rf .env
fi

$PYTHON_CMD -m venv .env
print_success "Virtual environment created"

# Activate virtual environment
print_info "Activating virtual environment..."
source .env/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel
print_success "Build tools upgraded"

# Install Python dependencies
print_info "Installing Python dependencies (this may take 10-30 minutes)..."
pip install -r requirements.txt
print_success "Python dependencies installed"

# Download spaCy models
print_info "Downloading spaCy models..."
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_sm
print_success "spaCy models downloaded"

# Create test script
print_info "Creating verification script..."
cat > test_installation.py << 'EOF'
#!/usr/bin/env python
"""Verify installation of Poetry Analyzer App dependencies"""

packages = {
    'FastAPI': 'fastapi',
    'spaCy': 'spacy',
    'Transformers': 'transformers',
    'Sentence Transformers': 'sentence_transformers',
    'Stanza': 'stanza',
    'Textdescriptives': 'textdescriptives',
    'Scikit-learn': 'sklearn',
    'SciPy': 'scipy',
    'NumPy': 'numpy',
    'Pandas': 'pandas',
    'PyTorch': 'torch',
}

print("\n" + "="*50)
print("  Installation Verification")
print("="*50 + "\n")

all_ok = True
for name, module in packages.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {name} {version}")
    except ImportError as e:
        print(f"✗ {name} - NOT INSTALLED")
        all_ok = False

print("\n" + "="*50)
if all_ok:
    print("  All packages installed successfully!")
else:
    print("  Some packages are missing!")
print("="*50 + "\n")
EOF

print_success "Verification script created"

# Run verification
print_info "Verifying installation..."
python test_installation.py

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
print_info "Next steps:"
echo "  1. Activate virtual environment: source .env/bin/activate"
echo "  2. Start the server: uvicorn app.main:app --reload"
echo "  3. Open browser: http://localhost:8000"
echo ""
print_info "For more information, see INSTALLATION.md"
echo ""
