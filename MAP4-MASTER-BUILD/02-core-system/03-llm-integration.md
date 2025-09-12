# MAP4 LLM Integration - Multi-Provider System

## Objective
Implement a sophisticated multi-LLM provider system with auto-registration, factory pattern, unified interface, and intelligent fallback strategies for AI-powered music analysis enrichment.

## Prerequisites
- Completed infrastructure and core implementation
- API keys for LLM providers (OpenAI, Anthropic, Google Gemini, ZAI)
- Python packages: openai, anthropic, google-generativeai, requests

## Step 1: Base Provider Architecture

### 1.1 Create Base Provider Class
Create `src/analysis/providers/base_provider.py`:

```python
"""Base provider class for all LLM integrations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)

class ProviderStatus(Enum):
    """Provider status enumeration."""
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DISABLED = "disabled"
    NOT_CONFIGURED = "not_configured"

@dataclass
class ProviderConfig:
    """Configuration for LLM providers."""
    api_key: str
    model: str = ""
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 60  # requests per minute
    max_retries: int = 3
    retry_delay: float = 1.0
    cost_per_1k_tokens: float = 0.001
    enabled: bool = True
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.api_key or self.api_key == "your_api_key_here":
            return False
        if self.max_tokens <= 0:
            return False
        if not 0 <= self.temperature <= 2:
            return False
        return True

@dataclass
class AnalysisRequest:
    """Standard analysis request format."""
    track_data: Dict[str, Any]
    analysis_type: str = "full"  # full, genre, mood, tags
    include_confidence: bool = True
    max_response_length: int = 500
    custom_prompt: Optional[str] = None

@dataclass
class AnalysisResponse:
    """Standard analysis response format."""
    success: bool
    provider: str
    model: str
    genre: Optional[str] = None
    subgenres: Optional[List[str]] = None
    mood: Optional[str] = None
    moods: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    era: Optional[str] = None
    style: Optional[str] = None
    scene: Optional[str] = None
    confidence: float = 0.5
    raw_response: Optional[str] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0

class BaseProvider(ABC):
    """Abstract base class for LLM providers."""
    
    # Provider metadata
    PROVIDER_NAME = "base"
    SUPPORTED_MODELS = []
    DEFAULT_MODEL = ""
    
    def __init__(self, config: ProviderConfig):
        """Initialize provider with configuration.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.status = ProviderStatus.NOT_CONFIGURED
        self._request_count = 0
        self._last_request_time = 0
        self._error_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        
        # Validate and set status
        if self.config.validate():
            self.status = ProviderStatus.AVAILABLE
            if not self.config.model:
                self.config.model = self.DEFAULT_MODEL
        else:
            logger.warning(f"{self.PROVIDER_NAME} provider not configured properly")
    
    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """Perform analysis on track data.
        
        Args:
            request: Analysis request
        
        Returns:
            Analysis response
        """
        pass
    
    @abstractmethod
    def _create_prompt(self, request: AnalysisRequest) -> str:
        """Create analysis prompt for the provider.
        
        Args:
            request: Analysis request
        
        Returns:
            Formatted prompt string
        """
        pass
    
    @abstractmethod
    def _parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse provider response into standard format.
        
        Args:
            raw_response: Raw response from provider
        
        Returns:
            Parsed response dictionary
        """
        pass
    
    def check_rate_limit(self) -> bool:
        """Check if rate limit allows request.
        
        Returns:
            True if request is allowed
        """
        if self.config.rate_limit <= 0:
            return True
        
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < (60 / self.config.rate_limit):
            self.status = ProviderStatus.RATE_LIMITED
            return False
        
        return True
    
    def update_metrics(self, tokens: int, cost: float):
        """Update usage metrics.
        
        Args:
            tokens: Tokens used
            cost: Cost incurred
        """
        self._request_count += 1
        self._last_request_time = time.time()
        self._total_tokens += tokens
        self._total_cost += cost
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get provider metrics.
        
        Returns:
            Metrics dictionary
        """
        return {
            'provider': self.PROVIDER_NAME,
            'status': self.status.value,
            'request_count': self._request_count,
            'error_count': self._error_count,
            'total_tokens': self._total_tokens,
            'total_cost': self._total_cost,
            'average_tokens': self._total_tokens / max(1, self._request_count),
            'average_cost': self._total_cost / max(1, self._request_count)
        }
    
    def create_base_prompt(self, track_data: Dict[str, Any]) -> str:
        """Create base analysis prompt used by all providers.
        
        Args:
            track_data: Track information
        
        Returns:
            Base prompt string
        """
        prompt = f"""Analyze this music track and provide detailed metadata:

Track Information:
- Title: {track_data.get('title', 'Unknown')}
- Artist: {track_data.get('artist', 'Unknown')}
- BPM: {track_data.get('bpm', 'Unknown')}
- Key: {track_data.get('key', 'Unknown')}
- Energy: {track_data.get('energy', 'Unknown')}
- Duration: {track_data.get('duration', 'Unknown')} seconds

Audio Features:
- HAMMS Vector: {track_data.get('hamms_vector', [])}
- Danceability: {track_data.get('danceability', 'Unknown')}
- Valence: {track_data.get('valence', 'Unknown')}
- Acousticness: {track_data.get('acousticness', 'Unknown')}

Please provide:
1. Primary genre and up to 3 subgenres
2. Primary mood and emotional characteristics
3. Descriptive tags (5-10 relevant tags)
4. Detected or likely instruments
5. Production era and style
6. Scene or context where this music fits
7. Confidence level (0-1) for your analysis

Format your response as structured data."""
        
        return prompt
    
    def validate_response(self, response: AnalysisResponse) -> AnalysisResponse:
        """Validate and clean analysis response.
        
        Args:
            response: Raw analysis response
        
        Returns:
            Validated response
        """
        # Ensure confidence is in valid range
        response.confidence = max(0.0, min(1.0, response.confidence))
        
        # Clean genre
        if response.genre:
            response.genre = response.genre.strip().title()
        
        # Clean subgenres
        if response.subgenres:
            response.subgenres = [g.strip().title() for g in response.subgenres]
            response.subgenres = response.subgenres[:5]  # Limit to 5
        
        # Clean mood
        if response.mood:
            response.mood = response.mood.strip().title()
        
        # Clean tags
        if response.tags:
            response.tags = [t.strip().lower() for t in response.tags]
            response.tags = list(set(response.tags))[:10]  # Unique, max 10
        
        # Clean instruments
        if response.instruments:
            response.instruments = [i.strip().title() for i in response.instruments]
            response.instruments = list(set(response.instruments))[:10]
        
        return response
    
    def handle_error(self, error: Exception) -> AnalysisResponse:
        """Handle provider errors.
        
        Args:
            error: Exception that occurred
        
        Returns:
            Error response
        """
        self._error_count += 1
        self.status = ProviderStatus.ERROR
        
        return AnalysisResponse(
            success=False,
            provider=self.PROVIDER_NAME,
            model=self.config.model,
            error=str(error)
        )

# Export
__all__ = ['BaseProvider', 'ProviderConfig', 'AnalysisRequest', 'AnalysisResponse', 'ProviderStatus']
```

