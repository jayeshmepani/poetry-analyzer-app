"""
API Routes for Poetry & Literary Analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.schemas import (
    AnalysisInput, AnalysisResult, BatchAnalysisInput, 
    BatchAnalysisResult, HealthCheck, ErrorResponse
)
from app.services.analysis import AnalysisService, analyze_batch

router = APIRouter()

# In-memory storage for analysis results (in production, use database)
analysis_results = {}


@router.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Poetry & Literary Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "analyze": "POST /api/v1/analyze",
            "analyze_batch": "POST /api/v1/analyze/batch",
            "get_result": "GET /api/v1/result/{result_id}",
            "health": "GET /api/v1/health"
        }
    }


@router.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": True
    }


@router.post("/analyze", response_model=AnalysisResult, tags=["analysis"])
async def analyze_text(input_data: AnalysisInput):
    """Analyze a single text"""
    try:
        # Validate input
        if not input_data.text or len(input_data.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Generate result ID
        result_id = input_data.id or str(uuid.uuid4())
        
        # Run analysis
        service = AnalysisService()
        result = service.analyze(
            text=input_data.text,
            language=input_data.language.value if hasattr(input_data.language, 'value') else input_data.language,
            strictness=input_data.strictness
        )
        
        # Build response
        response = AnalysisResult(
            id=result_id,
            title=input_data.title,
            language=input_data.language.value if hasattr(input_data.language, 'value') else input_data.language,
            form=input_data.form.value if hasattr(input_data.form, 'value') else input_data.form,
            timestamp=datetime.now(),
            quantitative=result.get("quantitative"),
            meter=result.get("prosody", {}).get("meter"),
            rhyme=result.get("prosody", {}).get("rhyme"),
            linguistic=result.get("linguistic"),
            literary_devices=result.get("literary_devices"),
            ratings=result.get("ratings"),
            errors=[],
            executive_summary=result.get("executive_summary"),
            strengths=result.get("strengths", []),
            suggestions=result.get("suggestions", [])
        )
        
        # Store result
        analysis_results[result_id] = response.model_dump()
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/batch", response_model=BatchAnalysisResult, tags=["analysis"])
async def analyze_batch_texts(input_data: BatchAnalysisInput):
    """Analyze multiple texts in batch"""
    try:
        # Prepare inputs for batch processing
        inputs = []
        for item in input_data.inputs:
            inputs.append({
                "id": item.id or str(uuid.uuid4()),
                "title": item.title,
                "text": item.text,
                "language": item.language.value if hasattr(item.language, 'value') else item.language,
                "form": item.form.value if hasattr(item.form, 'value') else item.form,
                "strictness": item.strictness
            })
        
        # Run batch analysis
        results = analyze_batch(inputs)
        
        # Build response
        response_results = []
        for result in results:
            response_results.append(AnalysisResult(
                id=result.get("id"),
                title=result.get("title"),
                language=result.get("language", "en"),
                form=result.get("form", "free_verse"),
                timestamp=datetime.now(),
                quantitative=result.get("quantitative"),
                meter=result.get("prosody", {}).get("meter"),
                rhyme=result.get("prosody", {}).get("rhyme"),
                linguistic=result.get("linguistic"),
                literary_devices=result.get("literary_devices"),
                ratings=result.get("ratings"),
                errors=[],
                executive_summary=result.get("executive_summary"),
                strengths=result.get("strengths", []),
                suggestions=result.get("suggestions", [])
            ))
        
        return BatchAnalysisResult(
            results=response_results,
            total_analyzed=len(response_results),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{result_id}", tags=["results"])
async def get_result(result_id: str):
    """Get a previously stored analysis result"""
    if result_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return analysis_results[result_id]


@router.get("/results", tags=["results"])
async def list_results(limit: int = 10):
    """List all analysis results"""
    results = list(analysis_results.values())
    return {
        "total": len(results),
        "results": results[:limit]
    }


@router.delete("/result/{result_id}", tags=["results"])
async def delete_result(result_id: str):
    """Delete a stored result"""
    if result_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    del analysis_results[result_id]
    return {"message": "Result deleted successfully"}


# Additional utility endpoints

@router.get("/forms", tags=["utilities"])
async def list_forms():
    """List supported poem forms"""
    return {
        "forms": [
            {"id": "free_verse", "name": "Free Verse", "description": "No fixed meter or rhyme"},
            {"id": "sonnet", "name": "Sonnet", "description": "14 lines, iambic pentameter"},
            {"id": "ghazal", "name": "Ghazal", "description": "Couplets with qaafiya and radif"},
            {"id": "haiku", "name": "Haiku", "description": "5-7-5 syllables, 3 lines"},
            {"id": "villanelle", "name": "Villanelle", "description": "19 lines, 2 refrains"},
            {"id": "doha", "name": "Doha", "description": "Hindi couplet form, 13+11 matras"},
            {"id": "chaupai", "name": "Chaupai", "description": "Hindi quatrain, 16 matras per line"},
            {"id": "nazm", "name": "Nazm", "description": "Urdu/Hindi structured poem"},
            {"id": "geet", "name": "Geet", "description": "Lyric song form"},
            {"id": "bhajan", "name": "Bhajan", "description": "Devotional hymn"},
            {"id": "blank_verse", "name": "Blank Verse", "description": "Unrhymed iambic pentameter"}
        ]
    }


@router.get("/meters", tags=["utilities"])
async def list_meters():
    """List supported meter types"""
    return {
        "meters": [
            {"id": "iambic", "name": "Iambic", "pattern": "da-DUM", "description": "Unstressed-stressed"},
            {"id": "trochaic", "name": "Trochaic", "pattern": "DUM-da", "description": "Stressed-unstressed"},
            {"id": "anapestic", "name": "Anapestic", "pattern": "da-da-DUM", "description": "Two unstressed + stressed"},
            {"id": "dactylic", "name": "Dactylic", "pattern": "DUM-da-da", "description": "Stressed + two unstressed"},
            {"id": "spondaic", "name": "Spondaic", "pattern": "DUM-DUM", "description": "Two stressed"},
            {"id": "iambic_pentameter", "name": "Iambic Pentameter", "pattern": "5 iambs per line", "description": "10 syllable lines"}
        ]
    }


@router.get("/literary-devices", tags=["utilities"])
async def list_literary_devices():
    """List supported literary devices"""
    return {
        "tropes": [
            "metaphor", "simile", "personification", "metonymy", "synecdoche",
            "hyperbole", "litotes", "irony", "oxymoron", "paradox", "apostrophe", "synesthesia"
        ],
        "schemes": [
            "alliteration", "assonance", "consonance", "anaphora", "epistrophe",
            "chiasmus", "parallelism", "zeugma", "antithesis"
        ],
        "imagery_types": [
            "visual", "auditory", "tactile", "gustatory", "olfactory", "kinesthetic"
        ]
    }


@router.get("/metrics", tags=["utilities"])
async def list_metrics():
    """List available metrics"""
    return {
        "quantitative": [
            "type_token_ratio", "mtld", "mattr", "lexical_density",
            "flesch_kincaid_grade", "flesch_reading_ease", "gunning_fog",
            "syllable_count", "word_count", "sentence_count", "line_count"
        ],
        "prosody": [
            "meter_detection", "scansion", "rhyme_scheme", "rhyme_density"
        ],
        "linguistic": [
            "pos_distribution", "sentence_complexity", "prefix_suffix_count"
        ]
    }
