# Poetry Analyzer App - Installation Guide

Complete installation instructions for **Windows 10/11**, **Linux (Ubuntu/Debian)**, and **macOS**.

---

## 📋 System Requirements

### Minimum Requirements
- **RAM:** 8 GB (16 GB recommended for large models)
- **Storage:** 10 GB free space (20+ GB recommended for models and datasets)
- **Internet:** Required for initial package installation and model downloads

### Supported Platforms
| Platform | Version | Support |
|----------|---------|---------|
| **Windows** | 10/11 (64-bit) | ✅ Full Support |
| **Linux** | Ubuntu 20.04+, Debian 11+ | ✅ Full Support |
| **macOS** | 11.0+ (Big Sur or later) | ✅ Full Support |

### Python Version
- **Required:** Python 3.13 (64-bit only)
- **Note:** 32-bit Python is NOT supported

---

## 🔧 External System Dependencies

### Windows 10/11

#### 1. Microsoft Visual C++ Build Tools (REQUIRED)
Most scientific Python packages require C++ compilation on Windows.

**Option A: Build Tools Only (Recommended - Smaller Download)**
```powershell
# Download and install from:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

# During installation, select:
✓ MSVC v143 - VS 2022 C++ x64/x86 build tools
✓ Windows 10/11 SDK
✓ C++ CMake tools
```

**Option B: Visual Studio Community (Full IDE)**
```powershell
# Download from:
https://visualstudio.microsoft.com/vs/community/

# During installation, select:
✓ Desktop development with C++
```

**Verify Installation:**
```powershell
# Open PowerShell as Administrator
cl
# Should show Microsoft C/C++ compiler version
```

#### 2. Python 3.13 (64-bit)
```powershell
# Option 1: Microsoft Store (Recommended for Windows)
# Open Microsoft Store and search for "Python 3.13"

# Option 2: Official Python Installer
# Download from: https://www.python.org/downloads/windows/
# ✓ Check "Add Python to PATH" during installation
```

**Verify Python Installation:**
```powershell
python --version
# Should show: Python 3.13.x

python -c "import struct; print(struct.calcsize('P') * 8)"
# Should show: 64 (confirms 64-bit)
```

---

### Linux (Ubuntu/Debian)

#### 1. System Build Dependencies
```bash
# Update package list
sudo apt update

# Install essential build tools and libraries
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
```

#### 2. Python 3.13
```bash
# Ubuntu 24.04+ (Python 3.13 available in default repos)
sudo apt install -y python3.13 python3.13-venv python3.13-dev

# For older Ubuntu versions, use Deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev
```

**Verify Installation:**
```bash
python3.13 --version
# Should show: Python 3.13.x

python3.13 -c "import struct; print(struct.calcsize('P') * 8)"
# Should show: 64 (confirms 64-bit)
```

---

### macOS

#### 1. Xcode Command Line Tools
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Accept license
sudo xcodebuild -license accept
```

#### 2. Homebrew (Recommended Package Manager)
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.13
brew install openblas
brew install pkg-config
brew install cmake
brew install git
```

#### 3. Python 3.13
```bash
# Via Homebrew (Recommended)
brew install python@3.13

# Or download from python.org
# https://www.python.org/downloads/macos/
```

**Verify Installation:**
```bash
python3.13 --version
# Should show: Python 3.13.x

python3.13 -c "import struct; print(struct.calcsize('P') * 8)"
# Should show: 64 (confirms 64-bit)
```

---

## 🐍 Python Environment Setup

### Create Virtual Environment (All Platforms)

#### Windows (PowerShell)
```powershell
# Navigate to project directory
cd C:\path\to\poetry_analyzer_app

# Create virtual environment
python -m venv .env

# Activate virtual environment
.\.env\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Linux/macOS (Bash/Zsh)
```bash
# Navigate to project directory
cd /path/to/poetry_analyzer_app

# Create virtual environment
python3.13 -m venv .env

# Activate virtual environment
source .env/bin/activate
```

**Verify Virtual Environment:**
```bash
# Should show (.env) prefix in prompt
which python
# Should point to .env/bin/python (Linux/macOS) or .env\Scripts\python.exe (Windows)
```

---

## 📦 Install Python Dependencies

### Upgrade Build Tools (IMPORTANT)
```bash
# Upgrade pip, setuptools, and wheel FIRST
python -m pip install --upgrade pip setuptools wheel
```

### Install Requirements
```bash
# Install all Python dependencies
pip install -r requirements.txt
```

**Installation Time Estimate:**
- **Fast Internet (100+ Mbps):** 5-10 minutes
- **Medium Internet (20-50 Mbps):** 15-25 minutes
- **Slow Internet (<10 Mbps):** 30-60 minutes

### Troubleshooting Installation Errors

#### Windows: "Microsoft Visual C++ 14.0 or greater is required"
```powershell
# Install Build Tools (see Windows section above)
# OR install via pip:
pip install --upgrade pip setuptools wheel
pip install --only-binary :all: package_name
```

#### Linux: "No module named 'numpy'"
```bash
# Install numpy first, then retry
pip install numpy
pip install -r requirements.txt
```

#### macOS: "zsh: command not found" or architecture issues
```bash
# For Apple Silicon (M1/M2/M3), ensure using ARM64 Python
arch -arm64 python3.13 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

