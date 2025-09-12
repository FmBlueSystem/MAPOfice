"""Enhanced Provider Factory with Auto-Registration System

This module implements a factory pattern with automatic provider registration
to eliminate duplicate providers and provide a clean, extensible architecture.
"""

from __future__ import annotations

import os
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, Type, Optional, List, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import logging

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported LLM provider types"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ZAI = "zai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


@dataclass
class ProviderConfig:
    """Unified configuration for any LLM provider"""
    provider_type: ProviderType
    api_key: str
    model: str
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    rate_limit_rpm: int = 60
    base_url: Optional[str] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_key or not self.api_key.strip():
            raise ValueError(f"{self.provider_type.value} API key is required and cannot be empty")
        
    @classmethod
    def from_env(cls, provider_type: ProviderType, model: str = None) -> ProviderConfig:
        """Create configuration from environment variables"""
        env_key_map = {
            ProviderType.OPENAI: "OPENAI_API_KEY",
            ProviderType.GEMINI: "GEMINI_API_KEY",
            ProviderType.ZAI: "ZAI_API_KEY",
            ProviderType.ANTHROPIC: "ANTHROPIC_API_KEY",
        }
        
        default_models = {
            ProviderType.OPENAI: "gpt-4o-mini",
            ProviderType.GEMINI: "gemini-1.5-flash",
            ProviderType.ZAI: "zai-2024",
            ProviderType.ANTHROPIC: "claude-3-haiku-20240307",
        }
        
        api_key = os.getenv(env_key_map.get(provider_type, ""))
        if not api_key:
            raise ValueError(f"API key not found in environment for {provider_type.value}")
        
        return cls(
            provider_type=provider_type,
            api_key=api_key,
            model=model or default_models.get(provider_type, "default")
        )


@dataclass
class ProviderResponse:
    """Standardized response from any LLM provider"""
    success: bool
    content: Dict[str, Any]
    raw_response: str
    provider_type: ProviderType
    model: str
    processing_time_ms: int
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseProvider(ABC):
    """Enhanced abstract base class for all LLM providers"""
    
    # Class-level metadata for auto-registration
    provider_type: ProviderType = None
    supported_models: List[str] = []
    
    def __init__(self, config: ProviderConfig):
        """Initialize provider with configuration"""
        self.config = config
        self.last_request_time = 0.0
        self.min_request_interval = 60.0 / config.rate_limit_rpm
        self._validate_config()
        
    def _validate_config(self):
        """Validate provider-specific configuration"""
        if self.provider_type and self.config.provider_type != self.provider_type:
            raise ValueError(
                f"Configuration mismatch: expected {self.provider_type.value}, "
                f"got {self.config.provider_type.value}"
            )
        
        if self.supported_models and self.config.model not in self.supported_models:
            logger.warning(f"Model {self.config.model} not in supported models: {self.supported_models}")
    
    def _wait_for_rate_limit(self) -> None:
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    @abstractmethod
    def analyze_track(self, track_metadata: Dict[str, Any]) -> ProviderResponse:
        """Analyze single track and return enriched metadata"""
        pass
    
    def batch_analyze(self, tracks: List[Dict[str, Any]]) -> List[ProviderResponse]:
        """Analyze multiple tracks efficiently (default implementation)"""
        results = []
        for track in tracks:
            try:
                result = self.analyze_track(track)
                results.append(result)
            except Exception as e:
                results.append(ProviderResponse(
                    success=False,
                    content={},
                    raw_response="",
                    provider_type=self.config.provider_type,
                    model=self.config.model,
                    processing_time_ms=0,
                    error_message=str(e)
                ))
        return results
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if provider is accessible and configured correctly"""
        pass
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost of the API call (optional implementation)"""
        return 0.0
    
    def get_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "provider_type": self.provider_type.value if self.provider_type else "unknown",
            "model": self.config.model,
            "supported_models": self.supported_models,
            "rate_limit_rpm": self.config.rate_limit_rpm,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }


# Legacy compatibility - import BaseLLMProvider for backward compatibility
try:
    from src.analysis.llm_provider import BaseLLMProvider
except ImportError:
    BaseLLMProvider = BaseProvider


