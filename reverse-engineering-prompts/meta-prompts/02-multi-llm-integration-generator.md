# Multi-LLM Integration Pattern Generator Meta-Prompt

## Overview
This meta-prompt generates comprehensive reproduction prompts for creating sophisticated multi-LLM provider systems with auto-registration, factory patterns, unified interfaces, and intelligent fallback strategies. Based on MAP4's successful multi-provider architecture.

## Meta-Prompt Template

### Multi-LLM Configuration Parameters
Configure your multi-LLM system with these parameters:

```yaml
# Multi-LLM Integration Configuration
SYSTEM_CONFIG:
  system_name: "{SYSTEM_NAME}"                    # e.g., "AI Analysis Engine", "Content Generator"
  primary_use_case: "{USE_CASE}"                  # "ANALYSIS", "GENERATION", "CLASSIFICATION", "PROCESSING"
  complexity_level: "{COMPLEXITY}"                # "BASIC", "INTERMEDIATE", "ADVANCED", "ENTERPRISE"
  
PROVIDERS:
  openai:
    enabled: {INCLUDE_OPENAI}                      # true/false
    models: [{OPENAI_MODELS}]                      # ["gpt-4", "gpt-3.5-turbo", "gpt-4o-mini"]
    priority: {OPENAI_PRIORITY}                    # 1-10 (1 = highest)
    
  anthropic:
    enabled: {INCLUDE_ANTHROPIC}                   # true/false  
    models: [{ANTHROPIC_MODELS}]                   # ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"]
    priority: {ANTHROPIC_PRIORITY}                 # 1-10
    
  google:
    enabled: {INCLUDE_GOOGLE}                      # true/false
    models: [{GOOGLE_MODELS}]                      # ["gemini-1.5-flash", "gemini-1.5-pro"]
    priority: {GOOGLE_PRIORITY}                    # 1-10
    
  custom_providers: [{CUSTOM_PROVIDERS}]          # Additional providers

FEATURES:
  auto_registration: {AUTO_REGISTRATION}          # true/false
  factory_pattern: {FACTORY_PATTERN}              # true/false
  fallback_strategy: {FALLBACK_STRATEGY}          # "PRIORITY", "ROUND_ROBIN", "COST_OPTIMIZED", "PERFORMANCE"
  cost_optimization: {COST_OPTIMIZATION}          # true/false
  rate_limiting: {RATE_LIMITING}                  # true/false
  caching: {INCLUDE_CACHING}                      # true/false
  monitoring: {INCLUDE_MONITORING}                # true/false
  health_checks: {HEALTH_CHECKS}                  # true/false

ARCHITECTURE:
  unified_interface: {UNIFIED_INTERFACE}          # true/false
  async_support: {ASYNC_SUPPORT}                  # true/false
  batch_processing: {BATCH_PROCESSING}            # true/false
  streaming: {STREAMING_SUPPORT}                  # true/false
  retry_mechanisms: {RETRY_MECHANISMS}            # true/false
```

## Generated Multi-LLM System Template

Based on the configuration, this meta-prompt generates:

---

# {SYSTEM_NAME} - Multi-LLM Provider Integration System

## System Overview
Create a {COMPLEXITY} multi-LLM provider system for {USE_CASE} applications with intelligent provider management, cost optimization, and robust fallback strategies.

