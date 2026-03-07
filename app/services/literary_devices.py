"""
Literary Devices Analysis Module
Complete implementation of tropes, schemes, imagery, Sanskrit Alankar, and Rasa theory
Based on Ultimate Literary Master System - Dimension 3
"""

import re
import logging
from typing import Dict, List, Tuple, Set, Optional, Any
from collections import Counter
import spacy
from transformers import pipeline
from nltk.corpus import wordnet as wn
from app.config import Settings
from app.services.label_loader import get_labels
from app.services.rule_loader import get_thresholds, get_literary_device_rules
from app.services.iwn_resources import (
    iwn_runtime_supported,
    get_iwn_language_enum,
    silence_pyiwn_info_logs,
)


class LiteraryDevicesAnalyzer:
    """
    Comprehensive literary devices analysis
    Western tropes/schemes + Indian Alankar + Rasa theory
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.text = ""
        self.lines: List[str] = []
        self.words: List[str] = []
        self._nlp = None
        self._zero_shot = None
        self._settings = Settings()
        self._logger = logging.getLogger(__name__)
        self._rules = get_literary_device_rules() or {}

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete literary devices analysis"""
        self.text = text
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]
        # Support for multilingual word extraction (including Devanagari)
        self.words = re.findall(r'[\w]+', text.lower(), re.UNICODE)

        result = {
            "tropes": self._analyze_tropes(),
            "schemes": self._analyze_schemes(),
            "imagery": self._analyze_imagery(),
            "sanskrit_alankar": self._analyze_sanskrit_alankar(),
            "special_devices": self._analyze_special_devices()
        }

        # Add Rasa analysis for Indic languages
        if self.language in ["hi", "gu", "mr", "bn", "sa"]:
            result["rasa_vector"] = self._analyze_rasa()

        return result

    def _ensure_nlp(self) -> Optional[Any]:
        if self._nlp is not None:
            return self._nlp
        try:
            if self.language == "en":
                self._nlp = spacy.load(self._settings.spacy.english_model)
            else:
                self._nlp = spacy.load(self._settings.spacy.multilingual_model)
        except Exception as e:
            self._logger.info(f"spaCy pipeline not initialized for literary devices: {e}")
            self._nlp = None
        return self._nlp

    def _ensure_zero_shot(self):
        if self._zero_shot is not None:
            return self._zero_shot
        try:
            model_name = self._settings.transformer.generalist_zero_shot_model
            self._zero_shot = pipeline("zero-shot-classification", model=model_name, device=-1)
        except Exception as e:
            self._logger.info(f"Zero-shot pipeline not initialized for literary devices: {e}")
            self._zero_shot = None
        return self._zero_shot

    def _zero_shot_labels(self, text: str, labels: List[str], threshold: float = None) -> List[Tuple[str, float]]:
        zs = self._ensure_zero_shot()
        if not zs or not labels:
            return []
        if threshold is None:
            thresholds = get_thresholds()
            threshold = thresholds.get("zero_shot_min_confidence")
            if threshold is None:
                return []
        try:
            out = zs(text, labels)
            results = []
            for label, score in zip(out["labels"], out["scores"]):
                if score >= threshold:
                    results.append((label, float(score)))
            return results
        except Exception:
            return []

    def _detect_zero_shot_device(self, label: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for i, line in enumerate(self.lines):
            scores = self._zero_shot_labels(line, [label])
            if scores:
                results.append({
                    "line": line,
                    "line_number": i + 1,
                    "score": scores[0][1],
                    "type": label
                })
        if limit is None:
            top_k = self._rules.get("top_k")
            return results[: int(top_k)] if top_k is not None else results
        return results[:limit]

    # ==================== TROPES (Figures of Thought) ====================

    def _analyze_tropes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze tropes (figures of thought)"""
        return {
            "metaphor": self._detect_metaphor(),
            "simile": self._detect_simile(),
            "personification": self._detect_personification(),
            "metonymy": self._detect_metonymy(),
            "synecdoche": self._detect_synecdoche(),
            "hyperbole": self._detect_hyperbole(),
            "litotes": self._detect_litotes(),
            "irony": self._detect_irony(),
            "oxymoron": self._detect_oxymoron(),
            "paradox": self._detect_paradox(),
            "apostrophe": self._detect_apostrophe(),
            "synesthesia": self._detect_synesthesia(),
            "euphemism": self._detect_euphemism()
        }

    def _detect_metaphor(self) -> List[Dict[str, Any]]:
        """Detect metaphors"""
        metaphors: List[Dict[str, Any]] = []
        nlp = self._ensure_nlp()
        if nlp:
            for i, line in enumerate(self.lines):
                doc = nlp(line)
                for sent in doc.sents:
                    root = sent.root
                    if root.lemma_ == "be":
                        subj = next((t for t in sent if t.dep_ in {"nsubj", "nsubjpass"}), None)
                        attr = next((t for t in sent if t.dep_ in {"attr", "oprd"}), None)
                        if subj is not None and attr is not None:
                            if subj.has_vector and attr.has_vector:
                                sim = subj.similarity(attr)
                                sim_threshold = self._rules.get("embedding_similarity_threshold")
                                if sim_threshold is not None and sim < float(sim_threshold):
                                    metaphors.append({
                                        "line": line,
                                        "line_number": i + 1,
                                        "text": f"{subj.text} {root.text} {attr.text}",
                                        "similarity": round(sim, 3),
                                        "type": "metaphor"
                                    })
        if not metaphors:
            for i, line in enumerate(self.lines):
                labels = get_labels("literary_metaphor")
                if not labels:
                    continue
                scores = self._zero_shot_labels(line, labels)
                if scores:
                    metaphors.append({
                        "line": line,
                        "line_number": i + 1,
                        "score": scores[0][1],
                        "type": "metaphor"
                    })
        top_k = self._rules.get("top_k")
        return metaphors[: int(top_k)] if top_k is not None else metaphors

    def _detect_simile(self) -> List[Dict[str, Any]]:
        """Detect similes"""
        similes = []
        for i, line in enumerate(self.lines):
            labels = get_labels("literary_simile")
            if not labels:
                continue
            scores = self._zero_shot_labels(line, labels)
            if scores:
                similes.append({
                    "line": line,
                    "line_number": i + 1,
                    "score": scores[0][1],
                    "type": "simile"
                })
        top_k = self._rules.get("top_k")
        return similes[: int(top_k)] if top_k is not None else similes

    def _detect_personification(self) -> List[Dict[str, Any]]:
        """Detect personification"""
        personifications = []
        nlp = self._ensure_nlp()
        if not nlp:
            return personifications

        human_verb_lexnames = set(self._rules.get("personification_verb_lexnames", []))

        for i, line in enumerate(self.lines):
            doc = nlp(line)
            for sent in doc.sents:
                for token in sent:
                    if token.pos_ != "VERB":
                        continue
                    lexnames = {s.lexname() for s in wn.synsets(token.lemma_, pos=wn.VERB)}
                    if not (lexnames & human_verb_lexnames):
                        continue
                    subj = next((t for t in sent if t.dep_ in {"nsubj", "nsubjpass"}), None)
                    if not subj:
                        continue
                    noun_syns = wn.synsets(subj.lemma_, pos=wn.NOUN)
                    is_person = any(s.lexname() == "noun.person" for s in noun_syns)
                    if not is_person:
                        personifications.append({
                            "line": line,
                            "line_number": i + 1,
                            "subject": subj.text,
                            "verb": token.text,
                            "type": "personification"
                        })
        top_k = self._rules.get("top_k")
        return personifications[: int(top_k)] if top_k is not None else personifications

    def _detect_metonymy(self) -> List[Dict[str, Any]]:
        """Detect metonymy (substitution of associated term)"""
        return self._detect_zero_shot_device("metonymy")

    def _detect_synecdoche(self) -> List[Dict[str, Any]]:
        """Detect synecdoche (part for whole or whole for part)"""
        synecdoches = []
        for i, line in enumerate(self.lines):
            tokens = re.findall(r"[A-Za-z']+", line.lower())
            for word in tokens:
                synsets = wn.synsets(word, pos=wn.NOUN)
                for syn in synsets:
                    holos = syn.member_holonyms() + syn.part_holonyms() + syn.substance_holonyms()
                    meros = syn.member_meronyms() + syn.part_meronyms() + syn.substance_meronyms()
                    if holos or meros:
                        synecdoches.append({
                            "line": line,
                            "line_number": i + 1,
                            "word": word,
                            "holonyms": [h.name().split('.')[0] for h in holos][: int(self._rules.get("holonym_top_k"))] if self._rules.get("holonym_top_k") is not None else [h.name().split('.')[0] for h in holos],
                            "meronyms": [m.name().split('.')[0] for m in meros][: int(self._rules.get("meronym_top_k"))] if self._rules.get("meronym_top_k") is not None else [m.name().split('.')[0] for m in meros],
                            "type": "synecdoche"
                        })
                        break
        top_k = self._rules.get("top_k")
        return synecdoches[: int(top_k)] if top_k is not None else synecdoches

    def _detect_hyperbole(self) -> List[Dict[str, Any]]:
        """Detect hyperbole (exaggeration)"""
        return self._detect_zero_shot_device("hyperbole")

    def _detect_litotes(self) -> List[Dict[str, Any]]:
        """Detect litotes (understatement using negation)"""
        litotes = []
        nlp = self._ensure_nlp()
        if not nlp:
            return self._detect_zero_shot_device("litotes")

        def antonyms(word: str) -> Set[str]:
            ants = set()
            for syn in wn.synsets(word):
                for lemma in syn.lemmas():
                    for ant in lemma.antonyms():
                        ants.add(ant.name().replace("_", " "))
            return ants

        for i, line in enumerate(self.lines):
            doc = nlp(line)
            for token in doc:
                if token.dep_ == "neg" and token.head is not None:
                    head = token.head
                    ant = antonyms(head.lemma_.lower())
                    if ant:
                        litotes.append({
                            "line": line,
                            "line_number": i + 1,
                            "negated_head": head.text,
                            "antonyms": list(ant)[: int(self._rules.get("antonym_top_k"))] if self._rules.get("antonym_top_k") is not None else list(ant),
                            "type": "litotes"
                        })
                        break
        if not litotes:
            return self._detect_zero_shot_device("litotes")
        top_k = self._rules.get("top_k")
        return litotes[: int(top_k)] if top_k is not None else litotes

    def _detect_irony(self) -> List[Dict[str, Any]]:
        """Detect irony markers"""
        return self._detect_zero_shot_device("irony")

    def _detect_oxymoron(self) -> List[Dict[str, Any]]:
        """Detect oxymoron (contradictory terms)"""
        return self._detect_zero_shot_device("oxymoron")

    def _detect_paradox(self) -> List[Dict[str, Any]]:
        """Detect paradox (seemingly contradictory truth)"""
        return self._detect_zero_shot_device("paradox")

    def _detect_apostrophe(self) -> List[Dict[str, Any]]:
        """Detect apostrophe (addressing absent/abstract entities)"""
        apostrophes = []
        nlp = self._ensure_nlp()
        if not nlp:
            return self._detect_zero_shot_device("apostrophe")

        for i, line in enumerate(self.lines):
            doc = nlp(line)
            for sent in doc.sents:
                vocative = any(t.dep_ == "vocative" for t in sent)
                starts_intj = len(sent) > 1 and sent[0].pos_ == "INTJ" and sent[1].pos_ in {"PROPN", "NOUN"}
                if vocative or starts_intj:
                    apostrophes.append({
                        "line": line,
                        "line_number": i + 1,
                        "type": "apostrophe"
                    })
                    break

        if not apostrophes:
            return self._detect_zero_shot_device("apostrophe")
        top_k = self._rules.get("top_k")
        return apostrophes[: int(top_k)] if top_k is not None else apostrophes

    def _detect_synesthesia(self) -> List[Dict[str, Any]]:
        """Detect synesthesia (mixing senses)"""
        return self._detect_zero_shot_device("synesthesia")

    def _detect_euphemism(self) -> List[Dict[str, Any]]:
        """Detect euphemisms"""
        return self._detect_zero_shot_device("euphemism")

    # ==================== SCHEMES (Figures of Sound/Structure) ====================

    def _analyze_schemes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze schemes (figures of sound and structure)"""
        return {
            "alliteration": self._detect_alliteration_scheme(),
            "anaphora": self._detect_anaphora(),
            "epistrophe": self._detect_epistrophe(),
            "parallelism": self._detect_parallelism(),
            "antithesis": self._detect_antithesis(),
            "chiasmus": self._detect_chiasmus(),
            "zeugma": self._detect_zeugma(),
            "asyndeton": self._detect_asyndeton(),
            "polysyndeton": self._detect_polysyndeton(),
            "symploce": self._detect_symploce(),
            "anadiplosis": self._detect_anadiplosis(),
            "climax": self._detect_climax(),
            "antimetabole": self._detect_antimetabole(),
            "isocolon": self._detect_isocolon(),
            "ellipsis": self._detect_ellipsis()
        }

    def _detect_alliteration_scheme(self) -> List[Dict[str, Any]]:
        """Detect alliteration"""
        alliterations = []

        for i, line in enumerate(self.lines):
            words = line.split()
            if len(words) >= 2:
                first_letters = [w[0].lower() for w in words if w and w[0].isalpha()]
                for j in range(len(first_letters) - 1):
                    consonants = self._rules.get("alliteration_consonants")
                    if consonants is None:
                        continue
                    if first_letters[j] == first_letters[j+1] and first_letters[j] in consonants:
                        alliterations.append({
                            "line": line,
                            "line_number": i + 1,
                            "letter": first_letters[j],
                            "words": [words[j], words[j+1]],
                            "type": "alliteration"
                        })

        top_k = self._rules.get("top_k")
        return alliterations[: int(top_k)] if top_k is not None else alliterations

    def _detect_anaphora(self) -> List[Dict[str, Any]]:
        """Detect anaphora (repetition at beginning)"""
        anaphoras = []

        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].lower().split()
            words2 = self.lines[i+1].lower().split()

            min_len = self._rules.get("min_word_length")
            if min_len is None:
                continue
            if words1 and words2 and words1[0] == words2[0] and len(words1[0]) >= int(min_len):
                anaphoras.append({
                    "lines": f"{i+1}-{i+2}",
                    "repeated_word": words1[0],
                    "type": "anaphora"
                })

        top_k = self._rules.get("top_k")
        return anaphoras[: int(top_k)] if top_k is not None else anaphoras

    def _detect_epistrophe(self) -> List[Dict[str, Any]]:
        """Detect epistrophe (repetition at end)"""
        epistrophes = []

        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].lower().split()
            words2 = self.lines[i+1].lower().split()

            min_len = self._rules.get("min_word_length")
            if min_len is None:
                continue
            if words1 and words2 and words1[-1] == words2[-1] and len(words1[-1]) >= int(min_len):
                epistrophes.append({
                    "lines": f"{i+1}-{i+2}",
                    "repeated_word": words1[-1],
                    "type": "epistrophe"
                })

        top_k = self._rules.get("top_k")
        return epistrophes[: int(top_k)] if top_k is not None else epistrophes

    def _detect_parallelism(self) -> List[Dict[str, Any]]:
        """Detect parallelism (similar structure)"""
        parallelisms = []

        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].split()
            words2 = self.lines[i+1].split()

            min_words = self._rules.get("min_words_per_line")
            if min_words is None:
                continue
            if len(words1) == len(words2) and len(words1) >= int(min_words):
                parallelisms.append({
                    "lines": f"{i+1}-{i+2}",
                    "structure": "parallel",
                    "word_count": len(words1),
                    "type": "parallelism"
                })

        top_k = self._rules.get("top_k")
        return parallelisms[: int(top_k)] if top_k is not None else parallelisms

    def _detect_antithesis(self) -> List[Dict[str, Any]]:
        """Detect antithesis (contrasting ideas in parallel)"""
        antitheses = []
        nlp = self._ensure_nlp()
        if not nlp:
            return self._detect_zero_shot_device("antithesis")

        for i, line in enumerate(self.lines):
            doc = nlp(line)
            lemmas = {t.lemma_.lower() for t in doc if t.is_alpha}
            pairs = []
            for lemma in lemmas:
                for syn in wn.synsets(lemma):
                    for l in syn.lemmas():
                        for ant in l.antonyms():
                            ant_lemma = ant.name().replace("_", " ")
                            if ant_lemma in lemmas:
                                pairs.append((lemma, ant_lemma))
            if pairs:
                pair_limit = self._rules.get("antithesis_pair_limit")
                antitheses.append({
                    "line": line,
                    "line_number": i + 1,
                    "pairs": pairs[: int(pair_limit)] if pair_limit is not None else pairs,
                    "type": "antithesis"
                })

        if not antitheses:
            return self._detect_zero_shot_device("antithesis")
        top_k = self._rules.get("top_k")
        return antitheses[: int(top_k)] if top_k is not None else antitheses

    def _detect_chiasmus(self) -> List[Dict[str, Any]]:
        """Detect chiasmus (ABBA structure)"""
        chiasmi = []
        nlp = self._ensure_nlp()
        if not nlp:
            return self._detect_zero_shot_device("chiasmus")

        for i, line in enumerate(self.lines):
            doc = nlp(line)
            seq = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]
            window = int(self._rules.get("chiasmus_window", 4))
            min_len = self._rules.get("min_word_length")
            for j in range(len(seq) - (window - 1)):
                chunk = seq[j:j + window]
                if len(chunk) != window:
                    continue
                a, b, c, d = chunk[:4]
                if min_len is None:
                    continue
                if a == d and b == c and len(a) >= int(min_len) and len(b) >= int(min_len):
                    chiasmi.append({
                        "line": line,
                        "line_number": i + 1,
                        "pattern": f"{a} {b} ... {c} {d}",
                        "type": "chiasmus"
                    })
                    break
        if not chiasmi:
            return self._detect_zero_shot_device("chiasmus")
        top_k = self._rules.get("top_k")
        return chiasmi[: int(top_k)] if top_k is not None else chiasmi

    def _detect_zeugma(self) -> List[Dict[str, Any]]:
        """Detect zeugma (one word governing multiple)"""
        zeugmas = []
        nlp = self._ensure_nlp()
        if not nlp:
            return self._detect_zero_shot_device("zeugma")

        for i, line in enumerate(self.lines):
            doc = nlp(line)
            for token in doc:
                if token.pos_ != "VERB":
                    continue
                objects = [c for c in token.children if c.dep_ in {"dobj", "obj", "iobj", "pobj"}]
                min_objs = self._rules.get("zeugma_min_objects")
                if min_objs is None:
                    continue
                if len(objects) >= int(min_objs):
                    zeugmas.append({
                        "line": line,
                        "line_number": i + 1,
                        "governing_word": token.text,
                        "objects": [o.text for o in objects[: int(self._rules.get("zeugma_max_objects", 3))]],
                        "type": "zeugma"
                    })
                    break
        if not zeugmas:
            return self._detect_zero_shot_device("zeugma")
        top_k = self._rules.get("top_k")
        return zeugmas[: int(top_k)] if top_k is not None else zeugmas

    def _detect_asyndeton(self) -> List[Dict[str, Any]]:
        """Detect asyndeton (omission of conjunctions)"""
        asyndetons = []
        # Look for lists without conjunctions
        for i, line in enumerate(self.lines):
            words = line.split()
            min_words = self._rules.get("asyndeton_min_words")
            min_commas = self._rules.get("asyndeton_min_commas")
            if min_words is None or min_commas is None:
                continue
            if len(words) >= int(min_words) and "and" not in line.lower() and "or" not in line.lower():
                if line.count(",") >= int(min_commas):
                    asyndetons.append({
                        "line": line,
                        "line_number": i + 1,
                        "type": "asyndeton"
                    })

        top_k = self._rules.get("top_k")
        return asyndetons[: int(top_k)] if top_k is not None else asyndetons

    def _detect_polysyndeton(self) -> List[Dict[str, Any]]:
        """Detect polysyndeton (excessive conjunctions)"""
        polysyndetons = []

        for i, line in enumerate(self.lines):
            and_count = line.lower().count(" and ")
            min_and = self._rules.get("polysyndeton_min_and")
            if min_and is None:
                continue
            if and_count >= int(min_and):
                polysyndetons.append({
                    "line": line,
                    "line_number": i + 1,
                    "conjunction_count": and_count,
                    "type": "polysyndeton"
                })

        top_k = self._rules.get("top_k")
        return polysyndetons[: int(top_k)] if top_k is not None else polysyndetons

    def _detect_symploce(self) -> List[Dict[str, Any]]:
        """Detect symploce (anaphora + epistrophe)"""
        symploces = []
        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].lower().split()
            words2 = self.lines[i+1].lower().split()
            min_words = self._rules.get("min_words_per_line")
            if min_words is None:
                continue
            if len(words1) >= int(min_words) and len(words2) >= int(min_words):
                if words1[0] == words2[0] and words1[-1] == words2[-1]:
                    symploces.append({
                        "lines": f"{i+1}-{i+2}",
                        "repeated_start": words1[0],
                        "repeated_end": words1[-1],
                        "type": "symploce"
                    })
        top_k = self._rules.get("top_k")
        return symploces[: int(top_k)] if top_k is not None else symploces

    def _detect_anadiplosis(self) -> List[Dict[str, Any]]:
        """Detect anadiplosis (repetition of end of line at start of next)"""
        anadiplosis = []
        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].lower().split()
            words2 = self.lines[i+1].lower().split()
            min_len = self._rules.get("min_word_length")
            if min_len is None:
                continue
            if words1 and words2 and words1[-1] == words2[0] and len(words1[-1]) >= int(min_len):
                anadiplosis.append({
                    "lines": f"{i+1}-{i+2}",
                    "repeated_word": words1[-1],
                    "type": "anadiplosis"
                })
        top_k = self._rules.get("top_k")
        return anadiplosis[: int(top_k)] if top_k is not None else anadiplosis

    def _detect_climax(self) -> List[Dict[str, Any]]:
        """Detect climax (words in increasing order of importance/intensity)"""
        climaxes = []
        try:
            import syllables
        except Exception:
            return self._detect_zero_shot_device("climax")

        for i, line in enumerate(self.lines):
            parts = [p.strip() for p in re.split(r",|;| and | or ", line) if p.strip()]
            min_parts = self._rules.get("climax_min_parts")
            max_parts = self._rules.get("climax_max_parts")
            if min_parts is None or max_parts is None:
                continue
            if len(parts) < int(min_parts):
                continue
            scores = []
            for part in parts[: int(max_parts)]:
                words = re.findall(r"[A-Za-z']+", part.lower())
                if not words:
                    continue
                syl = sum(syllables.syllable(w) for w in words)
                scores.append(syl / max(1, len(words)))
            min_scores = self._rules.get("climax_min_scores")
            if min_scores is None:
                continue
            if len(scores) >= int(min_scores) and all(scores[i] < scores[i+1] for i in range(len(scores)-1)):
                climaxes.append({
                    "line": line,
                    "line_number": i + 1,
                    "intensity_sequence": [round(s, 2) for s in scores[: int(self._rules.get("climax_intensity_top_k"))]] if self._rules.get("climax_intensity_top_k") is not None else [round(s, 2) for s in scores],
                    "type": "climax"
                })
        if not climaxes:
            return self._detect_zero_shot_device("climax")
        top_k = self._rules.get("top_k")
        return climaxes[: int(top_k)] if top_k is not None else climaxes

    def _detect_antimetabole(self) -> List[Dict[str, Any]]:
        """Detect antimetabole (repetition in reverse order)"""
        antimetaboles = []
        window = self._rules.get("antimetabole_window")
        min_len = self._rules.get("min_word_length")
        if window is None or min_len is None:
            return antimetaboles
        window = int(window)
        for i, line in enumerate(self.lines):
            words = line.lower().split()
            if len(words) >= window:
                # Basic check for A B ... B A pattern
                for j in range(len(words) - (window - 1)):
                    if words[j] == words[j+window-1] and words[j+1] == words[j+2] and len(words[j]) >= int(min_len):
                        antimetaboles.append({
                            "line": line,
                            "line_number": i + 1,
                            "pattern": f"{words[j]} {words[j+1]} ... {words[j+2]} {words[j+window-1]}",
                            "type": "antimetabole"
                        })
        top_k = self._rules.get("top_k")
        return antimetaboles[: int(top_k)] if top_k is not None else antimetaboles

    def _detect_isocolon(self) -> List[Dict[str, Any]]:
        """Detect isocolon (parallel structures of same length)"""
        isocolons = []
        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].split()
            words2 = self.lines[i+1].split()
            min_words = self._rules.get("min_words_per_line")
            if min_words is None:
                continue
            if len(words1) == len(words2) and len(words1) >= int(min_words):
                # Checking syllable count matching as a proxy
                try:
                    import syllables
                    syl1 = sum(syllables.syllable(w) for w in words1)
                    syl2 = sum(syllables.syllable(w) for w in words2)
                    if syl1 == syl2:
                        isocolons.append({
                            "lines": f"{i+1}-{i+2}",
                            "structure": "isocolon",
                            "syllable_count": syl1,
                            "type": "isocolon"
                        })
                except:
                    pass
        top_k = self._rules.get("top_k")
        return isocolons[: int(top_k)] if top_k is not None else isocolons

    def _detect_ellipsis(self) -> List[Dict[str, Any]]:
        """Detect ellipsis (omission of words)"""
        ellipses = []
        for i, line in enumerate(self.lines):
            if "..." in line or "…" in line:
                ellipses.append({
                    "line": line,
                    "line_number": i + 1,
                    "type": "ellipsis"
                })
        top_k = self._rules.get("top_k")
        return ellipses[: int(top_k)] if top_k is not None else ellipses

    # ==================== IMAGERY ====================

    def _analyze_imagery(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze sensory imagery"""
        return {
            "visual": self._detect_visual_imagery(),
            "auditory": self._detect_auditory_imagery(),
            "tactile": self._detect_tactile_imagery(),
            "gustatory": self._detect_gustatory_imagery(),
            "olfactory": self._detect_olfactory_imagery(),
            "kinesthetic": self._detect_kinesthetic_imagery(),
            "organic": self._detect_organic_imagery()
        }

    def _detect_visual_imagery(self) -> List[Dict[str, Any]]:
        """Visual imagery (sight)"""
        return self._detect_imagery_by_zero_shot("visual imagery")

    def _detect_auditory_imagery(self) -> List[Dict[str, Any]]:
        """Auditory imagery (sound)"""
        return self._detect_imagery_by_zero_shot("auditory imagery")

    def _detect_tactile_imagery(self) -> List[Dict[str, Any]]:
        """Tactile imagery (touch)"""
        return self._detect_imagery_by_zero_shot("tactile imagery")

    def _detect_gustatory_imagery(self) -> List[Dict[str, Any]]:
        """Gustatory imagery (taste)"""
        return self._detect_imagery_by_zero_shot("gustatory imagery")

    def _detect_olfactory_imagery(self) -> List[Dict[str, Any]]:
        """Olfactory imagery (smell)"""
        return self._detect_imagery_by_zero_shot("olfactory imagery")

    def _detect_kinesthetic_imagery(self) -> List[Dict[str, Any]]:
        """Kinesthetic imagery (movement)"""
        return self._detect_imagery_by_zero_shot("kinesthetic imagery")

    def _detect_organic_imagery(self) -> List[Dict[str, Any]]:
        """Organic imagery (internal sensations)"""
        return self._detect_imagery_by_zero_shot("organic imagery")

    def _detect_imagery_by_zero_shot(self, label: str) -> List[Dict[str, Any]]:
        imagery = []
        for i, line in enumerate(self.lines):
            scores = self._zero_shot_labels(line, [label])
            if scores:
                imagery.append({
                    "line": line,
                    "line_number": i + 1,
                    "score": scores[0][1],
                    "type": label
                })
        top_k = self._rules.get("top_k")
        return imagery[: int(top_k)] if top_k is not None else imagery

    # ==================== SANSKRIT ALANKAR ====================

    def _analyze_sanskrit_alankar(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze Sanskrit/Hindi Alankar (figures of speech)
        Based on classical Indian poetics (Kavyaprakasha, Alamkara Shastra)
        """
        return {
            "yamaka": self._detect_yamaka(),
            "shlesha": self._detect_shlesha(),
            "utpreksha": self._detect_utpreksha(),
            "vibhavana": self._detect_vibhavana(),
            "vishesokti": self._detect_vishesokti(),
            "rupak": self._detect_rupak(),
            "upama": self._detect_upama()
        }

    def _detect_yamaka(self) -> List[Dict[str, Any]]:
        """
        Yamaka: Repetition of same syllables/words with different meanings
        Example: कर कर (doer/hands), हर हर (Shiva/remove)
        """
        yamakas: List[Dict[str, Any]] = []

        def polysemy_count(word: str) -> int:
            if self.language == "en":
                try:
                    from nltk.corpus import wordnet as wn
                    return len(wn.synsets(word))
                except Exception:
                    return 0
            try:
                if not iwn_runtime_supported(self.language):
                    return 0
                from pyiwn import IndoWordNet
                silence_pyiwn_info_logs()
                lang_enum = get_iwn_language_enum(self.language)
                if lang_enum is None:
                    return 0
                iwn = IndoWordNet(lang=lang_enum)
                return len(iwn.synsets(word))
            except Exception:
                return 0

        for i, line in enumerate(self.lines):
            tokens = re.findall(r"[\w\u0900-\u097F\u0600-\u06FF]+", line)
            counts = Counter(tokens)
            for word, count in counts.items():
                if count >= 2 and polysemy_count(word) >= 2:
                    splits = count * (count - 1) // 2
                    yamakas.append({
                        "line": line,
                        "line_number": i + 1,
                        "repeated_word": word,
                        "count": count,
                        "valid_splits": splits,
                        "polysemy": polysemy_count(word),
                        "type": "yamaka"
                    })

        top_k = self._rules.get("yamaka_top_k")
        return yamakas[: int(top_k)] if top_k is not None else yamakas

    def _detect_shlesha(self) -> List[Dict[str, Any]]:
        """
        Shlesha: Pun/double meaning (one word, multiple meanings)
        Example: सारा (entire/essence), रस (juice/essence/emotion)
        """
        shleshas: List[Dict[str, Any]] = []

        if self.language == "en":
            try:
                from nltk.corpus import wordnet as wn
                for i, line in enumerate(self.lines):
                    tokens = re.findall(r"[A-Za-z']+", line.lower())
                    for word in tokens:
                        synsets = wn.synsets(word)
                        if len(synsets) >= 2:
                            meanings = [s.definition() for s in synsets[: int(self._rules.get("shlesha_meaning_top_k"))]] if self._rules.get("shlesha_meaning_top_k") is not None else [s.definition() for s in synsets]
                            shleshas.append({
                                "line": line,
                                "line_number": i + 1,
                                "word": word,
                                "meanings": meanings,
                                "type": "shlesha"
                            })
            except Exception:
                pass
            top_k = self._rules.get("shlesha_top_k")
            return shleshas[: int(top_k)] if top_k is not None else shleshas

        try:
            if not iwn_runtime_supported(self.language):
                top_k = self._rules.get("shlesha_top_k")
                return shleshas[: int(top_k)] if top_k is not None else shleshas
            from pyiwn import IndoWordNet
            silence_pyiwn_info_logs()
            lang_enum = get_iwn_language_enum(self.language)
            if lang_enum is None:
                top_k = self._rules.get("shlesha_top_k")
                return shleshas[: int(top_k)] if top_k is not None else shleshas
            iwn = IndoWordNet(lang=lang_enum)
            for i, line in enumerate(self.lines):
                tokens = re.findall(r"[\w\u0900-\u097F\u0600-\u06FF]+", line)
                for word in tokens:
                    synsets = iwn.synsets(word)
                    if len(synsets) >= 2:
                        meanings = [s.gloss() for s in synsets[: int(self._rules.get("shlesha_meaning_top_k"))] if getattr(s, "gloss", None)] if self._rules.get("shlesha_meaning_top_k") is not None else [s.gloss() for s in synsets if getattr(s, "gloss", None)]
                        shleshas.append({
                            "line": line,
                            "line_number": i + 1,
                            "word": word,
                            "meanings": meanings,
                            "type": "shlesha"
                        })
        except Exception:
            pass

        top_k = self._rules.get("shlesha_top_k")
        return shleshas[: int(top_k)] if top_k is not None else shleshas

    def _detect_utpreksha(self) -> List[Dict[str, Any]]:
        """
        Utpreksha: Imaginative comparison/fanciful identification
        Example: "Her face is the moon"
        """
        return self._detect_zero_shot_device("utpreksha", limit=10)

    def _detect_vibhavana(self) -> List[Dict[str, Any]]:
        """
        Vibhavana: Effect described without cause (or cause without effect)
        Example: "Tears flow" (without saying why)
        """
        return self._detect_zero_shot_device("vibhavana", limit=10)

    def _detect_vishesokti(self) -> List[Dict[str, Any]]:
        """
        Vishesokti: Contradiction of natural sequence
        Example: "Fire burns cold"
        """
        return self._detect_zero_shot_device("vishesokti", limit=10)

    def _detect_rupak(self) -> List[Dict[str, Any]]:
        """
        Rupak: Metaphor (direct identification)
        Example: "She is a goddess"
        """
        return self._detect_zero_shot_device("rupak", limit=10)

    def _detect_upama(self) -> List[Dict[str, Any]]:
        """
        Upama: Simile (comparison using like/as)
        Example: "Fair as a star"
        """
        return self._detect_zero_shot_device("upama", limit=10)

    # ==================== RASA THEORY ====================

    def _analyze_rasa(self) -> Dict[str, Any]:
        """
        Analyze Rasa (aesthetic emotion) based on Navarasa theory
        From Bharata's Natyashastra
        """
        rasa_scores = {k: 0.0 for k in [
            "shringara", "hasya", "karuna", "raudra", "veera",
            "bhayanaka", "bibhatsa", "adbhuta", "shanta"
        ]}

        rasa_labels = {
            "shringara": "shringara (love/beauty)",
            "hasya": "hasya (laughter/comedy)",
            "karuna": "karuna (compassion/sorrow)",
            "raudra": "raudra (fury/anger)",
            "veera": "veera (heroism/courage)",
            "bhayanaka": "bhayanaka (fear/terror)",
            "bibhatsa": "bibhatsa (disgust)",
            "adbhuta": "adbhuta (wonder/awe)",
            "shanta": "shanta (peace/serenity)"
        }

        for line in self.lines:
            scores = self._zero_shot_labels(line, list(rasa_labels.values()), threshold=0.3)
            for label, score in scores:
                for rasa, rasa_label in rasa_labels.items():
                    if label == rasa_label:
                        rasa_scores[rasa] += float(score)

        # Find dominant rasa
        dominant_rasa = max(rasa_scores, key=rasa_scores.get) if any(v > 0 for v in rasa_scores.values()) else None

        # Normalize scores
        total = sum(rasa_scores.values())
        if total > 0:
            rasa_scores = {k: round(v / total, 4) for k, v in rasa_scores.items()}

        # Bhava (emotion) detection
        bhava_detection = {
            "vibhava": self._detect_vibhava(),
            "anubhava": self._detect_anubhava(),
            "vyabhichari_bhava": self._detect_vyabhichari_bhava()
        }

        return {
            "rasa_vector": rasa_scores,
            "dominant_rasa": dominant_rasa,
            "rasa_colors": self._get_rasa_colors(),
            "bhava_analysis": bhava_detection,
            "analysis": "Navarasa analysis based on Bharata's Natyashastra"
        }

    def _detect_vibhava(self) -> List[Dict[str, str]]:
        """Detect Vibhava (determinant/cause of emotion)"""
        vibavas = []
        nlp = self._ensure_nlp()
        if not nlp:
            return vibavas

        for i, line in enumerate(self.lines):
            doc = nlp(line)
            for token in doc:
                if token.pos_ in {"NOUN", "PROPN"}:
                    syns = wn.synsets(token.lemma_, pos=wn.NOUN)
                    lexnames = {s.lexname() for s in syns}
                    if lexnames & {"noun.person", "noun.location", "noun.event", "noun.object", "noun.group"}:
                        vibavas.append({
                            "line_number": i + 1,
                            "stimulus": token.text,
                            "category": next(iter(lexnames)) if lexnames else "entity"
                        })
        top_k = self._rules.get("vibava_top_k")
        return vibavas[: int(top_k)] if top_k is not None else vibavas

    def _detect_anubhava(self) -> List[Dict[str, str]]:
        """Detect Anubhava (consequent/physical reaction)"""
        anubhavas = []
        nlp = self._ensure_nlp()
        if not nlp:
            return anubhavas

        for i, line in enumerate(self.lines):
            doc = nlp(line)
            for token in doc:
                if token.pos_ in {"VERB", "ADJ"}:
                    syns = wn.synsets(token.lemma_, pos=wn.VERB if token.pos_ == "VERB" else wn.ADJ)
                    lexnames = {s.lexname() for s in syns}
                    if lexnames & {"verb.emotion", "verb.body", "verb.perception"} or "adj.feeling" in lexnames:
                        anubhavas.append({
                            "line_number": i + 1,
                            "reaction": token.text,
                            "category": next(iter(lexnames)) if lexnames else "reaction"
                        })
        top_k = self._rules.get("anubhava_top_k")
        return anubhavas[: int(top_k)] if top_k is not None else anubhavas

    def _detect_vyabhichari_bhava(self) -> List[Dict[str, str]]:
        """Detect Vyabhichari Bhava (transitory states)"""
        vyabhichari = []
        nlp = self._ensure_nlp()
        if not nlp:
            return vyabhichari
        for i, line in enumerate(self.lines):
            doc = nlp(line)
            for token in doc:
                if token.pos_ in {"NOUN", "ADJ"}:
                    syns = wn.synsets(token.lemma_, pos=wn.NOUN if token.pos_ == "NOUN" else wn.ADJ)
                    if any(s.lexname() == "noun.feeling" or s.lexname().startswith("adj.") for s in syns):
                        vyabhichari.append({"line_number": i + 1, "state": token.text})
        top_k = self._rules.get("vyabhichari_top_k")
        return vyabhichari[: int(top_k)] if top_k is not None else vyabhichari

    def _calculate_rasa_score(self, text: str, word_list: List[str]) -> float:
        """Calculate score for a specific rasa"""
        return 0.0

    def _get_rasa_colors(self) -> Dict[str, str]:
        """Get traditional colors associated with each rasa"""
        return {
            "shringara": "light_green",
            "hasya": "white",
            "karuna": "grey",
            "raudra": "red",
            "veera": "orange",
            "bhayanaka": "black",
            "bibhatsa": "blue",
            "adbhuta": "yellow",
            "shanta": "white_blue"
        }

    # ==================== SPECIAL DEVICES ====================

    def _analyze_special_devices(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze special literary devices"""
        return {
            "foreshadowing": self._detect_foreshadowing(),
            "symbolism": self._detect_symbolism(),
            "allusion": self._detect_allusion(),
            "motif": self._detect_motif()
        }

    def _detect_foreshadowing(self) -> List[Dict[str, Any]]:
        """Detect foreshadowing"""
        return self._detect_zero_shot_device("foreshadowing")

    def _detect_symbolism(self) -> List[Dict[str, Any]]:
        """Detect symbolism"""
        return self._detect_symbol()

    def _detect_symbol(self) -> List[Dict[str, Any]]:
        """Detect symbols"""
        return self._detect_zero_shot_device("symbolism")

    def _detect_allusion(self) -> List[Dict[str, Any]]:
        """Detect allusion (reference to other works/events)"""
        return self._detect_zero_shot_device("allusion")

    def _detect_motif(self) -> List[Dict[str, Any]]:
        """Detect recurring motifs"""
        motifs = []
        word_freq = Counter(self.words)

        # Find words that appear multiple times
        min_count = self._rules.get("motif_min_count")
        min_len = self._rules.get("motif_min_length")
        if min_count is None or min_len is None:
            return motifs
        recurring = [
            (word, count)
            for word, count in word_freq.items()
            if count >= int(min_count) and len(word) >= int(min_len)
        ]

        motif_top_k = self._rules.get("motif_top_k")
        line_top_k = self._rules.get("motif_line_top_k")
        for word, count in recurring[: int(motif_top_k)] if motif_top_k is not None else recurring:
            lines_with_word = [i+1 for i, line in enumerate(self.lines) if word in line.lower()]
            motifs.append({
                "word": word,
                "occurrences": count,
                "line_numbers": lines_with_word[: int(line_top_k)] if line_top_k is not None else lines_with_word,
                "type": "motif"
            })

        return motifs


def analyze_idioms_and_proverbs(text: str) -> Dict[str, List[str]]:
    """Detect idioms and proverbs"""
    analyzer = LiteraryDevicesAnalyzer()
    analyzer.text = text
    analyzer.lines = [l.strip() for l in text.split("\n") if l.strip()]

    idioms = []
    proverbs = []
    for i, line in enumerate(analyzer.lines):
        idiom_labels = get_labels("idiom")
        proverb_labels = get_labels("proverb")
        if not idiom_labels or not proverb_labels:
            return result
        idiom_scores = analyzer._zero_shot_labels(line, idiom_labels)
        proverb_scores = analyzer._zero_shot_labels(line, proverb_labels)
        if idiom_scores:
            idioms.append(line)
        if proverb_scores:
            proverbs.append(line)

    rules = analyzer._rules or {}
    top_k = rules.get("idiom_proverb_top_k")
    return {
        "idioms": idioms[: int(top_k)] if top_k is not None else idioms,
        "proverbs": proverbs[: int(top_k)] if top_k is not None else proverbs,
    }
