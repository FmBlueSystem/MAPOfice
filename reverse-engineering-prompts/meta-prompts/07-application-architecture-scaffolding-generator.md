# Application Architecture Scaffolding Generator Meta-Prompt

## Overview
This meta-prompt generates comprehensive reproduction prompts for creating scalable application architectures with repository patterns, service layers, dependency injection, configuration systems, and enterprise-grade patterns. Based on MAP4's robust architectural foundation.

## Meta-Prompt Template

### Architecture Configuration Parameters
Configure your application architecture scaffolding:

```yaml
# Application Architecture Configuration
ARCHITECTURE_CONFIG:
  application_name: "{APP_NAME}"                  # e.g., "Enterprise Analyzer", "Data Platform"
  architecture_pattern: "{ARCHITECTURE_PATTERN}" # "MVC", "LAYERED", "HEXAGONAL", "MICROSERVICES", "CLEAN"
  complexity_level: "{COMPLEXITY}"                # "BASIC", "INTERMEDIATE", "ADVANCED", "ENTERPRISE"
  domain_type: "{DOMAIN_TYPE}"                   # "BUSINESS", "SCIENTIFIC", "EDUCATIONAL", "ENTERPRISE"

CORE_PATTERNS:
  repository_pattern: {REPOSITORY_PATTERN}       # true/false
  service_layer: {SERVICE_LAYER}                 # true/false
  dependency_injection: {DEPENDENCY_INJECTION}   # true/false
  factory_pattern: {FACTORY_PATTERN}             # true/false
  observer_pattern: {OBSERVER_PATTERN}           # true/false
  strategy_pattern: {STRATEGY_PATTERN}           # true/false
  command_pattern: {COMMAND_PATTERN}             # true/false

DATA_ACCESS:
  orm_integration: {ORM_INTEGRATION}             # true/false
  database_migrations: {DATABASE_MIGRATIONS}     # true/false
  connection_pooling: {CONNECTION_POOLING}       # true/false
  transaction_management: {TRANSACTION_MGMT}     # true/false
  caching_layer: {CACHING_LAYER}                # true/false

CONFIGURATION:
  hierarchical_config: {HIERARCHICAL_CONFIG}     # true/false
  environment_support: {ENVIRONMENT_SUPPORT}     # true/false
  hot_reload: {HOT_RELOAD}                       # true/false
  validation: {CONFIG_VALIDATION}                # true/false
  encryption: {CONFIG_ENCRYPTION}                # true/false

LOGGING_OBSERVABILITY:
  structured_logging: {STRUCTURED_LOGGING}       # true/false
  log_aggregation: {LOG_AGGREGATION}             # true/false
  metrics_collection: {METRICS_COLLECTION}       # true/false
  health_checks: {HEALTH_CHECKS}                # true/false
  distributed_tracing: {DISTRIBUTED_TRACING}     # true/false

SCALABILITY:
  async_processing: {ASYNC_PROCESSING}           # true/false
  message_queues: {MESSAGE_QUEUES}               # true/false
  load_balancing: {LOAD_BALANCING}               # true/false
  horizontal_scaling: {HORIZONTAL_SCALING}       # true/false
  performance_monitoring: {PERF_MONITORING}      # true/false

SECURITY:
  authentication: {AUTHENTICATION}               # true/false
  authorization: {AUTHORIZATION}                 # true/false
  input_validation: {INPUT_VALIDATION}           # true/false
  rate_limiting: {RATE_LIMITING}                # true/false
  audit_logging: {AUDIT_LOGGING}                # true/false

TESTING:
  unit_testing: {UNIT_TESTING}                  # true/false
  integration_testing: {INTEGRATION_TESTING}     # true/false
  mocking_framework: {MOCKING_FRAMEWORK}         # true/false
  test_fixtures: {TEST_FIXTURES}                # true/false
  coverage_reporting: {COVERAGE_REPORTING}       # true/false

DEPLOYMENT:
  containerization: {CONTAINERIZATION}           # true/false
  orchestration: {ORCHESTRATION}                # true/false
  ci_cd_pipeline: {CI_CD_PIPELINE}              # true/false
  infrastructure_as_code: {INFRASTRUCTURE_CODE}  # true/false
```

## Generated Application Architecture Template

Based on the configuration, this meta-prompt generates:

---

# {APP_NAME} - Scalable Application Architecture

## Architecture Overview
Create a {COMPLEXITY}-level application architecture following {ARCHITECTURE_PATTERN} pattern for {DOMAIN_TYPE} applications with enterprise-grade patterns, scalability, and maintainability.

### Architectural Principles
- **Separation of Concerns**: Clear layer boundaries and responsibilities
- **Dependency Inversion**: High-level modules independent of low-level details
- **Single Responsibility**: Each component has one reason to change
- **Open/Closed Principle**: Open for extension, closed for modification
- **Interface Segregation**: Clients depend only on interfaces they use

## Core Architecture Implementation

### 1. Foundation Layer - Dependency Injection Container
Core dependency injection system for managing application dependencies:

