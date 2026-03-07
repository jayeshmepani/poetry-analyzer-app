"""
Pydantic Schemas for Ultimate Literary & Linguistic Master System
Complete request/response models for all API endpoints
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class LanguageEnum(str, Enum):
    """Supported languages"""
    EN = "en"
    ENGLISH = "en"
    EN_OLD = "en_old"
    EN_MIDDLE = "en_middle"
    EN_MODERN = "en_modern"
    EN_BRITISH = "en_british"
    EN_AMERICAN = "en_american"
    EN_AUSTRALIAN = "en_australian"
    EN_INDIAN = "en_indian"
    EN_SOUTH_AFRICAN = "en_south_african"
    EN_CARIBBEAN = "en_caribbean"
    EN_SCOTS = "en_scots"
    EN_AAVE = "en_aave"
    EN_COCKNEY = "en_cockney"
    EN_SOUTHERN_US = "en_southern_us"
    EN_GEORDIE = "en_geordie"
    HI = "hi"
    HI_BRAJ = "hi_braj"
    HI_AWADHI = "hi_awadhi"
    HI_MAITHILI = "hi_maithili"
    HI_SADHUKKARI = "hi_sadhukkari"
    HI_KHARIBOLI = "hi_khariboli"
    GU = "gu"
    GU_KATHIAWADI = "gu_kathiawadi"
    GU_CHAROTARI = "gu_charotari"
    GU_SURATI = "gu_surati"
    GU_OLD = "gu_old"
    UR_STANDARD = "ur_standard"
    UR_DAKHNI = "ur_dakhni"
    UR_REKHTA = "ur_rekhta"
    UR_DHAKAIYA = "ur_dhakaiya"
    EN_CREOLE = "en_creole"
    HINGLISH = "hinglish"


class FormEnum(str, Enum):
    """Poetic forms"""
    FREE_VERSE = "free_verse"
    SONNET = "sonnet"
    GHAZAL = "ghazal"
    NAZM = "nazm"
    HAIKU = "haiku"
    VILLANELLE = "villanelle"
    DOHA = "doha"
    CHAUPAI = "chaupai"
    SORATHA = "soratha"
    KUNDALIYA = "kundaliya"
    ROLA = "rola"
    SAVAIYA = "savaiya"
    KAVITT = "kavitt"
    GARBI = "garbi"
    RAAS = "raas"
    BLANK_VERSE = "blank_verse"
    LIMERICK = "limerick"
    ODE = "ode"
    ELEGY = "elegy"
    PROSE_POEM = "prose_poem"


class RegisterEnum(str, Enum):
    """Language register levels"""
    FROZEN = "frozen"
    FORMAL = "formal"
    CONSULTATIVE = "consultative"
    CASUAL = "casual"
    INTIMATE = "intimate"


class SeverityEnum(str, Enum):
    """Issue severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class IssueTypeEnum(str, Enum):
    """Types of issues detected"""
    GRAMMAR = "grammar"
    METER = "meter"
    RHYME = "rhyme"
    DICTION = "diction"
    SYNTAX = "syntax"
    SEMANTICS = "semantics"
    ORTHOGRAPHY = "orthography"
    REGISTER = "register"
    CULTURAL = "cultural"
    METAPHOR = "metaphor"
    TONE = "tone"
    TRANSLITERATION = "transliteration"
    TYPO = "typo"
    STRUCTURAL = "structural"
    PROSODY = "prosody"
    ALANKAR = "alankar"
    RASA = "rasa"
    OTHER = "other"


class AnalysisMethodEnum(str, Enum):
    """Analysis methods"""
    TP_CASTT = "tp_castt"
    SWIFT = "swift"
    T_SWIFT = "t_swift"
    SIFT = "sift"
    NEW_CRITICISM = "new_criticism"
    TOUCHSTONE = "touchstone"
    COMPREHENSIVE = "comprehensive"


# =============================================================================
# INPUT MODELS
# =============================================================================

