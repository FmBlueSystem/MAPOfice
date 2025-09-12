"""Backward Compatibility Shim for OpenAI Provider

This module provides backward compatibility for code using the old openai_provider imports.
"""

import warnings
from src.analysis.provider_factory import ProviderFactory, ProviderConfig, ProviderType
from src.analysis.llm_provider import BaseLLMProvider, LLMConfig, LLMResponse, LLMProvider
import src.analysis.providers  # Trigger auto-registration


warnings.warn(
    "openai_provider.py is deprecated. Please use the new provider factory: "
    "from src.analysis.provider_factory import ProviderFactory",
    DeprecationWarning,
    stacklevel=2
)


class OpenAIProvider(BaseLLMProvider):
    """Compatibility wrapper for old OpenAIProvider class"""
    
    def __init__(self, config: LLMConfig):
        """Initialize compatibility wrapper"""
        super().__init__(config)
        
        # Create new provider config
        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key=config.api_key,
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            timeout=config.timeout,
            max_retries=config.max_retries,
            rate_limit_rpm=config.rate_limit_rpm
        )
        
        # Create actual provider using factory
        self._provider = ProviderFactory.create_provider(
            name="openai",
            config=provider_config
        )
        
        # Copy pricing info
        if hasattr(self._provider, 'pricing'):
            self.pricing = self._provider.pricing
            
        # Copy client for backward compatibility
        if hasattr(self._provider, 'client'):
            self.client = self._provider.client
    
    def analyze_track(self, track_data) -> LLMResponse:
        """Analyze track using new provider"""
        response = self._provider.analyze_track(track_data)
        
        # Convert to old response format
        return LLMResponse(
            success=response.success,
            content=response.content,
            raw_response=response.raw_response,
            provider=LLMProvider.OPENAI,
            model=response.model,
            processing_time_ms=response.processing_time_ms,
            tokens_used=response.tokens_used,
            cost_estimate=response.cost_estimate,
            error_message=response.error_message
        )
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate cost"""
        if hasattr(self._provider, '_estimate_cost'):
            return self._provider._estimate_cost(prompt_tokens, response_tokens)
        return 0.0