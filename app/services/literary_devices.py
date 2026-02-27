"""
Literary Devices Analysis Module
Complete implementation of tropes, schemes, imagery, Sanskrit Alankar, and Rasa theory
Based on Ultimate Literary Master System - Dimension 3
"""

import re
from typing import Dict, List, Tuple, Set, Optional, Any
from collections import Counter


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

    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete literary devices analysis"""
        self.text = text
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]
        self.words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

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
        metaphors = []
        metaphor_patterns = [
            r'\b(\w+)\s+is\s+\w+',
            r'\b(\w+)\s+was\s+\w+',
            r'\b(\w+)\s+becomes?\s+\w+',
            r'\blife\s+(is|was|becomes)\b',
            r'\btime\s+(is|was|becomes)\b',
            r'\bdeath\s+(is|was|becomes)\b',
            r'\blove\s+(is|was|becomes)\b',
            r'\bhope\s+(is|was|becomes)\b',
            r'\bheart\s+(is|was|becomes)\b',
            r'\bsoul\s+(is|was|becomes)\b'
        ]

        for i, line in enumerate(self.lines):
            for pattern in metaphor_patterns:
                matches = re.finditer(pattern, line.lower())
                for match in matches:
                    metaphors.append({
                        "line": line,
                        "line_number": i + 1,
                        "text": match.group(),
                        "type": "direct_metaphor"
                    })

        return metaphors[:15]

    def _detect_simile(self) -> List[Dict[str, Any]]:
        """Detect similes"""
        similes = []
        patterns = [
            r'\blike\s+\w+',
            r'\bas\s+\w+\s+as\b',
            r'\bas\s+\w+\b',
            r'\bthan\s+\w+',
            r'\bresembles?\b',
            r'\bakin\s+to\b',
            r'\bsimilar\s+to\b'
        ]

        for i, line in enumerate(self.lines):
            for pattern in patterns:
                matches = re.finditer(pattern, line.lower())
                for match in matches:
                    similes.append({
                        "line": line,
                        "line_number": i + 1,
                        "phrase": match.group(),
                        "type": "simile"
                    })

        return similes[:15]

    def _detect_personification(self) -> List[Dict[str, Any]]:
        """Detect personification"""
        personifications = []
        human_verbs = [
            "whisper", "shout", "cry", "laugh", "smile", "speak", "talk", "think",
            "feel", "know", "want", "love", "hate", "dance", "run", "walk", "fly",
            "sleep", "wake", "sing", "weep", "mourn", "rejoice", "sigh", "gaze",
            "beckon", "embrace", "kiss", "bless", "curse", "forgive", "remember"
        ]

        nature_words = ["wind", "storm", "rain", "thunder", "lightning", "sun", "moon",
                       "star", "sky", "cloud", "river", "ocean", "sea", "mountain",
                       "tree", "flower", "leaf", "branch", "root", "earth", "fire"]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for verb in human_verbs:
                if verb in line_lower:
                    # Check if subject is non-human
                    for nature in nature_words:
                        if nature in line_lower:
                            personifications.append({
                                "line": line,
                                "line_number": i + 1,
                                "human_verb": verb,
                                "subject": nature,
                                "type": "nature_personification"
                            })

        return personifications[:15]

    def _detect_metonymy(self) -> List[Dict[str, Any]]:
        """Detect metonymy (substitution of associated term)"""
        metonymies = []
        metonymy_dict = {
            "crown": "royalty/monarchy",
            "throne": "monarchy/power",
            "sword": "military/war",
            "pen": "writing/literature",
            "press": "media/newspapers",
            "hollywood": "film industry",
            "wall street": "finance/capitalism",
            "the white house": "US presidency",
            "blue blood": "nobility",
            "silver screen": "cinema",
            "heart": "emotions/love",
            "head": "mind/intellect",
            "hand": "worker/labor",
            "brass": "military officers",
            "bench": "judiciary",
            "bar": "legal profession",
            "pulpit": "clergy",
            "scepter": "royal authority"
        }

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for key, meaning in metonymy_dict.items():
                if key in line_lower:
                    metonymies.append({
                        "line": line,
                        "line_number": i + 1,
                        "term": key,
                        "represents": meaning,
                        "type": "metonymy"
                    })

        return metonymies[:15]

    def _detect_synecdoche(self) -> List[Dict[str, Any]]:
        """Detect synecdoche (part for whole or whole for part)"""
        synecdoches = []
        part_whole = {
            "head": "person",
            "hand": "worker/helper",
            "foot": "soldier/traveler",
            "heart": "emotions/courage",
            "eye": "vision/attention",
            "sail": "ship",
            "wheels": "car/vehicle",
            "glass": "mirror/drinking vessel",
            "roof": "home/shelter",
            "mouth": "person/speaker",
            "tongue": "language/speech",
            "ear": "attention/listening",
            "face": "person",
            "body": "person/corpse",
            "blood": "family/lineage",
            "flesh": "humanity/mortality"
        }

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for part, whole in part_whole.items():
                if re.search(rf'\b{part}s?\b', line_lower):
                    synecdoches.append({
                        "line": line,
                        "line_number": i + 1,
                        "part": part,
                        "represents": whole,
                        "type": "synecdoche"
                    })

        return synecdoches[:15]

    def _detect_hyperbole(self) -> List[Dict[str, Any]]:
        """Detect hyperbole (exaggeration)"""
        hyperboles = []
        extreme_words = [
            "million", "billion", "trillion", "zillion", "infinite", "eternal",
            "forever", "never", "always", "enormous", "immense", "tremendous",
            "colossal", "gigantic", "mammoth", "monstrous", "endless", "boundless",
            "limitless", "countless", "myriad", "ocean", "sea", "mountain", "world",
            "universe", "cosmos", "heaven", "hell", "death", "god", "devil"
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for word in extreme_words:
                if word in line_lower:
                    hyperboles.append({
                        "line": line,
                        "line_number": i + 1,
                        "exaggeration": word,
                        "type": "hyperbole"
                    })

        return hyperboles[:15]

    def _detect_litotes(self) -> List[Dict[str, Any]]:
        """Detect litotes (understatement using negation)"""
        litotes = []
        litotes_patterns = [
            r'not\s+bad',
            r'no\s+small',
            r"isn't\s+bad",
            r'not\s+uncommon',
            r'not\s+unlike',
            r'not\s+without',
            r'no\s+little',
            r'not\s+few',
            r'not\s+least',
            r'no\s+ordinary',
            r'not\s+exactly',
            r'less\s+than',
            r'could\s+be\s+better',
            r'pretty\s+good',
            r'fair\s+enough'
        ]

        for i, line in enumerate(self.lines):
            for pattern in litotes_patterns:
                if re.search(pattern, line.lower()):
                    litotes.append({
                        "line": line,
                        "line_number": i + 1,
                        "type": "understatement",
                        "pattern": pattern
                    })

        return litotes[:15]

    def _detect_irony(self) -> List[Dict[str, Any]]:
        """Detect irony markers"""
        ironies = []
        irony_markers = [
            "little did", "ironically", "amazingly", "of course", "clearly",
            "naturally", "what a", "how", "oh", "alas", "lo", "behold",
            "would you believe", "as if", "yeah right", "sure", "right"
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for marker in irony_markers:
                if marker in line_lower:
                    ironies.append({
                        "line": line,
                        "line_number": i + 1,
                        "marker": marker,
                        "type": "verbal_irony"
                    })

        return ironies[:15]

    def _detect_oxymoron(self) -> List[Dict[str, Any]]:
        """Detect oxymoron (contradictory terms)"""
        oxymorons = []
        oxymora = [
            "deafening silence", "bitter sweet", "living dead", "pretty ugly",
            "small fortune", "free gift", "open secret", "alone together",
            "seriously funny", "original copy", "virtual reality", "act naturally",
            "found missing", "clearly confused", "same difference", "real fake",
            "controlled chaos", "organized mess", "happy sadness", "cruel kindness",
            "dark light", "cold fire", "dry water", "heavy lightness", "wise fool"
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for ox in oxymora:
                if ox in line_lower:
                    oxymorons.append({
                        "line": line,
                        "line_number": i + 1,
                        "oxymoron": ox,
                        "type": "oxymoron"
                    })

        return oxymorons[:15]

    def _detect_paradox(self) -> List[Dict[str, Any]]:
        """Detect paradox (seemingly contradictory truth)"""
        paradoxes = []
        paradox_phrases = [
            "less is more", "more is less", "everything must change",
            "change is constant", "the beginning of the end", "endless beginning",
            "I know nothing", "the only truth is lies", "silence speaks",
            "alone together", "living death", "dying to live", "lost found",
            "wise ignorance", "ignorant wisdom", "strong weakness", "weak strength"
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for phrase in paradox_phrases:
                if phrase in line_lower:
                    paradoxes.append({
                        "line": line,
                        "line_number": i + 1,
                        "paradox": phrase,
                        "type": "paradox"
                    })

        return paradoxes[:15]

    def _detect_apostrophe(self) -> List[Dict[str, Any]]:
        """Detect apostrophe (addressing absent/abstract entities)"""
        apostrophes = []

        for i, line in enumerate(self.lines):
            if re.match(r'^(O|Oh|Hey|Dear|Hail|Welcome)\s+\w+', line, re.IGNORECASE):
                apostrophes.append({
                    "line": line,
                    "line_number": i + 1,
                    "type": "apostrophe"
                })
            # Also detect direct address
            elif re.search(r'\bO\s+\w+\b', line, re.IGNORECASE):
                apostrophes.append({
                    "line": line,
                    "line_number": i + 1,
                    "type": "apostrophe"
                })

        return apostrophes[:15]

    def _detect_synesthesia(self) -> List[Dict[str, Any]]:
        """Detect synesthesia (mixing senses)"""
        synesthesias = []
        syn_phrases = [
            "loud color", "loud colors", "sweet music", "sweet sound",
            "bitter cold", "soft sound", "warm voice", "cold voice",
            "colorful sound", "musical color", "bright sound", "dark taste",
            "smooth taste", "rough sound", "sharp taste", "heavy color",
            "light sound", "quiet color", "noisy color", "fragrant color"
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for phrase in syn_phrases:
                if phrase in line_lower:
                    synesthesias.append({
                        "line": line,
                        "line_number": i + 1,
                        "phrase": phrase,
                        "type": "synesthesia"
                    })

        return synesthesias[:15]

    def _detect_euphemism(self) -> List[Dict[str, Any]]:
        """Detect euphemisms"""
        euphemisms = []
        euphemism_dict = {
            "passed away": "died", "departed": "died", "passed on": "died",
            "let go": "fired", "between jobs": "unemployed", "downsized": "fired",
            "expecting": "pregnant", "in a better place": "dead", "sleeping": "dead",
            "adult beverages": "alcohol", "pre-owned": "used", "collateral damage": "civilian casualties",
            "passed over": "ignored", "correctional facility": "prison", "put to sleep": "euthanized",
            "friendly fire": "accidental attack on allies"
        }

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for eu, meaning in euphemism_dict.items():
                if eu in line_lower:
                    euphemisms.append({
                        "line": line,
                        "line_number": i + 1,
                        "euphemism": eu,
                        "meaning": meaning,
                        "type": "euphemism"
                    })

        return euphemisms[:15]

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
                    if first_letters[j] == first_letters[j+1] and first_letters[j] in 'bcdfghjklmnpqrstvwxyz':
                        alliterations.append({
                            "line": line,
                            "line_number": i + 1,
                            "letter": first_letters[j],
                            "words": [words[j], words[j+1]],
                            "type": "alliteration"
                        })

        return alliterations[:15]

    def _detect_anaphora(self) -> List[Dict[str, Any]]:
        """Detect anaphora (repetition at beginning)"""
        anaphoras = []

        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].lower().split()
            words2 = self.lines[i+1].lower().split()

            if words1 and words2 and words1[0] == words2[0] and len(words1[0]) > 2:
                anaphoras.append({
                    "lines": f"{i+1}-{i+2}",
                    "repeated_word": words1[0],
                    "type": "anaphora"
                })

        return anaphoras[:15]

    def _detect_epistrophe(self) -> List[Dict[str, Any]]:
        """Detect epistrophe (repetition at end)"""
        epistrophes = []

        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].lower().split()
            words2 = self.lines[i+1].lower().split()

            if words1 and words2 and words1[-1] == words2[-1] and len(words1[-1]) > 2:
                epistrophes.append({
                    "lines": f"{i+1}-{i+2}",
                    "repeated_word": words1[-1],
                    "type": "epistrophe"
                })

        return epistrophes[:15]

    def _detect_parallelism(self) -> List[Dict[str, Any]]:
        """Detect parallelism (similar structure)"""
        parallelisms = []

        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].split()
            words2 = self.lines[i+1].split()

            if len(words1) == len(words2) and len(words1) > 2:
                parallelisms.append({
                    "lines": f"{i+1}-{i+2}",
                    "structure": "parallel",
                    "word_count": len(words1),
                    "type": "parallelism"
                })

        return parallelisms[:15]

    def _detect_antithesis(self) -> List[Dict[str, Any]]:
        """Detect antithesis (contrasting ideas in parallel)"""
        antitheses = []
        contrast_pairs = [
            ("good", "bad"), ("love", "hate"), ("light", "dark"), ("life", "death"),
            ("hope", "fear"), ("joy", "sorrow"), ("peace", "war"), ("hot", "cold"),
            ("fast", "slow"), ("big", "small"), ("rich", "poor"), ("strong", "weak"),
            ("high", "low"), ("up", "down"), ("in", "out"), ("front", "back"),
            ("beginning", "end"), ("birth", "death"), ("day", "night"), ("sun", "moon"),
            ("heaven", "hell"), ("god", "devil"), ("angel", "demon"), ("sweet", "bitter")
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for w1, w2 in contrast_pairs:
                if w1 in line_lower and w2 in line_lower:
                    antitheses.append({
                        "line": line,
                        "line_number": i + 1,
                        "pair": f"{w1}-{w2}",
                        "type": "antithesis"
                    })

        return antitheses[:15]

    def _detect_chiasmus(self) -> List[Dict[str, Any]]:
        """Detect chiasmus (ABBA structure)"""
        chiasmi = []
        # Simplified detection - looks for reversed word patterns
        common_chiasmus = [
            ("ask not", "not ask"), ("country you", "you country"),
            ("mind body", "body mind"), ("heart soul", "soul heart")
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for w1, w2 in common_chiasmus:
                if w1 in line_lower and w2 in line_lower:
                    chiasmi.append({
                        "line": line,
                        "line_number": i + 1,
                        "pattern": f"{w1}...{w2}",
                        "type": "chiasmus"
                    })

        return chiasmi[:15]

    def _detect_zeugma(self) -> List[Dict[str, Any]]:
        """Detect zeugma (one word governing multiple)"""
        zeugmas = []
        # Simplified detection
        zeugma_verbs = ["lost", "broke", "raised", "lowered", "opened", "closed"]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for verb in zeugma_verbs:
                if verb in line_lower and line_lower.count("and") >= 1:
                    zeugmas.append({
                        "line": line,
                        "line_number": i + 1,
                        "governing_word": verb,
                        "type": "zeugma"
                    })

        return zeugmas[:15]

    def _detect_asyndeton(self) -> List[Dict[str, Any]]:
        """Detect asyndeton (omission of conjunctions)"""
        asyndetons = []
        # Look for lists without conjunctions
        for i, line in enumerate(self.lines):
            words = line.split()
            if len(words) >= 4 and "and" not in line.lower() and "or" not in line.lower():
                if line.count(",") >= 2:
                    asyndetons.append({
                        "line": line,
                        "line_number": i + 1,
                        "type": "asyndeton"
                    })

        return asyndetons[:15]

    def _detect_polysyndeton(self) -> List[Dict[str, Any]]:
        """Detect polysyndeton (excessive conjunctions)"""
        polysyndetons = []

        for i, line in enumerate(self.lines):
            and_count = line.lower().count(" and ")
            if and_count >= 2:
                polysyndetons.append({
                    "line": line,
                    "line_number": i + 1,
                    "conjunction_count": and_count,
                    "type": "polysyndeton"
                })

        return polysyndetons[:15]

    def _detect_symploce(self) -> List[Dict[str, Any]]:
        """Detect symploce (anaphora + epistrophe)"""
        symploces = []
        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].lower().split()
            words2 = self.lines[i+1].lower().split()
            if len(words1) > 2 and len(words2) > 2:
                if words1[0] == words2[0] and words1[-1] == words2[-1]:
                    symploces.append({
                        "lines": f"{i+1}-{i+2}",
                        "repeated_start": words1[0],
                        "repeated_end": words1[-1],
                        "type": "symploce"
                    })
        return symploces[:15]

    def _detect_anadiplosis(self) -> List[Dict[str, Any]]:
        """Detect anadiplosis (repetition of end of line at start of next)"""
        anadiplosis = []
        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].lower().split()
            words2 = self.lines[i+1].lower().split()
            if words1 and words2 and words1[-1] == words2[0] and len(words1[-1]) > 2:
                anadiplosis.append({
                    "lines": f"{i+1}-{i+2}",
                    "repeated_word": words1[-1],
                    "type": "anadiplosis"
                })
        return anadiplosis[:15]

    def _detect_climax(self) -> List[Dict[str, Any]]:
        """Detect climax (words in increasing order of importance/intensity)"""
        climaxes = []
        climax_patterns = [
            r'\b(good).*?(better).*?(best)\b',
            r'\b(small).*?(medium).*?(large)\b',
            r'\b(smile).*?(laugh).*?(roar)\b',
            r'\b(walk).*?(run).*?(fly)\b'
        ]
        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for pattern in climax_patterns:
                if re.search(pattern, line_lower):
                    climaxes.append({
                        "line": line,
                        "line_number": i + 1,
                        "type": "climax"
                    })
        return climaxes[:15]

    def _detect_antimetabole(self) -> List[Dict[str, Any]]:
        """Detect antimetabole (repetition in reverse order)"""
        antimetaboles = []
        for i, line in enumerate(self.lines):
            words = line.lower().split()
            if len(words) >= 4:
                # Basic check for A B ... B A pattern
                for j in range(len(words) - 3):
                    if words[j] == words[j+3] and words[j+1] == words[j+2] and len(words[j]) > 2:
                        antimetaboles.append({
                            "line": line,
                            "line_number": i + 1,
                            "pattern": f"{words[j]} {words[j+1]} ... {words[j+2]} {words[j+3]}",
                            "type": "antimetabole"
                        })
        return antimetaboles[:15]

    def _detect_isocolon(self) -> List[Dict[str, Any]]:
        """Detect isocolon (parallel structures of same length)"""
        isocolons = []
        for i in range(len(self.lines) - 1):
            words1 = self.lines[i].split()
            words2 = self.lines[i+1].split()
            if len(words1) == len(words2) and len(words1) >= 3:
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
        return isocolons[:15]

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
        return ellipses[:15]

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
        visual_words = [
            "see", "saw", "look", "looking", "watch", "bright", "dark", "light",
            "shadow", "color", "red", "blue", "green", "golden", "shining", "gleaming",
            "sun", "moon", "star", "sky", "cloud", "rainbow", "sparkle", "glitter",
            "glow", "beam", "ray", "flash", "glimmer", "shimmer", "dazzle", "blind"
        ]
        return self._detect_imagery_by_words(visual_words, "visual")

    def _detect_auditory_imagery(self) -> List[Dict[str, Any]]:
        """Auditory imagery (sound)"""
        auditory_words = [
            "hear", "heard", "listen", "sound", "loud", "quiet", "silent", "whisper",
            "thunder", "rumble", "ring", "voice", "music", "song", "cry", "shout",
            "laugh", "scream", "shriek", "roar", "howl", "buzz", "hiss", "clang",
            "crash", "bang", "pop", "splash", "drip", "hum", "chirp", "tweet"
        ]
        return self._detect_imagery_by_words(auditory_words, "auditory")

    def _detect_tactile_imagery(self) -> List[Dict[str, Any]]:
        """Tactile imagery (touch)"""
        tactile_words = [
            "touch", "feel", "warm", "cold", "hot", "cool", "rough", "smooth",
            "soft", "hard", "sharp", "sticky", "dry", "wet", "tight", "loose",
            "prickle", "tingle", "burn", "freeze", "ache", "pain", "pressure"
        ]
        return self._detect_imagery_by_words(tactile_words, "tactile")

    def _detect_gustatory_imagery(self) -> List[Dict[str, Any]]:
        """Gustatory imagery (taste)"""
        gustatory_words = [
            "taste", "sweet", "sour", "bitter", "salty", "spicy", "delicious",
            "yummy", "flavor", "savory", "bland", "tender", "juicy", "tangy",
            "zesty", "rich", "creamy", "crispy", "crunchy"
        ]
        return self._detect_imagery_by_words(gustatory_words, "gustatory")

    def _detect_olfactory_imagery(self) -> List[Dict[str, Any]]:
        """Olfactory imagery (smell)"""
        olfactory_words = [
            "smell", "scent", "fragrant", "stink", "foul", "fresh", "sweet",
            "perfume", "flower", "rose", "aroma", "incense", "smoke", "rain",
            "musty", "pungent", "acrid", "earthy", "musky", "floral"
        ]
        return self._detect_imagery_by_words(olfactory_words, "olfactory")

    def _detect_kinesthetic_imagery(self) -> List[Dict[str, Any]]:
        """Kinesthetic imagery (movement)"""
        kinesthetic_words = [
            "move", "run", "walk", "jump", "fly", "swim", "dance", "spin", "turn",
            "twist", "flow", "drift", "glide", "slide", "creep", "climb", "rise",
            "fall", "swing", "sway", "rock", "roll", "tumble", "soar", "dive"
        ]
        return self._detect_imagery_by_words(kinesthetic_words, "kinesthetic")

    def _detect_organic_imagery(self) -> List[Dict[str, Any]]:
        """Organic imagery (internal sensations)"""
        organic_words = [
            "hunger", "thirst", "tired", "exhausted", "nausea", "dizzy", "faint",
            "weak", "energy", "fatigue", "ache", "pain", "comfort", "ease",
            "suffocate", "breathe", "heartbeat", "pulse", "chill", "fever"
        ]
        return self._detect_imagery_by_words(organic_words, "organic")

    def _detect_imagery_by_words(self, word_list: List[str], imagery_type: str) -> List[Dict[str, Any]]:
        """Helper function to detect imagery by word list"""
        imagery = []
        for i, line in enumerate(self.lines):
            found = [w for w in word_list if w in line.lower()]
            if found:
                imagery.append({
                    "line": line,
                    "line_number": i + 1,
                    "imagery_words": found[:5],
                    "type": imagery_type
                })
        return imagery[:15]

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
        yamakas = []
        # Common Yamaka words in Hindi/Sanskrit
        yamaka_words = ["कर", "हर", "रवि", "शशि", "नीर", "वारि", "अम्बु", "जल"]

        for i, line in enumerate(self.lines):
            for word in yamaka_words:
                count = line.count(word)
                if count >= 2:
                    yamakas.append({
                        "line": line,
                        "line_number": i + 1,
                        "repeated_word": word,
                        "count": count,
                        "type": "yamaka"
                    })

        return yamakas[:10]

    def _detect_shlesha(self) -> List[Dict[str, Any]]:
        """
        Shlesha: Pun/double meaning (one word, multiple meanings)
        Example: सारा (entire/essence), रस (juice/essence/emotion)
        """
        shleshas = []
        # Words with multiple meanings
        shlesha_words = {
            "सारा": ["entire", "essence"],
            "रस": ["juice", "essence", "emotion"],
            "नीर": ["water", "arrow"],
            "अलि": ["bee", "friend"],
            "हरि": ["Vishnu", "lion", "green"],
            "गिरा": ["speech", "mountain"]
        }

        for i, line in enumerate(self.lines):
            for word, meanings in shlesha_words.items():
                if word in line:
                    shleshas.append({
                        "line": line,
                        "line_number": i + 1,
                        "word": word,
                        "meanings": meanings,
                        "type": "shlesha"
                    })

        return shleshas[:10]

    def _detect_utpreksha(self) -> List[Dict[str, Any]]:
        """
        Utpreksha: Imaginative comparison/fanciful identification
        Example: "Her face is the moon"
        """
        utprekshas = []
        # Common imaginative comparisons
        utpreksha_patterns = [
            r'face.*moon', r'eyes.*star', r'hair.*night', r'lips.*rose',
            r'cheek.*rose', r'walk.*swan', r'voice.*cuckoo', r'waist.*lightning'
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for pattern in utpreksha_patterns:
                if re.search(pattern, line_lower):
                    utprekshas.append({
                        "line": line,
                        "line_number": i + 1,
                        "type": "utpreksha"
                    })

        return utprekshas[:10]

    def _detect_vibhavana(self) -> List[Dict[str, Any]]:
        """
        Vibhavana: Effect described without cause (or cause without effect)
        Example: "Tears flow" (without saying why)
        """
        vibhavanas = []
        effect_words = ["tears", "weep", "cry", "tremble", "blush", "faint", "swoon"]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for word in effect_words:
                if word in line_lower:
                    # Check if cause is NOT mentioned
                    if not any(cause in line_lower for cause in ["because", "since", "for", "why"]):
                        vibhavanas.append({
                            "line": line,
                            "line_number": i + 1,
                            "effect": word,
                            "type": "vibhavana"
                        })

        return vibhavanas[:10]

    def _detect_vishesokti(self) -> List[Dict[str, Any]]:
        """
        Vishesokti: Contradiction of natural sequence
        Example: "Fire burns cold"
        """
        vishesoktis = []
        contradictions = [
            ("fire", "cold"), ("ice", "hot"), ("sun", "night"), ("moon", "heat"),
            ("water", "dry"), ("stone", "soft"), ("feather", "heavy")
        ]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for w1, w2 in contradictions:
                if w1 in line_lower and w2 in line_lower:
                    vishesoktis.append({
                        "line": line,
                        "line_number": i + 1,
                        "contradiction": f"{w1}-{w2}",
                        "type": "vishesokti"
                    })

        return vishesoktis[:10]

    def _detect_rupak(self) -> List[Dict[str, Any]]:
        """
        Rupak: Metaphor (direct identification)
        Example: "She is a goddess"
        """
        rupaks = []
        # Common metaphorical identifications
        metaphor_patterns = [
            r'is\s+a\s+(goddess|god|angel|moon|star|flower)',
            r'was\s+a\s+(goddess|god|angel|moon|star)',
            r'are\s+(goddesses|gods|angels|flowers)'
        ]

        for i, line in enumerate(self.lines):
            for pattern in metaphor_patterns:
                matches = re.finditer(pattern, line.lower())
                for match in matches:
                    rupaks.append({
                        "line": line,
                        "line_number": i + 1,
                        "metaphor": match.group(),
                        "type": "rupak"
                    })

        return rupaks[:10]

    def _detect_upama(self) -> List[Dict[str, Any]]:
        """
        Upama: Simile (comparison using like/as)
        Example: "Fair as a star"
        """
        upamas = []
        simile_patterns = [
            r'\blike\s+\w+',
            r'\bas\s+\w+\s+as\b',
            r'\bजैसा\b',
            r'\bसा\b',
            r'\bसमान\b'
        ]

        for i, line in enumerate(self.lines):
            for pattern in simile_patterns:
                matches = re.finditer(pattern, line.lower())
                for match in matches:
                    upamas.append({
                        "line": line,
                        "line_number": i + 1,
                        "simile": match.group(),
                        "type": "upama"
                    })

        return upamas[:10]

    # ==================== RASA THEORY ====================

    def _analyze_rasa(self) -> Dict[str, Any]:
        """
        Analyze Rasa (aesthetic emotion) based on Navarasa theory
        From Bharata's Natyashastra
        """
        rasa_scores = {
            "shringara": 0.0,  # Love/Beauty
            "hasya": 0.0,      # Laughter/Comedy
            "karuna": 0.0,     # Compassion/Sorrow
            "raudra": 0.0,     # Fury/Anger
            "veera": 0.0,      # Heroism/Courage
            "bhayanaka": 0.0,  # Terror/Fear
            "bibhatsa": 0.0,   # Disgust
            "adbhuta": 0.0,    # Wonder/Awe
            "shanta": 0.0      # Peace/Serenity
        }

        text_lower = self.text.lower()

        # Shringara (Love/Beauty)
        shringara_words = ["love", "beautiful", "beloved", "desire", "passion", "romance", "kiss", "embrace", "charm", "grace", "delight", "joy", "pleasure"]
        rasa_scores["shringara"] = self._calculate_rasa_score(text_lower, shringara_words)

        # Hasya (Laughter/Comedy)
        hasya_words = ["laugh", "funny", "joke", "humor", "comic", "ridiculous", "absurd", "amusing", "merry", "giggle", "chuckle"]
        rasa_scores["hasya"] = self._calculate_rasa_score(text_lower, hasya_words)

        # Karuna (Compassion/Sorrow)
        karuna_words = ["sad", "sorrow", "tear", "weep", "cry", "grief", "pain", "suffer", "mourn", "lament", "tragic", "pitiful", "compassion"]
        rasa_scores["karuna"] = self._calculate_rasa_score(text_lower, karuna_words)

        # Raudra (Fury/Anger)
        raudra_words = ["anger", "fury", "rage", "wrath", "hate", "destroy", "kill", "violent", "cruel", "fierce", "terrible", "vengeance"]
        rasa_scores["raudra"] = self._calculate_rasa_score(text_lower, raudra_words)

        # Veera (Heroism/Courage)
        veera_words = ["hero", "brave", "courage", "valor", "victory", "triumph", "glory", "honor", "noble", "warrior", "strength", "power", "bold"]
        rasa_scores["veera"] = self._calculate_rasa_score(text_lower, veera_words)

        # Bhayanaka (Terror/Fear)
        bhayanaka_words = ["fear", "terror", "horror", "dread", "fright", "panic", "tremble", "nightmare", "darkness", "death", "danger", "threat"]
        rasa_scores["bhayanaka"] = self._calculate_rasa_score(text_lower, bhayanaka_words)

        # Bibhatsa (Disgust)
        bibhatsa_words = ["disgust", "revolting", "foul", "vile", "nasty", "repulsive", "loathsome", "ugly", "dirty", "filthy", "abhor"]
        rasa_scores["bibhatsa"] = self._calculate_rasa_score(text_lower, bibhatsa_words)

        # Adbhuta (Wonder/Awe)
        adbhuta_words = ["wonder", "amazing", "marvel", "miracle", "awe", "magnificent", "splendid", "glorious", "divine", "mysterious", "extraordinary"]
        rasa_scores["adbhuta"] = self._calculate_rasa_score(text_lower, adbhuta_words)

        # Shanta (Peace/Serenity)
        shanta_words = ["peace", "calm", "quiet", "serene", "tranquil", "still", "silence", "meditation", "bliss", "content", "harmony", "balance"]
        rasa_scores["shanta"] = self._calculate_rasa_score(text_lower, shanta_words)

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
        stimuli = {
            "nature": ["moon", "spring", "garden", "flower", "river", "wind", "rain"],
            "person": ["beloved", "hero", "enemy", "king", "friend"],
            "event": ["battle", "festival", "departure", "arrival", "death"]
        }
        for i, line in enumerate(self.lines):
            for category, words in stimuli.items():
                for word in words:
                    if word in line.lower():
                        vibavas.append({"line_number": i+1, "stimulus": word, "category": category})
        return vibavas[:5]

    def _detect_anubhava(self) -> List[Dict[str, str]]:
        """Detect Anubhava (consequent/physical reaction)"""
        anubhavas = []
        reactions = {
            "physical": ["tear", "smile", "tremble", "sweat", "blush", "faint", "sigh", "gasp", "stare"],
            "vocal": ["cry", "laugh", "shout", "whisper", "sing", "stammer", "stutter"]
        }
        for i, line in enumerate(self.lines):
            for category, words in reactions.items():
                for word in words:
                    if word in line.lower():
                        anubhavas.append({"line_number": i+1, "reaction": word, "category": category})
        return anubhavas[:5]

    def _detect_vyabhichari_bhava(self) -> List[Dict[str, str]]:
        """Detect Vyabhichari Bhava (transitory states)"""
        vyabhichari = []
        transitory = ["anxiety", "joy", "shame", "arrogance", "despair", "envy", "doubt", "pride", "weakness"]
        for i, line in enumerate(self.lines):
            for state in transitory:
                if state in line.lower():
                    vyabhichari.append({"line_number": i+1, "state": state})
        return vyabhichari[:5]

    def _calculate_rasa_score(self, text: str, word_list: List[str]) -> float:
        """Calculate score for a specific rasa"""
        count = sum(text.count(word) for word in word_list)
        total_words = len(text.split())
        return min(1.0, count / max(1, total_words) * 100)

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
        foreshadowing = []
        markers = ["will", "shall", "would", "could", "might", "future", "tomorrow", "someday", "one day", "eventually", "never", "always", "remember", "warning", "ominous", "premonition", "destiny", "fate"]

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for marker in markers:
                if marker in line_lower:
                    foreshadowing.append({
                        "line": line,
                        "line_number": i + 1,
                        "marker": marker,
                        "type": "foreshadowing"
                    })

        return foreshadowing[:15]

    def _detect_symbolism(self) -> List[Dict[str, Any]]:
        """Detect symbolism"""
        return self._detect_symbol()

    def _detect_symbol(self) -> List[Dict[str, Any]]:
        """Detect symbols"""
        symbols = []
        symbol_dict = {
            "rose": "love/passion",
            "dove": "peace",
            "eagle": "freedom/strength",
            "serpent": "evil/temptation",
            "moon": "femininity/change",
            "sun": "vitality/masculinity",
            "star": "hope/guidance",
            "rain": "cleansing/renewal",
            "storm": "conflict/turmoil",
            "fire": "passion/destruction",
            "water": "life/purification",
            "ocean": "emotions/infinity",
            "mountain": "stability/obstacle",
            "road": "life journey",
            "door": "opportunity",
            "window": "perspective",
            "cross": "sacrifice/suffering",
            "phoenix": "rebirth/resurrection",
            "owl": "wisdom",
            "lion": "courage/royalty"
        }

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for symbol, meaning in symbol_dict.items():
                if symbol in line_lower:
                    symbols.append({
                        "line": line,
                        "line_number": i + 1,
                        "symbol": symbol,
                        "meaning": meaning,
                        "type": "symbolism"
                    })

        return symbols[:15]

    def _detect_allusion(self) -> List[Dict[str, Any]]:
        """Detect allusion (reference to other works/events)"""
        allusions = []
        references = {
            "adam": "biblical", "eve": "biblical", "moses": "biblical", "jesus": "biblical",
            "odysseus": "greek", "achilles": "greek", "athena": "greek", "venus": "roman",
            "apollo": "greek", "artemis": "greek", "prometheus": "greek", "icarus": "greek",
            "shakespeare": "literary", "dante": "literary", "homer": "literary",
            "robin hood": "folklore", "king arthur": "folklore", "medusa": "greek",
            "garden of eden": "biblical", "trojan": "greek", "olympus": "greek"
        }

        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            for ref, category in references.items():
                if ref in line_lower:
                    allusions.append({
                        "line": line,
                        "line_number": i + 1,
                        "reference": ref,
                        "category": category,
                        "type": "allusion"
                    })

        return allusions[:15]

    def _detect_motif(self) -> List[Dict[str, Any]]:
        """Detect recurring motifs"""
        motifs = []
        word_freq = Counter(self.words)

        # Find words that appear multiple times
        recurring = [(word, count) for word, count in word_freq.items() if count >= 3 and len(word) > 3]

        for word, count in recurring[:10]:
            lines_with_word = [i+1 for i, line in enumerate(self.lines) if word in line.lower()]
            motifs.append({
                "word": word,
                "occurrences": count,
                "line_numbers": lines_with_word[:10],
                "type": "motif"
            })

        return motifs


def analyze_idioms_and_proverbs(text: str) -> Dict[str, List[str]]:
    """Detect idioms and proverbs"""
    idioms = [
        "break the ice", "bite the bullet", "beat around the bush", "burn the midnight oil",
        "cost an arm and a leg", "hit the nail on the head", "kill two birds with one stone",
        "let the cat out of the bag", "make a long story short", "once in a blue moon",
        "piece of cake", "rain cats and dogs", "spill the beans", "take it with a grain of salt"
    ]

    proverbs = [
        "a stitch in time saves nine", "actions speak louder than words", "all that glitters is not gold",
        "an apple a day keeps the doctor away", "birds of a feather flock together", "better safe than sorry"
    ]

    text_lower = text.lower()
    return {
        "idioms": [idiom for idiom in idioms if idiom in text_lower],
        "proverbs": [proverb for proverb in proverbs if proverb in text_lower]
    }
