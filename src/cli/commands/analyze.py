"""Analyze command module for MAP4 CLI.

This module provides commands for analyzing music files and libraries.
"""

import os
import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.services.enhanced_analyzer import EnhancedAnalyzer, EnhancedAnalysisResult
from src.services.storage import Storage
from src.services.metadata_writer import metadata_writer
from src.analysis.multi_llm_enricher import is_multi_llm_available
from src.analysis.provider_factory import LLMProviderFactory, get_provider


@click.group(name='analyze')
def analyze_group():
    """Music analysis commands."""
    pass


@analyze_group.command(name='track')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--provider', default='zai', help='LLM provider to use')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['json', 'csv', 'text']), 
              default='json', help='Output format')
@click.option('--write-metadata', is_flag=True, help='Write metadata to audio file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def analyze_track(ctx, file_path: str, provider: str, output: Optional[str], 
                  output_format: str, write_metadata: bool, verbose: bool):
    """Analyze a single music track.
    
    Example:
        map4 analyze track song.mp3 --provider claude --output analysis.json
    """
    file_path = Path(file_path).resolve()
    
    if verbose:
        click.echo(f"Analyzing: {file_path}")
        click.echo(f"Provider: {provider}")
    
    # Initialize storage and analyzer
    storage = Storage.from_path("data/music.db")
    analyzer = EnhancedAnalyzer(storage, enable_ai=True, skip_validation=True)
    
    try:
        # Perform analysis
        result = analyzer.analyze_file(str(file_path))
        
        if result:
            # Format output
            if output_format == 'json':
                output_data = json.dumps(result.to_dict(), indent=2)
            elif output_format == 'csv':
                output_data = _format_as_csv([result.to_dict()])
            else:  # text
                output_data = _format_as_text(result.to_dict())
            
            # Write output
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                click.echo(f"✓ Analysis saved to: {output}")
            else:
                click.echo(output_data)
            
            # Write metadata if requested
            if write_metadata and result.ai_analysis:
                metadata_writer.write(str(file_path), result.ai_analysis)
                click.echo(f"✓ Metadata written to: {file_path}")
            
            click.echo(f"✓ Analysis complete for: {file_path.name}")
        else:
            click.echo(f"✗ Analysis failed for: {file_path}", err=True)
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"Error analyzing track: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        ctx.exit(1)


@analyze_group.command(name='library')
@click.argument('folder_path', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, default=True, help='Scan recursively')
@click.option('--formats', '-f', multiple=True, default=['mp3', 'flac', 'wav', 'm4a'], 
              help='File formats to analyze')
@click.option('--provider', default='zai', help='LLM provider to use')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['json', 'csv']), 
              default='json', help='Output format')
@click.option('--write-metadata', is_flag=True, help='Write metadata to audio files')
@click.option('--force', is_flag=True, help='Force reanalysis of all files')
@click.option('--batch-size', default=10, help='Batch size for processing')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def analyze_library(ctx, folder_path: str, recursive: bool, formats: tuple, 
                    provider: str, output: Optional[str], output_format: str,
                    write_metadata: bool, force: bool, batch_size: int, verbose: bool):
    """Analyze an entire music library.
    
    Example:
        map4 analyze library ~/Music --recursive --formats mp3 flac --output library.json
    """
    folder_path = Path(folder_path).resolve()
    
    click.echo(f"Analyzing library: {folder_path}")
    click.echo(f"Recursive: {recursive}")
    click.echo(f"Formats: {', '.join(formats)}")
    click.echo(f"Provider: {provider}")
    
    # Find audio files
    audio_files = _find_audio_files(folder_path, recursive, formats, verbose)
    
    if not audio_files:
        click.echo("No audio files found", err=True)
        ctx.exit(1)
    
    click.echo(f"Found {len(audio_files)} files to analyze")
    
    # Initialize storage and analyzer
    storage = Storage.from_path("data/music.db")
    analyzer = EnhancedAnalyzer(storage, enable_ai=True, skip_validation=True)
    
    results = []
    errors = []
    
    # Process files with progress bar
    with click.progressbar(audio_files, label='Analyzing files') as files:
        for file_path in files:
            try:
                # Check if already analyzed (unless force flag)
                if not force and storage.get_track_by_path(str(file_path)):
                    if verbose:
                        click.echo(f"Skipping (already analyzed): {file_path.name}")
                    continue
                
                # Analyze file
                result = analyzer.analyze_file(str(file_path))
                
                if result:
                    results.append(result.to_dict())
                    
                    # Write metadata if requested
                    if write_metadata and result.ai_analysis:
                        metadata_writer.write(str(file_path), result.ai_analysis)
                else:
                    errors.append(str(file_path))
                    
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")
                if verbose:
                    click.echo(f"Error: {e}", err=True)
    
    # Summary
    click.echo(f"\n=== Analysis Complete ===")
    click.echo(f"✓ Successful: {len(results)}")
    click.echo(f"✗ Errors: {len(errors)}")
    
    # Save results
    if output and results:
        if output_format == 'json':
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
        else:  # csv
            _save_as_csv(results, output)
        
        click.echo(f"✓ Results saved to: {output}")
    
    # Show errors if any
    if errors and verbose:
        click.echo("\nErrors encountered:")
        for error in errors[:10]:  # Show first 10 errors
            click.echo(f"  - {error}")
        if len(errors) > 10:
            click.echo(f"  ... and {len(errors) - 10} more")