class AnalysisInput(BaseModel):
    """Main analysis input model"""
    id: Optional[str] = Field(None, description="Unique identifier for analysis")
    title: Optional[str] = Field(None, description="Title of the work")
    text: str = Field(..., min_length=10, max_length=50000, description="Text to analyze")
    language: LanguageEnum = Field(default=LanguageEnum.ENGLISH, description="Language of the text")
    form: FormEnum = Field(default=FormEnum.FREE_VERSE, description="Poetic form")
    audience: str = Field(default="general", description="Intended audience")
    register: RegisterEnum = Field(default=RegisterEnum.FORMAL, description="Language register")
    strictness: int = Field(default=7, ge=1, le=10, description="Analysis strictness level (1-10)")
    analysis_methods: List[AnalysisMethodEnum] = Field(
        default=[AnalysisMethodEnum.COMPREHENSIVE],
        description="Analysis methods to apply"
    )
    enable_constraints: bool = Field(default=False, description="Enable Oulipo constraint detection")
    enable_rasa: bool = Field(default=True, description="Enable Rasa analysis for Indic texts")
    enable_touchstone: bool = Field(default=True, description="Enable touchstone comparison")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Untitled",
                "text": "Shall I compare thee to a summer's day?\nThou art more lovely and more temperate...",
                "language": "en",
                "form": "sonnet",
                "strictness": 8
            }
        }


class BatchAnalysisInput(BaseModel):
    """Batch analysis input for multiple texts"""
    items: List[AnalysisInput] = Field(..., min_length=1, max_length=10, description="List of texts to analyze")
    compare: bool = Field(default=False, description="Generate comparative analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"text": "First poem...", "language": "en", "form": "sonnet"},
                    {"text": "Second poem...", "language": "hi", "form": "ghazal"}
                ],
                "compare": True
            }
        }


class ConstraintGenerationInput(BaseModel):
    """Input for constraint-based poetry generation"""
    constraint_type: Literal["n_plus_7", "lipogram", "snowball", "pilish", "univocalism"] = Field(
        ..., description="Type of constraint to apply"
    )
    source_text: Optional[str] = Field(None, description="Source text for transformation")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Constraint-specific parameters")
    language: LanguageEnum = Field(default=LanguageEnum.ENGLISH, description="Output language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "constraint_type": "n_plus_7",
                "source_text": "The quick brown fox jumps over the lazy dog",
                "parameters": {"n": 7},
                "language": "en"
            }
        }


# =============================================================================
# METRIC MODELS
# =============================================================================

class LexicalMetrics(BaseModel):
    """Lexical diversity metrics"""
    type_token_ratio: float = Field(..., description="Type-Token Ratio (TTR)")
    mtld: float = Field(..., description="Measure of Textual Lexical Diversity")
    matttr: float = Field(..., description="Moving-Average Type-Token Ratio")
    lexical_density: float = Field(..., description="Lexical density percentage")
    total_words: int = Field(..., description="Total word count")
    unique_words: int = Field(..., description="Unique word count")
    hapax_legomena: int = Field(default=0, description="Words appearing only once")
    yules_k: Optional[float] = Field(default=None)
    sichels_s: Optional[float] = Field(default=None)
    herdans_c: Optional[float] = Field(default=None)
    kuraszkiewicz_w: Optional[float] = Field(default=None)
    honores_r: Optional[float] = Field(default=None)
    dis_legomena: int = Field(default=0, description="Words appearing twice")


class SyllableMetrics(BaseModel):
    """Syllable-based metrics"""
    total_syllables: int = Field(..., description="Total syllable count")
    avg_syllables_per_word: float = Field(..., description="Average syllables per word")
    syllable_distribution: Dict[int, int] = Field(..., description="Distribution by syllable count")
    monosyllabic_words: int = Field(default=0, description="Count of 1-syllable words")
    polysyllabic_words: int = Field(default=0, description="Count of 3+ syllable words")


class ReadabilityMetrics(BaseModel):
    """Readability indices"""
    flesch_kincaid_grade: float = Field(..., description="Flesch-Kincaid Grade Level")
    flesch_reading_ease: float = Field(..., description="Flesch Reading Ease (0-100)")
    gunning_fog: float = Field(..., description="Gunning Fog Index")
    coleman_liau: float = Field(..., description="Coleman-Liau Index")
    ari: float = Field(..., description="Automated Readability Index")
    smog_index: float = Field(..., description="SMOG Index")
    avg_sentence_length: float = Field(..., description="Average sentence length")
    avg_word_length: float = Field(..., description="Average word length")
    linsear_write_formula: Optional[float] = Field(default=None)
    dale_chall_readability_score: Optional[float] = Field(default=None)
    spache_readability: Optional[float] = Field(default=None)
    forcast_readability: Optional[float] = Field(default=None)
    powers_sumner_kearl: Optional[float] = Field(default=None)
    danielson_bryan: Optional[float] = Field(default=None)
    wheeler_smith: Optional[float] = Field(default=None)