### Supported Providers
{#if INCLUDE_OPENAI}
- **OpenAI**: {OPENAI_MODELS} (Priority: {OPENAI_PRIORITY})
{/if}
{#if INCLUDE_ANTHROPIC}
- **Anthropic**: {ANTHROPIC_MODELS} (Priority: {ANTHROPIC_PRIORITY})
{/if}
{#if INCLUDE_GOOGLE}
- **Google Gemini**: {GOOGLE_MODELS} (Priority: {GOOGLE_PRIORITY})
{/if}
{#for provider in CUSTOM_PROVIDERS}
- **{provider.name}**: {provider.models} (Priority: {provider.priority})
{/for}

## Core Architecture Implementation

### 1. Base Provider Interface
Create the foundation for all LLM providers:

```python
"""
{SYSTEM_NAME} - Base Provider Architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import logging
import time
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class ProviderStatus(Enum):
    """Provider operational status."""
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited" 
    ERROR = "error"
    DISABLED = "disabled"
    NOT_CONFIGURED = "not_configured"
    MAINTENANCE = "maintenance"

class RequestPriority(Enum):
    """Request priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ProviderConfig:
    """Configuration for LLM providers."""
    name: str
    api_key: str
    models: List[str]
    default_model: str = ""
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 60  # requests per minute
    max_retries: int = 3
    retry_delay: float = 1.0
    cost_per_1k_tokens: float = 0.001
    priority: int = 5  # 1-10, lower = higher priority
    enabled: bool = True
    {#if HEALTH_CHECKS}
    health_check_interval: int = 300  # seconds
    {/if}
    {#if COST_OPTIMIZATION}
    daily_budget: float = 10.0  # USD
    cost_tracking: bool = True
    {/if}
    
    def validate(self) -> bool:
        """Validate provider configuration."""
        if not self.api_key or self.api_key in ["", "your_api_key_here"]:
            return False
        if not self.models:
            return False
        if not self.default_model and self.models:
            self.default_model = self.models[0]
        return True

@dataclass
class ProviderRequest:
    """Unified request format for all providers."""
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    priority: RequestPriority = RequestPriority.NORMAL
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = None
    {#if USE_CASE == "ANALYSIS"}
    analysis_type: str = "general"
    context_data: Dict[str, Any] = None
    {/if}
    {#if USE_CASE == "CLASSIFICATION"}
    categories: List[str] = None
    confidence_threshold: float = 0.5
    {/if}
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        {#if USE_CASE == "ANALYSIS"}
        if self.context_data is None:
            self.context_data = {}
        {/if}

@dataclass
class ProviderResponse:
    """Unified response format from all providers."""
    success: bool
    provider: str
    model: str
    content: str = ""
    {#if USE_CASE == "ANALYSIS"}
    # Analysis-specific fields
    analysis_results: Dict[str, Any] = None
    confidence: float = 0.0
    categories: List[str] = None
    {/if}
    {#if USE_CASE == "CLASSIFICATION"}
    # Classification-specific fields
    predicted_class: str = ""
    class_probabilities: Dict[str, float] = None
    {/if}
    usage: Dict[str, int] = None
    cost: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.usage is None:
            self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        {#if USE_CASE == "ANALYSIS"}
        if self.analysis_results is None:
            self.analysis_results = {}
        {/if}
        {#if USE_CASE == "CLASSIFICATION"}
        if self.class_probabilities is None:
            self.class_probabilities = {}
        {/if}

{#if AUTO_REGISTRATION}
# Provider auto-registration decorator
_registered_providers = {}

def register_provider(provider_class):
    """Decorator for automatic provider registration."""
    _registered_providers[provider_class.PROVIDER_NAME] = provider_class
    logger.info(f"Registered provider: {provider_class.PROVIDER_NAME}")
    return provider_class

def get_registered_providers():
    """Get all registered provider classes."""
    return _registered_providers.copy()
{/if}

class BaseProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    # Provider metadata - must be overridden
    PROVIDER_NAME = "base"
    SUPPORTED_MODELS = []
    DEFAULT_MODEL = ""
    BASE_URL = ""
    
    def __init__(self, config: ProviderConfig):
        """Initialize provider with configuration."""
        self.config = config
        self.status = ProviderStatus.NOT_CONFIGURED
        self._last_request_time = 0
        self._request_count = 0
        self._total_cost = 0.0
        {#if RATE_LIMITING}
        self._rate_limiter = self._setup_rate_limiter()
        {/if}
        {#if HEALTH_CHECKS}
        self._last_health_check = 0
        self._health_status = True
        {/if}
        
        # Validate and initialize
        if self.config.validate():
            self.status = ProviderStatus.AVAILABLE
            self._initialize_client()
        else:
            logger.error(f"Invalid configuration for {self.PROVIDER_NAME}")
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize provider-specific client."""
        pass
    
    @abstractmethod
    def _make_request(self, request: ProviderRequest) -> ProviderResponse:
        """Make request to provider. Must be implemented by subclasses."""
        pass
    
    {#if ASYNC_SUPPORT}
    @abstractmethod
    async def _make_async_request(self, request: ProviderRequest) -> ProviderResponse:
        """Make async request to provider. Must be implemented by subclasses."""
        pass
    {/if}
    
    {#if HEALTH_CHECKS}
    def health_check(self) -> bool:
        """Perform health check on provider."""
        try:
            test_request = ProviderRequest(
                prompt="Test connection",
                max_tokens=5,
                temperature=0.0
            )
            response = self._make_request(test_request)
            self._health_status = response.success
            self._last_health_check = time.time()
            return self._health_status
        except Exception as e:
            logger.error(f"Health check failed for {self.PROVIDER_NAME}: {e}")
            self._health_status = False
            return False
    {/if}
    
    {#if RATE_LIMITING}
    def _setup_rate_limiter(self):
        """Setup rate limiting for provider."""
        return {"requests": [], "limit": self.config.rate_limit}
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits."""
        now = time.time()
        minute_ago = now - 60
        
        # Remove old requests
        self._rate_limiter["requests"] = [
            req_time for req_time in self._rate_limiter["requests"]
            if req_time > minute_ago
        ]
        
        # Check if under limit
        return len(self._rate_limiter["requests"]) < self._rate_limiter["limit"]
    
    def _record_request(self):
        """Record request for rate limiting."""
        self._rate_limiter["requests"].append(time.time())
    {/if}
    
    {#if COST_OPTIMIZATION}
    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate request cost."""
        total_tokens = usage.get("total_tokens", 0)
        return (total_tokens / 1000) * self.config.cost_per_1k_tokens
    
    def get_daily_cost(self) -> float:
        """Get total cost for current day."""
        # Implementation would track daily costs
        return self._total_cost
    
    def is_within_budget(self, estimated_cost: float = 0) -> bool:
        """Check if request would exceed daily budget."""
        return (self._total_cost + estimated_cost) <= self.config.daily_budget
    {/if}
    
    def request(self, request: ProviderRequest) -> ProviderResponse:
        """Main request method with all safety checks."""
        start_time = time.time()
        
        # Pre-request validation
        if not self._can_make_request(request):
            return self._create_error_response("Cannot make request - validation failed")
        
        {#if RETRY_MECHANISMS}
        # Retry logic
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._make_request_with_safety(request)
                response.retry_count = attempt
                response.processing_time = time.time() - start_time
                return response
                
            except Exception as e:
                if attempt == self.config.max_retries:
                    return self._create_error_response(f"Request failed after {attempt + 1} attempts: {e}")
                    
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
        {/if}
        {#if not RETRY_MECHANISMS}
        # Single attempt
        try:
            response = self._make_request_with_safety(request)
            response.processing_time = time.time() - start_time
            return response
        except Exception as e:
            return self._create_error_response(str(e))
        {/if}
    
    {#if ASYNC_SUPPORT}
    async def async_request(self, request: ProviderRequest) -> ProviderResponse:
        """Async version of request method."""
        start_time = time.time()
        
        if not self._can_make_request(request):
            return self._create_error_response("Cannot make async request - validation failed")
        
        try:
            response = await self._make_async_request(request)
            response.processing_time = time.time() - start_time
            return response
        except Exception as e:
            return self._create_error_response(str(e))
    {/if}
    
    def _can_make_request(self, request: ProviderRequest) -> bool:
        """Check if request can be made safely."""
        if self.status != ProviderStatus.AVAILABLE:
            return False
            
        {#if RATE_LIMITING}
        if not self._check_rate_limit():
            self.status = ProviderStatus.RATE_LIMITED
            return False
        {/if}
        
        {#if COST_OPTIMIZATION}
        estimated_cost = (request.max_tokens or self.config.max_tokens) / 1000 * self.config.cost_per_1k_tokens
        if not self.is_within_budget(estimated_cost):
            logger.warning(f"Request would exceed daily budget for {self.PROVIDER_NAME}")
            return False
        {/if}
        
        {#if HEALTH_CHECKS}
        # Periodic health checks
        if time.time() - self._last_health_check > self.config.health_check_interval:
            if not self.health_check():
                self.status = ProviderStatus.ERROR
                return False
        {/if}
        
        return True
    
    def _make_request_with_safety(self, request: ProviderRequest) -> ProviderResponse:
        """Make request with safety measures."""
        {#if RATE_LIMITING}
        self._record_request()
        {/if}
        
        # Apply request defaults
        if request.max_tokens is None:
            request.max_tokens = self.config.max_tokens
        if request.temperature is None:
            request.temperature = self.config.temperature
        if request.model is None:
            request.model = self.config.default_model
            
        # Make the actual request
        response = self._make_request(request)
        
        {#if COST_OPTIMIZATION}
        # Track costs
        if response.success and response.usage:
            response.cost = self._calculate_cost(response.usage)
            self._total_cost += response.cost
        {/if}
        
        return response
    
    def _create_error_response(self, error_message: str) -> ProviderResponse:
        """Create standardized error response."""
        return ProviderResponse(
            success=False,
            provider=self.PROVIDER_NAME,
            model=self.config.default_model,
            error=error_message
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status information."""
        return {
            "provider": self.PROVIDER_NAME,
            "status": self.status.value,
            "models": self.SUPPORTED_MODELS,
            "default_model": self.config.default_model,
            "rate_limit": self.config.rate_limit,
            {#if COST_OPTIMIZATION}
            "daily_cost": self._total_cost,
            "daily_budget": self.config.daily_budget,
            "budget_remaining": self.config.daily_budget - self._total_cost,
            {/if}
            {#if HEALTH_CHECKS}
            "health_status": self._health_status,
            "last_health_check": self._last_health_check,
            {/if}
            "priority": self.config.priority,
            "enabled": self.config.enabled
        }
```

### 2. Provider Implementations

{#if INCLUDE_OPENAI}
#### OpenAI Provider
```python
"""
OpenAI Provider Implementation
"""

import openai
from typing import Dict, Any
import json

{#if AUTO_REGISTRATION}
@register_provider
{/if}
class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""
    
    PROVIDER_NAME = "openai"
    SUPPORTED_MODELS = {OPENAI_MODELS}
    DEFAULT_MODEL = "{OPENAI_MODELS[0] if OPENAI_MODELS else 'gpt-3.5-turbo'}"
    BASE_URL = "https://api.openai.com/v1"
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        self.client = openai.OpenAI(api_key=self.config.api_key)
    
    def _make_request(self, request: ProviderRequest) -> ProviderResponse:
        """Make request to OpenAI API."""
        try:
            # Prepare messages
            messages = [{"role": "user", "content": request.prompt}]
            
            {#if USE_CASE == "ANALYSIS"}
            # Add context for analysis
            if request.context_data:
                context_prompt = f"Context: {json.dumps(request.context_data)}\n\n{request.prompt}"
                messages = [{"role": "user", "content": context_prompt}]
            {/if}
            
            # Make API call
            response = self.client.chat.completions.create(
                model=request.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                timeout=request.timeout or self.config.timeout
            )
            
            # Parse response
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens, 
                "total_tokens": response.usage.total_tokens
            }
            
            {#if USE_CASE == "ANALYSIS"}
            # Parse analysis results
            analysis_results = self._parse_analysis_response(content)
            return ProviderResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=request.model,
                content=content,
                analysis_results=analysis_results,
                confidence=analysis_results.get("confidence", 0.5),
                usage=usage
            )
            {/if}
            {#if USE_CASE == "CLASSIFICATION"}
            # Parse classification results
            classification = self._parse_classification_response(content, request.categories)
            return ProviderResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=request.model,
                content=content,
                predicted_class=classification["predicted_class"],
                class_probabilities=classification["probabilities"],
                usage=usage
            )
            {/if}
            {#if USE_CASE not in ["ANALYSIS", "CLASSIFICATION"]}
            return ProviderResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=request.model,
                content=content,
                usage=usage
            )
            {/if}
            
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            return self._create_error_response(str(e))
    
    {#if ASYNC_SUPPORT}
    async def _make_async_request(self, request: ProviderRequest) -> ProviderResponse:
        """Make async request to OpenAI API."""
        async_client = openai.AsyncOpenAI(api_key=self.config.api_key)
        
        try:
            messages = [{"role": "user", "content": request.prompt}]
            
            response = await async_client.chat.completions.create(
                model=request.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                timeout=request.timeout or self.config.timeout
            )
            
            # Process response similar to sync version
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return ProviderResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=request.model,
                content=content,
                usage=usage
            )
            
        except Exception as e:
            return self._create_error_response(str(e))
    {/if}
    
    {#if USE_CASE == "ANALYSIS"}
    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parse OpenAI response for analysis results."""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                return json.loads(content)
            
            # Otherwise, extract key information
            results = {"raw_response": content}
            
            # Add specific parsing logic based on your analysis needs
            if "confidence:" in content.lower():
                try:
                    confidence_line = [line for line in content.split('\n') if 'confidence:' in line.lower()][0]
                    confidence = float(confidence_line.split(':')[1].strip().replace('%', '')) / 100
                    results["confidence"] = confidence
                except:
                    results["confidence"] = 0.5
            
            return results
            
        except Exception as e:
            logger.warning(f"Failed to parse analysis response: {e}")
            return {"raw_response": content, "confidence": 0.5}
    {/if}
```
{/if}

{#if INCLUDE_ANTHROPIC}
#### Anthropic Provider
```python
"""
Anthropic Claude Provider Implementation
"""

import anthropic
from typing import Dict, Any

{#if AUTO_REGISTRATION}
@register_provider
{/if}
class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider implementation."""
    
    PROVIDER_NAME = "anthropic"
    SUPPORTED_MODELS = {ANTHROPIC_MODELS}
    DEFAULT_MODEL = "{ANTHROPIC_MODELS[0] if ANTHROPIC_MODELS else 'claude-3-haiku-20240307'}"
    BASE_URL = "https://api.anthropic.com"
    
    def _initialize_client(self):
        """Initialize Anthropic client."""
        self.client = anthropic.Anthropic(api_key=self.config.api_key)
    
    def _make_request(self, request: ProviderRequest) -> ProviderResponse:
        """Make request to Anthropic API."""
        try:
            response = self.client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=[{"role": "user", "content": request.prompt}]
            )
            
            content = response.content[0].text
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            return ProviderResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=request.model,
                content=content,
                usage=usage
            )
            
        except Exception as e:
            logger.error(f"Anthropic request failed: {e}")
            return self._create_error_response(str(e))
    
    {#if ASYNC_SUPPORT}
    async def _make_async_request(self, request: ProviderRequest) -> ProviderResponse:
        """Make async request to Anthropic API."""
        async_client = anthropic.AsyncAnthropic(api_key=self.config.api_key)
        
        try:
            response = await async_client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=[{"role": "user", "content": request.prompt}]
            )
            
            content = response.content[0].text
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            return ProviderResponse(
                success=True,
                provider=self.PROVIDER_NAME,
                model=request.model,
                content=content,
                usage=usage
            )
            
        except Exception as e:
            return self._create_error_response(str(e))
    {/if}
```
{/if}

### 3. Provider Factory and Manager

{#if FACTORY_PATTERN}
```python
"""
Multi-LLM Provider Factory and Manager
"""

from typing import Dict, List, Optional, Union
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

logger = logging.getLogger(__name__)

class ProviderFactory:
    """Factory for creating and managing LLM providers."""
    
    def __init__(self):
        """Initialize provider factory."""
        self._providers: Dict[str, BaseProvider] = {}
        self._configs: Dict[str, ProviderConfig] = {}
        {#if AUTO_REGISTRATION}
        self._registered_classes = get_registered_providers()
        {/if}
    
    def register_provider_config(self, name: str, config: ProviderConfig):
        """Register provider configuration."""
        self._configs[name] = config
        logger.info(f"Registered config for provider: {name}")
    
    def create_provider(self, name: str) -> Optional[BaseProvider]:
        """Create provider instance from registered configuration."""
        if name not in self._configs:
            logger.error(f"No configuration found for provider: {name}")
            return None
        
        config = self._configs[name]
        
        {#if AUTO_REGISTRATION}
        # Use auto-registered providers
        if name in self._registered_classes:
            provider_class = self._registered_classes[name]
            return provider_class(config)
        {/if}
        {#if not AUTO_REGISTRATION}
        # Manual provider creation
        if name == "openai" and INCLUDE_OPENAI:
            return OpenAIProvider(config)
        elif name == "anthropic" and INCLUDE_ANTHROPIC:
            return AnthropicProvider(config)
        elif name == "google" and INCLUDE_GOOGLE:
            return GoogleProvider(config)
        {/if}
        
        logger.error(f"Unknown provider type: {name}")
        return None
    
    def create_all_providers(self) -> Dict[str, BaseProvider]:
        """Create all configured providers."""
        providers = {}
        
        for name in self._configs:
            provider = self.create_provider(name)
            if provider and provider.status == ProviderStatus.AVAILABLE:
                providers[name] = provider
                logger.info(f"Successfully created provider: {name}")
            else:
                logger.warning(f"Failed to create provider: {name}")
        
        return providers
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        {#if AUTO_REGISTRATION}
        return list(self._registered_classes.keys())
        {/if}
        {#if not AUTO_REGISTRATION}
        available = []
        {#if INCLUDE_OPENAI}
        available.append("openai")
        {/if}
        {#if INCLUDE_ANTHROPIC}
        available.append("anthropic")
        {/if}
        {#if INCLUDE_GOOGLE}
        available.append("google")
        {/if}
        return available
        {/if}

class MultiLLMManager:
    """Manager for multiple LLM providers with intelligent routing."""
    
    def __init__(self, provider_configs: Dict[str, Dict[str, Any]]):
        """Initialize manager with provider configurations."""
        self.factory = ProviderFactory()
        self.providers: Dict[str, BaseProvider] = {}
        {#if FALLBACK_STRATEGY}
        self.fallback_strategy = "{FALLBACK_STRATEGY}"
        {/if}
        {#if INCLUDE_CACHING}
        self.cache = {}  # Simple in-memory cache
        {/if}
        {#if INCLUDE_MONITORING}
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "provider_usage": {},
            "average_response_time": 0.0
        }
        {/if}
        
        # Initialize providers
        self._initialize_providers(provider_configs)
    
    def _initialize_providers(self, configs: Dict[str, Dict[str, Any]]):
        """Initialize all providers from configurations."""
        for provider_name, config_dict in configs.items():
            if config_dict.get("enabled", True):
                config = ProviderConfig(
                    name=provider_name,
                    **config_dict
                )
                self.factory.register_provider_config(provider_name, config)
        
        # Create all providers
        self.providers = self.factory.create_all_providers()
        logger.info(f"Initialized {len(self.providers)} providers")
    
    {#if FALLBACK_STRATEGY == "PRIORITY"}
    def _get_providers_by_priority(self) -> List[BaseProvider]:
        """Get providers sorted by priority (lower number = higher priority)."""
        return sorted(
            [p for p in self.providers.values() if p.status == ProviderStatus.AVAILABLE],
            key=lambda x: x.config.priority
        )
    {/if}
    
    {#if FALLBACK_STRATEGY == "COST_OPTIMIZED"}
    def _get_providers_by_cost(self) -> List[BaseProvider]:
        """Get providers sorted by cost (lower cost first)."""
        return sorted(
            [p for p in self.providers.values() if p.status == ProviderStatus.AVAILABLE],
            key=lambda x: x.config.cost_per_1k_tokens
        )
    {/if}
    
    {#if FALLBACK_STRATEGY == "PERFORMANCE"}
    def _get_providers_by_performance(self) -> List[BaseProvider]:
        """Get providers sorted by performance metrics."""
        # This would use historical performance data
        return [p for p in self.providers.values() if p.status == ProviderStatus.AVAILABLE]
    {/if}
    
    def request(self, request: ProviderRequest, preferred_provider: str = None) -> ProviderResponse:
        """Make request with intelligent provider selection and fallback."""
        {#if INCLUDE_MONITORING}
        self.metrics["total_requests"] += 1
        {/if}
        
        {#if INCLUDE_CACHING}
        # Check cache first
        cache_key = self._generate_cache_key(request)
        if cache_key in self.cache:
            logger.debug("Returning cached response")
            return self.cache[cache_key]
        {/if}
        
        # Determine provider order
        provider_order = self._get_provider_order(preferred_provider)
        
        # Try providers in order
        last_error = None
        for provider in provider_order:
            try:
                logger.debug(f"Trying provider: {provider.PROVIDER_NAME}")
                response = provider.request(request)
                
                if response.success:
                    {#if INCLUDE_CACHING}
                    # Cache successful responses
                    self.cache[cache_key] = response
                    {/if}
                    {#if INCLUDE_MONITORING}
                    self.metrics["successful_requests"] += 1
                    self._update_provider_metrics(provider.PROVIDER_NAME, response)
                    {/if}
                    return response
                else:
                    last_error = response.error
                    logger.warning(f"Provider {provider.PROVIDER_NAME} failed: {response.error}")
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Provider {provider.PROVIDER_NAME} exception: {e}")
        
        # All providers failed
        {#if INCLUDE_MONITORING}
        self.metrics["failed_requests"] += 1
        {/if}
        
        return ProviderResponse(
            success=False,
            provider="none",
            model="",
            error=f"All providers failed. Last error: {last_error}"
        )
    
    {#if ASYNC_SUPPORT}
    async def async_request(self, request: ProviderRequest, preferred_provider: str = None) -> ProviderResponse:
        """Make async request with provider fallback."""
        provider_order = self._get_provider_order(preferred_provider)
        
        for provider in provider_order:
            try:
                response = await provider.async_request(request)
                if response.success:
                    return response
            except Exception as e:
                logger.error(f"Async provider {provider.PROVIDER_NAME} failed: {e}")
        
        return ProviderResponse(
            success=False,
            provider="none", 
            model="",
            error="All async providers failed"
        )
    {/if}
    
    {#if BATCH_PROCESSING}
    def batch_request(self, requests: List[ProviderRequest], max_workers: int = 5) -> List[ProviderResponse]:
        """Process multiple requests in parallel."""
        responses = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            future_to_request = {
                executor.submit(self.request, req): req 
                for req in requests
            }
            
            # Collect responses
            for future in as_completed(future_to_request):
                try:
                    response = future.result()
                    responses.append(response)
                except Exception as e:
                    # Create error response for failed request
                    responses.append(ProviderResponse(
                        success=False,
                        provider="batch_error",
                        model="",
                        error=str(e)
                    ))
        
        return responses
    {/if}
    
    def _get_provider_order(self, preferred_provider: str = None) -> List[BaseProvider]:
        """Get ordered list of providers to try."""
        available_providers = [p for p in self.providers.values() 
                             if p.status == ProviderStatus.AVAILABLE]
        
        if not available_providers:
            return []
        
        # If preferred provider specified and available, try it first
        if preferred_provider and preferred_provider in self.providers:
            preferred = self.providers[preferred_provider]
            if preferred.status == ProviderStatus.AVAILABLE:
                other_providers = [p for p in available_providers if p != preferred]
                return [preferred] + self._order_providers(other_providers)
        
        return self._order_providers(available_providers)
    
    def _order_providers(self, providers: List[BaseProvider]) -> List[BaseProvider]:
        """Order providers based on fallback strategy."""
        {#if FALLBACK_STRATEGY == "PRIORITY"}
        return sorted(providers, key=lambda x: x.config.priority)
        {/if}
        {#if FALLBACK_STRATEGY == "COST_OPTIMIZED"}
        return sorted(providers, key=lambda x: x.config.cost_per_1k_tokens)
        {/if}
        {#if FALLBACK_STRATEGY == "ROUND_ROBIN"}
        # Simple round-robin (would need state tracking for true round-robin)
        return providers
        {/if}
        {#if FALLBACK_STRATEGY == "PERFORMANCE"}
        # Sort by performance metrics (placeholder)
        return providers
        {/if}
    
    {#if INCLUDE_CACHING}
    def _generate_cache_key(self, request: ProviderRequest) -> str:
        """Generate cache key for request."""
        # Simple hash of key parameters
        key_data = f"{request.prompt}_{request.max_tokens}_{request.temperature}_{request.model}"
        return f"cache_{hash(key_data)}"
    {/if}
    
    {#if INCLUDE_MONITORING}
    def _update_provider_metrics(self, provider_name: str, response: ProviderResponse):
        """Update provider usage metrics."""
        if provider_name not in self.metrics["provider_usage"]:
            self.metrics["provider_usage"][provider_name] = {
                "requests": 0,
                "success_rate": 0.0,
                "average_response_time": 0.0,
                "total_cost": 0.0
            }
        
        provider_metrics = self.metrics["provider_usage"][provider_name]
        provider_metrics["requests"] += 1
        provider_metrics["total_cost"] += response.cost
        
        # Update average response time
        current_avg = provider_metrics["average_response_time"]
        current_count = provider_metrics["requests"]
        new_avg = ((current_avg * (current_count - 1)) + response.processing_time) / current_count
        provider_metrics["average_response_time"] = new_avg
    {/if}
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "total_providers": len(self.providers),
            "available_providers": len([p for p in self.providers.values() 
                                      if p.status == ProviderStatus.AVAILABLE]),
            "providers": {name: provider.get_status() 
                         for name, provider in self.providers.items()},
            {#if FALLBACK_STRATEGY}
            "fallback_strategy": self.fallback_strategy,
            {/if}
            {#if INCLUDE_MONITORING}
            "metrics": self.metrics,
            {/if}
        }
        
        return status
    
    def shutdown(self):
        """Gracefully shutdown all providers."""
        logger.info("Shutting down Multi-LLM Manager")
        # Cleanup resources, save metrics, etc.
        for provider in self.providers.values():
            # Provider-specific cleanup if needed
            pass
```
{/if}

## Configuration Template

```yaml
# {SYSTEM_NAME} Multi-LLM Configuration

# System settings
system:
  name: "{SYSTEM_NAME}"
  log_level: "INFO"
  {#if FALLBACK_STRATEGY}
  fallback_strategy: "{FALLBACK_STRATEGY}"
  {/if}
  {#if INCLUDE_CACHING}
  enable_caching: true
  cache_ttl: 3600  # seconds
  {/if}
  {#if BATCH_PROCESSING}
  batch_processing:
    max_workers: 5
    batch_size: 10
  {/if}

# Provider configurations
providers:
  {#if INCLUDE_OPENAI}
  openai:
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    models: {OPENAI_MODELS}
    default_model: "{OPENAI_MODELS[0] if OPENAI_MODELS else 'gpt-3.5-turbo'}"
    priority: {OPENAI_PRIORITY}
    max_tokens: 1000
    temperature: 0.7
    rate_limit: 60
    cost_per_1k_tokens: 0.002
    {#if COST_OPTIMIZATION}
    daily_budget: 10.0
    {/if}
  {/if}
  
  {#if INCLUDE_ANTHROPIC}
  anthropic:
    enabled: true
    api_key: "${ANTHROPIC_API_KEY}"
    models: {ANTHROPIC_MODELS}
    default_model: "{ANTHROPIC_MODELS[0] if ANTHROPIC_MODELS else 'claude-3-haiku-20240307'}"
    priority: {ANTHROPIC_PRIORITY}
    max_tokens: 1000
    temperature: 0.7
    rate_limit: 50
    cost_per_1k_tokens: 0.0015
    {#if COST_OPTIMIZATION}
    daily_budget: 10.0
    {/if}
  {/if}
  
  {#if INCLUDE_GOOGLE}
  google:
    enabled: true
    api_key: "${GOOGLE_API_KEY}"
    models: {GOOGLE_MODELS}
    default_model: "{GOOGLE_MODELS[0] if GOOGLE_MODELS else 'gemini-1.5-flash'}"
    priority: {GOOGLE_PRIORITY}
    max_tokens: 1000
    temperature: 0.7
    rate_limit: 60
    cost_per_1k_tokens: 0.001
    {#if COST_OPTIMIZATION}
    daily_budget: 10.0
    {/if}
  {/if}

{#if USE_CASE == "ANALYSIS"}
# Analysis-specific settings
analysis:
  default_analysis_type: "full"
  confidence_threshold: 0.7
  include_confidence_scores: true
{/if}

{#if USE_CASE == "CLASSIFICATION"}
# Classification-specific settings  
classification:
  default_categories: ["positive", "negative", "neutral"]
  confidence_threshold: 0.8
  multi_label: false
{/if}

{#if INCLUDE_MONITORING}
# Monitoring settings
monitoring:
  enabled: true
  metrics_retention: 7  # days
  alert_thresholds:
    error_rate: 0.1
    response_time: 5.0  # seconds
{/if}
```

## Usage Examples

### Basic Usage
```python
# Initialize Multi-LLM system
config = {
    {#if INCLUDE_OPENAI}
    "openai": {
        "enabled": True,
        "api_key": "your-openai-key",
        "models": {OPENAI_MODELS},
        "priority": {OPENAI_PRIORITY}
    },
    {/if}
    {#if INCLUDE_ANTHROPIC}
    "anthropic": {
        "enabled": True,
        "api_key": "your-anthropic-key", 
        "models": {ANTHROPIC_MODELS},
        "priority": {ANTHROPIC_PRIORITY}
    }
    {/if}
}

manager = MultiLLMManager(config)

# Make a request
request = ProviderRequest(
    prompt="Analyze this text for sentiment...",
    max_tokens=100
)

response = manager.request(request)
print(f"Response: {response.content}")
print(f"Provider: {response.provider}")
print(f"Cost: ${response.cost:.4f}")
```

{#if ASYNC_SUPPORT}
### Async Usage
```python
async def analyze_async():
    request = ProviderRequest(prompt="Analyze this...")
    response = await manager.async_request(request)
    return response
    
# Run async
import asyncio
result = asyncio.run(analyze_async())
```
{/if}

{#if BATCH_PROCESSING}
### Batch Processing
```python
# Process multiple requests
requests = [
    ProviderRequest(prompt=f"Analyze text {i}...")
    for i in range(10)
]

responses = manager.batch_request(requests, max_workers=3)
for i, response in enumerate(responses):
    print(f"Request {i}: {response.success}")
```
{/if}

## Installation Requirements

```bash
# Core dependencies
pip install openai anthropic google-generativeai

# Additional dependencies
pip install pyyaml python-dotenv dataclasses
pip install asyncio concurrent.futures  # For async/batch support
```

## Validation Criteria

A successful implementation should demonstrate:

1. **Provider Integration**: All configured providers work correctly
2. **Fallback Strategy**: System gracefully handles provider failures
3. **Cost Management**: Accurate cost tracking and budget controls
4. **Rate Limiting**: Respects provider rate limits
5. **Performance**: Efficient request routing and processing
6. **Monitoring**: Comprehensive metrics and status reporting

---

*Generated by Multi-LLM Integration Pattern Generator Meta-Prompt*
*Version 1.0 - Based on MAP4 Multi-Provider Architecture*