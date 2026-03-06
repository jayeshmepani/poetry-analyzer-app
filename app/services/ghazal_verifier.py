"""
Ghazal Structure Verifier
Complete ghazal validation with Matla, Maqta, Qaafiya, Radif
Based on quantitative_poetry_metrics.md Section 4.3
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from app.services.rule_loader import get_ghazal_rules


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
        rules = get_ghazal_rules()
        if not rules:
            return {"is_valid_ghazal": False, "reason": "Missing ghazal rules"}
        min_couplets = rules.get("minimum_couplets")
        if min_couplets is None:
            return {"is_valid_ghazal": False, "reason": "Missing ghazal rule: minimum_couplets"}
        min_couplets = int(min_couplets)
        qaafiya_round = rules.get("qaafiya_density_round")
        if qaafiya_round is None:
            return {"is_valid_ghazal": False, "reason": "Missing ghazal rule: qaafiya_density_round"}
        self.text = text
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Group into couplets (sher)
        self.couplets = self._group_into_couplets()
        
        if len(self.couplets) < min_couplets:
            return {
                "is_valid_ghazal": False,
                "reason": f"Insufficient couplets: {len(self.couplets)} (minimum {min_couplets} required)",
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
        qaafiya_required = rules.get("qaafiya_density_required") if rules else None
        if qaafiya_required is None:
            return {"is_valid_ghazal": False, "reason": "Missing ghazal rule: qaafiya_density_required"}
        is_ghazal_formula = (
            len(self.couplets) >= min_couplets
            and matla_valid
            and radif_valid
            and qaafiya_valid
            and qaafiya_density == float(qaafiya_required)
        )
        
        # Overall validation
        is_valid = is_ghazal_formula
        
        return {
            "is_valid_ghazal": is_valid,
            "couplet_count": len(self.couplets),
            "matla_valid": matla_valid,
            "radif_valid": radif_valid,
            "qaafiya_valid": qaafiya_valid,
            "radif": radif,
            "qaafiya": qaafiya,
            "qaafiya_density": round(qaafiya_density, int(qaafiya_round)),
            "is_ghazal_formula": is_ghazal_formula,
            "maqta": maqta_info,
            "scheme": self._get_ghazal_scheme(),
            "analysis": "Classical ghazal structure verification"
        }

    def _group_into_couplets(self) -> List[Tuple[str, str]]:
        """Group lines into couplets (sher)"""
        couplets = []
        rules = get_ghazal_rules()
        if not rules:
            return couplets
        lines_per_couplet = rules.get("lines_per_couplet")
        if lines_per_couplet is None:
            return couplets
        lines_per_couplet = int(lines_per_couplet)
        
        for i in range(0, len(self.lines) - (lines_per_couplet - 1), lines_per_couplet):
            first_misra = self.lines[i]
            second_misra = self.lines[i + 1] if (i + 1) < len(self.lines) else ""
            couplets.append((first_misra, second_misra))
        
        return couplets

    def _extract_radif_qaafiya(self) -> Tuple[Optional[str], Optional[str]]:
        """Extract Radif (refrain) and Qaafiya (rhyme)"""
        rules = get_ghazal_rules()
        if not rules:
            return None, None
        max_couplets = rules.get("max_couplets_for_radif_check")
        ending_window = rules.get("ending_word_window")
        if max_couplets is None or ending_window is None:
            return None, None
        max_couplets = int(max_couplets)
        ending_window = int(ending_window)
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
        for _, second_misra in self.couplets[:max_couplets]:
            words = second_misra.split()
            if words:
                endings.append(words[-ending_window:])
        
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
        rules = get_ghazal_rules()
        if not rules or rules.get("radif_min_length") is None:
            return None
        min_radif_len = int(rules.get("radif_min_length"))
        for i in range(min_radif_len, min_len + 1):
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
            return True  # ghair-muraddaf case

        from app.services.phonology_resources import get_phonology
        phon = get_phonology("ur")

        base = qaafiya
        matches = 0
        for _, second_misra in self.couplets:
            word = self._qaafiya_of_line(second_misra)
            if word and phon.rhyme_key(word) == phon.rhyme_key(base):
                matches += 1
        return matches == len(self.couplets)

    def _ends_with_radif(self, line: str, radif: str) -> bool:
        """Check if line ends with radif"""
        return line.strip().endswith(radif.strip())

    def _check_for_maqta(self) -> Dict[str, Any]:
        """Check for Maqta (final couplet with takhallus)"""
        if not self.couplets:
            return {"present": False}
        
        last_couplet = self.couplets[-1]
        combined = f"{last_couplet[0]} {last_couplet[1]}".lower()

        found = None
        # Use NER to detect a likely pen name in the final couplet.
        try:
            import spacy
            from app.config import settings
            nlp = spacy.load(settings.spacy.multilingual_model)
            doc = nlp(combined)
            persons = [ent.text for ent in doc.ents if ent.label_ in {"PERSON", "PER"}]
            if persons:
                found = persons[0]
        except Exception:
            found = None

        return {
            "present": found is not None,
            "takhallus": found,
            "is_final_couplet": True
        }

    def _calculate_qaafiya_density(self) -> float:
        """Calculate Qaafiya density"""
        if not self.couplets:
            return 0.0

        radif, qaafiya = self._extract_radif_qaafiya()
        if not qaafiya:
            return 0.0

        from app.services.phonology_resources import get_phonology
        phon = get_phonology("ur")

        base_key = phon.rhyme_key(qaafiya)
        if not base_key:
            return 0.0

        matches = 0
        for _, second_misra in self.couplets:
            word = self._qaafiya_of_line(second_misra)
            if word and phon.rhyme_key(word) == base_key:
                matches += 1
        return matches / len(self.couplets)

    def _qaafiya_of_line(self, line: str) -> Optional[str]:
        radif, _ = self._extract_radif_qaafiya()
        if not radif:
            return None
        words = line.split()
        if not words:
            return None
        radif_words = radif.split()
        if len(words) <= len(radif_words):
            return None
        if " ".join(words[-len(radif_words):]) != radif:
            return None
        return words[-(len(radif_words) + 1)]

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