class HindiReadabilityMetrics(BaseModel):
    """Hindi-specific readability metrics"""
    rh1_score: float = Field(..., description="Readability Hindi-1 score")
    rh2_score: float = Field(..., description="Readability Hindi-2 score")
    matra_complexity_index: float = Field(..., description="Matra Complexity Index")
    avg_akshars_per_word: float = Field(..., description="Average akshars per word")
    jukta_akshar_density: float = Field(..., description="Conjunct consonant density")


class StructuralMetrics(BaseModel):
    """Structural analysis metrics"""
    total_lines: int = Field(..., description="Total line count")
    total_stanzas: int = Field(..., description="Total stanza count")
    total_sentences: int = Field(..., description="Total sentence count")
    avg_words_per_line: float = Field(..., description="Average words per line")
    avg_words_per_sentence: float = Field(..., description="Average words per sentence")
    line_length_variance: float = Field(..., description="Line length variance")
    golden_ratio_turn_line: int = Field(..., description="Expected volta/turn line")
    stanza_pattern: Optional[str] = Field(None, description="Detected stanza pattern")


class QuantitativeMetrics(BaseModel):
    """Complete quantitative metrics"""
    lexical_metrics: LexicalMetrics
    syllable_metrics: SyllableMetrics
    readability_metrics: ReadabilityMetrics
    structural_metrics: StructuralMetrics
    hindi_metrics: Optional[HindiReadabilityMetrics] = None
    computational_greatness_score: Optional[float] = None


# =============================================================================
# PROSODY MODELS
# =============================================================================

class StressPattern(BaseModel):
    """Stress pattern for a word"""
    word: str
    stress: str
    marked: str


class ScansionLine(BaseModel):
    """Scansion for a single line"""
    line_number: int
    text: str
    syllables: List[StressPattern]
    foot_pattern: Optional[str] = None


class MeterAnalysis(BaseModel):
    """Meter analysis results"""
    detected_meter: Optional[str] = Field(None, description="Detected meter type")
    metrical_regularity: float = Field(..., ge=0, le=1, description="Regularity score")
    foot_count_distribution: Dict[str, int] = Field(default_factory=dict)
    sample_patterns: List[str] = Field(default_factory=list)
    substitutions: List[Dict[str, Any]] = Field(default_factory=list)
    caesura_positions: List[int] = Field(default_factory=list)


class RhymeGroup(BaseModel):
    """Rhyme group information"""
    letter: str
    words: List[str]
    line_numbers: List[int]
    rhyme_type: Literal["perfect", "slant", "eye", "rich", "identical"]


class RhymeAnalysis(BaseModel):
    """Rhyme analysis results"""
    detected_scheme: Optional[str] = Field(None, description="Rhyme scheme (e.g., ABAB)")
    rhyme_density: float = Field(..., ge=0, le=1, description="Rhyme density")
    rhyme_groups: Dict[str, RhymeGroup] = Field(default_factory=dict)
    rhyme_quality: Literal["none", "partial", "perfect", "mixed"]
    total_lines: int
    internal_rhymes: List[Dict[str, Any]] = Field(default_factory=list)


class HindiChhandAnalysis(BaseModel):
    """Hindi Chhand analysis"""
    detected_chhand: Optional[str] = Field(None, description="Detected Chhand type")
    matra_counts: List[int] = Field(default_factory=list)
    charan_count: int = Field(default=0)
    is_valid: bool = Field(default=False)
    deviations: List[str] = Field(default_factory=list)


class UrduBahrAnalysis(BaseModel):
    """Urdu Bahr (meter) analysis"""
    detected_bahr: Optional[str] = Field(None, description="Detected Bahr type")
    arkaan: List[str] = Field(default_factory=list)
    taqti_pattern: Optional[str] = Field(None)
    is_valid: bool = Field(default=False)