---

## 🤖 Download NLP Models

### spaCy Models (REQUIRED)
```bash
# English transformer model (best quality)
python -m spacy download en_core_web_trf

# English small model (faster, good for basic tasks)
python -m spacy download en_core_web_sm

# Multi-language model (for non-English poetry)
python -m spacy download xx_sent_ud_sm
```

### Stanza Models (Download as needed)
```python
# In Python, download models for your languages
import stanza

# English
stanza.download('en')

# For other languages (as needed)
# stanza.download('es')  # Spanish
# stanza.download('fr')  # French
# stanza.download('de')  # German
# stanza.download('hi')  # Hindi
# stanza.download('ta')  # Tamil
```

### NLTK Data (Optional - for additional text processing)
```python
import nltk

# Download common resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('vader_lexicon')
```

---

## ✅ Verify Installation

### Run Verification Script
```bash
# Create a test script: test_installation.py
python test_installation.py
```

**Expected Output:**
```
✓ FastAPI 0.129.0
✓ spaCy 3.8.7
✓ Transformers 4.49.0
✓ Sentence Transformers 3.4.1
✓ Stanza 1.10.1
✓ Textdescriptives 2.8.2
✓ Scikit-learn 1.6.1
✓ SciPy 1.13.1
✓ NumPy 1.26.4
✓ Pandas 2.2.3
✓ PyTorch 2.10.0

All packages installed successfully!
```

### Manual Verification
```python
# In Python interpreter
import fastapi
import spacy
import transformers
import sentence_transformers
import stanza
import textdescriptives
import sklearn
import scipy
import numpy
import pandas
import torch

print(f"✓ FastAPI {fastapi.__version__}")
print(f"✓ spaCy {spacy.__version__}")
print(f"✓ Transformers {transformers.__version__}")
print(f"✓ Sentence Transformers {sentence_transformers.__version__}")
print(f"✓ Stanza {stanza.__version__}")
print(f"✓ Textdescriptives {textdescriptives.__version__}")
print(f"✓ Scikit-learn {sklearn.__version__}")
print(f"✓ SciPy {scipy.__version__}")
print(f"✓ NumPy {numpy.__version__}")
print(f"✓ Pandas {pandas.__version__}")
print(f"✓ PyTorch {torch.__version__}")
```

---

## 🚀 Run the Application

### Start the Server
```bash
# Activate virtual environment (if not already active)
# Windows: .env\Scripts\activate
# Linux/macOS: source .env/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Application
- **Web Interface:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Alternative API Docs:** http://localhost:8000/redoc

---

## 🛠️ Common Issues & Solutions

### Issue 1: pip install fails with "Could not build wheels"
**Solution:**
```bash
# Windows: Ensure Visual C++ Build Tools installed
# Linux: Ensure build-essential, gfortran installed
# macOS: Ensure Xcode Command Line Tools installed

# Then retry with:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

### Issue 2: "ImportError: DLL load failed" (Windows)
**Solution:**
```powershell
# Reinstall affected package
pip uninstall package_name
pip install package_name --force-reinstall

# Or install with pre-compiled wheels
pip install package_name --only-binary :all:
```

### Issue 3: "libopenblas not found" (Linux/macOS)
**Solution:**
```bash
# Linux
sudo apt install libopenblas-dev

# macOS
brew install openblas
export PKG_CONFIG_PATH="/opt/homebrew/opt/openblas/lib/pkgconfig"
```

### Issue 4: spaCy model download fails
**Solution:**
```bash
# Download directly
python -m spacy download en_core_web_trf --direct

# Or use pip
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0-py3-none-any.whl
```

### Issue 5: Out of memory during installation
**Solution:**
```bash
# Install packages one at a time
pip install torch --no-cache-dir
pip install transformers --no-cache-dir
pip install spacy --no-cache-dir
# ... continue with other packages
```

---

## 📝 Post-Installation Checklist

- [ ] All Python packages installed successfully
- [ ] spaCy English model downloaded (`en_core_web_trf`)
- [ ] Stanza models downloaded for required languages
- [ ] NLTK data downloaded (if needed)
- [ ] Virtual environment activates correctly
- [ ] Application starts without errors
- [ ] Web interface accessible at http://localhost:8000
- [ ] API documentation loads correctly

---

## 📚 Additional Resources

### Official Documentation
- [Python 3.13](https://docs.python.org/3.13/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [spaCy](https://spacy.io/usage)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [PyTorch](https://pytorch.org/docs/stable/index.html)
- [SciPy](https://docs.scipy.org/doc/scipy/)

### Troubleshooting
- [Python Packaging User Guide](https://packaging.python.org/)
- [pip User Guide](https://pip.pypa.io/en/stable/)
- [spaCy Installation](https://spacy.io/usage#installation)

---

## 📞 Support

If you encounter issues not covered in this guide:

1. Check the [Common Issues](#common-issues--solutions) section
2. Review error messages carefully
3. Search GitHub Issues for similar problems
4. Ensure all system dependencies are installed correctly

---

**Last Updated:** February 27, 2026  
**Compatible with:** Python 3.13, Windows 10/11, Ubuntu 20.04+, macOS 11.0+