```python
"""
{APP_NAME} - Dependency Injection Container
Enterprise-grade dependency management system
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar, Generic, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
import threading
import inspect
import logging
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ServiceLifetime(Enum):
    """Service lifetime options."""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

@dataclass
class ServiceDescriptor:
    """Describes how a service should be created and managed."""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    dependencies: List[Type] = field(default_factory=list)

class ServiceContainer:
    """Dependency injection container."""
    
    def __init__(self):
        """Initialize service container."""
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}  # Singleton instances
        self._scoped_instances: Dict[int, Dict[Type, Any]] = {}  # Scoped instances per context
        self._lock = threading.RLock()
        
        # Register container itself
        self.register_singleton(ServiceContainer, instance=self)
    
    def register_transient(self, service_type: Type, implementation_type: Type = None, factory: Callable = None):
        """Register a transient service (new instance each time)."""
        with self._lock:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                implementation_type=implementation_type or service_type,
                factory=factory,
                lifetime=ServiceLifetime.TRANSIENT
            )
        logger.debug(f"Registered transient service: {service_type.__name__}")
    
    def register_singleton(self, service_type: Type, implementation_type: Type = None, 
                          factory: Callable = None, instance: Any = None):
        """Register a singleton service (same instance always returned)."""
        with self._lock:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                implementation_type=implementation_type or service_type,
                factory=factory,
                instance=instance,
                lifetime=ServiceLifetime.SINGLETON
            )
        logger.debug(f"Registered singleton service: {service_type.__name__}")
    
    def register_scoped(self, service_type: Type, implementation_type: Type = None, factory: Callable = None):
        """Register a scoped service (same instance per scope)."""
        with self._lock:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                implementation_type=implementation_type or service_type,
                factory=factory,
                lifetime=ServiceLifetime.SCOPED
            )
        logger.debug(f"Registered scoped service: {service_type.__name__}")
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve service instance."""
        with self._lock:
            return self._resolve_internal(service_type)
    
    def _resolve_internal(self, service_type: Type[T]) -> T:
        """Internal resolve method (assumes lock is held)."""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} not registered")
        
        descriptor = self._services[service_type]
        
        # Handle singleton
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if descriptor.instance is not None:
                return descriptor.instance
            
            if service_type in self._instances:
                return self._instances[service_type]
            
            instance = self._create_instance(descriptor)
            self._instances[service_type] = instance
            return instance
        
        # Handle scoped (simplified - using thread ID as scope)
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            scope_id = threading.get_ident()
            
            if scope_id not in self._scoped_instances:
                self._scoped_instances[scope_id] = {}
            
            if service_type in self._scoped_instances[scope_id]:
                return self._scoped_instances[scope_id][service_type]
            
            instance = self._create_instance(descriptor)
            self._scoped_instances[scope_id][service_type] = instance
            return instance
        
        # Handle transient
        else:
            return self._create_instance(descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor):
        """Create service instance using appropriate method."""
        if descriptor.factory:
            # Use factory function
            return self._invoke_factory(descriptor.factory)
        
        # Use constructor
        implementation_type = descriptor.implementation_type
        return self._create_via_constructor(implementation_type)
    
    def _invoke_factory(self, factory: Callable):
        """Invoke factory function with dependency injection."""
        sig = inspect.signature(factory)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                dependency = self._resolve_internal(param.annotation)
                kwargs[param_name] = dependency
        
        return factory(**kwargs)
    
    def _create_via_constructor(self, implementation_type: Type):
        """Create instance via constructor with dependency injection."""
        try:
            sig = inspect.signature(implementation_type.__init__)
            kwargs = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    # Resolve dependency
                    dependency = self._resolve_internal(param.annotation)
                    kwargs[param_name] = dependency
            
            return implementation_type(**kwargs)
            
        except Exception as e:
            logger.error(f"Failed to create instance of {implementation_type.__name__}: {e}")
            raise
    
    def create_scope(self):
        """Create a new dependency scope."""
        return ServiceScope(self)

class ServiceScope:
    """Represents a dependency resolution scope."""
    
    def __init__(self, container: ServiceContainer):
        """Initialize service scope."""
        self.container = container
        self.scope_id = threading.get_ident()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up scoped instances."""
        with self.container._lock:
            if self.scope_id in self.container._scoped_instances:
                del self.container._scoped_instances[self.scope_id]

# Dependency injection decorators
def inject(service_container: ServiceContainer):
    """Decorator for automatic dependency injection."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            injected_kwargs = {}
            
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty and param_name not in kwargs:
                    # Resolve dependency
                    dependency = service_container.resolve(param.annotation)
                    injected_kwargs[param_name] = dependency
            
            return func(*args, **kwargs, **injected_kwargs)
        
        return wrapper
    return decorator

# Global service container instance
service_container = ServiceContainer()
```

### 2. Configuration Management System
Hierarchical configuration with validation and environment support:

```python
"""
{APP_NAME} - Configuration Management System
Enterprise configuration with validation and hot-reload
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Type, Union, List
from dataclasses import dataclass, fields
from abc import ABC, abstractmethod
import logging
{#if CONFIG_VALIDATION}
from marshmallow import Schema, fields as ma_fields, ValidationError, post_load
{/if}
{#if CONFIG_ENCRYPTION}
from cryptography.fernet import Fernet
import base64
{/fi}
{#if HOT_RELOAD}
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
{/fi}

logger = logging.getLogger(__name__)

{#if CONFIG_VALIDATION}
class ConfigurationSchema(Schema):
    """Base configuration schema for validation."""
    
    class Meta:
        unknown = 'EXCLUDE'  # Ignore unknown fields
    
    @post_load
    def create_config(self, data, **kwargs):
        """Post-process configuration data."""
        return data
{/fi}

@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "app_db"
    username: str = "user"
    password: str = ""
    max_connections: int = 10
    ssl_mode: str = "prefer"

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_output: bool = True
    console_output: bool = True
    max_file_size: str = "10MB"
    backup_count: int = 5

@dataclass
class SecurityConfig:
    """Security configuration."""
    {#if AUTHENTICATION}
    jwt_secret: str = ""
    jwt_expiration: int = 3600
    {/fi}
    {#if RATE_LIMITING}
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    {/fi}
    {#if INPUT_VALIDATION}
    max_request_size: str = "10MB"
    allowed_origins: List[str] = None
    {/fi}

@dataclass
class ApplicationConfig:
    """Main application configuration."""
    name: str = "{APP_NAME}"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Nested configurations
    database: DatabaseConfig = None
    logging: LoggingConfig = None
    security: SecurityConfig = None
    
    def __post_init__(self):
        """Initialize nested configurations."""
        if self.database is None:
            self.database = DatabaseConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.security is None:
            self.security = SecurityConfig()

class ConfigurationProvider(ABC):
    """Abstract base for configuration providers."""
    
    @abstractmethod
    def load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from source."""
        pass
    
    @abstractmethod
    def save_config(self, path: str, config: Dict[str, Any]):
        """Save configuration to source."""
        pass

class JsonConfigurationProvider(ConfigurationProvider):
    """JSON configuration provider."""
    
    def load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = Path(path)
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON config from {path}: {e}")
            return {}
    
    def save_config(self, path: str, config: Dict[str, Any]):
        """Save configuration to JSON file."""
        try:
            config_path = Path(path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save JSON config to {path}: {e}")
            raise

class YamlConfigurationProvider(ConfigurationProvider):
    """YAML configuration provider."""
    
    def load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_path = Path(path)
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML config from {path}: {e}")
            return {}
    
    def save_config(self, path: str, config: Dict[str, Any]):
        """Save configuration to YAML file."""
        try:
            config_path = Path(path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save YAML config to {path}: {e}")
            raise

{#if CONFIG_ENCRYPTION}
class EncryptedConfigurationProvider(ConfigurationProvider):
    """Encrypted configuration provider."""
    
    def __init__(self, inner_provider: ConfigurationProvider, encryption_key: str = None):
        """Initialize encrypted provider."""
        self.inner_provider = inner_provider
        
        if encryption_key:
            self.fernet = Fernet(encryption_key.encode())
        else:
            # Generate key from environment or create new
            key = os.environ.get('CONFIG_ENCRYPTION_KEY')
            if not key:
                key = Fernet.generate_key().decode()
                logger.warning(f"Generated new encryption key: {key}")
            self.fernet = Fernet(key.encode())
    
    def load_config(self, path: str) -> Dict[str, Any]:
        """Load and decrypt configuration."""
        encrypted_config = self.inner_provider.load_config(path)
        if not encrypted_config:
            return {}
        
        try:
            # Decrypt sensitive fields
            return self._decrypt_config(encrypted_config)
        except Exception as e:
            logger.error(f"Failed to decrypt config: {e}")
            return {}
    
    def save_config(self, path: str, config: Dict[str, Any]):
        """Encrypt and save configuration."""
        encrypted_config = self._encrypt_config(config.copy())
        self.inner_provider.save_config(path, encrypted_config)
    
    def _encrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive configuration values."""
        sensitive_fields = ['password', 'secret', 'key', 'token']
        
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = self._encrypt_config(value)
            elif isinstance(value, str) and any(field in key.lower() for field in sensitive_fields):
                encrypted = self.fernet.encrypt(value.encode())
                config[key] = base64.b64encode(encrypted).decode()
        
        return config
    
    def _decrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive configuration values."""
        sensitive_fields = ['password', 'secret', 'key', 'token']
        
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = self._decrypt_config(value)
            elif isinstance(value, str) and any(field in key.lower() for field in sensitive_fields):
                try:
                    encrypted_data = base64.b64decode(value.encode())
                    decrypted = self.fernet.decrypt(encrypted_data)
                    config[key] = decrypted.decode()
                except Exception:
                    # Value might not be encrypted, keep as-is
                    pass
        
        return config
{/fi}

{#if HOT_RELOAD}
class ConfigurationWatcher(FileSystemEventHandler):
    """File system watcher for configuration changes."""
    
    def __init__(self, config_manager: "ConfigurationManager"):
        """Initialize configuration watcher."""
        self.config_manager = config_manager
        self.last_reload = time.time()
        self.reload_delay = 1.0  # Seconds to wait before reloading
    
    def on_modified(self, event):
        """Handle file modification event."""
        if not event.is_directory and event.src_path in self.config_manager.config_files:
            # Debounce rapid file changes
            now = time.time()
            if now - self.last_reload > self.reload_delay:
                logger.info(f"Configuration file changed: {event.src_path}")
                self.config_manager.reload_configuration()
                self.last_reload = now
{/fi}

class ConfigurationManager:
    """Comprehensive configuration management system."""
    
    def __init__(self, 
                 config_files: List[str] = None,
                 environment: str = None,
                 provider: ConfigurationProvider = None):
        """Initialize configuration manager."""
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config_files = config_files or self._get_default_config_files()
        self.provider = provider or self._create_default_provider()
        
        self._config_data: Dict[str, Any] = {}
        self._config_object: ApplicationConfig = ApplicationConfig()
        self._change_callbacks: List[Callable] = []
        
        {#if HOT_RELOAD}
        self._observer = None
        self._watcher = None
        {/fi}
        
        self.load_configuration()
        
        {#if HOT_RELOAD}
        if self.get('hot_reload', True):
            self._setup_hot_reload()
        {/fi}
    
    def _get_default_config_files(self) -> List[str]:
        """Get default configuration file paths."""
        base_files = [
            "config/config.yaml",
            f"config/config.{self.environment}.yaml"
        ]
        
        # Add environment-specific overrides
        env_file = os.environ.get('CONFIG_FILE')
        if env_file:
            base_files.append(env_file)
        
        return base_files
    
    def _create_default_provider(self) -> ConfigurationProvider:
        """Create default configuration provider."""
        base_provider = YamlConfigurationProvider()
        
        {#if CONFIG_ENCRYPTION}
        if os.environ.get('CONFIG_ENCRYPTION_ENABLED', 'false').lower() == 'true':
            return EncryptedConfigurationProvider(base_provider)
        {/fi}
        
        return base_provider
    
    def load_configuration(self):
        """Load configuration from all sources."""
        merged_config = {}
        
        # Load from files
        for config_file in self.config_files:
            file_config = self.provider.load_config(config_file)
            merged_config = self._merge_config(merged_config, file_config)
        
        # Override with environment variables
        env_config = self._load_from_environment()
        merged_config = self._merge_config(merged_config, env_config)
        
        self._config_data = merged_config
        
        {#if CONFIG_VALIDATION}
        # Validate configuration
        self._validate_configuration()
        {/fi}
        
        # Create typed configuration object
        self._create_config_object()
        
        logger.info("Configuration loaded successfully")
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        prefix = f"{APP_NAME.upper().replace(' ', '_')}_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Convert nested keys (e.g., DATABASE_HOST -> database.host)
                nested_keys = config_key.split('_')
                
                current = env_config
                for nested_key in nested_keys[:-1]:
                    if nested_key not in current:
                        current[nested_key] = {}
                    current = current[nested_key]
                
                # Try to parse value as JSON, fall back to string
                try:
                    current[nested_keys[-1]] = json.loads(value)
                except json.JSONDecodeError:
                    current[nested_keys[-1]] = value
        
        return env_config
    
    {#if CONFIG_VALIDATION}
    def _validate_configuration(self):
        """Validate configuration using schema."""
        try:
            schema = ConfigurationSchema()
            validated_data = schema.load(self._config_data)
            logger.info("Configuration validation passed")
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e.messages}")
            raise ValueError(f"Invalid configuration: {e.messages}")
    {/fi}
    
    def _create_config_object(self):
        """Create typed configuration object."""
        try:
            self._config_object = self._dict_to_dataclass(self._config_data, ApplicationConfig)
        except Exception as e:
            logger.error(f"Failed to create configuration object: {e}")
            self._config_object = ApplicationConfig()
    
    def _dict_to_dataclass(self, data: Dict[str, Any], dataclass_type: Type) -> Any:
        """Convert dictionary to dataclass instance."""
        if not data:
            return dataclass_type()
        
        # Get dataclass fields
        dataclass_fields = {f.name: f for f in fields(dataclass_type)}
        kwargs = {}
        
        for key, value in data.items():
            if key in dataclass_fields:
                field_info = dataclass_fields[key]
                
                # Handle nested dataclasses
                if hasattr(field_info.type, '__dataclass_fields__'):
                    kwargs[key] = self._dict_to_dataclass(value, field_info.type)
                else:
                    kwargs[key] = value
        
        return dataclass_type(**kwargs)
    
    {#if HOT_RELOAD}
    def _setup_hot_reload(self):
        """Setup hot reload monitoring."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            self._watcher = ConfigurationWatcher(self)
            self._observer = Observer()
            
            # Monitor configuration directories
            monitored_dirs = set()
            for config_file in self.config_files:
                config_path = Path(config_file)
                if config_path.exists():
                    dir_path = str(config_path.parent)
                    if dir_path not in monitored_dirs:
                        self._observer.schedule(self._watcher, dir_path, recursive=False)
                        monitored_dirs.add(dir_path)
            
            self._observer.start()
            logger.info("Hot reload monitoring started")
            
        except ImportError:
            logger.warning("Hot reload not available - install watchdog package")
        except Exception as e:
            logger.error(f"Failed to setup hot reload: {e}")
    {/fi}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        # Recreate config object
        self._create_config_object()
        
        # Notify change callbacks
        self._notify_change_callbacks(key, value)
    
    def get_config(self) -> ApplicationConfig:
        """Get typed configuration object."""
        return self._config_object
    
    def add_change_callback(self, callback: Callable[[str, Any], None]):
        """Add configuration change callback."""
        self._change_callbacks.append(callback)
    
    def _notify_change_callbacks(self, key: str, value: Any):
        """Notify all change callbacks."""
        for callback in self._change_callbacks:
            try:
                callback(key, value)
            except Exception as e:
                logger.error(f"Configuration change callback error: {e}")
    
    def reload_configuration(self):
        """Reload configuration from sources."""
        old_config = self._config_data.copy()
        self.load_configuration()
        
        # Notify about changes
        self._notify_configuration_reloaded(old_config, self._config_data)
    
    def _notify_configuration_reloaded(self, old_config: Dict, new_config: Dict):
        """Notify about configuration reload."""
        changes = self._find_config_changes(old_config, new_config)
        for key, (old_value, new_value) in changes.items():
            self._notify_change_callbacks(key, new_value)
    
    def _find_config_changes(self, old: Dict, new: Dict, prefix: str = "") -> Dict[str, tuple]:
        """Find differences between configuration dictionaries."""
        changes = {}
        
        all_keys = set(old.keys()) | set(new.keys())
        for key in all_keys:
            full_key = f"{prefix}.{key}" if prefix else key
            
            old_value = old.get(key)
            new_value = new.get(key)
            
            if old_value != new_value:
                if isinstance(old_value, dict) and isinstance(new_value, dict):
                    nested_changes = self._find_config_changes(old_value, new_value, full_key)
                    changes.update(nested_changes)
                else:
                    changes[full_key] = (old_value, new_value)
        
        return changes
    
    def save_configuration(self, config_file: str = None):
        """Save current configuration to file."""
        if not config_file:
            config_file = self.config_files[0]
        
        self.provider.save_config(config_file, self._config_data)
        logger.info(f"Configuration saved to {config_file}")
    
    def shutdown(self):
        """Shutdown configuration manager."""
        {#if HOT_RELOAD}
        if self._observer:
            self._observer.stop()
            self._observer.join()
        {/fi}
        
        logger.info("Configuration manager shut down")
```