class ProsodyAnalysis(BaseModel):
    """Complete prosody analysis"""
    meter: MeterAnalysis
    rhyme: RhymeAnalysis
    scansion: List[ScansionLine]
    hindi_chhand: Optional[HindiChhandAnalysis] = None
    urdu_bahr: Optional[UrduBahrAnalysis] = None
    gujarati_form: Optional[str] = None
    detected_form: Optional[str] = Field(None, description="Detected poetic form")
    form_confidence: float = Field(default=0, ge=0, le=1)


# =============================================================================
# LINGUISTIC MODELS
# =============================================================================

class PhoneticAnalysis(BaseModel):
    """Phonetic analysis results"""
    consonant_count: int
    vowel_count: int
    consonant_vowel_ratio: float
    phonesthemes: Dict[str, List[str]]
    alliteration: List[Dict[str, Any]]
    assonance: List[Dict[str, Any]]
    consonance: List[Dict[str, Any]]
    onomatopoeia: List[str]
    plosive_density: float = Field(default=0)
    fricative_density: float = Field(default=0)


class MorphologicalAnalysis(BaseModel):
    """Morphological analysis"""
    word_length_distribution: Dict[int, int]
    avg_word_length: float
    prefixes: Dict[str, int]
    suffixes: Dict[str, int]
    compound_words: List[str]
    prefix_count: int
    suffix_count: int


class SyntacticAnalysis(BaseModel):
    """Syntactic analysis"""
    total_sentences: int
    avg_sentence_length: float
    sentence_length_distribution: Dict[int, int]
    clauses: Dict[str, Any]
    sentence_types: Dict[str, int]
    complexity_score: float


class SemanticAnalysis(BaseModel):
    """Semantic analysis"""
    unique_words: int
    total_words: int
    semantic_density: float
    top_20_words: List[str]
    concrete_word_count: int
    abstract_word_count: int
    sentiment_scores: Optional[Dict[str, float]] = None


class LexicalRelations(BaseModel):
    """Lexical relationship analysis"""
    homophones: List[List[str]]
    synonyms: Dict[str, List[str]]
    antonyms: Dict[str, List[str]]
    palindromes: List[str]
    contronyms: List[List[str]] = Field(default_factory=list)
    minimal_pairs: List[List[str]] = Field(default_factory=list)


class POSDistribution(BaseModel):
    """Part-of-speech distribution"""
    noun: int
    verb: int
    adjective: int
    adverb: int
    pronoun: int
    preposition: int
    conjunction: int
    determiner: int
    detected_nouns: List[str]
    detected_verbs: List[str]
    detected_adjectives: List[str]


class LinguisticAnalysis(BaseModel):
    """Complete linguistic analysis"""
    phonetics: PhoneticAnalysis
    morphology: MorphologicalAnalysis
    syntax: SyntacticAnalysis
    semantics: SemanticAnalysis
    lexical_relations: LexicalRelations
    pos_distribution: POSDistribution
    idioms_detected: List[Dict[str, Any]] = Field(default_factory=list)
    proverbs_detected: List[Dict[str, Any]] = Field(default_factory=list)
    register_analysis: Optional[Dict[str, Any]] = None


# =============================================================================
# LITERARY DEVICES MODELS
# =============================================================================

class TropeInstance(BaseModel):
    """Single trope instance"""
    line: str
    line_number: int
    text: str
    type: str


class TropesAnalysis(BaseModel):
    """Tropes (figures of thought) analysis"""
    metaphor: List[Dict[str, Any]]
    simile: List[Dict[str, Any]]
    personification: List[Dict[str, Any]]
    metonymy: List[Dict[str, Any]]
    synecdoche: List[Dict[str, Any]]
    hyperbole: List[Dict[str, Any]]
    litotes: List[Dict[str, Any]]
    irony: List[Dict[str, Any]]
    oxymoron: List[Dict[str, Any]]
    paradox: List[Dict[str, Any]]
    apostrophe: List[Dict[str, Any]]
    synesthesia: List[Dict[str, Any]]


class SchemeInstance(BaseModel):
    """Single scheme instance"""
    line: Optional[str]
    lines: Optional[str]
    repeated_word: Optional[str]
    letter: Optional[str]
    words: Optional[List[str]]


class SchemesAnalysis(BaseModel):
    """Schemes (figures of sound/structure) analysis"""
    alliteration: List[Dict[str, Any]]
    anaphora: List[Dict[str, Any]]
    epistrophe: List[Dict[str, Any]]
    parallelism: List[Dict[str, Any]]
    antithesis: List[Dict[str, Any]]
    chiasmus: List[Dict[str, Any]] = Field(default_factory=list)
    zeugma: List[Dict[str, Any]] = Field(default_factory=list)


