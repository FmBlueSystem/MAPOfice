"""HAMMS Advanced Database Model

This module defines the database model for storing HAMMS v3.0 analysis data.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.services.storage import Base


class HAMMSAdvanced(Base):
    """Database model for HAMMS v3.0 12-dimensional analysis data"""
    
    __tablename__ = "hamms_advanced"
    
    # Primary key - references tracks table
    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    
    # HAMMS v3.0 data
    vector_12d = Column(Text, nullable=False)  # JSON: [0.1, 0.8, 0.7, ...]
    dimension_scores = Column(Text)  # JSON: {"bpm": 0.1, "key": 0.8, ...}
    similarity_cache = Column(Text)  # JSON: pre-computed similarities
    
    # Metadata
    ml_confidence = Column(Float)  # Confidence in the analysis (0-1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to tracks table - temporarily disabled to avoid circular import issues
    # track = relationship("TrackORM", back_populates="hamms_advanced")
    
    def __repr__(self) -> str:
        return f"<HAMMSAdvanced(track_id={self.track_id}, created_at={self.created_at})>"
    
    def get_vector_12d(self) -> List[float]:
        """Get the 12-dimensional HAMMS vector as a list of floats"""
        if not self.vector_12d:
            return [0.0] * 12
        
        try:
            vector = json.loads(self.vector_12d)
            if len(vector) == 12:
                return [float(v) for v in vector]
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
        
        return [0.0] * 12
    
    def set_vector_12d(self, vector: List[float]) -> None:
        """Set the 12-dimensional HAMMS vector"""
        if not isinstance(vector, list) or len(vector) != 12:
            raise ValueError("Vector must be a list of 12 float values")
        
        if not all(isinstance(v, (int, float)) for v in vector):
            raise ValueError("All vector elements must be numeric")
        
        if not all(0 <= v <= 1 for v in vector):
            raise ValueError("All vector elements must be between 0 and 1")
        
        self.vector_12d = json.dumps([float(v) for v in vector])
    
    def get_dimension_scores(self) -> Dict[str, float]:
        """Get dimension scores as a dictionary"""
        if not self.dimension_scores:
            return {}
        
        try:
            return json.loads(self.dimension_scores)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_dimension_scores(self, scores: Dict[str, float]) -> None:
        """Set dimension scores"""
        if not isinstance(scores, dict):
            raise ValueError("Scores must be a dictionary")
        
        # Validate all values are numeric and 0-1
        for key, value in scores.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"Score for {key} must be numeric, got {type(value)}")
            if not 0 <= value <= 1:
                raise ValueError(f"Score for {key} must be between 0-1, got {value}")
        
        self.dimension_scores = json.dumps(scores)
    
    def get_similarity_cache(self) -> Dict[str, Any]:
        """Get similarity cache as a dictionary"""
        if not self.similarity_cache:
            return {}
        
        try:
            return json.loads(self.similarity_cache)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_similarity_cache(self, cache: Dict[str, Any]) -> None:
        """Set similarity cache"""
        if not isinstance(cache, dict):
            raise ValueError("Cache must be a dictionary")
        
        self.similarity_cache = json.dumps(cache)
    
    def validate_data(self) -> bool:
        """Validate that all HAMMS data is correct"""
        try:
            # Validate vector
            vector = self.get_vector_12d()
            if len(vector) != 12:
                return False
            
            if not all(0 <= v <= 1 for v in vector):
                return False
            
            # Validate confidence
            if self.ml_confidence is not None:
                if not 0 <= self.ml_confidence <= 1:
                    return False
            
            return True
        except Exception:
            return False