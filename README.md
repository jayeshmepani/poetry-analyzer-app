# Ultimate Literary & Linguistic Master System
## Backend Implementation - COMPLETE ✅

Comprehensive poetry and literary analysis system implementing all frameworks from `quantitative_poetry_metrics.md` and `ultimate_literary_master_system.md`.

---

## 📊 **Backend Completion Status: 100%**

### ✅ **Completed Modules**

| Module | File | Status | Features |
|--------|------|--------|----------|
| **Configuration** | `config.py` | ✅ | 10 setting classes, env support |
| **Schemas** | `schemas.py` | ✅ | 50+ Pydantic models |
| **Linguistic Analysis** | `linguistic.py` | ✅ | spaCy, Stanza, Indic NLP |
| **Quantitative Metrics** | `quantitative.py` | ✅ | TTR, MTLD, MATTR, RH1/RH2, MCI |
| **Prosody Engine** | `prosody.py` | ✅ | English meter, Hindi Chhand, Urdu Aruz, Gujarati |
| **Literary Devices** | `literary_devices.py` | ✅ | Tropes, Schemes, Alankar, Rasa |
| **Advanced Analysis** | `advanced_analysis.py` | ✅ | TP-CASTT, SWIFT, Touchstone, Sentiment |
| **Evaluation** | `evaluation.py` | ✅ | 7-category scoring, publishability |
| **Analysis Service** | `analysis_service.py` | ✅ | Orchestrates all modules |
| **API Application** | `main.py` | ✅ | FastAPI with 20+ endpoints |

---

## 🚀 **Quick Start**

### **Automated Installation (Recommended)**

#### **Linux/macOS**
```bash
cd poetry_analyzer_app
chmod +x install.sh
./install.sh
```

#### **Windows (PowerShell as Administrator)**
```powershell
cd poetry_analyzer_app
.\install.ps1
```

### **Manual Installation**

#### **1. Install System Dependencies**

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y \
    build-essential gcc g++ gfortran \
    libopenblas-dev liblapack-dev pkg-config \
    python3-dev python3-pip python3-venv cmake git
```

**macOS:**
```bash
xcode-select --install
brew install python@3.13 openblas pkg-config cmake git
```

**Windows:**
- Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Install [Python 3.13 (64-bit)](https://www.python.org/downloads/)

> 📖 **See [INSTALLATION.md](INSTALLATION.md) for detailed platform-specific instructions**

#### **2. Create Virtual Environment**
```bash
cd poetry_analyzer_app

# Create virtual environment
python3.13 -m venv .env

# Activate (Linux/macOS)
source .env/bin/activate

# Activate (Windows PowerShell)
.\.env\Scripts\Activate.ps1
```

#### **3. Install Python Dependencies**
```bash
# Upgrade build tools
python -m pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
```

#### **4. Download NLP Models**
```bash
# spaCy English transformer (Primary model for English)
python -m spacy download en_core_web_trf

# spaCy Multilingual small (For other languages)
python -m spacy download xx_sent_ud_sm
```

#### **5. Run the Application**
```bash
# Using run script
chmod +x run.sh
./run.sh

# Or manually
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **6. Access the API**

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root**: http://localhost:8000

---

## 📁 **Project Structure**

```
poetry_analyzer_app/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Configuration system
│   ├── main.py                      # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic models (50+)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py      # Master orchestrator
│   │   ├── linguistic.py            # spaCy/Stanza/Indic NLP
│   │   ├── quantitative.py          # TTR, MTLD, readability
│   │   ├── prosody.py               # Meter, rhyme, Chhand, Aruz
│   │   ├── literary_devices.py      # Tropes, Alankar, Rasa
│   │   ├── advanced_analysis.py     # TP-CASTT, Touchstone
│   │   └── evaluation.py            # 7-category scoring
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                # API routes (in main.py)
│   └── utils/
│       ├── __init__.py
│       └── helpers.py               # Utility functions
├── templates/                       # Frontend (to be added)
├── static/                          # CSS, JS, images
├── requirements.txt                 # All dependencies
├── run.sh                          # Run script
└── README.md                       # This file
```