### 3. Repository Pattern Implementation
Data access layer with repository pattern:

```python
"""
{APP_NAME} - Repository Pattern Implementation
Data access layer with repository and unit of work patterns
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any, Union
from dataclasses import dataclass
import logging
{#if ORM_INTEGRATION}
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
{/fi}
{#if CONNECTION_POOLING}
from sqlalchemy.pool import QueuePool
{/fi}
{#if DATABASE_MIGRATIONS}
from alembic.config import Config
from alembic import command
{/fi}
import threading
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')

{#if ORM_INTEGRATION}
# SQLAlchemy base
Base = declarative_base()

# Example entity models
class BaseEntity(Base):
    """Base entity with common fields."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ApplicationEntity(BaseEntity):
    """Example application entity."""
    __tablename__ = 'application_entities'
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    metadata = Column(Text)  # JSON data
{/fi}

class IRepository(ABC, Generic[T]):
    """Generic repository interface."""
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def find(self, **criteria) -> List[T]:
        """Find entities by criteria."""
        pass
    
    @abstractmethod
    def add(self, entity: T) -> T:
        """Add new entity."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def count(self, **criteria) -> int:
        """Count entities matching criteria."""
        pass

{#if ORM_INTEGRATION}
class SqlAlchemyRepository(IRepository[T], Generic[T]):
    """SQLAlchemy-based repository implementation."""
    
    def __init__(self, session: Session, entity_type: type):
        """Initialize repository."""
        self.session = session
        self.entity_type = entity_type
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        try:
            return self.session.query(self.entity_type).filter(
                self.entity_type.id == entity_id,
                self.entity_type.is_active == True
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting entity by ID {entity_id}: {e}")
            raise
    
    def get_all(self) -> List[T]:
        """Get all active entities."""
        try:
            return self.session.query(self.entity_type).filter(
                self.entity_type.is_active == True
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all entities: {e}")
            raise
    
    def find(self, **criteria) -> List[T]:
        """Find entities by criteria."""
        try:
            query = self.session.query(self.entity_type).filter(
                self.entity_type.is_active == True
            )
            
            for key, value in criteria.items():
                if hasattr(self.entity_type, key):
                    query = query.filter(getattr(self.entity_type, key) == value)
            
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding entities with criteria {criteria}: {e}")
            raise
    
    def add(self, entity: T) -> T:
        """Add new entity."""
        try:
            self.session.add(entity)
            return entity
        except SQLAlchemyError as e:
            logger.error(f"Error adding entity: {e}")
            self.session.rollback()
            raise
    
    def update(self, entity: T) -> T:
        """Update existing entity."""
        try:
            entity.updated_at = datetime.utcnow()
            self.session.merge(entity)
            return entity
        except SQLAlchemyError as e:
            logger.error(f"Error updating entity: {e}")
            self.session.rollback()
            raise
    
    def delete(self, entity_id: int) -> bool:
        """Soft delete entity by ID."""
        try:
            entity = self.get_by_id(entity_id)
            if entity:
                entity.is_active = False
                entity.updated_at = datetime.utcnow()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting entity {entity_id}: {e}")
            self.session.rollback()
            raise
    
    def count(self, **criteria) -> int:
        """Count entities matching criteria."""
        try:
            query = self.session.query(self.entity_type).filter(
                self.entity_type.is_active == True
            )
            
            for key, value in criteria.items():
                if hasattr(self.entity_type, key):
                    query = query.filter(getattr(self.entity_type, key) == value)
            
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting entities: {e}")
            raise
{/fi}

{#if TRANSACTION_MGMT}
class IUnitOfWork(ABC):
    """Unit of work interface for transaction management."""
    
    @abstractmethod
    def begin_transaction(self):
        """Begin a new transaction."""
        pass
    
    @abstractmethod
    def commit(self):
        """Commit current transaction."""
        pass
    
    @abstractmethod
    def rollback(self):
        """Rollback current transaction."""
        pass
    
    @abstractmethod
    def create_repository(self, entity_type: type) -> IRepository:
        """Create repository for entity type."""
        pass

{#if ORM_INTEGRATION}
class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy-based unit of work implementation."""
    
    def __init__(self, session_factory):
        """Initialize unit of work."""
        self.session_factory = session_factory
        self.session = None
        self.transaction = None
        self._repositories = {}
    
    def __enter__(self):
        """Enter unit of work context."""
        self.session = self.session_factory()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit unit of work context."""
        if exc_type is not None:
            self.rollback()
        else:
            try:
                self.commit()
            except Exception:
                self.rollback()
                raise
        finally:
            if self.session:
                self.session.close()
    
    def begin_transaction(self):
        """Begin a new transaction."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        self.transaction = self.session.begin()
    
    def commit(self):
        """Commit current transaction."""
        if self.session:
            self.session.commit()
    
    def rollback(self):
        """Rollback current transaction."""
        if self.session:
            self.session.rollback()
    
    def create_repository(self, entity_type: type) -> IRepository:
        """Create repository for entity type."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        repo_key = entity_type.__name__
        if repo_key not in self._repositories:
            self._repositories[repo_key] = SqlAlchemyRepository(self.session, entity_type)
        
        return self._repositories[repo_key]
{/fi}
{/fi}

class DatabaseManager:
    """Database connection and migration management."""
    
    def __init__(self, config: "ApplicationConfig"):
        """Initialize database manager."""
        self.config = config
        self.engine = None
        self.session_factory = None
        self._lock = threading.Lock()
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection."""
        try:
            db_config = self.config.database
            
            # Build connection string
            connection_string = self._build_connection_string(db_config)
            
            # Create engine
            engine_kwargs = {
                'echo': self.config.debug,
                {#if CONNECTION_POOLING}
                'poolclass': QueuePool,
                'pool_size': db_config.max_connections,
                'max_overflow': db_config.max_connections * 2,
                'pool_pre_ping': True,
                {/fi}
            }
            
            self.engine = create_engine(connection_string, **engine_kwargs)
            
            {#if ORM_INTEGRATION}
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(self.engine)
            {/fi}
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _build_connection_string(self, db_config: DatabaseConfig) -> str:
        """Build database connection string."""
        return (
            f"postgresql://{db_config.username}:{db_config.password}"
            f"@{db_config.host}:{db_config.port}/{db_config.database}"
            f"?sslmode={db_config.ssl_mode}"
        )
    
    {#if DATABASE_MIGRATIONS}
    def run_migrations(self, migration_dir: str = "migrations"):
        """Run database migrations."""
        try:
            alembic_cfg = Config()
            alembic_cfg.set_main_option("script_location", migration_dir)
            alembic_cfg.set_main_option("sqlalchemy.url", str(self.engine.url))
            
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed")
            
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            raise
    {/fi}
    
    @contextmanager
    def get_session(self):
        """Get database session."""
        {#if ORM_INTEGRATION}
        session = self.session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        {/if}
    
    {#if TRANSACTION_MGMT}
    def create_unit_of_work(self) -> IUnitOfWork:
        """Create unit of work instance."""
        {#if ORM_INTEGRATION}
        return SqlAlchemyUnitOfWork(self.session_factory)
        {/fi}
    {/fi}
    
    def health_check(self) -> bool:
        """Perform database health check."""
        try:
            {#if ORM_INTEGRATION}
            with self.get_session() as session:
                session.execute("SELECT 1")
            {/fi}
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def shutdown(self):
        """Shutdown database connections."""
        if self.engine:
            self.engine.dispose()
        logger.info("Database manager shut down")
```

