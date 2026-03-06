"""
Style, Tone & Register Analysis Service
Delegates to dynamic StyleToneAnalyzer to avoid static lexicons.
"""

from typing import Dict, Any
from app.services.style_analysis import StyleToneAnalyzer as CoreStyleToneAnalyzer


class StyleToneAnalyzer:
    """
    Wrapper delegating to the primary StyleToneAnalyzer with dynamic detection.
    """

    def __init__(self, language: str = "en"):
        self._core = CoreStyleToneAnalyzer(language=language)

    def analyze(self, text: str) -> Dict[str, Any]:
        return self._core.analyze(text)
