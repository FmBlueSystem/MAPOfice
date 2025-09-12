# MAP4 CLI System - Unified Command-Line Interface

## Objective
Create a comprehensive command-line interface using Click framework with command groups for analysis, playlist generation, provider management, and BMAD operations.

## Prerequisites
- Completed core implementation and services
- Click framework installed
- All analysis components functional

## Step 1: Unified CLI Main Entry

### 1.1 Create Main CLI Entry Point
Create `src/cli/unified_main.py`:

```python
"""Unified CLI interface for MAP4."""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.cli.commands.analyze_commands import analyze_group
from src.cli.commands.playlist_commands import playlist_group
from src.cli.commands.provider_commands import provider_group
from src.cli.commands.bmad_commands import bmad_group
from src.cli.commands.library_commands import library_group

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', type=click.Path(), help='Configuration file path')
@click.pass_context
def cli(ctx, debug: bool, config: Optional[str]):
    """MAP4 - Music Analyzer Pro - Unified CLI Interface
    
    Professional music analysis with HAMMS v3.0 and AI enrichment.
    """
    # Set debug level
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        click.echo("Debug mode enabled")
    
    # Load configuration
    ctx.ensure_object(dict)
    ctx.obj['config'] = get_config(config)
    ctx.obj['debug'] = debug

# Register command groups
cli.add_command(analyze_group)
cli.add_command(playlist_group)
cli.add_command(provider_group)
cli.add_command(bmad_group)
cli.add_command(library_group)

@cli.command()
def version():
    """Show MAP4 version information."""
    click.echo("MAP4 - Music Analyzer Pro v3.0")
    click.echo("HAMMS Engine: v3.0")
    click.echo("Python: " + sys.version.split()[0])

@cli.command()
@click.pass_context
def status(ctx):
    """Show system status."""
    from src.services.storage_service import StorageService
    from src.analysis.providers.provider_factory import ProviderFactory
    
    click.echo("MAP4 System Status")
    click.echo("=" * 50)
    
    # Database status
    storage = StorageService()
    stats = storage.get_statistics()
    click.echo(f"Database:")
    click.echo(f"  Total tracks: {stats['total_tracks']}")
    click.echo(f"  Analyzed tracks: {stats['analyzed_tracks']}")
    click.echo(f"  HAMMS vectors: {stats['total_hamms_vectors']}")
    click.echo(f"  AI analyses: {stats['total_ai_analyses']}")
    
    # Provider status
    click.echo(f"\nProviders:")
    providers = ProviderFactory.get_available_providers()
    for provider in providers:
        click.echo(f"  - {provider}")
    
    # Configuration status
    config = ctx.obj['config']
    click.echo(f"\nConfiguration:")
    click.echo(f"  Sample rate: {config.analysis.sample_rate} Hz")
    click.echo(f"  Cache enabled: {config.analysis.cache_enabled}")
    click.echo(f"  Parallel processing: {config.cli['parallel']}")

def main():
    """Main entry point."""
    cli(obj={})

if __name__ == '__main__':
    main()
```

## Step 2: Analysis Commands

### 2.1 Create Analysis Commands
Create `src/cli/commands/analyze_commands.py`:

