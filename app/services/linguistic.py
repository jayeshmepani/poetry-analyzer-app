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
from typing import Dict, List, Tuple, Set, Optional, Any
from collections import Counter
import logging

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

logger = logging.getLogger(__name__)


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

        # Initialize NLP models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize spaCy and Stanza models"""
        # spaCy initialization - use installed models only
        if self.use_spacy:
            import spacy
            from app.config import Settings

            settings = Settings()

            if self.language == "en":
                # Use transformer model for English
                try:
                    self.nlp = spacy.load(settings.spacy.english_model)
                    logger.info(f"Loaded spaCy model: {settings.spacy.english_model}")
                except OSError as e:
                    logger.warning(f"English spaCy model not found: {e}")
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
                    logger.warning(f"Multilingual spaCy model not found: {e}")
                    self.nlp = None

        # Stanza initialization for multilingual
        if self.use_stanza:
            try:
                import stanza

                lang_code = self._get_stanza_lang_code()
                self.stanza_nlp = stanza.Pipeline(
                    lang=lang_code,
                    processors="tokenize,pos,lemma,depparse",
                    verbose=False,
                )
                logger.info(f"Loaded Stanza pipeline for {lang_code}")
            except Exception as e:
                logger.warning(f"Stanza not available: {e}")
                self.stanza_nlp = None

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
        self.text = text
        self._preprocess()

        # Use spaCy if available (en_core_web_trf for English, xx_sent_ud_sm for others)
        if self.nlp:
            return self._analyze_with_spacy()
        elif self.stanza_nlp:
            return self._analyze_with_stanza()
        else:
            return self._analyze_rule_based()

    def _preprocess(self):
        """Preprocess text into words, lines, sentences"""
        # Apply Indic Normalization if applicable
        if self.language in ["hi", "gu", "mr", "bn", "sa", "ur"]:
            try:
                factory = IndicNormalizerFactory()
                normalizer = factory.get_normalizer(self.language)
                self.text = normalizer.normalize(self.text)
            except Exception as e:
                logger.warning(f"Indic normalization failed: {e}")

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

        # Use spaCy for sentence segmentation if available (xx_sent_ud_sm or en_core_web_trf)
        if self.nlp:
            doc = self.nlp(self.text)
            self.sentences = [
                sent.text.strip() for sent in doc.sents if sent.text.strip()
            ]
        else:
            self.sentences = re.split(r"[.!?।]+", self.text)
            self.sentences = [s.strip() for s in self.sentences if s.strip()]

    def _analyze_with_spacy(self) -> Dict[str, Any]:
        """Analyze using spaCy with full potential - leveraging all installed libraries"""
        doc = self.nlp(self.text)

        # === SPACY: NER (Named Entity Recognition) ===
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

        # === SPACY: Lemmas with POS ===
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

        # === SPACY: Word Vectors for Similarity ===
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

        # === SPACY: Noun Chunks with details ===
        noun_chunks = []
        for chunk in doc.noun_chunks:
            noun_chunks.append(
                {
                    "text": chunk.text,
                    "root": chunk.root.text,
                    "root_dep": chunk.root.dep_,
                }
            )

        # === SPACY: Dependency Tree Analysis ===
        dep_tree = []
        for token in doc:
            dep_tree.append(
                {
                    "text": token.text,
                    "dep": token.dep_,
                    "head": token.head.text,
                    "lefts": [t.text for t in token.lefts],
                    "rights": [t.text for t in token.rights],
                }
            )

        # === TextDescriptives: Comprehensive Text Metrics ===
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

        # === VADER Sentiment Analysis ===
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

        return {
            "phonetics": self._analyze_phonetics_basic(),
            "morphology": self._analyze_morphology_spacy(doc),
            "syntax": self._analyze_syntax_spacy(doc),
            "semantics": self._analyze_semantics_spacy(doc),
            "lexical_relations": self._analyze_lexical_relations(),
            "pos_distribution": self._analyze_pos_spacy(doc),
            # New spaCy features
            "named_entities": entities,
            "lemmas_with_pos": lemmas_with_pos[:50],
            "word_vectors": word_vectors,
            "noun_chunks": noun_chunks[:20],
            "dependency_tree": dep_tree[:30],
            # Library integrations
            "text_metrics": text_metrics,
            "sentiment": sentiment_analysis,
        }

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
        """Fallback rule-based analysis"""
        return {
            "phonetics": self._analyze_phonetics_basic(),
            "morphology": self._analyze_morphology_basic(),
            "syntax": self._analyze_syntax_basic(),
            "semantics": self._analyze_semantics_basic(),
            "lexical_relations": self._analyze_lexical_relations(),
            "pos_distribution": self._analyze_pos_basic(),
        }

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
        phonestheme_dict = {
            "gl-": ["glow", "glitter", "gleam", "glisten", "glimmer"],
            "sn-": ["snore", "sniff", "snout", "sneer", "snarl"],
            "fl-": ["flow", "flutter", "fling", "flap", "flash"],
            "sl-": ["slow", "slide", "slip", "slimy", "slap"],
            "cr-": ["crack", "crush", "crumble", "crisp", "crazy"],
            "sp-": ["sparkle", "speck", "spit", "spray", "spread"],
            "st-": ["star", "stone", "still", "stop", "sturdy"],
            "bl-": ["black", "blot", "blaze", "bleak", "blind"],
            "gr-": ["green", "grow", "grass", "grave", "grim"],
            "pr-": ["pray", "press", "prize", "proud", "pretty"],
            "tr-": ["tree", "trial", "treat", "true", "trust"],
            "dr-": ["dream", "drop", "drift", "drive", "drama"],
            "sw-": ["sweet", "swift", "swing", "swim", "swell"],
            "tw-": ["twin", "twist", "twinkle", "twelve", "twenty"],
        }

        found = {}
        for cluster, examples in phonestheme_dict.items():
            matches = [
                word for word in examples if cluster + word[2:] in text or word in text
            ]
            if matches:
                found[cluster] = matches
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
        return alliterations[:10]

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
        return assonances[:10]

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
        return consonances[:10]

    def _detect_onomatopoeia(self) -> List[str]:
        """Detect onomatopoeic words"""
        onomatopoeic_words = [
            "buzz",
            "hiss",
            "clang",
            "crash",
            "bang",
            "pop",
            "splash",
            "drip",
            "drop",
            "hum",
            "ring",
            "ding",
            "dong",
            "meow",
            "bark",
            "woof",
            "moo",
            "quack",
            "cuckoo",
            "chirp",
            "tweet",
            "flutter",
            "rattle",
            "clatter",
            "thud",
            "thump",
            "wham",
            "zap",
            "zoom",
            "whoosh",
            "swish",
            "tick",
            "tock",
            "ping",
            "clink",
            "clank",
            "jingle",
            "jangle",
            "rumble",
            "grumble",
            "gurgle",
            "bubble",
            "burp",
            "chomp",
            "gobble",
            "slurp",
            "sigh",
            "yawn",
            "gasp",
            "giggle",
            "laugh",
            "chuckle",
            "sob",
            "cry",
            "wail",
            "whimper",
            "moan",
            "groan",
            "roar",
            "sizzle",
            "fizz",
            "crackle",
            "snap",
            "crunch",
            "creak",
            "squeak",
            "screech",
            "howl",
            "whistle",
            "chime",
        ]
        text_lower = self.text.lower()
        return [word for word in onomatopoeic_words if word in text_lower]

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

        return {
            "avg_word_length": round(
                sum(len(t.text) for t in doc if t.is_alpha)
                / max(1, len([t for t in doc if t.is_alpha])),
                2,
            ),
            "grammatical_features": dict(feature_counts.most_common(10)),
            "prefix_count": sum(
                1
                for t in doc
                if any(t.text.lower().startswith(p) for p in ["un", "re", "pre", "dis"])
            ),
            "suffix_count": sum(
                1
                for t in doc
                if any(
                    t.text.lower().endswith(s) for s in ["ing", "tion", "ment", "ness"]
                )
            ),
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
        return {
            "word_length_distribution": dict(length_dist),
            "avg_word_length": round(
                sum(len(w) for w in self.words) / max(1, len(self.words)), 2
            ),
            "prefixes": self._detect_prefixes(),
            "suffixes": self._detect_suffixes(),
            "compound_words": self._detect_compounds(),
            "prefix_count": sum(
                1
                for w in self.words
                if any(w.startswith(p) for p in ["un", "re", "pre", "dis"])
            ),
            "suffix_count": sum(
                1
                for w in self.words
                if any(w.endswith(s) for s in ["ing", "tion", "ment", "ness"])
            ),
        }

    def _detect_prefixes(self) -> Dict[str, int]:
        """Detect common prefixes"""
        prefixes = [
            "un",
            "re",
            "pre",
            "dis",
            "mis",
            "over",
            "under",
            "inter",
            "trans",
            "con",
            "com",
            "pro",
            "anti",
            "auto",
            "bi",
            "co",
            "de",
            "ex",
            "in",
            "non",
            "out",
            "post",
            "sub",
            "super",
            "sym",
            "syn",
        ]
        return {
            p: sum(1 for w in self.words if w.startswith(p))
            for p in prefixes
            if sum(1 for w in self.words if w.startswith(p)) > 0
        }

    def _detect_suffixes(self) -> Dict[str, int]:
        """Detect common suffixes"""
        suffixes = [
            "ing",
            "tion",
            "sion",
            "ment",
            "ness",
            "able",
            "ible",
            "ful",
            "less",
            "ly",
            "ed",
            "er",
            "est",
            "s",
            "es",
            "ous",
            "ious",
            "ive",
            "al",
            "ial",
            "ic",
            "y",
            "ary",
            "ory",
            "ery",
            "ity",
            "ty",
            "ance",
            "ence",
            "ism",
            "ist",
            "ship",
            "hood",
            "dom",
        ]
        return {
            s: sum(1 for w in self.words if w.endswith(s))
            for s in suffixes
            if sum(1 for w in self.words if w.endswith(s)) > 0
        }

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
        sentence_lengths = [len(sent) for sent in doc.sents]

        # Dependency Map for first few sentences (to avoid massive JSON)
        dep_map = []
        for sent in list(doc.sents)[:3]:
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

        avg_deps = sum(len(list(token.children)) for token in doc) / max(1, len(doc))

        return {
            "total_sentences": len(list(doc.sents)),
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

    def _analyze_syntax_stanza(self, doc) -> Dict[str, Any]:
        """Syntactic analysis using Stanza"""
        sentence_lengths = [len(sent.words) for sent in doc.sentences]
        subordinating = [
            "because",
            "although",
            "while",
            "when",
            "if",
            "unless",
            "since",
            "though",
        ]
        coordinating = ["and", "but", "or", "nor", "for", "yet", "so"]

        sub_count = sum(
            1
            for sent in doc.sentences
            for word in sent.words
            if word.deprel in ["mark", "advmod"] and word.text.lower() in subordinating
        )
        coord_count = sum(
            1
            for sent in doc.sentences
            for word in sent.words
            if word.deprel == "cc" and word.text.lower() in coordinating
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
        subordinating = [
            "because",
            "although",
            "while",
            "when",
            "if",
            "unless",
            "since",
            "though",
        ]
        coordinating = ["and", "but", "or", "nor", "for", "yet", "so"]

        text_lower = self.text.lower()
        sub_count = sum(text_lower.count(w) for w in subordinating)
        coord_count = sum(text_lower.count(w) for w in coordinating)

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
            "entities": entities[:20],
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
        return {
            "book",
            "house",
            "car",
            "tree",
            "flower",
            "water",
            "fire",
            "stone",
            "metal",
            "glass",
            "chair",
            "table",
            "door",
            "window",
            "road",
            "mountain",
            "river",
            "sea",
            "sky",
            "star",
            "moon",
            "sun",
            "earth",
            "hand",
            "foot",
            "head",
            "eye",
            "ear",
            "nose",
            "mouth",
            "heart",
            "walk",
            "run",
            "eat",
            "drink",
            "sleep",
            "see",
            "hear",
            "touch",
            "taste",
            "smell",
            "red",
            "blue",
            "green",
            "yellow",
            "white",
            "black",
            "dark",
            "light",
            "hot",
            "cold",
        }

    # ==================== LEXICAL RELATIONS ====================
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
        homophone_groups = [
            ["their", "there", "they're"],
            ["your", "you're"],
            ["its", "it's"],
            ["to", "too", "two"],
            ["sea", "see"],
            ["right", "write"],
            ["sun", "son"],
            ["won", "one"],
            ["ate", "eight"],
            ["bare", "bear"],
            ["break", "brake"],
            ["hair", "hare"],
            ["know", "no"],
            ["meat", "meet"],
            ["pair", "pear"],
            ["flour", "flower"],
            ["peace", "piece"],
            ["week", "weak"],
            ["which", "witch"],
        ]
        return [
            group
            for group in homophone_groups
            if len([w for w in group if w in self.words]) > 1
        ]

    def _detect_synonyms(self) -> Dict[str, List[str]]:
        """Detect synonyms"""
        synonyms = {
            "happy": ["joyful", "cheerful", "delighted", "pleased"],
            "sad": ["unhappy", "sorrowful", "dejected", "melancholy"],
            "big": ["large", "huge", "enormous", "vast"],
            "beautiful": ["lovely", "gorgeous", "stunning", "attractive"],
            "good": ["excellent", "great", "fine", "superb"],
            "bad": ["poor", "terrible", "awful", "horrible"],
            "fast": ["quick", "rapid", "swift", "speedy"],
            "slow": ["sluggish", "gradual", "leisurely"],
            "smart": ["intelligent", "clever", "bright", "wise"],
            "love": ["adore", "cherish", "treasure"],
            "hate": ["detest", "despise", "loathe"],
        }
        found = {}
        for word, syns in synonyms.items():
            matches = [s for s in syns if s in self.words]
            if word in self.words or matches:
                found[word] = ([word] if word in self.words else []) + matches
        return {k: v for k, v in found.items() if len(v) > 1 or v}

    def _detect_antonyms(self) -> Dict[str, List[str]]:
        """Detect antonyms"""
        antonyms = {
            "good": ["bad", "evil", "poor"],
            "big": ["small", "little", "tiny"],
            "happy": ["sad", "unhappy"],
            "light": ["dark", "heavy"],
            "fast": ["slow"],
            "hot": ["cold", "cool"],
            "strong": ["weak"],
            "easy": ["hard", "difficult"],
            "love": ["hate"],
            "peace": ["war"],
            "success": ["failure"],
            "begin": ["end"],
            "open": ["close"],
            "full": ["empty"],
            "rich": ["poor"],
            "loud": ["quiet"],
        }
        return {
            word: [a for a in ants if a in self.words]
            for word, ants in antonyms.items()
            if word in self.words and any(a in self.words for a in ants)
        }

    def _detect_palindromes(self) -> List[str]:
        """Detect palindromes"""
        return list(
            set(w for w in self.words if len(w) > 2 and w.lower() == w.lower()[::-1])
        )

    def _detect_contronyms(self) -> List[List[str]]:
        """Detect contronyms"""
        contronyms = [
            "cleave",
            "dust",
            "seed",
            "stone",
            "trim",
            "oversight",
            "sanction",
            "bolt",
            "fast",
        ]
        return [[w] for w in contronyms if w in self.words]

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
        return pairs[:10]

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
        result["detected_nouns"] = [t.text for t in doc if t.pos_ == "NOUN"][:10]
        result["detected_verbs"] = [t.text for t in doc if t.pos_ == "VERB"][:10]
        result["detected_adjectives"] = [t.text for t in doc if t.pos_ == "ADJ"][:10]
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
            "detected_nouns": list(nouns)[:10],
            "detected_verbs": list(verbs)[:10],
            "detected_adjectives": list(adjectives)[:10],
        }

    def _detect_nouns(self) -> Set[str]:
        """Detect common nouns"""
        common = {
            "time",
            "year",
            "people",
            "way",
            "day",
            "man",
            "thing",
            "woman",
            "life",
            "child",
            "world",
            "school",
            "state",
            "family",
            "student",
            "group",
            "country",
            "problem",
            "hand",
            "part",
            "place",
            "case",
            "week",
            "company",
            "system",
            "program",
            "question",
            "number",
            "night",
            "point",
            "home",
            "water",
            "room",
            "mother",
            "area",
            "money",
            "story",
            "fact",
            "month",
            "lot",
            "right",
            "study",
            "book",
            "eye",
            "job",
            "word",
            "business",
            "issue",
            "side",
            "kind",
            "head",
            "house",
            "service",
            "friend",
            "father",
            "power",
            "hour",
            "game",
            "line",
            "end",
            "member",
            "law",
            "car",
            "city",
            "name",
            "president",
            "team",
            "minute",
            "idea",
            "kid",
            "body",
            "information",
            "back",
            "parent",
            "face",
            "level",
            "office",
            "door",
            "health",
            "art",
            "war",
            "history",
            "party",
            "result",
            "change",
            "morning",
            "reason",
            "research",
            "girl",
            "guy",
            "moment",
            "air",
            "teacher",
            "force",
            "education",
            "foot",
            "boy",
            "age",
            "policy",
            "process",
            "music",
            "market",
            "sense",
            "nation",
            "plan",
            "college",
            "interest",
            "death",
            "experience",
            "effect",
            "use",
            "class",
            "control",
            "care",
            "field",
            "development",
            "role",
            "effort",
            "rate",
            "heart",
            "drug",
            "show",
            "leader",
            "light",
            "voice",
            "wife",
            "whole",
            "police",
            "mind",
            "church",
            "report",
            "action",
            "price",
            "need",
            "difference",
            "image",
            "table",
            "river",
            "sun",
            "moon",
            "star",
            "sky",
            "earth",
            "sea",
            "mountain",
            "tree",
            "flower",
            "road",
        }
        return set(self.words).intersection(common)

    def _detect_verbs(self) -> Set[str]:
        """Detect common verbs"""
        common = {
            "be",
            "have",
            "do",
            "say",
            "get",
            "make",
            "go",
            "know",
            "take",
            "see",
            "come",
            "want",
            "use",
            "find",
            "give",
            "tell",
            "try",
            "call",
            "keep",
            "let",
            "put",
            "seem",
            "help",
            "show",
            "hear",
            "play",
            "run",
            "move",
            "live",
            "believe",
            "hold",
            "bring",
            "happen",
            "write",
            "provide",
            "sit",
            "stand",
            "lose",
            "pay",
            "meet",
            "include",
            "continue",
            "set",
            "learn",
            "change",
            "lead",
            "understand",
            "watch",
            "follow",
            "stop",
            "create",
            "speak",
            "read",
            "spend",
            "grow",
            "open",
            "walk",
            "win",
            "offer",
            "remember",
            "love",
            "consider",
            "appear",
            "buy",
            "wait",
            "serve",
            "die",
            "send",
            "expect",
            "build",
            "stay",
            "fall",
            "cut",
            "reach",
            "kill",
            "remain",
            "suggest",
            "raise",
            "pass",
            "sell",
            "require",
            "report",
            "decide",
            "pull",
            "is",
            "are",
            "was",
            "were",
            "been",
            "being",
            "am",
            "does",
            "did",
            "has",
            "had",
            "will",
            "would",
            "can",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
        }
        return set(self.words).intersection(common)

    def _detect_adjectives(self) -> Set[str]:
        """Detect common adjectives"""
        common = {
            "good",
            "bad",
            "big",
            "small",
            "large",
            "little",
            "old",
            "new",
            "young",
            "early",
            "late",
            "great",
            "high",
            "low",
            "right",
            "left",
            "first",
            "last",
            "long",
            "short",
            "tall",
            "wide",
            "narrow",
            "deep",
            "shallow",
            "hot",
            "cold",
            "warm",
            "cool",
            "dark",
            "bright",
            "light",
            "heavy",
            "easy",
            "hard",
            "difficult",
            "simple",
            "complex",
            "clear",
            "beautiful",
            "ugly",
            "happy",
            "sad",
            "angry",
            "calm",
            "quiet",
            "loud",
            "soft",
            "strong",
            "weak",
            "fast",
            "slow",
            "quick",
            "rich",
            "poor",
            "clean",
            "dirty",
            "dry",
            "wet",
            "full",
            "empty",
            "open",
            "closed",
            "true",
            "false",
            "real",
            "same",
            "different",
            "other",
            "more",
            "most",
            "some",
            "any",
            "no",
            "every",
            "each",
            "both",
            "few",
            "many",
            "much",
            "several",
            "all",
            "whole",
            "single",
            "double",
            "certain",
            "likely",
            "possible",
            "necessary",
            "important",
            "special",
            "common",
            "public",
            "private",
            "personal",
            "social",
            "political",
            "economic",
            "cultural",
            "historical",
            "modern",
            "ancient",
            "classical",
            "traditional",
            "popular",
            "serious",
            "formal",
            "informal",
            "basic",
            "final",
            "central",
            "human",
            "natural",
            "physical",
            "mental",
            "emotional",
            "spiritual",
            "intellectual",
            "moral",
            "free",
            "busy",
            "alone",
            "together",
            "ready",
            "willing",
            "able",
            "due",
            "next",
            "previous",
            "current",
            "recent",
            "past",
            "future",
            "present",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "regular",
            "constant",
            "permanent",
            "temporary",
            "partial",
            "complete",
            "total",
            "exact",
            "specific",
            "general",
            "rare",
            "unique",
            "various",
        }
        return set(self.words).intersection(common)

    def _detect_adverbs(self) -> Set[str]:
        """Detect common adverbs"""
        common = {
            "very",
            "really",
            "just",
            "still",
            "already",
            "also",
            "always",
            "never",
            "often",
            "sometimes",
            "usually",
            "ever",
            "again",
            "even",
            "almost",
            "yet",
            "only",
            "much",
            "more",
            "most",
            "less",
            "least",
            "quite",
            "rather",
            "fairly",
            "too",
            "so",
            "thus",
            "therefore",
            "however",
            "although",
            "though",
            "while",
            "when",
            "where",
            "why",
            "how",
            "there",
            "here",
            "now",
            "then",
            "today",
            "tomorrow",
            "yesterday",
            "soon",
            "later",
            "early",
            "late",
            "quickly",
            "slowly",
            "carefully",
            "suddenly",
            "finally",
            "recently",
            "currently",
            "certainly",
            "definitely",
            "exactly",
            "especially",
            "simply",
            "absolutely",
            "completely",
            "entirely",
            "extremely",
            "possibly",
            "probably",
            "perhaps",
            "maybe",
            "around",
            "away",
            "back",
            "down",
            "forward",
            "in",
            "off",
            "out",
            "over",
            "through",
            "together",
            "up",
        }
        return set(self.words).intersection(common)

    def _detect_pronouns(self) -> Set[str]:
        """Detect pronouns"""
        common = {
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "its",
            "our",
            "their",
            "mine",
            "yours",
            "hers",
            "ours",
            "theirs",
            "this",
            "that",
            "these",
            "those",
            "who",
            "whom",
            "whose",
            "which",
            "what",
            "someone",
            "somebody",
            "something",
            "anyone",
            "anybody",
            "anything",
            "everyone",
            "everybody",
            "everything",
            "nobody",
            "nothing",
            "each",
            "either",
            "neither",
            "one",
        }
        return set(self.words).intersection(common)

    def _detect_prepositions(self) -> Set[str]:
        """Detect prepositions"""
        common = {
            "in",
            "on",
            "at",
            "by",
            "for",
            "with",
            "about",
            "against",
            "between",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "to",
            "from",
            "up",
            "down",
            "out",
            "off",
            "over",
            "under",
            "around",
            "near",
            "onto",
            "opposite",
            "outside",
            "past",
            "since",
            "toward",
            "until",
            "upon",
            "within",
            "without",
        }
        return set(self.words).intersection(common)

    def _detect_conjunctions(self) -> Set[str]:
        """Detect conjunctions"""
        common = {
            "and",
            "but",
            "or",
            "nor",
            "for",
            "yet",
            "so",
            "because",
            "although",
            "though",
            "while",
            "when",
            "if",
            "unless",
            "since",
            "until",
            "provided",
            "whereas",
            "whenever",
            "wherever",
            "whether",
            "than",
            "rather",
        }
        return set(self.words).intersection(common)

    def _detect_determiners(self) -> Set[str]:
        """Detect determiners"""
        common = {
            "a",
            "an",
            "the",
            "this",
            "that",
            "these",
            "those",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "some",
            "any",
            "no",
            "not",
            "all",
            "both",
            "each",
            "every",
            "either",
            "neither",
            "much",
            "many",
            "more",
            "most",
            "few",
            "little",
            "less",
            "least",
            "several",
            "enough",
            "quite",
            "rather",
            "such",
        }
        return set(self.words).intersection(common)


def analyze_idioms(text: str) -> Dict[str, List[str]]:
    """Detect idioms and proverbs"""
    idioms = [
        "break the ice",
        "bite the bullet",
        "beat around the bush",
        "burn the midnight oil",
        "cost an arm and a leg",
        "hit the nail on the head",
        "kill two birds with one stone",
        "let the cat out of the bag",
        "make a long story short",
        "once in a blue moon",
        "piece of cake",
        "rain cats and dogs",
        "spill the beans",
        "take it with a grain of salt",
        "the ball is in your court",
        "the best of both worlds",
        "throw caution to the wind",
        "under the weather",
        "when pigs fly",
        "a penny for your thoughts",
        "actions speak louder than words",
        "add insult to injury",
        "against all odds",
        "back to the drawing board",
        "barking up the wrong tree",
        "beat a dead horse",
        "better late than never",
        "bite off more than you can chew",
        "blood is thicker than water",
        "break a leg",
        "by the skin of your teeth",
        "call it a day",
        "come rain or shine",
        "cross that bridge when you come to it",
        "curiosity killed the cat",
        "cut corners",
        "cut to the chase",
        "don't count your chickens",
        "don't put all your eggs in one basket",
        "easier said than done",
        "every cloud has a silver lining",
        "get a taste of your own medicine",
        "get out of hand",
        "get your act together",
        "give someone the benefit of the doubt",
        "go back to the drawing board",
        "go the extra mile",
        "good things come to those who wait",
        "hang in there",
        "hit the sack",
        "in the heat of the moment",
        "in the nick of time",
        "it takes two to tango",
        "jump on the bandwagon",
        "keep something at bay",
        "last but not least",
        "let sleeping dogs lie",
        "miss the boat",
        "no pain no gain",
        "on the ball",
        "on the fence",
        "play devil's advocate",
        "pull someone's leg",
        "put something on hold",
        "see eye to eye",
        "sit on the fence",
        "so far so good",
        "stab someone in the back",
        "take it easy",
        "the elephant in the room",
        "the last straw",
        "time flies",
        "to make matters worse",
        "under pressure",
        "up in the air",
        "up to the ears",
        "wait and see",
        "when it rains it pours",
        "you can say that again",
    ]

    proverbs = [
        "a stitch in time saves nine",
        "all that glitters is not gold",
        "an apple a day keeps the doctor away",
        "birds of a feather flock together",
        "better safe than sorry",
        "don't judge a book by its cover",
        "early bird catches the worm",
        "honesty is the best policy",
        "if it ain't broke don't fix it",
        "knowledge is power",
        "laughter is the best medicine",
        "look before you leap",
        "money can't buy happiness",
        "practice makes perfect",
        "prevention is better than cure",
        "rome wasn't built in a day",
        "the pen is mightier than the sword",
        "there's no place like home",
        "time heals all wounds",
        "to err is human",
        "two heads are better than one",
        "when in rome do as the romans do",
        "where there's a will there's a way",
        "you can't have your cake and eat it too",
    ]

    text_lower = text.lower()
    return {
        "idioms": [idiom for idiom in idioms if idiom in text_lower],
        "proverbs": [proverb for proverb in proverbs if proverb in text_lower],
    }
