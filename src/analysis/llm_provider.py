"""Multi-LLM Provider Architecture for Music Analysis

This module provides a unified interface for multiple LLM providers including:
- OpenAI (GPT-4, GPT-4o-mini)
- Google Gemini (gemini-pro, gemini-1.5-pro)

The architecture allows easy switching between providers and cost optimization.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ZAI = "zai"


@dataclass
class LLMConfig:
    """Configuration for any LLM provider"""
    provider: LLMProvider
    api_key: str
    model: str
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    rate_limit_rpm: int = 60

    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_key or not self.api_key.strip():
            raise ValueError(f"{self.provider.value} API key is required and cannot be empty")


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    success: bool
    content: Dict[str, Any]
    raw_response: str
    provider: LLMProvider
    model: str
    processing_time_ms: int
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    error_message: Optional[str] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.last_request_time = 0.0
        self.min_request_interval = 60.0 / config.rate_limit_rpm
        
    def _wait_for_rate_limit(self) -> None:
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def _create_music_analysis_prompt(self, track_data: Dict[str, Any]) -> str:
        """Create standardized music analysis prompt"""
        # Validate required fields
        required_fields = ['hamms_vector', 'bpm', 'key', 'energy']
        missing_fields = [field for field in required_fields if field not in track_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
            
        # Extract data with defaults
        hamms = track_data.get('hamms_vector', [0.0] * 12)
        bpm = track_data.get('bpm', 0)
        key = track_data.get('key', 'Unknown')
        energy = track_data.get('energy', 0.0)
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        
        # Format HAMMS vector for analysis
        hamms_formatted = ', '.join([f"{v:.3f}" for v in hamms])
        
        return f"""Analyze this music track and provide a JSON response with detailed musical characteristics:

**Track Information:**
- Title: {title}
- Artist: {artist} 
- BPM: {bpm}
- Key: {key}
- Energy Level: {energy:.3f}
- HAMMS Vector: [{hamms_formatted}]

**HAMMS Vector Explanation:**
The 12-dimensional HAMMS vector represents harmonic and acoustic features:
- Dimensions 0-3: Harmonic content and chord progressions
- Dimensions 4-7: Rhythmic patterns and percussive elements  
- Dimensions 8-11: Timbral characteristics and sonic texture

**Required JSON Response Format:**
```json
{{
    "genre": "Primary music genre",
    "subgenre": "Specific subgenre classification", 
    "mood": "Emotional mood/atmosphere",
    "era": "Musical era or decade",
    "tags": ["descriptive", "keywords", "style", "elements"],
    "confidence": 0.85,
    "analysis_notes": "Brief explanation of the classification"
}}
```

**Analysis Guidelines:**
1. Use the BPM and energy to inform tempo and intensity classifications
2. Consider the key signature for harmonic style analysis
3. Use HAMMS vector patterns to identify genre-specific characteristics
4. Provide confidence score between 0-1 based on data quality
5. Include 3-5 relevant tags describing musical style and elements
6. Be specific with subgenre classifications (e.g., "Deep House" not just "House")

Respond only with valid JSON."""

    @abstractmethod
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze a music track using the specific LLM provider"""
        pass
    
    @abstractmethod
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost of the API call"""
        pass


class LLMProviderFactory:
    """Factory class to create appropriate LLM providers"""
    
    @staticmethod
    def create_provider(config: LLMConfig) -> BaseLLMProvider:
        """Create a provider instance based on configuration
        
        Args:
            config: LLM configuration specifying provider and settings
            
        Returns:
            Configured LLM provider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        if config.provider == LLMProvider.OPENAI:
            try:
                from src.analysis.openai_provider import OpenAIProvider
                return OpenAIProvider(config)
            except ImportError as e:
                raise ValueError(f"OpenAI provider not available: {e}")
                
        elif config.provider == LLMProvider.GEMINI:
            try:
                from src.analysis.gemini_provider import GeminiProvider  
                return GeminiProvider(config)
            except ImportError as e:
                raise ValueError(f"Gemini provider not available: {e}")
                
        elif config.provider == LLMProvider.ZAI:
            try:
                from src.analysis.zai_provider import ZaiProvider
                return ZaiProvider(config)
            except ImportError as e:
                raise ValueError(f"Z.ai provider not available: {e}")
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")


def get_recommended_configs() -> List[LLMConfig]:
    """Get recommended LLM configurations ordered by cost-effectiveness
    
    Returns:
        List of recommended configurations, cheapest first
    """
    import os
    
    configs = []
    
    # Gemini - Most cost-effective option
    if os.getenv('GEMINI_API_KEY'):
        configs.append(LLMConfig(
            provider=LLMProvider.GEMINI,
            api_key=os.getenv('GEMINI_API_KEY'),
            model="gemini-1.5-flash",  # Fastest and cheapest
            max_tokens=1000,
            temperature=0.1,
            rate_limit_rpm=60
        ))
    
    # Z.ai - Competitive pricing with strong performance
    if os.getenv('ZAI_API_KEY'):
        configs.append(LLMConfig(
            provider=LLMProvider.ZAI,
            api_key=os.getenv('ZAI_API_KEY'),
            model="glm-4-32b-0414-128k",  # Cost-effective model
            max_tokens=1000,
            temperature=0.1,
            rate_limit_rpm=60
        ))
    
    # OpenAI - More expensive but reliable
    if os.getenv('OPENAI_API_KEY'):
        configs.append(LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key=os.getenv('OPENAI_API_KEY'),
            model="gpt-4o-mini",  # Cheapest OpenAI option
            max_tokens=1000,
            temperature=0.1,
            rate_limit_rpm=60
        ))
    
    return configs