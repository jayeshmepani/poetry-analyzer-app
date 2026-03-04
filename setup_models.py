"""
Post-Installation Model Setup
==============================
Downloads all required NLP models defined in the .env configuration.

Usage:
    python setup_models.py

This script should be run once after `pip install -r requirements.txt`.
It reads model names directly from your .env (or falls back to defaults)
so the downloaded models always stay in sync with your configuration.
"""

import subprocess
import sys
import os
import logging
import json
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_env(path: Optional[str] = None) -> dict:
    """Lightweight .env parser (no external dependency required)."""
    env = {}
    candidates: List[str] = [path] if path else [".env", ".env.example"]
    chosen = next((p for p in candidates if p and os.path.exists(p)), None)
    if not chosen:
        logger.warning(".env/.env.example not found — using defaults")
        return env
    logger.info(f"Loading configuration from {chosen}")
    with open(chosen, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def parse_json_env(raw: Optional[str], fallback: Any) -> Any:
    if raw is None:
        return fallback
    try:
        return json.loads(raw)
    except Exception:
        return fallback


def env_or_default(env: Dict[str, str], key: str, default: str) -> str:
    value = env.get(key, default)
    return str(value).strip().strip('"').strip("'")


def download_spacy_models(env: dict) -> None:
    """Download spaCy models listed in env configuration."""
    import spacy

    models = [
        env.get("SPACY_ENGLISH_MODEL", "en_core_web_trf"),
        env.get("SPACY_MULTILINGUAL_MODEL", "xx_sent_ud_sm"),
    ]

    for model in models:
        # Skip download if already installed and loadable.
        if spacy.util.is_package(model):
            try:
                spacy.load(model)
                logger.info(f"spaCy model already installed: {model} (skip)")
                continue
            except Exception as e:
                logger.warning(f"spaCy package exists but failed to load ({model}): {e}. Retrying download.")

        logger.info(f"Downloading spaCy model: {model}")
        result = subprocess.run(
            [sys.executable, "-m", "spacy", "download", model],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info(f"  ✓ {model} installed successfully")
        else:
            logger.error(f"  ✗ {model} failed: {result.stderr.strip()}")


def download_nltk_data() -> None:
    """Download required NLTK datasets."""
    import nltk

    packages = ["punkt", "punkt_tab", "averaged_perceptron_tagger"]
    for pkg in packages:
        logger.info(f"Downloading NLTK data: {pkg}")
        nltk.download(pkg, quiet=True)
    logger.info("  ✓ NLTK data downloaded")


def prefetch_transformer_models(env: dict) -> None:
    """
    Pre-download HuggingFace transformer models so the first analysis
    doesn't block for several minutes. These are cached to HF_HOME.
    """
    hf_home = env.get("HF_HOME")
    if hf_home:
        os.environ["HF_HOME"] = hf_home

    # Model bundle aligned with app/config.py + .env(.example), with task-aware prefetch.
    indic_emotion_mode = env_or_default(
        env, "TRANSFORMER_INDIC_EMOTION_MODE", "zero-shot-classification"
    )
    if indic_emotion_mode not in {"text-classification", "zero-shot-classification"}:
        indic_emotion_mode = "zero-shot-classification"

    models = [
        (
            "english_sentiment",
            env_or_default(
                env, "TRANSFORMER_SENTIMENT_MODEL", "siebert/sentiment-roberta-large-english"
            ),
            "sentiment-analysis",
        ),
        (
            "english_emotion",
            env_or_default(
                env, "TRANSFORMER_EMOTION_MODEL", "duelker/samo-goemotions-deberta-v3-large"
            ),
            "text-classification",
        ),
        (
            "multilingual_sentiment",
            env_or_default(
                env, "TRANSFORMER_MULTILINGUAL_SENTIMENT_MODEL", "cardiffnlp/twitter-xlm-roberta-base-sentiment"
            ),
            "sentiment-analysis",
        ),
        (
            "multilingual_emotion",
            env_or_default(
                env,
                "TRANSFORMER_MULTILINGUAL_EMOTION_MODEL",
                "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
            ),
            "zero-shot-classification",
        ),
        (
            "indic_sentiment",
            env_or_default(
                env, "TRANSFORMER_INDIC_SENTIMENT_MODEL", "cardiffnlp/twitter-xlm-roberta-base-sentiment"
            ),
            "sentiment-analysis",
        ),
        (
            "indic_emotion",
            env_or_default(
                env,
                "TRANSFORMER_INDIC_EMOTION_MODEL",
                "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
            ),
            indic_emotion_mode,
        ),
        (
            "generalist_zero_shot",
            env_or_default(
                env,
                "TRANSFORMER_GENERALIST_ZERO_SHOT_MODEL",
                "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
            ),
            "zero-shot-classification",
        ),
    ]

    for label, model_name, task in models:
        logger.info(f"Pre-downloading {label}: {model_name} (task={task})")
        try:
            from transformers import pipeline
            p = pipeline(task=task, model=model_name, device=-1)
            _ = p  # keep explicit reference to trigger full model+tokenizer load
            logger.info(f"  ✓ {model_name} cached successfully")
        except Exception as e:
            logger.error(f"  ✗ {model_name} failed (task={task}): {e}")


def setup_stanza_resources(env: dict) -> None:
    """Prepare writable Stanza resources directory and download configured languages."""
    resources_dir = env_or_default(env, "STANZA_RESOURCES_DIR", ".stanza_cache")
    os.environ["STANZA_RESOURCES_DIR"] = resources_dir
    os.makedirs(resources_dir, exist_ok=True)

    langs = parse_json_env(env.get("STANZA_LANGUAGES"), ["en", "hi", "gu", "ur"])
    processors = env_or_default(env, "STANZA_PROCESSORS", "tokenize,pos,lemma,depparse")
    if not isinstance(langs, list):
        langs = ["en", "hi", "gu", "ur"]

    try:
        import stanza
        from stanza.resources.common import UnknownLanguageError

        downloaded = 0
        skipped = 0
        for lang in langs:
            lang_code = str(lang).strip()
            if not lang_code:
                continue
            logger.info(f"Downloading Stanza resources: lang={lang_code} processors={processors}")
            try:
                stanza.download(
                    lang=lang_code,
                    processors=processors,
                    model_dir=resources_dir,
                    verbose=False,
                )
                downloaded += 1
            except UnknownLanguageError:
                skipped += 1
                logger.warning(f"Stanza language not available in this version: {lang_code} (skipped)")
            except Exception as lang_err:
                skipped += 1
                logger.warning(f"Stanza download failed for {lang_code}: {lang_err} (skipped)")
        logger.info(f"  ✓ Stanza resources processed (downloaded={downloaded}, skipped={skipped})")
    except Exception as e:
        logger.warning(f"Stanza resource setup skipped/failed: {e}")


def main() -> None:
    print("=" * 60)
    print("  Poetry Analyzer — Model Setup")
    print("=" * 60)

    env = load_env()

    # 1. spaCy models
    print("\n[1/4] spaCy models")
    download_spacy_models(env)

    # 2. NLTK data
    print("\n[2/4] NLTK data")
    download_nltk_data()

    # 3. Stanza resources
    print("\n[3/4] Stanza resources")
    setup_stanza_resources(env)

    # 4. Transformer models (optional, large download)
    print("\n[4/4] Transformer models (this may take a while)")
    prefetch_transformer_models(env)

    print("\n" + "=" * 60)
    print("  Setup complete! You can now run the application.")
    print("=" * 60)


if __name__ == "__main__":
    main()
