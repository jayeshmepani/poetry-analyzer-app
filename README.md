# Poetry Analyzer App

A state-of-the-art literary and linguistic analysis engine. The application operates on a pure, asynchronous **FastAPI** architecture and leverages flagship 1.5GB HuggingFace Transformer models for unparalleled sentiment and emotion classification.

---

## 🚀 Installation Guide

We support Windows, Linux, and macOS. The backend requires **Python 3.12 (64-bit)**.
_(Note: Python 3.12 is strictly required over 3.13 due to `pkg_resources` dependencies in the `pronouncing` library)._

### 1. Prerequisite Build Tools

Because we compile massive NLP libraries, you need C++ build tools installed on your system.

**Windows (PowerShell as Admin):**
Install the [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Make sure to select "C++ build tools" during installation.

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install -y build-essential gcc g++ python3.12-dev python3.12-venv
```

**macOS:**

```bash
xcode-select --install
brew install python@3.12
```

### 2. Python Environment Setup

Open your terminal inside the `poetry-analyzer-app` directory and create a virtual environment.

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install Core Dependencies

Install the required packages. We use strict version pinning to ensure absolute stability between the FastAPI backend and the AI models.

```bash
# Upgrade build tools first
python -m pip install --upgrade pip setuptools wheel

# Install the exact application requirements
pip install -r requirements.txt
```

### 4. Download NLP Models

Run the **one-step setup script** which reads your `.env` (or `.env.example` fallback) and downloads everything automatically:
- spaCy models
- NLTK data
- Stanza resources (`STANZA_RESOURCES_DIR`, `STANZA_LANGUAGES`, `STANZA_PROCESSORS`)
- HuggingFace transformer bundles (English / Indic / multilingual / generalist)

```bash
python setup_models.py
```

This ensures downloaded assets always match the exact model names configured in your environment file. You can re-run this script any time you change model settings.

<details>
<summary>Manual alternative (if you prefer)</summary>

```bash
python -m spacy download en_core_web_trf
python -m spacy download xx_sent_ud_sm

python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

_(The HuggingFace transformer models will auto-download on first analysis run.)_

</details>

---

## ⚡ Running the Server

Initialize the database migrations via Alembic (first run only):

```bash
alembic upgrade head
```

Start the FastAPI asynchronous server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9005 --reload
```

### View The Application

- **Main Interface:** `http://localhost:9005`
- **Interactive API Docs (Swagger):** `http://localhost:9005/docs`

---

## 💾 Native Database Support

The application natively supports **SQLite** (default), **PostgreSQL**, and **MySQL/MariaDB**.

To switch your database backend, simply edit the dedicated `DB_` variables in your `.env` file. The SQLAlchemy engine will automatically parse these into the correct driver connection string and configure the appropriate connection pooling parameters behind the scenes.

**SQLite (Default)**:

```env
DB_CONNECTION=sqlite
DB_DATABASE=poetry_analyzer
```

**PostgreSQL**:

```env
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=poetry_db
DB_USERNAME=postgres
DB_PASSWORD=secret
```

**MySQL**:

```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=poetry_db
DB_USERNAME=root
DB_PASSWORD=secret
```

---

## 🧠 Core Technologies & Dependencies

As defined in `requirements.txt`, the application is powered by a heavily curated AI stack:

- **Web Framework**: FastAPI `0.135.0` + Uvicorn `0.41.0` + Jinja2 `3.1.6`
- **Deep Learning**: PyTorch `2.10.0` + Transformers `4.49.0`
- **NLP Pipelines**: spaCy `3.8.11`, NLTK `3.9.3`, Stanza `1.11.1`, indic-nlp-library `0.92`
- **Text Processing**: textdescriptives `2.8.4`, textstat `0.7.13`, syllables `1.1.5`, pronouncing `0.2.0`
- **Data & Math**: Pandas `3.0.1`, NumPy `1.26.4`
- **Database**: SQLAlchemy `2.0.47` + Alembic `1.18.4`

---

## 📁 Project Architecture

The system utilizes a structured, modern MVC-style architecture fully migrated to FastAPI:

```text
poetry-analyzer-app/
├── alembic/                # Database migration scripts and versions
├── alembic.ini             # Alembic configuration
├── app/                    # Primary Application Logic
│   ├── api/                # API routers and endpoints
│   ├── models/             # SQLAlchemy ORM models & Pydantic schemas
│   ├── services/           # Core NLP logic (linguistic, prosody, quantitative, transformers)
│   ├── utils/              # Helper functions
│   ├── config.py           # Pydantic Settings management
│   ├── database.py         # SQLAlchemy engine setup
│   ├── main.py             # FastAPI application entrypoint
│   └── route_registry.py   # Named route resolution
├── controllers/            # View data binding for full-stack templates
├── routes/                 # Web route definitions mapping URLs to controllers
├── static/                 # CSS/JS assets
├── templates/              # Jinja2 HTML templates
├── requirements.txt        # Strictly pinned dependencies
├── setup_models.py         # Post-install model downloader (reads .env)
└── verify_app.py           # Integration test suite
```
