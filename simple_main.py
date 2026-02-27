"""
FastAPI Main Application - Simplified
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simple config
class Settings:
    APP_NAME = "Poetry & Literary Analysis System"
    VERSION = "1.0.0"
    API_PREFIX = "/api/v1"

settings = Settings()

# Create FastAPI
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# In-memory storage
analysis_results = {}

# Input models
class AnalysisInput(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    language: str = "en"
    form: str = "free_verse"
    audience: str = "general"
    register: str = "formal"
    strictness: int = Field(default=7, ge=1, le=10)
    text: str = Field(..., min_length=1)

# Analysis Service
class AnalysisService:
    def analyze(self, text: str, language: str = "en", strictness: int = 7) -> Dict:
        # Import analysis modules
        from app.services.quantitative import QuantitativeMetricsCalculator
        from app.services.prosody import ProsodyAnalyzer
        from app.services.linguistic import LinguisticAnalyzer
        from app.services.literary_devices import LiteraryDevicesAnalyzer
        
        # Run analyses
        quant_calc = QuantitativeMetricsCalculator()
        prosody = ProsodyAnalyzer()
        linguistic = LinguisticAnalyzer()
        literary = LiteraryDevicesAnalyzer()
        
        quantitative = quant_calc.analyze(text)
        prosody_result = prosody.analyze(text)
        linguistic_result = linguistic.analyze(text)
        literary_result = literary.analyze(text)
        
        # Calculate ratings
        ratings = self._calculate_ratings(quantitative, linguistic_result, literary_result)
        
        # Generate summary
        summary = self._generate_summary(quantitative, ratings)
        
        # Strengths
        strengths = self._identify_strengths(quantitative, literary_result)
        
        # Suggestions
        suggestions = self._generate_suggestions(ratings)
        
        return {
            "quantitative": quantitative,
            "prosody": prosody_result,
            "linguistic": linguistic_result,
            "literary_devices": literary_result,
            "ratings": ratings,
            "executive_summary": summary,
            "strengths": strengths,
            "suggestions": suggestions
        }
    
    def _calculate_ratings(self, quantitative: Dict, linguistic: Dict, literary: Dict) -> Dict:
        # Simple rating calculation
        base_score = 6.0
        
        lex_metrics = quantitative.get("lexical_metrics", {})
        ttr = lex_metrics.get("type_token_ratio", 0)
        
        # Adjust based on TTR
        if ttr > 0.5:
            tech = min(10, base_score + 1.5)
        else:
            tech = min(10, base_score)
        
        # Calculate overall
        overall = (tech + 7.0 + 7.0 + 6.5 + 7.0 + 6.5) / 6
        
        return {
            "technical_craft": round(tech, 1),
            "language_diction": round(base_score + 1, 1),
            "imagery_voice": round(base_score + 1, 1),
            "emotional_impact": round(base_score + 0.5, 1),
            "cultural_fidelity": round(base_score + 1, 1),
            "originality": round(base_score + 0.5, 1),
            "overall_quality": round(overall, 1)
        }
    
    def _generate_summary(self, quantitative: Dict, ratings: Dict) -> str:
        lines = quantitative.get("structural_metrics", {}).get("total_lines", "several")
        overall = ratings.get("overall_quality", 6)
        
        if overall >= 8:
            quality = "polished and publishable"
        elif overall >= 6:
            quality = "promising with room for improvement"
        else:
            quality = "requiring significant revision"
        
        return f"This is a {lines}-line literary work with an overall quality score of {overall}/10. The work is {quality}."
    
    def _identify_strengths(self, quantitative: Dict, literary: Dict) -> List[str]:
        strengths = []
        
        lex = quantitative.get("lexical_metrics", {})
        if lex.get("type_token_ratio", 0) > 0.4:
            strengths.append("Good vocabulary diversity")
        
        imagery = literary.get("imagery", {})
        if sum(len(v) for v in imagery.values()) > 2:
            strengths.append("Effective use of sensory imagery")
        
        tropes = literary.get("tropes", {})
        if sum(len(v) for v in tropes.values()) > 2:
            strengths.append("Strong figurative language")
        
        return strengths[:3]
    
    def _generate_suggestions(self, ratings: Dict) -> List[str]:
        suggestions = []
        
        if ratings.get("technical_craft", 7) < 7:
            suggestions.append("Consider varying sentence structure for better flow")
        
        if ratings.get("imagery_voice", 7) < 7:
            suggestions.append("Add more vivid sensory details")
        
        if ratings.get("originality", 6) < 7:
            suggestions.append("Explore more unique word choices")
        
        return suggestions[:3]


# Analysis service instance
analysis_service = AnalysisService()


# Routes
@app.get("/")
async def root():
    return {
        "message": "Poetry & Literary Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/v1/analyze")
async def analyze(input_data: AnalysisInput):
    try:
        result_id = input_data.id or str(uuid.uuid4())
        
        result = analysis_service.analyze(
            text=input_data.text,
            language=input_data.language,
            strictness=input_data.strictness
        )
        
        # Store
        result["id"] = result_id
        result["title"] = input_data.title
        result["language"] = input_data.language
        result["form"] = input_data.form
        result["timestamp"] = datetime.now().isoformat()
        
        analysis_results[result_id] = result
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/result/{result_id}")
async def get_result(result_id: str):
    if result_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Result not found")
    return analysis_results[result_id]

@app.get("/api/v1/forms")
async def list_forms():
    return {"forms": [
        {"id": "free_verse", "name": "Free Verse"},
        {"id": "sonnet", "name": "Sonnet"},
        {"id": "ghazal", "name": "Ghazal"},
        {"id": "haiku", "name": "Haiku"},
        {"id": "doha", "name": "Doha"},
        {"id": "chaupai", "name": "Chaupai"}
    ]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
