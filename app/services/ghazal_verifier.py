"""
Ghazal Structure Verifier
Complete ghazal validation with Matla, Maqta, Qaafiya, Radif
Based on quantitative_poetry_metrics.md Section 4.3
"""

import re
from typing import Dict, List, Any, Optional, Tuple


class GhazalVerifier:
    """
    Verify ghazal structure according to classical rules
    
    From quantitative_poetry_metrics.md:
    - Radif: Exact repetition at end of every second misra
    - Qaafiya: Rhyming word(s) before Radif
    - Matla: Opening couplet where both lines end with Radif+Qaafiya
    - Maqta: Final couplet with poet's pen name (takhallus)
    - Minimum 5 couplets
    """

    def __init__(self):
        self.text = ""
        self.lines: List[str] = []
        self.couplets: List[Tuple[str, str]] = []

    def verify(self, text: str) -> Dict[str, Any]:
        """Verify ghazal structure"""
        self.text = text
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Group into couplets (sher)
        self.couplets = self._group_into_couplets()
        
        if len(self.couplets) < 5:
            return {
                "is_valid_ghazal": False,
                "reason": f"Insufficient couplets: {len(self.couplets)} (minimum 5 required)",
                "couplet_count": len(self.couplets)
            }
        
        # Extract Radif and Qaafiya
        radif, qaafiya = self._extract_radif_qaafiya()
        
        # Verify Matla
        matla_valid = self._verify_matla(radif, qaafiya)
        
        # Verify Radif consistency
        radif_valid = self._verify_radif_consistency(radif)
        
        # Verify Qaafiya
        qaafiya_valid = self._verify_qaafiya(qaafiya)
        
        # Check for Maqta
        maqta_info = self._check_for_maqta()
        
        # Calculate Qaafiya density
        qaafiya_density = self._calculate_qaafiya_density()
        
        # Overall validation
        is_valid = (
            len(self.couplets) >= 5 and
            matla_valid and
            radif_valid and
            qaafiya_valid
        )
        
        return {
            "is_valid_ghazal": is_valid,
            "couplet_count": len(self.couplets),
            "matla_valid": matla_valid,
            "radif_valid": radif_valid,
            "qaafiya_valid": qaafiya_valid,
            "radif": radif,
            "qaafiya": qaafiya,
            "qaafiya_density": round(qaafiya_density, 3),
            "maqta": maqta_info,
            "scheme": self._get_ghazal_scheme(),
            "analysis": "Classical ghazal structure verification"
        }

    def _group_into_couplets(self) -> List[Tuple[str, str]]:
        """Group lines into couplets (sher)"""
        couplets = []
        
        # Ghazal typically has 2 lines per sher
        for i in range(0, len(self.lines) - 1, 2):
            first_misra = self.lines[i]
            second_misra = self.lines[i + 1]
            couplets.append((first_misra, second_misra))
        
        return couplets

    def _extract_radif_qaafiya(self) -> Tuple[Optional[str], Optional[str]]:
        """Extract Radif (refrain) and Qaafiya (rhyme)"""
        if not self.couplets:
            return None, None
        
        # Get ending of first couplet's second line
        first_couplets_second = self.couplets[0][1]
        words = first_couplets_second.split()
        
        if not words:
            return None, None
        
        # Try to identify Radif (repeated phrase)
        # Look for repeated ending across couplets
        endings = []
        for _, second_misra in self.couplets[:5]:  # Check first 5 couplets
            words = second_misra.split()
            if words:
                endings.append(words[-3:])  # Last 3 words
        
        # Find common ending (Radif)
        radif = self._find_common_ending(endings)
        
        # Qaafiya is the word before Radif
        qaafiya = None
        if radif:
            words_before_radif = first_couplets_second.split()
            radif_word_count = len(radif.split())
            if len(words_before_radif) > radif_word_count:
                qaafiya = words_before_radif[-(radif_word_count + 1)]
        
        return radif, qaafiya

    def _find_common_ending(self, endings: List[List[str]]) -> Optional[str]:
        """Find common ending phrase across lines"""
        if not endings:
            return None
        
        # Start with last word
        common = endings[0][-1:]
        
        # Check if all endings have this
        for ending in endings[1:]:
            if not ending or ending[-1] != common[-1]:
                return " ".join(common[:-1]) if len(common) > 1 else None
        
        # Try to extend common ending
        min_len = min(len(e) for e in endings)
        for i in range(2, min_len + 1):
            phrase = endings[0][-i:]
            if all(e[-i:] == phrase for e in endings):
                common = phrase
            else:
                break
        
        return " ".join(common)

    def _verify_matla(self, radif: Optional[str], qaafiya: Optional[str]) -> bool:
        """Verify Matla (opening couplet)"""
        if not self.couplets or not radif:
            return False
        
        first_couplet = self.couplets[0]
        
        # Both lines of Matla should end with Radif+Qaafiya
        first_ends_with = self._ends_with_radif(first_couplet[0], radif)
        second_ends_with = self._ends_with_radif(first_couplet[1], radif)
        
        return first_ends_with and second_ends_with

    def _verify_radif_consistency(self, radif: Optional[str]) -> bool:
        """Verify Radif appears in all second lines"""
        if not radif or not self.couplets:
            return False
        
        for _, second_misra in self.couplets[1:]:  # Skip Matla
            if not self._ends_with_radif(second_misra, radif):
                return False
        
        return True

    def _verify_qaafiya(self, qaafiya: Optional[str]) -> bool:
        """Verify Qaafiya consistency"""
        if not qaafiya or not self.couplets:
            return True  # Some ghazals are ghair-muraddaf (without radif)
        
        matches = 0
        for first_misra, second_misra in self.couplets:
            if qaafiya in first_misra or qaafiya in second_misra:
                matches += 1
        
        return matches >= len(self.couplets) * 0.8  # 80% consistency

    def _ends_with_radif(self, line: str, radif: str) -> bool:
        """Check if line ends with radif"""
        return line.strip().endswith(radif.strip())

    def _check_for_maqta(self) -> Dict[str, Any]:
        """Check for Maqta (final couplet with takhallus)"""
        if not self.couplets:
            return {"present": False}
        
        last_couplet = self.couplets[-1]
        combined = f"{last_couplet[0]} {last_couplet[1]}".lower()
        
        # Common takhallus markers
        takhallus_markers = ["mir", "ghalib", "daagh", "faiz", "iqbal", "momin", "zauq"]
        
        found_takhallus = None
        for marker in takhallus_markers:
            if marker in combined:
                found_takhallus = marker
                break
        
        return {
            "present": found_takhallus is not None,
            "takhallus": found_takhallus,
            "is_final_couplet": True
        }

    def _calculate_qaafiya_density(self) -> float:
        """Calculate Qaafiya density"""
        if not self.couplets:
            return 0.0
        
        radif, qaafiya = self._extract_radif_qaafiya()
        if not qaafiya:
            return 0.0
        
        matches = sum(
            1 for first, second in self.couplets
            if qaafiya in first or qaafiya in second
        )
        
        return matches / len(self.couplets)

    def _get_ghazal_scheme(self) -> str:
        """Get ghazal rhyme scheme"""
        if not self.couplets:
            return ""
        
        radif, qaafiya = self._extract_radif_qaafiya()
        
        if radif:
            return f"AA BA CA... (Radif: {radif})"
        else:
            return "Free scheme (no Radif)"


def verify_ghazal(text: str) -> Dict[str, Any]:
    """Standalone function to verify ghazal"""
    verifier = GhazalVerifier()
    return verifier.verify(text)
