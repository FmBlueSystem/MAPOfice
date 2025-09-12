"""Provider command module for MAP4 CLI.

This module provides commands for managing LLM providers.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import click
from tabulate import tabulate

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.provider_factory import LLMProviderFactory, get_provider
from src.analysis.base_provider import ProviderConfig


@click.group(name='provider')
def provider_group():
    """LLM provider management commands."""
    pass


@provider_group.command(name='list')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information')
@click.pass_context
def list_providers(ctx, verbose: bool):
    """List all available LLM providers.
    
    Example:
        map4 provider list --verbose
    """
    click.echo("=== Available LLM Providers ===\n")
    
    # Auto-discover providers
    LLMProviderFactory.auto_discover_providers()
    
    providers = LLMProviderFactory.list_providers()
    
    if not providers:
        click.echo("No providers registered.")
        click.echo("\nTo register providers, ensure they are in src/analysis/providers/")
        return
    
    if verbose:
        # Detailed table view
        table_data = []
        for provider_name in providers:
            try:
                info = LLMProviderFactory.get_provider_info(provider_name)
                table_data.append([
                    provider_name,
                    info.get('version', 'N/A'),
                    ', '.join(info.get('capabilities', [])) if info.get('capabilities') else 'N/A',
                    '✓' if info.get('available', False) else '✗'
                ])
            except Exception as e:
                table_data.append([
                    provider_name,
                    'Error',
                    str(e)[:50],
                    '✗'
                ])
        
        headers = ['Provider', 'Version', 'Capabilities', 'Available']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    else:
        # Simple list
        for provider_name in providers:
            click.echo(f"  • {provider_name}")
    
    click.echo(f"\nTotal providers: {len(providers)}")


@provider_group.command(name='configure')
@click.argument('provider_name')
@click.option('--api-key', help='API key for the provider')
@click.option('--api-key-env', help='Environment variable containing API key')
@click.option('--model', help='Model to use')
@click.option('--base-url', help='Base URL for API')
@click.option('--timeout', type=int, default=30, help='Request timeout in seconds')
@click.option('--save', is_flag=True, help='Save configuration to file')
@click.option('--config-file', type=click.Path(), help='Configuration file path')
@click.pass_context
def configure_provider(ctx, provider_name: str, api_key: Optional[str],
                       api_key_env: Optional[str], model: Optional[str],
                       base_url: Optional[str], timeout: int, save: bool,
                       config_file: Optional[str]):
    """Configure an LLM provider.
    
    Example:
        map4 provider configure zai --api-key-env ZAI_API_KEY --model gpt-4 --save
    """
    click.echo(f"Configuring provider: {provider_name}")
    
    # Build configuration
    config = {}
    
    if api_key:
        config['api_key'] = api_key
    elif api_key_env:
        config['api_key_env'] = api_key_env
        # Try to load from environment
        env_value = os.getenv(api_key_env)
        if env_value:
            config['api_key'] = env_value
            click.echo(f"✓ Loaded API key from {api_key_env}")
        else:
            click.echo(f"⚠ Environment variable {api_key_env} not set", err=True)
    
    if model:
        config['model'] = model
    
    if base_url:
        config['base_url'] = base_url
    
    config['timeout'] = timeout
    
    # Register provider with configuration
    try:
        # First, auto-discover to ensure provider class is available
        LLMProviderFactory.auto_discover_providers()
        
        # Get provider class
        provider_class = LLMProviderFactory.get_provider_class(provider_name)
        
        # Register with default config
        LLMProviderFactory.register_provider(
            provider_name, 
            provider_class,
            default_config=config
        )
        
        click.echo(f"✓ Provider {provider_name} configured successfully")
        
        # Test the configuration
        click.echo("\nTesting provider connection...")
        provider = get_provider(provider_name)
        if provider.test_connection():
            click.echo("✓ Connection test successful")
        else:
            click.echo("✗ Connection test failed", err=True)
        
    except Exception as e:
        click.echo(f"Error configuring provider: {e}", err=True)
        ctx.exit(1)
    
    # Save configuration if requested
    if save:
        if not config_file:
            config_file = f"config/{provider_name}_config.json"
        
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        click.echo(f"✓ Configuration saved to: {config_path}")


@provider_group.command(name='test')
@click.argument('provider_name', required=False)
@click.option('--all', 'test_all', is_flag=True, help='Test all providers')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def test_provider(ctx, provider_name: Optional[str], test_all: bool, verbose: bool):
    """Test provider connections.
    
    Example:
        map4 provider test zai
        map4 provider test --all
    """
    # Auto-discover providers
    LLMProviderFactory.auto_discover_providers()
    
    if test_all:
        click.echo("Testing all providers...\n")
        results = LLMProviderFactory.test_all_providers()
        
        # Display results
        table_data = []
        for name, status in results.items():
            status_symbol = '✓' if status else '✗'
            status_text = 'Connected' if status else 'Failed'
            table_data.append([name, status_symbol, status_text])
        
        headers = ['Provider', 'Status', 'Connection']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Summary
        successful = sum(1 for s in results.values() if s)
        click.echo(f"\nSummary: {successful}/{len(results)} providers connected successfully")
        
    elif provider_name:
        click.echo(f"Testing provider: {provider_name}")
        
        try:
            provider = get_provider(provider_name)
            
            if verbose:
                info = provider.get_provider_info()
                click.echo(f"\nProvider Info:")
                click.echo(f"  Name: {info.get('name', 'Unknown')}")
                click.echo(f"  Version: {info.get('version', 'Unknown')}")
                click.echo(f"  Capabilities: {', '.join(info.get('capabilities', []))}")
            
            click.echo("\nTesting connection...")
            if provider.test_connection():
                click.echo("✓ Connection successful")
                
                # Get rate limit status if available
                if verbose:
                    try:
                        rate_limit = provider.get_rate_limit_status()
                        if rate_limit and rate_limit.get('requests_remaining') is not None:
                            click.echo(f"\nRate Limit Status:")
                            click.echo(f"  Requests remaining: {rate_limit['requests_remaining']}")
                            click.echo(f"  Limit: {rate_limit.get('limit', 'N/A')}")
                    except:
                        pass
            else:
                click.echo("✗ Connection failed", err=True)
                ctx.exit(1)
                
        except Exception as e:
            click.echo(f"Error testing provider: {e}", err=True)
            if verbose:
                import traceback
                traceback.print_exc()
            ctx.exit(1)
    else:
        click.echo("Please specify a provider name or use --all")
        ctx.exit(1)


@provider_group.command(name='benchmark')
@click.argument('provider_name')
@click.option('--test-file', type=click.Path(exists=True), 
              help='Audio file to use for benchmark')
@click.option('--iterations', type=int, default=5, help='Number of iterations')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def benchmark_provider(ctx, provider_name: str, test_file: Optional[str],
                       iterations: int, verbose: bool):
    """Benchmark provider performance.
    
    Example:
        map4 provider benchmark zai --test-file sample.mp3 --iterations 10
    """
    import time
    import statistics
    
    click.echo(f"Benchmarking provider: {provider_name}")
    click.echo(f"Iterations: {iterations}")
    
    try:
        provider = get_provider(provider_name)
    except Exception as e:
        click.echo(f"Failed to initialize provider: {e}", err=True)
        ctx.exit(1)
    
    # Prepare test data
    if test_file:
        from mutagen import File
        audio_file = File(test_file)
        test_metadata = {
            'title': audio_file.get('TIT2', ['Unknown'])[0] if audio_file else 'Test Track',
            'artist': audio_file.get('TPE1', ['Unknown'])[0] if audio_file else 'Test Artist',
            'album': audio_file.get('TALB', ['Unknown'])[0] if audio_file else 'Test Album',
            'duration': audio_file.info.length if audio_file else 180,
            'file_path': test_file
        }
    else:
        # Use dummy data
        test_metadata = {
            'title': 'Benchmark Test Track',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'duration': 240,
            'file_path': 'test.mp3'
        }
    
    click.echo(f"Test track: {test_metadata['artist']} - {test_metadata['title']}")
    click.echo("\nRunning benchmark...")
    
    # Run benchmark
    times = []
    errors = 0
    
    with click.progressbar(range(iterations), label='Progress') as bar:
        for i in bar:
            try:
                start_time = time.time()
                result = provider.analyze_track(test_metadata)
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                if verbose and i == 0:
                    click.echo(f"\nFirst result sample:")
                    if isinstance(result, dict):
                        for key in ['genre', 'mood', 'key', 'bpm']:
                            if key in result:
                                click.echo(f"  {key}: {result[key]}")
                
            except Exception as e:
                errors += 1
                if verbose:
                    click.echo(f"\nError in iteration {i+1}: {e}")
    
    # Calculate statistics
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        click.echo("\n=== Benchmark Results ===")
        click.echo(f"Successful: {len(times)}/{iterations}")
        click.echo(f"Errors: {errors}")
        click.echo(f"\nTiming Statistics:")
        click.echo(f"  Average: {avg_time:.2f}s")
        click.echo(f"  Min: {min_time:.2f}s")
        click.echo(f"  Max: {max_time:.2f}s")
        click.echo(f"  Std Dev: {std_dev:.2f}s")
        click.echo(f"\nThroughput: {60/avg_time:.1f} tracks/minute")
    else:
        click.echo("All benchmark iterations failed", err=True)
        ctx.exit(1)


@provider_group.command(name='compare')
@click.argument('providers', nargs=-1, required=True)
@click.option('--test-file', type=click.Path(exists=True), required=True,
              help='Audio file to analyze')
@click.option('--output', '-o', type=click.Path(), help='Save comparison to file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def compare_providers(ctx, providers: tuple, test_file: str, 
                     output: Optional[str], verbose: bool):
    """Compare analysis results from multiple providers.
    
    Example:
        map4 provider compare zai claude gemini --test-file song.mp3
    """
    from mutagen import File
    import time
    
    click.echo(f"Comparing providers: {', '.join(providers)}")
    click.echo(f"Test file: {test_file}")
    
    # Load test file metadata
    audio_file = File(test_file)
    if audio_file:
        test_metadata = {
            'title': str(audio_file.get('TIT2', ['Unknown'])[0]) if audio_file.get('TIT2') else 'Unknown',
            'artist': str(audio_file.get('TPE1', ['Unknown'])[0]) if audio_file.get('TPE1') else 'Unknown',
            'album': str(audio_file.get('TALB', ['Unknown'])[0]) if audio_file.get('TALB') else 'Unknown',
            'duration': audio_file.info.length,
            'file_path': test_file
        }
    else:
        click.echo("Failed to read audio file metadata", err=True)
        ctx.exit(1)
    
    click.echo(f"\nAnalyzing: {test_metadata['artist']} - {test_metadata['title']}")
    click.echo("=" * 60)
    
    results = {}
    
    for provider_name in providers:
        click.echo(f"\nTesting {provider_name}...")
        
        try:
            provider = get_provider(provider_name)
            
            start_time = time.time()
            result = provider.analyze_track(test_metadata)
            elapsed = time.time() - start_time
            
            results[provider_name] = {
                'result': result,
                'time': elapsed,
                'success': True
            }
            
            click.echo(f"✓ Completed in {elapsed:.2f}s")
            
        except Exception as e:
            results[provider_name] = {
                'error': str(e),
                'success': False
            }
            click.echo(f"✗ Failed: {e}")
    
    # Display comparison
    click.echo("\n=== Comparison Results ===")
    
    # Create comparison table
    comparison_fields = ['genre', 'mood', 'key', 'bpm', 'energy', 'valence']
    table_data = []
    
    for field in comparison_fields:
        row = [field.capitalize()]
        for provider_name in providers:
            if results[provider_name]['success']:
                value = results[provider_name]['result'].get(field, 'N/A')
                row.append(str(value))
            else:
                row.append('Error')
        table_data.append(row)
    
    # Add timing row
    timing_row = ['Time (s)']
    for provider_name in providers:
        if results[provider_name]['success']:
            timing_row.append(f"{results[provider_name]['time']:.2f}")
        else:
            timing_row.append('N/A')
    table_data.append(timing_row)
    
    headers = ['Field'] + list(providers)
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Save results if requested
    if output:
        output_data = {
            'test_file': test_file,
            'metadata': test_metadata,
            'providers': results
        }
        
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        click.echo(f"\n✓ Comparison saved to: {output}")