"""
Structural Analysis Module
Golden Ratio, Fibonacci, and mathematical structure detection
Based on quantitative_poetry_metrics.md Section 4.2
"""

import math
from typing import Dict, List, Any, Optional


class StructuralAnalyzer:
    """
    Analyze mathematical structures in poetry
    Golden Ratio, Fibonacci sequence, and proportional analysis
    """

    def __init__(self):
        self.text = ""
        self.lines: List[str] = []
        self.golden_ratio = 1.618033988749895

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
        total_lines = len(self.lines)
        if total_lines < 2:
            return {"present": False, "reason": "Insufficient lines"}

        # Calculate golden section points
        golden_section_line = int(total_lines * (1 - 0.618))
        golden_section_line_alt = int(total_lines * 0.618)

        # Check if there's a structural shift at golden ratio point
        has_golden_shift = self._detect_shift_at_line(golden_section_line)

        # Calculate ratio of line lengths
        line_lengths = [len(l.split()) for l in self.lines]
        if len(line_lengths) >= 2:
            max_length = max(line_lengths)
            min_length = min(line_lengths)
            if min_length > 0:
                length_ratio = max_length / min_length
                is_golden = abs(length_ratio - self.golden_ratio) < 0.2
            else:
                length_ratio = 0
                is_golden = False
        else:
            length_ratio = 0
            is_golden = False

        return {
            "present": has_golden_shift or is_golden,
            "golden_section_line": golden_section_line,
            "golden_section_line_alt": golden_section_line_alt,
            "total_lines": total_lines,
            "golden_ratio_position": round((1 - 0.618) * 100, 1),
            "has_shift_at_golden_point": has_golden_shift,
            "length_ratio": round(length_ratio, 3),
            "is_golden_ratio": is_golden,
            "analysis": f"Golden ratio analysis for {total_lines}-line poem"
        }

    def _analyze_fibonacci(self) -> Dict[str, Any]:
        """
        Analyze Fibonacci sequence in poem structure
        
        From quantitative_poetry_metrics.md:
        - Syllables per line follow Fibonacci: 1, 1, 2, 3, 5, 8, 13...
        - Minimum 6 lines
        """
        fibonacci_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

        # Count syllables per line (simplified)
        syllable_counts = []
        for line in self.lines:
            words = line.split()
            # Simplified syllable counting
            syllables = sum(self._count_syllables_simple(word) for word in words)
            syllable_counts.append(syllables)

        # Check if syllable counts match Fibonacci
        is_fibonacci = self._matches_fibonacci(syllable_counts, fibonacci_sequence)

        # Check for Fibonacci-like patterns
        has_fibonacci_pattern = self._has_fibonacci_pattern(syllable_counts)

        # Calculate Fibonacci compliance score
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
        total_lines = len(self.lines)
        if total_lines < 2:
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
            "has_balanced_proportions": 0.8 <= proportion_ratio <= 1.2 if proportion_ratio > 0 else False
        }

    def _analyze_symmetry(self) -> Dict[str, Any]:
        """Analyze symmetry in poem structure"""
        total_lines = len(self.lines)
        if total_lines < 2:
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
        symmetry_score = (
            (is_palindromic * 0.5) +
            (is_symmetric_rhyme * 0.5)
        )

        return {
            "is_symmetric": symmetry_score > 0.5,
            "symmetry_score": round(symmetry_score, 3),
            "is_palindromic": is_palindromic,
            "is_rhyme_symmetric": is_symmetric_rhyme,
            "line_length_symmetry": is_palindromic,
            "rhyme_scheme": rhyme_scheme
        }

    def _count_syllables_simple(self, word: str) -> int:
        """Simple syllable counter"""
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        
        if word.endswith('e') and count > 1:
            count -= 1
        
        return max(1, count)

    def _matches_fibonacci(self, counts: List[int], fib: List[int]) -> bool:
        """Check if counts match Fibonacci sequence"""
        if len(counts) < 3:
            return False
        
        for i, count in enumerate(counts):
            if i < len(fib):
                if abs(count - fib[i]) > 1:  # Allow small variance
                    return False
        return True

    def _has_fibonacci_pattern(self, counts: List[int]) -> bool:
        """Check for Fibonacci-like pattern (each = sum of previous two)"""
        if len(counts) < 3:
            return False
        
        matches = 0
        for i in range(2, len(counts)):
            if counts[i] == counts[i-1] + counts[i-2]:
                matches += 1
        
        return matches >= len(counts) - 2

    def _calculate_fibonacci_compliance(self, counts: List[int], fib: List[int]) -> float:
        """Calculate compliance with Fibonacci pattern"""
        if not counts:
            return 0.0
        
        total_diff = sum(abs(counts[i] - fib[i]) for i in range(min(len(counts), len(fib))))
        max_possible_diff = sum(fib[:len(counts)])
        
        if max_possible_diff == 0:
            return 0.0
        
        return 1.0 - (total_diff / max_possible_diff)

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
        """Detect if there's a thematic/tonal shift at given line"""
        if line_num < 1 or line_num >= len(self.lines):
            return False
        
        # Simplified: check for punctuation or line break
        prev_line = self.lines[line_num - 1] if line_num > 0 else ""
        curr_line = self.lines[line_num]
        
        # Check for punctuation indicating shift
        shift_markers = [".", "!", "?", "—", "..."]
        has_punctuation = any(prev_line.endswith(m) for m in shift_markers)
        
        # Check for line length change
        length_change = abs(len(curr_line.split()) - len(prev_line.split())) > 3
        
        return has_punctuation or length_change

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
        
        vowels = "aeiouy"
        
        def get_ending(word):
            for i in range(len(word) - 1, -1, -1):
                if word[i] in vowels:
                    return word[i:]
            return word[-2:] if len(word) > 1 else word
        
        return get_ending(word1) == get_ending(word2)

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
