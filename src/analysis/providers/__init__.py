"""Unified LLM Providers Module

This module consolidates all LLM provider implementations using the factory pattern.
All providers are auto-registered and available through the ProviderFactory.
"""

# Import all unified providers to trigger auto-registration
# Use try-except to handle missing dependencies gracefully
try:
    from .zai_unified import UnifiedZaiProvider
except ImportError as e:
    import logging
    logging.debug(f"Could not import ZAI provider: {e}")
    UnifiedZaiProvider = None

try:
    from .claude_unified import UnifiedClaudeProvider
except ImportError as e:
    import logging
    logging.debug(f"Could not import Claude provider: {e}")
    UnifiedClaudeProvider = None

try:
    from .openai_unified import UnifiedOpenAIProvider
except ImportError as e:
    import logging
    logging.debug(f"Could not import OpenAI provider: {e}")
    UnifiedOpenAIProvider = None

try:
    from .gemini_unified import UnifiedGeminiProvider
except ImportError as e:
    import logging
    logging.debug(f"Could not import Gemini provider: {e}")
    UnifiedGeminiProvider = None

# Export key components for easy access
__all__ = []
if UnifiedZaiProvider:
    __all__.append('UnifiedZaiProvider')
if UnifiedClaudeProvider:
    __all__.append('UnifiedClaudeProvider')
if UnifiedOpenAIProvider:
    __all__.append('UnifiedOpenAIProvider')
if UnifiedGeminiProvider:
    __all__.append('UnifiedGeminiProvider')

# Provider information
PROVIDER_INFO = {
    "zai": {
        "name": "Z.ai",
        "models": ["glm-4.5", "glm-4.5-flash", "glm-4.5v"],
        "recommended": "glm-4.5-flash",  # FREE
        "env_key": "ZAI_API_KEY"
    },
    "claude": {
        "name": "Anthropic Claude",
        "models": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"],
        "recommended": "claude-3-haiku-20240307",
        "env_key": "ANTHROPIC_API_KEY"
    },
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "recommended": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY"
    },
    "gemini": {
        "name": "Google Gemini",
        "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "recommended": "gemini-1.5-flash",
        "env_key": "GEMINI_API_KEY"
    }
}