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
    ANTHROPIC = "anthropic"


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

**STEP 1: Date Verification (CRITICAL)**
First, determine if you know the original release date for this artist and track:
- Do you recognize this artist and song combination?
- What is the known original release year/decade?
- Does the metadata date match your knowledge?
- If there's a discrepancy, note it as a likely reissue/compilation scenario

**Required JSON Response Format:**
```json
{{
    "date_verification": {{
        "artist_known": true/false,
        "track_known": true/false,
        "known_original_year": "1979" or null,
        "metadata_year": "1992",
        "is_likely_reissue": true/false,
        "verification_notes": "Brief explanation of date analysis"
    }},
    "genre": "Primary music genre",
    "subgenre": "Specific subgenre classification", 
    "mood": "Emotional mood/atmosphere",
    "era": "Musical era or decade (use verified original date if available)",
    "tags": ["descriptive", "keywords", "style", "elements"],
    "confidence": 0.85,
    "analysis_notes": "Brief explanation of the classification including date verification"
}}
```

**CRITICAL Analysis Guidelines:**

**Era Classification Rules:**
- Determine the ORIGINAL musical era when the song was first created, NOT reissue/compilation dates
- Use specific decades: "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"
- Consider the artist's peak period and musical style context
- CRITICAL: Cross-validate metadata dates with artist career timeline and genre emergence
- ISRC codes: The year in ISRC is Year of Reference for catalog assignment, NOT recording year
- If genre predates metadata date significantly, investigate for reissue scenario
- Examples: The Police → "1980s" (not 1995 compilation date), Beatles → "1960s"

**Genre Classification Rules:**
- Be precise and specific, avoid overly generic terms like "pop" or "rock"
- Use established music genres: New Wave, Post-Punk, Synthpop, Progressive Rock, Funk, etc.
- For subgenres, be even more specific: "British New Wave", "Darkwave", "Italo Disco"
- Consider historical and cultural context of the artist and era

**CRITICAL: Genre Evolution and Hybrid Classification:**
- **Soul vs Disco (1975-1980)**: If artist is soul but year is 1975+, likely "Disco" with subgenre "Disco Soul"
- **Rock vs New Wave (1977-1985)**: Post-1977 rock bands are often "New Wave" or "Post-Punk"
- **Pop vs Synthpop (1980-1989)**: 1980s pop with synthesizers is "Synthpop" not generic "Pop"
- **R&B Evolution**: 1990s+ R&B is "Contemporary R&B", 1970s R&B is "Soul" or "Funk"
- **Electronic Evolution**: 1970s electronic is "Electronic/Krautrock", 1980s is "Synthpop/New Wave", 1990s+ is specific subgenres

**Historical Genre Transitions:**
- **1975-1979**: Soul → Disco, Rock → Punk/New Wave
- **1980-1984**: Disco → New Wave/Synthpop, Rock → Post-Punk
- **1985-1989**: New Wave → Alternative Rock, Synthpop → Dance/House
- **1990-1994**: Disco Revival/Euro House, Alternative Rock, Early Hip-Hop
- **1995-1999**: House/Techno dominance, Grunge peak, Contemporary R&B
- **2000s+**: Electronic music diversification, Hip-Hop mainstream

**Technical Analysis:**
1. Use BPM and energy to inform tempo and intensity classifications
2. Consider the key signature for harmonic style analysis
3. Use HAMMS vector patterns to identify genre-specific characteristics
4. Provide confidence score between 0-1 based on data quality
5. Include 3-5 relevant tags describing musical style and elements

**BPM-Based Genre Indicators:**
- **60-90 BPM**: Ballads, Slow Soul, Ambient
- **90-110 BPM**: Soul, R&B, Hip-Hop, Trip-Hop
- **110-130 BPM**: Disco, Funk, House, Pop, Rock
- **130-140 BPM**: Techno, Trance, Hard Rock
- **140+ BPM**: Punk, Hardcore, Speed Metal, Drum & Bass

