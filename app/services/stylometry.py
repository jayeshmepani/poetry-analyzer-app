"""
Stylometry Analysis Module
Authorial style stats, lexical richness, and syntactic fingerprints
"""

import string
from typing import Dict, Any, List
from collections import Counter
import math

class StylometryAnalyzer:
    """
    Analyzes text for authorial stylistic fingerprints (Stylometry).
    """

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run stylometric analysis."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Clean text preserving some punctuation
        words_raw = text.split()
        words = [w.lower().strip(string.punctuation) for w in words_raw if w.strip(string.punctuation)]
        
        if not words:
            return {
                "ttr": 0.0,
                "hapax_legomena_ratio": 0.0,
                "avg_sentence_len": 0.0,
                "punctuation_frequencies": {},
                "unique_words_count": 0,
                "total_words": 0
            }

        word_counts = Counter(words)
        
        # 1. Type-Token Ratio (TTR)
        unique_words = len(word_counts)
        total_words = len(words)
        ttr = unique_words / total_words

        # 2. Hapax Legomena (Words occurring exactly once)
        hapax_count = sum(1 for w, c in word_counts.items() if c == 1)
        hapax_ratio = hapax_count / total_words

        # 3. Yule's K Characteristic (Lexical richness, robust to text length)
        # K = 10^4 * (sum(f_r * r^2) - N) / N^2
        freq_spectrum = Counter(word_counts.values())
        sum_r2_fr = sum((r ** 2) * fr for r, fr in freq_spectrum.items())
        if total_words > 1:
            yules_k = 10000 * (sum_r2_fr - total_words) / (total_words ** 2)
        else:
            yules_k = 0.0

        # 4. Sentence Length Variance
        # Assuming lines approximate syntactic boundaries in poetry if no strong punctuation
        sentences = [s.strip() for s in text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        if not sentences:
            sentences = lines # Fallback to lines if no terminal punctuation
            
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_len = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        if len(sentence_lengths) > 1:
            variance = sum((length - avg_sentence_len) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        else:
            variance = 0.0

        # 5. Punctuation Frequencies
        punct_counts = Counter(c for c in text if c in string.punctuation)
        punct_freq = {k: v / max(1, len(text)) for k, v in punct_counts.items() if k in ",.;:!?-"}

        return {
            "ttr": round(ttr, 3),
            "hapax_legomena_ratio": round(hapax_ratio, 3),
            "yules_k": round(yules_k, 2),
            "avg_sentence_len": round(avg_sentence_len, 2),
            "sentence_length_variance": round(variance, 2),
            "punctuation_frequencies": {k: round(v * 100, 2) for k, v in punct_freq.items()},
            "unique_words_count": unique_words,
            "total_words": total_words
        }

def analyze_stylometry(text: str) -> Dict[str, Any]:
    """Standalone function to run stylometric logic"""
    analyzer = StylometryAnalyzer()
    return analyzer.analyze(text)
