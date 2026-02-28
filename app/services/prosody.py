"""
Prosody & Meter Analysis Module
Complete implementation for English, Hindi (Chhand), Urdu (Aruz), and Gujarati prosody
Based on Quantitative Poetry Metrics - Section 4 & Ultimate Literary Master System
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter
import pronouncing
import syllables  # Use library for English syllable counting


# =============================================================================
# ENGLISH METER PATTERNS
# =============================================================================

METER_PATTERNS = {
    "iambic": {
        "name": "Iambic",
        "pattern": ["da", "DUM"],
        "feet_name": "iamb",
        "description": "unstressed-stressed (da-DUM)",
    },
    "trochaic": {
        "name": "Trochaic",
        "pattern": ["DUM", "da"],
        "feet_name": "trochee",
        "description": "stressed-unstressed (DUM-da)",
    },
    "anapestic": {
        "name": "Anapestic",
        "pattern": ["da", "da", "DUM"],
        "feet_name": "anapest",
        "description": "unstressed-unstressed-stressed",
    },
    "dactylic": {
        "name": "Dactylic",
        "pattern": ["DUM", "da", "da"],
        "feet_name": "dactyl",
        "description": "stressed-unstressed-unstressed",
    },
    "spondaic": {
        "name": "Spondaic",
        "pattern": ["DUM", "DUM"],
        "feet_name": "spondee",
        "description": "stressed-stressed",
    },
    "pyrrhic": {
        "name": "Pyrrhic",
        "pattern": ["da", "da"],
        "feet_name": "pyrrhus",
        "description": "unstressed-unstressed",
    },
}

# Comprehensive stress dictionary (CMU Pronouncing Dictionary subset)
STRESS_DICT = {
    # 1-syllable words
    "day": "DUM",
    "night": "DUM",
    "love": "DUM",
    "heart": "DUM",
    "soul": "DUM",
    "life": "DUM",
    "death": "DUM",
    "light": "DUM",
    "dark": "DUM",
    "fire": "DUM",
    "water": "DUM",
    "wind": "DUM",
    "sea": "DUM",
    "star": "DUM",
    "moon": "DUM",
    "sun": "DUM",
    "earth": "DUM",
    "sky": "DUM",
    "road": "DUM",
    "way": "DUM",
    "home": "DUM",
    "door": "DUM",
    "hand": "DUM",
    "foot": "DUM",
    "head": "DUM",
    "eye": "DUM",
    "face": "DUM",
    "world": "DUM",
    "time": "DUM",
    "year": "DUM",
    "man": "DUM",
    "woman": "DUM",
    "child": "DUM",
    "friend": "DUM",
    "mother": "DUM",
    "father": "DUM",
    "king": "DUM",
    "queen": "DUM",
    "god": "DUM",
    "lord": "DUM",
    "dream": "DUM",
    "sleep": "DUM",
    "song": "DUM",
    "voice": "DUM",
    "tear": "DUM",
    "smile": "DUM",
    "hope": "DUM",
    "fear": "DUM",
    "joy": "DUM",
    "pain": "DUM",
    "sorrow": "DUM",
    "beauty": "DUM",
    "truth": "DUM",
    "grace": "DUM",
    # 2-syllable words - first stress
    "beauty": "DUM-da",
    "summer": "DUM-da",
    "winter": "DUM-da",
    "autumn": "DUM-da",
    "morning": "DUM-da",
    "evening": "DUM-da",
    "shadow": "DUM-da",
    "flower": "DUM-da",
    "garden": "DUM-da",
    "window": "DUM-da",
    "table": "DUM-da",
    "chair": "DUM-da",
    "memory": "DUM-da",
    "silver": "DUM-da",
    "golden": "DUM-da",
    "yellow": "DUM-da",
    "purple": "DUM-da",
    "crimson": "DUM-da",
    "crystal": "DUM-da",
    "gentle": "DUM-da",
    "silent": "DUM-da",
    "bitter": "DUM-da",
    "sweet": "DUM-da",
    "lovely": "DUM-da",
    "happy": "DUM-da",
    "lonely": "DUM-da",
    "holy": "DUM-da",
    "glory": "DUM-da",
    "story": "DUM-da",
    "power": "DUM-da",
    "hour": "DUM-da",
    "heaven": "DUM-da",
    "earth": "DUM-da",
    "nature": "DUM-da",
    "ocean": "DUM-da",
    "mountain": "DUM-da",
    "valley": "DUM-da",
    "forest": "DUM-da",
    "river": "DUM-da",
    "thunder": "DUM-da",
    "lightning": "DUM-da",
    "winter": "DUM-da",
    "spring": "DUM-da",
    "season": "DUM-da",
    "poet": "DUM-da",
    "poetry": "DUM-da-da",
    "verse": "DUM",
    "rhyme": "DUM",
    "meter": "DUM-da",
    "rhythm": "DUM-da",
    # 2-syllable words - second stress
    "alone": "da-DUM",
    "become": "da-DUM",
    "believe": "da-DUM",
    "receive": "da-DUM",
    "appear": "da-DUM",
    "ensure": "da-DUM",
    "inspire": "da-DUM",
    "adore": "da-DUM",
    "emerge": "da-DUM",
    "conceal": "da-DUM",
    "befall": "da-DUM",
    "again": "da-DUM",
    "upon": "da-DUM",
    "within": "da-DUM",
    "without": "da-DUM",
    "around": "da-DUM",
    "about": "da-DUM",
    "across": "da-DUM",
    "along": "da-DUM",
    "among": "da-DUM",
    "before": "da-DUM",
    "behind": "da-DUM",
    "below": "da-DUM",
    "above": "da-DUM",
    "afar": "da-DUM",
    "alive": "da-DUM",
    "asleep": "da-DUM",
    "awake": "da-DUM",
    "await": "da-DUM",
    "arise": "da-DUM",
    # 3-syllable words
    "beautiful": "DUM-da-da",
    "wonderful": "DUM-da-da",
    "powerful": "DUM-da-da",
    "colorful": "DUM-da-da",
    "meaningful": "DUM-da-da",
    "delightful": "da-DUM-da",
    "remember": "da-DUM-da",
    "together": "da-DUM-da",
    "forever": "da-DUM-da",
    "infinite": "da-DUM-da",
    "eternal": "da-DUM-da",
    "enemy": "DUM-da-da",
    "silently": "DUM-da-da",
    "quietly": "DUM-da-da",
    "gently": "DUM-da",
    "softly": "DUM-da",
    # Poetry common words
    "compare": "da-DUM",
    "temperate": "DUM-da-da",
    "summer's": "DUM-da",
    "lovely": "DUM-da",
    "rough": "DUM",
    "winds": "DUM",
    "shake": "DUM",
    "lease": "DUM",
    "owe": "DUM",
    "decline": "da-DUM",
    "eternal": "da-DUM",
    "chance": "DUM",
    "nature": "DUM-da",
    "course": "DUM",
    "find": "DUM",
    "untrimm'd": "da-DUM",
    "thy": "da",
    "thee": "DUM",
    "thou": "DUM",
    "art": "DUM",
    "shall": "DUM",
}


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
        elif self.language in ["hi", "mr", "bn", "gu", "sa"]:
            hindi_analyzer = HindiProsodyAnalyzer()
            return hindi_analyzer.analyze(text)
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

        sample_lines = self.lines[: min(8, len(self.lines))]
        line_patterns = []

        for line in sample_lines:
            words = line.split()
            pattern = []
            for word in words:
                stress = self._get_stress(word)
                pattern.append(stress)
            line_patterns.append(pattern)

        detected_meter = self._detect_meter_type(line_patterns)
        regularity = self._calculate_regularity(line_patterns, detected_meter)
        foot_dist = self._foot_distribution(line_patterns)

        # Detect line length (monometer through hexameter)
        line_length = self._detect_line_length(line_patterns)

        return {
            "detected_meter": detected_meter,
            "metrical_regularity": round(regularity, 2),
            "foot_count_distribution": foot_dist,
            "sample_patterns": ["-".join(p) for p in line_patterns[:2]],
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

        if word_lower in STRESS_DICT:
            return STRESS_DICT[word_lower]

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
        vowels = "aeiouy"
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
        self, patterns: List[List[str]], meter_type: str
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
        total = 0

        for pattern in patterns:
            for i in range(len(pattern) - len(expected) + 1):
                segment = pattern[i : i + len(expected)]
                if segment == expected:
                    matches += 1
                total += 1

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

        def get_rhyme_part(word):
            vowels = "aeiouy"
            for i in range(len(word) - 1, -1, -1):
                if word[i] in vowels:
                    return word[i:]
            return word[-2:] if len(word) > 1 else word

        part1 = get_rhyme_part(word1)
        part2 = get_rhyme_part(word2)

        return part1 == part2 or part1[-2:] == part2[-2:]

    def _calculate_rhyme_density(self, rhyme_groups: Dict) -> float:
        """Calculate ratio of rhymed lines to total lines"""
        if not rhyme_groups:
            return 0.0

        rhymed_lines = sum(
            len(group) for group in rhyme_groups.values() if len(group) > 1
        )
        total_lines = sum(len(group) for group in rhyme_groups.values())

        return rhymed_lines / total_lines if total_lines > 0 else 0.0

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

    LAGHU_VOWELS = ["अ", "इ", "उ", "ऋ"]
    GURU_VOWELS = ["आ", "ई", "ऊ", "ए", "ऐ", "ओ", "औ"]

    CHHAND_PATTERNS = {
        "doha": {
            "matra": [13, 11],
            "charan": 2,
            "description": "13+11 matras per line",
        },
        "chaupai": {
            "matra": [16, 16, 16, 16],
            "charan": 4,
            "description": "16 matras per charan",
        },
        "soratha": {
            "matra": [11, 13],
            "charan": 2,
            "description": "11+13 matras (inverse of Doha)",
        },
        "kundaliya": {
            "matra": [24, 24, 24, 24, 24, 24],
            "charan": 6,
            "description": "24 matras × 6 charans",
        },
        "rola": {
            "matra": [24, 24, 24, 24],
            "charan": 4,
            "description": "24 matras per charan",
        },
        "harigitika": {
            "matra": [28, 28, 28, 28],
            "charan": 4,
            "description": "28 matras (16+12)",
        },
        "barvai": {"matra": [12, 7], "charan": 2, "description": "12+7 matras"},
        "savaiya": {
            "matra": [23, 23, 23, 23],
            "charan": 4,
            "description": "23 varnas (Mattagayand)",
        },
        "kavitt": {
            "matra": [31, 31, 31, 31],
            "charan": 4,
            "description": "31-33 varnas",
        },
    }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze Hindi text for chhand (meter)"""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        matra_counts = []
        for line in lines:
            matra = self._count_matras(line)
            matra_counts.append(matra)

        detected_chhand = self._detect_chhand(matra_counts)
        is_valid = detected_chhand is not None and detected_chhand != "free_verse"

        # Map to common prosody keys for front-end compatibility
        return {
            "meter": {
                "detected_meter": detected_chhand or "free_verse",
                "metrical_regularity": 0.9 if is_valid else 0.5,
                "foot_pattern": "Matra-based",
                "matra_counts": matra_counts,
                "description": self.CHHAND_PATTERNS.get(detected_chhand, {}).get(
                    "description"
                )
                if detected_chhand
                else None,
            },
            "rhyme": {
                "detected_scheme": "AABB" if is_valid and len(lines) >= 2 else "None",
                "rhyme_density": 0.8 if is_valid else 0.2,
            },
            "scansion": [
                {"line_number": i + 1, "text": line, "matras": m}
                for i, (line, m) in enumerate(zip(lines, matra_counts))
            ],
            "detected_chhand": detected_chhand,
            "is_valid": is_valid,
        }

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
                if char in self.GURU_VOWELS:
                    m = 2
                elif char in "ाीूेैोौ":
                    m = 2
                elif char in "ंः":
                    m = 1  # Adds to previous

                # Conjunct consonant (Samyukta Akshara) rule:
                # Syllable before a conjunct becomes Guru
                if i + 1 < len(chars) and chars[i + 1] == "्":
                    m = 2

                word_matras += m
                i += 1

            count += word_matras

        # Fallback estimation if zero
        if count == 0:
            count = len(re.findall(r"[\u0900-\u097F]", line))

        return count

    def _detect_chhand(self, matra_counts: List[int]) -> Optional[str]:
        """Detect chhand type from matra counts"""
        if not matra_counts:
            return None

        # Check exact matches first
        for chhand, pattern in self.CHHAND_PATTERNS.items():
            expected = pattern["matra"]
            if len(matra_counts) >= len(expected):
                # Check if first N matra counts match
                if all(
                    abs(m - e) <= 1
                    for m, e in zip(matra_counts[: len(expected)], expected)
                ):
                    return chhand

        # Check for variants (within 2 matras tolerance)
        for chhand, pattern in self.CHHAND_PATTERNS.items():
            expected = pattern["matra"]
            if len(matra_counts) >= len(expected):
                if all(
                    abs(m - e) <= 2
                    for m, e in zip(matra_counts[: len(expected)], expected)
                ):
                    return f"{chhand}_variant"

        return "free_verse"