**Energy Level Genre Mapping:**
- **0.0-0.3**: Ambient, Ballads, Classical, Downtempo
- **0.3-0.5**: Soul, Folk, Jazz, Soft Rock
- **0.5-0.7**: Pop, Disco, New Wave, Alternative
- **0.7-0.9**: Rock, Funk, Dance, Punk
- **0.9-1.0**: Metal, Hardcore, Aggressive Electronic

**Example Classifications:**
- The Police → Genre: "New Wave", Subgenre: "British New Wave", Era: "1980s"
- A Flock of Seagulls → Genre: "Synthpop", Subgenre: "New Romantic", Era: "1980s"
- Kraftwerk → Genre: "Electronic", Subgenre: "Krautrock", Era: "1970s"

**Genre-Era Validation Logic:**
- **Disco detection**: If BPM 110-130, high energy, 4/4 rhythm → likely Disco (1970s-early 1980s)
- **New Wave indicators**: Synthesizers + post-1977 → likely New Wave (1980s), not generic Rock
- **Electronic evolution**: Pre-1990 electronic usually Synthpop/New Wave, not House/Techno
- **Reissue red flags**: Modern electronic subgenres with vintage BPM/energy patterns
- **Cross-validation**: Artist name + genre + era must align historically

**Example Validation Patterns:**
- Classic Disco sound + 1990s date = investigate for reissue scenario
- New Wave characteristics + 1970s date = likely mislabeled, should be 1980s
- House/Techno genre + pre-1985 date = impossible, check for reissue

Respond only with valid JSON."""

    @abstractmethod
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze a music track using the specific LLM provider"""
        pass
    
    @abstractmethod
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost of the API call"""
        pass


class LLMProviderAdapter(BaseLLMProvider):
    """Adapter to wrap new unified providers for backward compatibility"""
    
    def __init__(self, provider, config: LLMConfig):
        """Initialize adapter with new provider and old config"""
        super().__init__(config)
        self.provider = provider
        
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze track using wrapped provider"""
        # Call the new provider
        response = self.provider.analyze_track(track_data)
        
        # Convert ProviderResponse to LLMResponse
        return LLMResponse(
            success=response.success,
            content=response.content,
            raw_response=response.raw_response,
            provider=self.config.provider,
            model=response.model,
            processing_time_ms=response.processing_time_ms,
            tokens_used=response.tokens_used,
            cost_estimate=response.cost_estimate,
            error_message=response.error_message
        )
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate cost using wrapped provider"""
        if hasattr(self.provider, '_estimate_cost'):
            return self.provider._estimate_cost(prompt_tokens, response_tokens)
        return 0.0


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
        # Import the new factory and providers to trigger registration
        from src.analysis.provider_factory import ProviderFactory, ProviderConfig, ProviderType
        import src.analysis.providers  # Import to trigger auto-registration
        
        # Convert LLMConfig to ProviderConfig
        provider_config = ProviderConfig(
            provider_type=ProviderType(config.provider.value),
            api_key=config.api_key,
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            timeout=config.timeout,
            max_retries=config.max_retries,
            rate_limit_rpm=config.rate_limit_rpm
        )
        
        # Use the new factory to create provider
        try:
            provider = ProviderFactory.create_provider(
                name=config.provider.value,
                config=provider_config
            )
            
            # Wrap the new provider to maintain backward compatibility
            return LLMProviderAdapter(provider, config)
        except Exception as e:
            raise ValueError(f"Failed to create provider {config.provider.value}: {e}")


def get_recommended_configs() -> List[LLMConfig]:
    """Get recommended LLM configurations ordered by cost-effectiveness
    
    Returns:
        List of recommended configurations, cheapest first
    """
    import os
    
    configs = []
    
    # Claude Haiku - ONLY supported LLM provider
    if os.getenv('ANTHROPIC_API_KEY'):
        configs.append(LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            model="claude-3-haiku-20240307",  # Optimized Claude model
            max_tokens=1000,
            temperature=0.1,
            rate_limit_rpm=60
        ))
    
    return configs