```python
"""Analysis CLI commands."""

import click
import json
from pathlib import Path
from typing import Optional, List
import time

from src.analysis.enhanced_analyzer import EnhancedAnalyzer
from src.analysis.ai_enricher import AIEnricher

@click.group(name='analyze')
def analyze_group():
    """Music analysis commands."""
    pass

@analyze_group.command('track')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--use-ai/--no-ai', default=True, help='Enable AI enrichment')
@click.option('--provider', type=click.Choice(['auto', 'openai', 'anthropic', 'gemini']), 
              default='auto', help='AI provider')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--format', type=click.Choice(['json', 'csv', 'text']), 
              default='json', help='Output format')
@click.pass_context
def analyze_track(ctx, file_path: str, use_ai: bool, provider: str, 
                  output: Optional[str], format: str):
    """Analyze a single audio track."""
    click.echo(f"Analyzing: {file_path}")
    
    # Create analyzer
    analyzer = EnhancedAnalyzer(ctx.obj['config'])
    
    # Perform analysis
    start_time = time.time()
    result = analyzer.analyze_track(
        file_path,
        use_ai=use_ai,
        ai_provider=provider if provider != 'auto' else None,
        store_results=True
    )
    
    # Display results
    click.echo(f"Analysis complete in {result.processing_time:.2f}s")
    click.echo(f"  BPM: {result.audio_features.get('bpm', 0):.1f}")
    click.echo(f"  Key: {result.audio_features.get('key', 'Unknown')}")
    click.echo(f"  Energy: {result.audio_features.get('energy', 0):.2f}")
    click.echo(f"  Confidence: {result.confidence:.2f}")
    
    if result.ai_analysis and result.ai_analysis.get('success'):
        click.echo(f"  Genre: {result.ai_analysis.get('genre', 'Unknown')}")
        click.echo(f"  Mood: {result.ai_analysis.get('mood', 'Unknown')}")
        click.echo(f"  Tags: {', '.join(result.ai_analysis.get('tags', []))}")
    
    # Save results if requested
    if output:
        save_results(result, output, format)
        click.echo(f"Results saved to: {output}")

@analyze_group.command('library')
@click.argument('directory', type=click.Path(exists=True))
@click.option('--use-ai/--no-ai', default=False, help='Enable AI enrichment')
@click.option('--parallel/--sequential', default=True, help='Parallel processing')
@click.option('--workers', default=4, help='Number of parallel workers')
@click.option('--recursive/--no-recursive', default=True, help='Scan subdirectories')
@click.option('--extensions', default='.mp3,.wav,.flac', help='File extensions to analyze')
@click.pass_context
def analyze_library(ctx, directory: str, use_ai: bool, parallel: bool,
                   workers: int, recursive: bool, extensions: str):
    """Analyze entire music library."""
    click.echo(f"Analyzing library: {directory}")
    
    # Find audio files
    ext_list = extensions.split(',')
    audio_files = find_audio_files(directory, ext_list, recursive)
    click.echo(f"Found {len(audio_files)} audio files")
    
    if not audio_files:
        click.echo("No audio files found")
        return
    
    # Create analyzer
    analyzer = EnhancedAnalyzer(ctx.obj['config'])
    
    # Analyze library
    with click.progressbar(audio_files, label='Analyzing tracks') as files:
        results = []
        for file_path in files:
            try:
                result = analyzer.analyze_track(
                    str(file_path),
                    use_ai=use_ai,
                    store_results=True
                )
                results.append(result)
            except Exception as e:
                click.echo(f"Error analyzing {file_path}: {e}", err=True)
    
    # Summary
    click.echo(f"\nAnalysis complete:")
    click.echo(f"  Successful: {len([r for r in results if r.confidence > 0])}")
    click.echo(f"  Failed: {len([r for r in results if r.confidence == 0])}")
    
    # Calculate average metrics
    if results:
        avg_bpm = sum(r.audio_features.get('bpm', 0) for r in results) / len(results)
        avg_energy = sum(r.audio_features.get('energy', 0) for r in results) / len(results)
        click.echo(f"  Average BPM: {avg_bpm:.1f}")
        click.echo(f"  Average Energy: {avg_energy:.2f}")

def find_audio_files(directory: str, extensions: List[str], 
                    recursive: bool) -> List[Path]:
    """Find audio files in directory."""
    path = Path(directory)
    files = []
    
    if recursive:
        for ext in extensions:
            files.extend(path.rglob(f"*{ext}"))
    else:
        for ext in extensions:
            files.extend(path.glob(f"*{ext}"))
    
    return sorted(files)

def save_results(result, output_path: str, format: str):
    """Save analysis results to file."""
    data = {
        'file_path': result.file_path,
        'audio_features': result.audio_features,
        'hamms_vector': result.hamms_vector.tolist(),
        'hamms_dimensions': result.hamms_dimensions,
        'confidence': result.confidence,
        'ai_analysis': result.ai_analysis,
        'processing_time': result.processing_time
    }
    
    if format == 'json':
        Path(output_path).write_text(json.dumps(data, indent=2))
    elif format == 'csv':
        # Simplified CSV output
        import csv
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['file', 'bpm', 'key', 'energy', 'confidence'])
            writer.writerow([
                result.file_path,
                result.audio_features.get('bpm', 0),
                result.audio_features.get('key', ''),
                result.audio_features.get('energy', 0),
                result.confidence
            ])
    else:
        # Text format
        text = f"File: {result.file_path}\n"
        text += f"BPM: {result.audio_features.get('bpm', 0):.1f}\n"
        text += f"Key: {result.audio_features.get('key', '')}\n"
        text += f"Energy: {result.audio_features.get('energy', 0):.2f}\n"
        text += f"Confidence: {result.confidence:.2f}\n"
        Path(output_path).write_text(text)
```

