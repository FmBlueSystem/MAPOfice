"""Provider factory for managing and creating LLM provider instances.

This module implements the factory pattern for LLM providers, allowing
dynamic registration and instantiation of different provider implementations.
"""

import os
import importlib
import logging
from typing import Dict, Any, Type, Optional, List
from functools import wraps

from .base_provider import BaseLLMProvider, ProviderConfig

logger = logging.getLogger(__name__)


def register_provider(name: str):
    """Decorator for auto-registering providers with the factory.
    
    Args:
        name: The name to register the provider under
    
    Returns:
        Decorator function
    """
    def decorator(cls):
        LLMProviderFactory.register_provider(name, cls)
        return cls
    return decorator


class LLMProviderFactory:
    """Factory class for creating and managing LLM provider instances.
    
    This class implements the factory pattern, allowing dynamic registration
    and instantiation of different LLM provider implementations.
    """
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {}
    _instances: Dict[str, BaseLLMProvider] = {}
    _default_configs: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider], 
                         default_config: Optional[Dict[str, Any]] = None):
        """Register a new provider with the factory.
        
        Args:
            name: Name to register the provider under
            provider_class: The provider class (must inherit from BaseLLMProvider)
            default_config: Optional default configuration for the provider
        
        Raises:
            ValueError: If provider doesn't inherit from BaseLLMProvider
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError(f"Provider {provider_class.__name__} must inherit from BaseLLMProvider")
        
        cls._providers[name.lower()] = provider_class
        if default_config:
            cls._default_configs[name.lower()] = default_config
        
        logger.info(f"Registered provider: {name} -> {provider_class.__name__}")
    
    @classmethod
    def create_provider(cls, name: str, config: Optional[Dict[str, Any]] = None, 
                       use_singleton: bool = True, **kwargs) -> BaseLLMProvider:
        """Create or retrieve a provider instance.
        
        Args:
            name: Name of the provider to create
            config: Optional configuration dictionary
            use_singleton: If True, reuse existing instances
            **kwargs: Additional configuration parameters
        
        Returns:
            Provider instance
        
        Raises:
            ValueError: If provider name is not registered
        """
        name = name.lower()
        
        if name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(f"Unknown provider: {name}. Available: {available}")
        
        # Check for singleton instance
        if use_singleton and name in cls._instances:
            logger.debug(f"Returning cached instance for provider: {name}")
            return cls._instances[name]
        
        # Merge configurations
        final_config = {}
        
        # Start with default config
        if name in cls._default_configs:
            final_config.update(cls._default_configs[name])
        
        # Apply provided config
        if config:
            final_config.update(config)
        
        # Apply kwargs
        final_config.update(kwargs)
        
        # Handle API key from environment
        if 'api_key_env' in final_config and not final_config.get('api_key'):
            env_var = final_config['api_key_env']
            api_key = os.getenv(env_var)
            if api_key:
                final_config['api_key'] = api_key
                logger.debug(f"Loaded API key from environment: {env_var}")
        
        # Create instance
        provider_class = cls._providers[name]
        instance = provider_class(final_config)
        
        # Cache if singleton
        if use_singleton:
            cls._instances[name] = instance
            logger.info(f"Created and cached new instance for provider: {name}")
        else:
            logger.info(f"Created new instance for provider: {name}")
        
        return instance
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """Get list of registered provider names.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_class(cls, name: str) -> Type[BaseLLMProvider]:
        """Get the provider class for a given name.
        
        Args:
            name: Provider name
        
        Returns:
            Provider class
        
        Raises:
            ValueError: If provider not found
        """
        name = name.lower()
        if name not in cls._providers:
            raise ValueError(f"Provider not found: {name}")
        return cls._providers[name]
    
    @classmethod
    def clear_instances(cls):
        """Clear all cached provider instances."""
        cls._instances.clear()
        logger.info("Cleared all cached provider instances")
    
    @classmethod
    def remove_provider(cls, name: str):
        """Remove a provider from the registry.
        
        Args:
            name: Provider name to remove
        """
        name = name.lower()
        if name in cls._providers:
            del cls._providers[name]
            
        if name in cls._instances:
            del cls._instances[name]
            
        if name in cls._default_configs:
            del cls._default_configs[name]
        
        logger.info(f"Removed provider: {name}")
    
    @classmethod
    def auto_discover_providers(cls, package_path: str = "src.analysis.providers"):
        """Auto-discover and register providers from a package.
        
        Args:
            package_path: Python package path to scan for providers
        """
        try:
            package = importlib.import_module(package_path)
            package_dir = os.path.dirname(package.__file__)
            
            for filename in os.listdir(package_dir):
                if filename.endswith('_provider.py') and not filename.startswith('_'):
                    module_name = filename[:-3]
                    try:
                        module = importlib.import_module(f"{package_path}.{module_name}")
                        logger.debug(f"Discovered provider module: {module_name}")
                    except ImportError as e:
                        logger.warning(f"Failed to import provider module {module_name}: {e}")
        except (ImportError, AttributeError, OSError) as e:
            logger.warning(f"Failed to auto-discover providers from {package_path}: {e}")
    
    @classmethod
    def test_all_providers(cls) -> Dict[str, bool]:
        """Test connection for all registered providers.
        
        Returns:
            Dictionary mapping provider names to connection status
        """
        results = {}
        for name in cls._providers:
            try:
                provider = cls.create_provider(name)
                results[name] = provider.test_connection()
            except Exception as e:
                logger.error(f"Failed to test provider {name}: {e}")
                results[name] = False
        return results
    
    @classmethod
    def get_provider_info(cls, name: str) -> Dict[str, Any]:
        """Get information about a specific provider.
        
        Args:
            name: Provider name
        
        Returns:
            Provider information dictionary
        """
        name = name.lower()
        if name not in cls._providers:
            raise ValueError(f"Provider not found: {name}")
        
        try:
            provider = cls.create_provider(name)
            return provider.get_provider_info()
        except Exception as e:
            logger.error(f"Failed to get info for provider {name}: {e}")
            return {
                'name': name,
                'error': str(e),
                'available': False
            }


# Convenience function for getting providers
def get_provider(name: str, config: Optional[Dict[str, Any]] = None, **kwargs) -> BaseLLMProvider:
    """Convenience function to get a provider instance.
    
    Args:
        name: Provider name
        config: Optional configuration
        **kwargs: Additional configuration parameters
    
    Returns:
        Provider instance
    """
    return LLMProviderFactory.create_provider(name, config, **kwargs)