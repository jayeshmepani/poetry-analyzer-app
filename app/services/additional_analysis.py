"""
Additional Analysis Modules
Dialect Detection, Discourse Analysis, Text Correction, Idiom/Proverb Detection
Based on ultimate_literary_master_system.md
"""

import os
import re
import logging
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Route HuggingFace model cache to local project directory (not C: drive)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.environ.setdefault("HF_HOME", str(_PROJECT_ROOT / ".huggingface_cache"))

from transformers import pipeline
from app.config import settings
from app.services.label_loader import get_labels
from app.services.rule_loader import get_thresholds, get_performance_rules

logger = logging.getLogger(__name__)

# ==================== SENTIMENT & EMOTION (Transformers) ====================

class TransformerAnalyzer:
    """
    Advanced sentiment and emotion analysis using BERT/Transformer models
    """

    _PIPELINE_CACHE: Dict[Tuple[str, str], Any] = {}
    _INIT_LOCK = threading.Lock()

    def __init__(self, language: str = "en"):
        self.language = language
        self._sentiment_pipe = None
        self._emotion_pipe = None
        self._sentiment_task = "sentiment-analysis"
        self._emotion_task = "text-classification"
        self._initialized = False

    def _is_english_route(self) -> bool:
        lang = (self.language or "").strip().lower()
        return lang in {c.lower() for c in settings.transformer.english_language_codes}

    def _is_indic_route(self) -> bool:
        lang = (self.language or "").strip().lower()
        return lang in {c.lower() for c in settings.transformer.indic_language_codes}

    def _route_profile(self) -> str:
        if self._is_english_route():
            return "english"
        if self._is_indic_route():
            return "indic"
        return "generalist"

    def _normalize_sentiment_label(self, raw_label: str) -> str:
        label = str(raw_label or "").strip()
        if not label:
            return "UNKNOWN"
        mapped = settings.transformer.multilingual_sentiment_label_map.get(label)
        if mapped:
            return mapped
        mapped_ci = settings.transformer.multilingual_sentiment_label_map.get(label.lower())
        if mapped_ci:
            return mapped_ci
        return label.upper()

    def _initialize_models(self):
        # Alias for _initialize_pipelines to maintain consistency if needed
        self._initialize_pipelines()

    def _get_cached_pipeline(self, task: str, model_name: str, device: int, **kwargs):
        cache_key = (task, model_name)
        if cache_key in self._PIPELINE_CACHE:
            logger.info("[additional][transformer] cache hit: %s (%s)", model_name, task)
            return self._PIPELINE_CACHE[cache_key]
        t0 = time.perf_counter()
        built = pipeline(task, model=model_name, device=device, **kwargs)
        self._PIPELINE_CACHE[cache_key] = built
        logger.info(
            "[additional][transformer] pipeline loaded: %s (%s) in %.2fs",
            model_name,
            task,
            time.perf_counter() - t0,
        )
        return built

    def _initialize_pipelines(self, progress_cb=None):
        """Initialize transformer pipelines lazily with multilingual routing."""
        if self._initialized:
            return
        with self._INIT_LOCK:
            if self._initialized:
                return
            self._initialized = True
            t0_total = time.perf_counter()
            try:
                import torch
                device = 0 if torch.cuda.is_available() else -1
                profile = self._route_profile()
                if progress_cb:
                    progress_cb(70, f"Transformer: loading {profile} models...")
                if profile == "english":
                    logger.info(
                        f"Loading English transformer pipelines: "
                        f"{settings.transformer.sentiment_model} + {settings.transformer.emotion_model}"
                    )
                    self._sentiment_task = "sentiment-analysis"
                    self._emotion_task = "text-classification"
                    self._sentiment_pipe = self._get_cached_pipeline(
                        "sentiment-analysis",
                        settings.transformer.sentiment_model,
                        device,
                    )
                    if progress_cb:
                        progress_cb(75, "Transformer: sentiment model ready")
                    self._emotion_pipe = self._get_cached_pipeline(
                        "text-classification",
                        settings.transformer.emotion_model,
                        device,
                        top_k=None,
                    )
                elif profile == "indic":
                    logger.info(
                        f"Loading Indic transformer pipelines: "
                        f"{settings.transformer.indic_sentiment_model} + "
                        f"{settings.transformer.indic_emotion_model}"
                    )
                    try:
                        self._sentiment_task = "sentiment-analysis"
                        self._sentiment_pipe = self._get_cached_pipeline(
                            "sentiment-analysis",
                            settings.transformer.indic_sentiment_model,
                            device,
                        )
                        if progress_cb:
                            progress_cb(75, "Transformer: sentiment model ready")
                    except Exception:
                        logger.warning(
                            "Indic sentiment model failed for sentiment-analysis. "
                            "Falling back to generalist zero-shot."
                        )
                        self._sentiment_task = "zero-shot-classification"
                        self._sentiment_pipe = self._get_cached_pipeline(
                            "zero-shot-classification",
                            settings.transformer.generalist_zero_shot_model,
                            device,
                        )
                    self._emotion_task = settings.transformer.indic_emotion_mode
                    if self._emotion_task == "zero-shot-classification":
                        self._emotion_pipe = self._get_cached_pipeline(
                            "zero-shot-classification",
                            settings.transformer.indic_emotion_model,
                            device,
                        )
                    else:
                        try:
                            self._emotion_pipe = self._get_cached_pipeline(
                                "text-classification",
                                settings.transformer.indic_emotion_model,
                                device,
                                top_k=None,
                            )
                            self._emotion_task = "text-classification"
                        except Exception:
                            logger.warning(
                                "Indic emotion model does not expose text-classification head. "
                                "Falling back to generalist zero-shot."
                            )
                            self._emotion_task = "zero-shot-classification"
                            self._emotion_pipe = self._get_cached_pipeline(
                                "zero-shot-classification",
                                settings.transformer.generalist_zero_shot_model,
                                device,
                            )
                else:
                    logger.info(
                        f"Loading generalist zero-shot model: {settings.transformer.generalist_zero_shot_model}"
                    )
                    self._sentiment_task = "zero-shot-classification"
                    self._emotion_task = "zero-shot-classification"
                    self._sentiment_pipe = self._get_cached_pipeline(
                        "zero-shot-classification",
                        settings.transformer.generalist_zero_shot_model,
                        device,
                    )
                    self._emotion_pipe = self._sentiment_pipe
                logger.info("Transformer pipelines initialized successfully in %.2fs", time.perf_counter() - t0_total)
                if progress_cb:
                    progress_cb(78, "Transformer: models initialized")
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.warning(f"Transformer initialization failed: {e}")

    def analyze(self, text: str, progress_cb=None) -> Dict[str, Any]:
        """Perform sentiment and emotion analysis"""
        # Lazy-load models on first call (avoids debug reloader loading 2x ~3GB)
        if not self._initialized:
            self._initialize_pipelines(progress_cb=progress_cb)
        if not self._sentiment_pipe:
            return {"status": "unsupported_or_failed", "sentiment": {}, "emotions": {}}

        try:
            # Truncate text if too long for transformer (512 tokens approx)
            perf_rules = get_performance_rules()
            max_chars = perf_rules.get("analysis_input_max_chars") if perf_rules else None
            truncated_text = text if max_chars is None else text[: int(max_chars)]
            
            t0 = time.perf_counter()
            if progress_cb:
                progress_cb(82, "Transformer: sentiment inference...")
            if self._sentiment_task == "zero-shot-classification":
                zs_sent = self._sentiment_pipe(
                    truncated_text,
                    candidate_labels=settings.transformer.generalist_sentiment_labels,
                    multi_label=False,
                )
                sentiment_label = self._normalize_sentiment_label(
                    (zs_sent.get("labels") or ["UNKNOWN"])[0]
                )
                sentiment_score = round(float((zs_sent.get("scores") or [0.0])[0]), 4)
            else:
                sentiment_res = self._sentiment_pipe(truncated_text)[0]
                sentiment_label = self._normalize_sentiment_label(sentiment_res.get("label", ""))
                sentiment_score = round(float(sentiment_res.get("score", 0.0)), 4)
            logger.info("[additional][transformer] sentiment %.2fs", time.perf_counter() - t0)

            t0 = time.perf_counter()
            if progress_cb:
                progress_cb(90, "Transformer: emotion/NLI inference...")
            if self._emotion_task == "text-classification" and self._emotion_pipe:
                emotion_res = self._emotion_pipe(truncated_text)[0]
                emotions = {
                    item["label"].lower(): round(float(item["score"]), 4)
                    for item in emotion_res
                }
            else:
                candidate_labels = settings.transformer.multilingual_emotion_labels
                zs = self._emotion_pipe(
                    truncated_text,
                    candidate_labels=candidate_labels,
                    multi_label=True,
                )
                emotions = {
                    lbl.lower(): round(float(score), 4)
                    for lbl, score in zip(zs.get("labels", []), zs.get("scores", []))
                }
            logger.info("[additional][transformer] emotions %.2fs", time.perf_counter() - t0)
            if progress_cb:
                progress_cb(100, "Transformer: analysis complete")
            
            return {
                "status": "ok",
                "sentiment": {
                    "label": sentiment_label,
                    "score": sentiment_score,
                },
                "emotions": emotions,
                "dominant_emotion": max(emotions, key=emotions.get) if emotions else "unknown",
                "route_profile": self._route_profile(),
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Transformer analysis failed: {e}")
            return {"status": "failed", "error": str(e)}

class DialectDetector:
    """Detect Hindi/Indic dialects and language varieties"""

    def __init__(self):
        self._zero_shot = None

    def _ensure_zero_shot(self):
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            self._zero_shot = pipeline(
                "zero-shot-classification",
                model=settings.transformer.generalist_zero_shot_model,
                device=-1,
            )
        except Exception:
            self._zero_shot = None
        return self._zero_shot

    def detect(self, text: str) -> Dict[str, Any]:
        """Detect dialect from text"""
        zs = self._ensure_zero_shot()
        labels = get_labels("dialect")
        if not zs:
            return {"detected": "unknown", "confidence": 0.0}
        if not labels:
            return {"detected": "unknown", "confidence": 0.0}
        try:
            out = zs(text, labels)
            top_label = out["labels"][0]
            top_score = float(out["scores"][0])
            scores = {label: float(score) for label, score in zip(out["labels"], out["scores"])}
            return {
                "detected_dialect": top_label,
                "confidence": round(top_score, 3),
                "all_scores": scores,
                "marker_count": int(round(top_score * 100)),
            }
        except Exception:
            return {"detected": "unknown", "confidence": 0.0}


# ==================== DISCOURSE ANALYSIS ====================

class DiscourseAnalyzer:
    """
    Analyze discourse using Halliday & Hasan cohesive devices
    """

    def __init__(self):
        self._nlp = None

    def _ensure_nlp(self):
        if self._nlp is not None:
            return self._nlp
        try:
            import spacy
            self._nlp = spacy.load(settings.spacy.english_model)
        except Exception:
            self._nlp = None
        return self._nlp

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze discourse cohesion"""
        words = text.lower().split()
        doc = None
        nlp = self._ensure_nlp()
        if nlp:
            doc = nlp(text)
        
        results = {
            "reference": self._analyze_reference(words, doc),
            "substitution": self._analyze_substitution(words, doc),
            "conjunction": self._analyze_conjunction(words, doc),
            "lexical_cohesion": self._analyze_lexical_cohesion(words),
            "coherence_score": 0.0
        }
        
        # Calculate overall coherence
        total_cohesion = (
            results["reference"]["count"] +
            results["substitution"]["count"] +
            results["conjunction"]["count"] +
            results["lexical_cohesion"]["count"]
        )
        
        results["coherence_score"] = min(1.0, total_cohesion / len(words) * 10) if words else 0
        
        return results

    def _analyze_reference(self, words: List[str], doc) -> Dict[str, Any]:
        """Analyze reference devices (pronoun-based)"""
        if doc is None:
            return {"anaphoric": 0, "cataphoric": 0, "exophoric": 0, "count": 0}
        pronouns = [t for t in doc if t.pos_ == "PRON"]
        return {
            "anaphoric": len(pronouns),
            "cataphoric": 0,
            "exophoric": 0,
            "count": len(pronouns)
        }

    def _analyze_substitution(self, words: List[str], doc) -> Dict[str, Any]:
        """Analyze substitution devices (auxiliaries as proxy)"""
        if doc is None:
            return {"count": 0, "instances": []}
        aux = [t.text.lower() for t in doc if t.pos_ == "AUX"]
        return {"count": len(aux), "instances": aux[:10]}

    def _analyze_conjunction(self, words: List[str], doc) -> Dict[str, Any]:
        """Analyze conjunction devices (POS-based)"""
        if doc is None:
            return {"additive": 0, "adversative": 0, "causal": 0, "temporal": 0, "count": 0}
        conj = [t for t in doc if t.pos_ in {"CCONJ", "SCONJ"}]
        return {
            "additive": len(conj),
            "adversative": 0,
            "causal": 0,
            "temporal": 0,
            "count": len(conj)
        }

    def _analyze_lexical_cohesion(self, words: List[str]) -> Dict[str, Any]:
        """Analyze lexical cohesion (repetition)"""
        from collections import Counter
        word_freq = Counter(words)
        repeated = sum(1 for count in word_freq.values() if count > 1)
        return {
            "repeated_words": repeated,
            "count": repeated
        }


# ==================== TEXT CORRECTION ====================

class TextCorrector:
    """
    Correct and enhance text
    """

    def __init__(self):
        self._lexicon_by_letter = {}
        try:
            from nltk.corpus import wordnet as wn
            for syn in wn.all_synsets():
                for lemma in syn.lemma_names():
                    w = lemma.replace("_", " ").lower()
                    if not w or " " in w:
                        continue
                    self._lexicon_by_letter.setdefault(w[0], set()).add(w)
        except Exception:
            self._lexicon_by_letter = {}

    def correct(self, text: str) -> Dict[str, Any]:
        """Correct text errors"""
        words = text.split()
        corrected = []
        corrections = []
        
        for i, word in enumerate(words):
            clean = re.sub(r'[^a-zA-Z]', '', word)
            if clean:
                pool = self._lexicon_by_letter.get(clean.lower()[:1], set())
                if clean.lower() not in pool and pool:
                    import difflib
                    matches = difflib.get_close_matches(clean.lower(), list(pool), n=1, cutoff=0.88)
                else:
                    matches = []
            else:
                matches = []

            if matches:
                correction = matches[0]
                # Preserve capitalization
                if clean[0].isupper():
                    correction = correction.capitalize()
                corrected_word = word.replace(clean, correction)
                corrected.append(corrected_word)
                corrections.append({
                    "original": clean,
                    "corrected": correction,
                    "position": i
                })
            else:
                corrected.append(word)
        
        return {
            "original_text": text,
            "corrected_text": " ".join(corrected),
            "corrections": corrections,
            "correction_count": len(corrections)
        }

    def enhance(self, text: str) -> Dict[str, Any]:
        """Enhance text with varied vocabulary"""
        words = text.split()
        enhanced = []
        enhancements = []
        try:
            from nltk.corpus import wordnet as wn
        except Exception:
            wn = None
        
        for i, word in enumerate(words):
            clean = re.sub(r'[^a-zA-Z]', '', word)
            if wn and clean and i % 3 == 0:
                syns = wn.synsets(clean.lower())
                candidates = []
                for syn in syns:
                    for lemma in syn.lemmas():
                        cand = lemma.name().replace("_", " ")
                        if cand.lower() != clean.lower():
                            candidates.append(cand)
                if candidates:
                    enhancement = candidates[0]
                    if clean[0].isupper():
                        enhancement = enhancement.capitalize()
                    enhanced_word = word.replace(clean, enhancement)
                    enhanced.append(enhanced_word)
                    enhancements.append({
                        "original": clean,
                        "enhanced": enhancement,
                        "position": i
                    })
                    continue
            enhanced.append(word)
        
        return {
            "original_text": text,
            "enhanced_text": " ".join(enhanced),
            "enhancements": enhancements,
            "enhancement_count": len(enhancements)
        }


# ==================== IDIOM & PROVERB DETECTION ====================

class IdiomProverbDetector:
    """
    Detect idioms and proverbs in multiple languages
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self._zero_shot = None

    def _ensure_zero_shot(self):
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            self._zero_shot = pipeline(
                "zero-shot-classification",
                model=settings.transformer.generalist_zero_shot_model,
                device=-1,
            )
        except Exception:
            self._zero_shot = None
        return self._zero_shot

    def detect(self, text: str) -> Dict[str, Any]:
        """Detect idioms and proverbs"""
        zs = self._ensure_zero_shot()
        idioms_found = []
        proverbs_found = []
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        thresholds = get_thresholds()
        min_conf = thresholds.get("idiom_proverb_confidence")
        if min_conf is None:
            return {
                "language": self.language,
                "idioms_found": [],
                "idiom_count": 0,
                "proverbs_found": [],
                "proverb_count": 0,
                "total_found": 0,
            }
        if zs:
            for line in lines:
                try:
                    idiom_labels = get_labels("idiom")
                    proverb_labels = get_labels("proverb")
                    if not idiom_labels or not proverb_labels:
                        continue
                    idiom_out = zs(line, idiom_labels)
                    proverb_out = zs(line, proverb_labels)
                    if idiom_out["scores"][0] >= min_conf:
                        idioms_found.append(line)
                    if proverb_out["scores"][0] >= min_conf:
                        proverbs_found.append(line)
                except Exception:
                    continue

        return {
            "language": self.language,
            "idioms_found": idioms_found[:10],
            "idiom_count": len(idioms_found),
            "proverbs_found": proverbs_found[:10],
            "proverb_count": len(proverbs_found),
            "total_found": len(idioms_found) + len(proverbs_found)
        }


# ==================== PRAGMATICS ANALYSIS ====================

class PragmaticsAnalyzer:
    """
    Analyze pragmatics: illocutionary force, politeness, speech acts
    Based on ultimate_literary_master_system.md Dimension 1.8
    """

    def __init__(self):
        self._zero_shot = None

    def _ensure_zero_shot(self):
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            self._zero_shot = pipeline(
                "zero-shot-classification",
                model=settings.transformer.generalist_zero_shot_model,
                device=-1,
            )
        except Exception:
            self._zero_shot = None
        return self._zero_shot

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze pragmatics of text"""
        zs = self._ensure_zero_shot()
        speech_labels = get_labels("speech_acts")
        politeness_labels = get_labels("politeness")
        if not speech_labels:
            speech_labels = []
        if not politeness_labels:
            politeness_labels = []
        speech_acts = {k: 0.0 for k in speech_labels}
        politeness = {k: 0.0 for k in politeness_labels}

        if zs and speech_labels:
            try:
                out = zs(text, speech_labels)
                speech_acts = {label: float(score) for label, score in zip(out["labels"], out["scores"])}
            except Exception:
                pass
        if zs and politeness_labels:
            try:
                out = zs(text, politeness_labels)
                politeness = {label: float(score) for label, score in zip(out["labels"], out["scores"])}
            except Exception:
                pass

        dominant_act = max(speech_acts, key=speech_acts.get) if speech_acts else "unknown"
        politeness_level = max(politeness, key=politeness.get) if politeness else "neutral"

        thresholds = get_thresholds()
        min_conf = thresholds.get("zero_shot_min_confidence")
        if min_conf is None:
            illocutionary_force = "moderate"
        else:
            illocutionary_force = "strong" if any(v > min_conf for v in speech_acts.values()) else "moderate"

        return {
            "speech_acts": {
                "counts": speech_acts,
                "dominant_act": dominant_act
            },
            "politeness_strategies": {
                "counts": politeness,
                "politeness_level": politeness_level
            },
            "illocutionary_force": illocutionary_force,
            "implicatures_detected": []
        }


# ==================== COMBINED ANALYSIS FUNCTION ====================

def run_additional_analyses(
    text: str,
    language: str = "en",
    progress_cb=None,
) -> Dict[str, Any]:
    """
    Run all additional analysis modules
    
    Args:
        text: Text to analyze
        language: Language code (en, hi, gu)
    
    Returns:
        Combined analysis results
    """
    def update(pct: int, message: str) -> None:
        if progress_cb:
            progress_cb(int(pct), message)

    t0_total = time.perf_counter()
    dialect_detector = DialectDetector()
    discourse_analyzer = DiscourseAnalyzer()
    text_corrector = TextCorrector()
    idiom_detector = IdiomProverbDetector(language)
    pragmatics_analyzer = PragmaticsAnalyzer()
    transformer_analyzer = TransformerAnalyzer(language)

    update(5, "Additional: dialect detection...")
    t0 = time.perf_counter()
    dialect = dialect_detector.detect(text)
    logger.info("[additional] dialect %.2fs", time.perf_counter() - t0)

    update(15, "Additional: discourse analysis...")
    t0 = time.perf_counter()
    discourse = discourse_analyzer.analyze(text)
    logger.info("[additional] discourse %.2fs", time.perf_counter() - t0)

    update(30, "Additional: text correction...")
    t0 = time.perf_counter()
    correction = text_corrector.correct(text)
    logger.info("[additional] text_correction %.2fs", time.perf_counter() - t0)

    update(40, "Additional: text enhancement...")
    t0 = time.perf_counter()
    enhancement = text_corrector.enhance(text)
    logger.info("[additional] text_enhancement %.2fs", time.perf_counter() - t0)

    update(55, "Additional: idioms & proverbs...")
    t0 = time.perf_counter()
    idioms = idiom_detector.detect(text)
    logger.info("[additional] idioms_proverbs %.2fs", time.perf_counter() - t0)

    update(65, "Additional: pragmatics...")
    t0 = time.perf_counter()
    pragmatics = pragmatics_analyzer.analyze(text)
    logger.info("[additional] pragmatics %.2fs", time.perf_counter() - t0)

    update(75, "Additional: transformer analysis...")
    t0 = time.perf_counter()
    transformer = transformer_analyzer.analyze(text, progress_cb=progress_cb)
    logger.info("[additional] transformer_analysis %.2fs", time.perf_counter() - t0)

    update(100, "Additional: complete")
    logger.info("[additional] total %.2fs", time.perf_counter() - t0_total)

    return {
        "dialect_detection": dialect,
        "discourse_analysis": discourse,
        "text_correction": correction,
        "text_enhancement": enhancement,
        "idioms_proverbs": idioms,
        "pragmatics": pragmatics,
        "transformer_analysis": transformer,
    }