## Step 3: Playlist Commands

### 3.1 Create Playlist Commands
Create `src/cli/commands/playlist_commands.py`:

```python
"""Playlist generation CLI commands."""

import click
import json
from pathlib import Path
from typing import Optional

from src.services.storage_service import StorageService
from src.analysis.hamms_v3 import HAMMSAnalyzer

@click.group(name='playlist')
def playlist_group():
    """Playlist generation commands."""
    pass

@playlist_group.command('generate')
@click.option('--seed', required=True, help='Seed track file path')
@click.option('--size', default=20, help='Number of tracks')
@click.option('--threshold', default=0.7, help='Similarity threshold (0-1)')
@click.option('--harmonic/--no-harmonic', default=True, help='Enable harmonic mixing')
@click.option('--output', '-o', help='Output playlist file')
@click.option('--format', type=click.Choice(['m3u', 'json', 'text']), default='m3u')
def generate_playlist(seed: str, size: int, threshold: float, 
                     harmonic: bool, output: Optional[str], format: str):
    """Generate playlist from seed track."""
    click.echo(f"Generating playlist from: {seed}")
    
    # Get seed track analysis
    storage = StorageService()
    seed_data = storage.get_track_by_path(seed)
    
    if not seed_data:
        click.echo("Seed track not found in database. Please analyze it first.", err=True)
        return
    
    # Find similar tracks
    similar = storage.get_similar_tracks(
        seed_data['id'],
        threshold=threshold,
        limit=size
    )
    
    if not similar:
        click.echo("No similar tracks found. Try lowering the threshold.", err=True)
        return
    
    click.echo(f"Found {len(similar)} compatible tracks")
    
    # Build playlist
    playlist = []
    for track_id, similarity in similar:
        track = storage.get_analysis_by_track(track_id)
        if track:
            playlist.append({
                'file_path': track['file_path'],
                'title': track['title'],
                'artist': track['artist'],
                'similarity': similarity,
                'bpm': track['analysis'].get('bpm') if track.get('analysis') else None,
                'key': track['analysis'].get('key') if track.get('analysis') else None
            })
    
    # Sort by similarity
    playlist.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Display playlist
    click.echo("\nGenerated Playlist:")
    for i, track in enumerate(playlist, 1):
        click.echo(f"{i:2d}. {track['title']} - {track['artist']} "
                  f"(Similarity: {track['similarity']:.2f})")
    
    # Save if requested
    if output:
        save_playlist(playlist, output, format)
        click.echo(f"\nPlaylist saved to: {output}")

@playlist_group.command('optimize')
@click.argument('playlist_file', type=click.Path(exists=True))
@click.option('--energy-curve', type=click.Choice(['flat', 'rising', 'peak', 'wave']),
              default='rising', help='Energy progression curve')
@click.option('--output', '-o', help='Output optimized playlist')
def optimize_playlist(playlist_file: str, energy_curve: str, output: Optional[str]):
    """Optimize playlist order for better flow."""
    click.echo(f"Optimizing playlist: {playlist_file}")
    
    # Load playlist
    playlist = load_playlist(playlist_file)
    
    if not playlist:
        click.echo("Failed to load playlist", err=True)
        return
    
    # Optimize order based on energy curve
    optimized = optimize_track_order(playlist, energy_curve)
    
    # Display optimized order
    click.echo(f"\nOptimized for {energy_curve} energy curve:")
    for i, track in enumerate(optimized, 1):
        click.echo(f"{i:2d}. {track.get('title', Path(track['file_path']).stem)}")
    
    # Save if requested
    if output:
        save_playlist(optimized, output, 'm3u')
        click.echo(f"\nOptimized playlist saved to: {output}")

def save_playlist(playlist, output_path: str, format: str):
    """Save playlist to file."""
    if format == 'm3u':
        lines = ['#EXTM3U\n']
        for track in playlist:
            lines.append(f"#EXTINF:-1,{track.get('title', '')} - {track.get('artist', '')}\n")
            lines.append(f"{track['file_path']}\n")
        Path(output_path).write_text(''.join(lines))
    
    elif format == 'json':
        Path(output_path).write_text(json.dumps(playlist, indent=2))
    
    else:  # text
        lines = []
        for i, track in enumerate(playlist, 1):
            lines.append(f"{i}. {track['file_path']}\n")
        Path(output_path).write_text(''.join(lines))

def load_playlist(file_path: str):
    """Load playlist from file."""
    # Simplified loader - would be more robust in production
    playlist = []
    
    if file_path.endswith('.json'):
        playlist = json.loads(Path(file_path).read_text())
    elif file_path.endswith('.m3u'):
        lines = Path(file_path).read_text().split('\n')
        for line in lines:
            if line and not line.startswith('#'):
                playlist.append({'file_path': line})
    
    return playlist

def optimize_track_order(playlist, energy_curve: str):
    """Optimize track order based on energy curve."""
    # Simplified optimization
    if energy_curve == 'rising':
        # Sort by increasing energy
        return sorted(playlist, key=lambda x: x.get('energy', 0.5))
    elif energy_curve == 'peak':
        # Build to peak in middle
        sorted_tracks = sorted(playlist, key=lambda x: x.get('energy', 0.5))
        mid = len(sorted_tracks) // 2
        return sorted_tracks[:mid] + sorted_tracks[mid:][::-1]
    else:
        return playlist
```

