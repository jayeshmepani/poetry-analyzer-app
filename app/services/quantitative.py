"""
Complete Quantitative Metrics Implementation
Implements ALL metrics from quantitative_poetry_metrics.md

Metrics covered:
- Lexical Diversity: TTR, MTLD, MATTR, Yule's K, Sichel's S, Herdan's C, etc.
- Readability: 15+ formulas (Flesch, Flesch-Kincaid, Gunning Fog, SMOG, etc.)
- Syllable Analysis: Complete syllable counting and distribution
- Word Metrics: Length, frequency, hapax/dis legomena
- Sentence/Line Metrics: Length, enjambment, etc.
"""

import re
import math
from typing import List, Dict, Tuple, Any
from collections import Counter
import syllables
import textstat
import pyphen
import textdescriptives as td
import spacy

from app.services.rule_loader import get_quantitative_rules


class QuantitativeMetricsCalculator:
    """
    Complete implementation of ALL quantitative poetry metrics
    from quantitative_poetry_metrics.md specification
    """

    def __init__(self, text: str = "", language: str = "en"):
        self.language = language
        self.original_text = text
        self.text = text.lower()
        self.sentences = self._get_sentences() if text else []
        self.words = self._get_words() if text else []
        self.lines = self._get_lines() if text else []
        self.word_freq = Counter(self.words)
        self.total_words = len(self.words)
        self.unique_words = len(set(self.words))
        self._rules = get_quantitative_rules()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run all quantitative metrics"""
        self.original_text = text
        self.text = text.lower()
        self.sentences = self._get_sentences()
        self.words = self._get_words()
        self.lines = self._get_lines()
        self.word_freq = Counter(self.words)
        self.total_words = len(self.words)
        self.unique_words = len(set(self.words))

        # Build the schema-compliant structure
        lexical = self._all_lexical_diversity_metrics()
        readability = self._all_readability_metrics()
        structural = self._complete_structural_metrics()
        syllables = self._complete_syllable_analysis()
        word_metrics = self._complete_word_metrics()
        
        # Get advanced metrics from textdescriptives (50+ additional metrics)
        advanced = self._advanced_textdescriptives_metrics()

        metrics = {
            "lexical_metrics": {
                **lexical,
                "matttr": lexical.get("mattr", 0),  # alias for schema
            },
            "syllable_metrics": syllables,
            "readability_metrics": {
                **readability,
                "avg_sentence_length": structural.get("avg_words_per_sentence", 0),
                "avg_word_length": sum(len(w) for w in self.words)
                / max(1, self.total_words),
            },
            "structural_metrics": structural,
            "word_metrics": word_metrics,
            "computational_greatness_score": None,
            "advanced_metrics": advanced,  # NEW: textdescriptives metrics
        }

        # Add language-specific metrics
        if self.language in ["hi", "ur", "mr", "gu", "bn"]:
            metrics["hindi_metrics"] = self._calculate_hindi_metrics()

        # Calculate computational greatness score
        metrics["computational_greatness_score"] = (
            self._calculate_computational_greatness(metrics)
        )

        return metrics

    def _calculate_hindi_metrics(self) -> Dict[str, Any]:
        """Calculate Hindi-specific readability metrics"""
        if not self.words:
            return {
                "rh1_score": 0.0,
                "rh2_score": 0.0,
                "matra_complexity_index": 0.0,
                "avg_akshars_per_word": 0.0,
                "jukta_akshar_density": 0.0,
            }

        total_akshars = sum(self._count_akshars(w) for w in self.words)
        avg_word_length = total_akshars / len(self.words)

        # JUK: conjunct consonants per 100 words
        virama_map = {
            "hi": "्",
            "mr": "्",
            "bn": "্",
            "gu": "્",
        }
        virama = virama_map.get(self.language, "")
        jukta_count = sum(word.count(virama) for word in self.words) if virama else 0
        jukta_density = (jukta_count / len(self.words)) * 100

        # PSW: percentage of polysyllabic words (>=3 akshars)
        polysyllabic = sum(1 for w in self.words if self._count_akshars(w) >= 3)
        psw = (polysyllabic / len(self.words)) * 100

        # RH1/RH2 (Sinha et al.)
        rh1_score = -2.34 + 2.14 * avg_word_length + 0.01 * jukta_density
        rh2_score = -0.82 + 1.83 * avg_word_length + 0.09 * psw

        # Matra Complexity Index (MCI) = guru syllables / total syllables * 100
        guru_count, total_syllables = self._count_guru_syllables(self.words)
        matra_complexity = (guru_count / total_syllables * 100) if total_syllables > 0 else 0.0

        return {
            "rh1_score": round(rh1_score, 2),
            "rh2_score": round(rh2_score, 2),
            "matra_complexity_index": round(matra_complexity, 2),
            "avg_akshars_per_word": round(avg_word_length, 2),
            "jukta_akshar_density": round(jukta_density, 2),
        }

    def _advanced_textdescriptives_metrics(self) -> Dict[str, Any]:
        """Extract 50+ advanced metrics using textdescriptives library"""
        try:
            # Load spaCy model if not already loaded
            if not hasattr(self, '_nlp'):
                try:
                    self._nlp = spacy.load("en_core_web_trf")
                except:
                    self._nlp = spacy.load("en_core_web_sm")
            
            # Process text with spaCy
            doc = self._nlp(self.original_text)
            
            # Extract comprehensive metrics using textdescriptives
            metrics = td.extract_metrics(
                doc,
                metrics=[
                    "lexical_density",
                    "coherence", 
                    "dependency_distance",
                    "pos_proportions",
                    "quality"
                ],
                include_qi=True
            )
            
            # Flatten and return metrics
            return {
                "textdescriptives_metrics": metrics,
                "lexical_density_advanced": metrics.get('lexical_density', {}).get('lexical_density', 0),
                "coherence_score": metrics.get('coherence', {}).get('coherence', 0),
                "dependency_distance_mean": metrics.get('dependency_distance', {}).get('mean_dependency_distance', 0),
                "pos_proportions": metrics.get('pos_proportions', {}),
                "quality_score": metrics.get('quality', {}).get('quality_score', 0),
            }
        except Exception as e:
            # Fallback if textdescriptives fails
            return {
                "textdescriptives_metrics": {},
                "error": str(e),
                "fallback_used": True
            }

    def _syllables_with_pyphen(self, word: str) -> int:
        """Count syllables using pyphen library for better accuracy"""
        try:
            dic = pyphen.Pyphen(lang='en')
            hyphenated = dic.inserted(word)
            return len(hyphenated.split('-'))
        except:
            # Fallback to default syllables library
            return syllables.estimate(word)

    def _calculate_computational_greatness(self, metrics: Dict[str, Any]) -> float:
        """Calculate composite 'Computational Greatness' score"""
        # Normalize metrics across comparison set: poem + canonical touchstones
        candidates = [self.original_text] + self._touchstone_passages()

        def _metric_bundle(text: str) -> Dict[str, float]:
            calc = QuantitativeMetricsCalculator(text=text, language=self.language)
            base = calc._all_lexical_diversity_metrics()
            ld = base.get("lexical_density", 0.0)
            mtld = base.get("mtld", 0.0)
            ttr_val = base.get("type_token_ratio", 0.0)
            ppl = calc._calculate_perplexity()
            n_emb = calc._embedding_novelty(text, self._touchstone_passages())
            r_d = calc._calculate_rhyme_density_pairwise(text)
            return {"ld": ld, "mtld": mtld, "ttr": ttr_val, "ppl": ppl, "n_emb": n_emb, "r_d": r_d}

        bundles = [_metric_bundle(t) for t in candidates]

        def _norm(key: str, value: float) -> float:
            values = [b[key] for b in bundles]
            vmin, vmax = min(values), max(values)
            if vmax - vmin == 0:
                return 0.0
            return (value - vmin) / (vmax - vmin)

        current = _metric_bundle(self.original_text)
        ld_n = _norm("ld", current["ld"])
        mtld_n = _norm("mtld", current["mtld"])
        ppl_n = _norm("ppl", current["ppl"])
        nemb_n = _norm("n_emb", current["n_emb"])
        rd_n = _norm("r_d", current["r_d"])

        # G_comp = w1*Ld + w2*MTLD + w3*(1-PPL) + w4*N_emb + w5*R_d
        weights = self._rules["computational_greatness"]["weights"]
        scale = float(self._rules["computational_greatness"]["scale"])
        score = (
            weights["ld"] * ld_n
            + weights["mtld"] * mtld_n
            + weights["ppl"] * (1 - ppl_n)
            + weights["n_emb"] * nemb_n
            + weights["r_d"] * rd_n
        )
        return round(score * scale, 2)

    def _calculate_rhyme_density_pairwise(self, text: str) -> float:
        """Exact rhyme density: R / (n(n-1)/2) on end words."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        last_words = []
        for line in lines:
            words = line.split()
            if words:
                last_words.append(words[-1].lower().strip(".,!?;:'\""))
        n = len(last_words)
        if n < 2:
            return 0.0
        pairs = n * (n - 1) / 2
        r = 0
        for i in range(n):
            for j in range(i + 1, n):
                if self._rhymes_with(last_words[i], last_words[j]):
                    r += 1
        return r / pairs

    def _rhymes_with(self, word1: str, word2: str) -> bool:
        if not word1 or not word2:
            return False
        from app.services.phonology_resources import get_phonology

        phon = get_phonology(self.language)
        part1 = phon.rhyme_key(word1)
        part2 = phon.rhyme_key(word2)
        return bool(part1 and part2 and part1 == part2)

    def _touchstone_passages(self) -> List[str]:
        from app.services.touchstone_loader import select_touchstone_passages
        try:
            from app.config import Settings
            limit = Settings().touchstone.max_passages
        except Exception:
            limit = 4
        return select_touchstone_passages(self.original_text, limit=limit)

    def _embedding_novelty(self, text: str, canon: List[str]) -> float:
        """Novelty = 1 - max cosine similarity to canonical set."""
        try:
            if not hasattr(self, "_nlp"):
                try:
                    self._nlp = spacy.load("en_core_web_trf")
                except Exception:
                    self._nlp = spacy.load("en_core_web_sm")
            doc = self._nlp(text)
            if not doc.has_vector:
                return 0.0
            sims = []
            for passage in canon:
                d2 = self._nlp(passage)
                if d2.has_vector:
                    sims.append(doc.similarity(d2))
            if not sims:
                return 0.0
            max_sim = max(sims)
            return max(0.0, min(1.0, 1 - max_sim))
        except Exception:
            return 0.0

    def _count_akshars(self, word: str) -> int:
        """Count akshars/syllable nuclei in Indic/Urdu scripts."""
        if not word:
            return 0
        script_vowels = {
            "hi": (set("अआइईउऊऋएऐओऔ"), set("ािीुूृेैोौंः")),
            "mr": (set("अआइईउऊऋएऐओऔ"), set("ािीुूृेैोौंः")),
            "bn": (set("অআইঈউঊঋএঐওঔ"), set("ািীুূৃেৈোৌংঃ")),
            "gu": (set("અઆઇઈઉઊઋએઐઓઔ"), set("ાિીુૂૃેૈોૌંઃ")),
        }
        if self.language in script_vowels:
            independent_vowels, vowel_signs = script_vowels[self.language]
            count = sum(1 for ch in word if ch in independent_vowels or ch in vowel_signs)
            return count if count > 0 else 1

        # Urdu/Arabic and other scripts: fall back to multilingual syllable estimator.
        return self._get_syllables_per_word(word)

    def _count_guru_syllables(self, words: List[str]) -> Tuple[int, int]:
        """Count guru syllables and total syllables for MCI."""
        script_sets = {
            "hi": {
                "guru_vowels": set("आईऊएऐओऔ"),
                "guru_signs": set("ाीूेैोौ"),
                "short_vowels": set("अइउऋ"),
                "short_signs": set("िुृ"),
                "anusvara_visarga": set("ंः"),
                "virama": "्",
            },
            "mr": {
                "guru_vowels": set("आईऊएऐओऔ"),
                "guru_signs": set("ाीूेैोौ"),
                "short_vowels": set("अइउऋ"),
                "short_signs": set("िुृ"),
                "anusvara_visarga": set("ंः"),
                "virama": "्",
            },
            "bn": {
                "guru_vowels": set("আঈঊএঐওঔ"),
                "guru_signs": set("াীূেৈোৌ"),
                "short_vowels": set("অইউঋ"),
                "short_signs": set("িুৃ"),
                "anusvara_visarga": set("ংঃ"),
                "virama": "্",
            },
            "gu": {
                "guru_vowels": set("આઈઊએઐઓઔ"),
                "guru_signs": set("ાીૂેૈોૌ"),
                "short_vowels": set("અઇઉઋ"),
                "short_signs": set("િુૃ"),
                "anusvara_visarga": set("ંઃ"),
                "virama": "્",
            },
        }
        sets = script_sets.get(self.language)
        if not sets:
            # For scripts without laghu/guru marks (e.g., Urdu), return total
            # syllables with guru=0 to keep MCI mathematically defined.
            total = sum(self._get_syllables_per_word(w) for w in words)
            return 0, total

        guru_vowels = sets["guru_vowels"]
        guru_signs = sets["guru_signs"]
        short_vowels = sets["short_vowels"]
        short_signs = sets["short_signs"]
        anusvara_visarga = sets["anusvara_visarga"]
        virama = sets["virama"]
        total = 0
        guru = 0
        for word in words:
            chars = list(word)
            for i, ch in enumerate(chars):
                if ch in guru_vowels or ch in guru_signs:
                    total += 1
                    guru += 1
                elif ch in short_vowels or ch in short_signs:
                    total += 1
                    next_char = chars[i + 1] if i + 1 < len(chars) else ""
                    if next_char == virama or next_char in anusvara_visarga:
                        guru += 1
        return guru, total

    def _get_sentences(self) -> List[str]:
        """Extract sentences from text"""
        sentences = re.split(r"[.!?।]", self.original_text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_words(self) -> List[str]:
        """Extract words from text (multilingual support)"""
        # Support for Devanagari, Arabic, Latin scripts
        words = re.findall(r"[\w\u0900-\u097F\u0600-\u06FF]+", self.text)
        return words

    def _get_lines(self) -> List[str]:
        """Extract lines from text"""
        lines = self.original_text.strip().split("\n")
        return [l.strip() for l in lines if l.strip()]

    def _get_syllables_per_word(self, word: str) -> int:
        """Get syllable count for a word (multilingual)"""
        try:
            # For English words - use pyphen for better accuracy
            if re.match(r"^[a-zA-Z]+$", word):
                return self._syllables_with_pyphen(word)
            # For Hindi/Indic words - count vowel marks
            elif re.match(r"^[\u0900-\u097F]+$", word):
                vowels = re.findall(r"[\u0904-\u0914\u093A-\u0944]", word)
                return max(1, len(vowels))
            # For Arabic/Urdu words
            elif re.match(r"^[\u0600-\u06FF]+$", word):
                vowels = re.findall(r"[\u064B-\u0652\u0670]", word)
                return max(1, len(vowels))
            else:
                return max(
                    1,
                    len(
                        re.findall(r"[aeiouy\u0904-\u0914\u064B-\u0652]", word.lower())
                    ),
                )
        except:
            return 1

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get ALL quantitative metrics in one call
        Returns comprehensive metrics dictionary
        """
        return {
            # Lexical Diversity Metrics
            "lexical_diversity": self._all_lexical_diversity_metrics(),
            # Readability Metrics
            "readability": self._all_readability_metrics(),
            # Syllable Analysis
            "syllable_analysis": self._complete_syllable_analysis(),
            # Word Metrics
            "word_metrics": self._complete_word_metrics(),
            # Line/Sentence Metrics
            "structural_metrics": self._complete_structural_metrics(),
            # Advanced Metrics
            "advanced_metrics": self._advanced_metrics(),
        }

    def _all_lexical_diversity_metrics(self) -> Dict[str, float]:
        """Calculate ALL lexical diversity metrics"""
        return {
            # Basic TTR
            "type_token_ratio": self._calculate_ttr(),
            "corrected_ttr": self._calculate_corrected_ttr(),
            # Advanced TTR variants
            "mattr": self._calculate_mattr(),
            "mattr_10": self._calculate_mattr(window_size=10),
            "mattr_50": self._calculate_mattr(window_size=50),
            "mattr_100": self._calculate_mattr(window_size=100),
            "mtld": self._calculate_mtld(),
            "mtld_mean": self._calculate_mtld_mean(),
            # Yule's characteristics
            "yules_k": self._calculate_yules_k(),
            "yules_i": self._calculate_yules_i(),
            # Sichel's parameter
            "sichels_s": self._calculate_sichels_s(),
            # Herdan's constant
            "herdans_c": self._calculate_herdans_c(),
            # Kuraszkiewicz's coefficient
            "kuraszkiewicz_w": self._calculate_kuraszkiewicz_w(),
            # Honoré's statistic
            "honores_r": self._calculate_honores_r(),
            # Somers' measure
            "somers_measure": self._calculate_somers_measure(),
            # Lexical density
            "lexical_density": self._calculate_lexical_density(),
            "lexical_density_percent": self._calculate_lexical_density_percent(),
            "content_word_ratio": self._calculate_content_word_ratio(),
        }

    def _all_readability_metrics(self) -> Dict[str, float]:
        """Calculate ALL 15+ readability formulas"""
        text = self.original_text

        return {
            # Most common
            "flesch_reading_ease": textstat.flesch_reading_ease(text) if text else 0,
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text) if text else 0,
            "gunning_fog": textstat.gunning_fog(text) if text else 0,
            "smog_index": textstat.smog_index(text) if text else 0,
            "automated_readability_index": textstat.automated_readability_index(text)
            if text
            else 0,
            "coleman_liau_index": textstat.coleman_liau_index(text) if text else 0,
            "linsear_write_formula": textstat.linsear_write_formula(text)
            if text
            else 0,
            "dale_chall_readability_score": textstat.dale_chall_readability_score(text)
            if text
            else 0,
            # Additional formulas
            "text_standard": textstat.text_standard(text) if text else "N/A",
            "spache_readability": self._calculate_spache(),
            "raygor_readability": self._calculate_raygor(),
            "fry_readability": self._calculate_fry(),
            "forcast_readability": self._calculate_forcast(),
            "powers_sumner_kearl": self._calculate_powers_sumner_kearl(),
            "danielson_bryan": self._calculate_danielson_bryan(),
            "wheeler_smith": self._calculate_wheeler_smith(),
            # Average grade level
            "average_grade_level": self._calculate_average_grade_level(),
        }

    def _complete_syllable_analysis(self) -> Dict[str, Any]:
        """Complete syllable analysis"""
        syllable_counts = [self._get_syllables_per_word(word) for word in self.words]

        if not syllable_counts:
            return {
                "total_syllables": 0,
                "avg_syllables_per_word": 0,
                "syllable_distribution": {},
                "monosyllabic_words": 0,
                "disyllabic_words": 0,
                "polysyllabic_words": 0,
                "syllables_per_line": [],
            }

        total_syllables = sum(syllable_counts)
        avg_syllables = total_syllables / len(syllable_counts) if syllable_counts else 0

        # Syllable distribution
        dist = Counter(syllable_counts)

        # Word categories by syllables
        monosyllabic = sum(1 for s in syllable_counts if s == 1)
        disyllabic = sum(1 for s in syllable_counts if s == 2)
        polysyllabic = sum(1 for s in syllable_counts if s >= 3)

        # Syllables per line
        syllables_per_line = []
        for line in self.lines:
            line_words = re.findall(r"[\w\u0900-\u097F\u0600-\u06FF]+", line.lower())
            line_syllables = sum(self._get_syllables_per_word(w) for w in line_words)
            syllables_per_line.append(line_syllables)

        return {
            "total_syllables": total_syllables,
            "avg_syllables_per_word": round(avg_syllables, 3),
            "syllable_distribution": dict(dist),
            "monosyllabic_words": monosyllabic,
            "monosyllabic_percentage": round(
                (monosyllabic / len(syllable_counts)) * 100, 2
            )
            if syllable_counts
            else 0,
            "disyllabic_words": disyllabic,
            "disyllabic_percentage": round((disyllabic / len(syllable_counts)) * 100, 2)
            if syllable_counts
            else 0,
            "polysyllabic_words": polysyllabic,
            "polysyllabic_percentage": round(
                (polysyllabic / len(syllable_counts)) * 100, 2
            )
            if syllable_counts
            else 0,
            "syllables_per_line": syllables_per_line,
            "avg_syllables_per_line": round(
                sum(syllables_per_line) / len(syllables_per_line), 2
            )
            if syllables_per_line
            else 0,
        }

    def _complete_word_metrics(self) -> Dict[str, Any]:
        """Complete word-level metrics"""
        if not self.words:
            return {
                "total_words": 0,
                "unique_words": 0,
                "avg_word_length": 0,
                "word_length_distribution": {},
                "hapax_legomena": 0,
                "dis_legomena": 0,
                "avg_word_frequency": 0,
            }

        word_lengths = [len(w) for w in self.words]
        avg_word_length = sum(word_lengths) / len(word_lengths)

        # Word length distribution
        length_dist = Counter(word_lengths)

        # Hapax and Dis Legomena
        hapax = sum(1 for w, c in self.word_freq.items() if c == 1)
        dis = sum(1 for w, c in self.word_freq.items() if c == 2)

        # Average word frequency
        avg_freq = (
            sum(self.word_freq.values()) / len(self.word_freq) if self.word_freq else 0
        )

        return {
            "total_words": self.total_words,
            "unique_words": self.unique_words,
            "avg_word_length": round(avg_word_length, 3),
            "word_length_distribution": dict(length_dist),
            "shortest_word": min(word_lengths) if word_lengths else 0,
            "longest_word": max(word_lengths) if word_lengths else 0,
            "hapax_legomena": hapax,
            "hapax_percentage": round((hapax / self.unique_words) * 100, 2)
            if self.unique_words
            else 0,
            "dis_legomena": dis,
            "dis_percentage": round((dis / self.unique_words) * 100, 2)
            if self.unique_words
            else 0,
            "avg_word_frequency": round(avg_freq, 3),
            "most_common_words": self.word_freq.most_common(10),
        }

    def _complete_structural_metrics(self) -> Dict[str, Any]:
        """Complete line and sentence metrics"""
        if not self.lines:
            return {
                "total_lines": 0,
                "avg_line_length_words": 0,
                "avg_line_length_chars": 0,
                "total_sentences": 0,
                "avg_sentence_length": 0,
                "enjambment_ratio": 0,
                "end_stopped_ratio": 0,
                "end_syllable_density": 0.0,
            }

        # Line metrics
        line_word_counts = [
            len(re.findall(r"[\w\u0900-\u097F\u0600-\u06FF]+", line))
            for line in self.lines
        ]
        line_char_counts = [len(line) for line in self.lines]

        # Sentence metrics
        num_sentences = len(self.sentences)
        avg_sentence_length = (
            self.total_words / num_sentences if num_sentences > 0 else 0
        )

        # Enjambment detection (lines without end punctuation)
        end_stopped = sum(
            1 for line in self.lines if line.rstrip()[-1] in ".!?।,;" if line.rstrip()
        )
        enjambed = len(self.lines) - end_stopped
        enjambment_ratio = enjambed / len(self.lines) if self.lines else 0

        return {
            "total_lines": len(self.lines),
            "avg_line_length_words": round(
                sum(line_word_counts) / len(line_word_counts), 2
            )
            if line_word_counts
            else 0,
            "avg_line_length_chars": round(
                sum(line_char_counts) / len(line_char_counts), 2
            )
            if line_char_counts
            else 0,
            "shortest_line_words": min(line_word_counts) if line_word_counts else 0,
            "longest_line_words": max(line_word_counts) if line_word_counts else 0,
            "total_sentences": num_sentences,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "enjambment_ratio": round(enjambment_ratio, 3),
            "end_stopped_ratio": round(1 - enjambment_ratio, 3),
            "end_stopped_lines": end_stopped,
            "enjambed_lines": enjambed,
            "end_syllable_density": round(self._calculate_end_syllable_density(), 4),
        }

    def _calculate_end_syllable_density(self) -> float:
        """
        A_d = (Lines with matching end-syllable patterns) / (Total Lines)
        """
        if not self.lines:
            return 0.0
        from app.services.phonology_resources import get_phonology

        phon = get_phonology(self.language)
        end_keys = []
        for line in self.lines:
            words = line.split()
            if not words:
                end_keys.append(None)
                continue
            key = phon.rhyme_key(words[-1])
            end_keys.append(key)
        # Count lines whose key appears at least twice
        counts = Counter(k for k in end_keys if k)
        matching = sum(1 for k in end_keys if k and counts.get(k, 0) >= 2)
        return matching / len(self.lines) if self.lines else 0.0

    def _advanced_metrics(self) -> Dict[str, float]:
        """Advanced linguistic metrics"""
        return {
            # Sentence complexity
            "avg_words_per_sentence": self.total_words / len(self.sentences)
            if self.sentences
            else 0,
            # Word frequency metrics
            "repeated_word_ratio": self._calculate_repeated_word_ratio(),
            # Vocabulary richness
            "vocabulary_richness": self._calculate_vocabulary_richness(),
            # Information density
            "information_density": self._calculate_information_density(),
        }

    # ==================== LEXICAL DIVERSITY METRICS ====================

    def _calculate_ttr(self) -> float:
        """Type-Token Ratio: Unique Words / Total Words"""
        if self.total_words == 0:
            return 0.0
        return round(self.unique_words / self.total_words, 4)

    def _calculate_corrected_ttr(self) -> float:
        """Corrected TTR: (Unique Words / sqrt(2 * Total Words)) * 100"""
        if self.total_words == 0:
            return 0.0
        return round((self.unique_words / math.sqrt(2 * self.total_words)) * 100, 4)

    def _calculate_mattr(self, window_size: int = 50) -> float:
        """Moving-Average Type-Token Ratio"""
        if len(self.words) < window_size:
            return self._calculate_ttr()

        ttrs = []
        for i in range(len(self.words) - window_size + 1):
            window = self.words[i : i + window_size]
            ttr = len(set(window)) / len(window)
            ttrs.append(ttr)

        return round(sum(ttrs) / len(ttrs), 4) if ttrs else 0.0

    def _calculate_mtld(self, threshold: float = 0.72) -> float:
        """
        Measure of Textual Lexical Diversity
        Counts how many words needed to reach TTR threshold
        """
        if self.total_words == 0:
            return 0.0

        factors = []
        start = 0

        while start < self.total_words:
            end = start + 1
            while end <= self.total_words:
                segment = self.words[start:end]
                ttr = len(set(segment)) / len(segment)
                if ttr < threshold:
                    break
                end += 1

            factor_length = end - start - 1
            if factor_length > 0:
                factors.append(factor_length)
            start = end - 1 if end > start + 1 else start + 1

        if not factors:
            return round(self.total_words / max(1, self.unique_words), 2)

        return round(sum(factors) / len(factors), 2)

    def _calculate_mtld_mean(self) -> float:
        """MTLD Mean (bidirectional average)"""
        # Forward MTLD
        mtld_forward = self._calculate_mtld()

        # Backward MTLD (reverse word list)
        self.words.reverse()
        mtld_backward = self._calculate_mtld()
        self.words.reverse()  # Restore original order

        return round((mtld_forward + mtld_backward) / 2, 2)

    def _calculate_yules_k(self) -> float:
        """
        Yule's K Characteristic
        Measures vocabulary richness independent of text length
        K = 10^4 * (M2 - M1) / (M1^2)
        where M1 = number of items occurring once, M2 = number occurring twice, etc.
        """
        if self.total_words == 0 or self.unique_words == 0:
            return 0.0

        # Count frequency of frequencies
        freq_of_freq = Counter(self.word_freq.values())

        m1 = self.unique_words  # Number of types
        m2 = sum((i**2) * count for i, count in freq_of_freq.items())

        if m1 == 0:
            return 0.0

        k = (10**4) * (m2 - m1) / (m1**2)
        return round(k, 4)

    def _calculate_yules_i(self) -> float:
        """Yule's I Characteristic (alternative form)"""
        k = self._calculate_yules_k()
        return round(k / 100, 4)

    def _calculate_sichels_s(self) -> float:
        """
        Sichel's S Parameter
        S = V(2) / V where V(2) is number of types occurring twice
        """
        if self.unique_words == 0:
            return 0.0

        dis_legomena = sum(1 for count in self.word_freq.values() if count == 2)
        return round(dis_legomena / self.unique_words, 4)

    def _calculate_herdans_c(self) -> float:
        """
        Herdan's C Constant
        C = log(V) / log(N) where V = vocabulary size, N = total words
        """
        if self.total_words <= 1 or self.unique_words <= 1:
            return 0.0

        c = math.log(self.unique_words) / math.log(self.total_words)
        return round(c, 4)

    def _calculate_kuraszkiewicz_w(self) -> float:
        """
        Kuraszkiewicz's W Coefficient
        W = V / (2 * sqrt(H)) where H = hapax legomena
        """
        hapax = sum(1 for count in self.word_freq.values() if count == 1)
        if hapax == 0:
            return 0.0

        w = self.unique_words / (2 * math.sqrt(hapax))
        return round(w, 4)

    def _calculate_honores_r(self) -> float:
        """
        Honoré's R Statistic
        R = 100 * (V - H) / (N - H) where V = vocabulary, H = hapax, N = total
        """
        hapax = sum(1 for count in self.word_freq.values() if count == 1)
        denominator = self.total_words - hapax

        if denominator == 0:
            return 0.0

        r = 100 * (self.unique_words - hapax) / denominator
        return round(r, 4)

    def _calculate_somers_measure(self) -> float:
        """Somers' Measure of lexical richness"""
        if self.total_words == 0:
            return 0.0
        return round(math.log(self.unique_words) / math.log(self.total_words), 4)

    def _calculate_lexical_density(self) -> float:
        """
        Lexical Density: |T_lex| / |T|
        Content words: nouns, verbs, adjectives, adverbs
        """
        if self.total_words == 0:
            return 0.0

        try:
            if not hasattr(self, "_nlp"):
                try:
                    self._nlp = spacy.load("en_core_web_trf")
                except Exception:
                    self._nlp = spacy.load("en_core_web_sm")
            doc = self._nlp(self.original_text)
            content_pos = {"NOUN", "VERB", "ADJ", "ADV"}
            lexical_tokens = [t for t in doc if t.is_alpha]
            if not lexical_tokens:
                return 0.0
            content_words = sum(1 for t in lexical_tokens if t.pos_ in content_pos)
            return round(content_words / len(lexical_tokens), 4)
        except Exception:
            return 0.0

    def _calculate_lexical_density_percent(self) -> float:
        """Lexical Density percent: (content words / total words) * 100"""
        if self.total_words == 0:
            return 0.0
        ratio = self._calculate_lexical_density()
        return round(ratio * 100, 2)

    def _calculate_content_word_ratio(self) -> float:
        """Ratio of content words to function words"""
        if self.total_words == 0:
            return 0.0

        try:
            if not hasattr(self, "_nlp"):
                try:
                    self._nlp = spacy.load("en_core_web_trf")
                except Exception:
                    self._nlp = spacy.load("en_core_web_sm")
            doc = self._nlp(self.original_text)
            function_pos = {"DET", "ADP", "CCONJ", "SCONJ", "AUX", "PRON", "PART"}
            function_count = sum(1 for t in doc if t.pos_ in function_pos)
            content_pos = {"NOUN", "VERB", "ADJ", "ADV"}
            content_count = sum(1 for t in doc if t.pos_ in content_pos)
            if function_count == 0:
                return round(float(content_count), 4)
            return round(content_count / function_count, 4)
        except Exception:
            return 0.0

    def _calculate_spache(self) -> float:
        """Spache Readability Formula (for grades 1-3)"""
        if len(self.sentences) == 0 or self.total_words == 0:
            return 0.0

        # Use real difficult-word ratio from textstat instead of a static placeholder.
        avg_sentence_length = self.total_words / len(self.sentences)
        difficult_word_count = textstat.difficult_words(self.original_text)
        percentage_difficult_words = (difficult_word_count / self.total_words) * 100

        score = (
            (0.121 * avg_sentence_length) + (0.082 * percentage_difficult_words) + 0.659
        )
        return round(score, 2)

    def _calculate_raygor(self) -> Dict[str, Any]:
        """Raygor Readability Estimate"""
        if len(self.sentences) == 0:
            return {"grade": 0, "avg_sentence_length": 0, "avg_syllables_per_100": 0}

        avg_sentence_length = self.total_words / len(self.sentences)

        total_syllables = sum(self._get_syllables_per_word(w) for w in self.words)
        avg_syllables_per_100 = (total_syllables / self.total_words) * 100 if self.total_words else 0

        # Estimate grade level
        grade = round((avg_sentence_length * 0.1) + (avg_syllables_per_100 * 0.01), 1)

        return {
            "grade": grade,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_syllables_per_100": round(avg_syllables_per_100, 2),
        }

    def _calculate_fry(self) -> Dict[str, Any]:
        """Fry Readability Graph"""
        if len(self.sentences) == 0:
            return {"grade": 0}

        total_syllables = sum(self._get_syllables_per_word(w) for w in self.words)
        avg_syllables = (total_syllables / self.total_words) * 100 if self.total_words else 0
        avg_sentences = (len(self.sentences) / self.total_words) * 100 if self.total_words else 0

        # Fry graph estimation
        grade = round((avg_syllables / 10) + (avg_sentences * 0.5), 1)

        return {"grade": grade}

    def _calculate_forcast(self) -> float:
        """FORCAST Readability Formula (for technical documents)"""
        if self.total_words == 0:
            return 0.0
        monosyllabic = sum(1 for w in self.words if self._get_syllables_per_word(w) == 1)
        grade = 20 - ((monosyllabic / self.total_words) * 100 / 10)
        return round(max(0, min(18, grade)), 1)

    def _calculate_powers_sumner_kearl(self) -> float:
        """Powers-Sumner-Kearl Readability Formula"""
        if len(self.sentences) == 0 or self.total_words == 0:
            return 0.0

        avg_sentence_length = self.total_words / len(self.sentences)
        avg_word_length = sum(len(w) for w in self.words) / self.total_words

        score = (0.942 * avg_word_length) + (0.036 * avg_sentence_length) - 3.456
        return round(max(0, score), 2)

    def _calculate_danielson_bryan(self) -> float:
        """Danielson-Bryan Readability Formula"""
        if len(self.sentences) == 0:
            return 0.0

        avg_sentence_length = self.total_words / len(self.sentences)
        percentage_long_words = (
            sum(1 for w in self.words if len(w) > 6) / self.total_words * 100
        )

        score = (
            (0.1528 * avg_sentence_length) + (0.1053 * percentage_long_words) + 1.9759
        )
        return round(score, 2)

    def _calculate_wheeler_smith(self) -> float:
        """Wheeler-Smith Readability Formula"""
        if self.total_words == 0:
            return 0.0

        avg_word_length = sum(len(w) for w in self.words) / self.total_words
        percentage_prepositions = 0.0
        try:
            if not hasattr(self, "_nlp"):
                try:
                    self._nlp = spacy.load("en_core_web_trf")
                except Exception:
                    self._nlp = spacy.load("en_core_web_sm")
            doc = self._nlp(self.original_text)
            tokens = [t for t in doc if t.is_alpha]
            if tokens:
                prep_count = sum(1 for t in tokens if t.pos_ == "ADP")
                percentage_prepositions = (prep_count / len(tokens)) * 100.0
        except Exception:
            percentage_prepositions = 0.0

        score = (2.5 * avg_word_length) - (1.5 * percentage_prepositions)
        return round(score, 2)

    def _calculate_average_grade_level(self) -> float:
        """Calculate average grade level across all formulas"""
        grades = [
            textstat.flesch_kincaid_grade(self.original_text)
            if self.original_text
            else 0,
            textstat.gunning_fog(self.original_text) if self.original_text else 0,
            textstat.smog_index(self.original_text) if self.original_text else 0,
            textstat.automated_readability_index(self.original_text)
            if self.original_text
            else 0,
            textstat.coleman_liau_index(self.original_text)
            if self.original_text
            else 0,
        ]

        valid_grades = [g for g in grades if g > 0]
        return round(sum(valid_grades) / len(valid_grades), 1) if valid_grades else 0.0

    # ==================== ADVANCED METRICS ====================

    def _calculate_repeated_word_ratio(self) -> float:
        """Ratio of repeated words to total words"""
        if self.total_words == 0:
            return 0.0

        repeated = sum(count for word, count in self.word_freq.items() if count > 1)
        return round(repeated / self.total_words, 4)

    def _calculate_vocabulary_richness(self) -> float:
        """Vocabulary richness score (0-1)"""
        if self.total_words == 0:
            return 0.0

        # Combine multiple metrics
        ttr = self._calculate_ttr()
        mtld = min(self._calculate_mtld() / 100, 1.0)  # Normalize
        hapax_ratio = (
            sum(1 for c in self.word_freq.values() if c == 1) / self.unique_words
            if self.unique_words > 0
            else 0
        )

        richness = (ttr * 0.4) + (mtld * 0.4) + (hapax_ratio * 0.2)
        return round(richness, 4)

    def _calculate_information_density(self) -> float:
        """Information density: unique concepts per word"""
        if self.total_words == 0:
            return 0.0

        # Simplified: ratio of content words to total
        content_ratio = self._calculate_content_word_ratio()
        lexical_diversity = self._calculate_ttr()

        density = (content_ratio * 0.6) + (lexical_diversity * 0.4)
        return round(density, 4)

    # ==================== INFORMATION THEORY METRICS ====================
    # ✅ NEW: Perplexity, Entropy, Semantic Novelty

    def _calculate_perplexity(self) -> float:
        """
        Calculate perplexity of text using unigram language model
        Perplexity = 2^H where H is entropy
        Lower perplexity = more predictable text
        Higher perplexity = more surprising/diverse text
        """
        if self.total_words == 0:
            return 0.0

        # Calculate unigram probabilities
        word_probs = {
            word: count / self.total_words for word, count in self.word_freq.items()
        }

        # Calculate cross-entropy
        entropy = 0.0
        for word, count in self.word_freq.items():
            prob = word_probs[word]
            if prob > 0:
                entropy -= (count / self.total_words) * math.log2(prob)

        # Perplexity = 2^entropy
        perplexity = math.pow(2, entropy)

        return round(perplexity, 2)

    def _calculate_entropy(self) -> float:
        """
        Calculate Shannon entropy of word distribution
        H = -Σ p(x) * log2(p(x))
        Higher entropy = more diverse/unpredictable word choice
        """
        if self.total_words == 0:
            return 0.0

        entropy = 0.0
        for word, count in self.word_freq.items():
            prob = count / self.total_words
            if prob > 0:
                entropy -= prob * math.log2(prob)

        return round(entropy, 4)

    def _calculate_character_entropy(self) -> float:
        """Calculate entropy at character level"""
        if not self.original_text:
            return 0.0

        char_freq = Counter(self.original_text.lower())
        total_chars = sum(char_freq.values())

        if total_chars == 0:
            return 0.0

        entropy = 0.0
        for char, count in char_freq.items():
            if char.isalpha():  # Only count letters
                prob = count / total_chars
                if prob > 0:
                    entropy -= prob * math.log2(prob)

        return round(entropy, 4)

    def _calculate_conditional_entropy(self) -> float:
        """
        Calculate conditional entropy H(X|Y) for bigrams
        Measures how predictable next word is given current word
        """
        if len(self.words) < 2:
            return 0.0

        # Count bigrams
        bigrams = Counter(zip(self.words[:-1], self.words[1:]))
        total_bigrams = sum(bigrams.values())

        # Count unigrams (first word of bigram)
        unigrams = Counter(self.words[:-1])

        # Calculate conditional entropy
        conditional_entropy = 0.0
        for (w1, w2), count in bigrams.items():
            p_w1 = unigrams[w1] / len(self.words[:-1])
            p_w2_given_w1 = count / unigrams[w1] if unigrams[w1] > 0 else 0

            if p_w1 > 0 and p_w2_given_w1 > 0:
                conditional_entropy -= p_w1 * p_w2_given_w1 * math.log2(p_w2_given_w1)

        return round(conditional_entropy, 4)