## Service Layer Implementation
Business logic and application services:

```python
"""
{APP_NAME} - Service Layer Implementation
Business logic and application services
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Generic, TypeVar
from dataclasses import dataclass
import logging
{#if ASYNC_PROCESSING}
import asyncio
from concurrent.futures import ThreadPoolExecutor
{/fi}
{#if CACHING_LAYER}
from functools import lru_cache
import redis
{/fi}
{#if MESSAGE_QUEUES}
import pika
import json
{/fi}

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class ServiceResult(Generic[T]):
    """Standard service operation result."""
    success: bool
    data: Optional[T] = None
    message: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class IService(ABC):
    """Base service interface."""
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        pass

class BaseService(IService):
    """Base service implementation."""
    
    def __init__(self, 
                 repository_factory: Optional[Callable] = None,
                 config: Optional["ApplicationConfig"] = None):
        """Initialize base service."""
        self.repository_factory = repository_factory
        self.config = config
        {#if CACHING_LAYER}
        self._cache = {}
        {/fi}
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "service_name": self.__class__.__name__,
            "version": "1.0.0",
            "status": "active"
        }
    
    {#if CACHING_LAYER}
    def _get_from_cache(self, key: str) -> Any:
        """Get value from cache."""
        return self._cache.get(key)
    
    def _set_cache(self, key: str, value: Any, ttl: int = 300):
        """Set cache value with TTL."""
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is valid."""
        if key not in self._cache:
            return False
        return self._cache[key]['expires'] > time.time()
    {/fi}

{#if DOMAIN_TYPE == "BUSINESS"}
class BusinessService(BaseService):
    """Business logic service."""
    
    def __init__(self, 
                 entity_repository: IRepository,
                 unit_of_work: IUnitOfWork,
                 config: "ApplicationConfig"):
        """Initialize business service."""
        super().__init__(config=config)
        self.entity_repository = entity_repository
        self.unit_of_work = unit_of_work
    
    def create_entity(self, entity_data: Dict[str, Any]) -> ServiceResult:
        """Create new business entity."""
        try:
            with self.unit_of_work as uow:
                # Validate entity data
                validation_result = self._validate_entity_data(entity_data)
                if not validation_result.success:
                    return validation_result
                
                # Create entity
                entity = ApplicationEntity(
                    name=entity_data.get('name'),
                    description=entity_data.get('description'),
                    category=entity_data.get('category'),
                    metadata=json.dumps(entity_data.get('metadata', {}))
                )
                
                repository = uow.create_repository(ApplicationEntity)
                created_entity = repository.add(entity)
                uow.commit()
                
                logger.info(f"Created entity: {created_entity.id}")
                
                return ServiceResult(
                    success=True,
                    data=created_entity,
                    message="Entity created successfully"
                )
                
        except Exception as e:
            logger.error(f"Failed to create entity: {e}")
            return ServiceResult(
                success=False,
                error=str(e),
                message="Entity creation failed"
            )
    
    def get_entity(self, entity_id: int) -> ServiceResult:
        """Get entity by ID."""
        try:
            {#if CACHING_LAYER}
            cache_key = f"entity_{entity_id}"
            if self._is_cache_valid(cache_key):
                cached_entity = self._get_from_cache(cache_key)
                return ServiceResult(
                    success=True,
                    data=cached_entity['value'],
                    message="Entity retrieved from cache"
                )
            {/fi}
            
            entity = self.entity_repository.get_by_id(entity_id)
            
            if entity:
                {#if CACHING_LAYER}
                self._set_cache(cache_key, entity)
                {/fi}
                
                return ServiceResult(
                    success=True,
                    data=entity,
                    message="Entity retrieved successfully"
                )
            else:
                return ServiceResult(
                    success=False,
                    message="Entity not found"
                )
                
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            return ServiceResult(
                success=False,
                error=str(e),
                message="Entity retrieval failed"
            )
    
    def update_entity(self, entity_id: int, update_data: Dict[str, Any]) -> ServiceResult:
        """Update existing entity."""
        try:
            with self.unit_of_work as uow:
                repository = uow.create_repository(ApplicationEntity)
                entity = repository.get_by_id(entity_id)
                
                if not entity:
                    return ServiceResult(
                        success=False,
                        message="Entity not found"
                    )
                
                # Update entity fields
                for key, value in update_data.items():
                    if hasattr(entity, key) and key != 'id':
                        setattr(entity, key, value)
                
                updated_entity = repository.update(entity)
                uow.commit()
                
                {#if CACHING_LAYER}
                # Invalidate cache
                cache_key = f"entity_{entity_id}"
                if cache_key in self._cache:
                    del self._cache[cache_key]
                {/fi}
                
                return ServiceResult(
                    success=True,
                    data=updated_entity,
                    message="Entity updated successfully"
                )
                
        except Exception as e:
            logger.error(f"Failed to update entity {entity_id}: {e}")
            return ServiceResult(
                success=False,
                error=str(e),
                message="Entity update failed"
            )
    
    def _validate_entity_data(self, entity_data: Dict[str, Any]) -> ServiceResult:
        """Validate entity data."""
        if not entity_data.get('name'):
            return ServiceResult(
                success=False,
                message="Entity name is required"
            )
        
        if len(entity_data['name']) > 255:
            return ServiceResult(
                success=False,
                message="Entity name too long (max 255 characters)"
            )
        
        return ServiceResult(success=True)
{/fi}

{#if ASYNC_PROCESSING}
class AsyncProcessingService(BaseService):
    """Asynchronous processing service."""
    
    def __init__(self, config: "ApplicationConfig"):
        """Initialize async processing service."""
        super().__init__(config=config)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.processing_queue = asyncio.Queue()
    
    async def process_async(self, data: Any) -> ServiceResult:
        """Process data asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._process_data, 
                data
            )
            
            return ServiceResult(
                success=True,
                data=result,
                message="Async processing completed"
            )
            
        except Exception as e:
            logger.error(f"Async processing failed: {e}")
            return ServiceResult(
                success=False,
                error=str(e),
                message="Async processing failed"
            )
    
    def _process_data(self, data: Any) -> Any:
        """Process data synchronously."""
        # Simulate processing
        import time
        time.sleep(1)
        return f"processed_{data}"
    
    async def queue_processing_task(self, task_data: Any):
        """Queue a processing task."""
        await self.processing_queue.put(task_data)
    
    async def process_queue(self):
        """Process queued tasks."""
        while True:
            try:
                task_data = await self.processing_queue.get()
                result = await self.process_async(task_data)
                
                if result.success:
                    logger.info(f"Processed queued task: {result.data}")
                else:
                    logger.error(f"Queued task failed: {result.error}")
                
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
{/fi}

{#if MESSAGE_QUEUES}
class MessageQueueService(BaseService):
    """Message queue service for distributed processing."""
    
    def __init__(self, config: "ApplicationConfig"):
        """Initialize message queue service."""
        super().__init__(config=config)
        self.connection = None
        self.channel = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Setup RabbitMQ connection."""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue='processing_queue', durable=True)
            
            logger.info("Message queue connection established")
            
        except Exception as e:
            logger.error(f"Failed to setup message queue: {e}")
    
    def publish_message(self, queue: str, message: Dict[str, Any]) -> ServiceResult:
        """Publish message to queue."""
        try:
            if not self.channel:
                return ServiceResult(
                    success=False,
                    message="Message queue not connected"
                )
            
            self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)  # Persistent
            )
            
            return ServiceResult(
                success=True,
                message="Message published successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return ServiceResult(
                success=False,
                error=str(e),
                message="Message publishing failed"
            )
    
    def consume_messages(self, queue: str, callback: Callable):
        """Consume messages from queue."""
        try:
            if not self.channel:
                raise RuntimeError("Message queue not connected")
            
            def wrapper(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    callback(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Message processing error: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=wrapper
            )
            
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Failed to consume messages: {e}")
    
    def shutdown(self):
        """Shutdown message queue connections."""
        if self.connection:
            self.connection.close()
{/fi}

# Service registry for dependency injection
def register_services(container: ServiceContainer, config: "ApplicationConfig"):
    """Register all services with dependency injection container."""
    
    # Register configuration
    container.register_singleton(ApplicationConfig, instance=config)
    
    # Register database manager
    container.register_singleton(DatabaseManager, 
                                factory=lambda cfg: DatabaseManager(cfg))
    
    {#if DOMAIN_TYPE == "BUSINESS"}
    # Register business services
    container.register_scoped(BusinessService,
                             factory=lambda repo, uow, cfg: BusinessService(repo, uow, cfg))
    {/fi}
    
    {#if ASYNC_PROCESSING}
    # Register async services
    container.register_singleton(AsyncProcessingService,
                                factory=lambda cfg: AsyncProcessingService(cfg))
    {/fi}
    
    {#if MESSAGE_QUEUES}
    # Register message queue service
    container.register_singleton(MessageQueueService,
                                factory=lambda cfg: MessageQueueService(cfg))
    {/fi}
    
    logger.info("All services registered successfully")
```

