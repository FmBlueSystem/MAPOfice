# CLI-GUI Integration Pattern Generator Meta-Prompt

## Overview
This meta-prompt generates comprehensive reproduction prompts for creating unified CLI/GUI applications with shared business logic, Click framework integration, command structure patterns, and professional interface design. Based on MAP4's successful dual-interface architecture.

## Meta-Prompt Template

### CLI-GUI Integration Configuration Parameters
Configure your unified command-line and graphical interface application:

```yaml
# CLI-GUI Integration Configuration
APPLICATION_CONFIG:
  app_name: "{APP_NAME}"                          # e.g., "Media Analyzer", "Data Processor"
  app_type: "{APP_TYPE}"                          # "ANALYSIS", "PROCESSING", "MANAGEMENT", "DEVELOPMENT"
  complexity: "{COMPLEXITY}"                      # "BASIC", "INTERMEDIATE", "ADVANCED", "PROFESSIONAL"

CLI_FRAMEWORK:
  primary_framework: "{CLI_FRAMEWORK}"            # "click", "argparse", "typer", "fire"
  command_groups: {COMMAND_GROUPS}                # true/false - organized command structure
  interactive_mode: {INTERACTIVE_MODE}            # true/false - interactive CLI mode
  progress_bars: {CLI_PROGRESS_BARS}              # true/false - progress indicators
  colored_output: {COLORED_OUTPUT}                # true/false - colored terminal output
  config_files: {CONFIG_FILES}                   # true/false - configuration file support

GUI_FRAMEWORK:
  gui_framework: "{GUI_FRAMEWORK}"                # "PyQt6", "tkinter", "kivy", "web"
  shared_components: {SHARED_COMPONENTS}          # true/false - reusable UI components
  real_time_updates: {REAL_TIME_UPDATES}          # true/false - live data updates
  theme_system: {THEME_SYSTEM}                   # true/false - consistent theming

ARCHITECTURE:
  shared_business_logic: {SHARED_LOGIC}           # true/false - unified core logic
  service_layer: {SERVICE_LAYER}                 # true/false - service layer pattern
  plugin_architecture: {PLUGIN_ARCHITECTURE}     # true/false - extensible plugin system
  async_operations: {ASYNC_OPERATIONS}           # true/false - asynchronous processing

INTEGRATION_FEATURES:
  unified_configuration: {UNIFIED_CONFIG}         # true/false - shared configuration
  cross_interface_communication: {CROSS_COMM}    # true/false - interface communication
  shared_state_management: {SHARED_STATE}        # true/false - unified state handling
  common_data_formats: {COMMON_DATA_FORMATS}     # true/false - standardized data exchange

PROFESSIONAL_FEATURES:
  logging_system: {LOGGING_SYSTEM}               # true/false - comprehensive logging
  error_handling: {ERROR_HANDLING}               # true/false - robust error management
  testing_framework: {TESTING_FRAMEWORK}         # true/false - automated testing
  documentation: {DOCUMENTATION}                 # true/false - integrated documentation
  packaging: {PACKAGING}                         # true/false - distribution packaging
```

## Generated CLI-GUI Integration Template

Based on the configuration, this meta-prompt generates:

---

# {APP_NAME} - Unified CLI/GUI Application

## Application Overview
Create a {COMPLEXITY}-level application with unified command-line and graphical interfaces for {APP_TYPE} operations. Both interfaces share common business logic while providing optimal user experiences for their respective use cases.