## Step 4: Provider Management Commands

### 4.1 Create Provider Commands
Create `src/cli/commands/provider_commands.py`:

```python
"""Provider management CLI commands."""

import click
import json
from typing import Optional

from src.analysis.providers.provider_manager import get_provider_manager, SelectionStrategy

@click.group(name='provider')
def provider_group():
    """LLM provider management commands."""
    pass

@provider_group.command('list')
def list_providers():
    """List available LLM providers."""
    manager = get_provider_manager()
    stats = manager.get_provider_statistics()
    
    click.echo("Available LLM Providers:")
    click.echo("=" * 50)
    
    for provider_name, metrics in stats['providers'].items():
        click.echo(f"\n{provider_name}:")
        click.echo(f"  Status: {metrics['status']}")
        click.echo(f"  Requests: {metrics['request_count']}")
        click.echo(f"  Errors: {metrics['error_count']}")
        click.echo(f"  Total cost: ${metrics['total_cost']:.4f}")
        click.echo(f"  Avg tokens: {metrics['average_tokens']:.0f}")

@provider_group.command('test')
@click.option('--provider', required=True, help='Provider name to test')
def test_provider(provider: str):
    """Test a specific provider."""
    click.echo(f"Testing provider: {provider}")
    
    manager = get_provider_manager()
    
    # Test with sample data
    test_data = {
        'title': 'Test Track',
        'bpm': 128,
        'key': 'Am',
        'energy': 0.7
    }
    
    from src.analysis.providers.provider_manager import ProviderPreferences
    prefs = ProviderPreferences(
        preferred_providers=[provider],
        enable_fallback=False
    )
    
    response = manager.analyze(test_data, prefs)
    
    if response.success:
        click.echo("✓ Provider test successful")
        click.echo(f"  Model: {response.model}")
        click.echo(f"  Genre: {response.genre}")
        click.echo(f"  Confidence: {response.confidence:.2f}")
        click.echo(f"  Processing time: {response.processing_time:.2f}s")
        click.echo(f"  Cost: ${response.cost:.6f}")
    else:
        click.echo(f"✗ Provider test failed: {response.error}", err=True)

@provider_group.command('configure')
@click.option('--provider', required=True, help='Provider name')
@click.option('--api-key', help='API key')
@click.option('--model', help='Model name')
@click.option('--enable/--disable', default=True, help='Enable/disable provider')
def configure_provider(provider: str, api_key: Optional[str], 
                      model: Optional[str], enable: bool):
    """Configure a provider."""
    from src.config import get_config
    
    config = get_config()
    
    if provider not in config.providers:
        click.echo(f"Unknown provider: {provider}", err=True)
        return
    
    provider_config = config.providers[provider]
    
    if api_key:
        provider_config.api_key = api_key
        click.echo(f"Updated API key for {provider}")
    
    if model:
        provider_config.model = model
        click.echo(f"Updated model for {provider}: {model}")
    
    provider_config.enabled = enable
    click.echo(f"Provider {provider} {'enabled' if enable else 'disabled'}")
    
    # Save configuration
    config.save('config/map4.yaml')
    click.echo("Configuration saved")

@provider_group.command('benchmark')
@click.option('--test-file', required=True, help='Test audio file')
@click.option('--iterations', default=3, help='Test iterations per provider')
def benchmark_providers(test_file: str, iterations: int):
    """Benchmark all providers."""
    click.echo(f"Benchmarking providers with {iterations} iterations each")
    
    from src.lib.audio_processing import get_audio_processor
    
    # Analyze test file
    processor = get_audio_processor()
    audio_data = processor.analyze_track(test_file)
    
    if not audio_data.get('success'):
        click.echo("Failed to analyze test file", err=True)
        return
    
    manager = get_provider_manager()
    results = {}
    
    # Test each provider
    for provider_name in ['openai', 'anthropic', 'gemini']:
        click.echo(f"\nTesting {provider_name}...")
        
        times = []
        costs = []
        successes = 0
        
        for i in range(iterations):
            from src.analysis.providers.provider_manager import ProviderPreferences
            prefs = ProviderPreferences(
                preferred_providers=[provider_name],
                enable_fallback=False
            )
            
            response = manager.analyze(audio_data, prefs)
            
            if response.success:
                successes += 1
                times.append(response.processing_time)
                costs.append(response.cost)
        
        if times:
            results[provider_name] = {
                'success_rate': successes / iterations,
                'avg_time': sum(times) / len(times),
                'avg_cost': sum(costs) / len(costs)
            }
    
    # Display results
    click.echo("\nBenchmark Results:")
    click.echo("=" * 50)
    
    for provider, metrics in results.items():
        click.echo(f"\n{provider}:")
        click.echo(f"  Success rate: {metrics['success_rate']:.0%}")
        click.echo(f"  Avg time: {metrics['avg_time']:.2f}s")
        click.echo(f"  Avg cost: ${metrics['avg_cost']:.6f}")
```

