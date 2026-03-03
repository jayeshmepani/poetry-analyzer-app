"""
Comprehensive Configuration System
Ultimate Literary & Linguistic Master System
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, List, Optional
from functools import lru_cache
import os


class SpaCySettings(BaseSettings):
    """spaCy model configuration"""

    english_model: str = Field(
        default="en_core_web_trf", description="English transformer model"
    )
    multilingual_model: str = Field(
        default="xx_sent_ud_sm", description="Multilingual model"
    )
    hindi_model: str = Field(default="hi_core_news_sm", description="Hindi model")
    load_transformer: bool = Field(default=True, description="Load transformer models")

    class Config:
        env_prefix = "SPACY_"


class StanzaSettings(BaseSettings):
    """Stanza multilingual NLP configuration"""

    languages: List[str] = Field(
        default=["en", "hi", "gu", "ur"], description="Languages to load"
    )
    processors: str = Field(
        default="tokenize,pos,lemma,depparse", description="Processors to load"
    )

    class Config:
        env_prefix = "STANZA_"


class IndicNLPSettings(BaseSettings):
    """Indic NLP configuration"""

    enabled: bool = Field(default=True, description="Enable Indic NLP")
    languages: List[str] = Field(
        default=["hi", "gu", "mr", "bn", "ta", "te", "ur"],
        description="Indic languages",
    )

    class Config:
        env_prefix = "INDIC_NLP_"


class AnalysisSettings(BaseSettings):
    """Analysis configuration"""

    default_language: str = Field(default="en", description="Default analysis language")
    default_strictness: int = Field(
        default=7, ge=1, le=10, description="Default strictness level"
    )
    max_text_length: int = Field(
        default=50000, description="Maximum text length in characters"
    )
    min_text_length: int = Field(default=10, description="Minimum text length")
    enable_batch_processing: bool = Field(
        default=True, description="Enable batch analysis"
    )
    max_batch_size: int = Field(default=10, description="Maximum batch size")

    class Config:
        env_prefix = "ANALYSIS_"


class RatingWeights(BaseSettings):
    """Weights for rating calculations"""

    technical_craft: float = Field(default=0.15, description="Technical craft weight")
    language_diction: float = Field(
        default=0.15, description="Language & diction weight"
    )
    imagery_voice: float = Field(default=0.15, description="Imagery & voice weight")
    emotional_impact: float = Field(default=0.15, description="Emotional impact weight")
    cultural_fidelity: float = Field(
        default=0.15, description="Cultural fidelity weight"
    )
    originality: float = Field(default=0.15, description="Originality weight")
    computational_greatness: float = Field(
        default=0.10, description="Computational greatness weight"
    )

    class Config:
        env_prefix = "RATING_WEIGHTS_"


class ProsodySettings(BaseSettings):
    """Prosody analysis configuration"""

    english_meters: List[str] = Field(
        default=["iambic", "trochaic", "anapestic", "dactylic", "spondaic", "pyrrhic"],
        description="English meters to detect",
    )
    hindi_chhands: List[str] = Field(
        default=[
            "doha",
            "chaupai",
            "soratha",
            "kundaliya",
            "rola",
            "harigitika",
            "barvai",
            "savaiya",
            "kavitt",
        ],
        description="Hindi chhand types",
    )
    urdu_bahrs: List[str] = Field(
        default=["mutaqaarib", "hazaj", "ramal", "kaamil", "mujtass"],
        description="Urdu bahr types",
    )
    gujarati_forms: List[str] = Field(
        default=["padyabandh", "garbi", "raas", "ghazal"],
        description="Gujarati poetic forms",
    )

    class Config:
        env_prefix = "PROSODY_"


class RasaSettings(BaseSettings):
    """Rasa theory configuration for Indic aesthetics"""

    enabled: bool = Field(default=True, description="Enable Rasa analysis")
    rasas: List[str] = Field(
        default=[
            "shringara",
            "hasya",
            "karuna",
            "raudra",
            "veera",
            "bhayanaka",
            "bibhatsa",
            "adbhuta",
            "shanta",
        ],
        description="Nine rasas (Navarasa)",
    )
    model_path: Optional[str] = Field(
        default=None, description="Path to Rasa classification model"
    )

    class Config:
        env_prefix = "RASA_"


class TouchstoneSettings(BaseSettings):
    """Touchstone method configuration"""

    enabled: bool = Field(default=True, description="Enable touchstone comparison")
    english_touchstones: List[Dict[str, str]] = Field(
        default=[
            {"name": "Milton", "passage": "And courage never to submit or yield"},
            {
                "name": "Shakespeare",
                "passage": "Shall I compare thee to a summer's day",
            },
            {
                "name": "Homer",
                "passage": "Sing goddess the anger of Peleus son Achilles",
            },
            {"name": "Dante", "passage": "In the middle of the journey of our life"},
        ],
        description="English touchstone passages",
    )

    class Config:
        env_prefix = "TOUCHSTONE_"


class ConstraintSettings(BaseSettings):
    """Oulipo constraint configuration"""

    enabled: bool = Field(default=True, description="Enable constraint-based analysis")
    constraints: List[str] = Field(
        default=["n_plus_7", "lipogram", "snowball", "pilish", "univocalism"],
        description="Supported constraints",
    )
    dictionary_path: Optional[str] = Field(
        default=None, description="Path to dictionary for N+7"
    )

    class Config:
        env_prefix = "CONSTRAINT_"


class VisualizationSettings(BaseSettings):
    """Visualization configuration"""

    enable_charts: bool = Field(default=True, description="Enable chart generation")
    enable_heatmaps: bool = Field(
        default=True, description="Enable heatmap visualization"
    )
    enable_network_graphs: bool = Field(
        default=True, description="Enable network graphs"
    )
    chart_library: str = Field(
        default="plotly", description="Chart library (plotly/matplotlib)"
    )
    output_format: str = Field(
        default="html", description="Output format for visualizations"
    )

    class Config:
        env_prefix = "VISUALIZATION_"


class AppSettings(BaseSettings):
    """Main application settings"""

    app_name: str = Field(
        default="Ultimate Literary & Linguistic Master System",
        description="Application name",
    )
    version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    api_prefix: str = Field(default="/api/v2", description="API prefix")

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of workers")

    # CORS
    cors_origins: List[str] = Field(default=["*"], description="CORS origins")

    # Database (for storing analysis results)
    database_url: str = Field(
        default="sqlite:///./literary_analysis.db", description="Database URL"
    )

    # Cache
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")

    class Config:
        env_prefix = "APP_"


class DatabaseSettings(BaseSettings):
    """Database configuration mimicking a classic .env structure"""
    
    connection: str = Field(default="sqlite", description="Database connection type (sqlite, mysql, pgsql)")
    host: str = Field(default="127.0.0.1", description="Database host")
    port: int = Field(default=3306, description="Database port")
    database: str = Field(default="poetry_analyzer", description="Database name")
    username: str = Field(default="root", description="Database username")
    password: str = Field(default="", description="Database password")

    @property
    def get_url(self) -> str:
        """Construct SQLAlchemy URL from simple environment variables"""
        conn = self.connection.lower()
        if conn == "sqlite":
            return f"sqlite:///./{self.database}.db"
        elif conn == "mysql":
            pwd = f":{self.password}" if self.password else ""
            return f"mysql+pymysql://{self.username}{pwd}@{self.host}:{self.port}/{self.database}"
        elif conn in ["pgsql", "postgresql", "postgres"]:
            pwd = f":{self.password}" if self.password else ""
            return f"postgresql+psycopg://{self.username}{pwd}@{self.host}:{self.port}/{self.database}"
        return f"sqlite:///./{self.database}.db"
        
    class Config:
        env_prefix = "DB_"


class Settings(BaseSettings):
    """Master settings class combining all configurations"""

    app: AppSettings = Field(default_factory=AppSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    spacy: SpaCySettings = Field(default_factory=SpaCySettings)
    stanza: StanzaSettings = Field(default_factory=StanzaSettings)
    indic_nlp: IndicNLPSettings = Field(default_factory=IndicNLPSettings)
    analysis: AnalysisSettings = Field(default_factory=AnalysisSettings)
    rating_weights: RatingWeights = Field(default_factory=RatingWeights)
    prosody: ProsodySettings = Field(default_factory=ProsodySettings)
    rasa: RasaSettings = Field(default_factory=RasaSettings)
    touchstone: TouchstoneSettings = Field(default_factory=TouchstoneSettings)
    constraint: ConstraintSettings = Field(default_factory=ConstraintSettings)
    visualization: VisualizationSettings = Field(default_factory=VisualizationSettings)

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience function for quick access
settings = get_settings()


if __name__ == "__main__":
    # Print current settings for debugging
    import json

    print(json.dumps(settings.model_dump(), indent=2, default=str))