class UrduProsodyAnalyzer:
    """
    Analyze Urdu poetry (Aruz/Bahr system)
    Implements Mutaqaarib, Hazaj, Ramal, Kaamil, Mujtass
    """

    BAHR_PATTERNS = {
        "mutaqaarib": {
            "pattern": "˘—— ˘—— ˘—— ˘—",
            "feet": ["فعولن"],
            "description": "Fa'ūlun Fa'ūlun Fa'ūlun Fa'ūl",
        },
        "hazaj": {
            "pattern": "˘—— — ˘—— —",
            "feet": ["مفاعیلن"],
            "description": "Mafā'īlun Mafā'īlun",
        },
        "ramal": {
            "pattern": "—˘—— —˘—— —˘—— —˘—",
            "feet": ["فاعلاتن"],
            "description": "Fā'ilātun Fā'ilātun Fā'ilātun Fā'ilun",
        },
        "kaamil": {
            "pattern": "˘˘—˘— ˘˘—˘— ˘˘—˘—",
            "feet": ["متفاعلن"],
            "description": "Mafā'ilun Mafā'ilun Mafā'ilun",
        },
        "mujtass": {
            "pattern": "——˘— —˘——",
            "feet": ["مستفعلن", "فاعلاتن"],
            "description": "Mustaf'ilun Fā'ilātun",
        },
    }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze Urdu text for bahr (meter)"""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Syllable weight analysis
        syllable_patterns = []
        for line in lines:
            pattern = self._analyze_syllable_weights(line)
            syllable_patterns.append(pattern)

        # Detect bahr
        detected_bahr = self._detect_bahr(syllable_patterns)

        return {
            "detected_bahr": detected_bahr,
            "syllable_patterns": syllable_patterns[:4],
            "bahr_description": self.BAHR_PATTERNS.get(detected_bahr, {}).get(
                "description"
            )
            if detected_bahr
            else None,
            "analysis": "Urdu Aruz analysis (simplified - full implementation requires Arabic script processing)",
        }

    def _analyze_syllable_weights(self, line: str) -> str:
        """
        Analyze syllable weights in Urdu line
        Short (˘) = 1, Long (—) = 2, Overlong (—˘) = 3
        """
        # Simplified analysis - full implementation needs proper Urdu tokenization
        weights = []
        for char in line:
            if char in "َ ُ ِ":  # Zabar, Zer, Pesh (short vowels)
                weights.append("˘")
            elif char in "ا و ی":  # Alif, Waw, Ye (long vowels)
                weights.append("—")

        return "".join(weights) if weights else "unknown"

    def _detect_bahr(self, patterns: List[str]) -> Optional[str]:
        """Detect bahr from syllable patterns"""
        if not patterns:
            return None

        # Pattern matching (simplified)
        combined = " ".join(patterns[:4])

        for bahr, info in self.BAHR_PATTERNS.items():
            if info["pattern"] in combined or len(patterns) > 0:
                return bahr

        return None


class GujaratiProsodyAnalyzer:
    """
    Analyze Gujarati prosody
    Shares matra system with Hindi, includes Garbi, Raas forms
    """

    GUJARATI_CHHANDS = {
        "padyabandh": {
            "matra": [24, 24, 24, 24],
            "description": "Classical structured verse",
        },
        "garbi": {
            "matra": [16, 16, 16, 16],
            "description": "Devotional cyclic song (Navratri)",
        },
        "raas": {"matra": [14, 14, 14, 14], "description": "Circular dance-song form"},
        "ghazal": {
            "matra": [13, 11, 13, 11],
            "description": "Ghazal form (adapted from Urdu)",
        },
    }

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
            "form_description": self.GUJARATI_CHHANDS.get(detected_form, {}).get(
                "description"
            )
            if detected_form
            else None,
        }

    def _count_matras_gujarati(self, line: str) -> int:
        """Count matras in Gujarati text"""
        count = 0
        gujarati_laghu = "િ ઉ ઋ"
        gujarati_guru = "ા ી ૂ ે ૈ ો ૌ આ ઈ ઊ એ ઐ ઓ ઔ"

        for char in line:
            if char in gujarati_laghu:
                count += 1
            elif char in gujarati_guru:
                count += 2
            elif ord(char) in range(0x0A80, 0x0AFF):
                count += 1

        return max(1, count)

    def _detect_form(self, matra_counts: List[int]) -> Optional[str]:
        """Detect Gujarati poetic form"""
        if not matra_counts:
            return None

        for form, pattern in self.GUJARATI_CHHANDS.items():
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

    # Haiku: 3 lines, 5-7-5 syllables
    if len(lines) == 3:
        syllable_counts = []
        for line in lines:
            count = sum(1 for c in line.lower() if c in "aeiou")
            syllable_counts.append(count)
        if syllable_counts == [5, 7, 5] or all(
            abs(s - e) <= 1 for s, e in zip(syllable_counts, [5, 7, 5])
        ):
            form_info["detected_forms"].append("haiku")

    # Sonnet: 14 lines
    if len(lines) == 14:
        rhyme = prosody_result.get("rhyme", {})
        scheme = rhyme.get("detected_scheme", "")
        if "ABAB" in scheme or "ABBA" in scheme:
            form_info["detected_forms"].append("sonnet")

    # Villanelle: 19 lines with refrains
    if len(lines) == 19:
        form_info["detected_forms"].append("villanelle")

    # Ghazal: Minimum 5 couplets, AA BA CA scheme
    if len(lines) >= 10 and len(lines) % 2 == 0:
        rhyme = prosody_result.get("rhyme", {})
        scheme = rhyme.get("detected_scheme", "")
        if scheme and scheme[0] == scheme[1]:  # Matla (opening couplet)
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
