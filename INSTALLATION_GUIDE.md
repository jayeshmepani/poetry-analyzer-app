# INSTALLATION GUIDE
## Ultimate Literary Master System

**Last Updated**: 2024  
**Python Version**: 3.13.x  
**Status**: Production Ready

---

## 📋 PREREQUISITES

### **System Requirements**
- Python 3.10 - 3.13 (tested on 3.13)
- pip >= 24.0
- 8GB RAM minimum (16GB recommended for transformer models)
- 10GB disk space

### **Optional (for GPU acceleration)**
- NVIDIA GPU with CUDA 11.8+
- NVIDIA cuDNN 8.x

---

## 🚀 QUICK START

### **1. Create Virtual Environment**

```bash
cd poetry_analyzer_app

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### **2. Upgrade pip**

```bash
pip install --upgrade pip setuptools wheel
```

### **3. Install Core Dependencies**

```bash
# Install core packages first (this takes time)
pip install fastapi uvicorn pydantic spacy nltk stanza

# Install transformers and PyTorch
pip install transformers sentence-transformers torch torchaudio torchvision

# Install remaining packages
pip install -r requirements.txt
```

**OR** install everything at once:

```bash
pip install -r requirements.txt
```

⏱️ **Installation Time**: 15-30 minutes depending on internet speed

### **4. Download NLP Models**

```bash
# spaCy English transformer model (REQUIRED)
python -m spacy download en_core_web_trf

# Stanza multilingual models (OPTIONAL - for non-English languages)
python -c "import stanza; stanza.download('en')"
python -c "import stanza; stanza.download('hi')"
python -c "import stanza; stanza.download('gu')"
```

### **5. Verify Installation**

```bash
# Test imports
python -c "import spacy; print('spaCy:', spacy.__version__)"
python -c "import nltk; print('NLTK:', nltk.__version__)"
python -c "import stanza; print('Stanza:', stanza.__version__)"
python -c "import transformers; print('Transformers:', transformers.__version__)"
```

### **6. Run the Application**

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access at:**
- **Home**: http://localhost:8000
- **Analyze**: http://localhost:8000/analyze
- **API Docs**: http://localhost:8000/docs

---

## 📦 PACKAGE VERSIONS

All versions in requirements.txt are **LATEST STABLE** and **Python 3.13 compatible**:

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.115.6 | Web framework |
| spacy | 3.8.7 | Core NLP |
| spacy-transformers | 1.3.9 | Transformer support |
| nltk | 3.9.1 | Traditional NLP |
| stanza | 1.9.2 | Multilingual NLP |
| transformers | 4.47.1 | BERT models |
| torch | 2.5.1 | Deep learning |
| sentence-transformers | 3.3.1 | Embeddings |
| pandas | 2.2.3 | Data processing |
| numpy | 1.26.4 | Numerical computing |
| matplotlib | 3.10.0 | Visualization |
| plotly | 5.24.1 | Interactive charts |

---

## 🔧 TROUBLESHOOTING

### **Issue: spacy installation fails**

**Solution**: Install build tools first

```bash
# On Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# On macOS
xcode-select --install

# Then retry
pip install spacy
```

### **Issue: torch installation fails**

**Solution**: Use PyTorch index

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### **Issue: indic-nlp-library installation fails**

**Solution**: Install dependencies manually

```bash
pip install numpy scipy matplotlib
pip install indic-nlp-library
```

### **Issue: Module not found errors**

**Solution**: Make sure virtual environment is activated

```bash
# Check if venv is active
which python  # Should point to venv/bin/python

# If not, activate it
source venv/bin/activate
```

---

## 📊 POST-INSTALLATION VERIFICATION

Run the comprehensive test:

```bash
python -c "
from app.services.analysis_service import create_analysis_service

# Create service
service = create_analysis_service()

# Test analysis
text = 'Shall I compare thee to a summer day?'
result = service.analyze(text)

print('✅ Backend is working!')
print(f'Overall Quality: {result[\"evaluation\"][\"ratings\"][\"overall_quality\"]}/10')
"
```

---

## 🎯 OPTIONAL ENHANCEMENTS

### **GPU Support**

For GPU acceleration (NVIDIA):

```bash
# Uninstall CPU version
pip uninstall torch torchvision torchaudio

# Install GPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### **Additional spaCy Models**

```bash
# Multilingual models
python -m spacy download xx_sent_ud_sm

# Other languages
python -m spacy download de_core_news_trf  # German
python -m spacy download fr_core_news_trf  # French
python -m spacy download es_core_news_trf  # Spanish
```

---

## 📝 NOTES

1. **First Run**: The first analysis will be slower as models are cached
2. **Disk Space**: Models require ~2-3GB additional space
3. **Memory**: Transformer models require 4-8GB RAM
4. **Internet**: Required for initial model downloads only

---

## ✅ VERIFICATION CHECKLIST

- [ ] Virtual environment created and activated
- [ ] All packages installed successfully
- [ ] spaCy model downloaded (`en_core_web_trf`)
- [ ] Test imports work without errors
- [ ] Server starts without errors
- [ ] Can access http://localhost:8000
- [ ] Analysis endpoint works

---

## 🆘 GETTING HELP

If you encounter issues:

1. Check the error message carefully
2. Search GitHub issues for the specific package
3. Ensure Python version is 3.10-3.13
4. Try creating a fresh virtual environment
5. Check that all build tools are installed

---

**Status**: ✅ **READY FOR PRODUCTION**  
**Last Tested**: Python 3.13  
**All Libraries**: Latest Stable Versions