## Project Structure

```
{APP_NAME.lower().replace(' ', '_')}/
├── src/
│   ├── __init__.py
│   ├── core/                          # Core architecture
│   │   ├── __init__.py
│   │   ├── container.py               # Dependency injection
│   │   ├── configuration.py           # Configuration management
│   │   └── exceptions.py              # Custom exceptions
│   ├── data/                          # Data access layer
│   │   ├── __init__.py
│   │   ├── repositories/              # Repository implementations
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py
│   │   │   └── entity_repository.py
│   │   ├── models/                    # Data models/entities
│   │   │   ├── __init__.py
│   │   │   ├── base_entity.py
│   │   │   └── application_entity.py
│   │   ├── migrations/                # Database migrations
│   │   └── database.py                # Database management
│   ├── services/                      # Business logic layer
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   ├── business_service.py
│   │   └── async_service.py
│   ├── interfaces/                    # Application interfaces
│   │   ├── __init__.py
│   │   ├── cli/                       # Command-line interface
│   │   └── api/                       # REST API interface
│   {#if CONTAINERIZATION}
│   ├── infrastructure/                # Infrastructure concerns
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── monitoring.py
│   │   └── messaging.py
│   {/if}
│   └── utils/                         # Shared utilities
│       ├── __init__.py
│       ├── helpers.py
│       └── validators.py
├── config/                            # Configuration files
│   ├── config.yaml
│   ├── config.development.yaml
│   ├── config.production.yaml
│   └── logging.yaml
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── unit/                          # Unit tests
│   ├── integration/                   # Integration tests
│   └── fixtures/                      # Test fixtures
{#if CONTAINERIZATION}
├── docker/                            # Docker configurations
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
{/fi}
{#if CI_CD_PIPELINE}
├── .github/                           # CI/CD workflows
│   └── workflows/
│       ├── test.yml
│       └── deploy.yml
{/fi}
├── scripts/                           # Utility scripts
│   ├── setup.sh
│   ├── migrate.sh
│   └── deploy.sh
├── requirements.txt
├── requirements-dev.txt
├── setup.py
└── README.md
```