### Key Features
{#if COMMAND_GROUPS}
- **Organized CLI Commands**: Grouped command structure with {CLI_FRAMEWORK}
{/if}
{#if INTERACTIVE_MODE}
- **Interactive Mode**: User-friendly interactive command-line interface
{/if}
{#if SHARED_LOGIC}
- **Unified Business Logic**: Single source of truth for all operations
{/if}
{#if REAL_TIME_UPDATES}
- **Real-time GUI Updates**: Live data synchronization in graphical interface
{/if}
{#if PLUGIN_ARCHITECTURE}
- **Plugin System**: Extensible architecture for additional functionality
{/if}

## Core Architecture Implementation

### 1. Shared Business Logic Layer
Foundation service layer that both CLI and GUI interfaces utilize:

```python
"""
{APP_NAME} - Shared Business Logic
Core services used by both CLI and GUI interfaces
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
import json
import yaml
import threading
import time
{#if ASYNC_OPERATIONS}
import asyncio
from concurrent.futures import ThreadPoolExecutor
{/if}
{#if LOGGING_SYSTEM}
import logging.handlers
{/if}

logger = logging.getLogger(__name__)

class OperationResult:
    """Standard result format for all operations."""
    
    def __init__(self, success: bool = True, data: Any = None, message: str = "", error: str = ""):
        self.success = success
        self.data = data
        self.message = message
        self.error = error
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationResult":
        """Create result from dictionary."""
        return cls(
            success=data.get("success", True),
            data=data.get("data"),
            message=data.get("message", ""),
            error=data.get("error", "")
        )

class OperationStatus(Enum):
    """Status of long-running operations."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProgressUpdate:
    """Progress update information."""
    current: int
    total: int
    message: str = ""
    percentage: float = field(init=False)
    
    def __post_init__(self):
        self.percentage = (self.current / self.total * 100) if self.total > 0 else 0

{#if UNIFIED_CONFIG}
class ConfigurationManager:
    """Unified configuration management for CLI and GUI."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_path = Path(config_path) if config_path else Path("config.yaml")
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    if self.config_path.suffix.lower() == '.json':
                        self.config = json.load(f)
                    else:
                        self.config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                self.config = self.get_default_config()
                self.save_config()
                logger.info("Created default configuration")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = self.get_default_config()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                if self.config_path.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2)
                else:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "application": {
                "name": "{APP_NAME}",
                "version": "1.0.0",
                "log_level": "INFO"
            },
            "interfaces": {
                "cli": {
                    "enabled": True,
                    {#if COLORED_OUTPUT}
                    "colored_output": True,
                    {/if}
                    {#if CLI_PROGRESS_BARS}
                    "progress_bars": True,
                    {/if}
                    {#if INTERACTIVE_MODE}
                    "interactive_mode": True
                    {/fi}
                },
                "gui": {
                    "enabled": True,
                    {#if THEME_SYSTEM}
                    "theme": "dark",
                    {/fi}
                    {#if REAL_TIME_UPDATES}
                    "real_time_updates": True
                    {/fi}
                }
            },
            {#if APP_TYPE == "ANALYSIS"}
            "analysis": {
                "default_output_format": "json",
                "batch_size": 10,
                "parallel_processing": True
            },
            {/if}
            {#if APP_TYPE == "PROCESSING"}
            "processing": {
                "max_workers": 4,
                "timeout": 30,
                "retry_attempts": 3
            },
            {/fi}
            {#if LOGGING_SYSTEM}
            "logging": {
                "level": "INFO",
                "file_output": True,
                "console_output": True,
                "max_file_size": "10MB",
                "backup_count": 5
            }
            {/fi}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
{/if}

{#if SHARED_STATE}
class StateManager:
    """Shared state management for CLI and GUI interfaces."""
    
    def __init__(self):
        """Initialize state manager."""
        self._state = {}
        self._listeners = []
        self._lock = threading.Lock()
    
    def get_state(self, key: str = None) -> Any:
        """Get state value or entire state."""
        with self._lock:
            if key is None:
                return self._state.copy()
            return self._state.get(key)
    
    def set_state(self, key: str, value: Any):
        """Set state value and notify listeners."""
        with self._lock:
            old_value = self._state.get(key)
            self._state[key] = value
            
        # Notify listeners outside of lock
        if old_value != value:
            self._notify_listeners(key, value, old_value)
    
    def update_state(self, updates: Dict[str, Any]):
        """Update multiple state values."""
        changes = {}
        with self._lock:
            for key, value in updates.items():
                old_value = self._state.get(key)
                if old_value != value:
                    self._state[key] = value
                    changes[key] = (value, old_value)
        
        # Notify listeners for all changes
        for key, (new_value, old_value) in changes.items():
            self._notify_listeners(key, new_value, old_value)
    
    def add_listener(self, callback: Callable[[str, Any, Any], None]):
        """Add state change listener."""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Remove state change listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, key: str, new_value: Any, old_value: Any):
        """Notify all listeners of state change."""
        for callback in self._listeners:
            try:
                callback(key, new_value, old_value)
            except Exception as e:
                logger.error(f"State listener error: {e}")
{/fi}

class BaseService(ABC):
    """Abstract base class for all services."""
    
    def __init__(self, config_manager: Optional["ConfigurationManager"] = None):
        """Initialize service."""
        self.config = config_manager
        {#if SHARED_STATE}
        self.state = StateManager()
        {/if}
        self._progress_callback = None
        
    def set_progress_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Set progress update callback."""
        self._progress_callback = callback
    
    def _update_progress(self, current: int, total: int, message: str = ""):
        """Update operation progress."""
        if self._progress_callback:
            update = ProgressUpdate(current=current, total=total, message=message)
            self._progress_callback(update)
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get service information."""
        pass

{#if APP_TYPE == "ANALYSIS"}
class AnalysisService(BaseService):
    """Core analysis service shared by CLI and GUI."""
    
    def __init__(self, config_manager: Optional["ConfigurationManager"] = None):
        """Initialize analysis service."""
        super().__init__(config_manager)
        self.analysis_history = []
        {#if ASYNC_OPERATIONS}
        self._executor = ThreadPoolExecutor(max_workers=4)
        {/fi}
    
    def analyze_single(self, input_data: Any, options: Dict[str, Any] = None) -> OperationResult:
        """Analyze single item."""
        try:
            options = options or {}
            
            # Simulate analysis process
            self._update_progress(0, 100, "Starting analysis...")
            
            # Perform analysis (placeholder implementation)
            result_data = {
                "input": str(input_data)[:100],  # Truncate for display
                "analysis_type": options.get("type", "default"),
                "confidence": 0.85,
                "categories": ["category_1", "category_2"],
                "metrics": {
                    "accuracy": 0.92,
                    "processing_time": 1.2
                }
            }
            
            self._update_progress(100, 100, "Analysis complete")
            
            # Store in history
            self.analysis_history.append(result_data)
            
            return OperationResult(
                success=True,
                data=result_data,
                message="Analysis completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return OperationResult(
                success=False,
                error=str(e),
                message="Analysis failed"
            )
    
    def analyze_batch(self, input_items: List[Any], options: Dict[str, Any] = None) -> OperationResult:
        """Analyze multiple items."""
        try:
            options = options or {}
            results = []
            total_items = len(input_items)
            
            for i, item in enumerate(input_items):
                self._update_progress(i, total_items, f"Processing item {i+1}/{total_items}")
                
                # Analyze individual item
                item_result = self.analyze_single(item, options)
                results.append(item_result.data if item_result.success else None)
                
                # Small delay to simulate processing
                time.sleep(0.1)
            
            successful_results = [r for r in results if r is not None]
            
            batch_result = {
                "total_items": total_items,
                "successful": len(successful_results),
                "failed": total_items - len(successful_results),
                "results": successful_results
            }
            
            return OperationResult(
                success=True,
                data=batch_result,
                message=f"Batch analysis completed: {len(successful_results)}/{total_items} successful"
            )
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return OperationResult(
                success=False,
                error=str(e),
                message="Batch analysis failed"
            )
    
    {#if ASYNC_OPERATIONS}
    async def analyze_async(self, input_data: Any, options: Dict[str, Any] = None) -> OperationResult:
        """Asynchronous analysis operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor, 
            self.analyze_single, 
            input_data, 
            options
        )
    {/fi}
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis history."""
        return self.analysis_history.copy()
    
    def clear_history(self):
        """Clear analysis history."""
        self.analysis_history.clear()
    
    def export_results(self, output_path: str, format: str = "json") -> OperationResult:
        """Export analysis results."""
        try:
            output_file = Path(output_path)
            
            if format.lower() == "json":
                with open(output_file, 'w') as f:
                    json.dump(self.analysis_history, f, indent=2)
            elif format.lower() == "yaml":
                with open(output_file, 'w') as f:
                    yaml.dump(self.analysis_history, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return OperationResult(
                success=True,
                message=f"Results exported to {output_file}"
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                error=str(e),
                message="Export failed"
            )
    
    def get_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "service_name": "AnalysisService",
            "version": "1.0.0",
            "capabilities": ["single_analysis", "batch_analysis", "export"],
            "history_count": len(self.analysis_history),
            {#if ASYNC_OPERATIONS}
            "async_support": True,
            {/fi}
            "supported_formats": ["json", "yaml"]
        }
{/if}

{#if APP_TYPE == "PROCESSING"}
class ProcessingService(BaseService):
    """Core processing service shared by CLI and GUI."""
    
    def __init__(self, config_manager: Optional["ConfigurationManager"] = None):
        """Initialize processing service."""
        super().__init__(config_manager)
        self.processing_queue = []
        self.processing_results = []
    
    def process_item(self, input_data: Any, processing_options: Dict[str, Any] = None) -> OperationResult:
        """Process single item."""
        try:
            options = processing_options or {}
            
            self._update_progress(0, 100, "Starting processing...")
            
            # Simulate processing steps
            steps = ["validation", "transformation", "optimization", "finalization"]
            for i, step in enumerate(steps):
                self._update_progress(
                    (i + 1) * 25, 100, 
                    f"Processing step: {step}"
                )
                time.sleep(0.2)  # Simulate processing time
            
            processed_data = {
                "original": str(input_data),
                "processed": f"processed_{input_data}",
                "processing_options": options,
                "timestamp": time.time()
            }
            
            self.processing_results.append(processed_data)
            
            return OperationResult(
                success=True,
                data=processed_data,
                message="Processing completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return OperationResult(
                success=False,
                error=str(e),
                message="Processing failed"
            )
    
    def get_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "service_name": "ProcessingService",
            "version": "1.0.0",
            "queue_size": len(self.processing_queue),
            "results_count": len(self.processing_results)
        }
{/fi}

{#if SERVICE_LAYER}
class ServiceRegistry:
    """Central registry for all services."""
    
    def __init__(self):
        """Initialize service registry."""
        self._services = {}
        self._config_manager = None
    
    def set_config_manager(self, config_manager: "ConfigurationManager"):
        """Set configuration manager for all services."""
        self._config_manager = config_manager
    
    def register_service(self, name: str, service_class: type, **kwargs):
        """Register a service."""
        if self._config_manager:
            kwargs['config_manager'] = self._config_manager
        
        service = service_class(**kwargs)
        self._services[name] = service
        logger.info(f"Registered service: {name}")
    
    def get_service(self, name: str) -> Optional[BaseService]:
        """Get service by name."""
        return self._services.get(name)
    
    def get_all_services(self) -> Dict[str, BaseService]:
        """Get all registered services."""
        return self._services.copy()
    
    def shutdown(self):
        """Shutdown all services."""
        for name, service in self._services.items():
            if hasattr(service, 'shutdown'):
                try:
                    service.shutdown()
                    logger.info(f"Service {name} shut down")
                except Exception as e:
                    logger.error(f"Error shutting down service {name}: {e}")

# Global service registry instance
service_registry = ServiceRegistry()
{/fi}
```

### 2. Command-Line Interface Implementation
Professional CLI using {CLI_FRAMEWORK}:

```python
"""
{APP_NAME} - Command Line Interface
Professional CLI built with {CLI_FRAMEWORK}
"""

{#if CLI_FRAMEWORK == "click"}
import click
from click import echo, style, progressbar
{/if}
{#if CLI_FRAMEWORK == "argparse"}
import argparse
import sys
{/fi}
{#if CLI_FRAMEWORK == "typer"}
import typer
from typing_extensions import Annotated
{/fi}

import sys
import json
import yaml
from pathlib import Path
from typing import Optional, List
{#if COLORED_OUTPUT}
from colorama import init, Fore, Back, Style
{/fi}
{#if CLI_PROGRESS_BARS}
from tqdm import tqdm
{/fi}

# Initialize colorama for cross-platform colored output
{#if COLORED_OUTPUT}
init()
{/fi}

# Import shared services
{#if SERVICE_LAYER}
from .core import service_registry, ConfigurationManager
{/fi}
{#if not SERVICE_LAYER}
from .core import AnalysisService, ProcessingService, ConfigurationManager
{/fi}

{#if CLI_FRAMEWORK == "click"}
# Click-based CLI implementation
class CLI:
    """Command line interface class."""
    
    def __init__(self):
        """Initialize CLI."""
        self.config_manager = ConfigurationManager()
        {#if SERVICE_LAYER}
        service_registry.set_config_manager(self.config_manager)
        self._setup_services()
        {/fi}
        {#if not SERVICE_LAYER}
        {#if APP_TYPE == "ANALYSIS"}
        self.analysis_service = AnalysisService(self.config_manager)
        {/fi}
        {#if APP_TYPE == "PROCESSING"}
        self.processing_service = ProcessingService(self.config_manager)
        {/fi}
        {/fi}
        self._setup_progress_callbacks()
    
    {#if SERVICE_LAYER}
    def _setup_services(self):
        """Setup all services."""
        {#if APP_TYPE == "ANALYSIS"}
        service_registry.register_service("analysis", AnalysisService)
        {/fi}
        {#if APP_TYPE == "PROCESSING"}
        service_registry.register_service("processing", ProcessingService)
        {/fi}
    {/fi}
    
    def _setup_progress_callbacks(self):
        """Setup progress callbacks for services."""
        {#if CLI_PROGRESS_BARS}
        def progress_callback(update):
            """Progress callback for CLI."""
            if not hasattr(self, '_current_progress'):
                self._current_progress = tqdm(total=100, desc="Processing")
            
            self._current_progress.n = update.percentage
            self._current_progress.set_description(update.message)
            self._current_progress.refresh()
            
            if update.current >= update.total:
                self._current_progress.close()
                delattr(self, '_current_progress')
        
        # Set progress callback for services
        {#if SERVICE_LAYER}
        for service in service_registry.get_all_services().values():
            service.set_progress_callback(progress_callback)
        {/fi}
        {#if not SERVICE_LAYER}
        {#if APP_TYPE == "ANALYSIS"}
        self.analysis_service.set_progress_callback(progress_callback)
        {/fi}
        {#if APP_TYPE == "PROCESSING"}
        self.processing_service.set_progress_callback(progress_callback)
        {/fi}
        {/fi}
        {/fi}

# Create CLI instance
cli_instance = CLI()

@click.group()
@click.version_option()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """
    {APP_NAME} - Professional {APP_TYPE} Application
    
    Unified command-line and graphical interface for {APP_TYPE} operations.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if config:
        cli_instance.config_manager = ConfigurationManager(config)
        {#if SERVICE_LAYER}
        service_registry.set_config_manager(cli_instance.config_manager)
        {/fi}
    
    if verbose:
        {#if COLORED_OUTPUT}
        click.echo(style("Verbose mode enabled", fg='green'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo("Verbose mode enabled")
        {/fi}

{#if COMMAND_GROUPS and APP_TYPE == "ANALYSIS"}
@cli.group()
def analyze():
    """Analysis commands."""
    pass

@analyze.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'yaml', 'txt']))
@click.option('--type', '-t', default='default', help='Analysis type')
@click.pass_context
def single(ctx, input_file, output, format, type):
    """Analyze single file."""
    {#if COLORED_OUTPUT}
    click.echo(style(f"Analyzing: {input_file}", fg='blue'))
    {/fi}
    {#if not COLORED_OUTPUT}
    click.echo(f"Analyzing: {input_file}")
    {/fi}
    
    try:
        # Get analysis service
        {#if SERVICE_LAYER}
        analysis_service = service_registry.get_service("analysis")
        {/fi}
        {#if not SERVICE_LAYER}
        analysis_service = cli_instance.analysis_service
        {/fi}
        
        if not analysis_service:
            {#if COLORED_OUTPUT}
            click.echo(style("Analysis service not available", fg='red'))
            {/fi}
            {#if not COLORED_OUTPUT}
            click.echo("Analysis service not available")
            {/fi}
            sys.exit(1)
        
        # Perform analysis
        result = analysis_service.analyze_single(
            input_file, 
            {"type": type}
        )
        
        if result.success:
            # Output result
            if output:
                output_path = Path(output)
                if format == 'json':
                    with open(output_path, 'w') as f:
                        json.dump(result.data, f, indent=2)
                elif format == 'yaml':
                    with open(output_path, 'w') as f:
                        yaml.dump(result.data, f, default_flow_style=False)
                else:
                    with open(output_path, 'w') as f:
                        f.write(str(result.data))
                
                {#if COLORED_OUTPUT}
                click.echo(style(f"Results saved to: {output_path}", fg='green'))
                {/fi}
                {#if not COLORED_OUTPUT}
                click.echo(f"Results saved to: {output_path}")
                {/fi}
            else:
                # Print to console
                if format == 'json':
                    click.echo(json.dumps(result.data, indent=2))
                elif format == 'yaml':
                    click.echo(yaml.dump(result.data, default_flow_style=False))
                else:
                    click.echo(str(result.data))
        else:
            {#if COLORED_OUTPUT}
            click.echo(style(f"Analysis failed: {result.error}", fg='red'))
            {/fi}
            {#if not COLORED_OUTPUT}
            click.echo(f"Analysis failed: {result.error}")
            {/fi}
            sys.exit(1)
    
    except Exception as e:
        {#if COLORED_OUTPUT}
        click.echo(style(f"Error: {e}", fg='red'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo(f"Error: {e}")
        {/fi}
        sys.exit(1)

@analyze.command()
@click.argument('input_files', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', help='Output directory')
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'yaml']))
@click.option('--type', '-t', default='default', help='Analysis type')
@click.pass_context  
def batch(ctx, input_files, output, format, type):
    """Analyze multiple files."""
    if not input_files:
        click.echo("No input files specified")
        sys.exit(1)
    
    {#if COLORED_OUTPUT}
    click.echo(style(f"Batch analyzing {len(input_files)} files", fg='blue'))
    {/fi}
    {#if not COLORED_OUTPUT}
    click.echo(f"Batch analyzing {len(input_files)} files")
    {/fi}
    
    try:
        # Get analysis service
        {#if SERVICE_LAYER}
        analysis_service = service_registry.get_service("analysis")
        {/fi}
        {#if not SERVICE_LAYER}
        analysis_service = cli_instance.analysis_service
        {/fi}
        
        # Perform batch analysis
        result = analysis_service.analyze_batch(
            list(input_files),
            {"type": type}
        )
        
        if result.success:
            {#if COLORED_OUTPUT}
            click.echo(style(result.message, fg='green'))
            {/fi}
            {#if not COLORED_OUTPUT}
            click.echo(result.message)
            {/fi}
            
            # Save results if output specified
            if output:
                output_dir = Path(output)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_file = output_dir / f"batch_results.{format}"
                if format == 'json':
                    with open(output_file, 'w') as f:
                        json.dump(result.data, f, indent=2)
                else:
                    with open(output_file, 'w') as f:
                        yaml.dump(result.data, f, default_flow_style=False)
                
                click.echo(f"Results saved to: {output_file}")
            
        else:
            {#if COLORED_OUTPUT}
            click.echo(style(f"Batch analysis failed: {result.error}", fg='red'))
            {/fi}
            {#if not COLORED_OUTPUT}
            click.echo(f"Batch analysis failed: {result.error}")
            {/fi}
            sys.exit(1)
    
    except Exception as e:
        {#if COLORED_OUTPUT}
        click.echo(style(f"Error: {e}", fg='red'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo(f"Error: {e}")
        {/fi}
        sys.exit(1)
{/if}

{#if INTERACTIVE_MODE}
@cli.command()
def interactive():
    """Start interactive mode."""
    {#if COLORED_OUTPUT}
    click.echo(style("Starting interactive mode...", fg='cyan'))
    click.echo(style("Type 'help' for available commands, 'exit' to quit", fg='yellow'))
    {/fi}
    {#if not COLORED_OUTPUT}
    click.echo("Starting interactive mode...")
    click.echo("Type 'help' for available commands, 'exit' to quit")
    {/fi}
    
    while True:
        try:
            {#if COLORED_OUTPUT}
            command = click.prompt(style("{APP_NAME.lower()}", fg='green') + " > ", type=str)
            {/fi}
            {#if not COLORED_OUTPUT}
            command = input("{APP_NAME.lower()} > ")
            {/fi}
            
            if command.lower() in ['exit', 'quit']:
                {#if COLORED_OUTPUT}
                click.echo(style("Goodbye!", fg='cyan'))
                {/fi}
                {#if not COLORED_OUTPUT}
                click.echo("Goodbye!")
                {/fi}
                break
            elif command.lower() == 'help':
                show_interactive_help()
            elif command.lower() == 'status':
                show_status()
            elif command.startswith('analyze '):
                handle_interactive_analyze(command)
            else:
                {#if COLORED_OUTPUT}
                click.echo(style(f"Unknown command: {command}", fg='red'))
                {/fi}
                {#if not COLORED_OUTPUT}
                click.echo(f"Unknown command: {command}")
                {/fi}
                
        except (KeyboardInterrupt, EOFError):
            {#if COLORED_OUTPUT}
            click.echo(style("\nGoodbye!", fg='cyan'))
            {/fi}
            {#if not COLORED_OUTPUT}
            click.echo("\nGoodbye!")
            {/fi}
            break
        except Exception as e:
            {#if COLORED_OUTPUT}
            click.echo(style(f"Error: {e}", fg='red'))
            {/fi}
            {#if not COLORED_OUTPUT}
            click.echo(f"Error: {e}")
            {/fi}

def show_interactive_help():
    """Show help for interactive mode."""
    help_text = """
Available Commands:
  help                 - Show this help message
  status               - Show application status
  analyze <file>       - Analyze a single file
  exit/quit           - Exit interactive mode
    """
    click.echo(help_text)

def show_status():
    """Show application status."""
    {#if SERVICE_LAYER}
    services = service_registry.get_all_services()
    click.echo("Service Status:")
    for name, service in services.items():
        info = service.get_info()
        click.echo(f"  {name}: {info.get('version', 'unknown')}")
    {/fi}
    {#if not SERVICE_LAYER}
    click.echo("Application Status: Running")
    {/fi}

def handle_interactive_analyze(command):
    """Handle interactive analyze command."""
    parts = command.split(' ', 1)
    if len(parts) < 2:
        click.echo("Usage: analyze <file_path>")
        return
    
    file_path = parts[1].strip()
    if not Path(file_path).exists():
        {#if COLORED_OUTPUT}
        click.echo(style(f"File not found: {file_path}", fg='red'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo(f"File not found: {file_path}")
        {/fi}
        return
    
    # Perform analysis
    {#if SERVICE_LAYER}
    analysis_service = service_registry.get_service("analysis")
    {/fi}
    {#if not SERVICE_LAYER}
    analysis_service = cli_instance.analysis_service
    {/fi}
    
    if analysis_service:
        result = analysis_service.analyze_single(file_path)
        if result.success:
            click.echo(json.dumps(result.data, indent=2))
        else:
            {#if COLORED_OUTPUT}
            click.echo(style(f"Analysis failed: {result.error}", fg='red'))
            {/fi}
            {#if not COLORED_OUTPUT}
            click.echo(f"Analysis failed: {result.error}")
            {/fi}
{/if}

@cli.command()
def gui():
    """Launch graphical user interface."""
    {#if COLORED_OUTPUT}
    click.echo(style("Launching GUI...", fg='cyan'))
    {/fi}
    {#if not COLORED_OUTPUT}
    click.echo("Launching GUI...")
    {/fi}
    
    try:
        from .gui import launch_gui
        launch_gui()
    except ImportError:
        {#if COLORED_OUTPUT}
        click.echo(style("GUI not available. Install GUI dependencies.", fg='red'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo("GUI not available. Install GUI dependencies.")
        {/fi}
    except Exception as e:
        {#if COLORED_OUTPUT}
        click.echo(style(f"Failed to launch GUI: {e}", fg='red'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo(f"Failed to launch GUI: {e}")
        {/fi}

@cli.command()
def config():
    """Show current configuration."""
    config_data = cli_instance.config_manager.config
    click.echo(json.dumps(config_data, indent=2))

@cli.command()
@click.option('--key', '-k', required=True, help='Configuration key')
@click.option('--value', '-v', required=True, help='Configuration value')
def set_config(key, value):
    """Set configuration value."""
    try:
        # Try to parse value as JSON first
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        
        cli_instance.config_manager.set(key, parsed_value)
        {#if COLORED_OUTPUT}
        click.echo(style(f"Configuration updated: {key} = {parsed_value}", fg='green'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo(f"Configuration updated: {key} = {parsed_value}")
        {/fi}
    except Exception as e:
        {#if COLORED_OUTPUT}
        click.echo(style(f"Failed to set configuration: {e}", fg='red'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo(f"Failed to set configuration: {e}")
        {/fi}

def main():
    """Main CLI entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        {#if COLORED_OUTPUT}
        click.echo(style("\nOperation cancelled by user", fg='yellow'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo("\nOperation cancelled by user")
        {/fi}
        sys.exit(1)
    except Exception as e:
        {#if COLORED_OUTPUT}
        click.echo(style(f"Unexpected error: {e}", fg='red'))
        {/fi}
        {#if not COLORED_OUTPUT}
        click.echo(f"Unexpected error: {e}")
        {/fi}
        sys.exit(1)

if __name__ == '__main__':
    main()
{/fi}
```

### 3. Graphical User Interface Implementation
Professional GUI using {GUI_FRAMEWORK}:

```python
"""
{APP_NAME} - Graphical User Interface
Professional GUI built with {GUI_FRAMEWORK}
"""

{#if GUI_FRAMEWORK == "PyQt6"}
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QLineEdit, QTextEdit, QProgressBar, QStatusBar,
    QMenuBar, QMenu, QFileDialog, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QAction
{/fi}

from typing import Optional, Dict, Any, List
import json
import logging
from pathlib import Path

# Import shared services
{#if SERVICE_LAYER}
from .core import service_registry, ConfigurationManager
{/fi}
{#if not SERVICE_LAYER}
from .core import AnalysisService, ProcessingService, ConfigurationManager
{/fi}

logger = logging.getLogger(__name__)

{#if GUI_FRAMEWORK == "PyQt6"}
class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Initialize services
        self.config_manager = ConfigurationManager()
        {#if SERVICE_LAYER}
        service_registry.set_config_manager(self.config_manager)
        self._setup_services()
        {/fi}
        {#if not SERVICE_LAYER}
        {#if APP_TYPE == "ANALYSIS"}
        self.analysis_service = AnalysisService(self.config_manager)
        {/fi}
        {#if APP_TYPE == "PROCESSING"}
        self.processing_service = ProcessingService(self.config_manager)
        {/fi}
        {/fi}
        
        # Setup UI
        self.setWindowTitle("{APP_NAME}")
        self.setGeometry(100, 100, 1200, 800)
        
        {#if THEME_SYSTEM}
        self.setup_theme()
        {/fi}
        self.setup_ui()
        self.setup_connections()
        {#if REAL_TIME_UPDATES}
        self.setup_real_time_updates()
        {/fi}
        
        logger.info("GUI initialized")
    
    {#if SERVICE_LAYER}
    def _setup_services(self):
        """Setup all services."""
        {#if APP_TYPE == "ANALYSIS"}
        service_registry.register_service("analysis", AnalysisService)
        {/fi}
        {#if APP_TYPE == "PROCESSING"}
        service_registry.register_service("processing", ProcessingService)
        {/fi}
        
        # Setup progress callbacks
        for service in service_registry.get_all_services().values():
            service.set_progress_callback(self.on_progress_update)
    {/fi}
    
    {#if THEME_SYSTEM}
    def setup_theme(self):
        """Setup application theme."""
        theme = self.config_manager.get("interfaces.gui.theme", "dark")
        
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #3c3c3c;
                }
                QTabBar::tab {
                    background-color: #4a4a4a;
                    color: white;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #0078d4;
                }
                QPushButton {
                    background-color: #0078d4;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QTableWidget {
                    background-color: #3c3c3c;
                    alternate-background-color: #454545;
                    gridline-color: #555555;
                }
            """)
    {/fi}
    
    def setup_ui(self):
        """Setup user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup tabs
        {#if APP_TYPE == "ANALYSIS"}
        self.setup_analysis_tab()
        self.setup_results_tab()
        {/fi}
        {#if APP_TYPE == "PROCESSING"}
        self.setup_processing_tab()
        self.setup_queue_tab()
        {/fi}
        
        self.setup_settings_tab()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar in status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Menu bar
        self.setup_menu_bar()
    
    {#if APP_TYPE == "ANALYSIS"}
    def setup_analysis_tab(self):
        """Setup analysis tab."""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("Select file to analyze...")
        input_layout.addWidget(QLabel("Input File:"))
        input_layout.addWidget(self.input_file_edit)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_input_file)
        input_layout.addWidget(self.browse_button)
        
        layout.addLayout(input_layout)
        
        # Analysis options
        options_layout = QHBoxLayout()
        self.analysis_type_edit = QLineEdit("default")
        options_layout.addWidget(QLabel("Analysis Type:"))
        options_layout.addWidget(self.analysis_type_edit)
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("Analyze Single")
        self.analyze_button.clicked.connect(self.analyze_single)
        button_layout.addWidget(self.analyze_button)
        
        self.batch_analyze_button = QPushButton("Batch Analyze")
        self.batch_analyze_button.clicked.connect(self.analyze_batch)
        button_layout.addWidget(self.batch_analyze_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(QLabel("Analysis Results:"))
        layout.addWidget(self.results_text)
        
        self.tab_widget.addTab(analysis_widget, "Analysis")
    
    def setup_results_tab(self):
        """Setup results tab."""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "File", "Analysis Type", "Confidence", "Status"
        ])
        layout.addWidget(self.results_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_json_button = QPushButton("Export JSON")
        self.export_json_button.clicked.connect(lambda: self.export_results("json"))
        export_layout.addWidget(self.export_json_button)
        
        self.export_yaml_button = QPushButton("Export YAML")
        self.export_yaml_button.clicked.connect(lambda: self.export_results("yaml"))
        export_layout.addWidget(self.export_yaml_button)
        
        self.clear_results_button = QPushButton("Clear Results")
        self.clear_results_button.clicked.connect(self.clear_results)
        export_layout.addWidget(self.clear_results_button)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        self.tab_widget.addTab(results_widget, "Results")
    {/fi}
    
    def setup_settings_tab(self):
        """Setup settings tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Configuration display
        layout.addWidget(QLabel("Configuration:"))
        
        self.config_text = QTextEdit()
        self.config_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.config_text)
        
        # Update config display
        self.update_config_display()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reload_config_button = QPushButton("Reload Config")
        self.reload_config_button.clicked.connect(self.reload_config)
        button_layout.addWidget(self.reload_config_button)
        
        self.save_config_button = QPushButton("Save Config")
        self.save_config_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_config_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(settings_widget, "Settings")
    
    def setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        export_action = QAction('Export Results', self)
        export_action.triggered.connect(lambda: self.export_results("json"))
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        {#if THEME_SYSTEM}
        theme_menu = view_menu.addMenu('Theme')
        
        dark_theme_action = QAction('Dark', self)
        dark_theme_action.triggered.connect(lambda: self.change_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction('Light', self)
        light_theme_action.triggered.connect(lambda: self.change_theme('light'))
        theme_menu.addAction(light_theme_action)
        {/fi}
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_connections(self):
        """Setup signal/slot connections."""
        pass
    
    {#if REAL_TIME_UPDATES}
    def setup_real_time_updates(self):
        """Setup real-time updates."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(1000)  # Update every second
    
    def update_displays(self):
        """Update all displays with latest data."""
        # Update results table
        self.update_results_table()
        
        # Update status
        self.update_status()
    {/fi}
    
    # Event handlers
    def browse_input_file(self):
        """Browse for input file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input File", "", "All Files (*)"
        )
        
        if file_path:
            self.input_file_edit.setText(file_path)
    
    {#if APP_TYPE == "ANALYSIS"}
    def analyze_single(self):
        """Analyze single file."""
        input_file = self.input_file_edit.text().strip()
        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select an input file")
            return
        
        analysis_type = self.analysis_type_edit.text().strip()
        
        try:
            # Get analysis service
            {#if SERVICE_LAYER}
            analysis_service = service_registry.get_service("analysis")
            {/fi}
            {#if not SERVICE_LAYER}
            analysis_service = self.analysis_service
            {/fi}
            
            if not analysis_service:
                QMessageBox.critical(self, "Error", "Analysis service not available")
                return
            
            # Disable button during analysis
            self.analyze_button.setEnabled(False)
            
            # Start analysis in background thread
            self.analysis_thread = AnalysisThread(
                analysis_service, input_file, {"type": analysis_type}
            )
            self.analysis_thread.finished.connect(self.on_analysis_finished)
            self.analysis_thread.error.connect(self.on_analysis_error)
            self.analysis_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {e}")
            self.analyze_button.setEnabled(True)
    
    def analyze_batch(self):
        """Analyze multiple files."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Files for Batch Analysis", "", "All Files (*)"
        )
        
        if not file_paths:
            return
        
        analysis_type = self.analysis_type_edit.text().strip()
        
        try:
            # Get analysis service
            {#if SERVICE_LAYER}
            analysis_service = service_registry.get_service("analysis")
            {/fi}
            {#if not SERVICE_LAYER}
            analysis_service = self.analysis_service
            {/fi}
            
            # Start batch analysis
            self.batch_analyze_button.setEnabled(False)
            
            self.batch_analysis_thread = BatchAnalysisThread(
                analysis_service, file_paths, {"type": analysis_type}
            )
            self.batch_analysis_thread.finished.connect(self.on_batch_analysis_finished)
            self.batch_analysis_thread.error.connect(self.on_analysis_error)
            self.batch_analysis_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Batch analysis failed: {e}")
            self.batch_analyze_button.setEnabled(True)
    {/fi}
    
    def on_progress_update(self, update):
        """Handle progress updates from services."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(int(update.percentage))
        self.status_bar.showMessage(update.message)
        
        if update.current >= update.total:
            self.progress_bar.setVisible(False)
    
    def on_analysis_finished(self, result):
        """Handle analysis completion."""
        self.analyze_button.setEnabled(True)
        
        if result.success:
            # Display results
            self.results_text.setText(json.dumps(result.data, indent=2))
            
            # Update results table
            self.add_result_to_table(result)
            
            self.status_bar.showMessage("Analysis completed successfully")
        else:
            QMessageBox.critical(self, "Analysis Failed", result.error)
    
    def on_batch_analysis_finished(self, result):
        """Handle batch analysis completion."""
        self.batch_analyze_button.setEnabled(True)
        
        if result.success:
            # Display results
            self.results_text.setText(json.dumps(result.data, indent=2))
            
            # Update results table with all results
            if 'results' in result.data:
                for item_result in result.data['results']:
                    self.add_result_to_table(OperationResult(True, item_result))
            
            self.status_bar.showMessage(f"Batch analysis completed: {result.data.get('successful', 0)} successful")
        else:
            QMessageBox.critical(self, "Batch Analysis Failed", result.error)
    
    def on_analysis_error(self, error_message):
        """Handle analysis error."""
        self.analyze_button.setEnabled(True)
        self.batch_analyze_button.setEnabled(True)
        QMessageBox.critical(self, "Analysis Error", error_message)
    
    def add_result_to_table(self, result):
        """Add analysis result to results table."""
        if not result.success or not result.data:
            return
        
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Extract data for table
        data = result.data
        file_name = data.get('input', 'Unknown')[:50]  # Truncate long paths
        analysis_type = data.get('analysis_type', 'default')
        confidence = data.get('confidence', 0.0)
        
        self.results_table.setItem(row, 0, QTableWidgetItem(file_name))
        self.results_table.setItem(row, 1, QTableWidgetItem(analysis_type))
        self.results_table.setItem(row, 2, QTableWidgetItem(f"{confidence:.2f}"))
        self.results_table.setItem(row, 3, QTableWidgetItem("Completed"))
    
    def update_results_table(self):
        """Update results table with latest data."""
        # Get latest results from service
        {#if SERVICE_LAYER}
        analysis_service = service_registry.get_service("analysis")
        {/fi}
        {#if not SERVICE_LAYER}
        analysis_service = self.analysis_service
        {/fi}
        
        if analysis_service and hasattr(analysis_service, 'get_analysis_history'):
            history = analysis_service.get_analysis_history()
            
            # Clear and repopulate table
            self.results_table.setRowCount(0)
            for result_data in history:
                result = OperationResult(True, result_data)
                self.add_result_to_table(result)
    
    def update_status(self):
        """Update status bar with current information."""
        {#if SERVICE_LAYER}
        services = service_registry.get_all_services()
        active_services = len(services)
        self.status_bar.showMessage(f"Services active: {active_services}")
        {/fi}
    
    def export_results(self, format: str):
        """Export analysis results."""
        {#if SERVICE_LAYER}
        analysis_service = service_registry.get_service("analysis")
        {/fi}
        {#if not SERVICE_LAYER}
        analysis_service = self.analysis_service
        {/fi}
        
        if not analysis_service:
            QMessageBox.warning(self, "Warning", "Analysis service not available")
            return
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export Results as {format.upper()}", 
            f"results.{format}", f"{format.upper()} Files (*.{format})"
        )
        
        if file_path:
            result = analysis_service.export_results(file_path, format)
            if result.success:
                QMessageBox.information(self, "Success", result.message)
            else:
                QMessageBox.critical(self, "Export Failed", result.error)
    
    def clear_results(self):
        """Clear analysis results."""
        reply = QMessageBox.question(
            self, "Clear Results", 
            "Are you sure you want to clear all results?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            {#if SERVICE_LAYER}
            analysis_service = service_registry.get_service("analysis")
            {/fi}
            {#if not SERVICE_LAYER}
            analysis_service = self.analysis_service
            {/fi}
            
            if analysis_service and hasattr(analysis_service, 'clear_history'):
                analysis_service.clear_history()
            
            self.results_table.setRowCount(0)
            self.results_text.clear()
            
            QMessageBox.information(self, "Success", "Results cleared")
    
    def update_config_display(self):
        """Update configuration display."""
        config_text = json.dumps(self.config_manager.config, indent=2)
        self.config_text.setText(config_text)
    
    def reload_config(self):
        """Reload configuration."""
        self.config_manager.load_config()
        self.update_config_display()
        QMessageBox.information(self, "Success", "Configuration reloaded")
    
    def save_config(self):
        """Save configuration."""
        try:
            # Parse config text and save
            config_data = json.loads(self.config_text.toPlainText())
            self.config_manager.config = config_data
            self.config_manager.save_config()
            QMessageBox.information(self, "Success", "Configuration saved")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Invalid JSON", f"Configuration format error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Failed to save configuration: {e}")
    
    {#if THEME_SYSTEM}
    def change_theme(self, theme: str):
        """Change application theme."""
        self.config_manager.set("interfaces.gui.theme", theme)
        self.setup_theme()
        QMessageBox.information(self, "Theme Changed", f"Theme changed to {theme}")
    {/fi}
    
    def open_file(self):
        """Open file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        
        if file_path:
            self.input_file_edit.setText(file_path)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About {APP_NAME}",
            f"""
            <h3>{APP_NAME}</h3>
            <p>Professional {APP_TYPE} Application</p>
            <p>Unified CLI and GUI Interface</p>
            <p>Version 1.0</p>
            """
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save configuration
        self.config_manager.save_config()
        
        # Shutdown services
        {#if SERVICE_LAYER}
        service_registry.shutdown()
        {/fi}
        
        event.accept()

# Worker threads for background operations
class AnalysisThread(QThread):
    """Background thread for single analysis."""
    
    finished = pyqtSignal(object)  # OperationResult
    error = pyqtSignal(str)
    
    def __init__(self, analysis_service, input_file, options):
        super().__init__()
        self.analysis_service = analysis_service
        self.input_file = input_file
        self.options = options
    
    def run(self):
        """Run analysis in background."""
        try:
            result = self.analysis_service.analyze_single(self.input_file, self.options)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class BatchAnalysisThread(QThread):
    """Background thread for batch analysis."""
    
    finished = pyqtSignal(object)  # OperationResult
    error = pyqtSignal(str)
    
    def __init__(self, analysis_service, input_files, options):
        super().__init__()
        self.analysis_service = analysis_service
        self.input_files = input_files
        self.options = options
    
    def run(self):
        """Run batch analysis in background."""
        try:
            result = self.analysis_service.analyze_batch(self.input_files, self.options)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

def launch_gui():
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("{APP_NAME}")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    return app.exec()
{/fi}

def main():
    """Main GUI entry point."""
    {#if GUI_FRAMEWORK == "PyQt6"}
    return launch_gui()
    {/fi}

if __name__ == '__main__':
    sys.exit(main())
```

## Project Structure

```
{APP_NAME.lower().replace(' ', '_')}/
├── src/
│   ├── __init__.py
│   ├── core/                   # Shared business logic
│   │   ├── __init__.py
│   │   ├── services.py         # Core services
│   │   ├── config.py           # Configuration management
│   │   ├── state.py            # State management
│   │   └── models.py           # Data models
│   ├── cli/                    # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py             # CLI entry point
│   │   ├── commands/           # Command implementations
│   │   │   ├── __init__.py
│   │   │   ├── analyze.py
│   │   │   ├── config.py
│   │   │   └── interactive.py
│   │   └── utils.py            # CLI utilities
│   ├── gui/                    # Graphical interface
│   │   ├── __init__.py
│   │   ├── main.py             # GUI entry point
│   │   ├── windows/            # Main windows
│   │   │   ├── __init__.py
│   │   │   └── main_window.py
│   │   ├── widgets/            # Custom widgets
│   │   │   ├── __init__.py
│   │   │   ├── analysis_widget.py
│   │   │   └── results_widget.py
│   │   └── themes/             # Theme files
│   │       ├── __init__.py
│   │       ├── dark.py
│   │       └── light.py
│   {#if PLUGIN_ARCHITECTURE}
│   ├── plugins/                # Plugin system
│   │   ├── __init__.py
│   │   ├── base_plugin.py
│   │   └── sample_plugin.py
│   {/fi}
│   └── utils/                  # Shared utilities
│       ├── __init__.py
│       ├── logging.py
│       └── helpers.py
├── config/
│   ├── config.yaml             # Default configuration
│   └── config.example.yaml     # Example configuration
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   ├── test_cli/
│   └── test_gui/
├── scripts/
│   ├── {APP_NAME.lower()}-cli   # CLI entry script
│   └── {APP_NAME.lower()}-gui   # GUI entry script
├── requirements.txt
├── setup.py
└── README.md
```

## Dependencies

```txt
# Core dependencies
{#if CLI_FRAMEWORK == "click"}
click>=8.0.0
{/fi}
{#if CLI_FRAMEWORK == "typer"}
typer>=0.7.0
{/fi}

{#if GUI_FRAMEWORK == "PyQt6"}
PyQt6>=6.4.0
{/fi}

{#if COLORED_OUTPUT}
colorama>=0.4.0
{/fi}

{#if CLI_PROGRESS_BARS}
tqdm>=4.64.0
{/fi}

# Configuration
pyyaml>=6.0
python-dotenv>=0.19.0

# Utilities
pathlib
dataclasses
logging
threading
```

## Usage Examples

### CLI Usage
```bash
# Single file analysis
{APP_NAME.lower()} analyze single input.txt --output results.json

# Batch analysis
{APP_NAME.lower()} analyze batch *.txt --output-dir results/

# Interactive mode
{APP_NAME.lower()} interactive

# Launch GUI
{APP_NAME.lower()} gui

# Configuration
{APP_NAME.lower()} set-config analysis.batch_size 20
```

### GUI Usage
```python
# Launch GUI programmatically
from src.gui import launch_gui
launch_gui()

# Access shared services
from src.core import service_registry
analysis_service = service_registry.get_service("analysis")
```

### Shared Service Usage
```python
# Use services from both CLI and GUI
from src.core import AnalysisService, ConfigurationManager

config = ConfigurationManager()
service = AnalysisService(config)

result = service.analyze_single("data.txt")
if result.success:
    print(f"Analysis completed: {result.data}")
```

## Validation Criteria

A successful implementation should demonstrate:

1. **Unified Architecture**: Shared business logic between CLI and GUI
2. **Professional CLI**: Well-organized {CLI_FRAMEWORK} commands with proper help
3. **Modern GUI**: Responsive {GUI_FRAMEWORK} interface with themes
4. **Configuration Management**: Unified configuration system
5. **Cross-Interface Communication**: Seamless data sharing
6. **Error Handling**: Robust error management in both interfaces

---

*Generated by CLI-GUI Integration Pattern Generator Meta-Prompt*  
*Version 1.0 - Based on MAP4 Dual-Interface Architecture*