class ImageryInstance(BaseModel):
    """Imagery instance"""
    line: str
    line_number: int
    imagery_words: List[str]
    type: str


class ImageryAnalysis(BaseModel):
    """Sensory imagery analysis"""
    visual: List[Dict[str, Any]]
    auditory: List[Dict[str, Any]]
    tactile: List[Dict[str, Any]]
    gustatory: List[Dict[str, Any]]
    olfactory: List[Dict[str, Any]]
    kinesthetic: List[Dict[str, Any]]
    imagery_density: float = Field(default=0)
    dominant_sense: Optional[str] = None


class SanskritAlankar(BaseModel):
    """Sanskrit/Hindi Alankar analysis"""
    yamaka: List[Dict[str, Any]]
    shlesha: List[Dict[str, Any]]
    utpreksha: List[Dict[str, Any]]
    vibhavana: List[Dict[str, Any]]
    vishesokti: List[Dict[str, Any]]
    rupak: List[Dict[str, Any]] = Field(default_factory=list)
    upama: List[Dict[str, Any]] = Field(default_factory=list)


class RasaVector(BaseModel):
    """Rasa vector for Navarasa analysis"""
    shringara: float = Field(0, ge=0, le=1)
    hasya: float = Field(0, ge=0, le=1)
    karuna: float = Field(0, ge=0, le=1)
    raudra: float = Field(0, ge=0, le=1)
    veera: float = Field(0, ge=0, le=1)
    bhayanaka: float = Field(0, ge=0, le=1)
    bibhatsa: float = Field(0, ge=0, le=1)
    adbhuta: float = Field(0, ge=0, le=1)
    shanta: float = Field(0, ge=0, le=1)
    dominant_rasa: Optional[str] = None
    rasa_transitions: List[Dict[str, Any]] = Field(default_factory=list)


class LiteraryDevicesAnalysis(BaseModel):
    """Complete literary devices analysis"""
    tropes: TropesAnalysis
    schemes: SchemesAnalysis
    imagery: ImageryAnalysis
    sanskrit_alankar: SanskritAlankar
    rasa_vector: Optional[RasaVector] = None
    special_devices: Dict[str, List[Dict[str, Any]]]
    objective_correlative_score: float = Field(default=0, ge=0, le=1)
    imagist_efficiency_score: float = Field(default=0, ge=0, le=1)


# =============================================================================
# ADVANCED ANALYSIS MODELS
# =============================================================================

class TPCASTTAnalysis(BaseModel):
    """TP-CASTT method analysis"""
    title_prediction: str
    paraphrase: str
    connotation: Dict[str, List[str]]
    attitude: str
    shifts: List[Dict[str, Any]]
    title_revisited: str
    theme: str


class TouchstoneComparison(BaseModel):
    """Touchstone method comparison"""
    compared_with: str
    passage: str
    similarity_score: float
    assessment: str


class SentimentAnalysis(BaseModel):
    """Sentiment analysis results"""
    valence: float = Field(..., ge=-1, le=1)
    arousal: float = Field(..., ge=0, le=1)
    dominance: float = Field(..., ge=0, le=1)
    sentiment_arc: List[float]
    dominant_emotion: str
    emotion_distribution: Dict[str, float]


class EmbeddingAnalysis(BaseModel):
    """Embedding-based analysis"""
    semantic_similarity_to_canon: float
    novelty_score: float
    genre_classification: Optional[str]
    embedding_vector: Optional[List[float]] = None


class ConstraintAnalysis(BaseModel):
    """Oulipo constraint analysis"""
    detected_constraints: List[str]
    constraint_compliance: Dict[str, float]
    generated_text: Optional[str] = None


class AdvancedAnalysis(BaseModel):
    """Complete advanced analysis"""
    tp_castt: Optional[TPCASTTAnalysis] = None
    touchstone_comparisons: List[TouchstoneComparison] = Field(default_factory=list)
    swift: Optional[Dict[str, Any]] = None
    t_swift: Optional[Dict[str, Any]] = None
    sift: Optional[Dict[str, Any]] = None
    sentiment: Optional[SentimentAnalysis] = None
    embeddings: Optional[EmbeddingAnalysis] = None
    constraints: Optional[ConstraintAnalysis] = None