---

## 🔧 **API Endpoints**

### **Analysis Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Analyze single text |
| `POST` | `/api/v1/analyze/batch` | Batch analysis |
| `GET` | `/api/v1/result/{id}` | Get stored result |
| `DELETE` | `/api/v1/result/{id}` | Delete result |

### **Generation Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/generate/constraint` | Oulipo constraint generation |

### **Reference Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/forms` | List poetic forms |
| `GET` | `/api/v1/meters` | List metrical patterns |
| `GET` | `/api/v1/rasas` | Navarasa information |

### **Visualization Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/visualize/{id}` | Get chart data |

### **Utility Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/stats` | Usage statistics |
| `POST` | `/api/v1/clear-results` | Clear storage |

---

## 📊 **Analysis Features**

### **1. Quantitative Metrics**
- **Lexical Diversity**: TTR, MTLD, MATTR, Hapax Legomena
- **Readability**: Flesch-Kincaid, Gunning Fog, Coleman-Liau, ARI, SMOG
- **Hindi Metrics**: RH1, RH2, Matra Complexity Index, Jukta Akshar Density
- **Structural**: Line count, stanza pattern, enjambment ratio, golden ratio

### **2. Prosody Analysis**
- **English**: Iambic, Trochaic, Anapestic, Dactylic, Spondaic
- **Hindi**: Doha, Chaupai, Soratha, Kundaliya, Rola, Harigitika
- **Urdu**: Mutaqaarib, Hazaj, Ramal, Kaamil, Mujtass
- **Gujarati**: Padyabandh, Garbi, Raas, Ghazal

### **3. Linguistic Analysis**
- **Phonetics**: Alliteration, assonance, consonance, onomatopoeia, phonesthemes
- **Morphology**: Prefixes, suffixes, compounds, word length distribution
- **Syntax**: Sentence types, clause structure, syntactic complexity
- **Semantics**: Concrete vs abstract, named entities, semantic density
- **POS**: Full part-of-speech distribution

### **4. Literary Devices**
- **Tropes**: Metaphor, simile, personification, metonymy, synecdoche, hyperbole, irony, oxymoron, paradox
- **Schemes**: Alliteration, anaphora, epistrophe, parallelism, antithesis, chiasmus
- **Imagery**: Visual, auditory, tactile, gustatory, olfactory, kinesthetic, organic
- **Sanskrit Alankar**: Yamaka, Shlesha, Utpreksha, Vibhavana, Vishesokti, Rupak, Upama
- **Rasa Theory**: Complete Navarasa analysis (Shringara, Hasya, Karuna, Raudra, Veera, Bhayanaka, Bibhatsa, Adbhuta, Shanta)

### **5. Advanced Analysis**
- **TP-CASTT**: Title, Paraphrase, Connotation, Attitude, Shift, Title, Theme
- **SWIFT**: Structure, Word Choice, Imagery, Figurative Language, Theme
- **Touchstone Method**: Comparison against canonical passages (Milton, Shakespeare, Homer, Dante)
- **Sentiment Analysis**: Valence, Arousal, Dominance (VAD), emotion distribution, sentiment arc

### **6. Evaluation & Scoring**
- **7-Category Ratings**: Technical Craft, Language & Diction, Imagery & Voice, Emotional Impact, Cultural Fidelity, Originality, Computational Greatness
- **Publishability Assessment**: Ready / Light Edits / Heavy Revision / Major Rework
- **Performance Assessment**: Suitability for spoken word, breath units, memorability
- **Strengths & Suggestions**: Prioritized improvement recommendations

---

## 🌍 **Language Support**

