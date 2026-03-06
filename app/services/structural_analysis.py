"""
Structural Analysis Module
Golden Ratio, Fibonacci, and mathematical structure detection
Based on quantitative_poetry_metrics.md Section 4.2
"""

import math
import json
from pathlib import Path
import syllables
from typing import Dict, List, Any, Optional
from app.services.rule_loader import get_structural_rules
from app.services.phonology_resources import (
    get_phonology,
    count_syllables_from_ipa,
)


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "constraints"
FIBONACCI_STRUCTURAL = _load_json(_DATA_DIR / "fibonacci_structural.json")


class StructuralAnalyzer:
    """
    Analyze mathematical structures in poetry
    Golden Ratio, Fibonacci sequence, and proportional analysis
    """

    def __init__(self):
        self.text = ""
        self.lines: List[str] = []
        rules = get_structural_rules()
        self.golden_ratio = rules.get("golden_ratio") if rules else None

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete structural analysis"""
        self.text = text
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]

        return {
            "golden_ratio": self._analyze_golden_ratio(),
            "fibonacci": self._analyze_fibonacci(),
            "proportions": self._analyze_proportions(),
            "symmetry": self._analyze_symmetry()
        }

    def _analyze_golden_ratio(self) -> Dict[str, Any]:
        """
        Analyze Golden Ratio (φ ≈ 1.618) in poem structure
        
        From quantitative_poetry_metrics.md:
        - Golden Ratio appears in volta placement
        - Often at line ≈ 0.618 of total line count
        - Most aesthetically pleasing point for shift in logic
        """
        rules = get_structural_rules()
        total_lines = len(self.lines)
        if not rules:
            return {"present": False, "reason": "Missing structural rules"}
        min_lines = rules.get("min_lines_for_golden")
        golden_fraction = rules.get("golden_ratio_fraction")
        if min_lines is None or golden_fraction is None or total_lines < int(min_lines):
            return {"present": False, "reason": "Insufficient lines"}

        # Calculate golden section points
        golden_section_line = int(total_lines * (1 - float(golden_fraction)))
        golden_section_line_alt = int(total_lines * float(golden_fraction))

        # Strict: golden shift only if stanza break occurs exactly at golden section line
        has_golden_shift = self._detect_shift_at_line(golden_section_line)

        return {
            "present": has_golden_shift,
            "golden_section_line": golden_section_line,
            "golden_section_line_alt": golden_section_line_alt,
            "total_lines": total_lines,
            "golden_ratio_position": round((1 - float(golden_fraction)) * 100, 1),
            "has_shift_at_golden_point": has_golden_shift,
            "analysis": f"Golden ratio analysis for {total_lines}-line poem"
        }

    def _analyze_fibonacci(self) -> Dict[str, Any]:
        """
        Analyze Fibonacci sequence in poem structure
        
        From quantitative_poetry_metrics.md:
        - Syllables per line follow Fibonacci: 1, 1, 2, 3, 5, 8, 13...
        - Minimum 6 lines
        """
        fibonacci_sequence = FIBONACCI_STRUCTURAL if FIBONACCI_STRUCTURAL else []

        # Count syllables per line (IPA-driven when available)
        syllable_counts = []
        phon = get_phonology("en")
        for line in self.lines:
            words = line.split()
            syllable_total = 0
            for word in words:
                ipa = phon.ipa(word)
                if ipa:
                    count = count_syllables_from_ipa(ipa)
                    if count:
                        syllable_total += count
                        continue
                syllable_total += self._count_syllables_simple(word)
            syllable_counts.append(syllable_total)

        # Strict Fibonacci compliance (exact match, minimum 6 lines)
        is_fibonacci = self._matches_fibonacci(syllable_counts, fibonacci_sequence)
        has_fibonacci_pattern = is_fibonacci
        compliance = self._calculate_fibonacci_compliance(syllable_counts, fibonacci_sequence)

        return {
            "is_fibonacci_poem": is_fibonacci,
            "has_fibonacci_pattern": has_fibonacci_pattern,
            "syllable_counts": syllable_counts,
            "fibonacci_sequence": fibonacci_sequence[:len(syllable_counts)],
            "compliance_score": round(compliance, 3),
            "total_lines": len(self.lines),
            "analysis": "Fibonacci sequence analysis"
        }

    def _analyze_proportions(self) -> Dict[str, Any]:
        """Analyze various proportional relationships"""
        rules = get_structural_rules()
        total_lines = len(self.lines)
        if not rules:
            return {}
        min_lines = rules.get("min_lines_for_golden")
        if min_lines is None or total_lines < int(min_lines):
            return {}

        # Stanza proportions
        stanzas = self._detect_stanzas()
        stanza_ratios = []
        for i in range(len(stanzas) - 1):
            if len(stanzas[i]) > 0 and len(stanzas[i+1]) > 0:
                ratio = len(stanzas[i]) / len(stanzas[i+1])
                stanza_ratios.append(ratio)

        # Line length proportions
        line_lengths = [len(l.split()) for l in self.lines]
        if len(line_lengths) >= 2:
            avg_first_half = sum(line_lengths[:len(line_lengths)//2]) / (len(line_lengths)//2)
            avg_second_half = sum(line_lengths[len(line_lengths)//2:]) / (len(line_lengths) - len(line_lengths)//2)
            proportion_ratio = avg_first_half / avg_second_half if avg_second_half > 0 else 0
        else:
            proportion_ratio = 0

        return {
            "stanza_count": len(stanzas),
            "stanza_ratios": stanza_ratios,
            "line_proportion_ratio": round(proportion_ratio, 3),
            "has_balanced_proportions": (
                (rules.get("balance_ratio_min") <= proportion_ratio <= rules.get("balance_ratio_max"))
                if rules and proportion_ratio > 0 and rules.get("balance_ratio_min") is not None
                and rules.get("balance_ratio_max") is not None
                else False
            )
        }

    def _analyze_symmetry(self) -> Dict[str, Any]:
        """Analyze symmetry in poem structure"""
        rules = get_structural_rules()
        total_lines = len(self.lines)
        if not rules:
            return {"symmetric": False}
        min_lines = rules.get("min_lines_for_golden")
        if min_lines is None or total_lines < int(min_lines):
            return {"symmetric": False}

        # Check for line length symmetry
        line_lengths = [len(l.split()) for l in self.lines]
        
        # Palindromic symmetry (first line = last line, etc.)
        is_palindromic = all(
            line_lengths[i] == line_lengths[-(i+1)]
            for i in range(len(line_lengths) // 2)
        )

        # Check for rhyme symmetry
        rhyme_scheme = self._extract_rhyme_scheme()
        is_symmetric_rhyme = self._is_symmetric_scheme(rhyme_scheme)

        # Calculate overall symmetry score
        if rules:
            w_pal = rules.get("symmetry_weight_palindrome")
            w_rhyme = rules.get("symmetry_weight_rhyme")
        else:
            w_pal = None
            w_rhyme = None
        if w_pal is None or w_rhyme is None:
            return {
                "is_symmetric": False,
                "symmetry_score": 0.0,
                "is_palindromic": is_palindromic,
                "is_rhyme_symmetric": is_symmetric_rhyme,
                "line_length_symmetry": is_palindromic,
                "rhyme_scheme": rhyme_scheme
            }
        symmetry_score = (is_palindromic * float(w_pal)) + (is_symmetric_rhyme * float(w_rhyme))

        return {
            "is_symmetric": symmetry_score > float(rules.get("symmetry_threshold")) if rules and rules.get("symmetry_threshold") is not None else False,
            "symmetry_score": round(symmetry_score, 3),
            "is_palindromic": is_palindromic,
            "is_rhyme_symmetric": is_symmetric_rhyme,
            "line_length_symmetry": is_palindromic,
            "rhyme_scheme": rhyme_scheme
        }

    def _count_syllables_simple(self, word: str) -> int:
        """Syllable counter using syllables library (strict input)"""
        word = word.lower().strip()
        if not word:
            return 0
        try:
            return max(1, syllables.estimate(word))
        except Exception:
            return 0

    def _matches_fibonacci(self, counts: List[int], fib: List[int]) -> bool:
        """Check if counts match Fibonacci sequence exactly (min 6 lines)"""
        rules = get_structural_rules()
        if not rules:
            return False
        min_lines = rules.get("min_lines_for_fibonacci")
        if min_lines is None or len(counts) < int(min_lines):
            return False
        for i, count in enumerate(counts):
            if i < len(fib):
                if count != fib[i]:
                    return False
        return True

    def _has_fibonacci_pattern(self, counts: List[int]) -> bool:
        """Strict Fibonacci pattern check (exact recurrence)"""
        rules = get_structural_rules()
        if not rules:
            return False
        min_lines = rules.get("min_lines_for_fib_pattern")
        if min_lines is None or len(counts) < int(min_lines):
            return False
        for i in range(2, len(counts)):
            if counts[i] != counts[i - 1] + counts[i - 2]:
                return False
        return True

    def _calculate_fibonacci_compliance(self, counts: List[int], fib: List[int]) -> float:
        """Calculate strict compliance ratio (exact matches / total)"""
        if not counts:
            return 0.0
        total = min(len(counts), len(fib))
        matches = sum(1 for i in range(total) if counts[i] == fib[i])
        return matches / total if total > 0 else 0.0

    def _detect_stanzas(self) -> List[List[int]]:
        """Detect stanza breaks"""
        stanzas = []
        current_stanza = []
        
        for i, line in enumerate(self.text.split('\n')):
            if line.strip():
                current_stanza.append(i)
            else:
                if current_stanza:
                    stanzas.append(current_stanza)
                    current_stanza = []
        
        if current_stanza:
            stanzas.append(current_stanza)
        
        return stanzas

    def _detect_shift_at_line(self, line_num: int) -> bool:
        """Strict shift: stanza break exactly at given line"""
        stanzas = self._detect_stanzas()
        for stanza in stanzas:
            if stanza and stanza[-1] == line_num - 1:
                return True
        return False

    def _extract_rhyme_scheme(self) -> str:
        """Extract rhyme scheme"""
        if not self.lines:
            return ""
        
        last_words = []
        for line in self.lines:
            words = line.split()
            if words:
                last_words.append(words[-1].lower().strip(".,!?;:'\""))
        
        scheme = []
        rhyme_map = {}
        next_letter = ord('A')
        
        for word in last_words:
            found = False
            for letter, rhyme in rhyme_map.items():
                if self._rhymes_with(word, rhyme):
                    scheme.append(letter)
                    found = True
                    break
            
            if not found:
                letter = chr(next_letter)
                rhyme_map[letter] = word
                scheme.append(letter)
                next_letter += 1
        
        return "".join(scheme)

    def _rhymes_with(self, word1: str, word2: str) -> bool:
        """Check if words rhyme"""
        if not word1 or not word2:
            return False
        from app.services.phonology_resources import get_phonology

        phon = get_phonology("en")
        part1 = phon.rhyme_key(word1)
        part2 = phon.rhyme_key(word2)
        return bool(part1 and part2 and part1 == part2)

    def _is_symmetric_scheme(self, scheme: str) -> bool:
        """Check if rhyme scheme is symmetric"""
        if not scheme:
            return False
        
        # Check for palindromic rhyme scheme (ABBA, etc.)
        return scheme == scheme[::-1]


def analyze_golden_ratio_poetry(text: str) -> Dict[str, Any]:
    """
    Standalone function for golden ratio analysis
    """
    analyzer = StructuralAnalyzer()
    return analyzer.analyze(text)