## Step 5: Library Management Commands

### 5.1 Create Library Commands
Create `src/cli/commands/library_commands.py`:

```python
"""Library management CLI commands."""

import click
from typing import Optional

from src.services.storage_service import StorageService

@click.group(name='library')
def library_group():
    """Music library management commands."""
    pass

@library_group.command('stats')
def library_stats():
    """Show library statistics."""
    storage = StorageService()
    stats = storage.get_statistics()
    
    click.echo("Library Statistics")
    click.echo("=" * 50)
    click.echo(f"Total tracks: {stats['total_tracks']}")
    click.echo(f"Analyzed tracks: {stats['analyzed_tracks']}")
    click.echo(f"HAMMS vectors: {stats['total_hamms_vectors']}")
    click.echo(f"AI analyses: {stats['total_ai_analyses']}")
    
    if stats.get('genre_distribution'):
        click.echo("\nGenre Distribution:")
        for genre, count in sorted(stats['genre_distribution'].items(), 
                                  key=lambda x: x[1], reverse=True)[:10]:
            click.echo(f"  {genre}: {count}")

@library_group.command('search')
@click.option('--query', '-q', required=True, help='Search query')
@click.option('--field', type=click.Choice(['all', 'title', 'artist', 'genre']), 
              default='all', help='Search field')
@click.option('--limit', default=20, help='Maximum results')
def search_library(query: str, field: str, limit: int):
    """Search music library."""
    storage = StorageService()
    
    # Perform search (simplified)
    if field == 'genre':
        results = storage.get_tracks_by_genre(query, limit)
    else:
        # Would implement full text search in production
        results = []
    
    if not results:
        click.echo("No results found")
        return
    
    click.echo(f"Found {len(results)} results:")
    for i, track in enumerate(results, 1):
        click.echo(f"{i:2d}. {track['title']} - {track['artist']} ({track['genre']})")

@library_group.command('export')
@click.option('--output', '-o', required=True, help='Output file')
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx']), 
              default='json', help='Export format')
@click.option('--analyzed-only/--all', default=True, help='Export only analyzed tracks')
def export_library(output: str, format: str, analyzed_only: bool):
    """Export library data."""
    storage = StorageService()
    
    click.echo(f"Exporting library to {output}")
    
    # Get all tracks
    with storage.session() as session:
        from src.models.database import TrackORM
        
        query = session.query(TrackORM)
        if analyzed_only:
            query = query.filter(TrackORM.analyzed_at.isnot(None))
        
        tracks = query.all()
    
    click.echo(f"Exporting {len(tracks)} tracks")
    
    # Export based on format
    if format == 'json':
        import json
        data = []
        for track in tracks:
            data.append({
                'id': track.id,
                'file_path': track.file_path,
                'title': track.title,
                'artist': track.artist,
                'genre': track.genre,
                'duration': track.duration
            })
        
        from pathlib import Path
        Path(output).write_text(json.dumps(data, indent=2))
    
    elif format == 'csv':
        import csv
        with open(output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'File', 'Title', 'Artist', 'Genre', 'Duration'])
            for track in tracks:
                writer.writerow([
                    track.id, track.file_path, track.title,
                    track.artist, track.genre, track.duration
                ])
    
    click.echo(f"Export complete: {output}")

@library_group.command('cleanup')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted')
@click.confirmation_option(prompt='Are you sure you want to cleanup the library?')
def cleanup_library(dry_run: bool):
    """Remove orphaned database entries."""
    storage = StorageService()
    
    click.echo("Scanning for orphaned entries...")
    
    # Find tracks with missing files
    orphaned = []
    with storage.session() as session:
        from src.models.database import TrackORM
        from pathlib import Path
        
        tracks = session.query(TrackORM).all()
        for track in tracks:
            if not Path(track.file_path).exists():
                orphaned.append(track)
    
    click.echo(f"Found {len(orphaned)} orphaned entries")
    
    if orphaned and not dry_run:
        click.echo("Removing orphaned entries...")
        with storage.session() as session:
            for track in orphaned:
                session.delete(track)
        click.echo("Cleanup complete")
    elif dry_run:
        click.echo("Dry run - no changes made")
```

## Success Criteria

The CLI system is complete when:

1. **Unified Entry Point**: Single `map4` command with subcommands
2. **Analysis Commands**: Track and library analysis with options
3. **Playlist Commands**: Generation and optimization
4. **Provider Commands**: Management and benchmarking
5. **Library Commands**: Search, export, and maintenance
6. **BMAD Commands**: All BMAD modes accessible
7. **Progress Tracking**: Visual progress bars for long operations
8. **Configuration**: CLI-specific settings and options

## Usage Examples

```bash
# Analyze single track
map4 analyze track song.mp3 --use-ai --provider openai

# Analyze library
map4 analyze library /music --parallel --workers 8

# Generate playlist
map4 playlist generate --seed favorite.mp3 --size 30

# Run BMAD certification
map4 bmad certify --test-dir ./test --reference-dir ./reference

# Manage providers
map4 provider list
map4 provider test --provider anthropic

# Library operations
map4 library stats
map4 library search -q "house" --field genre
map4 library export -o library.json --format json
```

## Next Steps

1. Add integration and testing (see `07-integration-testing.md`)

The CLI system provides comprehensive command-line access to all MAP4 functionality.