| Language | Support Level | Features |
|----------|---------------|----------|
| **English** | ⭐⭐⭐⭐⭐ | Full support |
| **Hindi** | ⭐⭐⭐⭐⭐ | Chhand, RH1/RH2, Rasa, Alankar |
| **Gujarati** | ⭐⭐⭐⭐ | Prosody, basic analysis |
| **Urdu** | ⭐⭐⭐⭐ | Aruz/Bahr analysis |
| **Marathi** | ⭐⭐⭐ | Basic metrics |
| **Bengali** | ⭐⭐⭐ | Basic metrics |

---

## 📝 **Example Usage**

### **Analyze a Poem**

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Poem",
    "text": "Shall I compare thee to a summer'\''s day?\nThou art more lovely and more temperate...",
    "language": "en",
    "form": "sonnet",
    "strictness": 8
  }'
```

### **Batch Analysis**

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"text": "First poem...", "language": "en"},
      {"text": "Second poem...", "language": "hi"}
    ],
    "compare": true
  }'
```

### **Python SDK**

```python
from app.services.analysis_service import create_analysis_service

service = create_analysis_service(language="en", strictness=8)

result = service.analyze(
    text="Your poem here...",
    title="My Poem",
    form="sonnet"
)

print(f"Overall Quality: {result['evaluation']['ratings']['overall_quality']}/10")
print(f"Executive Summary: {result['executive_summary']}")
```

---

## 🧪 **Testing**

```bash
# Run tests (when added)
pytest tests/

# Test single module
python -m pytest tests/test_quantitative.py -v
```

---

## 📚 **Documentation**

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Source Code**: Inline docstrings throughout

---

## 🔑 **Key Formulas Implemented**

### **From quantitative_poetry_metrics.md**

1. **Type-Token Ratio**: `TTR = Unique Words / Total Words`
2. **MTLD**: Measure of Textual Lexical Diversity (threshold-based)
3. **MATTR**: Moving-Average Type-Token Ratio (windowed)
4. **Flesch-Kincaid**: `0.39 × (W/S) + 11.8 × (Syl/W) - 15.59`
5. **RH1**: `-2.34 + 2.14(AWL) + 0.01(JUK)`
6. **RH2**: `-0.82 + 1.83(AWL) + 0.09(PSW)`
7. **MCI**: `(Guru Syllables / Total Syllables) × 100`
8. **Computational Greatness**: Weighted composite score

### **From ultimate_literary_master_system**

1. **7-Category Rating System**: Weighted average with customizable weights
2. **Rasa Vector**: 9-dimensional emotion space
3. **TP-CASTT Pipeline**: 7-step analysis
4. **Touchstone Comparison**: Canonical passage similarity

---

## 🎯 **Next Steps (Frontend)**

Backend is **100% complete**. Next phase: **Frontend Implementation**

1. Create Jinja2 templates
2. Add Tailwind CSS styling
3. Implement FontAwesome icons
4. Build interactive visualizations (Chart.js)
5. Create analysis input form
6. Build results dashboard
7. Add comparative analysis view

---

## 📞 **Support**

For issues or questions:
1. Check API docs at `/docs`
2. Review source code docstrings
3. Check logs for error details

---

## 📄 **License**

Based on research frameworks from quantitative_poetry_metrics.md and ultimate_literary_master_system.md

---

## 📚 **Installation Documentation**

| Document | Description |
|----------|-------------|
| **[INSTALLATION.md](INSTALLATION.md)** | Complete installation guide for Windows, Linux, and macOS |
| **[EXTERNAL_DEPENDENCIES.md](EXTERNAL_DEPENDENCIES.md)** | System-level dependencies (compilers, libraries) |
| **[requirements.txt](requirements.txt)** | Python package dependencies |
| **[install.sh](install.sh)** | Automated installation script (Linux/macOS) |
| **[install.ps1](install.ps1)** | Automated installation script (Windows) |

---

**Backend Status: ✅ COMPLETE**
**Version**: 2.0.0
**Last Updated**: February 27, 2026