## Dependencies

```txt
# Core dependencies
{#if ORM_INTEGRATION}
sqlalchemy>=2.0.0
alembic>=1.8.0
{/if}

{#if ASYNC_PROCESSING}
asyncio
concurrent.futures
{/if}

{#if MESSAGE_QUEUES}
pika>=1.3.0
{/fi}

{#if CACHING_LAYER}
redis>=4.0.0
{/fi}

{#if CONFIG_ENCRYPTION}
cryptography>=3.4.0
{/fi}

{#if HOT_RELOAD}
watchdog>=2.1.0
{/fi}

# Configuration and validation
pyyaml>=6.0
{#if CONFIG_VALIDATION}
marshmallow>=3.17.0
{/fi}

# Testing
{#if UNIT_TESTING}
pytest>=7.0.0
{/fi}
{#if MOCKING_FRAMEWORK}
pytest-mock>=3.6.0
{/fi}
{#if COVERAGE_REPORTING}
pytest-cov>=3.0.0
{/fi}

# Monitoring and logging
{#if STRUCTURED_LOGGING}
structlog>=22.1.0
{/fi}
{#if METRICS_COLLECTION}
prometheus-client>=0.14.0
{/fi}
```

## Usage Examples

### Basic Service Usage
```python
# Initialize container and register services
container = ServiceContainer()
config = ConfigurationManager().get_config()
register_services(container, config)

# Resolve and use service
business_service = container.resolve(BusinessService)
result = business_service.create_entity({"name": "Test Entity"})
```

### Repository Pattern
```python
# Use repository with unit of work
with database_manager.create_unit_of_work() as uow:
    repo = uow.create_repository(ApplicationEntity)
    entity = repo.get_by_id(1)
    entity.name = "Updated Name"
    repo.update(entity)
    uow.commit()
```

### Configuration Management
```python
# Load and use configuration
config_manager = ConfigurationManager()
app_config = config_manager.get_config()

# Access nested configuration
db_host = config_manager.get("database.host")

# React to configuration changes
config_manager.add_change_callback(
    lambda key, value: print(f"Config changed: {key} = {value}")
)
```

## Validation Criteria

A successful implementation should demonstrate:

1. **Clean Architecture**: Clear separation between layers
2. **Dependency Injection**: Proper IoC container usage
3. **Configuration Management**: Hierarchical, validated configuration
4. **Repository Pattern**: Clean data access abstraction
5. **Service Layer**: Well-organized business logic
6. **Error Handling**: Comprehensive error management
7. **Testing Support**: Mockable, testable architecture
8. **Scalability**: Support for horizontal scaling patterns

---

*Generated by Application Architecture Scaffolding Generator Meta-Prompt*  
*Version 1.0 - Based on MAP4 Enterprise Architecture Patterns*