# =============================================================================
# RATING & EVALUATION MODELS
# =============================================================================

class Ratings(BaseModel):
    """7-category rating system"""
    technical_craft: float = Field(..., ge=0, le=10)
    language_diction: float = Field(..., ge=0, le=10)
    imagery_voice: float = Field(..., ge=0, le=10)
    emotional_impact: float = Field(..., ge=0, le=10)
    cultural_fidelity: float = Field(..., ge=0, le=10)
    originality: float = Field(..., ge=0, le=10)
    overall_quality: float = Field(..., ge=0, le=10)


class Issue(BaseModel):
    """Detected issue in text"""
    location: str
    issue_type: IssueTypeEnum
    severity: SeverityEnum
    technical_explanation: str
    impact_analysis: str
    evidence: str
    suggested_fix: str
    why_it_matters: str


class Strength(BaseModel):
    """Identified strength"""
    description: str
    evidence: List[str]
    impact: str


class Suggestion(BaseModel):
    """Improvement suggestion"""
    priority: int = Field(..., ge=1, le=3)
    category: str
    description: str
    example: Optional[str] = None


class PublishabilityAssessment(BaseModel):
    """Publishability assessment"""
    ready: bool
    needs_light_edits: bool
    needs_heavy_revision: bool
    major_rework_required: bool
    recommended_venues: List[str] = Field(default_factory=list)
    assessment_notes: str


class PerformanceAssessment(BaseModel):
    """Spoken word/performance assessment"""
    suitable_for_performance: bool
    physical_presence_notes: str
    vocal_dynamics_notes: str
    breath_units: str
    dramatic_appropriateness: str
    audience_engagement_potential: str
    memorability_score: float = Field(ge=0, le=10)


class Evaluation(BaseModel):
    """Complete evaluation"""
    ratings: Ratings
    issues: List[Issue]
    strengths: List[Strength]
    suggestions: List[Suggestion]
    publishability: PublishabilityAssessment
    performance: Optional[PerformanceAssessment] = None
    minimal_corrected_version: Optional[str] = None
    polished_version: Optional[str] = None


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    id: str
    title: Optional[str]
    language: str
    form: str
    timestamp: datetime
    text_preview: str
    
    quantitative: QuantitativeMetrics
    prosody: ProsodyAnalysis
    linguistic: LinguisticAnalysis
    literary_devices: LiteraryDevicesAnalysis
    advanced: Optional[AdvancedAnalysis] = None
    evaluation: Evaluation
    
    executive_summary: str
    educational_insight: str
    limitations: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "analysis-123",
                "title": "Untitled",
                "language": "en",
                "form": "sonnet",
                "timestamp": "2024-01-01T00:00:00",
                "executive_summary": "A 14-line sonnet with strong iambic pentameter..."
            }
        }


class BatchAnalysisResponse(BaseModel):
    """Batch analysis response"""
    results: List[AnalysisResponse]
    comparative_analysis: Optional[Dict[str, Any]] = None
    summary: Dict[str, Any]


class ConstraintGenerationResponse(BaseModel):
    """Constraint-based generation response"""
    original_text: Optional[str]
    generated_text: str
    constraint_type: str
    parameters: Dict[str, Any]
    compliance_score: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    models_loaded: Dict[str, bool]
    timestamp: datetime


class FormsResponse(BaseModel):
    """Available forms response"""
    forms: List[Dict[str, str]]
    languages: List[Dict[str, str]]


class ErrorDetail(BaseModel):
    """Error detail model"""
    error: str
    detail: str
    suggestion: Optional[str] = None


# =============================================================================
# VISUALIZATION MODELS
# =============================================================================

class VisualizationData(BaseModel):
    """Visualization data"""
    chart_type: str
    data: Dict[str, Any]
    config: Dict[str, Any]
    title: str
    description: str


class ScansionVisualization(BaseModel):
    """Scansion visualization data"""
    lines: List[Dict[str, Any]]
    meter_pattern: str
    highlights: List[Dict[str, Any]]


class RasaWheelData(BaseModel):
    """Rasa wheel visualization"""
    rasas: List[str]
    scores: List[float]
    colors: List[str]
    dominant: str