## Step 2: Provider Factory with Auto-Registration

### 2.1 Create Provider Factory
Create `src/analysis/providers/provider_factory.py`:

```python
"""Provider factory with auto-registration system."""

from typing import Dict, Type, Optional, List, Any
import logging
from functools import wraps

from src.analysis.providers.base_provider import (
    BaseProvider, ProviderConfig, AnalysisRequest, AnalysisResponse, ProviderStatus
)

logger = logging.getLogger(__name__)

class ProviderFactory:
    """Factory for creating and managing LLM providers with auto-registration."""
    
    # Registry of available providers
    _providers: Dict[str, Type[BaseProvider]] = {}
    
    # Instances cache
    _instances: Dict[str, BaseProvider] = {}
    
    # Provider priorities for fallback
    _priorities = ['openai', 'anthropic', 'gemini', 'zai']
    
    @classmethod
    def register_provider(cls, name: str = None):
        """Decorator for auto-registering providers.
        
        Args:
            name: Provider name (defaults to class PROVIDER_NAME)
        
        Returns:
            Decorator function
        """
        def decorator(provider_class: Type[BaseProvider]):
            provider_name = name or provider_class.PROVIDER_NAME
            
            if provider_name in cls._providers:
                logger.warning(f"Provider {provider_name} already registered, overwriting")
            
            cls._providers[provider_name] = provider_class
            logger.info(f"Registered provider: {provider_name}")
            
            return provider_class
        
        return decorator
    
    @classmethod
    def create_provider(cls, name: str, config: ProviderConfig) -> Optional[BaseProvider]:
        """Create or retrieve a provider instance.
        
        Args:
            name: Provider name
            config: Provider configuration
        
        Returns:
            Provider instance or None
        """
        # Check if already instantiated
        if name in cls._instances:
            return cls._instances[name]
        
        # Check if provider is registered
        if name not in cls._providers:
            logger.error(f"Provider {name} not registered")
            return None
        
        # Create new instance
        try:
            provider_class = cls._providers[name]
            provider = provider_class(config)
            cls._instances[name] = provider
            logger.info(f"Created provider instance: {name}")
            return provider
        except Exception as e:
            logger.error(f"Failed to create provider {name}: {e}")
            return None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of registered provider names.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def get_active_providers(cls) -> List[BaseProvider]:
        """Get list of active provider instances.
        
        Returns:
            List of active providers
        """
        active = []
        for provider in cls._instances.values():
            if provider.status == ProviderStatus.AVAILABLE:
                active.append(provider)
        return active
    
    @classmethod
    def analyze_with_fallback(cls, request: AnalysisRequest, 
                             preferred_provider: Optional[str] = None) -> AnalysisResponse:
        """Analyze with automatic fallback to other providers.
        
        Args:
            request: Analysis request
            preferred_provider: Preferred provider name
        
        Returns:
            Analysis response
        """
        # Build provider order
        provider_order = []
        
        if preferred_provider and preferred_provider in cls._instances:
            provider_order.append(preferred_provider)
        
        for name in cls._priorities:
            if name not in provider_order and name in cls._instances:
                provider_order.append(name)
        
        # Try each provider
        errors = []
        for provider_name in provider_order:
            provider = cls._instances[provider_name]
            
            # Check if provider is available
            if provider.status != ProviderStatus.AVAILABLE:
                continue
            
            # Check rate limit
            if not provider.check_rate_limit():
                logger.info(f"Provider {provider_name} rate limited, trying next")
                continue
            
            try:
                logger.info(f"Attempting analysis with {provider_name}")
                response = provider.analyze(request)
                
                if response.success:
                    return response
                else:
                    errors.append(f"{provider_name}: {response.error}")
                    
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                errors.append(f"{provider_name}: {str(e)}")
        
        # All providers failed
        return AnalysisResponse(
            success=False,
            provider="factory",
            model="fallback",
            error=f"All providers failed: {'; '.join(errors)}"
        )
    
    @classmethod
    def get_provider_stats(cls) -> Dict[str, Any]:
        """Get statistics for all providers.
        
        Returns:
            Provider statistics
        """
        stats = {
            'registered': len(cls._providers),
            'active': len(cls._instances),
            'providers': {}
        }
        
        for name, provider in cls._instances.items():
            stats['providers'][name] = provider.get_metrics()
        
        return stats
    
    @classmethod
    def reset(cls):
        """Reset factory (mainly for testing)."""
        cls._instances.clear()
        logger.info("Provider factory reset")

# Convenience function for provider registration
def register_provider(name: str = None):
    """Register a provider class with the factory.
    
    Args:
        name: Provider name
    
    Returns:
        Decorator function
    """
    return ProviderFactory.register_provider(name)

# Export
__all__ = ['ProviderFactory', 'register_provider']
```

