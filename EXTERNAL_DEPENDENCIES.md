# External System Dependencies Summary

This document lists all **external (non-Python) dependencies** required for the Poetry Analyzer App.

---

## 🖥️ Windows 10/11

### Required External Dependencies

| Dependency | Purpose | Installation |
|------------|---------|--------------|
| **Microsoft Visual C++ Build Tools** | C/C++ compiler for building scientific packages (scipy, scikit-learn, etc.) | [Download](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |
| **Windows 10/11 SDK** | Windows development headers | Included with Build Tools |
| **Python 3.13 (64-bit)** | Python runtime | [python.org](https://www.python.org/downloads/) or Microsoft Store |

### Installation Commands (PowerShell as Administrator)
```powershell
# 1. Install Python 3.13 (if using winget)
winget install Python.Python.3.13

# 2. Install Visual C++ Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# 3. Verify installations
python --version
cl  # Should show MSVC compiler version
```

### Notes for Windows
- ⚠️ **32-bit Python is NOT supported** - must use 64-bit
- ⚠️ **Visual C++ Build Tools are MANDATORY** - scipy, scikit-learn, and other packages require compilation
- 💡 Use **PowerShell** instead of Command Prompt for better compatibility
- 💡 Run as Administrator when installing system packages

---

## 🐧 Linux (Ubuntu/Debian)

### Required External Dependencies

| Dependency | Purpose | Installation Command |
|------------|---------|---------------------|
| **build-essential** | C/C++ compiler toolchain | `sudo apt install build-essential` |
| **gcc** | C compiler | `sudo apt install gcc` |
| **g++** | C++ compiler | `sudo apt install g++` |
| **gfortran** | Fortran compiler (required for scipy, numpy) | `sudo apt install gfortran` |
| **libopenblas-dev** | BLAS library for linear algebra | `sudo apt install libopenblas-dev` |
| **liblapack-dev** | LAPACK library for linear algebra | `sudo apt install liblapack-dev` |
| **pkg-config** | Build configuration tool | `sudo apt install pkg-config` |
| **python3-dev** | Python development headers | `sudo apt install python3-dev` |
| **python3-pip** | Python package manager | `sudo apt install python3-pip` |
| **python3-venv** | Python virtual environment | `sudo apt install python3-venv` |
| **cmake** | Build system generator | `sudo apt install cmake` |
| **git** | Version control | `sudo apt install git` |

### One-Line Installation (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install -y \
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

### For Other Linux Distributions

#### Fedora/RHEL
```bash
sudo dnf install -y \
    gcc \
    gcc-c++ \
    gcc-gfortran \
    python3-devel \
    openblas-devel \
    lapack-devel \
    pkgconfig \
    cmake \
    git
```

#### Arch Linux
```bash
sudo pacman -S \
    base-devel \
    gcc \
    gcc-fortran \
    python \
    python-pip \
    python-virtualenv \
    openblas \
    lapack \
    pkgconf \
    cmake \
    git
```

### Notes for Linux
- ✅ **gfortran is CRITICAL** - scipy and numpy require Fortran compilation
- ✅ **libopenblas-dev and liblapack-dev** are required for scipy linear algebra operations
- 💡 Use `python3.13` command if multiple Python versions are installed

---

## 🍎 macOS

### Required External Dependencies

| Dependency | Purpose | Installation Command |
|------------|---------|---------------------|
| **Xcode Command Line Tools** | C/C++/Objective-C compiler | `xcode-select --install` |
| **Homebrew** | Package manager (recommended) | See below |
| **openblas** | BLAS library for linear algebra | `brew install openblas` |
| **pkg-config** | Build configuration tool | `brew install pkg-config` |
| **cmake** | Build system generator | `brew install cmake` |
| **git** | Version control | `brew install git` |

### Installation Commands (macOS)
```bash
# 1. Install Xcode Command Line Tools
xcode-select --install

# 2. Accept Xcode license
sudo xcodebuild -license accept

# 3. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 4. Install dependencies via Homebrew
brew install python@3.13
brew install openblas
brew install pkg-config
brew install cmake
brew install git

# 5. Set up PATH for Apple Silicon (M1/M2/M3)
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Notes for macOS
- ⚠️ **Apple Silicon (M1/M2/M3)**: Use ARM64 Python, not Rosetta 2
- ⚠️ **Xcode Command Line Tools are MANDATORY** - required for package compilation
- 💡 **Homebrew is HIGHLY recommended** for managing dependencies
- 💡 For Intel Macs: OpenBLAS is installed to `/usr/local/opt/openblas`
- 💡 For Apple Silicon: OpenBLAS is installed to `/opt/homebrew/opt/openblas`

---

## 📊 Dependency Comparison Table

| Dependency | Windows | Linux | macOS | Required For |
|------------|---------|-------|-------|--------------|
| **C/C++ Compiler** | MSVC Build Tools | gcc/g++ | Xcode CLT | scipy, scikit-learn, numpy |
| **Fortran Compiler** | Included in Build Tools | gfortran | gfortran (via Homebrew) | scipy, numpy |
| **BLAS/LAPACK** | Bundled with wheels | libopenblas-dev, liblapack-dev | openblas (Homebrew) | scipy linear algebra |
| **Python Headers** | Included with Python | python3-dev | Included with Python | Building extensions |
| **pkg-config** | Not required | pkg-config | pkg-config (Homebrew) | Build configuration |
| **cmake** | Optional | cmake | cmake (Homebrew) | Some packages |
| **git** | Optional | git | git (Homebrew) | Model downloads |

---

## 🔍 Why These Dependencies Are Needed

### scipy
- **Requires:** C, C++, and Fortran compilers + BLAS/LAPACK libraries
- **Why:** Scientific computing library with optimized linear algebra operations
- **Without:** `pip install scipy` will fail with compilation errors

### scikit-learn
- **Requires:** C compiler + scipy + numpy
- **Why:** Machine learning library with Cython extensions
- **Without:** Will fail to build wheels

### numpy
- **Requires:** C compiler
- **Why:** Foundation for scientific Python, optimized array operations
- **Without:** Most scientific packages won't work

### spaCy
- **Requires:** C++ compiler (for some components)
- **Why:** NLP library with Cython extensions
- **Without:** May fail to install or run slowly

### PyTorch / transformers
- **Requires:** C++ compiler (for some components)
- **Why:** Deep learning framework
- **Without:** Some features may not work

---

## ✅ Verification Commands

### Windows (PowerShell)
```powershell
# Check Visual C++ compiler
cl

# Check Python (should be 64-bit)
python --version
python -c "import struct; print(struct.calcsize('P') * 8)"

# Check pip
pip --version
```

### Linux (Bash)
```bash
# Check compilers
gcc --version
g++ --version
gfortran --version

# Check libraries
ldconfig -p | grep openblas
ldconfig -p | grep lapack

# Check Python (should be 64-bit)
python3.13 --version
python3.13 -c "import struct; print(struct.calcsize('P') * 8)"
```

### macOS (Bash/Zsh)
```bash
# Check Xcode
xcode-select -p

# Check compilers
gcc --version
gfortran --version  # If installed via Homebrew

# Check libraries
brew list | grep openblas

# Check Python (should be 64-bit)
python3.13 --version
python3.13 -c "import struct; print(struct.calcsize('P') * 8)"
```

---

## 🚨 Common Issues

### Issue: "No Fortran compiler found"
**Solution:**
- **Windows:** Install Visual C++ Build Tools (includes gfortran)
- **Linux:** `sudo apt install gfortran`
- **macOS:** `brew install gcc` (includes gfortran)

### Issue: "openblas not found"
**Solution:**
- **Linux:** `sudo apt install libopenblas-dev`
- **macOS:** `brew install openblas`
- **Windows:** Not required (bundled with wheels)

### Issue: "Python.h: No such file or directory"
**Solution:**
- **Linux:** `sudo apt install python3-dev`
- **Windows:** Reinstall Python with "Include pip" option
- **macOS:** Reinstall Python via Homebrew

---

## 📦 Optional Dependencies

### For GPU Support (NVIDIA CUDA)
```bash
# Windows/Linux only
# Requires NVIDIA GPU with CUDA support

# Install CUDA Toolkit from:
# https://developer.nvidia.com/cuda-toolkit

# Then install PyTorch with CUDA:
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### For Development
```bash
# All platforms
pip install pytest black flake8 mypy
```

---

**Last Updated:** February 27, 2026  
**Compatible with:** Python 3.13, Windows 10/11, Ubuntu 20.04+, macOS 11.0+
