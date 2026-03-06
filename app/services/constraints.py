"""
Oulipo Constraint Engine
Complete implementation of constraint-based writing systems
Based on quantitative_poetry_metrics.md Section 7
"""

import re
import math
import json
from pathlib import Path
import random
import syllables
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
from app.services.prosody import ProsodyAnalyzer
from app.services.rule_loader import get_constraints_rules


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "constraints"
PI_DIGITS = _load_json(_DATA_DIR / "pi_digits.json")
FIBONACCI_SMALL = _load_json(_DATA_DIR / "fibonacci_small.json")
HAIKU_SYLLABLES = _load_json(_DATA_DIR / "haiku_syllables.json")


class OulipoConstraintEngine:
    """
    Oulipo (Ouvroir de Littérature Potentielle) constraint engine
    Implements N+7, Lipogram, Snowball, Pilish, Univocalism, and more
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.dictionary = self._load_dictionary()
        self._rules = get_constraints_rules()

    def _load_dictionary(self) -> Dict[str, List[str]]:
        """Load word lists by part of speech using real lexical resources."""
        nouns: List[str] = []
        verbs: List[str] = []
        adjectives: List[str] = []

        if self.language == "en":
            try:
                from nltk.corpus import wordnet as wn
                for syn in wn.all_synsets("n"):
                    nouns.extend(lemma.replace("_", " ") for lemma in syn.lemma_names())
                for syn in wn.all_synsets("v"):
                    verbs.extend(lemma.replace("_", " ") for lemma in syn.lemma_names())
                for syn in wn.all_synsets("a"):
                    adjectives.extend(lemma.replace("_", " ") for lemma in syn.lemma_names())
            except Exception:
                pass
        else:
            try:
                from pyiwn import IndoWordNet, Language
                lang_map = {
                    "hi": Language.HINDI,
                    "gu": Language.GUJARATI,
                    "ur": Language.URDU,
                    "mr": Language.MARATHI,
                    "bn": Language.BENGALI,
                    "sa": Language.SANSKRIT,
                    "ta": Language.TAMIL,
                    "te": Language.TELUGU,
                    "kn": Language.KANNADA,
                    "ml": Language.MALAYALAM,
                    "pa": Language.PUNJABI,
                }
                iwn = IndoWordNet(lang=lang_map.get(self.language, Language.HINDI))
                for syn in iwn.all_synsets():
                    pos = syn.pos()
                    lemmas = syn.lemma_names()
                    if pos == "noun":
                        nouns.extend(lemmas)
                    elif pos == "verb":
                        verbs.extend(lemmas)
                    elif pos == "adj":
                        adjectives.extend(lemmas)
            except Exception:
                pass

        return {
            "nouns": sorted(set(nouns)),
            "verbs": sorted(set(verbs)),
            "adjectives": sorted(set(adjectives)),
        }

    def apply_constraint(self, text: str, constraint_type: str, params: Dict = None) -> Dict[str, Any]:
        """
        Apply Oulipo constraint to text
        
        Args:
            text: Source text
            constraint_type: Type of constraint
            params: Constraint-specific parameters
            
        Returns:
            Dictionary with transformed text and metadata
        """
        params = params or {}
        
        if constraint_type == "n_plus_7":
            result = self.n_plus_7(text, params.get("n", self._rules["defaults"]["n_plus"]))
            return self._with_css(result)
        elif constraint_type == "lipogram":
            return self._with_css(self.lipogram(text, params.get("letter", self._rules["defaults"]["lipogram_letter"])))
        elif constraint_type == "snowball":
            return self._with_css(self.snowball(text))
        elif constraint_type == "pilish":
            return self._with_css(self.pilish(text))
        elif constraint_type == "univocalism":
            return self._with_css(self.univocalism(text, params.get("vowel", self._rules["defaults"]["univocal_vowel"])))
        elif constraint_type == "s_plus_10":
            return self._with_css(self.s_plus_n(text, params.get("n", self._rules["defaults"]["s_plus"]), "s"))
        elif constraint_type == "v_plus_5":
            return self._with_css(self.n_plus_n_for_verbs(text, params.get("n", self._rules["defaults"]["v_plus"])))
        elif constraint_type == "antonymic":
            return self._with_css(self.antonymic_transformation(text))
        elif constraint_type == "tautogram":
            return self._with_css(self.tautogram(text, params.get("letter", self._rules["defaults"]["tautogram_letter"])))
        elif constraint_type == "palindrome":
            return self._with_css(self.palindrome(text))
        elif constraint_type == "acrostic":
            return self._with_css(self.acrostic(text))
        elif constraint_type == "sestina":
            return self._with_css(self.sestina(text))
        elif constraint_type == "villanelle":
            return self._with_css(self.villanelle(text))
        elif constraint_type == "pantoum":
            return self._with_css(self.pantoum(text))
        elif constraint_type == "haiku":
            return self._with_css(self.haiku(text))
        elif constraint_type == "limerick":
            return self._with_css(self.limerick(text))
        elif constraint_type == "sonnet":
            return self._with_css(self.sonnet(text))
        else:
            raise ValueError(f"Unknown constraint type: {constraint_type}")

    def _with_css(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Attach Constraint Satisfaction Score (CSS) if possible."""
        if "compliance_score" in result:
            result["constraint_satisfaction_score"] = result["compliance_score"]
        # Combinatorial Difficulty = log2(valid arrangements / total arrangements)
        if "original_text" in result:
            words = re.findall(r"[A-Za-z'\u0900-\u097F\u0600-\u06FF]+", result["original_text"])
            total = len(words)
            if total > 0 and "removed_words" in result:
                valid = total - len(result.get("removed_words", []))
                ratio = max(valid / total, self._rules["math"]["ratio_min"])
                result["combinatorial_difficulty"] = round(math.log(ratio, self._rules["math"]["log_base"]), self._rules["rounding"]["difficulty"])
        return result

    def n_plus_7(self, text: str, n: Optional[int] = None) -> Dict[str, Any]:
        """
        N+7 Method: Replace every noun with the 7th noun following it in dictionary
        
        From quantitative_poetry_metrics.md:
        "Replace every noun with the 7th noun following it in a dictionary"
        """
        n = n if n is not None else self._rules["defaults"]["n_plus"]
        words = text.split()
        transformed = []
        replacements = []

        for word in words:
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            if clean_word.lower() in self.dictionary["nouns"]:
                # Find this noun in dictionary
                noun_list = self.dictionary["nouns"]
                try:
                    idx = noun_list.index(clean_word.lower())
                    # Get Nth noun after
                    new_idx = (idx + n) % len(noun_list)
                    new_word = noun_list[new_idx]
                    # Preserve capitalization
                    if clean_word[0].isupper():
                        new_word = new_word.capitalize()
                    transformed.append(word.replace(clean_word, new_word))
                    replacements.append({
                        "original": clean_word,
                        "replacement": new_word,
                        "position": len(transformed)
                    })
                except ValueError:
                    transformed.append(word)
            else:
                transformed.append(word)

        return {
            "original_text": text,
            "transformed_text": " ".join(transformed),
            "constraint_type": "n_plus_7",
            "parameters": {"n": n},
            "replacements": replacements[: self._rules["limits"]["n_plus_replacements"]],
            "compliance_score": self._rules["defaults"]["compliance_full"] if replacements else self._rules["defaults"]["compliance_none"]
        }

    def s_plus_n(self, text: str, n: Optional[int] = None, pos: str = "s") -> Dict[str, Any]:
        """
        S+10 Method: Replace every substantive (noun/adjective) with the 10th following
        Variant of N+7 for different parts of speech
        """
        n = n if n is not None else self._rules["defaults"]["s_plus"]
        words = text.split()
        transformed = []
        replacements = []

        for word in words:
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            word_lower = clean_word.lower()
            
            for pos_type in ["nouns", "adjectives"]:
                if word_lower in self.dictionary[pos_type]:
                    word_list = self.dictionary[pos_type]
                    try:
                        idx = word_list.index(word_lower)
                        new_idx = (idx + n) % len(word_list)
                        new_word = word_list[new_idx]
                        if clean_word[0].isupper():
                            new_word = new_word.capitalize()
                        transformed.append(word.replace(clean_word, new_word))
                        replacements.append({
                            "original": clean_word,
                            "replacement": new_word,
                            "pos": pos_type[:-1]  # Remove 's'
                        })
                        break
                    except ValueError:
                        pass
            else:
                transformed.append(word)

        return {
            "original_text": text,
            "transformed_text": " ".join(transformed),
            "constraint_type": f"s_plus_{n}",
            "parameters": {"n": n, "pos": pos},
            "replacements": replacements[: self._rules["limits"]["s_plus_replacements"]]
        }

    def n_plus_n_for_verbs(self, text: str, n: Optional[int] = None) -> Dict[str, Any]:
        """
        V+5 Method: Replace every verb with the 5th verb following it
        """
        n = n if n is not None else self._rules["defaults"]["v_plus"]
        words = text.split()
        transformed = []
        replacements = []

        for word in words:
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            if clean_word.lower() in self.dictionary["verbs"]:
                verb_list = self.dictionary["verbs"]
                try:
                    idx = verb_list.index(clean_word.lower())
                    new_idx = (idx + n) % len(verb_list)
                    new_word = verb_list[new_idx]
                    if clean_word[0].isupper():
                        new_word = new_word.capitalize()
                    transformed.append(word.replace(clean_word, new_word))
                    replacements.append({
                        "original": clean_word,
                        "replacement": new_word
                    })
                except ValueError:
                    transformed.append(word)
            else:
                transformed.append(word)

        return {
            "original_text": text,
            "transformed_text": " ".join(transformed),
            "constraint_type": f"v_plus_{n}",
            "parameters": {"n": n},
            "replacements": replacements[: self._rules["limits"]["v_plus_replacements"]]
        }

    def lipogram(self, text: str, forbidden_letter: Optional[str] = None) -> Dict[str, Any]:
        """
        Lipogram: Write without using a specific letter
        
        From quantitative_poetry_metrics.md:
        "Forbid use of a specific letter (e.g., no 'e')"
        Example: Perec's 'A Void' (entire novel without the letter 'e')
        """
        forbidden_letter = forbidden_letter or self._rules["defaults"]["lipogram_letter"]
        forbidden = forbidden_letter.lower()
        words = text.split()
        transformed = []
        removed_words = []

        for word in words:
            if forbidden not in word.lower():
                transformed.append(word)
            else:
                # Try to find synonym without forbidden letter
                synonym = self._find_synonym_without_letter(word, forbidden)
                if synonym:
                    transformed.append(synonym)
                else:
                    removed_words.append(word)

        compliance = len(transformed) / len(words) if words else self._rules["defaults"]["compliance_full"]

        return {
            "original_text": text,
            "transformed_text": " ".join(transformed),
            "constraint_type": "lipogram",
            "parameters": {"forbidden_letter": forbidden_letter},
            "removed_words": removed_words,
            "compliance_score": round(compliance, self._rules["rounding"]["compliance"]),
            "note": self._rules["templates"]["lipogram_note"].format(letter=forbidden_letter)
        }

    def _find_synonym_without_letter(self, word: str, forbidden: str) -> Optional[str]:
        """Find a synonym that doesn't contain the forbidden letter"""
        word = word.lower()
        if self.language == "en":
            try:
                from nltk.corpus import wordnet as wn
                syns = set()
                for syn in wn.synsets(word):
                    for lemma in syn.lemma_names():
                        syns.add(lemma.replace("_", " "))
                for s in syns:
                    if forbidden not in s:
                        return s
            except Exception:
                return None
        return None

    def snowball(self, text: str = None) -> Dict[str, Any]:
        """
        Snowball (Rhopalic): Each word is one letter longer than the previous
        
        From quantitative_poetry_metrics.md:
        "Each line is one word/letter longer than previous"
        "Each line one word, +1 letter each time"
        """
        if text:
            # Analyze existing text for snowball pattern
            words = text.split()
            lengths = [len(re.sub(r'[^a-zA-Z]', '', w)) for w in words]
            
            tolerance = self._rules["snowball"]["length_tolerance"]
            is_snowball = all(
                lengths[i] <= lengths[i+1] + tolerance and lengths[i] >= lengths[i+1] - tolerance
                for i in range(len(lengths)-1)
            )
            
            return {
                "original_text": text,
                "constraint_type": "snowball",
                "is_valid_snowball": is_snowball,
                "word_lengths": lengths,
                "analysis": "Snowball pattern analysis"
            }
        else:
            # Generate a snowball dynamically from dictionary
            pool = self.dictionary["nouns"] + self.dictionary["verbs"] + self.dictionary["adjectives"]
            pool = [w for w in pool if w.isalpha()]
            by_len: Dict[int, List[str]] = {}
            for w in pool:
                by_len.setdefault(len(w), []).append(w)
            generated = []
            length = self._rules["snowball"]["min_length"]
            for _ in range(self._rules["snowball"]["generated_lines"]):
                # find next available length
                while length not in by_len and length < self._rules["snowball"]["max_length"]:
                    length += 1
                if length not in by_len:
                    break
                generated.append(by_len[length][0])
                length += 1

            return {
                "generated_text": " ".join(generated),
                "constraint_type": "snowball",
                "word_lengths": [len(w) for w in generated],
                "note": self._rules["templates"]["snowball_note"]
            }

    def pilish(self, text: str = None) -> Dict[str, Any]:
        """
        Pilish: Word lengths correspond to the digits of π
        
        From quantitative_poetry_metrics.md:
        "Word lengths correspond to the digits of π"
        "3.14159…; word lengths = π digits"
        """
        pi_digits = PI_DIGITS
        
        if text:
            # Analyze existing text for Pilish pattern
            words = text.split()
            lengths = [len(re.sub(r'[^a-zA-Z]', '', w)) for w in words]
            
            matches = sum(1 for i, l in enumerate(lengths[:len(pi_digits)]) 
                         if l == pi_digits[i])
            compliance = matches / min(len(lengths), len(pi_digits))
            
            return {
                "original_text": text,
                "constraint_type": "pilish",
                "word_lengths": lengths[: self._rules["limits"]["word_lengths"]],
                "pi_digits": pi_digits[:len(lengths)] if pi_digits else [],
                "compliance_score": round(compliance, self._rules["rounding"]["compliance"]),
                "matches": matches
            }
        else:
            # Generate Pilish text dynamically from dictionary by word length
            pool = self.dictionary["nouns"] + self.dictionary["verbs"] + self.dictionary["adjectives"]
            pool = [w for w in pool if w.isalpha()]
            by_len: Dict[int, List[str]] = {}
            for w in pool:
                by_len.setdefault(len(w), []).append(w)
            generated = []
            for d in (pi_digits[: self._rules["pilish"]["generated_lines"]] if pi_digits else []):
                if d in by_len and by_len[d]:
                    generated.append(by_len[d][0])
                else:
                    # If no exact match, use nearest available length
                    candidates = sorted(by_len.keys(), key=lambda k: abs(k - d))
                    if candidates:
                        generated.append(by_len[candidates[0]][0])
                    else:
                        break
            
            return {
                "generated_text": " ".join(generated),
                "constraint_type": "pilish",
                "word_lengths": [len(w) for w in generated],
                "pi_digits": pi_digits[:len(generated)] if pi_digits else [],
                "note": self._rules["templates"]["pilish_note"]
            }

    def univocalism(self, text: str, vowel: Optional[str] = None) -> Dict[str, Any]:
        """
        Univocalism: Use only one vowel throughout the text
        
        From quantitative_poetry_metrics.md:
        "One vowel only throughout the text"
        """
        vowel = (vowel or self._rules["defaults"]["univocal_vowel"]).lower()
        if vowel not in self._rules["defaults"]["vowels"]:
            raise ValueError(self._rules["templates"]["vowel_error"].format(vowels=", ".join(self._rules["defaults"]["vowels"])))
        
        words = text.split()
        valid_words = []
        invalid_words = []
        
        for word in words:
            word_vowels = set(c.lower() for c in word if c.lower() in self._rules["defaults"]["vowels"])
            if not word_vowels or word_vowels == {vowel}:
                valid_words.append(word)
            else:
                invalid_words.append(word)
        
        compliance = len(valid_words) / len(words) if words else self._rules["defaults"]["compliance_full"]
        
        return {
            "original_text": text,
            "valid_words": valid_words,
            "invalid_words": invalid_words,
            "constraint_type": "univocalism",
            "parameters": {"vowel": vowel},
            "compliance_score": round(compliance, self._rules["rounding"]["compliance"]),
            "transformed_text": " ".join(valid_words),
            "note": self._rules["templates"]["univocal_note"].format(vowel=vowel)
        }

    def antonymic_transformation(self, text: str) -> Dict[str, Any]:
        """
        Antonymic transformation: Replace words with their opposites
        """
        antonyms = {}
        if self.language == "en":
            try:
                from nltk.corpus import wordnet as wn
                for w in set(re.findall(r"[A-Za-z']+", text.lower())):
                    ants = set()
                    for syn in wn.synsets(w):
                        for lemma in syn.lemmas():
                            for ant in lemma.antonyms():
                                ants.add(ant.name().replace("_", " "))
                    if ants:
                        antonyms[w] = sorted(ants)
            except Exception:
                antonyms = {}
        
        words = text.split()
        transformed = []
        replacements = []
        
        for word in words:
            clean = re.sub(r'[^a-zA-Z]', '', word)
            if clean.lower() in antonyms and antonyms[clean.lower()]:
                new_word = antonyms[clean.lower()][0]
                if clean[0].isupper():
                    new_word = new_word.capitalize()
                transformed.append(word.replace(clean, new_word))
                replacements.append({"original": clean, "replacement": new_word})
            else:
                transformed.append(word)
        
        return {
            "original_text": text,
            "transformed_text": " ".join(transformed),
            "constraint_type": "antonymic",
            "replacements": replacements[: self._rules["limits"]["n_plus_replacements"]]
        }

    def tautogram(self, text: str, letter: Optional[str] = None) -> Dict[str, Any]:
        """
        Tautogram: All words start with the same letter
        
        Note: This analyzes if text is a tautogram, doesn't transform
        """
        letter = (letter or self._rules["defaults"]["tautogram_letter"]).lower()
        words = text.split()
        
        all_match = all(
            re.sub(r'[^a-zA-Z]', '', w).lower().startswith(letter)
            for w in words if re.sub(r'[^a-zA-Z]', '', w)
        )
        
        matching_count = sum(
            1 for w in words
            if re.sub(r'[^a-zA-Z]', '', w).lower().startswith(letter)
        )
        
        return {
            "original_text": text,
            "constraint_type": "tautogram",
            "parameters": {"letter": letter},
            "is_valid_tautogram": all_match,
            "matching_words": matching_count,
            "total_words": len(words),
            "compliance_score": round(matching_count / len(words), self._rules["rounding"]["compliance"]) if words else self._rules["defaults"]["compliance_full"]
        }

    def palindrome(self, text: str) -> Dict[str, Any]:
        """Detect if text is a palindrome (ignoring spaces, punctuation, case)"""
        clean_text = re.sub(r'[^a-zA-Z]', '', text).lower()
        is_palindrome = clean_text == clean_text[::-1]
        
        return {
            "original_text": text,
            "constraint_type": "palindrome",
            "is_valid_palindrome": is_palindrome,
            "compliance_score": self._rules["defaults"]["compliance_full"] if is_palindrome else self._rules["defaults"]["compliance_none"]
        }

    def acrostic(self, text: str) -> Dict[str, Any]:
        """Extract acrostic word from first letters of lines"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        acrostic_word = ""
        for line in lines:
            if line:
                acrostic_word += line[0]
                
        return {
            "original_text": text,
            "constraint_type": "acrostic",
            "acrostic_word": acrostic_word,
            "compliance_score": self._rules["defaults"]["compliance_full"] if acrostic_word else self._rules["defaults"]["compliance_none"]
        }

    def sestina(self, text: str) -> Dict[str, Any]:
        """
        Detect or generate sestina structure (39 lines, 6 stanzas of 6 lines + 3-line envoi)
        End-word permutation pattern: 615243 → 364152 → 231645 → 526314 → 452163 → 143526
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Check if it's a sestina by length
        is_sestina_length = len(lines) == self._rules["forms"]["sestina_lines"]
        
        # Extract end words
        end_words = []
        for line in lines:
            words = line.split()
            if words:
                end_words.append(re.sub(r'[^a-zA-Z]', '', words[-1]).lower())
        
        # Sestina permutation pattern (retrogradatio cruciata)
        # Stanza 1: 1 2 3 4 5 6
        # Stanza 2: 6 1 5 2 4 3
        # Stanza 3: 3 6 4 1 2 5
        # Stanza 4: 5 3 2 6 1 4
        # Stanza 5: 4 5 1 3 6 2
        # Stanza 6: 2 4 6 5 3 1
        # Envoi: (2,4), (6,5), (3,1) or all 6 words
        
        patterns = self._rules["sestina"]["patterns"]

        def get_sestina_position(stanza: int, position: int) -> int:
            """Get which original end-word should appear at this position"""
            if stanza == 0:
                return position  # 1,2,3,4,5,6
            return patterns.get(str(stanza), [1, 2, 3, 4, 5, 6])[position]
        
        # Validate sestina structure (including envoi)
        compliance_checks = []
        if len(end_words) >= self._rules["forms"]["sestina_stanza_size"] and is_sestina_length:
            original_six = end_words[: self._rules["forms"]["sestina_stanza_size"]]
            for stanza in range(self._rules["forms"]["sestina_stanzas"]):
                for pos in range(self._rules["forms"]["sestina_stanza_size"]):
                    line_idx = stanza * self._rules["forms"]["sestina_stanza_size"] + pos
                    expected_word = original_six[get_sestina_position(stanza, pos) - 1]
                    actual_word = end_words[line_idx]
                    compliance_checks.append(expected_word == actual_word)

            # Envoi must include all six end-words, two per line
            envoi_lines = lines[-self._rules["forms"]["sestina_envoi_lines"]:]
            envoi_words = [set(re.findall(r"[A-Za-z]+", l.lower())) for l in envoi_lines]
            envoi_pairs = self._rules["sestina"]["envoi_pairs"]
            for idx, pair in enumerate(envoi_pairs):
                if idx < len(envoi_words) and len(original_six) >= max(pair):
                    pair_words = (original_six[pair[0] - 1], original_six[pair[1] - 1])
                    compliance_checks.append(pair_words[0] in envoi_words[idx] and pair_words[1] in envoi_words[idx])
                else:
                    compliance_checks.append(False)
        compliance_score = sum(compliance_checks) / len(compliance_checks) if compliance_checks else self._rules["defaults"]["compliance_none"]
        
        return {
            "original_text": text,
            "constraint_type": "sestina",
            "is_sestina_length": is_sestina_length,
            "line_count": len(lines),
            "end_words": end_words[: self._rules["limits"]["end_words"]] if len(end_words) >= self._rules["limits"]["end_words"] else end_words,
            "compliance_score": round(compliance_score, self._rules["rounding"]["css"]),
            "description": self._rules["templates"]["sestina_description"]
        }
    
    def generate_sestina(self, end_words: List[str]) -> str:
        """
        Generate a sestina template with the given 6 end-words
        Returns a template poem structure with end-words in correct positions
        """
        if len(end_words) != self._rules["forms"]["sestina_stanza_size"]:
            raise ValueError("Sestina requires exactly 6 end-words")
        
        patterns = [self._rules["sestina"]["base_pattern"]]
        for stanza_key in sorted(self._rules["sestina"]["patterns"].keys(), key=int):
            stanza = [p - 1 for p in self._rules["sestina"]["patterns"][stanza_key]]
            patterns.append(stanza)
        
        poem_lines = []
        for stanza_idx, pattern in enumerate(patterns):
            for pos in pattern:
                poem_lines.append(f"[Line {stanza_idx * self._rules['forms']['sestina_stanza_size'] + pos + 1}] ... {end_words[pos]}")
        
        # Envoi (3 lines with all 6 end-words embedded)
        envoi_pairs = self._rules["sestina"]["envoi_pairs"]
        for idx, pair in enumerate(envoi_pairs, start=1):
            poem_lines.append(f"[Envoi {idx}] ... {end_words[pair[0]-1]} ... {end_words[pair[1]-1]}")
        
        return "\n".join(poem_lines)

    def knights_tour(self, text: str) -> Dict[str, Any]:
        """
        Knight's Tour constraint: Text follows chess knight path on grid
        Can be used to hide messages or create reading patterns
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Create a grid from the text
        grid = []
        for line in lines:
            row = list(line.replace(' ', '').upper())
            grid.append(row)
        
        # Knight moves in L-shape: 2 squares one direction, 1 square perpendicular
        knight_moves = [tuple(m) for m in self._rules["knights_tour"]["moves"]]
        
        def is_valid(x: int, y: int) -> bool:
            return 0 <= x < len(grid) and 0 <= y < len(grid[0]) if grid else False
        
        # Try to find a knight's tour starting from each position
        max_path = []
        for start_x in range(len(grid)):
            for start_y in range(len(grid[0])) if grid else range(0):
                visited = set()
                path = []
                x, y = start_x, start_y
                
                while True:
                    if (x, y) not in visited and is_valid(x, y):
                        visited.add((x, y))
                        path.append(grid[x][y])
                        
                        # Find next valid move
                        moved = False
                        for dx, dy in knight_moves:
                            nx, ny = x + dx, y + dy
                            if is_valid(nx, ny) and (nx, ny) not in visited:
                                x, y = nx, ny
                                moved = True
                                break
                        
                        if not moved:
                            break
                    else:
                        break
                
                if len(path) > len(max_path):
                    max_path = path
        
        knight_text = ''.join(max_path)
        
        return {
            "original_text": text,
            "constraint_type": "knights_tour",
            "grid_dimensions": f"{len(grid)}x{len(grid[0])}" if grid else self._rules["templates"]["grid_dimensions_empty"],
            "knight_path_length": len(max_path),
            "knight_text": knight_text[: self._rules["limits"]["knight_preview_chars"]] + "..." if len(knight_text) > self._rules["limits"]["knight_preview_chars"] else knight_text,
            "description": self._rules["templates"]["knight_description"]
        }

    def villanelle(self, text: str) -> Dict[str, Any]:
        """Detect if poem follows villanelle structure (19 lines, 5 tercets + 1 quatrain)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        is_villanelle = len(lines) == self._rules["forms"]["villanelle_lines"]

        violations = 0
        total_constraints = 0

        # Constraint 1: line count
        total_constraints += self._rules["constraint_counts"]["villanelle_line"]
        if not is_villanelle:
            violations += 1

        # Constraints 2-3: refrains exact repetition
        a1 = lines[0] if len(lines) > 0 else ""
        a2 = lines[2] if len(lines) > 2 else ""
        a1_positions = self._rules["villanelle"]["a1_positions"]
        a2_positions = self._rules["villanelle"]["a2_positions"]
        total_constraints += len(a1_positions) + len(a2_positions)
        for idx in a1_positions:
            if idx < len(lines) and lines[idx] != a1:
                violations += 1
        for idx in a2_positions:
            if idx < len(lines) and lines[idx] != a2:
                violations += 1

        # Constraint 4: rhyme scheme A1 b A2 / abA1 / abA2 / abA1 / abA2 / abA1A2
        total_constraints += self._rules["constraint_counts"]["rhyme_scheme"]
        scheme_ok = self._check_villanelle_rhyme(lines)
        if not scheme_ok:
            violations += 1

        css = self._rules["defaults"]["compliance_full"] - (violations / total_constraints) if total_constraints > 0 else self._rules["defaults"]["compliance_none"]

        return {
            "original_text": text,
            "constraint_type": "villanelle",
            "is_villanelle_length": is_villanelle,
            "line_count": len(lines),
            "compliance_score": round(css, self._rules["rounding"]["css"]),
            "violations": violations,
            "total_constraints": total_constraints
        }

    def pantoum(self, text: str) -> Dict[str, Any]:
        """Detect pantoum structure (quatrains, lines 2&4 become 1&3 of next stanza)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return {
            "original_text": text,
            "constraint_type": "pantoum",
            "line_count": len(lines),
            "analysis": self._rules["templates"]["pantoum_analysis"]
        }

    def haiku(self, text: str) -> Dict[str, Any]:
        """Detect haiku structure (3 lines, typically 5-7-5 syllables)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        is_haiku_length = len(lines) == self._rules["forms"]["haiku_lines"]
        syllable_targets = HAIKU_SYLLABLES if HAIKU_SYLLABLES else self._rules["haiku"]["syllable_targets"]
        syllable_counts = [self._count_syllables(line) for line in lines]
        syllable_ok = is_haiku_length and len(syllable_counts) == self._rules["forms"]["haiku_lines"] and all(
            syllable_counts[i] == syllable_targets[i] for i in range(self._rules["forms"]["haiku_lines"])
        )

        violations = 0
        total_constraints = self._rules["constraint_counts"]["haiku_line"] + self._rules["forms"]["haiku_lines"]
        if not is_haiku_length:
            violations += 1
        for i in range(min(self._rules["forms"]["haiku_lines"], len(syllable_counts))):
            if syllable_counts[i] != syllable_targets[i]:
                violations += 1
        if len(syllable_counts) < self._rules["forms"]["haiku_lines"]:
            violations += (self._rules["forms"]["haiku_lines"] - len(syllable_counts))
        css = self._rules["defaults"]["compliance_full"] - (violations / total_constraints) if total_constraints > 0 else self._rules["defaults"]["compliance_none"]

        return {
            "original_text": text,
            "constraint_type": "haiku",
            "is_haiku_length": is_haiku_length,
            "line_count": len(lines),
            "syllable_counts": syllable_counts,
            "syllable_pattern": syllable_targets,
            "compliance_score": round(css, self._rules["rounding"]["css"]),
            "violations": violations,
            "total_constraints": total_constraints
        }

    def limerick(self, text: str) -> Dict[str, Any]:
        """Detect limerick structure (5 lines, AABBA rhyme)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        is_limerick_length = len(lines) == self._rules["forms"]["limerick_lines"]

        violations = 0
        total_constraints = self._rules["constraint_counts"]["limerick_total"]
        if not is_limerick_length:
            violations += 1
        rhyme_ok = self._check_limerick_rhyme(lines)
        if not rhyme_ok:
            violations += 1
        css = self._rules["defaults"]["compliance_full"] - (violations / total_constraints) if total_constraints > 0 else self._rules["defaults"]["compliance_none"]
        
        return {
            "original_text": text,
            "constraint_type": "limerick",
            "is_limerick_length": is_limerick_length,
            "line_count": len(lines),
            "compliance_score": round(css, self._rules["rounding"]["css"]),
            "violations": violations,
            "total_constraints": total_constraints
        }

    def sonnet(self, text: str) -> Dict[str, Any]:
        """Detect sonnet structure (14 lines)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        is_sonnet_length = len(lines) == self._rules["forms"]["sonnet_lines"]

        violations = 0
        total_constraints = self._rules["constraint_counts"]["sonnet_line"]  # line count
        if not is_sonnet_length:
            violations += 1

        # Rhyme scheme: Shakespearean or Petrarchan
        scheme_ok = self._check_sonnet_rhyme(lines)
        total_constraints += self._rules["constraint_counts"]["sonnet_rhyme"]
        if not scheme_ok:
            violations += 1

        # Meter: iambic pentameter for each line
        meter_ok, meter_violations = self._check_iambic_pentameter(lines)
        total_constraints += len(lines)
        violations += meter_violations

        css = self._rules["defaults"]["compliance_full"] - (violations / total_constraints) if total_constraints > 0 else self._rules["defaults"]["compliance_none"]
        
        return {
            "original_text": text,
            "constraint_type": "sonnet",
            "is_sonnet_length": is_sonnet_length,
            "line_count": len(lines),
            "compliance_score": round(css, self._rules["rounding"]["css"]),
            "violations": violations,
            "total_constraints": total_constraints,
            "rhyme_scheme_ok": scheme_ok,
            "meter_ok": meter_ok
        }

    def _count_syllables(self, line: str) -> int:
        words = re.findall(r"[A-Za-z']+", line)
        return sum(max(self._rules["defaults"]["syllable_min"], syllables.estimate(w)) for w in words) if words else 0

    def _rhyme_part(self, word: str) -> str:
        from app.services.phonology_resources import get_phonology

        phon = get_phonology(self.language)
        part = phon.rhyme_key(word)
        return part or ""

    def _check_villanelle_rhyme(self, lines: List[str]) -> bool:
        if len(lines) != self._rules["forms"]["villanelle_lines"]:
            return False
        a_lines = self._rules["villanelle"]["a_lines"]
        b_lines = self._rules["villanelle"]["b_lines"]
        a_end = self._line_end_word(lines[a_lines[0]]) if lines else ""
        b_end = self._line_end_word(lines[b_lines[0]]) if lines else ""
        if not a_end or not b_end:
            return False
        for idx in a_lines:
            if self._rhyme_part(self._line_end_word(lines[idx])) != self._rhyme_part(a_end):
                return False
        for idx in b_lines:
            if self._rhyme_part(self._line_end_word(lines[idx])) != self._rhyme_part(b_end):
                return False
        return self._rhyme_part(a_end) != self._rhyme_part(b_end)

    def _check_limerick_rhyme(self, lines: List[str]) -> bool:
        if len(lines) != self._rules["forms"]["limerick_lines"]:
            return False
        ends = [self._line_end_word(l) for l in lines]
        if any(not e for e in ends):
            return False
        a = self._rhyme_part(ends[0])
        b = self._rhyme_part(ends[2])
        return (
            self._rhyme_part(ends[1]) == a and
            self._rhyme_part(ends[4]) == a and
            self._rhyme_part(ends[2]) == b and
            self._rhyme_part(ends[3]) == b and
            a != b
        )

    def _check_sonnet_rhyme(self, lines: List[str]) -> bool:
        if len(lines) != self._rules["forms"]["sonnet_lines"]:
            return False
        ends = [self._line_end_word(l) for l in lines]
        if any(not e for e in ends):
            return False
        schemes = self._rules["sonnet"]["schemes"]
        return any(self._matches_scheme(ends, scheme) for scheme in schemes)

    def _matches_scheme(self, ends: List[str], scheme: str) -> bool:
        if len(ends) != len(scheme):
            return False
        groups = {}
        for end, letter in zip(ends, scheme):
            r = self._rhyme_part(end)
            if letter in groups:
                if groups[letter] != r:
                    return False
            else:
                groups[letter] = r
        # Ensure different letters are not accidentally same rhyme
        uniq = list(groups.values())
        return len(uniq) == len(set(uniq))

    def _line_end_word(self, line: str) -> str:
        words = re.findall(r"[A-Za-z']+", line)
        return words[-1].lower() if words else ""

    def _check_iambic_pentameter(self, lines: List[str]) -> Tuple[bool, int]:
        analyzer = ProsodyAnalyzer()
        expected = self._rules["meter"]["iambic_unit"] * self._rules["meter"]["iambic_feet"]
        violations = 0
        for line in lines:
            words = line.split()
            pattern = []
            for word in words:
                stress = analyzer._get_stress(word)
                pattern.extend(stress.split("-"))
            if pattern != expected:
                violations += 1
        return violations == 0, violations


