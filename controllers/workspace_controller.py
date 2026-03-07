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
import time
import logging

THEORY_TASKS: Dict[str, Dict[str, Any]] = {}
logger = logging.getLogger(__name__)


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

    @staticmethod
    def _resolve_overall_score(evaluation: Dict[str, Any], ratings: Dict[str, Any]) -> float:
        """
        Evaluation engine outputs overall under ratings.overall_quality.
        Keep compatibility with any legacy overall_score key.
        """
        raw = (
            (evaluation or {}).get("overall_score")
            if isinstance(evaluation, dict)
            else None
        )
        if raw is None and isinstance(ratings, dict):
            raw = ratings.get("overall_quality")
        try:
            if raw is None:
                return 0.0
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    @classmethod
    def _resolve_analysis_language(cls, selected_language: str, text: str) -> str:
        """
        Resolve backend analysis language from user selection + actual script evidence.
        Prevents script/language mismatches (e.g., Devanagari poem analyzed as Urdu).
        """
        mapped = cls._analysis_language(selected_language)
        inferred = cls._infer_language_from_text(text or "")

        # Trust strong script evidence for Indic scripts.
        if inferred in {"hi", "ur"} and mapped in {"hi", "ur"} and inferred != mapped:
            return inferred
        return mapped

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
            analysis_language = self._resolve_analysis_language(
                selected_language, data.get("text", "")
            )
            
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

                overall_score_value = self._resolve_overall_score(eval_obj, ratings_obj)

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
                    overall_score=overall_score_value,
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
                    sentiment_analysis=result.get("sentiment_analysis", {}),
                    evaluation=eval_obj,
                    executive_summary=result.get("executive_summary", ""),
                    # Extended analysis fields
                    theory_analysis=result.get("theory"),
                    structural_analysis=result.get("structural"),
                    stylometry_data=result.get("stylometry"),
                    competition_rubrics_data=result.get("competition_rubrics"),
                    evolutionary_data=result.get("evolutionary"),
                    educational_insight=result.get("educational_insight", ""),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(db_result)
                db.commit()
                db.refresh(db_result)

                # Return the full live analysis result merged with DB metadata
                # (live result has all keys including stylometry/theory/etc)
                payload = {
                    **result,
                    **db_result.to_full_dict(),
                    # Ensure live keys that to_full_dict() maps differently are present
                    "theory": result.get("theory"),
                    "structural": result.get("structural"),
                    "stylometry": result.get("stylometry"),
                    "competition_rubrics": result.get("competition_rubrics"),
                    "evolutionary": result.get("evolutionary"),
                    "educational_insight": result.get("educational_insight"),
                    "form_detected": result.get("form_detected"),
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

            # Authenticate user (required to set user_id on each result)
            auth_uuid = request.cookies.get("auth_uuid")
            if not auth_uuid:
                return self.error("Not authenticated", 401)
            db_auth = SessionLocal()
            try:
                user = db_auth.query(User).filter(User.uuid == auth_uuid).first()
                if not user or user.status == 0:
                    return self.error("Invalid or inactive session", 403)
                user_id = user.id
            finally:
                db_auth.close()

            from app.services.analysis_service import create_analysis_service

            db = SessionLocal()
            results = []

            try:
                for item in items:
                    selected_language = (item.get("language", "en") or "en").strip().lower()
                    analysis_language = self._resolve_analysis_language(
                        selected_language, item.get("text", "")
                    )
                    service = create_analysis_service(
                        language=analysis_language
                    )
                    analysis_result = service.analyze(
                        text=item.get("text", ""), title=item.get("title", "Untitled")
                    )

                    eval_obj = analysis_result.get("evaluation", {})
                    ratings_obj = eval_obj.get("ratings", {})

                    overall_score_value = self._resolve_overall_score(eval_obj, ratings_obj)

                    db_result = AnalysisResult(
                        title=item.get("title", "Untitled"),
                        text=item.get("text", ""),
                        language=selected_language,
                        user_id=user_id,
                        overall_score=overall_score_value,
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
                        linguistic_analysis=analysis_result.get("linguistic", {}),
                        literary_devices=analysis_result.get("literary_devices", {}),
                        sentiment_analysis=analysis_result.get("sentiment_analysis", {}),
                        evaluation=eval_obj,
                        executive_summary=analysis_result.get("executive_summary", ""),
                        # Extended fields
                        theory_analysis=analysis_result.get("theory"),
                        structural_analysis=analysis_result.get("structural"),
                        stylometry_data=analysis_result.get("stylometry"),
                        competition_rubrics_data=analysis_result.get("competition_rubrics"),
                        evolutionary_data=analysis_result.get("evolutionary"),
                        educational_insight=analysis_result.get("educational_insight", ""),
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

    async def list_results(self, request: Request, user: User = Depends(get_current_user)):
        """List analysis results for the current user with server-side table controls"""
        sortable_fields = {
            "title": AnalysisResult.title,
            "language": AnalysisResult.language,
            "poetic_form": AnalysisResult.poetic_form,
            "overall_score": AnalysisResult.overall_score,
            "word_count": AnalysisResult.word_count,
            "line_count": AnalysisResult.line_count,
            "created_at": AnalysisResult.created_at,
        }
        try:
            db = SessionLocal()
            try:
                raw_limit = request.query_params.get("limit")
                raw_offset = request.query_params.get("offset", "0")
                limit = None
                if raw_limit not in (None, "", "all", "ALL"):
                    limit = max(1, min(int(raw_limit), 200))
                offset = max(0, int(raw_offset)) if limit is not None else 0
                search = request.query_params.get("search", "").strip()
                sort = request.query_params.get("sort", "created_at").strip()
                order = request.query_params.get("order", "desc").strip().lower()

                if sort not in sortable_fields:
                    sort = "created_at"
                if order not in {"asc", "desc"}:
                    order = "desc"

                query = db.query(AnalysisResult).filter(AnalysisResult.user_id == user.id)

                if search:
                    from sqlalchemy import or_

                    query = query.filter(
                        or_(
                            AnalysisResult.title.ilike(f"%{search}%"),
                            AnalysisResult.language.ilike(f"%{search}%"),
                            AnalysisResult.poetic_form.ilike(f"%{search}%"),
                            AnalysisResult.text.ilike(f"%{search}%"),
                        )
                    )

                total = query.count()
                sort_column = sortable_fields[sort]
                query = query.order_by(
                    sort_column.desc() if order == "desc" else sort_column.asc()
                )
                if limit is not None:
                    query = query.offset(offset).limit(limit)
                results = query.all()

                rows = []
                for result in results:
                    eval_obj = result.evaluation or {}
                    ratings_obj = eval_obj.get("ratings", {}) if isinstance(eval_obj, dict) else {}
                    resolved_overall = (
                        float(result.overall_score)
                        if result.overall_score is not None and float(result.overall_score) > 0
                        else self._resolve_overall_score(eval_obj, ratings_obj)
                    )
                    rows.append(
                        {
                            "id": result.uuid,
                            "uuid": result.uuid,
                            "title": result.title or "Untitled",
                            "text_preview": (
                                (result.text[:120] + "...")
                                if result.text and len(result.text) > 120
                                else (result.text or "")
                            ),
                            "language": result.language or "en",
                            "poetic_form": result.poetic_form or "Free Verse",
                            "overall_score": resolved_overall,
                            "word_count": result.word_count or 0,
                            "line_count": result.line_count or 0,
                            "created_at": result.created_at.isoformat() if result.created_at else None,
                        }
                    )

                return self.success({"total": total, "rows": rows, "results": rows})
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
                payload = result.to_full_dict()
                eval_obj = payload.get("evaluation", {}) or {}
                ratings_obj = eval_obj.get("ratings", {}) if isinstance(eval_obj, dict) else {}
                if payload.get("overall_score") in (None, 0, 0.0):
                    payload["overall_score"] = self._resolve_overall_score(eval_obj, ratings_obj)
                return self.success(payload)
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

    async def delete_results_multiple(self, request: Request, user: User = Depends(get_current_user)):
        """Delete multiple selected analysis results for the current user"""
        try:
            data = await request.json()
            ids = data.get("ids", [])
            if not isinstance(ids, list) or not ids:
                return self.error("No results selected", 422)

            db = SessionLocal()
            try:
                deleted = (
                    db.query(AnalysisResult)
                    .filter(
                        AnalysisResult.user_id == user.id,
                        AnalysisResult.uuid.in_([str(item) for item in ids]),
                    )
                    .delete(synchronize_session=False)
                )
                db.commit()
                return self.success(
                    {"deleted": deleted, "message": f"Deleted {deleted} selected analyses"}
                )
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
            import asyncio
            import json
            from fastapi.responses import StreamingResponse
            from app.services.literary_theory import LiteraryTheoryAnalyzer
            from app.services.literary_theory import CriticismType
            from app.services.analysis_service import create_analysis_service

            data = await request.json()

            def run_analysis(payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
                total_start = time.perf_counter()
                if progress_cb:
                    progress_cb(10, "Validating inputs...")
                analyzer = LiteraryTheoryAnalyzer()
                poem = payload.get("poem", "")
                requested = payload.get("theories")
                if not isinstance(requested, list) or not requested:
                    single = payload.get("theory", "formalism")
                    requested = [single]

                valid = {c.value for c in CriticismType}
                theories = [t for t in requested if isinstance(t, str) and t in valid]
                if not theories:
                    theories = ["formalism"]

                if progress_cb:
                    progress_cb(20, "Preparing analysis pipeline...")
                # Build dynamic support signals from the full analysis pipeline.
                support_signals: Dict[str, Any] = {}
                try:
                    language = (
                        self._resolve_analysis_language(payload.get("language", ""), poem)
                        if payload.get("language")
                        else self._infer_language_from_text(poem)
                    )
                    if progress_cb:
                        progress_cb(30, "Running linguistic analysis...")
                    pipeline = create_analysis_service(language=language, strictness=int(payload.get("strictness", 7) or 7))
                    pipeline_start = time.perf_counter()
                    full = pipeline.analyze(
                        poem,
                        title="Theory Probe",
                        enable_all=False,
                        progress_cb=progress_cb,
                    )
                    pipeline_time = time.perf_counter() - pipeline_start
                    logger.info("[theory] pipeline.analyze completed in %.2fs", pipeline_time)
                    if progress_cb:
                        progress_cb(60, f"Pipeline complete ({pipeline_time:.1f}s). Building theory synthesis...")

                    lex = ((full.get("quantitative", {}) or {}).get("lexical_metrics", {}) or {})
                    rhyme = ((full.get("prosody", {}) or {}).get("rhyme", {}) or {})
                    schemes = ((full.get("literary_devices", {}) or {}).get("schemes", {}) or {})
                    tropes = ((full.get("literary_devices", {}) or {}).get("tropes", {}) or {})

                    trope_count = sum(len(v) for v in tropes.values() if isinstance(v, list))
                    scheme_count = sum(len(v) for v in schemes.values() if isinstance(v, list))

                    support_signals.update(
                        {
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
                    support_signals = {}

                if progress_cb:
                    progress_cb(75, "Synthesizing theory outputs...")
                theory_start = time.perf_counter()
                analyzed = analyzer.analyze(poem, theories, signals=support_signals)
                theory_time = time.perf_counter() - theory_start
                logger.info("[theory] theory.analyze completed in %.2fs", theory_time)
                if progress_cb:
                    progress_cb(90, f"Theory synthesis complete ({theory_time:.1f}s). Finalizing...")
                framework_results = analyzed.get("results", {})
                aggregated_insights: List[str] = []
                for framework_id in analyzed.get("frameworks_applied", []):
                    findings = framework_results.get(framework_id, {}).get("key_findings", [])
                    for finding in findings[:3]:
                        aggregated_insights.append(f"[{framework_id}] {finding}")

                return {
                    "frameworks_applied": analyzed.get("frameworks_applied", []),
                    "framework_results": framework_results,
                    "insights": aggregated_insights[:20],
                    "interpretation": analyzed.get("synthesis", ""),
                    "synthesis": analyzed.get("synthesis", ""),
                }

            if request.query_params.get("async") == "1":
                job_id = str(uuid.uuid4())
                THEORY_TASKS[job_id] = {
                    "status": "running",
                    "percent": 5,
                    "message": "Queued...",
                    "result": None,
                    "error": None,
                    "updated": time.time(),
                }

                def update_job(pct: int, message: str) -> None:
                    task = THEORY_TASKS.get(job_id)
                    if not task:
                        return
                    task["percent"] = int(pct)
                    task["message"] = message
                    task["updated"] = time.time()

                async def runner():
                    try:
                        result = await asyncio.to_thread(run_analysis, data, update_job)
                        task = THEORY_TASKS.get(job_id)
                        if task is not None:
                            task["status"] = "done"
                            task["percent"] = 100
                            task["message"] = "Complete."
                            task["result"] = result
                            task["updated"] = time.time()
                    except Exception as e:
                        task = THEORY_TASKS.get(job_id)
                        if task is not None:
                            task["status"] = "error"
                            task["error"] = str(e)
                            task["message"] = "Not completed."
                            task["updated"] = time.time()

                asyncio.create_task(runner())
                return self.success({"job_id": job_id})

            if request.query_params.get("status") == "1":
                job_id = request.query_params.get("job_id", "")
                task = THEORY_TASKS.get(job_id)
                if not task:
                    return self.error("Job not found", 404)
                return self.success({
                    "status": task["status"],
                    "percent": task["percent"],
                    "message": task["message"],
                    "result": task["result"],
                    "error": task["error"],
                })

            if request.query_params.get("stream") == "1":
                async def event_stream():
                    def sse(event: str, payload: Dict[str, Any]) -> str:
                        return f"event: {event}\\ndata: {json.dumps(payload)}\\n\\n"

                    try:
                        yield sse("progress", {"percent": 5, "message": "Validating request..."})
                        await asyncio.sleep(0.1)
                        yield sse("progress", {"percent": 15, "message": "Preparing theory engines..."})

                        task = asyncio.create_task(asyncio.to_thread(run_analysis, data))
                        progress = 20
                        keepalive_tick = 0
                        while not task.done():
                            await asyncio.sleep(1)
                            progress = min(progress + 5, 90)
                            yield sse("progress", {"percent": progress, "message": "Running theoretical synthesis..."})
                            keepalive_tick += 1
                            if keepalive_tick % 5 == 0:
                                yield ": keep-alive\\n\\n"

                        result = await task
                        yield sse("progress", {"percent": 95, "message": "Finalizing results..."})
                        yield sse("done", result)
                    except Exception as stream_err:
                        yield sse("error", {"message": str(stream_err)})
                        yield ": close\\n\\n"

                return StreamingResponse(
                    event_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "X-Accel-Buffering": "no",
                        "Connection": "keep-alive",
                    },
                )

            payload = await asyncio.to_thread(run_analysis, data, None)
            return self.success(payload)
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
        data_root = Path(__file__).resolve().parent.parent / "data" / "prosody"

        try:
            with (data_root / "meter_patterns.json").open("r", encoding="utf-8") as f:
                english_patterns = json.load(f)
            with (data_root / "chhand_patterns.json").open("r", encoding="utf-8") as f:
                hindi_chhands = json.load(f)
            with (data_root / "bahr_patterns.json").open("r", encoding="utf-8") as f:
                urdu_bahrs = json.load(f)
            with (data_root / "gujarati_chhands.json").open("r", encoding="utf-8") as f:
                gujarati_chhands = json.load(f)
        except Exception as e:
            return self.error(f"Could not load prosody references: {e}", 500)

        english = [
            {
                "id": key,
                "name": value.get("name", key.replace("_", " ").title()),
                "pattern": " ".join(value.get("pattern", [])),
                "description": value.get("description", ""),
                "feet_name": value.get("feet_name", ""),
            }
            for key, value in english_patterns.items()
        ]
        hindi = [
            {
                "id": key,
                "name": key.replace("_", " ").title(),
                "matra": value.get("matra", []),
                "charan": value.get("charan"),
                "description": value.get("description", ""),
            }
            for key, value in hindi_chhands.items()
        ]
        urdu = [
            {
                "id": key,
                "name": key.replace("_", " ").title(),
                "pattern": value.get("pattern", ""),
                "feet": value.get("feet", []),
                "description": value.get("description", ""),
            }
            for key, value in urdu_bahrs.items()
        ]
        gujarati = [
            {
                "id": key,
                "name": key.replace("_", " ").title(),
                "matra": value.get("matra", []),
                "description": value.get("description", ""),
            }
            for key, value in gujarati_chhands.items()
        ]

        return self.success(
            {
                "meters": {
                    "english": english,
                    "hindi": hindi,
                    "urdu": urdu,
                    "gujarati": gujarati,
                },
                "source_of_truth": "data/prosody/*.json",
            }
        )

    async def get_rasas(self, request: Request):
        """Rasas data"""
        rasas = [
            {
                "id": "shringara",
                "name": "Shringara",
                "sanskrit": "श्रृंगार",
                "emotion": "Love / Beauty / Romance",
                "color": "Light Green",
                "deity": "Vishnu",
            },
            {
                "id": "hasya",
                "name": "Hasya",
                "sanskrit": "हास्य",
                "emotion": "Laughter / Comedy / Humor",
                "color": "White",
                "deity": "Shiva",
            },
            {
                "id": "karuna",
                "name": "Karuna",
                "sanskrit": "करुण",
                "emotion": "Compassion / Sorrow / Pathos",
                "color": "Grey",
                "deity": "Yama",
            },
            {
                "id": "raudra",
                "name": "Raudra",
                "sanskrit": "रौद्र",
                "emotion": "Fury / Anger / Rage",
                "color": "Red",
                "deity": "Kali / Rudra",
            },
            {
                "id": "veera",
                "name": "Veera",
                "sanskrit": "वीर",
                "emotion": "Heroism / Courage / Valor",
                "color": "Orange",
                "deity": "Rama / Indra",
            },
            {
                "id": "bhayanaka",
                "name": "Bhayanaka",
                "sanskrit": "भयानक",
                "emotion": "Terror / Fear / Horror",
                "color": "Black",
                "deity": "Kala",
            },
            {
                "id": "bibhatsa",
                "name": "Bibhatsa",
                "sanskrit": "बीभत्स",
                "emotion": "Disgust / Revulsion",
                "color": "Blue",
                "deity": "Brahma",
            },
            {
                "id": "adbhuta",
                "name": "Adbhuta",
                "sanskrit": "अद्भुत",
                "emotion": "Wonder / Awe / Marvelous",
                "color": "Yellow",
                "deity": "Vishnu",
            },
            {
                "id": "shanta",
                "name": "Shanta",
                "sanskrit": "शांत",
                "emotion": "Peace / Serenity / Tranquility",
                "color": "White-Blue",
                "deity": "Shiva",
            },
        ]
        return self.success(
            {
                "rasas": rasas,
                "source_of_truth": "Bharata Natyashastra navarasa canon",
            }
        )

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

    async def backend_symbols_api(self, request: Request):
        """Backend symbol coverage summary"""
        try:
            from app.symbol_registry import summarize_symbol_registry

            return self.success(summarize_symbol_registry())
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