## Step 3: OpenAI Provider Implementation

### 3.1 Create OpenAI Provider
Create `src/analysis/providers/openai_provider.py`:

```python
"""OpenAI provider implementation."""

import json
import time
from typing import Dict, Any
import logging

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed")

from src.analysis.providers.base_provider import (
    BaseProvider, ProviderConfig, AnalysisRequest, AnalysisResponse
)
from src.analysis.providers.provider_factory import register_provider

logger = logging.getLogger(__name__)

@register_provider("openai")
class OpenAIProvider(BaseProvider):
    """OpenAI GPT provider for music analysis."""
    
    PROVIDER_NAME = "openai"
    SUPPORTED_MODELS = ["gpt-4", "gpt-4-turbo", "gpt-4o-mini", "gpt-3.5-turbo"]
    DEFAULT_MODEL = "gpt-4o-mini"
    
    # Token costs per 1K tokens (approximate)
    MODEL_COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
    }
    
    def __init__(self, config: ProviderConfig):
        """Initialize OpenAI provider."""
        super().__init__(config)
        
        if not OPENAI_AVAILABLE:
            self.status = ProviderStatus.NOT_CONFIGURED
            return
        
        if self.status == ProviderStatus.AVAILABLE:
            try:
                self.client = OpenAI(api_key=self.config.api_key)
                # Test connection
                self._test_connection()
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.status = ProviderStatus.ERROR
    
    def _test_connection(self):
        """Test OpenAI API connection."""
        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            logger.info(f"OpenAI connection test successful with {self.config.model}")
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            raise
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """Perform analysis using OpenAI.
        
        Args:
            request: Analysis request
        
        Returns:
            Analysis response
        """
        if self.status != ProviderStatus.AVAILABLE:
            return self.handle_error(Exception("Provider not available"))
        
        if not self.check_rate_limit():
            return self.handle_error(Exception("Rate limit exceeded"))
        
        start_time = time.time()
        
        try:
            # Create prompt
            prompt = self._create_prompt(request)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional music analyst with expertise in genre classification, mood detection, and music production."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse response
            raw_response = response.choices[0].message.content
            parsed = self._parse_response(raw_response)
            
            # Calculate metrics
            tokens_used = response.usage.total_tokens if response.usage else 0
            cost = self._calculate_cost(tokens_used)
            processing_time = time.time() - start_time
            
            # Update metrics
            self.update_metrics(tokens_used, cost)
            
            # Create response
            result = AnalysisResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=self.config.model,
                genre=parsed.get('genre'),
                subgenres=parsed.get('subgenres', []),
                mood=parsed.get('mood'),
                moods=parsed.get('moods', []),
                tags=parsed.get('tags', []),
                instruments=parsed.get('instruments', []),
                era=parsed.get('era'),
                style=parsed.get('style'),
                scene=parsed.get('scene'),
                confidence=parsed.get('confidence', 0.7),
                raw_response=raw_response,
                processing_time=processing_time,
                tokens_used=tokens_used,
                cost=cost
            )
            
            return self.validate_response(result)
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return self.handle_error(e)
    
    def _create_prompt(self, request: AnalysisRequest) -> str:
        """Create analysis prompt for OpenAI.
        
        Args:
            request: Analysis request
        
        Returns:
            Formatted prompt
        """
        if request.custom_prompt:
            return request.custom_prompt
        
        base_prompt = self.create_base_prompt(request.track_data)
        
        # Add JSON format instruction
        json_instruction = """
Please respond in JSON format with the following structure:
{
    "genre": "Primary genre",
    "subgenres": ["Subgenre1", "Subgenre2", "Subgenre3"],
    "mood": "Primary mood",
    "moods": ["Mood1", "Mood2"],
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "instruments": ["Instrument1", "Instrument2"],
    "era": "Production era (e.g., '1990s', 'Modern')",
    "style": "Production style",
    "scene": "Context or scene",
    "confidence": 0.85
}"""
        
        return f"{base_prompt}\n\n{json_instruction}"
    
    def _parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse OpenAI response.
        
        Args:
            raw_response: Raw JSON response
        
        Returns:
            Parsed dictionary
        """
        try:
            # Parse JSON response
            data = json.loads(raw_response)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            logger.debug(f"Raw response: {raw_response}")
            
            # Attempt basic extraction
            return {
                'genre': 'Unknown',
                'confidence': 0.3,
                'error': 'Failed to parse response'
            }
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost for tokens used.
        
        Args:
            tokens: Total tokens used
        
        Returns:
            Estimated cost
        """
        model_cost = self.MODEL_COSTS.get(self.config.model, {
            "input": 0.001,
            "output": 0.002
        })
        
        # Rough estimate: 2/3 input, 1/3 output
        input_tokens = tokens * 0.67
        output_tokens = tokens * 0.33
        
        cost = (input_tokens * model_cost["input"] + 
                output_tokens * model_cost["output"]) / 1000
        
        return cost

# Export
__all__ = ['OpenAIProvider']
```

