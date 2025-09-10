"""AI Analysis Database Model

This module defines the database model for storing OpenAI GPT-4 analysis results.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.services.storage import Base


class AIAnalysis(Base):
    """Database model for OpenAI GPT-4 analysis results"""
    
    __tablename__ = "ai_analysis"
    
    # Primary key - references tracks table
    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    
    # AI Analysis results
    genre = Column(String(100))          # Primary genre
    subgenre = Column(String(100))       # Specific subgenre
    mood = Column(String(100))           # Emotional mood
    era = Column(String(50))             # Musical era/decade
    tags = Column(Text)                  # JSON array of tags
    
    # Professional metadata
    isrc = Column(String(15))            # International Standard Recording Code
    
    # AI metadata
    ai_confidence = Column(Float)        # Overall AI confidence (0-1)
    ai_model = Column(String(50), default="gpt-4")  # AI model used
    openai_response = Column(Text)       # Full OpenAI response for debugging
    
    # Processing metadata
    analysis_date = Column(DateTime, default=datetime.utcnow)
    processing_time_ms = Column(Integer)  # Time taken for analysis in ms
    
    # Relationship to tracks table - temporarily disabled to avoid circular issues
    # track = relationship("TrackORM", back_populates="ai_analysis")
    
    def __repr__(self) -> str:
        return f"<AIAnalysis(track_id={self.track_id}, genre={self.genre}, mood={self.mood})>"
    
    def get_tags(self) -> List[str]:
        """Get tags as a list of strings"""
        if not self.tags:
            return []
        
        try:
            tags = json.loads(self.tags)
            if isinstance(tags, list):
                return [str(tag) for tag in tags]
        except (json.JSONDecodeError, TypeError):
            pass
        
        return []
    
    def set_tags(self, tags: List[str]) -> None:
        """Set tags from a list of strings"""
        if not isinstance(tags, list):
            raise ValueError("Tags must be a list")
        
        # Validate and clean tags
        clean_tags = []
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                clean_tags.append(tag.strip().lower())
        
        self.tags = json.dumps(clean_tags)
    
    def get_openai_response_data(self) -> Dict[str, Any]:
        """Get full OpenAI response as dictionary"""
        if not self.openai_response:
            return {}
        
        try:
            return json.loads(self.openai_response)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_openai_response_data(self, response_data: Dict[str, Any]) -> None:
        """Set OpenAI response data"""
        if not isinstance(response_data, dict):
            raise ValueError("Response data must be a dictionary")
        
        self.openai_response = json.dumps(response_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AI analysis to dictionary for API responses"""
        return {
            "track_id": self.track_id,
            "genre": self.genre,
            "subgenre": self.subgenre,
            "mood": self.mood,
            "era": self.era,
            "tags": self.get_tags(),
            "isrc": self.isrc,
            "ai_confidence": self.ai_confidence,
            "ai_model": self.ai_model,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "processing_time_ms": self.processing_time_ms
        }
    
    @classmethod
    def from_openai_response(cls, track_id: int, response_data: Dict[str, Any], 
                           processing_time_ms: Optional[int] = None) -> 'AIAnalysis':
        """Create AIAnalysis instance from OpenAI API response
        
        Args:
            track_id: ID of the track being analyzed
            response_data: Parsed response from OpenAI API
            processing_time_ms: Time taken for the analysis
            
        Returns:
            AIAnalysis instance ready for database insertion
        """
        analysis = cls()
        analysis.track_id = track_id
        analysis.processing_time_ms = processing_time_ms
        
        # Extract fields from response
        analysis.genre = response_data.get("genre")
        analysis.subgenre = response_data.get("subgenre")
        analysis.mood = response_data.get("mood")
        analysis.era = response_data.get("era")
        analysis.ai_confidence = response_data.get("confidence", 0.5)
        
        # Handle tags
        tags = response_data.get("tags", [])
        if isinstance(tags, list):
            analysis.set_tags(tags)
        
        # Store full response for debugging
        analysis.set_openai_response_data(response_data)
        
        return analysis
    
    def validate_data(self) -> bool:
        """Validate that AI analysis data is correct"""
        try:
            # Check confidence is valid
            if self.ai_confidence is not None:
                if not 0 <= self.ai_confidence <= 1:
                    return False
            
            # Validate tags can be parsed
            tags = self.get_tags()
            if not isinstance(tags, list):
                return False
            
            # Basic field validation
            if self.genre and not isinstance(self.genre, str):
                return False
            
            if self.mood and not isinstance(self.mood, str):
                return False
            
            return True
        except Exception:
            return False