"""
Prosody & Meter Analysis Module
Complete implementation for English, Hindi (Chhand), Urdu (Aruz), and Gujarati prosody
Based on Quantitative Poetry Metrics - Section 4 & Ultimate Literary Master System
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter
import pronouncing
import syllables  # Use library for English syllable counting
from app.services.phonology_resources import (
    get_phonology,
    IPA_VOWELS,
    count_syllables_from_ipa,
    fallback_syllable_count,
    syllabify_ipa,
)
from app.services.rule_loader import get_form_rules, get_output_limits


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "prosody"
_CONSTRAINTS_DIR = Path(__file__).resolve().parents[2] / "data" / "constraints"
METER_PATTERNS = _load_json(_DATA_DIR / "meter_patterns.json")
HAIKU_SYLLABLES = _load_json(_CONSTRAINTS_DIR / "haiku_syllables.json")
EN_VOWELS = set(_load_json(_DATA_DIR / "english_vowels.json").get("vowels", []))


# =============================================================================
# ENGLISH METER PATTERNS
# =============================================================================


# Comprehensive stress dictionary (CMU Pronouncing Dictionary subset)


class ProsodyAnalyzer:
    """
    Analyze meter, scansion, and rhyme patterns in poetry
    Supports English, Hindi, Urdu, and Gujarati prosodic systems
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.text = ""
        self.lines: List[str] = []

    def analyze(self, text: str) -> Dict[str, Any]:
        """Main analysis function"""
        self.text = text
        self.lines = [line.strip() for line in text.split("\n") if line.strip()]

        if self.language == "en":
            return {
                "meter": self._analyze_meter(),
                "rhyme": self._analyze_rhyme(),
                "scansion": self._generate_scansion(),
            }
        elif self.language in ["hi", "mr", "bn", "sa"]:
            hindi_analyzer = HindiProsodyAnalyzer()
            return hindi_analyzer.analyze(text)
        elif self.language == "gu":
            gujarati_analyzer = GujaratiProsodyAnalyzer()
            return gujarati_analyzer.analyze(text)
        elif self.language == "ur":
            urdu_analyzer = UrduProsodyAnalyzer()
            return urdu_analyzer.analyze(text)
        else:
            return {
                "meter": self._analyze_meter(),
                "rhyme": self._analyze_rhyme(),
                "scansion": self._generate_scansion(),
            }

    def _analyze_meter(self) -> Dict[str, Any]:
        """Detect meter pattern in the text"""
        if not self.lines:
            return {"detected_meter": None, "error": "No lines to analyze"}

        limits = get_output_limits()
        sample_limit = limits.get("prosody_meter_sample_lines") if limits else None
        sample_lines = self.lines[: int(sample_limit)] if sample_limit is not None else self.lines
        line_patterns = []

        for line in sample_lines:
            words = line.split()
            pattern = []
            for word in words:
                stress = self._get_stress(word)
                pattern.append(stress)
            line_patterns.append(pattern)

        detected_meter = self._detect_meter_type(line_patterns)
        regularity = self._calculate_regularity(line_patterns, detected_meter, tolerance_subs=0)
        regularity_tolerant = self._calculate_regularity(line_patterns, detected_meter, tolerance_subs=1)
        foot_dist = self._foot_distribution(line_patterns)

        # Detect line length (monometer through hexameter)
        line_length = self._detect_line_length(line_patterns)
        sample_pattern_limit = limits.get("prosody_sample_patterns") if limits else None
        sample_patterns = (
            line_patterns[: int(sample_pattern_limit)]
            if sample_pattern_limit is not None
            else line_patterns
        )

        return {
            "detected_meter": detected_meter,
            "metrical_regularity": round(regularity, 2),
            "metrical_regularity_tolerant": round(regularity_tolerant, 2),
            "metrical_regularity_strict": round(regularity, 2),
            "scansion_adherence_percent": round(regularity * 100, 2),
            "scansion_adherence_percent_tolerant": round(regularity_tolerant * 100, 2),
            "foot_count_distribution": foot_dist,
            "sample_patterns": ["-".join(p) for p in sample_patterns],
            "line_length": line_length,
            "full_meter_name": f"{detected_meter} {line_length}"
            if detected_meter and line_length
            else None,
        }

    def _get_stress(self, word: str) -> str:
        """Get stress pattern for a word"""
        word_lower = word.lower().strip(".,!?;:'\"")

        try:
            stresses_list = pronouncing.stresses_for_word(word_lower)
            if stresses_list:
                stress_pattern = stresses_list[0]
                return (
                    stress_pattern.replace("0", "da-")
                    .replace("1", "DUM-")
                    .replace("2", "DUM-")
                    .strip("-")
                )
        except:
            pass

        # Estimate based on syllable count
        syllable_count = self._count_syllables(word)

        if syllable_count == 1:
            return "DUM"
        elif syllable_count == 2:
            if word_lower.endswith(("ing", "ed", "er", "ly", "tion", "sion", "ment")):
                return "da-DUM"
            return "DUM-da"
        elif syllable_count == 3:
            return "DUM-da-da"
        else:
            return "da-" * (syllable_count - 1) + "DUM"

    def _count_syllables(self, word: str) -> int:
        """Count syllables using library for English, manual for others"""
        word = word.lower().strip(".,!?;:'\"")
        if not word:
            return 0

        # Use syllables library for English (more accurate than manual regex)
        if self.language == "en":
            try:
                return syllables.estimate(word) or 1
            except Exception:
                pass  # Fall back to manual

        # Manual vowel counting for non-English or fallback
        vowels = EN_VOWELS
        count = 0
        prev_is_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel

        if word.endswith("e") and count > 1:
            count -= 1
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            count += 1

        return max(1, count)

    def _detect_meter_type(self, patterns: List[List[str]]) -> str:
        """Detect the meter type from stress patterns"""
        if not patterns:
            return "unknown"

        flat = []
        for p in patterns:
            flat.extend(p)

        pattern_str = "-".join(flat)

        # Count frequencies of metrical feet
        iamb_count = pattern_str.count("da-DUM")
        trochee_count = pattern_str.count("DUM-da")
        anapest_count = pattern_str.count("da-da-DUM")
        dactyl_count = pattern_str.count("DUM-da-da")
        spondee_count = pattern_str.count("DUM-DUM")
        pyrrhic_count = pattern_str.count("da-da")

        counts = {
            "iambic": iamb_count,
            "trochaic": trochee_count,
            "anapestic": anapest_count,
            "dactylic": dactyl_count,
            "spondaic": spondee_count,
            "pyrrhic": pyrrhic_count,
        }

        if sum(counts.values()) == 0:
            return "free_verse"

        dominant_meter = max(counts, key=counts.get)

        # Check specific line lengths for full meter name
        if dominant_meter == "iambic" and any(len(p) == 10 for p in patterns):
            return "iambic_pentameter"
        if dominant_meter == "trochaic" and any(len(p) in [8, 7] for p in patterns):
            return "trochaic_tetrameter"
        if dominant_meter == "anapestic" and any(len(p) in [9, 8] for p in patterns):
            return "anapestic_trimeter"
        if dominant_meter == "dactylic" and any(
            len(p) in [17, 16, 15] for p in patterns
        ):
            return "dactylic_hexameter"

        return dominant_meter

    def _calculate_regularity(
        self, patterns: List[List[str]], meter_type: str, tolerance_subs: int = 0
    ) -> float:
        """Calculate metrical regularity score"""
        if not patterns or meter_type in ["free_verse", "unknown"]:
            return 0.0

        expected = METER_PATTERNS.get(meter_type.replace("_pentameter", ""), {}).get(
            "pattern", []
        )
        if not expected:
            return 0.0
        matches = 0
        total = len(patterns)

        for pattern in patterns:
            if len(pattern) % len(expected) != 0:
                continue
            repeated = expected * (len(pattern) // len(expected))
            if pattern == repeated:
                matches += 1
            else:
                # allow tolerance_subs substitutions
                mismatches = sum(1 for a, b in zip(pattern, repeated) if a != b)
                if mismatches <= tolerance_subs:
                    matches += 1

        return matches / total if total > 0 else 0.0

    def _foot_distribution(self, patterns: List[List[str]]) -> Dict[str, int]:
        """Count different foot types"""
        feet = Counter()

        for pattern in patterns:
            i = 0
            while i < len(pattern):
                if i < len(pattern) and pattern[i] == "da":
                    for j in range(i + 1, min(i + 4, len(pattern) + 1)):
                        segment = pattern[i:j]
                        if "DUM" in segment:
                            feet[tuple(segment)] += 1
                            i = j
                            break
                    else:
                        i += 1
                else:
                    for j in range(i + 1, min(i + 4, len(pattern) + 1)):
                        segment = pattern[i:j]
                        if "DUM" in segment:
                            feet[tuple(segment)] += 1
                            i = j
                            break
                    else:
                        i += 1

        named_feet = {}
        for foot, count in feet.items():
            foot_str = "-".join(foot)
            if "da-DUM" in foot_str:
                named_feet["iamb"] = named_feet.get("iamb", 0) + count
            elif "DUM-da" in foot_str:
                named_feet["trochee"] = named_feet.get("trochee", 0) + count
            elif "da-da-DUM" in foot_str:
                named_feet["anapest"] = named_feet.get("anapest", 0) + count
            elif "DUM-da-da" in foot_str:
                named_feet["dactyl"] = named_feet.get("dactyl", 0) + count
            elif "DUM-DUM" in foot_str:
                named_feet["spondee"] = named_feet.get("spondee", 0) + count
            elif "da-da" in foot_str:
                named_feet["pyrrhus"] = named_feet.get("pyrrhus", 0) + count
            else:
                named_feet["other"] = named_feet.get("other", 0) + count

        return named_feet

    def _detect_line_length(self, patterns: List[List[str]]) -> str:
        """Detect line length (monometer through octameter)"""
        if not patterns:
            return ""

        avg_feet = (
            sum(len(p) for p in patterns) / len(patterns) / 2
        )  # Approximate feet count

        length_map = {
            (0, 2): "monometer",
            (2, 4): "dimeter",
            (4, 6): "trimeter",
            (6, 8): "tetrameter",
            (8, 10): "pentameter",
            (10, 12): "hexameter",
            (12, 14): "heptameter",
            (14, 16): "octameter",
        }

        for (low, high), name in length_map.items():
            if low <= avg_feet < high:
                return name
        return "pentameter"

    def _generate_scansion(self) -> List[Dict[str, Any]]:
        """Generate scansion notation for each line"""
        scansion = []

        for i, line in enumerate(self.lines):
            words = line.split()
            stresses = []

            for word in words:
                stress = self._get_stress(word)
                marked = stress.replace("DUM", "/").replace("da", "×")
                stresses.append({"word": word, "stress": stress, "marked": marked})

            scansion.append({"line_number": i + 1, "text": line, "syllables": stresses})

        return scansion

    def _analyze_rhyme(self) -> Dict[str, Any]:
        """Analyze rhyme scheme and density"""
        if not self.lines:
            return {"detected_scheme": None}

        last_words = []
        for line in self.lines:
            words = line.split()
            if words:
                last_words.append(words[-1].lower().strip(".,!?;:'\""))

        rhyme_scheme = []
        rhyme_groups = {}
        next_letter = ord("A")

        for i, word in enumerate(last_words):
            found = False
            for letter, group in rhyme_groups.items():
                if self._rhymes_with(word, group[0]):
                    rhyme_groups[letter].append(word)
                    rhyme_scheme.append(letter)
                    found = True
                    break

            if not found:
                letter = chr(next_letter)
                rhyme_groups[letter] = [word]
                rhyme_scheme.append(letter)
                next_letter += 1

        rhyme_density = self._calculate_rhyme_density(rhyme_groups)
        quality = self._assess_rhyme_quality(last_words, rhyme_groups)

        # Detect form based on rhyme scheme
        detected_form = self._detect_form_from_rhyme(
            "".join(rhyme_scheme), len(self.lines)
        )

        return {
            "detected_scheme": "".join(rhyme_scheme),
            "rhyme_density": round(rhyme_density, 2),
            "rhyme_groups": {
                k: {"words": v, "count": len(v)} for k, v in rhyme_groups.items()
            },
            "rhyme_quality": quality,
            "total_lines": len(self.lines),
            "detected_form": detected_form,
        }

    def _rhymes_with(self, word1: str, word2: str) -> bool:
        """Check if two words rhyme"""
        if not word1 or not word2:
            return False
        from app.services.phonology_resources import get_phonology

        phon = get_phonology(self.language)
        part1 = phon.rhyme_key(word1)
        part2 = phon.rhyme_key(word2)
        return bool(part1 and part2 and part1 == part2)

    def _calculate_rhyme_density(self, rhyme_groups: Dict) -> float:
        """Calculate exact rhyme density: R / (n(n-1)/2)"""
        if not rhyme_groups:
            return 0.0

        # Flatten last words
        last_words = []
        for group in rhyme_groups.values():
            last_words.extend(group)
        n = len(last_words)
        if n < 2:
            return 0.0
        total_pairs = n * (n - 1) / 2
        r = 0
        for i in range(n):
            for j in range(i + 1, n):
                if self._rhymes_with(last_words[i], last_words[j]):
                    r += 1
        return r / total_pairs

    def _assess_rhyme_quality(self, last_words: List[str], rhyme_groups: Dict) -> str:
        """Assess rhyme quality"""
        if len(rhyme_groups) <= 1:
            return "none"

        perfect_count = sum(1 for group in rhyme_groups.values() if len(group) > 1)

        if perfect_count == len(rhyme_groups):
            return "perfect"
        elif perfect_count > 0:
            return "partial"
        else:
            return "slant"

    def _detect_form_from_rhyme(self, scheme: str, line_count: int) -> Optional[str]:
        """Detect poetic form from rhyme scheme"""
        if line_count == 14:
            if scheme in ["ABAB CDCD EFEF GG", "ABABCDCDEFEFGG"]:
                return "sonnet_shakespearean"
            elif scheme in ["ABBAABBA CDECDE", "ABBAABBA CDCDCD"]:
                return "sonnet_petrarchan"
        elif line_count == 3 and scheme == "ABA":
            return "haiku"
        elif line_count == 5 and scheme == "AABBA":
            return "limerick"
        elif line_count == 19 and scheme.startswith("A") and scheme.count("A") >= 6:
            return "villanelle"
        elif len(set(scheme)) == 2 and line_count % 2 == 0:
            if scheme == "AABB" * (line_count // 4):
                return "couplets"
            elif scheme == "ABAB" * (line_count // 4):
                return "alternate_rhyme"
        elif scheme.startswith("A") and all(s == scheme[0] for s in scheme):
            return "monorhyme"

        return None


class HindiProsodyAnalyzer:
    """
    Analyze Hindi/Devanagari prosody (Chhand system)
    Implements Doha, Chaupai, Soratha, Kundaliya, etc.
    """

    def __init__(self) -> None:
        vowels = _load_json(_DATA_DIR / "hindi_vowels.json")
        signs = _load_json(_DATA_DIR / "hindi_signs.json")
        self.laghu_vowels = set(vowels.get("laghu", []))
        self.guru_vowels = set(vowels.get("guru", []))
        self.laghu_signs = set(signs.get("laghu_signs", []))
        self.guru_signs = set(signs.get("guru_signs", []))
        self.anusvara_visarga = set(signs.get("anusvara_visarga", []))
        self.virama = signs.get("virama", "्")
        self.chhand_patterns = _load_json(_DATA_DIR / "chhand_patterns.json")
        self.lines: List[str] = []

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze Hindi text for chhand (meter)"""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        self.lines = lines

        matra_counts = []
        lg_sequences = []
        gana_sequences = []
        for line in lines:
            lg = self._lg_sequence(line)
            lg_sequences.append(lg)
            gana_sequences.append(self._gana_sequence(lg))
            matra = self._count_matras(line)
            matra_counts.append(matra)

        detected_chhand = self._detect_chhand(matra_counts)
        is_valid = detected_chhand is not None and detected_chhand != "free_verse"
        end_rule_ok = self._check_end_rules(lines, lg_sequences, detected_chhand)
        is_valid_chhand = bool(is_valid and end_rule_ok)

        expected = self.chhand_patterns.get(detected_chhand, {}).get("matra") if detected_chhand else None
        if expected:
            total = min(len(matra_counts), len(expected))
            matches = sum(1 for i in range(total) if matra_counts[i] == expected[i])
            metrical_regularity = matches / total if total > 0 else 0.0
        else:
            metrical_regularity = 0.0

        last_words = []
        end_patterns = []
        for line in lines:
            words = line.split()
            if words:
                last_word = words[-1].lower().strip(".,!?;:'\"")
                last_words.append(last_word)
                pattern = self._end_syllable_pattern(last_word)
                if pattern:
                    end_patterns.append(pattern)
        n = len(last_words)
        if n >= 2:
            total_pairs = n * (n - 1) / 2
            r = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if self._rhymes_with(last_words[i], last_words[j]):
                        r += 1
            rhyme_density = r / total_pairs
        else:
            rhyme_density = 0.0

        antyanuprasa_density = 0.0
        if end_patterns:
            pattern_counts = Counter(end_patterns)
            dominant_pattern = max(pattern_counts, key=pattern_counts.get)
            matching_lines = sum(1 for p in end_patterns if p == dominant_pattern)
            antyanuprasa_density = matching_lines / len(lines) if lines else 0.0

        # Map to common prosody keys for front-end compatibility
        return {
            "meter": {
                "detected_meter": detected_chhand or "free_verse",
                "metrical_regularity": round(metrical_regularity, 4),
                "scansion_adherence_percent": round(metrical_regularity * 100, 2),
                "foot_pattern": "Matra-based",
                "matra_counts": matra_counts,
                "lg_sequences": lg_sequences,
                "gana_sequences": gana_sequences,
                "end_rule_ok": end_rule_ok,
                "is_valid_chhand": is_valid_chhand,
                "description": self.chhand_patterns.get(detected_chhand, {}).get(
                    "description"
                )
                if detected_chhand
                else None,
            },
            "rhyme": {
                "detected_scheme": "AABB" if is_valid and len(lines) >= 2 else "None",
                "rhyme_density": round(rhyme_density, 4),
                "antyanuprasa_density": round(antyanuprasa_density, 4),
            },
            "scansion": [
                {"line_number": i + 1, "text": line, "matras": m}
                for i, (line, m) in enumerate(zip(lines, matra_counts))
            ],
            "detected_chhand": detected_chhand,
            "is_valid": is_valid,
        }

    def _lg_sequence(self, line: str) -> List[str]:
        """Compute L/G sequence for a line based on matra rules."""
        laghu = self.laghu_vowels
        guru = self.guru_vowels
        laghu_signs = self.laghu_signs
        guru_signs = self.guru_signs
        anusvara_visarga = self.anusvara_visarga
        sequence: List[str] = []

        chars = list(line)
        for i, ch in enumerate(chars):
            if ch in laghu:
                sequence.append("L")
            elif ch in guru:
                sequence.append("G")
            elif ch in laghu_signs:
                sequence.append("L")
            elif ch in guru_signs:
                sequence.append("G")
            elif ch == self.virama:  # conjunct: previous short becomes guru
                if sequence:
                    sequence[-1] = "G"
            elif ch in anusvara_visarga:
                if sequence:
                    sequence[-1] = "G"

        # End-of-line short vowel optionally guru (strictly apply)
        if sequence and sequence[-1] == "L":
            sequence[-1] = "G"
        return sequence

    def _gana_sequence(self, lg: List[str]) -> List[str]:
        """Pingala's 8 Gana system mapping from L/G triplets."""
        mapping = {
            "LGG": "Ya",
            "GGG": "Ma",
            "GGL": "Ta",
            "GLG": "Ra",
            "LGL": "Ja",
            "GLL": "Bha",
            "LLL": "Na",
            "LLG": "Sa",
        }
        gana = []
        for i in range(0, len(lg), 3):
            triplet = "".join(lg[i : i + 3])
            if len(triplet) == 3:
                gana.append(mapping.get(triplet, ""))
        return gana

    def _check_end_rules(self, lines: List[str], lg_sequences: List[List[str]], chhand: Optional[str]) -> bool:
        if not chhand or chhand not in self.chhand_patterns:
            return False

        # Helper to get last syllables of a sequence
        def last_syllables(seq: List[str], n: int) -> List[str]:
            return seq[-n:] if len(seq) >= n else seq

        if chhand == "doha":
            # even charan ends with Guru-Laghu (S|)
            for idx, seq in enumerate(lg_sequences):
                if not seq:
                    return False
                if last_syllables(seq, 2) != ["G", "L"]:
                    return False
            return True
        if chhand == "chaupai":
            # last two syllables NOT Guru-Laghu
            for seq in lg_sequences:
                if last_syllables(seq, 2) == ["G", "L"]:
                    return False
            return True
        if chhand == "harigitika":
            # ends with Laghu-Guru
            for seq in lg_sequences:
                if last_syllables(seq, 2) != ["L", "G"]:
                    return False
            return True
        if chhand == "barvai":
            # even charan ends with Jagana (LGL)
            for seq in lg_sequences:
                if last_syllables(seq, 3) != ["L", "G", "L"]:
                    return False
            return True
        if chhand == "soratha":
            # rhyme on odd charans: require line 1 and 2 end rhyme
            if len(lines) >= 2:
                last_words = [l.split()[-1] for l in lines if l.split()]
                if len(last_words) >= 2:
                    return self._rhymes_with(last_words[0], last_words[1])
            return False
        if chhand == "kavitt":
            # yati at 16-15 or 8-8-8-7 (approx via matra count)
            for line in lines:
                weights = self._matra_weights(line)
                total = sum(weights)
                if total not in {31, 32, 33}:
                    return False
                cum = 0
                positions = []
                for w in weights:
                    cum += w
                    positions.append(cum)
                if not (16 in positions or (8 in positions and 16 in positions and 24 in positions)):
                    return False
            return True
        if chhand == "savaiya":
            # Example Mattagayand: 7 Bha Ganas + GG = 23 varnas
            for seq in lg_sequences:
                if len(seq) != 23:
                    return False
                gana = self._gana_sequence(seq)
                if gana[:7] != ["Bha"] * 7:
                    return False
                if seq[-2:] != ["G", "G"]:
                    return False
            return True
        return True

    def _matra_weights(self, line: str) -> List[int]:
        lg = self._lg_sequence(line)
        return [1 if x == "L" else 2 for x in lg]

    def _count_matras(self, line: str) -> int:
        """
        Count matras (morae) in a Hindi/Sanskrit line
        Laghu (short) = 1 matra, Guru (long) = 2 matras
        """
        if not line:
            return 0

        # Clean line from Vedic accents and other marks
        line = re.sub(r"[\u0951-\u0954]", "", line)  # Vedic svaras
        line = line.replace("ᳪ", "ं")  # Anusvara variant

        count = 0
        words = line.split()

        for word in words:
            word_matras = 0
            chars = list(word)
            i = 0
            while i < len(chars):
                char = chars[i]

                # Default matra for a character
                m = 1

                # Check for Guru (Long) vowels/matras
                if char in self.guru_vowels:
                    m = 2
                elif char in self.guru_signs:
                    m = 2
                elif char in self.anusvara_visarga:
                    m = 1  # Adds to previous

                # Conjunct consonant (Samyukta Akshara) rule:
                # Syllable before a conjunct becomes Guru
                if i + 1 < len(chars) and chars[i + 1] == self.virama:
                    m = 2

                word_matras += m
                i += 1

            count += word_matras

        # Fallback estimation if zero
        if count == 0:
            count = len(re.findall(r"[\u0900-\u097F]", line))

        return count

    def _rhymes_with(self, word1: str, word2: str) -> bool:
        """Simple end-syllable rhyme check for Hindi (Devanagari)."""
        if not word1 or not word2:
            return False
        from app.services.phonology_resources import get_phonology

        phon = get_phonology("hi")
        part1 = phon.rhyme_key(word1)
        part2 = phon.rhyme_key(word2)
        return bool(part1 and part2 and part1 == part2)

    def _end_syllable_pattern(self, word: str) -> Optional[str]:
        """Return end-syllable pattern for Antyanuprasa density."""
        if not word:
            return None
        from app.services.phonology_resources import get_phonology

        phon = get_phonology("hi")
        return phon.rhyme_key(word)

    def _detect_chhand(self, matra_counts: List[int]) -> Optional[str]:
        """Detect chhand type from matra counts"""
        if not matra_counts:
            return None
        for chhand, pattern in self.chhand_patterns.items():
            expected = pattern["matra"]
            if chhand in {"doha", "soratha", "barvai"}:
                ok = True
                for line in self.lines:
                    if not self._line_matches_matra_pattern(line, expected):
                        ok = False
                        break
                if ok:
                    return chhand
            else:
                if all(m == expected[0] for m in matra_counts):
                    return chhand
        return "free_verse"

    def _line_matches_matra_pattern(self, line: str, targets: List[int]) -> bool:
        weights = self._matra_weights(line)
        idx = 0
        for t in targets:
            total = 0
            while idx < len(weights) and total < t:
                total += weights[idx]
                idx += 1
            if total != t:
                return False
        return True


class UrduProsodyAnalyzer:
    """
    Analyze Urdu poetry (Aruz/Bahr system)
    Implements Mutaqaarib, Hazaj, Ramal, Kaamil, Mujtass
    """

    def __init__(self) -> None:
        self.bahr_patterns = _load_json(_DATA_DIR / "bahr_patterns.json")
        self.rules = _load_json(_DATA_DIR / "urdu_aruz_rules.json")
        symbols = self.rules.get("symbols", {})
        self.sym_short = symbols.get("short", "˘")
        self.sym_long = symbols.get("long", "—")
        self.sym_overlong = symbols.get("overlong", "—˘")
        self.length_markers = set(self.rules.get("length_markers", []))
        self.ignore_chars = set(self.rules.get("ignore_chars", []))

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze Urdu text for bahr (meter)"""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        limits = get_output_limits()

        # Syllable weight analysis (Taqti)
        syllable_patterns = []
        line_details: List[Dict[str, Any]] = []
        for line in lines:
            pattern, details = self._taqti_line(line)
            syllable_patterns.append(pattern)
            line_details.append(details)

        # Detect bahr using DFA-style exact matching
        detected_bahr, score = self._detect_bahr(syllable_patterns)

        syllable_limit = limits.get("urdu_syllable_patterns") if limits else None
        syllable_patterns_out = (
            syllable_patterns[: int(syllable_limit)]
            if syllable_limit is not None
            else syllable_patterns
        )

        return {
            "detected_bahr": detected_bahr,
            "bahr_score": round(score, 3),
            "syllable_patterns": syllable_patterns_out,
            "taqti": line_details,
            "bahr_description": self.bahr_patterns.get(detected_bahr, {}).get(
                "description"
            )
            if detected_bahr
            else None,
        }

    def _taqti_line(self, line: str) -> Tuple[str, Dict[str, Any]]:
        tokens = re.findall(r"[\u0600-\u06FF']+", line)
        phon = get_phonology("ur")
        ipa_words = []
        for word in tokens:
            ipa = phon.ipa(word)
            if ipa:
                ipa_words.append(ipa)
            else:
                ipa_words.append(word)

        ipa_line = " ".join(ipa_words).strip()
        syllables = syllabify_ipa(ipa_line)
        weights = [self._syllable_weight(syl) for syl in syllables]
        pattern = "".join(weights) if weights else "unknown"
        return pattern, {
            "line": line,
            "ipa": ipa_line,
            "syllables": syllables,
            "weights": weights,
            "pattern": pattern,
        }

    def _syllable_weight(self, syllable: str) -> str:
        if not syllable:
            return self.sym_short
        vowel_positions = [i for i, ch in enumerate(syllable) if ch in IPA_VOWELS]
        if not vowel_positions:
            return self.sym_short
        vpos = vowel_positions[0]
        long_vowel = False
        if vpos + 1 < len(syllable) and syllable[vpos + 1] in self.length_markers:
            long_vowel = True
        coda = False
        for ch in syllable[vpos + 1 :]:
            if ch in self.ignore_chars:
                continue
            if ch not in IPA_VOWELS:
                coda = True
                break
        if long_vowel and coda:
            return self.sym_overlong
        if long_vowel or coda:
            return self.sym_long
        return self.sym_short

    def _tokenize_pattern(self, pattern: str) -> List[str]:
        compact = pattern.replace(" ", "")
        tokens: List[str] = []
        i = 0
        while i < len(compact):
            if compact[i : i + 2] == self.sym_overlong:
                tokens.append(self.sym_overlong)
                i += 2
            else:
                tokens.append(compact[i])
                i += 1
        return tokens

    def _dfa_match(self, tokens: List[str], target: List[str]) -> bool:
        if not tokens or not target:
            return False
        state = 0
        for tok in tokens:
            if state >= len(target):
                return False
            if tok == target[state]:
                state += 1
            else:
                return False
        return state == len(target)

    def _detect_bahr(self, patterns: List[str]) -> Tuple[Optional[str], float]:
        """Detect bahr from syllable patterns (Taqti DFA match)"""
        if not patterns:
            return None, 0.0

        normalized = [p.replace(" ", "") for p in patterns if p and p != "unknown"]
        if not normalized:
            return None, 0.0

        best_bahr = None
        best_score = 0.0
        for bahr, info in self.bahr_patterns.items():
            target_tokens = self._tokenize_pattern(info["pattern"])
            matches = 0
            total = 0
            for p in normalized:
                tokens = self._tokenize_pattern(p)
                total += 1
                if self._dfa_match(tokens, target_tokens):
                    matches += 1
            score = matches / total if total else 0.0
            if score > best_score:
                best_score = score
                best_bahr = bahr

        return best_bahr, best_score


class GujaratiProsodyAnalyzer:
    """
    Analyze Gujarati prosody
    Shares matra system with Hindi, includes Garbi, Raas forms
    """

    def __init__(self) -> None:
        self.gujarati_chhands = _load_json(_DATA_DIR / "gujarati_chhands.json")
        signs = _load_json(_DATA_DIR / "gujarati_signs.json")
        self.gujarati_laghu = set(signs.get("laghu", []))
        self.gujarati_guru = set(signs.get("guru", []))

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze Gujarati text for chhand"""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        matra_counts = []
        for line in lines:
            matra = self._count_matras_gujarati(line)
            matra_counts.append(matra)

        detected_form = self._detect_form(matra_counts)

        return {
            "detected_form": detected_form,
            "matra_counts": matra_counts,
            "form_description": self.gujarati_chhands.get(detected_form, {}).get(
                "description"
            )
            if detected_form
            else None,
        }

    def _count_matras_gujarati(self, line: str) -> int:
        """Count matras in Gujarati text"""
        count = 0
        for char in line:
            if char in self.gujarati_laghu:
                count += 1
            elif char in self.gujarati_guru:
                count += 2
            elif ord(char) in range(0x0A80, 0x0AFF):
                count += 1

        return max(1, count)

    def _detect_form(self, matra_counts: List[int]) -> Optional[str]:
        """Detect Gujarati poetic form"""
        if not matra_counts:
            return None

        for form, pattern in self.gujarati_chhands.items():
            expected = pattern["matra"]
            if len(matra_counts) >= len(expected):
                if all(
                    abs(m - e) <= 2
                    for m, e in zip(matra_counts[: len(expected)], expected)
                ):
                    return form

        return "free_verse"


def detect_poem_form(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Detect the form/structure of a poem
    Comprehensive form detection for multiple languages
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if not lines:
        return {"detected_forms": [], "confidence": 0}

    # Analyze with prosody analyzer
    analyzer = ProsodyAnalyzer(language)
    prosody_result = analyzer.analyze(text)

    # Form detection heuristics
    form_info = {"detected_forms": []}

    def _syllables_in_line(line: str) -> int:
        phon = get_phonology(language)
        words = re.findall(r"[A-Za-z\u0600-\u06FF\u0900-\u097F\u0A80-\u0AFF']+", line)
        count = 0
        for word in words:
            ipa = phon.ipa(word)
            if ipa:
                vcount = count_syllables_from_ipa(ipa)
                if vcount:
                    count += vcount
            else:
                # Fallback: English syllable lib or script-based vowel count
                if language == "en":
                    count += max(1, syllables.estimate(word))
                else:
                    count += fallback_syllable_count(word, language)
        return count if count > 0 else 0

    form_rules = get_form_rules()
    haiku = form_rules.get("haiku", {})
    if haiku:
        min_lines = int(haiku.get("min_lines", 3))
        max_lines = int(haiku.get("max_lines", 3))
        if min_lines <= len(lines) <= max_lines:
            syllable_counts = [_syllables_in_line(line) for line in lines]
            target = haiku.get("syllable_pattern", HAIKU_SYLLABLES if HAIKU_SYLLABLES else [5, 7, 5])
            tolerance = int(haiku.get("syllable_tolerance", 1))
            if syllable_counts == target or all(
                abs(s - e) <= tolerance for s, e in zip(syllable_counts, target)
            ):
                form_info["detected_forms"].append("haiku")

    # Sonnet: 14 lines
    sonnet = form_rules.get("sonnet", {})
    if sonnet:
        lines_required = int(sonnet.get("lines", 14))
        if len(lines) == lines_required:
            rhyme = prosody_result.get("rhyme", {})
            scheme = rhyme.get("detected_scheme", "")
            if any(tag in scheme for tag in sonnet.get("rhyme_contains", [])):
                form_info["detected_forms"].append("sonnet")

    # Villanelle: 19 lines with refrains
    villanelle = form_rules.get("villanelle", {})
    if villanelle:
        lines_required = int(villanelle.get("lines", 19))
        if len(lines) == lines_required:
            form_info["detected_forms"].append("villanelle")

    # Ghazal: Minimum 5 couplets, AA BA CA scheme
    ghazal = form_rules.get("ghazal", {})
    if ghazal:
        min_lines = int(ghazal.get("min_lines", 10))
        even_only = bool(ghazal.get("even_lines_only", True))
        requires_matla = bool(ghazal.get("requires_matla", True))
        if len(lines) >= min_lines and (len(lines) % 2 == 0 if even_only else True):
            rhyme = prosody_result.get("rhyme", {})
            scheme = rhyme.get("detected_scheme", "")
            if (not requires_matla) or (scheme and scheme[0] == scheme[1]):
                form_info["detected_forms"].append("ghazal")

    # Doha: 2 lines, 13+11 matras
    if len(lines) == 2 and language in ["hi", "mr", "bn"]:
        hindi_analyzer = HindiProsodyAnalyzer()
        result = hindi_analyzer.analyze(text)
        if result.get("detected_chhand") == "doha":
            form_info["detected_forms"].append("doha")

    # Free verse (default)
    if not form_info["detected_forms"]:
        form_info["detected_forms"].append("free_verse")

    form_info["confidence"] = 0.8 if len(form_info["detected_forms"]) == 1 else 0.5
    form_info["prosody_summary"] = prosody_result

    return form_info