## Step 4: Anthropic Claude Provider

### 4.1 Create Anthropic Provider
Create `src/analysis/providers/anthropic_provider.py`:

```python
"""Anthropic Claude provider implementation."""

import json
import time
from typing import Dict, Any
import logging

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic package not installed")

from src.analysis.providers.base_provider import (
    BaseProvider, ProviderConfig, AnalysisRequest, AnalysisResponse, ProviderStatus
)
from src.analysis.providers.provider_factory import register_provider

logger = logging.getLogger(__name__)

@register_provider("anthropic")
class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider for music analysis."""
    
    PROVIDER_NAME = "anthropic"
    SUPPORTED_MODELS = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    DEFAULT_MODEL = "claude-3-haiku"
    
    # Token costs per 1K tokens
    MODEL_COSTS = {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
    }
    
    def __init__(self, config: ProviderConfig):
        """Initialize Anthropic provider."""
        super().__init__(config)
        
        if not ANTHROPIC_AVAILABLE:
            self.status = ProviderStatus.NOT_CONFIGURED
            return
        
        if self.status == ProviderStatus.AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=self.config.api_key)
                self._test_connection()
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                self.status = ProviderStatus.ERROR
    
    def _test_connection(self):
        """Test Anthropic API connection."""
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            logger.info(f"Anthropic connection test successful with {self.config.model}")
        except Exception as e:
            logger.error(f"Anthropic connection test failed: {e}")
            raise
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """Perform analysis using Claude.
        
        Args:
            request: Analysis request
        
        Returns:
            Analysis response
        """
        if self.status != ProviderStatus.AVAILABLE:
            return self.handle_error(Exception("Provider not available"))
        
        if not self.check_rate_limit():
            return self.handle_error(Exception("Rate limit exceeded"))
        
        start_time = time.time()
        
        try:
            # Create prompt
            prompt = self._create_prompt(request)
            
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system="You are a professional music analyst with deep expertise in genre classification, mood detection, music theory, and production techniques. Provide detailed and accurate analysis.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract response text
            raw_response = response.content[0].text if response.content else ""
            parsed = self._parse_response(raw_response)
            
            # Calculate metrics
            tokens_used = response.usage.input_tokens + response.usage.output_tokens if hasattr(response, 'usage') else 0
            cost = self._calculate_cost(tokens_used)
            processing_time = time.time() - start_time
            
            # Update metrics
            self.update_metrics(tokens_used, cost)
            
            # Create response
            result = AnalysisResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=self.config.model,
                genre=parsed.get('genre'),
                subgenres=parsed.get('subgenres', []),
                mood=parsed.get('mood'),
                moods=parsed.get('moods', []),
                tags=parsed.get('tags', []),
                instruments=parsed.get('instruments', []),
                era=parsed.get('era'),
                style=parsed.get('style'),
                scene=parsed.get('scene'),
                confidence=parsed.get('confidence', 0.75),
                raw_response=raw_response,
                processing_time=processing_time,
                tokens_used=tokens_used,
                cost=cost
            )
            
            return self.validate_response(result)
            
        except Exception as e:
            logger.error(f"Anthropic analysis failed: {e}")
            return self.handle_error(e)
    
    def _create_prompt(self, request: AnalysisRequest) -> str:
        """Create analysis prompt for Claude.
        
        Args:
            request: Analysis request
        
        Returns:
            Formatted prompt
        """
        if request.custom_prompt:
            return request.custom_prompt
        
        base_prompt = self.create_base_prompt(request.track_data)
        
        # Claude-specific formatting
        claude_instruction = """
Analyze this track and provide your response in the following JSON format:

```json
{
    "genre": "Primary genre",
    "subgenres": ["Subgenre1", "Subgenre2", "Subgenre3"],
    "mood": "Primary mood",
    "moods": ["Additional mood 1", "Additional mood 2"],
    "tags": ["descriptive", "tags", "about", "the", "track"],
    "instruments": ["Detected instrument 1", "Detected instrument 2"],
    "era": "Production era",
    "style": "Production style",
    "scene": "Where this music would fit",
    "confidence": 0.85
}
```

Be specific and accurate in your analysis. Base your confidence on how clear the musical characteristics are."""
        
        return f"{base_prompt}\n\n{claude_instruction}"
    
    def _parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse Claude response.
        
        Args:
            raw_response: Raw response text
        
        Returns:
            Parsed dictionary
        """
        try:
            # Extract JSON from response
            # Claude often wraps JSON in markdown code blocks
            if "```json" in raw_response:
                start = raw_response.find("```json") + 7
                end = raw_response.find("```", start)
                json_str = raw_response[start:end].strip()
            elif "{" in raw_response and "}" in raw_response:
                # Try to extract raw JSON
                start = raw_response.find("{")
                end = raw_response.rfind("}") + 1
                json_str = raw_response[start:end]
            else:
                json_str = raw_response
            
            data = json.loads(json_str)
            return data
            
        except Exception as e:
            logger.error(f"Failed to parse Claude response: {e}")
            logger.debug(f"Raw response: {raw_response}")
            
            # Fallback parsing
            return {
                'genre': 'Unknown',
                'confidence': 0.3,
                'error': 'Failed to parse response'
            }
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost for tokens used.
        
        Args:
            tokens: Total tokens used
        
        Returns:
            Estimated cost
        """
        model_cost = self.MODEL_COSTS.get(self.config.model, {
            "input": 0.001,
            "output": 0.005
        })
        
        # Estimate input/output split
        input_tokens = tokens * 0.7
        output_tokens = tokens * 0.3
        
        cost = (input_tokens * model_cost["input"] + 
                output_tokens * model_cost["output"]) / 1000
        
        return cost

# Export
__all__ = ['AnthropicProvider']
```

## Step 5: Google Gemini Provider

### 5.1 Create Gemini Provider
Create `src/analysis/providers/gemini_provider.py`:

```python
"""Google Gemini provider implementation."""

import json
import time
from typing import Dict, Any
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google GenerativeAI package not installed")

from src.analysis.providers.base_provider import (
    BaseProvider, ProviderConfig, AnalysisRequest, AnalysisResponse, ProviderStatus
)
from src.analysis.providers.provider_factory import register_provider

logger = logging.getLogger(__name__)

@register_provider("gemini")
class GeminiProvider(BaseProvider):
    """Google Gemini provider for music analysis."""
    
    PROVIDER_NAME = "gemini"
    SUPPORTED_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    DEFAULT_MODEL = "gemini-1.5-flash"
    
    # Token costs (approximate)
    MODEL_COSTS = {
        "gemini-1.5-flash": {"input": 0.00035, "output": 0.00105},
        "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105},
        "gemini-pro": {"input": 0.0005, "output": 0.0015}
    }
    
    def __init__(self, config: ProviderConfig):
        """Initialize Gemini provider."""
        super().__init__(config)
        
        if not GEMINI_AVAILABLE:
            self.status = ProviderStatus.NOT_CONFIGURED
            return
        
        if self.status == ProviderStatus.AVAILABLE:
            try:
                genai.configure(api_key=self.config.api_key)
                self.model = genai.GenerativeModel(self.config.model)
                self._test_connection()
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.status = ProviderStatus.ERROR
    
    def _test_connection(self):
        """Test Gemini API connection."""
        try:
            response = self.model.generate_content(
                "test",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10
                )
            )
            logger.info(f"Gemini connection test successful with {self.config.model}")
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            raise
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """Perform analysis using Gemini.
        
        Args:
            request: Analysis request
        
        Returns:
            Analysis response
        """
        if self.status != ProviderStatus.AVAILABLE:
            return self.handle_error(Exception("Provider not available"))
        
        if not self.check_rate_limit():
            return self.handle_error(Exception("Rate limit exceeded"))
        
        start_time = time.time()
        
        try:
            # Create prompt
            prompt = self._create_prompt(request)
            
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
                response_mime_type="application/json"  # Request JSON response
            )
            
            # Call Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract response
            raw_response = response.text
            parsed = self._parse_response(raw_response)
            
            # Estimate tokens (Gemini doesn't always provide token count)
            tokens_used = len(prompt.split()) + len(raw_response.split())
            cost = self._calculate_cost(tokens_used)
            processing_time = time.time() - start_time
            
            # Update metrics
            self.update_metrics(tokens_used, cost)
            
            # Create response
            result = AnalysisResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=self.config.model,
                genre=parsed.get('genre'),
                subgenres=parsed.get('subgenres', []),
                mood=parsed.get('mood'),
                moods=parsed.get('moods', []),
                tags=parsed.get('tags', []),
                instruments=parsed.get('instruments', []),
                era=parsed.get('era'),
                style=parsed.get('style'),
                scene=parsed.get('scene'),
                confidence=parsed.get('confidence', 0.7),
                raw_response=raw_response,
                processing_time=processing_time,
                tokens_used=tokens_used,
                cost=cost
            )
            
            return self.validate_response(result)
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self.handle_error(e)
    
    def _create_prompt(self, request: AnalysisRequest) -> str:
        """Create analysis prompt for Gemini.
        
        Args:
            request: Analysis request
        
        Returns:
            Formatted prompt
        """
        if request.custom_prompt:
            return request.custom_prompt
        
        base_prompt = self.create_base_prompt(request.track_data)
        
        # Gemini-specific formatting
        gemini_instruction = """