class ProviderFactory:
    """Enhanced factory with auto-registration for LLM providers"""
    
    _providers: Dict[str, Type[BaseProvider]] = {}
    _instances: Dict[str, BaseProvider] = {}  # Singleton instances cache
    
    @classmethod
    def register_provider(cls, name: str = None) -> Callable:
        """Decorator for auto-registering providers
        
        Usage:
            @ProviderFactory.register_provider("custom_name")
            class MyProvider(BaseProvider):
                ...
        
        Or with auto-naming:
            @ProviderFactory.register_provider()
            class OpenAIProvider(BaseProvider):
                provider_type = ProviderType.OPENAI
                ...
        """
        def decorator(provider_class: Type[BaseProvider]) -> Type[BaseProvider]:
            provider_name = name
            
            # Auto-determine name if not provided
            if not provider_name:
                if hasattr(provider_class, 'provider_type') and provider_class.provider_type:
                    provider_name = provider_class.provider_type.value
                else:
                    # Extract from class name (e.g., OpenAIProvider -> openai)
                    class_name = provider_class.__name__
                    if class_name.endswith('Provider'):
                        provider_name = class_name[:-8].lower()
                    else:
                        provider_name = class_name.lower()
            
            cls._providers[provider_name] = provider_class
            logger.info(f"Registered provider: {provider_name} -> {provider_class.__name__}")
            return provider_class
        
        # Handle both @register_provider and @register_provider() syntax
        if name and not isinstance(name, str):
            # Called as @register_provider without parentheses
            provider_class = name
            name = None
            return decorator(provider_class)
        
        return decorator
    
    @classmethod
    def create_provider(
        cls, 
        name: str = None, 
        config: ProviderConfig = None,
        **kwargs
    ) -> BaseProvider:
        """Create or retrieve a provider instance
        
        Args:
            name: Provider name (optional if config has provider_type)
            config: Provider configuration
            **kwargs: Additional configuration parameters
            
        Returns:
            Configured provider instance
        """
        # Determine provider name
        if not name and config:
            name = config.provider_type.value
        elif not name:
            raise ValueError("Either name or config with provider_type must be provided")
        
        # Check if provider is registered
        if name not in cls._providers:
            # Try to auto-load provider
            cls._auto_load_provider(name)
            
            if name not in cls._providers:
                available = cls.list_providers()
                raise ValueError(
                    f"Unknown provider: {name}. Available providers: {available}"
                )
        
        # Create configuration if not provided
        if not config:
            provider_type = ProviderType(name) if name in [p.value for p in ProviderType] else ProviderType.CUSTOM
            config = ProviderConfig(provider_type=provider_type, **kwargs)
        
        # Create cache key for singleton pattern
        cache_key = f"{name}_{config.model}_{config.api_key[:8] if config.api_key else 'nokey'}"
        
        # Return cached instance if available
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Create new instance
        provider_class = cls._providers[name]
        instance = provider_class(config)
        
        # Cache instance
        cls._instances[cache_key] = instance
        
        return instance
    
    @classmethod
    def _auto_load_provider(cls, name: str) -> None:
        """Attempt to auto-load a provider module"""
        # Common provider module names
        module_names = [
            f"src.analysis.providers.{name}_unified",
            f"src.analysis.providers.{name}",
            f"src.analysis.{name}_provider",
            f"{name}_provider",
        ]
        
        for module_name in module_names:
            try:
                importlib.import_module(module_name)
                # If module loaded successfully and provider registered, we're done
                if name in cls._providers:
                    return
            except ImportError:
                continue
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List all registered providers"""
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_info(cls, name: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")
        
        provider_class = cls._providers[name]
        info = {
            "name": name,
            "class": provider_class.__name__,
            "module": provider_class.__module__,
        }
        
        if hasattr(provider_class, 'provider_type'):
            info["provider_type"] = provider_class.provider_type.value if provider_class.provider_type else None
        
        if hasattr(provider_class, 'supported_models'):
            info["supported_models"] = provider_class.supported_models
        
        return info
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached provider instances"""
        cls._instances.clear()
    
    @classmethod
    def auto_discover_providers(cls, directory: str = None) -> int:
        """Auto-discover and register all providers in a directory
        
        Args:
            directory: Directory to scan for providers (default: src/analysis)
            
        Returns:
            Number of providers discovered and registered
        """
        if directory is None:
            directory = Path(__file__).parent
        else:
            directory = Path(directory)
        
        count = 0
        
        # Also check providers subdirectory
        for search_dir in [directory, directory / "providers"]:
            if not search_dir.exists():
                continue
                
            # Find all Python files that might contain providers
            for file_path in search_dir.glob("*provider*.py"):
                if file_path.name.startswith("_") or file_path.name == "provider_factory.py":
                    continue
                
                try:
                    # Import the module
                    module_name = file_path.stem
                    spec = importlib.util.spec_from_file_location(
                        f"src.analysis.{module_name}", 
                        file_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Find all BaseProvider subclasses
                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, BaseProvider) and 
                                obj != BaseProvider):
                                
                                # Auto-register if not already registered
                                provider_name = None
                                if hasattr(obj, 'provider_type') and obj.provider_type:
                                    provider_name = obj.provider_type.value
                                else:
                                    provider_name = name.lower().replace('provider', '')
                                
                                if provider_name and provider_name not in cls._providers:
                                    cls._providers[provider_name] = obj
                                    count += 1
                                    logger.info(f"Auto-discovered provider: {provider_name}")
                            
                except Exception as e:
                    logger.warning(f"Failed to load provider from {file_path}: {e}")
        
        return count


# Legacy support - create LLMProviderFactory alias
LLMProviderFactory = ProviderFactory

# Legacy function for backward compatibility
def register_provider(name: str):
    """Legacy decorator for registering providers"""
    return ProviderFactory.register_provider(name)

# Convenience functions
def create_provider(name: str = None, **kwargs) -> BaseProvider:
    """Create a provider instance"""
    return ProviderFactory.create_provider(name, **kwargs)


def list_providers() -> List[str]:
    """List all available providers"""
    return ProviderFactory.list_providers()


def get_provider_from_env(provider_type: ProviderType, model: str = None) -> BaseProvider:
    """Create a provider using environment variables"""
    config = ProviderConfig.from_env(provider_type, model)
    return ProviderFactory.create_provider(config=config)


# Backward compatibility - old function name
def get_provider(name: str, config: Any = None, **kwargs):
    """Legacy function to get a provider"""
    if config and hasattr(config, '__dict__'):
        # Convert old config to new format
        provider_config = ProviderConfig(
            provider_type=ProviderType(name) if name in [p.value for p in ProviderType] else ProviderType.CUSTOM,
            api_key=getattr(config, 'api_key', kwargs.get('api_key', '')),
            model=getattr(config, 'model', kwargs.get('model', 'default')),
            max_tokens=getattr(config, 'max_tokens', 1000),
            temperature=getattr(config, 'temperature', 0.1),
            timeout=getattr(config, 'timeout', 30),
            max_retries=getattr(config, 'max_retries', 3),
            rate_limit_rpm=getattr(config, 'rate_limit_rpm', 60)
        )
        return ProviderFactory.create_provider(name=name, config=provider_config)
    else:
        return ProviderFactory.create_provider(name=name, **kwargs)