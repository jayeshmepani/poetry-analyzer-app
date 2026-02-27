# Poetry Analyzer App - Installation Script for Windows
# Usage: Open PowerShell as Administrator and run: .\install.ps1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Poetry Analyzer App - Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Functions
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Yellow
}

# Check if running as Administrator
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error-Custom "This script must be run as Administrator"
    Write-Info "Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

# Check Python version
Write-Info "Checking Python version..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.13") {
        Write-Success "Python 3.13 found"
    } else {
        Write-Error-Custom "Python 3.13 required, found: $pythonVersion"
        Write-Info "Please install Python 3.13 from https://www.python.org/downloads/"
        exit 1
    }
} catch {
    Write-Error-Custom "Python not found"
    Write-Info "Please install Python 3.13 from https://www.python.org/downloads/"
    exit 1
}

# Check if Python is 64-bit
$pythonBitness = python -c "import struct; print(struct.calcsize('P') * 8)"
if ($pythonBitness -ne "64") {
    Write-Error-Custom "64-bit Python required, found: ${pythonBitness}-bit"
    Write-Info "Please install 64-bit Python 3.13"
    exit 1
}
Write-Success "Python is 64-bit"

# Check for Visual C++ Build Tools
Write-Info "Checking for Visual C++ Build Tools..."
try {
    $clVersion = cl 2>&1 | Select-String "Microsoft"
    if ($clVersion) {
        Write-Success "Visual C++ Build Tools found"
    } else {
        Write-Info "Visual C++ Build Tools not detected"
        Write-Info "Installing via winget..."
        winget install Microsoft.VisualStudio.2022.BuildTools --silent --override "--wait --quiet --add ProductLang En-us --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
        Write-Success "Visual C++ Build Tools installed"
    }
} catch {
    Write-Info "Visual C++ Build Tools not found, installing..."
    try {
        winget install Microsoft.VisualStudio.2022.BuildTools --silent --override "--wait --quiet --add ProductLang En-us --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
        Write-Success "Visual C++ Build Tools installed"
    } catch {
        Write-Error-Custom "Failed to install Visual C++ Build Tools"
        Write-Info "Please install manually from: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
        Write-Info "Select: Desktop development with C++"
        exit 1
    }
}

# Create virtual environment
Write-Info "Creating virtual environment..."
if (Test-Path ".env") {
    Write-Info "Virtual environment already exists, removing..."
    Remove-Item -Recurse -Force .env
}

python -m venv .env
Write-Success "Virtual environment created"

# Activate virtual environment
Write-Info "Activating virtual environment..."
.\.env\Scripts\Activate.ps1
Write-Success "Virtual environment activated"

# Upgrade pip
Write-Info "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel --quiet
Write-Success "Build tools upgraded"

# Install Python dependencies
Write-Info "Installing Python dependencies (this may take 10-30 minutes)..."
pip install -r requirements.txt
Write-Success "Python dependencies installed"

# Download spaCy models
Write-Info "Downloading spaCy models..."
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_sm
Write-Success "spaCy models downloaded"

# Create test script
Write-Info "Creating verification script..."
$testScript = @'
# Verify installation of Poetry Analyzer App dependencies

$packages = @{
    'FastAPI' = 'fastapi'
    'spaCy' = 'spacy'
    'Transformers' = 'transformers'
    'Sentence Transformers' = 'sentence_transformers'
    'Stanza' = 'stanza'
    'Textdescriptives' = 'textdescriptives'
    'Scikit-learn' = 'sklearn'
    'SciPy' = 'scipy'
    'NumPy' = 'numpy'
    'Pandas' = 'pandas'
    'PyTorch' = 'torch'
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "  Installation Verification" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

$allOk = $true
foreach ($package in $packages.GetEnumerator()) {
    try {
        $module = Import-Module $package.Value -PassThru -ErrorAction Stop
        $version = $module.Version
        Write-Host "✓ $($package.Key) $version" -ForegroundColor Green
    } catch {
        Write-Host "✗ $($package.Key) - NOT INSTALLED" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
if ($allOk) {
    Write-Host "  All packages installed successfully!" -ForegroundColor Green
} else {
    Write-Host "  Some packages are missing!" -ForegroundColor Red
}
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
'@

$testScript | Out-File -FilePath "test_installation.ps1" -Encoding UTF8
Write-Success "Verification script created"

# Run verification
Write-Info "Verifying installation..."
python test_installation.py

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Info "Next steps:"
Write-Host "  1. Activate virtual environment: .\.env\Scripts\Activate.ps1"
Write-Host "  2. Start the server: uvicorn app.main:app --reload"
Write-Host "  3. Open browser: http://localhost:8000"
Write-Host ""
Write-Info "For more information, see INSTALLATION.md"
Write-Host ""
