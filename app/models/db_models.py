"""
Database Models
SQLAlchemy ORM models for Poetry Analyzer
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Index, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """
    Monolithic application user model
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Integer, nullable=False, default=1) # 0=superadmin, 1=user
    status = Column(Integer, nullable=False, default=1) # 0=inactive, 1=active

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True) # Soft deletes
    
    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class AnalysisResult(Base):
    """
    Main model storing poetry analysis results
    """

    __tablename__ = "analysis_results"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="analysis_results")

    # Text Information
    title = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    language = Column(String(10), nullable=False, default="en")
    poetic_form = Column(String(100), nullable=True)

    # Metrics - Quality Scores
    overall_score = Column(Float, nullable=True)
    technical_craft_score = Column(Float, nullable=True)
    language_diction_score = Column(Float, nullable=True)
    imagery_voice_score = Column(Float, nullable=True)
    emotional_impact_score = Column(Float, nullable=True)
    cultural_fidelity_score = Column(Float, nullable=True)
    originality_score = Column(Float, nullable=True)
    computational_greatness_score = Column(Float, nullable=True)

    # Analysis Results (stored as JSON for flexibility)
    quantitative_metrics = Column(JSON, nullable=True)
    prosody_analysis = Column(JSON, nullable=True)
    literary_devices = Column(JSON, nullable=True)
    linguistic_analysis = Column(JSON, nullable=True)  # spaCy + textdescriptives
    sentiment_analysis = Column(JSON, nullable=True)
    evaluation = Column(JSON, nullable=True)
    executive_summary = Column(Text, nullable=True)

    # Metadata
    strictness_level = Column(Integer, default=8)
    word_count = Column(Integer, nullable=True)
    line_count = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_language_created", "language", "created_at"),
        Index("idx_overall_score", "overall_score"),
        Index("idx_form", "poetic_form"),
    )

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, title='{self.title}', language='{self.language}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "title": self.title,
            "text": self.text[:500] + "..." if len(self.text) > 500 else self.text,
            "language": self.language,
            "poetic_form": self.poetic_form,
            "overall_score": self.overall_score,
            "technical_craft_score": self.technical_craft_score,
            "language_diction_score": self.language_diction_score,
            "imagery_voice_score": self.imagery_voice_score,
            "emotional_impact_score": self.emotional_impact_score,
            "cultural_fidelity_score": self.cultural_fidelity_score,
            "originality_score": self.originality_score,
            "computational_greatness_score": self.computational_greatness_score,
            "word_count": self.word_count,
            "line_count": self.line_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_full_dict(self) -> dict:
        """Convert model to full dictionary with all analysis data"""
        res = self.to_dict()
        res.update(
            {
                "text": self.text,
                "quantitative_metrics": self.quantitative_metrics,
                "prosody_analysis": self.prosody_analysis,
                "linguistic_analysis": self.linguistic_analysis,
                "literary_devices": self.literary_devices,
                "sentiment_analysis": self.sentiment_analysis,
                "evaluation": self.evaluation,
                "executive_summary": self.executive_summary,
                "strictness_level": self.strictness_level,
            }
        )
        return res


class DatabaseStats(Base):
    """
    Model for storing aggregated statistics
    """

    __tablename__ = "database_stats"

    id = Column(Integer, primary_key=True)
    stat_name = Column(String(100), unique=True, nullable=False)
    stat_value = Column(JSON, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DatabaseStats(stat_name='{self.stat_name}')>"


class UserSettings(Base):
    """
    Model for storing user settings/preferences
    """

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings(key='{self.setting_key}')>"
