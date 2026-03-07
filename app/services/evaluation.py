"""
Rating & Evaluation Engine
Complete 7-category scoring, publishability assessment, performance assessment
Based on Ultimate Literary Master System
"""

from typing import Dict, List, Any, Optional, Tuple

from app.services.rule_loader import get_evaluation_rules, get_output_limits


class EvaluationEngine:
    """
    Comprehensive evaluation and rating system
    7-category scoring with detailed justifications
    """

    def __init__(self):
        self._rules = get_evaluation_rules()
        self._output_limits = get_output_limits()
        self._weights = self._rules["weights"]
        self._base_scores = self._rules["base_scores"]
        self._thresholds = self._rules["thresholds"]
        self._templates = self._rules["templates"]
        self._limits = self._rules.get("limits", {})
        self.text = ""
        self.metrics: Dict[str, Any] = {}
        self.language = "en"

    def evaluate(self, text: str, metrics: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Complete evaluation of a literary work
        """
        self.text = text
        self.metrics = metrics
        self.language = language

        # Calculate ratings
        ratings = self._calculate_ratings()

        # Identify strengths
        strengths = self._identify_strengths()

        # Identify issues
        issues = self._identify_issues()

        # Generate suggestions
        suggestions = self._generate_suggestions()

        # Publishability assessment
        publishability = self._assess_publishability()

        # Performance assessment (for spoken word)
        performance = self._assess_performance_detailed(self.text, self.metrics)

        # Generate corrected versions
        minimal_corrected = self._generate_minimal_corrected()
        polished_version = self._generate_polished_version()

        return {
            "ratings": ratings,
            "strengths": strengths,
            "issues": issues,
            "suggestions": suggestions,
            "publishability": publishability,
            "performance": performance,
            "minimal_corrected_version": minimal_corrected,
            "polished_version": polished_version
        }

    def _calculate_ratings(self) -> Dict[str, float]:
        """Calculate 7-category ratings (0-10 scale)"""
        ratings = {}

        # 1. Technical Craft (meter, rhyme, structure)
        ratings["technical_craft"] = self._rate_technical_craft()

        # 2. Language & Diction
        ratings["language_diction"] = self._rate_language_diction()

        # 3. Imagery & Voice
        ratings["imagery_voice"] = self._rate_imagery_voice()

        # 4. Emotional Impact
        ratings["emotional_impact"] = self._rate_emotional_impact()

        # 5. Cultural Fidelity
        ratings["cultural_fidelity"] = self._rate_cultural_fidelity()

        # 6. Originality
        ratings["originality"] = self._rate_originality()

        # 7. Computational Greatness (if available)
        cg_score = self.metrics.get("quantitative", {}).get("computational_greatness_score")
        if cg_score is None:
            cg_score = self._base_scores["computational_greatness"]
        ratings["computational_greatness"] = cg_score

        # Overall quality (weighted average)
        overall = (
            ratings["technical_craft"] * self._weights["technical_craft"] +
            ratings["language_diction"] * self._weights["language_diction"] +
            ratings["imagery_voice"] * self._weights["imagery_voice"] +
            ratings["emotional_impact"] * self._weights["emotional_impact"] +
            ratings["cultural_fidelity"] * self._weights["cultural_fidelity"] +
            ratings["originality"] * self._weights["originality"] +
            ratings["computational_greatness"] * self._weights["computational_greatness"]
        )

        ratings["overall_quality"] = round(overall, 1)

        # Round all ratings
        for key in ratings:
            ratings[key] = round(ratings[key], 1)

        return ratings

    def _rate_technical_craft(self) -> float:
        """Rate technical craft (meter, rhyme, structure)"""
        score = self._base_scores["technical_craft"]

        prosody = self.metrics.get("prosody", {})
        quantitative = self.metrics.get("quantitative", {})

        # Meter regularity
        meter = prosody.get("meter", {})
        if meter.get("metrical_regularity", 0) > self._thresholds["metrical_regularity_high"]:
            score += 2.0
        elif meter.get("metrical_regularity", 0) > self._thresholds["metrical_regularity_mid"]:
            score += 1.0

        # Rhyme quality
        rhyme = prosody.get("rhyme", {})
        if rhyme.get("rhyme_density", 0) > self._thresholds["rhyme_density_high"]:
            score += 2.0
        elif rhyme.get("rhyme_density", 0) > self._thresholds["rhyme_density_mid"]:
            score += 1.0

        # Structure
        structural = quantitative.get("structural_metrics", {})
        if structural.get("total_lines", 0) > 0:
            score += 1.0

        return min(10, max(0, score))

    def _rate_language_diction(self) -> float:
        """Rate language and diction"""
        score = self._base_scores["language_diction"]

        linguistic = self.metrics.get("linguistic", {})
        quantitative = self.metrics.get("quantitative", {})

        # Lexical diversity
        lexical = quantitative.get("lexical_metrics", {})
        ttr = lexical.get("type_token_ratio", 0)
        if ttr > self._thresholds["ttr_high"]:
            score += 2.5
        elif ttr > self._thresholds["ttr_mid"]:
            score += 1.5

        # Lexical density
        density = lexical.get("lexical_density", 0)
        if density > self._thresholds["lexical_density_high"]:
            score += 1.5
        elif density > self._thresholds["lexical_density_mid"]:
            score += 0.5

        # POS distribution (good balance)
        pos = linguistic.get("pos_distribution", {})
        if pos.get("noun", 0) > 0 and pos.get("verb", 0) > 0:
            score += 1.0

        return min(10, max(0, score))

    def _rate_imagery_voice(self) -> float:
        """Rate imagery and voice"""
        score = self._base_scores["imagery_voice"]

        literary = self.metrics.get("literary_devices", {})
        imagery = literary.get("imagery", {})

        # Count imagery types
        imagery_count = sum(len(v) for v in imagery.values())
        if imagery_count > self._thresholds["imagery_count_high"]:
            score += 3.0
        elif imagery_count > self._thresholds["imagery_count_mid"]:
            score += 2.0
        elif imagery_count > self._thresholds["imagery_count_low"]:
            score += 1.0

        # Figurative language
        tropes = literary.get("tropes", {})
        trope_count = sum(len(v) for v in tropes.values())
        if trope_count > self._thresholds["trope_count_high"]:
            score += 2.0
        elif trope_count > self._thresholds["trope_count_mid"]:
            score += 1.0

        return min(10, max(0, score))

    def _rate_emotional_impact(self) -> float:
        """Rate emotional impact"""
        score = self._base_scores["emotional_impact"]

        advanced = self.metrics.get("advanced", {})
        sentiment = advanced.get("sentiment", {})

        # Sentiment intensity
        valence = abs(sentiment.get("valence", 0))
        if valence > self._thresholds["valence_high"]:
            score += 3.0
        elif valence > self._thresholds["valence_mid"]:
            score += 2.0
        elif valence > self._thresholds["valence_low"]:
            score += 1.0

        # Arousal (intensity)
        arousal = sentiment.get("arousal", 0)
        if arousal > self._thresholds["arousal_high"]:
            score += 2.0

        return min(10, max(0, score))

    def _rate_cultural_fidelity(self) -> float:
        """Rate cultural and historical fidelity"""
        score = self._base_scores["cultural_fidelity"]

        # Check for appropriate cultural elements
        literary = self.metrics.get("literary_devices", {})
        
        # Alankar usage for Indic languages
        alankar = literary.get("sanskrit_alankar", {})
        alankar_count = sum(len(v) for v in alankar.values())
        if alankar_count > self._thresholds["alankar_high"]:
            score += 2.0
        elif alankar_count > 0:
            score += 1.0

        # Rasa presence
        rasa = literary.get("rasa_vector", {})
        if rasa and rasa.get("dominant_rasa"):
            score += 2.0

        return min(10, max(0, score))

    def _rate_originality(self) -> float:
        """Rate originality and creativity"""
        score = self._base_scores["originality"]

        quantitative = self.metrics.get("quantitative", {})
        lexical = quantitative.get("lexical_metrics", {})

        # Unique word ratio
        ttr = lexical.get("type_token_ratio", 0)
        if ttr > self._thresholds["ttr_high"]:
            score += 3.0
        elif ttr > self._thresholds["ttr_mid"]:
            score += 2.0

        # Hapax legomena (words used once - indicates vocabulary richness)
        hapax = lexical.get("hapax_legomena", 0)
        total = lexical.get("total_words", 1)
        hapax_ratio = hapax / total if total > 0 else 0
        if hapax_ratio > self._thresholds["ttr_high"]:
            score += 2.0
        elif hapax_ratio > self._thresholds["ttr_mid"]:
            score += 1.0

        return min(10, max(0, score))

    def _identify_strengths(self) -> List[Dict[str, Any]]:
        """Identify strengths in the work"""
        strengths = []

        quantitative = self.metrics.get("quantitative", {})
        literary = self.metrics.get("literary_devices", {})
        prosody = self.metrics.get("prosody", {})

        lexical = quantitative.get("lexical_metrics", {})
        if lexical.get("type_token_ratio", 0) > self._thresholds["ttr_mid"]:
            tmpl = self._templates["strengths"]["vocabulary"]
            strengths.append({
                "category": tmpl["category"],
                "description": tmpl["description"],
                "evidence": tmpl["evidence"].format(ttr=lexical.get("type_token_ratio", 0)),
                "impact": tmpl["impact"]
            })

        # Check imagery
        imagery = literary.get("imagery", {})
        imagery_count = sum(len(v) for v in imagery.values())
        if imagery_count > self._thresholds["imagery_count_mid"]:
            tmpl = self._templates["strengths"]["imagery"]
            strengths.append({
                "category": tmpl["category"],
                "description": tmpl["description"],
                "evidence": tmpl["evidence"].format(count=imagery_count),
                "impact": tmpl["impact"]
            })

        # Check figurative language
        tropes = literary.get("tropes", {})
        trope_count = sum(len(v) for v in tropes.values())
        if trope_count > self._thresholds["trope_count_mid"]:
            tmpl = self._templates["strengths"]["figurative"]
            strengths.append({
                "category": tmpl["category"],
                "description": tmpl["description"],
                "evidence": tmpl["evidence"].format(count=trope_count),
                "impact": tmpl["impact"]
            })

        # Check meter
        meter = prosody.get("meter", {})
        if meter.get("metrical_regularity", 0) > self._thresholds["metrical_regularity_mid"]:
            tmpl = self._templates["strengths"]["prosody"]
            strengths.append({
                "category": tmpl["category"],
                "description": tmpl["description"].format(meter=meter.get("detected_meter", "meter")),
                "evidence": tmpl["evidence"].format(regularity=meter.get("metrical_regularity", 0)),
                "impact": tmpl["impact"]
            })

        # Check Alankar (for Indic)
        alankar = literary.get("sanskrit_alankar", {})
        alankar_count = sum(len(v) for v in alankar.values())
        if alankar_count > self._thresholds["alankar_low"]:
            tmpl = self._templates["strengths"]["classical"]
            strengths.append({
                "category": tmpl["category"],
                "description": tmpl["description"],
                "evidence": tmpl["evidence"].format(count=alankar_count),
                "impact": tmpl["impact"]
            })

        # Check Rasa
        rasa = literary.get("rasa_vector", {})
        if rasa and rasa.get("dominant_rasa"):
            tmpl = self._templates["strengths"]["rasa"]
            strengths.append({
                "category": tmpl["category"],
                "description": tmpl["description"].format(rasa=rasa.get("dominant_rasa", "").capitalize()),
                "evidence": tmpl["evidence"],
                "impact": tmpl["impact"]
            })

        # Check rule-based form compliance
        form_info = self.metrics.get("form_detected", {})
        detected_forms = form_info.get("detected_forms", [])
        if detected_forms and "free_verse" not in detected_forms:
            tmpl = self._templates["strengths"].get("form_compliance", {
                "category": "Structural Integrity",
                "description": "The poem successfully adheres to the strict rules of a traditional poetic form ({form}).",
                "evidence": "Detected strict compliance with {form} constraints.",
                "impact": "Demonstrates advanced technical control and mastery of established poetic structures."
            })
            strengths.append({
                "category": tmpl["category"],
                "description": tmpl["description"].format(form=detected_forms[0].replace("_", " ").title()),
                "evidence": tmpl["evidence"].format(form=detected_forms[0].replace("_", " ").title()),
                "impact": tmpl["impact"]
            })

        limit = self._output_limits.get("evaluation_strengths")
        if limit is None:
            return strengths
        return strengths[:limit]

    def _identify_issues(self) -> List[Dict[str, Any]]:
        """Identify issues in the work"""
        issues = []

        quantitative = self.metrics.get("quantitative", {})
        prosody = self.metrics.get("prosody", {})

        # Check for low lexical diversity
        lexical = quantitative.get("lexical_metrics", {})
        if lexical.get("type_token_ratio", 0) < self._thresholds["ttr_mid"]:
            tmpl = self._templates["issues"]["low_ttr"]
            issues.append({
                "location": tmpl["location"],
                "issue_type": tmpl["issue_type"],
                "severity": tmpl["severity"],
                "technical_explanation": tmpl["technical_explanation"],
                "impact_analysis": tmpl["impact_analysis"],
                "evidence": tmpl["evidence"].format(ttr=lexical.get("type_token_ratio", 0), ideal_ttr=self._thresholds["ttr_mid"]),
                "suggested_fix": tmpl["suggested_fix"],
                "why_it_matters": tmpl["why_it_matters"]
            })

        # Check for inconsistent meter
        meter = prosody.get("meter", {})
        if meter.get("detected_meter") == "free_verse" and meter.get("metrical_regularity", 0) < self._thresholds["metrical_regularity_low"]:
            tmpl = self._templates["issues"]["inconsistent_meter"]
            issues.append({
                "location": tmpl["location"],
                "issue_type": tmpl["issue_type"],
                "severity": tmpl["severity"],
                "technical_explanation": tmpl["technical_explanation"],
                "impact_analysis": tmpl["impact_analysis"],
                "evidence": tmpl["evidence"],
                "suggested_fix": tmpl["suggested_fix"],
                "why_it_matters": tmpl["why_it_matters"]
            })

        # Check for near-miss form compliance
        form_info = self.metrics.get("form_detected", {})
        detected_forms = form_info.get("detected_forms", [])
        
        # If no strict forms detected but rhyme scheme suggests an attempt:
        rhyme_form = prosody.get("rhyme", {}).get("detected_form")
        if rhyme_form and not detected_forms:
            tmpl = self._templates["issues"].get("form_near_miss", {
                "location": "Overall Structure",
                "issue_type": "Form Constraint Violation",
                "severity": "medium",
                "technical_explanation": "The rhyme scheme matches a {form}, but meter/syllable/line-count constraints are violated.",
                "impact_analysis": "The poem attempts a traditional form but breaks required rules, disrupting expected aesthetic patterns.",
                "evidence": "Detected {form} rhyme scheme without full structural compliance.",
                "suggested_fix": "Review the strict rules for {form} (meter, syllable count, stanza breaks) and revise non-compliant lines.",
                "why_it_matters": "Traditional forms derive power from the tension between strict constraints and creative expression."
            })
            issues.append({
                "location": tmpl["location"],
                "issue_type": tmpl["issue_type"],
                "severity": tmpl["severity"],
                "technical_explanation": tmpl["technical_explanation"].format(form=rhyme_form.replace("_", " ").title()),
                "impact_analysis": tmpl["impact_analysis"],
                "evidence": tmpl["evidence"].format(form=rhyme_form.replace("_", " ").title()),
                "suggested_fix": tmpl["suggested_fix"].format(form=rhyme_form.replace("_", " ").title()),
                "why_it_matters": tmpl["why_it_matters"]
            })

        limit = self._output_limits.get("evaluation_issues")
        if limit is None:
            return issues
        return issues[:limit]

    def _generate_suggestions(self) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        suggestions = []

        ratings = self._calculate_ratings()

        if ratings.get("technical_craft", 5) < self._thresholds["priority_cutoff"]:
            tmpl = self._templates["suggestions"]["technical_craft"]
            suggestions.append({
                "priority": tmpl["priority"],
                "category": tmpl["category"],
                "description": tmpl["description"],
                "example": tmpl["example"]
            })

        if ratings.get("imagery_voice", 5) < self._thresholds["priority_cutoff"]:
            tmpl = self._templates["suggestions"]["imagery"]
            suggestions.append({
                "priority": tmpl["priority"],
                "category": tmpl["category"],
                "description": tmpl["description"],
                "example": tmpl["example"]
            })

        if ratings.get("originality", 5) < self._thresholds["priority_cutoff"]:
            tmpl = self._templates["suggestions"]["originality"]
            suggestions.append({
                "priority": tmpl["priority"],
                "category": tmpl["category"],
                "description": tmpl["description"],
                "example": tmpl["example"]
            })

        # Rasa suggestions
        if ratings.get("emotional_impact", 5) < self._thresholds["priority_cutoff"]:
            tmpl = self._templates["suggestions"]["emotional_resonance"]
            suggestions.append({
                "priority": tmpl["priority"],
                "category": tmpl["category"],
                "description": tmpl["description"],
                "example": tmpl["example"]
            })

        limit = self._output_limits.get("evaluation_suggestions")
        if limit is None:
            return suggestions
        return suggestions[:limit]

    def _assess_publishability(self) -> Dict[str, Any]:
        """Assess publishability"""
        ratings = self._calculate_ratings()
        overall = ratings.get("overall_quality", 5)

        if overall >= self._thresholds["overall_excellent"]:
            return self._templates["publishability"]["excellent"]
        if overall >= self._thresholds["overall_good"]:
            return self._templates["publishability"]["good"]
        if overall >= self._thresholds["overall_fair"]:
            return self._templates["publishability"]["fair"]
        return self._templates["publishability"]["poor"]

    def _assess_performance_detailed(self, text: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detailed assessment for spoken word/performance based on real metrics
        """
        lines = [l for l in text.split('\n') if l.strip()]
        prosody = metrics.get("prosody", {})
        literary = metrics.get("literary_devices", {})
        
        # Calculate scores based on linguistic features
        vocal_score = self._base_scores["vocal"]
        if literary.get("schemes", {}).get("alliteration"):
            vocal_score += self._thresholds["voice_alliteration_bonus"]
        if prosody.get("meter", {}).get("metrical_regularity", 0) > self._thresholds["metrical_regularity_mid"]:
            vocal_score += self._thresholds["voice_meter_bonus"]

        breath_score = self._base_scores["breath"]
        avg_len = sum(len(l.split()) for l in lines) / len(lines) if lines else 0
        if avg_len > self._thresholds["avg_line_len_long"]:
            breath_score -= self._thresholds["breath_penalty"]

        dramatic_score = metrics.get("advanced", {}).get("sentiment", {}).get("valence", 0) * self._thresholds["dramatic_scale"] + self._thresholds["dramatic_base"]
        
        overall = (vocal_score + breath_score + dramatic_score) / 3
        
        perf_templates = self._templates["performance"]
        return {
            "overall": round(overall, 1),
            "vocal": round(min(10, vocal_score), 1),
            "breath": round(min(10, breath_score), 1),
            "dramatic": round(min(10, dramatic_score), 1),
            "engagement": round(metrics.get("evaluation", {}).get("ratings", {}).get("emotional_impact", 5), 1),
            "vocal_notes": perf_templates["vocal_notes_high"] if vocal_score > self._thresholds["priority_cutoff"] else perf_templates["vocal_notes_low"],
            "breath_notes": perf_templates["breath_notes_high"].format(avg_len=avg_len) if breath_score > self._thresholds["priority_cutoff"] else perf_templates["breath_notes_low"],
            "dramatic_notes": perf_templates["dramatic_notes_high"] if dramatic_score > self._thresholds["priority_cutoff"] else perf_templates["dramatic_notes_low"],
            "engagement_notes": perf_templates["engagement_notes"],
            "recommendations": perf_templates["recommendations"]
        }

    def _generate_minimal_corrected(self) -> Optional[str]:
        """Generate minimally corrected version"""
        from app.services.additional_analysis import TextCorrector
        corrector = TextCorrector()
        result = corrector.correct(self.text)
        return result.get("corrected_text", self.text)

    def _generate_polished_version(self) -> Optional[str]:
        """Generate polished/enhanced version"""
        from app.services.additional_analysis import TextCorrector
        corrector = TextCorrector()
        result = corrector.enhance(self.text)
        return result.get("enhanced_text", self.text)


def generate_executive_summary(metrics: Dict[str, Any], ratings: Dict[str, Any]) -> str:
    """Generate executive summary of analysis"""
    quantitative = metrics.get("quantitative", {})
    structural = quantitative.get("structural_metrics", {})
    overall = ratings.get("overall_quality", 5)

    total_lines = structural.get("total_lines", "several")

    rules = get_evaluation_rules()
    templates = rules["templates"]["summary"]
    thresholds = rules["thresholds"]
    if overall >= thresholds["overall_excellent"]:
        quality = templates["quality_excellent"]
    elif overall >= thresholds["overall_good"]:
        quality = templates["quality_good"]
    else:
        quality = templates["quality_fair"]

    return templates["template"].format(
        total_lines=total_lines,
        overall=overall,
        quality=quality,
        technical=ratings.get("technical_craft", 0),
        imagery=ratings.get("imagery_voice", 0)
    )


def generate_educational_insight(metrics: Dict[str, Any]) -> str:
    """Generate educational insight based on analysis"""
    prosody = metrics.get("prosody", {})
    meter = prosody.get("meter", {})

    rules = get_evaluation_rules()
    templates = rules["templates"]["education"]
    thresholds = rules["thresholds"]
    detected = meter.get("detected_meter", "free verse")
    regularity = meter.get("metrical_regularity", 0)
    pattern = "da-DUM" if "iamb" in detected else "DUM-da"

    if detected != "free verse" and regularity < thresholds["metrical_regularity_mid"]:
        return templates["meter_template"].format(
            meter=detected,
            regularity=regularity,
            pattern=pattern
        )
    return templates["default"]
