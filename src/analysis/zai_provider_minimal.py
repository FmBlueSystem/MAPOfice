"""Backward Compatibility Shim for Minimal ZAI Provider

This module redirects to the unified ZAI provider.
"""

import warnings
from src.analysis.zai_provider import ZaiProvider

warnings.warn(
    "zai_provider_minimal.py is deprecated. Please use the new provider factory: "
    "from src.analysis.provider_factory import ProviderFactory",
    DeprecationWarning,
    stacklevel=2
)

# Alias to unified provider
MinimalZaiProvider = ZaiProvider