"""Multi-LLM Enricher - Unified interface for music analysis with cost optimization"""

from __future__ import annotations

import os
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from src.analysis.llm_provider import (
    LLMConfig, LLMProvider, LLMProviderFactory, 
    LLMResponse, get_recommended_configs
)


@dataclass
class EnrichmentResult:
    """Result of music track enrichment"""
    success: bool
    genre: Optional[str] = None
    subgenre: Optional[str] = None  
    mood: Optional[str] = None
    era: Optional[str] = None
    tags: List[str] = None
    ai_confidence: float = 0.0
    ai_model: str = "unknown"
    provider: str = "unknown"
    processing_time_ms: int = 0
    cost_estimate: Optional[float] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class MultiLLMEnricher:
    """Multi-LLM enricher with automatic fallback and cost optimization"""
    
    def __init__(self, preferred_provider: Optional[str] = None):
        """Initialize multi-LLM enricher
        
        Args:
            preferred_provider: Preferred LLM provider ('openai', 'gemini', or 'zai')
                               If None, will use most cost-effective available
        """
        self.providers = []
        self.current_provider = None
        
        # Get provider configurations from environment
        self._initialize_providers(preferred_provider)
        
        if not self.providers:
            print("⚠️ No LLM providers configured. Please add API keys to .env file")
            
    def _initialize_providers(self, preferred_provider: Optional[str] = None) -> None:
        """Initialize available LLM providers based on environment configuration"""
        
        # Try to configure preferred provider first
        if preferred_provider:
            config = self._create_config_for_provider(preferred_provider)
            if config:
                try:
                    provider = LLMProviderFactory.create_provider(config)
                    self.providers.append(provider)
                    self.current_provider = provider
                    print(f"✅ {preferred_provider.title()} provider configured as primary")
                except Exception as e:
                    print(f"❌ Failed to configure {preferred_provider}: {e}")
        
        # Add other available providers as fallbacks
        recommended_configs = get_recommended_configs()
        for config in recommended_configs:
            if preferred_provider and config.provider.value == preferred_provider:
                continue  # Already added as primary
                
            try:
                provider = LLMProviderFactory.create_provider(config)
                self.providers.append(provider)
                if not self.current_provider:
                    self.current_provider = provider
                print(f"✅ {config.provider.value.title()} provider added as fallback")
            except Exception as e:
                print(f"❌ Failed to configure {config.provider.value}: {e}")
    
    def _create_config_for_provider(self, provider_name: str) -> Optional[LLMConfig]:
        """Create configuration for Anthropic Claude only"""
        
        if provider_name.lower() == "anthropic":
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key or api_key == 'your_anthropic_api_key_here':
                return None
                
            return LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                api_key=api_key,
                model=os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307'),
                max_tokens=int(os.getenv('ANTHROPIC_MAX_TOKENS', '1000')),
                temperature=float(os.getenv('ANTHROPIC_TEMPERATURE', '0.1'))
            )
        
        # Only Anthropic is supported
        return None
    
    def analyze_track(self, track_data: Dict[str, Any], 
                     progress_callback: Optional[Callable[[str, str], None]] = None) -> EnrichmentResult:
        """Analyze track with fallback support
        
        Args:
            track_data: Track metadata including HAMMS vector
            progress_callback: Optional callback for progress updates (provider, status)
            
        Returns:
            Enrichment result with analysis or error information
        """
        if not self.providers:
            return EnrichmentResult(
                success=False,
                error_message="No LLM providers available. Please configure API keys in .env file"
            )
        
        last_error = None
        
        # Try each provider in order (cheapest first)
        for provider in self.providers:
            try:
                provider_name = provider.config.provider.value.title()
                print(f"🔄 Analyzing with {provider_name} ({provider.config.model})...")
                
                # Notify UI about starting analysis
                if progress_callback:
                    progress_callback(provider_name, "analyzing")
                
                response = provider.analyze_track(track_data)
                
                if response.success:
                    # Notify UI about success
                    if progress_callback:
                        progress_callback(provider_name, "success")
                    
                    # Convert LLM response to enrichment result
                    return EnrichmentResult(
                        success=True,
                        genre=response.content.get('genre'),
                        subgenre=response.content.get('subgenre'),
                        mood=response.content.get('mood'),
                        era=response.content.get('era'),
                        tags=response.content.get('tags', []),
                        ai_confidence=response.content.get('confidence', 0.5),
                        ai_model=response.model,
                        provider=response.provider.value,
                        processing_time_ms=response.processing_time_ms,
                        cost_estimate=response.cost_estimate
                    )
                else:
                    print(f"❌ {provider_name} failed: {response.error_message}")
                    # Notify UI about failure
                    if progress_callback:
                        progress_callback(provider_name, "failed")
                    last_error = response.error_message
                    continue
                    
            except Exception as e:
                print(f"❌ Exception with {provider_name}: {str(e)}")
                # Notify UI about failure
                if progress_callback:
                    progress_callback(provider_name, "failed")
                last_error = str(e)
                continue
        
        # All providers failed
        return EnrichmentResult(
            success=False,
            error_message=f"All LLM providers failed. Last error: {last_error}"
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [provider.config.provider.value for provider in self.providers]
    
    def get_cost_estimates(self) -> Dict[str, Dict[str, float]]:
        """Get cost estimates for all available providers"""
        estimates = {}
        
        for provider in self.providers:
            provider_name = provider.config.provider.value
            estimates[provider_name] = {
                "input_cost_per_1M": provider.pricing["input"],
                "output_cost_per_1M": provider.pricing["output"],
                "model": provider.config.model
            }
            
        return estimates
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a specific provider
        
        Args:
            provider_name: Name of provider to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        for provider in self.providers:
            if provider.config.provider.value == provider_name.lower():
                self.current_provider = provider
                print(f"✅ Switched to {provider_name.title()} provider")
                return True
        
        print(f"❌ Provider {provider_name} not available")
        return False


def create_multi_llm_enricher_from_env(preferred_provider: Optional[str] = None) -> Optional[MultiLLMEnricher]:
    """Create MultiLLMEnricher from environment variables
    
    Args:
        preferred_provider: Preferred provider to use (optional)
        
    Returns:
        MultiLLMEnricher instance if any providers are available, None otherwise
    """
    try:
        enricher = MultiLLMEnricher(preferred_provider=preferred_provider)
        if enricher.providers:
            return enricher
        else:
            return None
    except Exception as e:
        print(f"Failed to create MultiLLMEnricher: {e}")
        return None


def is_multi_llm_available() -> bool:
    """Check if any LLM providers are available
    
    Returns:
        True if at least one LLM provider is configured and available
    """
    try:
        enricher = MultiLLMEnricher()
        return len(enricher.providers) > 0
    except Exception:
        return False