@analyze_group.command(name='playlist')
@click.argument('playlist_file', type=click.Path(exists=True))
@click.option('--provider', default='zai', help='LLM provider to use')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), 
              default='json', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def analyze_playlist(ctx, playlist_file: str, provider: str, output: Optional[str],
                    output_format: str, verbose: bool):
    """Analyze a playlist file (.m3u, .pls, etc).
    
    Example:
        map4 analyze playlist my_playlist.m3u --provider gemini --output analysis.json
    """
    playlist_path = Path(playlist_file).resolve()
    
    if verbose:
        click.echo(f"Analyzing playlist: {playlist_path}")
        click.echo(f"Provider: {provider}")
    
    # Parse playlist
    tracks = _parse_playlist(playlist_path)
    
    if not tracks:
        click.echo("No valid tracks found in playlist", err=True)
        ctx.exit(1)
    
    click.echo(f"Found {len(tracks)} tracks in playlist")
    
    # Initialize provider
    try:
        llm_provider = get_provider(provider)
    except Exception as e:
        click.echo(f"Failed to initialize provider: {e}", err=True)
        ctx.exit(1)
    
    # Analyze playlist as a whole
    playlist_metadata = {
        'name': playlist_path.stem,
        'file': str(playlist_path),
        'tracks': tracks
    }
    
    try:
        result = llm_provider.analyze_playlist(playlist_metadata)
        
        # Format output
        if output_format == 'json':
            output_data = json.dumps(result, indent=2)
        else:  # text
            output_data = _format_playlist_as_text(result)
        
        # Write output
        if output:
            with open(output, 'w') as f:
                f.write(output_data)
            click.echo(f"✓ Analysis saved to: {output}")
        else:
            click.echo(output_data)
        
        click.echo(f"✓ Playlist analysis complete")
        
    except Exception as e:
        click.echo(f"Error analyzing playlist: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        ctx.exit(1)


# Helper functions
def _find_audio_files(folder_path: Path, recursive: bool, 
                     formats: tuple, verbose: bool) -> List[Path]:
    """Find audio files in folder."""
    supported_formats = {f'.{fmt.lower()}' for fmt in formats}
    audio_files = []
    
    pattern = "**/*" if recursive else "*"
    
    for file_path in folder_path.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            audio_files.append(file_path)
    
    return sorted(audio_files)


def _format_as_text(data: Dict[str, Any]) -> str:
    """Format analysis result as text."""
    lines = []
    lines.append("=== Track Analysis ===")
    lines.append(f"Title: {data.get('title', 'Unknown')}")
    lines.append(f"Artist: {data.get('artist', 'Unknown')}")
    lines.append(f"Album: {data.get('album', 'Unknown')}")
    lines.append(f"Duration: {data.get('duration', 'Unknown')}")
    
    if 'ai_analysis' in data and data['ai_analysis']:
        ai = data['ai_analysis']
        lines.append("\n=== AI Analysis ===")
        lines.append(f"Genre: {ai.get('genre', 'Unknown')}")
        lines.append(f"Mood: {ai.get('mood', 'Unknown')}")
        lines.append(f"Key: {ai.get('key', 'Unknown')}")
        lines.append(f"BPM: {ai.get('bpm', 'Unknown')}")
        
        if 'themes' in ai:
            lines.append(f"Themes: {', '.join(ai['themes'])}")
    
    return '\n'.join(lines)


def _format_as_csv(data: List[Dict[str, Any]]) -> str:
    """Format analysis results as CSV."""
    import io
    
    if not data:
        return ""
    
    output = io.StringIO()
    fieldnames = ['title', 'artist', 'album', 'duration', 'genre', 'mood', 'key', 'bpm']
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for item in data:
        row = {
            'title': item.get('title', ''),
            'artist': item.get('artist', ''),
            'album': item.get('album', ''),
            'duration': item.get('duration', '')
        }
        
        if 'ai_analysis' in item and item['ai_analysis']:
            ai = item['ai_analysis']
            row.update({
                'genre': ai.get('genre', ''),
                'mood': ai.get('mood', ''),
                'key': ai.get('key', ''),
                'bpm': ai.get('bpm', '')
            })
        
        writer.writerow(row)
    
    return output.getvalue()


def _save_as_csv(data: List[Dict[str, Any]], output_path: str):
    """Save analysis results as CSV file."""
    csv_content = _format_as_csv(data)
    with open(output_path, 'w') as f:
        f.write(csv_content)


def _parse_playlist(playlist_path: Path) -> List[Dict[str, Any]]:
    """Parse playlist file and extract track information."""
    tracks = []
    
    with open(playlist_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Simple M3U parser
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # This is a file path
            track_path = Path(line)
            if track_path.exists():
                tracks.append({
                    'file_path': str(track_path),
                    'filename': track_path.name
                })
    
    return tracks


def _format_playlist_as_text(data: Dict[str, Any]) -> str:
    """Format playlist analysis as text."""
    lines = []
    lines.append("=== Playlist Analysis ===")
    lines.append(f"Name: {data.get('name', 'Unknown')}")
    lines.append(f"Total Tracks: {len(data.get('tracks', []))}")
    
    if 'analysis' in data:
        analysis = data['analysis']
        lines.append("\n=== Overall Analysis ===")
        for key, value in analysis.items():
            if key != 'tracks':
                lines.append(f"{key}: {value}")
    
    return '\n'.join(lines)