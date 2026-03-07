"""
Linguistic Analysis Module
Complete implementation with spaCy, Stanza, NLTK, Indic NLP support
Based on Ultimate Literary Master System - Dimension 1

Uses ALL libraries from requirements.txt:
- spaCy: Core NLP pipeline
- NLTK: Tokenization, lexical resources
- Stanza: Multilingual NLP (60+ languages)
- Indic NLP: Hindi, Gujarati, etc.
- transformers: BERT embeddings
- textacy: Advanced text features
- textdescriptives: Text metrics
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from collections import Counter
import logging
import time

# Import ALL libraries from requirements.txt
import spacy
import nltk
import stanza

# textacy removed - Python 3.13 compatibility issues
# import textacy
import textdescriptives
from transformers import pipeline

# gensim removed - Python 3.13 compatibility issues
# from gensim import corpora, models
from indicnlp.tokenize import indic_tokenize
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from app.services.iwn_resources import (
    iwn_runtime_supported,
    get_iwn_language_enum,
    resolve_iwn_data_dir,
    silence_pyiwn_info_logs,
)
from app.services.rule_loader import get_output_limits

logger = logging.getLogger(__name__)

try:
    import pronouncing as _pronouncing
except Exception:
    _pronouncing = None


class LinguisticAnalyzer:
    """
    Comprehensive linguistic analysis using spaCy, Stanza, and Indic NLP
    Supports: English, Hindi, Gujarati, Urdu, and other Indic languages
    """

    def __init__(
        self, language: str = "en", use_spacy: bool = True, use_stanza: bool = True
    ):
        self.language = language
        self.use_spacy = use_spacy
        self.use_stanza = use_stanza
        self.nlp = None
        self.stanza_nlp = None
        self.text = ""
        self.words: List[str] = []
        self.sentences: List[str] = []
        self.lines: List[str] = []
        self._zero_shot = None
        self._limits = get_output_limits()
        from app.config import Settings
        self._settings = Settings()

        # Initialize NLP models
        self._initialize_models()
        self._initialize_lexical_resources()

    def _limit(self, items: List[Any], key: str) -> List[Any]:
        limit = self._limits.get(key) if self._limits else None
        return items[: int(limit)] if limit is not None else items

    def _initialize_lexical_resources(self) -> None:
        """Initialize WordNet / IndoWordNet resources based on language."""
        self._wn = None
        self._iwn = None
        if self.language == "en":
            try:
                from nltk.corpus import wordnet as wn
                self._wn = wn
            except Exception as e:
                logger.info(f"NLTK WordNet not active in this environment: {e}")
        if self.language in ["hi", "gu", "ur", "mr", "bn", "sa", "ta", "te", "kn", "ml", "pa"]:
            if not iwn_runtime_supported(self.language):
                logger.info(
                    "IndoWordNet is disabled for language '%s' in this runtime.",
                    self.language,
                )
                return
            try:
                silence_pyiwn_info_logs()
                from pyiwn import IndoWordNet
                import pyiwn.constants as constants
                from app.config import settings

                iwn_dir = str(resolve_iwn_data_dir())
                os.makedirs(iwn_dir, exist_ok=True)
                constants.USER_HOME = os.path.dirname(iwn_dir)
                constants.IWN_DATA_PATH = iwn_dir
                constants.IWN_DATA_TEMP_PATH = os.path.join(constants.USER_HOME, "iwn_data.tar.gz")

                lang_enum = get_iwn_language_enum(self.language)
                if lang_enum is None:
                    return
                self._iwn = IndoWordNet(lang=lang_enum)
            except Exception as e:
                logger.info(f"IndoWordNet not active in this runtime: {e}")

    def _initialize_models(self):
        """Initialize spaCy and Stanza models"""
        # spaCy initialization - use installed models only
        if self.use_spacy:
            settings = self._settings
            if self.language == "en":
                # Use transformer model for English
                try:
                    self.nlp = spacy.load(settings.spacy.english_model)
                    logger.info(f"Loaded spaCy model: {settings.spacy.english_model}")
                except OSError as e:
                    logger.warning(f"English spaCy model could not be loaded: {e}")
                    self.nlp = None
            else:
                # Use multilingual model for non-English languages
                try:
                    self.nlp = spacy.load(settings.spacy.multilingual_model)
                    logger.info(
                        f"Loaded spaCy multilingual model: {settings.spacy.multilingual_model} "
                        f"for language '{self.language}'"
                    )
                except OSError as e:
                    logger.warning(f"Multilingual spaCy model could not be loaded: {e}")
                    self.nlp = None

        # Stanza initialization for multilingual fallback/dependency analysis
        if self.use_stanza:
            try:
                from app.config import settings
                lang_code = self._get_stanza_lang_code()
                resources_dir = Path(settings.stanza.resources_dir).resolve()
                resources_dir.mkdir(parents=True, exist_ok=True)
                os.environ["STANZA_RESOURCES_DIR"] = str(resources_dir)
                self.stanza_nlp = stanza.Pipeline(
                    lang=lang_code,
                    processors="tokenize,pos,lemma,depparse",
                    verbose=False,
                    dir=str(resources_dir),
                )
                logger.info(f"Loaded Stanza pipeline for {lang_code}")
            except Exception as e:
                logger.info(f"Stanza pipeline not initialized for this runtime: {e}")
                self.stanza_nlp = None

    def _ensure_zero_shot(self):
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            model_name = self._settings.transformer.generalist_zero_shot_model
            self._zero_shot = pipeline("zero-shot-classification", model=model_name, device=-1)
        except Exception as e:
            logger.info(f"Zero-shot pipeline not initialized in linguistic analyzer: {e}")
            self._zero_shot = None
        return self._zero_shot

    def _get_stanza_lang_code(self) -> str:
        """Convert language code to Stanza format"""
        lang_map = {
            "en": "en",
            "hi": "hi",
            "gu": "gu",
            "ur": "ur",
            "mr": "mr",
            "bn": "bn",
            "ta": "ta",
            "te": "te",
            "ml": "ml",
            "kn": "kn",
        }
        return lang_map.get(self.language, "en")

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete linguistic analysis"""
        start = time.perf_counter()
        self.text = text
        logger.info("[linguistic] preprocess start")
        self._preprocess()
        logger.info("[linguistic] preprocess done in %.2fs", time.perf_counter() - start)

        # Use spaCy if available (en_core_web_trf for English, xx_sent_ud_sm for others)
        if self.nlp:
            logger.info("[linguistic] spaCy analysis start")
            result = self._analyze_with_spacy()
            logger.info("[linguistic] spaCy analysis done in %.2fs", time.perf_counter() - start)
            return result
        elif self.stanza_nlp:
            logger.info("[linguistic] Stanza analysis start")
            result = self._analyze_with_stanza()
            logger.info("[linguistic] Stanza analysis done in %.2fs", time.perf_counter() - start)
            return result
        else:
            logger.info("[linguistic] Rule-based analysis start")
            result = self._analyze_rule_based()
            logger.info("[linguistic] Rule-based analysis done in %.2fs", time.perf_counter() - start)
            return result

    def _preprocess(self):
        """Preprocess text into words, lines, sentences"""
        # Apply Indic Normalization if applicable
        if self.language in ["hi", "gu", "mr", "bn", "sa", "ur"]:
            try:
                t0 = time.perf_counter()
                if self.language == "ur":
                    # IndicNormalizerFactory for Urdu may require optional extras;
                    # gracefully skip when unavailable.
                    try:
                        import urduhack  # type: ignore

                        self.text = urduhack.normalization.normalize(self.text)
                    except Exception:
                        pass
                else:
                    factory = IndicNormalizerFactory()
                    normalizer = factory.get_normalizer(self.language)
                    self.text = normalizer.normalize(self.text)
                logger.info("[linguistic] indic normalization %.2fs", time.perf_counter() - t0)
            except Exception as e:
                logger.info(f"Indic normalization skipped for language '{self.language}': {e}")

        self.lines = [line.strip() for line in self.text.split("\n") if line.strip()]

        if self.language in ["hi", "gu", "mr", "bn", "sa"]:
            # Use Indic Tokenizer
            try:
                self.words = indic_tokenize.trivial_tokenize(self.text, self.language)
            except:
                self.words = re.findall(
                    r"[\u0900-\u097F\u0A80-\u0AFF\u0D00-\u0D7F]+", self.text
                )
        else:
            self.words = re.findall(r"\b[a-zA-Z]+\b", self.text.lower())

        # Use spaCy for sentence segmentation if available
        if self.nlp:
            t0 = time.perf_counter()
            doc = self.nlp(self.text)
            self.sentences = [
                sent.text.strip() for sent in doc.sents if sent.text.strip()
            ]
            logger.info("[linguistic] spaCy sentence segmentation %.2fs", time.perf_counter() - t0)
        else:
            try:
                t0 = time.perf_counter()
                self.sentences = nltk.sent_tokenize(self.text)
                if not self.words: # If indic tokenizer wasn't used
                    self.words = nltk.word_tokenize(self.text.lower())
                logger.info("[linguistic] NLTK sentence/word tokenization %.2fs", time.perf_counter() - t0)
            except Exception as e:
                logger.info(f"NLTK tokenization path not active; regex tokenization used: {e}")
                self.sentences = re.split(r"[.!?।]+", self.text)
                self.sentences = [s.strip() for s in self.sentences if s.strip()]

    def _analyze_with_spacy(self) -> Dict[str, Any]:
        """Analyze using spaCy with full potential - leveraging all installed libraries"""
        t0_total = time.perf_counter()
        doc = self.nlp(self.text)
        logger.info("[linguistic] spaCy doc created in %.2fs", time.perf_counter() - t0_total)

        # === SPACY: NER (Named Entity Recognition) ===
        t0 = time.perf_counter()
        entities = []
        for ent in doc.ents:
            entities.append(
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start_char": ent.start_char,
                    "end_char": ent.end_char,
                }
            )
        logger.info("[linguistic] spaCy NER %.2fs", time.perf_counter() - t0)

        # === SPACY: Lemmas with POS ===
        t0 = time.perf_counter()
        lemmas_with_pos = []
        for token in doc:
            if token.is_alpha and not token.is_stop:
                lemmas_with_pos.append(
                    {
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "tag": token.tag_,
                        "dep": token.dep_,
                    }
                )
        logger.info("[linguistic] spaCy lemmas/POS %.2fs", time.perf_counter() - t0)

        # === SPACY: Word Vectors for Similarity ===
        t0 = time.perf_counter()
        word_vectors = {}
        if doc.has_vector:
            word_vectors = {
                "has_vectors": True,
                "vector_dim": doc.vector.shape[0]
                if hasattr(doc.vector, "shape")
                else 0,
                "vector_norm": float(doc.vector_norm)
                if hasattr(doc, "vector_norm")
                else 0,
            }
        logger.info("[linguistic] spaCy vectors %.2fs", time.perf_counter() - t0)

        # === SPACY: Noun Chunks with details ===
        # NOTE:
        # spaCy multilingual "xx" models do not implement language-specific
        # noun_chunks iterator and raise NotImplementedError [E894].
        t0 = time.perf_counter()
        noun_chunks = []
        try:
            for chunk in doc.noun_chunks:
                noun_chunks.append(
                    {
                        "text": chunk.text,
                        "root": chunk.root.text,
                        "root_dep": chunk.root.dep_,
                    }
                )
        except (NotImplementedError, ValueError) as e:
            logger.debug(
                "spaCy noun_chunks not provided for language '%s' (%s); using heuristic noun-phrase extraction.",
                self.language,
                e,
            )
            noun_chunks = self._fallback_noun_chunks(doc)
        logger.info("[linguistic] spaCy noun_chunks %.2fs", time.perf_counter() - t0)

        # === SPACY: Dependency Tree Analysis ===
        t0 = time.perf_counter()
        doc_len = len(doc)
        logger.info("[linguistic] dep_tree start (tokens=%d)", doc_len)
        dep_tree = []
        for i, token in enumerate(doc):
            if i and i % 50 == 0:
                logger.info(
                    "[linguistic] dep_tree progress %d/%d (%.2fs)",
                    i,
                    doc_len,
                    time.perf_counter() - t0,
                )
            t_tok = time.perf_counter()
            if token.is_space or token.is_punct:
                lefts = []
                rights = []
            else:
                lefts = [t.text for t in token.lefts]
                rights = [t.text for t in token.rights]
            tok_dt = time.perf_counter() - t_tok
            if tok_dt > 0.05:
                logger.info(
                    "[linguistic] dep_tree token %d slow %.2fs (lefts=%d rights=%d)",
                    i + 1,
                    tok_dt,
                    len(lefts),
                    len(rights),
                )
            dep_tree.append(
                {
                    "text": token.text,
                    "dep": token.dep_,
                    "head": token.head.text,
                    "lefts": lefts,
                    "rights": rights,
                }
            )
        logger.info("[linguistic] spaCy dependency tree %.2fs", time.perf_counter() - t0)

        # === TextDescriptives: Comprehensive Text Metrics ===
        t0 = time.perf_counter()
        try:
            from textdescriptives import descriptives

            td = descriptives(self.text)
            text_metrics = {
                "descriptive_stats": {
                    "word_count": int(td.word_count),
                    "sentence_count": int(td.sentence_count),
                    "syllable_count": int(td.syllable_count),
                    "avg_word_length": float(td.avg_word_length),
                    "avg_sentence_length": float(td.avg_sentence_length),
                },
                "readability": {
                    "flesch_reading_ease": float(td.flesch_reading_ease),
                    "flesch_kincaid_grade": float(td.flesch_kincaid_grade),
                    "gunning_fog": float(td.gunning_fog),
                    "smog_index": float(td.smog_index),
                },
            }
        except ImportError:
            text_metrics = {"error": "textdescriptives not available"}
        except Exception as e:
            text_metrics = {"error": str(e)}
        logger.info("[linguistic] textdescriptives %.2fs", time.perf_counter() - t0)

        # === VADER Sentiment Analysis ===
        t0 = time.perf_counter()
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

            vader = SentimentIntensityAnalyzer()
            sentiment = vader.polarity_scores(self.text)
            sentiment_analysis = {
                "vader": {
                    "compound": sentiment["compound"],
                    "positive": sentiment["pos"],
                    "negative": sentiment["neg"],
                    "neutral": sentiment["neu"],
                    "sentiment_label": "positive"
                    if sentiment["compound"] >= 0.05
                    else "negative"
                    if sentiment["compound"] <= -0.05
                    else "neutral",
                }
            }
        except ImportError:
            sentiment_analysis = {"error": "vaderSentiment not available"}
        except Exception as e:
            sentiment_analysis = {"error": str(e)}
        logger.info("[linguistic] vader sentiment %.2fs", time.perf_counter() - t0)

        logger.info("[linguistic] spaCy analysis total %.2fs", time.perf_counter() - t0_total)

        t0 = time.perf_counter()
        phonetics = self._analyze_phonetics_basic()
        logger.info("[linguistic] phonetics %.2fs", time.perf_counter() - t0)

        t0 = time.perf_counter()
        morphology = self._analyze_morphology_spacy(doc)
        logger.info("[linguistic] morphology %.2fs", time.perf_counter() - t0)

        t0 = time.perf_counter()
        syntax = self._analyze_syntax_spacy(doc)
        logger.info("[linguistic] syntax %.2fs", time.perf_counter() - t0)

        t0 = time.perf_counter()
        semantics = self._analyze_semantics_spacy(doc)
        logger.info("[linguistic] semantics %.2fs", time.perf_counter() - t0)

        t0 = time.perf_counter()
        lexical_relations = self._analyze_lexical_relations()
        logger.info("[linguistic] lexical_relations %.2fs", time.perf_counter() - t0)

        t0 = time.perf_counter()
        pos_distribution = self._analyze_pos_spacy(doc)
        logger.info("[linguistic] pos_distribution %.2fs", time.perf_counter() - t0)

        return {
            "phonetics": phonetics,
            "morphology": morphology,
            "syntax": syntax,
            "semantics": semantics,
            "lexical_relations": lexical_relations,
            "pos_distribution": pos_distribution,
            # New spaCy features
            "named_entities": entities,
            "lemmas_with_pos": self._limit(lemmas_with_pos, "linguistic_lemmas_with_pos"),
            "word_vectors": word_vectors,
            "noun_chunks": self._limit(noun_chunks, "linguistic_noun_chunks"),
            "dependency_tree": self._limit(dep_tree, "linguistic_dependency_tree"),
            # Library integrations
            "text_metrics": text_metrics,
            "sentiment": sentiment_analysis,
        }

    def _fallback_noun_chunks(self, doc) -> List[Dict[str, str]]:
        """
        Fallback noun-phrase extraction for models without noun_chunks support
        (e.g., spaCy multilingual xx_* pipelines).
        Groups contiguous NOUN/PROPN/ADJ tokens as lightweight NP candidates.
        """
        chunks: List[Dict[str, str]] = []
        current_tokens = []

        allowed_pos = {"NOUN", "PROPN", "ADJ"}
        t0 = time.perf_counter()
        for token in doc:
            if token.is_space or token.is_punct:
                if current_tokens:
                    root = current_tokens[-1]
                    chunks.append(
                        {
                            "text": " ".join(t.text for t in current_tokens),
                            "root": root.text,
                            "root_dep": root.dep_ or "dep",
                        }
                    )
                    current_tokens = []
                continue

            if token.pos_ in allowed_pos:
                current_tokens.append(token)
            else:
                if current_tokens:
                    root = current_tokens[-1]
                    chunks.append(
                        {
                            "text": " ".join(t.text for t in current_tokens),
                            "root": root.text,
                            "root_dep": root.dep_ or "dep",
                        }
                    )
                    current_tokens = []

        if current_tokens:
            root = current_tokens[-1]
            chunks.append(
                {
                    "text": " ".join(t.text for t in current_tokens),
                    "root": root.text,
                    "root_dep": root.dep_ or "dep",
                }
            )

        logger.info("[linguistic] heuristic noun_chunks built in %.2fs", time.perf_counter() - t0)
        return chunks

    def _analyze_with_stanza(self) -> Dict[str, Any]:
        """Analyze using Stanza"""
        doc = self.stanza_nlp(self.text)
        return {
            "phonetics": self._analyze_phonetics_basic(),
            "morphology": self._analyze_morphology_stanza(doc),
            "syntax": self._analyze_syntax_stanza(doc),
            "semantics": self._analyze_semantics_basic(),
            "lexical_relations": self._analyze_lexical_relations(),
            "pos_distribution": self._analyze_pos_stanza(doc),
        }

    def _analyze_rule_based(self) -> Dict[str, Any]:
        """Fallback rule-based analysis utilizing NLTK"""
        return {
            "phonetics": self._analyze_phonetics_basic(),
            "morphology": self._analyze_morphology_basic(),
            "syntax": self._analyze_syntax_basic(),
            "semantics": self._analyze_semantics_basic(),
            "lexical_relations": self._analyze_lexical_relations(),
            "pos_distribution": self._analyze_pos_nltk(),
        }

    def _analyze_pos_nltk(self) -> Dict[str, Any]:
        """POS tagging using NLTK"""
        try:
            tokens = nltk.word_tokenize(self.text)
            pos_tags = nltk.pos_tag(tokens)
            tag_counts = Counter(tag for word, tag in pos_tags)
            return {
                "nouns": sum(1 for tag, count in tag_counts.items() if tag.startswith('NN')),
                "verbs": sum(1 for tag, count in tag_counts.items() if tag.startswith('VB')),
                "adjectives": sum(1 for tag, count in tag_counts.items() if tag.startswith('JJ')),
                "adverbs": sum(1 for tag, count in tag_counts.items() if tag.startswith('RB')),
                "pronouns": sum(1 for tag, count in tag_counts.items() if tag.startswith('PR')),
                "total_tagged": len(pos_tags),
                "nltk_tag_distribution": dict(tag_counts)
            }
        except Exception as e:
            logger.info(f"NLTK POS tagging path not active; basic POS metrics used: {e}")
            return self._analyze_pos_basic()

    # ==================== PHONETICS ====================
    def _analyze_phonetics_basic(self) -> Dict[str, Any]:
        """Basic phonetic analysis"""
        text_lower = self.text.lower()
        consonants = set("bcdfghjklmnpqrstvwxyz")
        vowels = set("aeiou")

        consonant_count = sum(1 for c in text_lower if c in consonants)
        vowel_count = sum(1 for c in text_lower if c in vowels)

        return {
            "consonant_count": consonant_count,
            "vowel_count": vowel_count,
            "consonant_vowel_ratio": round(consonant_count / vowel_count, 2)
            if vowel_count > 0
            else 0,
            "phonesthemes": self._detect_phonesthemes(text_lower),
            "alliteration": self._detect_alliteration_basic(),
            "assonance": self._detect_assonance(),
            "consonance": self._detect_consonance(),
            "onomatopoeia": self._detect_onomatopoeia(),
            "plosive_density": self._calculate_plosive_density(text_lower),
            "fricative_density": self._calculate_fricative_density(text_lower),
        }

    def _detect_phonesthemes(self, text: str) -> Dict[str, List[str]]:
        """Detect phonestheme clusters"""
        words = re.findall(r"[A-Za-z']+", text.lower())
        clusters = Counter()
        examples: Dict[str, List[str]] = {}
        for w in words:
            if len(w) < 2:
                continue
            prefix_len = self._limits.get("linguistic_cluster_prefix_len") if self._limits else None
            if prefix_len is None:
                continue
            cluster = w[: int(prefix_len)] + "-"
            clusters[cluster] += 1
            examples.setdefault(cluster, []).append(w)
        found = {}
        for cluster, count in clusters.items():
            if count >= 2:
                example_limit = self._limits.get("linguistic_cluster_examples") if self._limits else None
                examples_list = list(dict.fromkeys(examples.get(cluster, [])))
                found[cluster] = examples_list[: int(example_limit)] if example_limit is not None else examples_list
        return found

    def _detect_alliteration_basic(self) -> List[Dict[str, Any]]:
        """Detect alliteration"""
        alliterations = []
        for line_idx, line in enumerate(self.lines):
            words = line.split()
            if len(words) < 2:
                continue
            initials = [w[0].lower() for w in words if w and w[0].isalpha()]
            for i in range(len(initials) - 1):
                if (
                    initials[i] == initials[i + 1]
                    and initials[i] in "bcdfghjklmnpqrstvwxyz"
                ):
                    alliterations.append(
                        {
                            "line": line,
                            "line_number": line_idx + 1,
                            "letter": initials[i],
                            "words": [words[i], words[i + 1]],
                        }
                    )
        return self._limit(alliterations, "linguistic_alliterations")

    def _detect_assonance(self) -> List[Dict[str, Any]]:
        """Detect assonance"""
        assonances = []
        vowels = "aeiouáéíóúàèìòùäëïöü"
        for line_idx, line in enumerate(self.lines):
            words = line.split()
            if len(words) < 2:
                continue
            first_vowels = []
            for word in words:
                for char in word.lower():
                    if char in vowels:
                        first_vowels.append(char)
                        break
            for i in range(len(first_vowels) - 1):
                if first_vowels[i] and first_vowels[i] == first_vowels[i + 1]:
                    assonances.append(
                        {
                            "line": line,
                            "line_number": line_idx + 1,
                            "vowel": first_vowels[i],
                            "words": [words[i], words[i + 1]],
                        }
                    )
        return self._limit(assonances, "linguistic_assonances")

    def _detect_consonance(self) -> List[Dict[str, Any]]:
        """Detect consonance"""
        consonances = []
        consonants = "bcdfghjklmnpqrstvwxyz"
        for line_idx, line in enumerate(self.lines):
            words = line.split()
            if len(words) < 2:
                continue
            last_consonants = []
            for word in words:
                for char in reversed(word.lower()):
                    if char in consonants:
                        last_consonants.append(char)
                        break
            for i in range(len(last_consonants) - 1):
                if last_consonants[i] and last_consonants[i] == last_consonants[i + 1]:
                    consonances.append(
                        {
                            "line": line,
                            "line_number": line_idx + 1,
                            "consonant": last_consonants[i],
                            "words": [words[i], words[i + 1]],
                        }
                    )
        return self._limit(consonances, "linguistic_consonances")

    def _detect_onomatopoeia(self) -> List[str]:
        """Detect onomatopoeic words"""
        if self.language != "en":
            return []
        words = list(dict.fromkeys(re.findall(r"[A-Za-z']+", self.text.lower())))
        if not words:
            return []
        zs = self._ensure_zero_shot()
        if not zs:
            return []
        found = []
        word_limit = self._limits.get("linguistic_phonestheme_words") if self._limits else None
        for word in (words[: int(word_limit)] if word_limit is not None else words):
            try:
                out = zs(word, ["onomatopoeia"])
                if out["scores"][0] >= 0.6:
                    found.append(word)
            except Exception:
                continue
        return found

    def _calculate_plosive_density(self, text: str) -> float:
        """Calculate density of plosive consonants"""
        plosives = set("pbt dkg")
        plosive_count = sum(1 for c in text if c in plosives)
        total_letters = sum(1 for c in text if c.isalpha())
        return round(plosive_count / total_letters, 4) if total_letters > 0 else 0

    def _calculate_fricative_density(self, text: str) -> float:
        """Calculate density of fricative consonants"""
        fricatives = set("fvsz")
        fricative_count = sum(1 for c in text if c in fricatives)
        total_letters = sum(1 for c in text if c.isalpha())
        return round(fricative_count / total_letters, 4) if total_letters > 0 else 0

    def _analyze_morphology_spacy(self, doc) -> Dict[str, Any]:
        """Detailed morphological analysis using Token.morph"""
        # Extract grammatical features
        morph_features = []
        for token in doc:
            if token.is_alpha and token.morph:
                morph_features.append(str(token.morph))

        feature_counts = Counter(morph_features)

        prefix_stats = self._detect_prefixes()
        suffix_stats = self._detect_suffixes()

        return {
            "avg_word_length": round(
                sum(len(t.text) for t in doc if t.is_alpha)
                / max(1, len([t for t in doc if t.is_alpha])),
                2,
            ),
            "grammatical_features": dict(feature_counts.most_common(10)),
            "prefix_count": sum(prefix_stats.values()),
            "suffix_count": sum(suffix_stats.values()),
        }

    def _analyze_morphology_stanza(self, doc) -> Dict[str, Any]:
        """Morphological analysis using Stanza"""
        words = [word.text for sent in doc.sentences for word in sent.words]
        length_dist = Counter(len(w) for w in words)
        return {
            "word_length_distribution": dict(length_dist),
            "avg_word_length": round(
                sum(len(w) for w in words) / max(1, len(words)), 2
            ),
            "prefixes": self._detect_prefixes(),
            "suffixes": self._detect_suffixes(),
            "compound_words": self._detect_compounds(),
            "prefix_count": sum(
                1
                for w in words
                if any(w.startswith(p) for p in ["un", "re", "pre", "dis"])
            ),
            "suffix_count": sum(
                1
                for w in words
                if any(w.endswith(s) for s in ["ing", "tion", "ment", "ness"])
            ),
        }

    def _analyze_morphology_basic(self) -> Dict[str, Any]:
        """Basic morphological analysis"""
        length_dist = Counter(len(w) for w in self.words)
        prefix_stats = self._detect_prefixes()
        suffix_stats = self._detect_suffixes()
        return {
            "word_length_distribution": dict(length_dist),
            "avg_word_length": round(
                sum(len(w) for w in self.words) / max(1, len(self.words)), 2
            ),
            "prefixes": prefix_stats,
            "suffixes": suffix_stats,
            "compound_words": self._detect_compounds(),
            "prefix_count": sum(prefix_stats.values()),
            "suffix_count": sum(suffix_stats.values()),
        }

    def _detect_prefixes(self) -> Dict[str, int]:
        """Detect common prefixes dynamically"""
        counts = Counter()
        for w in self.words:
            w = w.lower()
            for n in (2, 3, 4):
                if len(w) > n:
                    counts[w[:n]] += 1
        return {p: c for p, c in counts.items() if c >= 2}

    def _detect_suffixes(self) -> Dict[str, int]:
        """Detect common suffixes dynamically"""
        counts = Counter()
        for w in self.words:
            w = w.lower()
            for n in (2, 3, 4):
                if len(w) > n:
                    counts[w[-n:]] += 1
        return {s: c for s, c in counts.items() if c >= 2}

    def _detect_compounds(self) -> List[str]:
        """Detect compound words"""
        return [
            w
            for w in self.words
            if "-" in w
            or "_" in w
            or (
                len(w) > 10
                and any(w.startswith(p) for p in ["grand", "great", "over", "under"])
            )
        ]

    def _analyze_syntax_spacy(self, doc) -> Dict[str, Any]:
        """Deep syntactic analysis using spaCy dependency parser"""
        t0_total = time.perf_counter()
        logger.info("[linguistic] syntax_spacy start")

        t0 = time.perf_counter()
        sents_list = list(doc.sents)
        logger.info("[linguistic] syntax_spacy sents_list %d (%.2fs)", len(sents_list), time.perf_counter() - t0)

        t0 = time.perf_counter()
        sentence_lengths = [len(sent) for sent in sents_list]
        logger.info("[linguistic] syntax_spacy sentence_lengths (%.2fs)", time.perf_counter() - t0)

        # Dependency Map for first few sentences (to avoid massive JSON)
        dep_map = []
        t0 = time.perf_counter()
        sent_limit = self._limits.get("linguistic_syntax_sent_limit") if self._limits else None
        for sent in (sents_list[: int(sent_limit)] if sent_limit is not None else sents_list):
            sent_deps = []
            for token in sent:
                sent_deps.append(
                    {
                        "text": token.text,
                        "dep": token.dep_,
                        "head": token.head.text,
                        "pos": token.pos_,
                    }
                )
            dep_map.append(sent_deps)
        logger.info("[linguistic] syntax_spacy dep_map (%.2fs)", time.perf_counter() - t0)

        t0 = time.perf_counter()
        avg_deps = 0.0
        try:
            # spaCy xx models may not have reliable dependency parsing for some languages.
            # Avoid iterating children when parser isn't available to prevent hangs.
            if getattr(doc, "is_parsed", False) and self.language not in {"hi", "ur", "bn", "mr", "ta", "te", "ml", "kn"}:
                avg_deps = sum(len(list(token.children)) for token in doc) / max(1, len(doc))
            else:
                avg_deps = 0.0
        except Exception as e:
            logger.info("[linguistic] syntax_spacy avg_deps not computed: %s", e)
            avg_deps = 0.0
        logger.info("[linguistic] syntax_spacy avg_deps (%.2fs)", time.perf_counter() - t0)

        result = {
            "total_sentences": len(sents_list),
            "avg_sentence_length": round(
                sum(sentence_lengths) / max(1, len(sentence_lengths)), 2
            ),
            "sentence_length_distribution": dict(Counter(sentence_lengths)),
            "dependency_map": dep_map,
            "clauses": {
                "has_complex_sentences": any(t.dep_ in ["mark", "cc"] for t in doc),
            },
            "sentence_types": self._identify_sentence_types(),
            "syntactic_complexity": round(avg_deps, 2),
        }
        logger.info("[linguistic] syntax_spacy total %.2fs", time.perf_counter() - t0_total)
        return result

    def _analyze_syntax_stanza(self, doc) -> Dict[str, Any]:
        """Syntactic analysis using Stanza"""
        sentence_lengths = [len(sent.words) for sent in doc.sentences]
        sub_count = sum(
            1 for sent in doc.sentences for word in sent.words if word.deprel in ["mark", "advmod"]
        )
        coord_count = sum(
            1 for sent in doc.sentences for word in sent.words if word.deprel == "cc"
        )

        return {
            "total_sentences": len(doc.sentences),
            "avg_sentence_length": round(
                sum(sentence_lengths) / max(1, len(sentence_lengths)), 2
            ),
            "sentence_length_distribution": dict(Counter(sentence_lengths)),
            "clauses": {
                "subordinate_clauses_count": sub_count,
                "coordinating_clauses_count": coord_count,
                "has_complex_sentences": sub_count + coord_count > 0,
            },
            "sentence_types": self._identify_sentence_types(),
            "syntactic_complexity": 0,
        }

    def _analyze_syntax_basic(self) -> Dict[str, Any]:
        """Basic syntactic analysis"""
        sentence_lengths = [len(s.split()) for s in self.sentences]
        sub_count = 0
        coord_count = 0
        if self.language == "en":
            try:
                tokens = nltk.word_tokenize(self.text)
                tagged = nltk.pos_tag(tokens)
                sub_count = sum(1 for _, tag in tagged if tag == "IN")
                coord_count = sum(1 for _, tag in tagged if tag == "CC")
            except Exception:
                sub_count = 0
                coord_count = 0

        return {
            "total_sentences": len(self.sentences),
            "avg_sentence_length": round(
                sum(sentence_lengths) / max(1, len(sentence_lengths)), 2
            ),
            "sentence_length_distribution": dict(Counter(sentence_lengths)),
            "clauses": {
                "subordinate_clauses_count": sub_count,
                "coordinating_clauses_count": coord_count,
                "has_complex_sentences": sub_count + coord_count > 0,
            },
            "sentence_types": self._identify_sentence_types(),
            "syntactic_complexity": 0,
        }

    def _identify_sentence_types(self) -> Dict[str, int]:
        """Identify sentence types"""
        types = {
            "declarative": 0,
            "interrogative": 0,
            "imperative": 0,
            "exclamatory": 0,
        }
        for s in self.sentences:
            s = s.strip()
            if s.endswith("?"):
                types["interrogative"] += 1
            elif s.endswith("!"):
                types["exclamatory"] += 1
            elif s.lower().startswith(
                ("let", "please", "do", "don't", "go", "come", "be", "have")
            ):
                types["imperative"] += 1
            else:
                types["declarative"] += 1
        return types

    def _analyze_semantics_spacy(self, doc) -> Dict[str, Any]:
        """Semantic analysis using spaCy including robust NER"""
        word_freq = Counter(token.text.lower() for token in doc if token.is_alpha)
        concrete_words = self._get_concrete_words()
        concrete_count = sum(1 for token in doc if token.text.lower() in concrete_words)

        # Robust Entity Extraction
        entities = []
        for ent in doc.ents:
            entities.append(
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "description": spacy.explain(ent.label_),
                }
            )

        return {
            "unique_words": len(word_freq),
            "total_words": len([t for t in doc if t.is_alpha]),
            "semantic_density": round(len(word_freq) / max(1, len(doc)), 2),
            "top_20_words": [w for w, c in word_freq.most_common(20)],
            "concrete_word_count": concrete_count,
            "abstract_word_count": len([t for t in doc if t.is_alpha]) - concrete_count,
            "entities": self._limit(entities, "linguistic_entities"),
        }

    def _analyze_semantics_basic(self) -> Dict[str, Any]:
        """Basic semantic analysis"""
        word_freq = Counter(self.words)
        semantic_density = len(word_freq) / max(1, len(self.words))
        concrete_words = self._get_concrete_words()
        concrete_count = sum(1 for w in self.words if w in concrete_words)

        return {
            "unique_words": len(word_freq),
            "total_words": len(self.words),
            "semantic_density": round(semantic_density, 2),
            "top_20_words": [w for w, c in word_freq.most_common(20)],
            "concrete_word_count": concrete_count,
            "abstract_word_count": len(self.words) - concrete_count,
            "named_entities": [],
        }

    def _get_concrete_words(self) -> Set[str]:
        """Identify concrete words"""
        if not self._wn:
            return set()
        concrete_lexnames = {
            "noun.artifact",
            "noun.object",
            "noun.plant",
            "noun.animal",
            "noun.body",
            "noun.food",
            "noun.substance",
            "noun.location",
        }
        concrete = set()
        for w in set(self.words):
            syns = self._wn.synsets(w, pos=self._wn.NOUN)
            if any(s.lexname() in concrete_lexnames for s in syns):
                concrete.add(w)
        return concrete

    def _analyze_lexical_relations(self) -> Dict[str, Any]:
        """Analyze word relationships"""
        return {
            "homophones": self._detect_homophones(),
            "synonyms": self._detect_synonyms(),
            "antonyms": self._detect_antonyms(),
            "palindromes": self._detect_palindromes(),
            "contronyms": self._detect_contronyms(),
            "minimal_pairs": self._detect_minimal_pairs(),
        }

    def _detect_homophones(self) -> List[List[str]]:
        """Detect homophones"""
        if self.language != "en":
            return []
        if _pronouncing is None:
            logger.info("Pronouncing not active; homophone detection is disabled for this run.")
            return []

        word_set = set(w.lower() for w in self.words if w)
        phones_map: Dict[str, List[str]] = {}
        for w in word_set:
            phones = _pronouncing.phones_for_word(w)
            if not phones:
                continue
            for p in phones:
                phones_map.setdefault(p, []).append(w)
        return [group for group in phones_map.values() if len(group) > 1]

    def _detect_synonyms(self) -> Dict[str, List[str]]:
        """Detect synonyms"""
        word_set = set(w.lower() for w in self.words)
        results: Dict[str, List[str]] = {}

        if self._wn and self.language == "en":
            for word in word_set:
                syns = set()
                for syn in self._wn.synsets(word):
                    for lemma in syn.lemma_names():
                        lemma_clean = lemma.replace("_", " ").lower()
                        if lemma_clean != word:
                            syns.add(lemma_clean)
                matches = [s for s in syns if s in word_set]
                if matches:
                    results[word] = matches
            return results

        if self._iwn:
            for word in word_set:
                syns = set()
                try:
                    for syn in self._iwn.synsets(word):
                        for lemma in syn.lemma_names():
                            lemma_clean = str(lemma).strip()
                            if lemma_clean and lemma_clean != word:
                                syns.add(lemma_clean)
                except Exception:
                    continue
                matches = [s for s in syns if s in word_set]
                if matches:
                    results[word] = matches
            return results

        return {}

    def _detect_antonyms(self) -> Dict[str, List[str]]:
        """Detect antonyms"""
        word_set = set(w.lower() for w in self.words)
        results: Dict[str, List[str]] = {}

        if self._wn and self.language == "en":
            for word in word_set:
                ants = set()
                for syn in self._wn.synsets(word):
                    for lemma in syn.lemmas():
                        for ant in lemma.antonyms():
                            ant_name = ant.name().replace("_", " ").lower()
                            if ant_name:
                                ants.add(ant_name)
                matches = [a for a in ants if a in word_set]
                if matches:
                    results[word] = matches
            return results

        # IndoWordNet does not expose direct antonym relations in pyiwn.
        return {}

    def _detect_palindromes(self) -> List[str]:
        """Detect palindromes"""
        return list(
            set(w for w in self.words if len(w) > 2 and w.lower() == w.lower()[::-1])
        )

    def _detect_contronyms(self) -> List[List[str]]:
        """Detect contronyms using WordNet antonym presence"""
        contronyms = []
        if not self._wn:
            return contronyms
        for w in set(self.words):
            syns = self._wn.synsets(w)
            if len(syns) < 2:
                continue
            has_ant = any(lemma.antonyms() for syn in syns for lemma in syn.lemmas())
            if has_ant:
                contronyms.append([w])
        return contronyms

    def _detect_minimal_pairs(self) -> List[List[str]]:
        """Detect minimal pairs"""
        pairs = []
        word_set = set(self.words)
        for word in word_set:
            if len(word) >= 3:
                for i in range(len(word)):
                    for char in "abcdefghijklmnopqrstuvwxyz":
                        if char != word[i]:
                            new_word = word[:i] + char + word[i + 1 :]
                            if new_word in word_set:
                                pair = sorted([word, new_word])
                                if pair not in pairs:
                                    pairs.append(pair)
        return self._limit(pairs, "linguistic_pairs")

    # ==================== POS DISTRIBUTION ====================
    def _analyze_pos_spacy(self, doc) -> Dict[str, Any]:
        """POS distribution using spaCy"""
        pos_counts = Counter(token.pos_ for token in doc if token.is_alpha)
        pos_map = {
            "NOUN": "noun",
            "VERB": "verb",
            "ADJ": "adjective",
            "ADV": "adverb",
            "PRON": "pronoun",
            "ADP": "preposition",
            "CCONJ": "conjunction",
            "DET": "determiner",
        }
        result = {
            pos_map.get(pos, pos.lower()): count for pos, count in pos_counts.items()
        }
        result["detected_nouns"] = self._limit([t.text for t in doc if t.pos_ == "NOUN"], "linguistic_detected_pos")
        result["detected_verbs"] = self._limit([t.text for t in doc if t.pos_ == "VERB"], "linguistic_detected_pos")
        result["detected_adjectives"] = self._limit([t.text for t in doc if t.pos_ == "ADJ"], "linguistic_detected_pos")
        return result

    def _analyze_pos_stanza(self, doc) -> Dict[str, Any]:
        """POS distribution using Stanza"""
        pos_counts = Counter()
        nouns, verbs, adjectives = [], [], []
        for sentence in doc.sentences:
            for word in sentence.words:
                pos_counts[word.upos] += 1
                if word.upos == "NOUN" and len(nouns) < 10:
                    nouns.append(word.text)
                elif word.upos == "VERB" and len(verbs) < 10:
                    verbs.append(word.text)
                elif word.upos == "ADJ" and len(adjectives) < 10:
                    adjectives.append(word.text)

        pos_map = {
            "NOUN": "noun",
            "VERB": "verb",
            "ADJ": "adjective",
            "ADV": "adverb",
            "PRON": "pronoun",
            "ADP": "preposition",
            "CCONJ": "conjunction",
            "DET": "determiner",
        }
        result = {
            pos_map.get(pos, pos.lower()): count for pos, count in pos_counts.items()
        }
        result["detected_nouns"] = nouns
        result["detected_verbs"] = verbs
        result["detected_adjectives"] = adjectives
        return result

    def _analyze_pos_basic(self) -> Dict[str, Any]:
        """Basic POS analysis"""
        nouns = self._detect_nouns()
        verbs = self._detect_verbs()
        adjectives = self._detect_adjectives()
        adverbs = self._detect_adverbs()
        pronouns = self._detect_pronouns()
        prepositions = self._detect_prepositions()
        conjunctions = self._detect_conjunctions()
        determiners = self._detect_determiners()

        return {
            "noun": len(nouns),
            "verb": len(verbs),
            "adjective": len(adjectives),
            "adverb": len(adverbs),
            "pronoun": len(pronouns),
            "preposition": len(prepositions),
            "conjunction": len(conjunctions),
            "determiner": len(determiners),
            "detected_nouns": self._limit(list(nouns), "linguistic_detected_pos"),
            "detected_verbs": self._limit(list(verbs), "linguistic_detected_pos"),
            "detected_adjectives": self._limit(list(adjectives), "linguistic_detected_pos"),
        }

    def _extract_pos(self, pos_tags: Set[str]) -> Set[str]:
        """Extract tokens for requested POS tags without static lexicons."""
        if self.nlp:
            doc = self.nlp(self.text)
            return {t.text.lower() for t in doc if t.pos_ in pos_tags and t.is_alpha}

        if self.language == "en":
            try:
                tokens = nltk.word_tokenize(self.text)
                tagged = nltk.pos_tag(tokens)
                results = set()
                for word, tag in tagged:
                    if tag.startswith("NN") and "NOUN" in pos_tags:
                        results.add(word.lower())
                    if tag.startswith("VB") and "VERB" in pos_tags:
                        results.add(word.lower())
                    if tag.startswith("JJ") and "ADJ" in pos_tags:
                        results.add(word.lower())
                    if tag.startswith("RB") and "ADV" in pos_tags:
                        results.add(word.lower())
                    if tag in {"PRP", "PRP$"} and "PRON" in pos_tags:
                        results.add(word.lower())
                return results
            except Exception:
                return set()

        return set()

    def _detect_nouns(self) -> Set[str]:
        """Detect common nouns"""
        return self._extract_pos({"NOUN", "PROPN"})

    def _detect_verbs(self) -> Set[str]:
        """Detect common verbs"""
        return self._extract_pos({"VERB", "AUX"})

    def _detect_adjectives(self) -> Set[str]:
        """Detect adjectives"""
        return self._extract_pos({"ADJ"})

    def _detect_adverbs(self) -> Set[str]:
        """Detect adverbs"""
        return self._extract_pos({"ADV"})

    def _detect_pronouns(self) -> Set[str]:
        """Detect pronouns"""
        return self._extract_pos({"PRON"})

    def _detect_prepositions(self) -> Set[str]:
        """Detect prepositions"""
        return self._extract_pos({"ADP"})

    def _detect_conjunctions(self) -> Set[str]:
        """Detect conjunctions"""
        return self._extract_pos({"CCONJ", "SCONJ"})

    def _detect_determiners(self) -> Set[str]:
        """Detect determiners"""
        return self._extract_pos({"DET"})
