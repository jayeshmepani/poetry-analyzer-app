"""
Workspace Controller
Handles all primary workspace routes
"""

from fastapi import Request, HTTPException, Depends
from controllers.base_controller import BaseController
from fastapi.templating import Jinja2Templates
from typing import Dict, Any, List, Optional
from app.database import SessionLocal
from app.models.db_models import AnalysisResult, UserSettings, User
from routes.web import get_current_user
from datetime import datetime
import uuid
import json
from pathlib import Path


class WorkspaceController(BaseController):
    """
    Controller for workspace routes
    """

    def __init__(self, templates: Jinja2Templates):
        super().__init__(templates)

    @staticmethod
    def _infer_language_from_text(text: str) -> str:
        txt = text or ""
        deva = sum(1 for ch in txt if "\u0900" <= ch <= "\u097F")
        arab = sum(1 for ch in txt if "\u0600" <= ch <= "\u06FF")
        latin = sum(1 for ch in txt if ("a" <= ch.lower() <= "z"))
        if deva >= arab and deva >= latin and deva > 0:
            return "hi"
        if arab >= deva and arab >= latin and arab > 0:
            return "ur"
        return "en"

    @staticmethod
    def _analysis_language(selected_language: str) -> str:
        """
        Map UI language varieties/dialects to supported backend analyzer codes.
        """
        lang = (selected_language or "en").strip().lower()
        alias_map = {
            # Legacy selections kept for backward compatibility
            "en": "en",
            "hi": "hi",
            "gu": "gu",
            "ur": "ur",
            "mr": "hi",
            "bn": "hi",
            "sa": "hi",
            "ur_deva": "ur",
            "brj_deva": "hi",
            # English timeline, regional and literary varieties
            "en_old": "en",
            "en_middle": "en",
            "en_modern": "en",
            "en_british": "en",
            "en_american": "en",
            "en_australian": "en",
            "en_indian": "en",
            "en_south_african": "en",
            "en_caribbean": "en",
            "en_scots": "en",
            "en_aave": "en",
            "en_cockney": "en",
            "en_southern_us": "en",
            "en_geordie": "en",
            "en_creole": "en",
            # Hindi literary dialects
            "hi_braj": "hi",
            "hi_awadhi": "hi",
            "hi_maithili": "hi",
            "hi_sadhukkari": "hi",
            "hi_khariboli": "hi",
            # Gujarati literary dialects
            "gu_kathiawadi": "gu",
            "gu_charotari": "gu",
            "gu_surati": "gu",
            "gu_old": "gu",
            # Urdu variations
            "ur_standard": "ur",
            "ur_dakhni": "ur",
            "ur_rekhta": "ur",
            "ur_dhakaiya": "ur",
            # Hybrid/contact forms
            "hinglish": "hi",
        }
        return alias_map.get(lang, "en")

    async def dashboard(self, request: Request):
        """
        Dashboard
        GET /dashboard
        """
        return self.view("workspace/dashboard.html", request)

    async def analyze(self, request: Request):
        """
        Analyze Poem Page
        GET /analyze
        """
        return self.view("workspace/analyze.html", request)

    async def batch(self, request: Request):
        """
        Batch Analysis Page
        GET /batch
        """
        return self.view("workspace/batch.html", request)

    async def results(self, request: Request):
        """
        Analysis Results Page
        GET /results
        """
        return self.view("workspace/results.html", request)

    async def result_report(self, request: Request, result_id: str):
        """
        Analysis Result Report Page
        GET /results/{result_id}
        """
        return self.view("workspace/result_detail.html", request, {"result_id": result_id})

    async def database_status(self, request: Request):
        """
        Database Status Page
        GET /database
        """
        return self.view("workspace/database.html", request)

    async def theory(self, request: Request):
        """
        Literary Theory Page
        GET /theory
        """
        return self.view("workspace/theory.html", request)

    async def touchstone(self, request: Request):
        """
        Touchstone Comparison Page
        GET /touchstone
        """
        return self.view("workspace/touchstone.html", request)

    async def constraints(self, request: Request):
        """
        Oulipo Constraints Page
        GET /constraints
        """
        return self.view("workspace/constraints.html", request)

    async def performance(self, request: Request):
        """
        Performance Analysis Page
        GET /performance
        """
        return self.view("workspace/performance.html", request)

    async def rubrics(self, request: Request):
        """
        Evaluation Rubrics Page
        GET /rubrics
        """
        return self.view("workspace/rubrics.html", request)

    async def comparator(self, request: Request):
        """
        Text Comparator Page
        GET /comparator
        """
        return self.view("workspace/comparator.html", request)

    async def forms(self, request: Request):
        """
        Poetic Forms Reference Page
        GET /forms
        """
        return self.view("workspace/forms.html", request)

    async def meters(self, request: Request):
        """
        Meters Reference Page
        GET /meters
        """
        return self.view("workspace/meters.html", request)

    async def rasas(self, request: Request):
        """
        Rasas Reference Page
        GET /rasas
        """
        return self.view("workspace/rasas.html", request)

    async def settings(self, request: Request):
        """
        Settings Page
        GET /settings
        """
        return self.view("workspace/settings.html", request)

    # ==================== API ENDPOINTS (AJAX) ====================

    async def analyze_post(self, request: Request):
        """
        Submit text for analysis
        POST /analyze-run
        """
        try:
            data = await request.json()
            selected_language = (data.get("language", "en") or "en").strip().lower()
            analysis_language = self._analysis_language(selected_language)
            
            # Secure retrieve user from cookie
            from app.database import SessionLocal
            from app.models.db_models import User
            
            db = SessionLocal()
            auth_uuid = request.cookies.get("auth_uuid")
            if not auth_uuid:
                return self.error("Not authenticated", 401)
                
            user = db.query(User).filter(User.uuid == auth_uuid).first()
            if not user or user.status == 0:
                return self.error("Invalid or inactive session", 403)

            # Use REAL analysis service
            from app.services.analysis_service import create_analysis_service

            service = create_analysis_service(
                language=analysis_language,
                strictness=data.get("strictness", 8),
            )

            # Perform actual analysis
            result = service.analyze(
                text=data.get("text", ""),
                title=data.get("title", "Untitled"),
                form=data.get("form"),
            )

            # Save to database
            db = SessionLocal()
            try:
                eval_obj = result.get("evaluation", {})
                ratings_obj = eval_obj.get("ratings", {})

                db_result = AnalysisResult(
                    title=data.get("title", "Untitled"),
                    text=data.get("text", ""),
                    # Preserve user's selected label (including script variants).
                    language=selected_language,
                    poetic_form=data.get("form"),
                    strictness_level=data.get("strictness", 8),
                    word_count=len(data.get("text", "").split()),
                    line_count=len(data.get("text", "").split("\n")),
                    user_id=user.id,
                    # Map scores from analysis result
                    overall_score=eval_obj.get("overall_score", 0),
                    technical_craft_score=ratings_obj.get("technical_craft", 0),
                    language_diction_score=ratings_obj.get("language_diction", 0),
                    imagery_voice_score=ratings_obj.get("imagery_voice", 0),
                    emotional_impact_score=ratings_obj.get("emotional_impact", 0),
                    cultural_fidelity_score=ratings_obj.get("cultural_fidelity", 0),
                    originality_score=ratings_obj.get("originality", 0),
                    computational_greatness_score=ratings_obj.get(
                        "computational_greatness", 0
                    ),
                    quantitative_metrics=result.get("quantitative", {}),
                    prosody_analysis=result.get("prosody", {}),
                    linguistic_analysis=result.get("linguistic", {}),
                    literary_devices=result.get("literary_devices", {}),
                    sentiment_analysis=result.get("advanced", {}).get("sentiment", {}),
                    evaluation=eval_obj,
                    executive_summary=result.get("executive_summary", ""),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(db_result)
                db.commit()
                db.refresh(db_result)

                # Return full dictionary
                payload = {
                    **db_result.to_full_dict(),
                    "id": db_result.uuid,
                    "uuid": db_result.uuid,
                    "message": "Analysis completed and saved to database",
                }
                return self.success(payload)

            finally:
                db.close()

        except Exception as e:
            import traceback

            traceback.print_exc()
            return self.error(str(e), 500)

    async def batch_analyze_post(self, request: Request):
        """
        Batch analysis
        POST /batch-run
        """
        try:
            data = await request.json()
            items = data.get("items", [])

            if not items:
                return self.error("No items provided", 400)

            from app.services.analysis_service import create_analysis_service

            db = SessionLocal()
            results = []

            try:
                for item in items:
                    selected_language = (item.get("language", "en") or "en").strip().lower()
                    analysis_language = self._analysis_language(selected_language)
                    service = create_analysis_service(
                        language=analysis_language
                    )
                    analysis_result = service.analyze(
                        text=item.get("text", ""), title=item.get("title", "Untitled")
                    )

                    eval_obj = analysis_result.get("evaluation", {})
                    ratings_obj = eval_obj.get("ratings", {})

                    db_result = AnalysisResult(
                        title=item.get("title", "Untitled"),
                        text=item.get("text", ""),
                        language=selected_language,
                        overall_score=eval_obj.get("overall_score", 0),
                        technical_craft_score=ratings_obj.get("technical_craft", 0),
                        language_diction_score=ratings_obj.get("language_diction", 0),
                        imagery_voice_score=ratings_obj.get("imagery_voice", 0),
                        emotional_impact_score=ratings_obj.get("emotional_impact", 0),
                        cultural_fidelity_score=ratings_obj.get("cultural_fidelity", 0),
                        originality_score=ratings_obj.get("originality", 0),
                        computational_greatness_score=ratings_obj.get(
                            "computational_greatness", 0
                        ),
                        quantitative_metrics=analysis_result.get("quantitative", {}),
                        prosody_analysis=analysis_result.get("prosody", {}),
                        literary_devices=analysis_result.get("literary_devices", {}),
                        sentiment_analysis=analysis_result.get("advanced", {}).get(
                            "sentiment", {}
                        ),
                        evaluation=eval_obj,
                        executive_summary=analysis_result.get("executive_summary", ""),
                        word_count=len(item.get("text", "").split()),
                        line_count=len(item.get("text", "").split("\n")),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )

                    db.add(db_result)
                    db.flush()  # Get ID before commit
                    results.append(db_result.to_dict())

                db.commit()
                return self.success({"count": len(results), "results": results})

            finally:
                db.close()

        except Exception as e:
            import traceback

            traceback.print_exc()
            return self.error(str(e), 500)

    async def stats(self, request: Request):
        """Dashboard statistics"""
        try:
            from sqlalchemy import func
            from datetime import timedelta

            db = SessionLocal()
            try:
                total = db.query(AnalysisResult).count()
                avg_score = (
                    db.query(func.avg(AnalysisResult.overall_score)).scalar() or 0.0
                )

                by_language = (
                    db.query(AnalysisResult.language, func.count(AnalysisResult.id))
                    .group_by(AnalysisResult.language)
                    .all()
                )
                languages = {lang: count for lang, count in by_language}

                # Storage estimate
                storage_bytes = (
                    db.query(func.sum(func.length(AnalysisResult.text))).scalar() or 0
                )

                return self.success(
                    {
                        "total_analyses": total,
                        "avg_score": round(float(avg_score), 2),
                        "languages": languages,
                        "storage_mb": round(storage_bytes / 1048576, 2),
                    }
                )
            finally:
                db.close()
        except Exception as e:
            return self.error(str(e), 500)

    async def list_results(self, request: Request, user: User = Depends(get_current_user), limit: int = 50, offset: int = 0):
        """List all analysis results strictly for the current user"""
        try:
            db = SessionLocal()
            try:
                results = (
                    db.query(AnalysisResult)
                    .filter(AnalysisResult.user_id == user.id)
                    .order_by(AnalysisResult.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                    .all()
                )
                total = db.query(AnalysisResult).filter(AnalysisResult.user_id == user.id).count()
                return self.success(
                    {"results": [r.to_dict() for r in results], "total": total}
                )
            finally:
                db.close()
        except Exception as e:
            return self.error(str(e), 500)

    async def get_result(self, request: Request, result_id: str, user: User = Depends(get_current_user)):
        """Get a specific analysis result strictly for the current user"""
        try:
            db = SessionLocal()
            try:
                result = (
                    db.query(AnalysisResult)
                    .filter(AnalysisResult.uuid == result_id, AnalysisResult.user_id == user.id)
                    .first()
                )
                if not result:
                    return self.error("Result not found", 404)
                return self.success(result.to_full_dict())
            finally:
                db.close()
        except Exception as e:
            return self.error(str(e), 500)

    async def delete_result(self, request: Request, result_id: str, user: User = Depends(get_current_user)):
        """Delete a specific analysis result"""
        try:
            db = SessionLocal()
            try:
                result = (
                    db.query(AnalysisResult)
                    .filter(AnalysisResult.uuid == result_id, AnalysisResult.user_id == user.id)
                    .first()
                )
                if not result:
                    return self.error("Result not found", 404)
                db.delete(result)
                db.commit()
                return self.success({"message": "Deleted successfully"})
            finally:
                db.close()
        except Exception as e:
            return self.error(str(e), 500)

    async def clear_results(self, request: Request, user: User = Depends(get_current_user)):
        """Clear all analysis results for the CURRENT user"""
        try:
            db = SessionLocal()
            try:
                deleted_count = db.query(AnalysisResult).filter(AnalysisResult.user_id == user.id).delete()
                db.commit()
                return self.success(
                    {"deleted": deleted_count, "message": "All your history cleared"}
                )
            finally:
                db.close()
        except Exception as e:
            return self.error(str(e), 500)

    async def apply_constraint_api(self, request: Request):
        """Apply Oulipo constraint"""
        try:
            data = await request.json()
            from app.services.constraints import OulipoConstraintEngine

            engine = OulipoConstraintEngine()
            result = engine.apply_constraint(
                data.get("text", ""),
                data.get("constraint_type", "n_plus_7"),
                data.get("params", {}),
            )
            return self.success(result)
        except Exception as e:
            return self.error(str(e), 500)

    async def get_theory_recommendations(self, request: Request):
        """Theoretical definitions"""
        try:
            from app.services.literary_theory import CriticismType

            theories = [
                {
                    "id": criticism.value,
                    "name": criticism.value.replace("_", " ").title(),
                    "focus": f"{criticism.value.replace('_', ' ').title()} reading lens",
                }
                for criticism in CriticismType
            ]
            return self.success({"theories": theories})
        except Exception as e:
            return self.error(str(e), 500)

    async def analyze_with_theory_api(self, request: Request):
        """Theoretical analysis"""
        try:
            data = await request.json()
            from app.services.literary_theory import LiteraryTheoryAnalyzer
            from app.services.literary_theory import CriticismType
            from app.services.analysis_service import create_analysis_service

            analyzer = LiteraryTheoryAnalyzer()
            poem = data.get("poem", "")
            requested = data.get("theories")
            if not isinstance(requested, list) or not requested:
                single = data.get("theory", "formalism")
                requested = [single]

            valid = {c.value for c in CriticismType}
            theories = [t for t in requested if isinstance(t, str) and t in valid]
            if not theories:
                theories = ["formalism"]

            # Build dynamic support signals from the full analysis pipeline.
            support_signals: Dict[str, Any] = {"support_factor": 0.65}
            try:
                language = self._analysis_language(data.get("language", "")) if data.get("language") else self._infer_language_from_text(poem)
                pipeline = create_analysis_service(language=language, strictness=int(data.get("strictness", 7) or 7))
                full = pipeline.analyze(poem, title="Theory Probe")

                tr = (full.get("additional", {}) or {}).get("transformer_analysis", {}) or {}
                tr_supported = tr.get("status") not in ("unsupported_or_failed", "failed", None)

                lex = ((full.get("quantitative", {}) or {}).get("lexical_metrics", {}) or {})
                rhyme = ((full.get("prosody", {}) or {}).get("rhyme", {}) or {})
                schemes = ((full.get("literary_devices", {}) or {}).get("schemes", {}) or {})
                tropes = ((full.get("literary_devices", {}) or {}).get("tropes", {}) or {})

                trope_count = sum(len(v) for v in tropes.values() if isinstance(v, list))
                scheme_count = sum(len(v) for v in schemes.values() if isinstance(v, list))
                support_signals.update(
                    {
                        "support_factor": 1.0 if tr_supported else 0.7,
                        "lexical_density": float(lex.get("lexical_density", 0.0) or 0.0),
                        "ttr": float(lex.get("type_token_ratio", 0.0) or 0.0),
                        "rhyme_density": float(rhyme.get("rhyme_density", 0.0) or 0.0),
                        "trope_count": trope_count,
                        "scheme_count": scheme_count,
                        "quantitative": full.get("quantitative", {}) or {},
                        "prosody": full.get("prosody", {}) or {},
                        "linguistic": full.get("linguistic", {}) or {},
                        "literary_devices": full.get("literary_devices", {}) or {},
                        "advanced": full.get("advanced", {}) or {},
                        "additional": full.get("additional", {}) or {},
                        "structural": full.get("structural", {}) or {},
                        "sentiment_analysis": full.get("sentiment_analysis", {}) or {},
                        "evaluation": full.get("evaluation", {}) or {},
                    }
                )
            except Exception:
                # Keep endpoint responsive even if support pipeline partially fails.
                support_signals = {"support_factor": 0.65}

            analyzed = analyzer.analyze(poem, theories, signals=support_signals)
            framework_results = analyzed.get("results", {})
            aggregated_insights: List[str] = []
            for framework_id in analyzed.get("frameworks_applied", []):
                findings = framework_results.get(framework_id, {}).get("key_findings", [])
                for finding in findings[:3]:
                    aggregated_insights.append(f"[{framework_id}] {finding}")

            return self.success(
                {
                    "frameworks_applied": analyzed.get("frameworks_applied", []),
                    "framework_results": framework_results,
                    "insights": aggregated_insights[:20],
                    "interpretation": analyzed.get("synthesis", ""),
                    "synthesis": analyzed.get("synthesis", ""),
                }
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self.error(str(e), 500)

    async def analyze_touchstone_api(self, request: Request):
        """Matthew Arnold's Touchstone analysis"""
        try:
            data = await request.json()
            from app.services.advanced_analysis import AdvancedAnalysisEngine

            engine = AdvancedAnalysisEngine()
            result = engine.analyze(data.get("your_poem", ""), ["touchstone"])
            if data.get("touchstone"):
                result["reference_text"] = data.get("touchstone", "")
            return self.success(result)
        except Exception as e:
            return self.error(str(e), 500)

    async def analyze_performance_api(self, request: Request):
        """Performance suitability"""
        try:
            data = await request.json()
            from app.services.analysis_service import create_analysis_service
            from app.services.evaluation import EvaluationEngine

            metrics = create_analysis_service().analyze(data.get("poem", ""))
            return self.success(
                EvaluationEngine()._assess_performance_detailed(
                    data.get("poem", ""), metrics
                )
            )
        except Exception as e:
            return self.error(str(e), 500)

    async def generate_versions_api(self, request: Request):
        """Creative variations"""
        try:
            data = await request.json()
            from app.services.additional_analysis import run_additional_analyses

            res = run_additional_analyses(data.get("poem", ""), "en")
            return self.success(
                {
                    "original": data.get("poem", ""),
                    "corrected": res.get("text_correction", {}).get("corrected_text"),
                    "enhanced": res.get("text_enhancement", {}).get("enhanced_text"),
                }
            )
        except Exception as e:
            return self.error(str(e), 500)

    async def get_forms(self, request: Request):
        """Forms data"""
        forms_file = Path(__file__).resolve().parent.parent / "app" / "data" / "poetry_forms.json"
        with forms_file.open("r", encoding="utf-8") as f:
            forms = json.load(f)

        # Build normalized option objects for clients that need ids + labels.
        normalized = {}
        for group, names in forms.items():
            normalized[group] = [
                {"id": n.lower().replace("/", "_").replace(" ", "_").replace("-", "_"), "name": n}
                for n in names
            ]

        return self.success(
            {"forms": normalized, "source_of_truth": "final_synthesized_union_29_scope"}
        )

    async def get_meters(self, request: Request):
        """Meters data"""
        return self.success(
            {"meters": {"english": [{"id": "iambic", "name": "Iambic"}]}}
        )

    async def get_rasas(self, request: Request):
        """Rasas data"""
        return self.success({"rasas": [{"id": "shringara", "name": "Shringara"}]})

    async def database_status_api(self, request: Request):
        """DB status"""
        from app.database_verifier import DatabaseVerifier

        return self.success(DatabaseVerifier.full_status())

    async def database_init(self, request: Request):
        """Initialize database tables"""
        try:
            from app.database import init_db

            init_db()
            return self.success({"message": "Database initialized successfully"})
        except Exception as e:
            return self.error(str(e), 500)

    async def get_settings(self, request: Request, user: User = Depends(get_current_user)):
        """Settings retrieval — scoped to current user"""
        db = SessionLocal()
        try:
            settings_list = db.query(UserSettings).filter(
                UserSettings.user_id == user.id
            ).all()
            return self.success(
                {"settings": {s.setting_key: s.setting_value for s in settings_list}}
            )
        finally:
            db.close()

    async def save_settings(self, request: Request, user: User = Depends(get_current_user)):
        """Settings update — scoped to current user"""
        data = await request.json()
        db = SessionLocal()
        try:
            for key, value in data.get("settings", {}).items():
                setting = (
                    db.query(UserSettings)
                    .filter(
                        UserSettings.user_id == user.id,
                        UserSettings.setting_key == key
                    )
                    .first()
                )
                if setting:
                    setting.setting_value = value
                else:
                    db.add(UserSettings(
                        user_id=user.id,   # ← FK required
                        setting_key=key,
                        setting_value=value
                    ))
            db.commit()
            return self.success({"message": "Settings saved"})
        except Exception as e:
            db.rollback()
            return self.error(str(e), 500)
        finally:
            db.close()