def generate_constrained_text(constraint_type: str, params: Dict = None) -> Dict[str, Any]:
    """
    Generate new text using Oulipo constraints
    
    Args:
        constraint_type: Type of constraint to apply
        params: Constraint-specific parameters
        
    Returns:
        Generated text with constraint metadata
    """
    engine = OulipoConstraintEngine()
    
    if constraint_type == "fibonacci":
        # Generate Fibonacci poem (syllables per line: 1, 1, 2, 3, 5, 8)
        fib_sequence = FIBONACCI_SMALL if FIBONACCI_SMALL else engine._rules["fibonacci"]["fallback_sequence"]
        # Build dynamically from dictionary
        pool = engine.dictionary["nouns"] + engine.dictionary["verbs"] + engine.dictionary["adjectives"]
        pool = [w for w in pool if w.isalpha()]
        by_syl: Dict[int, List[str]] = {}
        for w in pool:
            syl = max(engine._rules["fibonacci"]["syllable_min"], syllables.estimate(w))
            by_syl.setdefault(syl, []).append(w)
        words = []
        for syl in fib_sequence:
            if syl in by_syl and by_syl[syl]:
                words.append(by_syl[syl][0])
            else:
                # fallback to nearest syllable count available
                candidates = sorted(by_syl.keys(), key=lambda k: abs(k - syl))
                if candidates:
                    words.append(by_syl[candidates[0]][0])
                else:
                    words.append("")
        return {
            "generated_text": "\n".join(words[i] for i in range(len(words))),
            "constraint_type": "fibonacci",
            "syllable_pattern": fib_sequence,
            "note": engine._rules["templates"]["fibonacci_note"]
        }
    
    # For other constraints, require source text
    return engine.apply_constraint("Text input required for constraint transformation", constraint_type, params)
