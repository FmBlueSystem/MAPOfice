#!/usr/bin/env python3
"""MAP4 - Music Analyzer Pro - Unified CLI Interface.

This is the main entry point for the MAP4 command-line interface,
providing a unified interface for all music analysis operations.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import click
from typing import Optional

# Import command groups
from .commands import analyze, playlist, provider, bmad

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.version_option(version='1.0.0', prog_name='MAP4')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--config', type=click.Path(exists=True), help='Path to configuration file')
@click.pass_context
def cli(ctx, debug: bool, config: Optional[str]):
    """MAP4 - Music Analyzer Pro - Unified CLI Interface.
    
    A comprehensive tool for music analysis, playlist generation,
    and audio processing using multiple LLM providers.
    
    Use 'map4 COMMAND --help' for more information on a specific command.
    """
    # Set debug logging if requested
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Store config path in context
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    
    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register command groups
cli.add_command(analyze.analyze_group)
cli.add_command(playlist.playlist_group)
cli.add_command(provider.provider_group)
cli.add_command(bmad.bmad_group)


@cli.command(name='version')
def show_version():
    """Show detailed version information."""
    click.echo("MAP4 - Music Analyzer Pro")
    click.echo("Version: 1.0.0")
    click.echo("Python: " + sys.version)
    click.echo("Project: Unified CLI Architecture")


@cli.command(name='info')
@click.pass_context
def show_info(ctx):
    """Show system and configuration information."""
    from ..analysis.provider_factory import LLMProviderFactory
    import os
    
    click.echo("=== MAP4 System Information ===")
    click.echo(f"Python Version: {sys.version}")
    click.echo(f"Project Root: {project_root}")
    
    # Check for API keys
    click.echo("\n=== API Key Status ===")
    api_keys = {
        'ZAI_API_KEY': 'ZAI Provider',
        'ANTHROPIC_API_KEY': 'Claude Provider',
        'GEMINI_API_KEY': 'Gemini Provider',
        'OPENAI_API_KEY': 'OpenAI Provider'
    }
    
    for key, provider in api_keys.items():
        status = "✓ Set" if os.getenv(key) else "✗ Not Set"
        click.echo(f"{provider}: {status}")
    
    # Show registered providers
    click.echo("\n=== Registered Providers ===")
    providers = LLMProviderFactory.list_providers()
    if providers:
        for provider in providers:
            click.echo(f"  - {provider}")
    else:
        click.echo("  No providers registered")
    
    # Show configuration
    if ctx.obj.get('config_path'):
        click.echo(f"\n=== Configuration ===")
        click.echo(f"Config File: {ctx.obj['config_path']}")


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        if '--debug' in sys.argv:
            raise
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()