You are an expert music analyst. Analyze this track and respond with a JSON object containing:

- genre: The primary musical genre
- subgenres: An array of 1-3 relevant subgenres
- mood: The primary emotional mood
- moods: Array of additional moods
- tags: Array of 5-10 descriptive tags
- instruments: Array of detected or likely instruments
- era: The production era (e.g., "1980s", "Modern")
- style: The production style
- scene: Where this music would typically be played
- confidence: Your confidence level from 0 to 1

Ensure your response is valid JSON format."""
        
        return f"{base_prompt}\n\n{gemini_instruction}"
    
    def _parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse Gemini response.
        
        Args:
            raw_response: Raw response text
        
        Returns:
            Parsed dictionary
        """
        try:
            # Gemini should return JSON directly
            data = json.loads(raw_response)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.debug(f"Raw response: {raw_response}")
            
            # Try to extract JSON if wrapped
            try:
                if "{" in raw_response and "}" in raw_response:
                    start = raw_response.find("{")
                    end = raw_response.rfind("}") + 1
                    json_str = raw_response[start:end]
                    data = json.loads(json_str)
                    return data
            except:
                pass
            
            return {
                'genre': 'Unknown',
                'confidence': 0.3,
                'error': 'Failed to parse response'
            }
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost for tokens used.
        
        Args:
            tokens: Estimated total tokens
        
        Returns:
            Estimated cost
        """
        model_cost = self.MODEL_COSTS.get(self.config.model, {
            "input": 0.0005,
            "output": 0.0015
        })
        
        # Estimate input/output split
        input_tokens = tokens * 0.6
        output_tokens = tokens * 0.4
        
        cost = (input_tokens * model_cost["input"] + 
                output_tokens * model_cost["output"]) / 1000
        
        return cost

# Export
__all__ = ['GeminiProvider']
```

## Step 6: Multi-Provider Manager

### 6.1 Create Provider Manager
Create `src/analysis/providers/provider_manager.py`:

```python
"""Multi-provider manager for intelligent LLM selection and fallback."""

from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
from enum import Enum

from src.config import get_config
from src.analysis.providers.base_provider import (
    ProviderConfig, AnalysisRequest, AnalysisResponse
)
from src.analysis.providers.provider_factory import ProviderFactory

# Import all providers to trigger registration
from src.analysis.providers.openai_provider import OpenAIProvider
from src.analysis.providers.anthropic_provider import AnthropicProvider
from src.analysis.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)

class SelectionStrategy(Enum):
    """Provider selection strategies."""
    COST_OPTIMIZED = "cost"
    QUALITY_OPTIMIZED = "quality"
    SPEED_OPTIMIZED = "speed"
    BALANCED = "balanced"
    ROUND_ROBIN = "round_robin"

@dataclass
class ProviderPreferences:
    """Provider selection preferences."""
    strategy: SelectionStrategy = SelectionStrategy.BALANCED
    preferred_providers: List[str] = None
    excluded_providers: List[str] = None
    max_cost_per_request: float = 0.10
    min_confidence: float = 0.6
    enable_fallback: bool = True

class ProviderManager:
    """Manager for multi-provider LLM analysis."""
    
    # Provider rankings for different strategies
    STRATEGY_RANKINGS = {
        SelectionStrategy.COST_OPTIMIZED: [
            'gemini', 'anthropic', 'openai', 'zai'
        ],
        SelectionStrategy.QUALITY_OPTIMIZED: [
            'openai', 'anthropic', 'gemini', 'zai'
        ],
        SelectionStrategy.SPEED_OPTIMIZED: [
            'gemini', 'openai', 'anthropic', 'zai'
        ],
        SelectionStrategy.BALANCED: [
            'openai', 'gemini', 'anthropic', 'zai'
        ]
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize provider manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or get_config()
        self.preferences = ProviderPreferences()
        self._round_robin_index = 0
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers."""
        logger.info("Initializing LLM providers...")
        
        # Get provider configurations
        provider_configs = self.config.providers
        
        for provider_name, provider_config in provider_configs.items():
            if not isinstance(provider_config, ProviderConfig):
                # Convert dict to ProviderConfig
                provider_config = ProviderConfig(**provider_config.__dict__)
            
            if provider_config.enabled and provider_config.api_key:
                provider = ProviderFactory.create_provider(
                    provider_name, provider_config
                )
                if provider:
                    logger.info(f"Initialized provider: {provider_name}")
                else:
                    logger.warning(f"Failed to initialize provider: {provider_name}")
        
        active = ProviderFactory.get_active_providers()
        logger.info(f"Active providers: {len(active)}")
    
    def analyze(self, track_data: Dict[str, Any], 
               preferences: Optional[ProviderPreferences] = None) -> AnalysisResponse:
        """Analyze track with intelligent provider selection.
        
        Args:
            track_data: Track information for analysis
            preferences: Optional provider preferences
        
        Returns:
            Analysis response
        """
        prefs = preferences or self.preferences
        
        # Create analysis request
        request = AnalysisRequest(
            track_data=track_data,
            analysis_type="full",
            include_confidence=True
        )
        
        # Select provider based on strategy
        provider_name = self._select_provider(prefs)
        
        if prefs.enable_fallback:
            # Use factory fallback mechanism
            response = ProviderFactory.analyze_with_fallback(
                request, provider_name
            )
        else:
            # Try single provider only
            provider = ProviderFactory._instances.get(provider_name)
            if provider:
                response = provider.analyze(request)
            else:
                response = AnalysisResponse(
                    success=False,
                    provider="manager",
                    model="none",
                    error=f"Provider {provider_name} not available"
                )
        
        # Validate response meets requirements
        if response.success and response.confidence < prefs.min_confidence:
            logger.warning(f"Response confidence {response.confidence} below threshold {prefs.min_confidence}")
        
        if response.success and response.cost > prefs.max_cost_per_request:
            logger.warning(f"Response cost ${response.cost:.4f} exceeds limit ${prefs.max_cost_per_request:.4f}")
        
        return response
    
    def _select_provider(self, preferences: ProviderPreferences) -> Optional[str]:
        """Select provider based on preferences.
        
        Args:
            preferences: Provider preferences
        
        Returns:
            Selected provider name
        """
        available = ProviderFactory.get_active_providers()
        if not available:
            logger.error("No providers available")
            return None
        
        available_names = [p.PROVIDER_NAME for p in available]
        
        # Apply exclusions
        if preferences.excluded_providers:
            available_names = [
                name for name in available_names 
                if name not in preferences.excluded_providers
            ]
        
        # Apply preferences
        if preferences.preferred_providers:
            for preferred in preferences.preferred_providers:
                if preferred in available_names:
                    return preferred
        
        # Apply strategy
        if preferences.strategy == SelectionStrategy.ROUND_ROBIN:
            # Round-robin selection
            if available_names:
                selected = available_names[self._round_robin_index % len(available_names)]
                self._round_robin_index += 1
                return selected
        else:
            # Use strategy rankings
            rankings = self.STRATEGY_RANKINGS.get(
                preferences.strategy,
                self.STRATEGY_RANKINGS[SelectionStrategy.BALANCED]
            )
            
            for provider_name in rankings:
                if provider_name in available_names:
                    return provider_name
        
        # Fallback to first available
        return available_names[0] if available_names else None
    
    def analyze_batch(self, tracks: List[Dict[str, Any]], 
                     preferences: Optional[ProviderPreferences] = None,
                     parallel: bool = True,
                     max_workers: int = 4) -> List[AnalysisResponse]:
        """Analyze multiple tracks with load balancing.
        
        Args:
            tracks: List of track data dictionaries
            preferences: Optional provider preferences
            parallel: Whether to process in parallel
            max_workers: Maximum parallel workers
        
        Returns:
            List of analysis responses
        """
        results = []
        
        if parallel and len(tracks) > 1:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.analyze, track, preferences): i
                    for i, track in enumerate(tracks)
                }
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Batch analysis error: {e}")
                        results.append(AnalysisResponse(
                            success=False,
                            provider="manager",
                            model="batch",
                            error=str(e)
                        ))
        else:
            for track in tracks:
                try:
                    result = self.analyze(track, preferences)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Track analysis error: {e}")
                    results.append(AnalysisResponse(
                        success=False,
                        provider="manager",
                        model="batch",
                        error=str(e)
                    ))
        
        return results
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get statistics for all providers.
        
        Returns:
            Provider statistics
        """
        stats = ProviderFactory.get_provider_stats()
        
        # Add manager-level stats
        stats['selection_strategy'] = self.preferences.strategy.value
        stats['fallback_enabled'] = self.preferences.enable_fallback
        
        return stats
    
    def optimize_selection(self, historical_data: List[AnalysisResponse]) -> ProviderPreferences:
        """Optimize provider selection based on historical performance.
        
        Args:
            historical_data: Historical analysis responses
        
        Returns:
            Optimized preferences
        """
        if not historical_data:
            return self.preferences
        
        # Calculate provider performance metrics
        provider_stats = {}
        
        for response in historical_data:
            provider = response.provider
            if provider not in provider_stats:
                provider_stats[provider] = {
                    'count': 0,
                    'success_rate': 0,
                    'avg_confidence': 0,
                    'avg_time': 0,
                    'avg_cost': 0
                }
            
            stats = provider_stats[provider]
            stats['count'] += 1
            if response.success:
                stats['success_rate'] += 1
                stats['avg_confidence'] += response.confidence
                stats['avg_time'] += response.processing_time
                stats['avg_cost'] += response.cost
        
        # Calculate averages
        for provider, stats in provider_stats.items():
            if stats['count'] > 0:
                stats['success_rate'] /= stats['count']
                if stats['success_rate'] > 0:
                    success_count = stats['success_rate'] * stats['count']
                    stats['avg_confidence'] /= success_count
                    stats['avg_time'] /= success_count
                    stats['avg_cost'] /= success_count
        
        # Rank providers by performance
        ranked = sorted(
            provider_stats.items(),
            key=lambda x: (
                x[1]['success_rate'] * 0.4 +
                x[1]['avg_confidence'] * 0.3 +
                (1 - min(x[1]['avg_time'] / 10, 1)) * 0.2 +
                (1 - min(x[1]['avg_cost'] / 0.1, 1)) * 0.1
            ),
            reverse=True
        )
        
        # Create optimized preferences
        optimized = ProviderPreferences(
            strategy=SelectionStrategy.BALANCED,
            preferred_providers=[provider for provider, _ in ranked[:3]],
            excluded_providers=[],
            enable_fallback=True
        )
        
        logger.info(f"Optimized provider preferences: {optimized.preferred_providers}")
        
        return optimized

# Singleton instance
_manager = None

def get_provider_manager(config: Optional[Dict[str, Any]] = None) -> ProviderManager:
    """Get or create provider manager instance.
    
    Args:
        config: Optional configuration
    
    Returns:
        Provider manager instance
    """
    global _manager
    if _manager is None:
        _manager = ProviderManager(config)
    return _manager

# Export
__all__ = [
    'ProviderManager', 'ProviderPreferences', 'SelectionStrategy',
    'get_provider_manager'
]
```

## Step 7: Integration with Enhanced Analyzer

### 7.1 Update Enhanced Analyzer for AI Integration
Create `src/analysis/ai_enricher.py`:

```python
"""AI enrichment integration for enhanced analyzer."""

from typing import Dict, Any, Optional, List
import logging

from src.analysis.providers.provider_manager import (
    get_provider_manager, ProviderPreferences, SelectionStrategy
)
from src.analysis.providers.base_provider import AnalysisRequest

logger = logging.getLogger(__name__)

class AIEnricher:
    """AI enrichment service for music analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize AI enricher.
        
        Args:
            config: Optional configuration
        """
        self.manager = get_provider_manager(config)
    
    def enrich_analysis(self, track_data: Dict[str, Any],
                        provider: Optional[str] = None,
                        strategy: SelectionStrategy = SelectionStrategy.BALANCED) -> Dict[str, Any]:
        """Enrich track analysis with AI-generated metadata.
        
        Args:
            track_data: Basic track analysis data
            provider: Preferred provider name
            strategy: Selection strategy
        
        Returns:
            Enriched analysis dictionary
        """
        # Set preferences
        preferences = ProviderPreferences(
            strategy=strategy,
            preferred_providers=[provider] if provider else None,
            enable_fallback=True,
            min_confidence=0.6
        )
        
        # Perform AI analysis
        response = self.manager.analyze(track_data, preferences)
        
        if response.success:
            return {
                'success': True,
                'provider': response.provider,
                'model': response.model,
                'genre': response.genre,
                'subgenres': response.subgenres,
                'mood': response.mood,
                'moods': response.moods,
                'tags': response.tags,
                'instruments': response.instruments,
                'era': response.era,
                'style': response.style,
                'scene': response.scene,
                'confidence': response.confidence,
                'processing_time': response.processing_time,
                'cost': response.cost
            }
        else:
            return {
                'success': False,
                'error': response.error
            }
    
    def enrich_batch(self, tracks: List[Dict[str, Any]],
                    strategy: SelectionStrategy = SelectionStrategy.BALANCED,
                    parallel: bool = True) -> List[Dict[str, Any]]:
        """Enrich multiple tracks with AI analysis.
        
        Args:
            tracks: List of track data dictionaries
            strategy: Selection strategy
            parallel: Whether to process in parallel
        
        Returns:
            List of enriched analysis dictionaries
        """
        preferences = ProviderPreferences(
            strategy=strategy,
            enable_fallback=True
        )
        
        responses = self.manager.analyze_batch(
            tracks, preferences, parallel
        )
        
        results = []
        for response in responses:
            if response.success:
                results.append({
                    'success': True,
                    'provider': response.provider,
                    'genre': response.genre,
                    'subgenres': response.subgenres,
                    'mood': response.mood,
                    'tags': response.tags,
                    'confidence': response.confidence
                })
            else:
                results.append({
                    'success': False,
                    'error': response.error
                })
        
        return results

# Export
__all__ = ['AIEnricher']
```

## Success Criteria

The LLM integration is complete when:

1. **Base Architecture**:
   - Abstract base provider class with standard interface
   - Configuration management with validation
   - Standard request/response formats
   - Error handling and retry logic

2. **Provider Factory**:
   - Auto-registration decorator system
   - Provider instance management
   - Fallback mechanism with priority ordering
   - Statistics and metrics tracking

3. **Provider Implementations**:
   - OpenAI GPT integration (GPT-4, GPT-3.5)
   - Anthropic Claude integration (Opus, Sonnet, Haiku)
   - Google Gemini integration (1.5 Flash, 1.5 Pro)
   - Consistent response parsing and validation

4. **Multi-Provider Management**:
   - Intelligent provider selection strategies
   - Cost optimization and rate limiting
   - Parallel batch processing
   - Performance-based optimization

5. **Integration**:
   - Seamless integration with enhanced analyzer
   - AI enrichment service
   - Storage integration for AI results

## Testing the LLM Integration

Create `test_llm_integration.py`:

```python
#!/usr/bin/env python3
"""Test LLM integration."""

import os
from src.analysis.providers.provider_manager import (
    get_provider_manager, SelectionStrategy, ProviderPreferences
)
from src.analysis.ai_enricher import AIEnricher

def test_provider_initialization():
    """Test provider initialization."""
    print("Testing provider initialization...")
    
    manager = get_provider_manager()
    stats = manager.get_provider_statistics()
    
    print(f"Registered providers: {stats['registered']}")
    print(f"Active providers: {stats['active']}")
    
    for provider, metrics in stats['providers'].items():
        print(f"  {provider}: {metrics['status']}")

def test_single_analysis():
    """Test single track analysis."""
    print("\nTesting single track analysis...")
    
    track_data = {
        'title': 'Test Track',
        'artist': 'Test Artist',
        'bpm': 128,
        'key': 'Am',
        'energy': 0.7,
        'duration': 240
    }
    
    enricher = AIEnricher()
    result = enricher.enrich_analysis(
        track_data,
        strategy=SelectionStrategy.COST_OPTIMIZED
    )
    
    if result['success']:
        print(f"✓ Analysis successful")
        print(f"  Provider: {result['provider']}")
        print(f"  Genre: {result['genre']}")
        print(f"  Confidence: {result['confidence']}")
    else:
        print(f"✗ Analysis failed: {result['error']}")

def test_fallback():
    """Test provider fallback."""
    print("\nTesting provider fallback...")
    
    manager = get_provider_manager()
    
    # Force fallback by excluding primary provider
    preferences = ProviderPreferences(
        excluded_providers=['openai'],
        enable_fallback=True
    )
    
    track_data = {'title': 'Fallback Test', 'bpm': 120}
    response = manager.analyze(track_data, preferences)
    
    if response.success:
        print(f"✓ Fallback successful to {response.provider}")
    else:
        print(f"✗ Fallback failed: {response.error}")

if __name__ == "__main__":
    print("MAP4 LLM Integration Test")
    print("=" * 50)
    
    # Check for API keys
    has_keys = False
    for provider in ['OPENAI', 'ANTHROPIC', 'GEMINI']:
        if os.getenv(f"{provider}_API_KEY"):
            print(f"✓ {provider} API key found")
            has_keys = True
        else:
            print(f"✗ {provider} API key not found")
    
    if has_keys:
        print("\n" + "=" * 50)
        test_provider_initialization()
        test_single_analysis()
        test_fallback()
    else:
        print("\nNo API keys found. Set environment variables to test.")
    
    print("\n" + "=" * 50)
    print("✓ LLM integration framework functional!")
```

## Next Steps

After completing the LLM integration:

1. Build the PyQt6 user interface (see `04-ui-development.md`)
2. Implement the BMAD methodology (see `05-bmad-framework.md`)
3. Create the unified CLI system (see `06-cli-system.md`)
4. Add integration and testing (see `07-integration-testing.md`)

This LLM integration provides a robust, extensible system for AI-powered music analysis with automatic fallback, cost optimization, and support for multiple providers.