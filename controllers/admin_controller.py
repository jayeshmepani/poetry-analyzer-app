"""
Admin Controller
Handles all admin dashboard routes
"""

from fastapi import Request, HTTPException
from controllers.base_controller import BaseController
from fastapi.templating import Jinja2Templates
from typing import Optional


class AdminController(BaseController):
    """
    Controller for admin dashboard routes
    All /admin/* routes are handled here
    """

    def __init__(self, templates: Jinja2Templates):
        super().__init__(templates)

    # ==================== PAGE ROUTES ====================

    async def dashboard(self, request: Request):
        """
        Admin Dashboard
        GET /admin
        """
        return self.view("admin/dashboard.html", request)

    async def analyze(self, request: Request):
        """
        Analysis Form Page
        GET /admin/analyze
        """
        return self.view("admin/analyze.html", request)

    async def batch(self, request: Request):
        """
        Batch Analysis Page
        GET /admin/batch
        """
        return self.view("admin/batch.html", request)

    async def results(self, request: Request):
        """
        Results History Page
        GET /admin/results
        """
        return self.view("admin/results.html", request)

    async def forms(self, request: Request):
        """
        Poetic Forms Reference
        GET /admin/forms
        """
        return self.view("admin/forms.html", request)

    async def meters(self, request: Request):
        """
        Meters & Prosody Reference
        GET /admin/meters
        """
        return self.view("admin/meters.html", request)

    async def rasas(self, request: Request):
        """
        Navarasa Reference
        GET /admin/rasas
        """
        return self.view("admin/rasas.html", request)

    async def settings(self, request: Request):
        """
        Settings Page
        GET /admin/settings
        """
        return self.view("admin/settings.html", request)

    async def database_status(self, request: Request):
        """
        Database Status Page
        GET /admin/database
        """
        return self.view("admin/database.html", request)

    # ==================== API ENDPOINTS (AJAX) ====================

    async def analyze_post(self, request: Request):
        """
        Submit text for analysis
        POST /api/analyze

        Performs REAL analysis and saves to database
        """
        try:
            data = await request.json()
            from app.database import SessionLocal
            from app.models.db_models import AnalysisResult
            from datetime import datetime

            # Use REAL analysis service
            from app.services.analysis_service import create_analysis_service

            service = create_analysis_service(
                language=data.get("language", "en"),
                strictness=data.get("strictness", 8),
            )

            # Perform actual analysis (not async)
            result = service.analyze(
                text=data.get("text", ""),
                title=data.get("title", "Untitled"),
                form=data.get("form"),
            )

            # Save to database
            db = SessionLocal()
            try:
                db_result = AnalysisResult(
                    title=data.get("title", "Untitled"),
                    text=data.get("text", ""),
                    language=data.get("language", "en"),
                    poetic_form=data.get("form"),
                    strictness_level=data.get("strictness", 8),
                    word_count=len(data.get("text", "").split()),
                    line_count=len(data.get("text", "").split("\n")),
                    # Map scores from analysis result
                    overall_score=result.get("evaluation", {})
                    .get("ratings", {})
                    .get("overall_quality", 0),
                    technical_craft_score=result.get("evaluation", {})
                    .get("ratings", {})
                    .get("technical_craft", 0),
                    language_diction_score=result.get("evaluation", {})
                    .get("ratings", {})
                    .get("language_diction", 0),
                    imagery_voice_score=result.get("evaluation", {})
                    .get("ratings", {})
                    .get("imagery_voice", 0),
                    emotional_impact_score=result.get("evaluation", {})
                    .get("ratings", {})
                    .get("emotional_impact", 0),
                    cultural_fidelity_score=result.get("evaluation", {})
                    .get("ratings", {})
                    .get("cultural_fidelity", 0),
                    originality_score=result.get("evaluation", {})
                    .get("ratings", {})
                    .get("originality", 0),
                    quantitative_metrics=result.get("quantitative_metrics", {}),
                    prosody_analysis=result.get("prosody_analysis", {}),
                    literary_devices=result.get("literary_devices", {}),
                    sentiment_analysis=result.get("sentiment_analysis", {}),
                    evaluation=result.get("evaluation", {}),
                    executive_summary=result.get("executive_summary", ""),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(db_result)
                db.commit()
                db.refresh(db_result)

                # Return complete result with database ID
                return self.success(
                    {
                        "id": db_result.uuid,
                        "executive_summary": db_result.executive_summary,
                        "evaluation": {
                            "overall_score": db_result.overall_score,
                            "publishability": db_result.evaluation.get(
                                "publishability", {}
                            ),
                            "ratings": {
                                "technical_craft": db_result.technical_craft_score,
                                "language_diction": db_result.language_diction_score,
                                "imagery_voice": db_result.imagery_voice_score,
                                "emotional_impact": db_result.emotional_impact_score,
                                "cultural_fidelity": db_result.cultural_fidelity_score,
                                "originality": db_result.originality_score,
                                "computational_greatness": result.get("evaluation", {})
                                .get("ratings", {})
                                .get("computational_greatness", 0),
                            },
                        },
                        "quantitative_metrics": db_result.quantitative_metrics,
                        "prosody_analysis": db_result.prosody_analysis,
                        "literary_devices": db_result.literary_devices,
                        "sentiment_analysis": db_result.sentiment_analysis,
                        "message": "Analysis completed and saved to database",
                    }
                )

            finally:
                db.close()

        except Exception as e:
            import traceback

            traceback.print_exc()
            return self.error(str(e), 500)

    async def batch_analyze_post(self, request: Request):
        """
        Batch analysis
        POST /api/analyze/batch

        Performs REAL analysis on multiple texts
        """
        try:
            data = await request.json()
            items = data.get("items", [])

            if not items:
                return self.error("No items provided", 400)

            if len(items) > 10:
                return self.error("Maximum 10 items per batch", 400)

            from app.database import SessionLocal
            from app.models.db_models import AnalysisResult
            from datetime import datetime
            from app.services.analysis_service import create_analysis_service

            db = SessionLocal()
            results = []

            try:
                for item in items:
                    # Perform REAL analysis
                    service = create_analysis_service(
                        language=item.get("language", "en"), strictness=8
                    )

                    analysis_result = await service.analyze(
                        text=item.get("text", ""), title=item.get("title", "Untitled")
                    )

                    # Save to database
                    db_result = AnalysisResult(
                        title=item.get("title", "Untitled"),
                        text=item.get("text", ""),
                        language=item.get("language", "en"),
                        overall_score=analysis_result.get("evaluation", {}).get(
                            "overall_score", 0
                        ),
                        technical_craft_score=analysis_result.get("evaluation", {})
                        .get("ratings", {})
                        .get("technical_craft", 0),
                        language_diction_score=analysis_result.get("evaluation", {})
                        .get("ratings", {})
                        .get("language_diction", 0),
                        imagery_voice_score=analysis_result.get("evaluation", {})
                        .get("ratings", {})
                        .get("imagery_voice", 0),
                        emotional_impact_score=analysis_result.get("evaluation", {})
                        .get("ratings", {})
                        .get("emotional_impact", 0),
                        cultural_fidelity_score=analysis_result.get("evaluation", {})
                        .get("ratings", {})
                        .get("cultural_fidelity", 0),
                        originality_score=analysis_result.get("evaluation", {})
                        .get("ratings", {})
                        .get("originality", 0),
                        quantitative_metrics=analysis_result.get(
                            "quantitative_metrics", {}
                        ),
                        prosody_analysis=analysis_result.get("prosody_analysis", {}),
                        literary_devices=analysis_result.get("literary_devices", {}),
                        sentiment_analysis=analysis_result.get(
                            "sentiment_analysis", {}
                        ),
                        evaluation=analysis_result.get("evaluation", {}),
                        executive_summary=analysis_result.get("executive_summary", ""),
                        word_count=len(item.get("text", "").split()),
                        line_count=len(item.get("text", "").split("\n")),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )

                    db.add(db_result)
                    results.append(db_result.to_dict())

                db.commit()

                return self.success(
                    {
                        "count": len(results),
                        "results": results,
                        "message": f"Analyzed {len(results)} texts successfully",
                    }
                )

            finally:
                db.close()

        except Exception as e:
            import traceback

            traceback.print_exc()
            return self.error(str(e), 500)

    async def stats(self, request: Request):
        """
        Get dashboard statistics from database
        GET /api/stats
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import AnalysisResult
            from sqlalchemy import func
            from datetime import datetime, timedelta

            db = SessionLocal()
            try:
                # Total analyses
                total = db.query(AnalysisResult).count()

                # Average score
                avg_result = db.query(func.avg(AnalysisResult.overall_score)).scalar()
                avg_score = float(avg_result) if avg_result else 0.0

                # By language
                by_language = (
                    db.query(AnalysisResult.language, func.count(AnalysisResult.id))
                    .group_by(AnalysisResult.language)
                    .all()
                )

                languages = {lang: count for lang, count in by_language}

                # Analyses by day (last 7 days)
                analyses_by_day = []
                for i in range(6, -1, -1):
                    day = datetime.utcnow().date() - timedelta(days=i)
                    day_start = datetime.combine(day, datetime.min.time())
                    day_end = datetime.combine(day, datetime.max.time())
                    count = (
                        db.query(AnalysisResult)
                        .filter(
                            AnalysisResult.created_at >= day_start,
                            AnalysisResult.created_at <= day_end,
                        )
                        .count()
                    )
                    analyses_by_day.append(count)

                # Recent analyses
                recent_results = (
                    db.query(AnalysisResult)
                    .order_by(AnalysisResult.created_at.desc())
                    .limit(5)
                    .all()
                )
                recent = [
                    {
                        "id": r.id,
                        "uuid": str(r.uuid),
                        "title": r.title or "Untitled",
                        "text": r.text[:100] + "..."
                        if r.text and len(r.text) > 100
                        else r.text,
                        "language": r.language,
                        "score": r.overall_score,
                        "created_at": r.created_at.isoformat()
                        if r.created_at
                        else None,
                    }
                    for r in recent_results
                ]

                # Recent (24h)
                day_ago = datetime.utcnow() - timedelta(days=1)
                recent_24h = (
                    db.query(AnalysisResult)
                    .filter(AnalysisResult.created_at >= day_ago)
                    .count()
                )

                # Storage estimate
                storage_result = db.query(
                    func.sum(func.length(AnalysisResult.text))
                ).scalar()
                storage_bytes = storage_result or 0

                return self.success(
                    {
                        "total_analyses": total,
                        "avg_score": round(avg_score, 2),
                        "languages": languages,
                        "analyses_by_day": analyses_by_day,
                        "recent": recent,
                        "recent_24h": recent_24h,
                        "storage_bytes": storage_bytes,
                        "storage_mb": round(storage_bytes / 1048576, 2),
                    }
                )

            finally:
                db.close()

        except Exception as e:
            return self.error(str(e), 500)

    async def list_results(self, request: Request, limit: int = 20, offset: int = 0):
        """
        List all analysis results from database
        GET /api/results
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import AnalysisResult

            db = SessionLocal()
            try:
                results = (
                    db.query(AnalysisResult)
                    .order_by(AnalysisResult.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                    .all()
                )

                total = db.query(AnalysisResult).count()

                return self.success(
                    {
                        "results": [r.to_dict() for r in results],
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                    }
                )

            finally:
                db.close()

        except Exception as e:
            return self.error(str(e), 500)

    async def get_result(self, request: Request, result_id: str):
        """
        Get single result by UUID from database
        GET /api/result/{result_id}
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import AnalysisResult

            db = SessionLocal()
            try:
                result = (
                    db.query(AnalysisResult)
                    .filter(AnalysisResult.uuid == result_id)
                    .first()
                )

                if not result:
                    return self.error("Result not found", 404)

                return self.success(result.to_full_dict())

            finally:
                db.close()

        except Exception as e:
            return self.error(str(e), 500)

    async def get_visualization(self, request: Request, result_id: str):
        """
        Get visualization data for a result
        GET /api/visualize/{result_id}
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import AnalysisResult

            db = SessionLocal()
            try:
                result = (
                    db.query(AnalysisResult)
                    .filter(AnalysisResult.uuid == result_id)
                    .first()
                )

                if not result:
                    return self.error("Result not found", 404)

                # Build visualization data
                advanced = (
                    result.evaluation.get("advanced", {})
                    if isinstance(result.evaluation, dict)
                    else {}
                )
                literary = (
                    result.literary_devices
                    if isinstance(result.literary_devices, dict)
                    else {}
                )
                eval_data = (
                    result.evaluation if isinstance(result.evaluation, dict) else {}
                )
                quant = (
                    result.quantitative_metrics
                    if isinstance(result.quantitative_metrics, dict)
                    else {}
                )
                prosody = (
                    result.prosody_analysis
                    if isinstance(result.prosody_analysis, dict)
                    else {}
                )

                sentiment = (
                    result.sentiment_analysis
                    if isinstance(result.sentiment_analysis, dict)
                    else {}
                )
                if not sentiment and "sentiment" in advanced:
                    sentiment = advanced["sentiment"]

                viz_data = {
                    "sentiment_arc": sentiment.get("sentiment_arc", []),
                    "ratings": eval_data.get("ratings", {}),
                    "emotion_distribution": sentiment.get("emotion_distribution", {}),
                    "rasa_distribution": literary.get("rasa_vector", {}),
                    "syllable_distribution": quant.get("syllable_metrics", {}).get(
                        "syllable_distribution", {}
                    ),
                    "word_length_distribution": quant.get("word_metrics", {}).get(
                        "word_length_distribution", {}
                    ),
                    "meter_distribution": prosody.get("meter", {}).get(
                        "foot_count_distribution", {}
                    ),
                    "lexical_diversity": {
                        "TTR": quant.get("lexical_metrics", {}).get(
                            "type_token_ratio", 0
                        ),
                        "MATTR": quant.get("lexical_metrics", {}).get("mattr", 0),
                        "MTLD": quant.get("lexical_metrics", {}).get("mtld", 0)
                        / 100.0,  # normalized
                    },
                }

                return self.success(viz_data)

            finally:
                db.close()

        except Exception as e:
            return self.error(str(e), 500)

    async def delete_result(self, request: Request, result_id: str):
        """
        Delete result from database
        DELETE /api/result/{result_id}
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import AnalysisResult

            db = SessionLocal()
            try:
                result = (
                    db.query(AnalysisResult)
                    .filter(AnalysisResult.uuid == result_id)
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

    async def clear_results(self, request: Request):
        """
        Clear all results from database
        POST /api/clear-results
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import AnalysisResult

            db = SessionLocal()
            try:
                count = db.query(AnalysisResult).count()
                db.query(AnalysisResult).delete()
                db.commit()

                return self.success(
                    {"message": f"Cleared {count} results", "count": count}
                )

            finally:
                db.close()

        except Exception as e:
            return self.error(str(e), 500)

    # ==================== REFERENCE DATA ====================

    async def get_forms(self, request: Request):
        """
        Get poetic forms reference data
        GET /api/forms
        """
        forms = {
            "english": [
                {
                    "id": "sonnet",
                    "name": "Sonnet",
                    "description": "14 lines, iambic pentameter",
                },
                {
                    "id": "villanelle",
                    "name": "Villanelle",
                    "description": "19 lines, A1bA2 pattern",
                },
                {
                    "id": "haiku",
                    "name": "Haiku",
                    "description": "3 lines, 5-7-5 syllables",
                },
                {"id": "limerick", "name": "Limerick", "description": "5 lines, AABBA"},
            ],
            "hindi": [
                {
                    "id": "doha",
                    "name": "दोहा (Doha)",
                    "description": "24 matras per line",
                },
                {
                    "id": "chaupai",
                    "name": "चौपाई (Chaupai)",
                    "description": "16 matras per line",
                },
            ],
        }
        return self.success({"forms": forms})

    async def get_meters(self, request: Request):
        """
        Get metrical patterns reference
        GET /api/meters
        """
        meters = {
            "english": [
                {"id": "iambic", "name": "Iambic", "pattern": "da-DUM"},
                {"id": "trochaic", "name": "Trochaic", "pattern": "DUM-da"},
                {"id": "anapestic", "name": "Anapestic", "pattern": "da-da-DUM"},
                {"id": "dactylic", "name": "Dactylic", "pattern": "DUM-da-da"},
            ]
        }
        return self.success({"meters": meters})

    async def get_rasas(self, request: Request):
        """
        Get Navarasa reference data
        GET /api/rasas
        """
        rasas = [
            {"id": "shringara", "name": "शृंगार", "emotion": "Love, Beauty"},
            {"id": "hasya", "name": "हास्य", "emotion": "Laughter, Joy"},
            {"id": "karuna", "name": "करुण", "emotion": "Compassion, Sorrow"},
            {"id": "raudra", "name": "रौद्र", "emotion": "Anger, Fury"},
            {"id": "veera", "name": "वीर", "emotion": "Heroism, Courage"},
            {"id": "bhayanaka", "name": "भयानक", "emotion": "Fear, Terror"},
            {"id": "bibhatsa", "name": "बीभत्स", "emotion": "Disgust"},
            {"id": "adbhuta", "name": "अद्भुत", "emotion": "Wonder"},
            {"id": "shanta", "name": "शांत", "emotion": "Peace"},
        ]
        return self.success({"rasas": rasas})

    # ==================== DATABASE API ====================

    async def database_status_api(self, request: Request):
        """
        Get database status
        GET /api/database/status
        """
        try:
            from app.database_verifier import DatabaseVerifier

            status = DatabaseVerifier.full_status()
            return self.success(status)
        except Exception as e:
            return self.error(str(e), 500)

    async def database_init(self, request: Request):
        """
        Initialize database
        POST /api/database/initialize
        """
        try:
            from app.database_verifier import init_database

            success = init_database()

            if success:
                return self.success({"message": "Database initialized successfully"})
            else:
                return self.error("Database initialization failed", 500)
        except Exception as e:
            return self.error(str(e), 500)

    # ==================== SETTINGS API ====================

    async def get_settings(self, request: Request):
        """
        Get user settings
        GET /api/settings
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import UserSettings

            db = SessionLocal()
            try:
                settings_list = db.query(UserSettings).all()
                settings = {s.setting_key: s.setting_value for s in settings_list}

                # Default settings if none exist
                if not settings:
                    settings = {
                        "default_language": "en",
                        "default_strictness": 8,
                        "enable_prosody": True,
                        "enable_literary_devices": True,
                        "enable_sentiment": True,
                        "enable_rasa": False,  # Default off
                    }

                return self.success({"settings": settings})

            finally:
                db.close()

        except Exception as e:
            return self.error(str(e), 500)

    async def save_settings(self, request: Request):
        """
        Save user settings
        POST /api/settings
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import UserSettings
            from datetime import datetime

            data = await request.json()
            settings = data.get("settings", {})

            db = SessionLocal()
            try:
                for key, value in settings.items():
                    # Upsert setting
                    setting = (
                        db.query(UserSettings)
                        .filter(UserSettings.setting_key == key)
                        .first()
                    )

                    if setting:
                        setting.setting_value = value
                        setting.updated_at = datetime.utcnow()
                    else:
                        setting = UserSettings(
                            setting_key=key,
                            setting_value=value,
                            updated_at=datetime.utcnow(),
                        )
                        db.add(setting)

                db.commit()

                return self.success({"message": "Settings saved", "settings": settings})

            finally:
                db.close()

        except Exception as e:
            return self.error(str(e), 500)
