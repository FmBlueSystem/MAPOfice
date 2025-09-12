"""Configuration management for MAP4.

This module handles loading and managing configuration from various sources.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration container for MAP4."""
    
    # CLI settings
    cli: Dict[str, Any] = field(default_factory=dict)
    
    # Provider configurations
    providers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Analysis settings
    analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Storage settings
    storage: Dict[str, Any] = field(default_factory=dict)
    
    # Playlist settings
    playlist: Dict[str, Any] = field(default_factory=dict)
    
    # BMAD settings
    bmad: Dict[str, Any] = field(default_factory=dict)
    
    # Logging settings
    logging: Dict[str, Any] = field(default_factory=dict)
    
    # Export settings
    export: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., 'cli.default_provider')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        parts = key.split('.')
        value = self.__dict__
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part, None)
            
            if value is None:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., 'cli.default_provider')
            value: Value to set
        """
        parts = key.split('.')
        target = self.__dict__
        
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        
        target[parts[-1]] = value
    
    def update(self, data: Dict[str, Any]):
        """Update configuration with dictionary data.
        
        Args:
            data: Configuration data dictionary
        """
        for key, value in data.items():
            if hasattr(self, key):
                if isinstance(value, dict) and isinstance(getattr(self, key), dict):
                    getattr(self, key).update(value)
                else:
                    setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return {
            'cli': self.cli,
            'providers': self.providers,
            'analysis': self.analysis,
            'storage': self.storage,
            'playlist': self.playlist,
            'bmad': self.bmad,
            'logging': self.logging,
            'export': self.export
        }


class ConfigLoader:
    """Configuration loader for MAP4."""
    
    DEFAULT_CONFIG_PATHS = [
        Path.home() / '.map4' / 'config.yaml',
        Path.home() / '.map4' / 'config.json',
        Path.cwd() / 'config' / 'default.yaml',
        Path.cwd() / 'config' / 'local.yaml',
        Path.cwd() / '.map4.yaml',
        Path.cwd() / '.map4.json'
    ]
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Config:
        """Load configuration from file or defaults.
        
        Args:
            config_path: Optional path to configuration file
        
        Returns:
            Loaded configuration
        """
        config = Config()
        
        # Load default configuration
        default_config = cls._load_default_config()
        if default_config:
            config.update(default_config)
        
        # Load from specified path
        if config_path:
            custom_config = cls._load_file(Path(config_path))
            if custom_config:
                config.update(custom_config)
                logger.info(f"Loaded configuration from: {config_path}")
        else:
            # Try to find configuration file
            for path in cls.DEFAULT_CONFIG_PATHS:
                if path.exists():
                    custom_config = cls._load_file(path)
                    if custom_config:
                        config.update(custom_config)
                        logger.info(f"Loaded configuration from: {path}")
                        break
        
        # Apply environment variable overrides
        cls._apply_env_overrides(config)
        
        return config
    
    @classmethod
    def _load_default_config(cls) -> Optional[Dict[str, Any]]:
        """Load default configuration.
        
        Returns:
            Default configuration dictionary
        """
        default_path = Path(__file__).parent.parent / 'config' / 'default.yaml'
        
        if default_path.exists():
            return cls._load_file(default_path)
        
        # Fallback to hardcoded defaults
        return {
            'cli': {
                'default_provider': 'zai',
                'output_format': 'json',
                'verbose': False
            },
            'providers': {
                'zai': {
                    'api_key_env': 'ZAI_API_KEY',
                    'timeout': 30,
                    'batch_size': 10
                }
            },
            'analysis': {
                'batch_size': 10,
                'retry_attempts': 3,
                'cache_results': True
            },
            'storage': {
                'database_path': 'data/music.db',
                'backup_enabled': True
            }
        }
    
    @classmethod
    def _load_file(cls, path: Path) -> Optional[Dict[str, Any]]:
        """Load configuration from file.
        
        Args:
            path: Path to configuration file
        
        Returns:
            Configuration dictionary or None
        """
        try:
            with open(path, 'r') as f:
                if path.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif path.suffix == '.json':
                    return json.load(f)
                else:
                    # Try to detect format
                    content = f.read()
                    f.seek(0)
                    
                    if content.strip().startswith('{'):
                        return json.load(f)
                    else:
                        return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load configuration from {path}: {e}")
            return None
    
    @classmethod
    def _apply_env_overrides(cls, config: Config):
        """Apply environment variable overrides to configuration.
        
        Args:
            config: Configuration to update
        """
        # Provider API key overrides
        env_mappings = {
            'MAP4_ZAI_API_KEY': 'providers.zai.api_key',
            'MAP4_CLAUDE_API_KEY': 'providers.claude.api_key',
            'MAP4_GEMINI_API_KEY': 'providers.gemini.api_key',
            'MAP4_OPENAI_API_KEY': 'providers.openai.api_key',
            'MAP4_DEFAULT_PROVIDER': 'cli.default_provider',
            'MAP4_DATABASE_PATH': 'storage.database_path',
            'MAP4_LOG_LEVEL': 'logging.level',
            'MAP4_DEBUG': 'cli.debug'
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Convert boolean strings
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                
                config.set(config_key, value)
                logger.debug(f"Applied environment override: {env_var} -> {config_key}")
    
    @classmethod
    def save(cls, config: Config, path: str):
        """Save configuration to file.
        
        Args:
            config: Configuration to save
            path: Path to save configuration
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(config.to_dict(), f, default_flow_style=False)
            else:
                json.dump(config.to_dict(), f, indent=2)
        
        logger.info(f"Saved configuration to: {path}")


# Global configuration instance
_config: Optional[Config] = None


def get_config(reload: bool = False, config_path: Optional[str] = None) -> Config:
    """Get global configuration instance.
    
    Args:
        reload: Force reload configuration
        config_path: Optional path to configuration file
    
    Returns:
        Configuration instance
    """
    global _config
    
    if _config is None or reload:
        _config = ConfigLoader.load(config_path)
    
    return _config


def set_config(config: Config):
    """Set global configuration instance.
    
    Args:
        config: Configuration to set
    """
    global _config
    _config = config