"""Playlist command module for MAP4 CLI.

This module provides commands for playlist generation and management.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
from datetime import datetime
import random

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.services.storage import Storage
from src.services.enhanced_analyzer import EnhancedAnalyzer
from src.analysis.provider_factory import get_provider


@click.group(name='playlist')
def playlist_group():
    """Playlist generation and management commands."""
    pass


@playlist_group.command(name='create')
@click.option('--library', '-l', type=click.Path(exists=True), required=True,
              help='Path to music library')
@click.option('--name', '-n', default='Generated Playlist', help='Playlist name')
@click.option('--mood', help='Target mood (e.g., energetic, relaxing, melancholic)')
@click.option('--genre', help='Target genre (e.g., rock, jazz, electronic)')
@click.option('--duration', type=int, help='Target duration in minutes')
@click.option('--count', type=int, default=20, help='Number of tracks')
@click.option('--provider', default='zai', help='LLM provider to use')
@click.option('--output', '-o', type=click.Path(), help='Output playlist file')
@click.option('--format', 'output_format', type=click.Choice(['m3u', 'pls', 'json']), 
              default='m3u', help='Output format')
@click.option('--shuffle', is_flag=True, help='Shuffle the playlist')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def create_playlist(ctx, library: str, name: str, mood: Optional[str], 
                   genre: Optional[str], duration: Optional[int], count: int,
                   provider: str, output: Optional[str], output_format: str,
                   shuffle: bool, verbose: bool):
    """Create a new playlist based on criteria.
    
    Example:
        map4 playlist create --library ~/Music --mood energetic --count 25 --output workout.m3u
    """
    library_path = Path(library).resolve()
    
    click.echo(f"Creating playlist: {name}")
    click.echo(f"Library: {library_path}")
    
    if mood:
        click.echo(f"Mood: {mood}")
    if genre:
        click.echo(f"Genre: {genre}")
    if duration:
        click.echo(f"Target duration: {duration} minutes")
    
    # Initialize storage and analyzer
    storage = Storage.from_path("data/music.db")
    analyzer = EnhancedAnalyzer(storage, enable_ai=True, skip_validation=True)
    
    # Get all analyzed tracks from the library
    tracks = _get_library_tracks(library_path, storage, verbose)
    
    if not tracks:
        click.echo("No analyzed tracks found in library. Run 'map4 analyze library' first.", err=True)
        ctx.exit(1)
    
    click.echo(f"Found {len(tracks)} analyzed tracks")
    
    # Filter tracks based on criteria
    filtered_tracks = _filter_tracks(tracks, mood, genre, verbose)
    
    if not filtered_tracks:
        click.echo("No tracks match the specified criteria", err=True)
        ctx.exit(1)
    
    click.echo(f"Filtered to {len(filtered_tracks)} matching tracks")
    
    # Select tracks for playlist
    selected_tracks = _select_tracks(filtered_tracks, count, duration)
    
    if shuffle:
        random.shuffle(selected_tracks)
    
    click.echo(f"Selected {len(selected_tracks)} tracks for playlist")
    
    # Generate playlist
    playlist_data = {
        'name': name,
        'created': datetime.now().isoformat(),
        'criteria': {
            'mood': mood,
            'genre': genre,
            'duration': duration,
            'count': count
        },
        'tracks': selected_tracks,
        'total_duration': sum(t.get('duration', 0) for t in selected_tracks)
    }
    
    # Save playlist
    if output:
        output_path = Path(output)
    else:
        output_path = Path(f"{name.replace(' ', '_')}.{output_format}")
    
    if output_format == 'm3u':
        _save_as_m3u(playlist_data, output_path)
    elif output_format == 'pls':
        _save_as_pls(playlist_data, output_path)
    else:  # json
        with open(output_path, 'w') as f:
            json.dump(playlist_data, f, indent=2)
    
    click.echo(f"✓ Playlist saved to: {output_path}")
    
    # Show summary
    total_duration = playlist_data['total_duration']
    click.echo(f"\n=== Playlist Summary ===")
    click.echo(f"Tracks: {len(selected_tracks)}")
    click.echo(f"Duration: {int(total_duration // 60)}:{int(total_duration % 60):02d}")
    
    if verbose:
        click.echo("\nTracklist:")
        for i, track in enumerate(selected_tracks[:10], 1):
            click.echo(f"  {i}. {track.get('artist', 'Unknown')} - {track.get('title', 'Unknown')}")
        if len(selected_tracks) > 10:
            click.echo(f"  ... and {len(selected_tracks) - 10} more")


@playlist_group.command(name='optimize')
@click.argument('playlist_file', type=click.Path(exists=True))
@click.option('--provider', default='zai', help='LLM provider to use')
@click.option('--output', '-o', type=click.Path(), help='Output optimized playlist')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def optimize_playlist(ctx, playlist_file: str, provider: str, 
                     output: Optional[str], verbose: bool):
    """Optimize an existing playlist for better flow.
    
    Example:
        map4 playlist optimize my_playlist.m3u --output optimized.m3u
    """
    playlist_path = Path(playlist_file).resolve()
    
    click.echo(f"Optimizing playlist: {playlist_path}")
    click.echo(f"Provider: {provider}")
    
    # Parse existing playlist
    tracks = _parse_playlist_file(playlist_path)
    
    if not tracks:
        click.echo("No valid tracks found in playlist", err=True)
        ctx.exit(1)
    
    click.echo(f"Found {len(tracks)} tracks")
    
    # Initialize provider
    try:
        llm_provider = get_provider(provider)
    except Exception as e:
        click.echo(f"Failed to initialize provider: {e}", err=True)
        ctx.exit(1)
    
    # Analyze playlist for optimization
    playlist_metadata = {
        'name': playlist_path.stem,
        'tracks': tracks
    }
    
    try:
        # Get optimization suggestions
        analysis = llm_provider.analyze_playlist(playlist_metadata)
        
        # Reorder tracks based on analysis
        optimized_tracks = _optimize_track_order(tracks, analysis, verbose)
        
        # Save optimized playlist
        if output:
            output_path = Path(output)
        else:
            output_path = playlist_path.with_stem(f"{playlist_path.stem}_optimized")
        
        playlist_data = {
            'name': f"{playlist_path.stem} (Optimized)",
            'tracks': optimized_tracks
        }
        
        if output_path.suffix == '.m3u':
            _save_as_m3u(playlist_data, output_path)
        elif output_path.suffix == '.pls':
            _save_as_pls(playlist_data, output_path)
        else:
            with open(output_path, 'w') as f:
                json.dump(playlist_data, f, indent=2)
        
        click.echo(f"✓ Optimized playlist saved to: {output_path}")
        
        if 'analysis' in analysis and verbose:
            click.echo("\n=== Optimization Summary ===")
            for key, value in analysis['analysis'].items():
                if isinstance(value, (str, int, float)):
                    click.echo(f"{key}: {value}")
        
    except Exception as e:
        click.echo(f"Error optimizing playlist: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        ctx.exit(1)


@playlist_group.command(name='export')
@click.argument('playlist_file', type=click.Path(exists=True))
@click.option('--format', 'output_format', type=click.Choice(['m3u', 'pls', 'xspf', 'json']), 
              required=True, help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--absolute-paths', is_flag=True, help='Use absolute file paths')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def export_playlist(ctx, playlist_file: str, output_format: str, 
                   output: Optional[str], absolute_paths: bool, verbose: bool):
    """Export playlist to different formats.
    
    Example:
        map4 playlist export my_playlist.json --format m3u --output exported.m3u
    """
    playlist_path = Path(playlist_file).resolve()
    
    if verbose:
        click.echo(f"Exporting playlist: {playlist_path}")
        click.echo(f"Format: {output_format}")
    
    # Parse playlist
    if playlist_path.suffix == '.json':
        with open(playlist_path, 'r') as f:
            playlist_data = json.load(f)
    else:
        tracks = _parse_playlist_file(playlist_path)
        playlist_data = {
            'name': playlist_path.stem,
            'tracks': tracks
        }
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = playlist_path.with_suffix(f'.{output_format}')
    
    # Export in requested format
    if output_format == 'm3u':
        _save_as_m3u(playlist_data, output_path, absolute_paths)
    elif output_format == 'pls':
        _save_as_pls(playlist_data, output_path, absolute_paths)
    elif output_format == 'xspf':
        _save_as_xspf(playlist_data, output_path, absolute_paths)
    else:  # json
        with open(output_path, 'w') as f:
            json.dump(playlist_data, f, indent=2)
    
    click.echo(f"✓ Playlist exported to: {output_path}")


@playlist_group.command(name='merge')
@click.argument('playlist_files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--name', '-n', default='Merged Playlist', help='Name for merged playlist')
@click.option('--output', '-o', type=click.Path(), required=True, help='Output file path')
@click.option('--remove-duplicates', is_flag=True, help='Remove duplicate tracks')
@click.option('--shuffle', is_flag=True, help='Shuffle the merged playlist')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def merge_playlists(ctx, playlist_files: tuple, name: str, output: str,
                   remove_duplicates: bool, shuffle: bool, verbose: bool):
    """Merge multiple playlists into one.
    
    Example:
        map4 playlist merge playlist1.m3u playlist2.m3u --output merged.m3u
    """
    all_tracks = []
    
    for playlist_file in playlist_files:
        playlist_path = Path(playlist_file).resolve()
        
        if verbose:
            click.echo(f"Reading: {playlist_path}")
        
        tracks = _parse_playlist_file(playlist_path)
        all_tracks.extend(tracks)
    
    click.echo(f"Total tracks before merge: {len(all_tracks)}")
    
    # Remove duplicates if requested
    if remove_duplicates:
        seen = set()
        unique_tracks = []
        for track in all_tracks:
            track_id = track.get('file_path', track.get('filename', ''))
            if track_id not in seen:
                seen.add(track_id)
                unique_tracks.append(track)
        all_tracks = unique_tracks
        click.echo(f"Tracks after removing duplicates: {len(all_tracks)}")
    
    # Shuffle if requested
    if shuffle:
        random.shuffle(all_tracks)
    
    # Create merged playlist
    playlist_data = {
        'name': name,
        'created': datetime.now().isoformat(),
        'source_playlists': [str(p) for p in playlist_files],
        'tracks': all_tracks
    }
    
    # Save merged playlist
    output_path = Path(output)
    
    if output_path.suffix == '.m3u':
        _save_as_m3u(playlist_data, output_path)
    elif output_path.suffix == '.pls':
        _save_as_pls(playlist_data, output_path)
    else:
        with open(output_path, 'w') as f:
            json.dump(playlist_data, f, indent=2)
    
    click.echo(f"✓ Merged playlist saved to: {output_path}")
    click.echo(f"Final track count: {len(all_tracks)}")


# Helper functions
def _get_library_tracks(library_path: Path, storage: Storage, verbose: bool) -> List[Dict[str, Any]]:
    """Get all analyzed tracks from library."""
    tracks = []
    
    # Query storage for tracks in this library path
    all_tracks = storage.get_all_tracks()
    
    for track in all_tracks:
        if track and 'file_path' in track:
            track_path = Path(track['file_path'])
            if library_path in track_path.parents or track_path.parent == library_path:
                tracks.append(track)
    
    return tracks


def _filter_tracks(tracks: List[Dict[str, Any]], mood: Optional[str], 
                  genre: Optional[str], verbose: bool) -> List[Dict[str, Any]]:
    """Filter tracks based on criteria."""
    filtered = []
    
    for track in tracks:
        if 'ai_analysis' not in track or not track['ai_analysis']:
            continue
        
        ai = track['ai_analysis']
        
        # Check mood
        if mood and ai.get('mood', '').lower() != mood.lower():
            continue
        
        # Check genre
        if genre and genre.lower() not in ai.get('genre', '').lower():
            continue
        
        filtered.append(track)
    
    return filtered


def _select_tracks(tracks: List[Dict[str, Any]], count: int, 
                  duration: Optional[int]) -> List[Dict[str, Any]]:
    """Select tracks for playlist based on count and duration."""
    if duration:
        # Select tracks to match target duration
        target_seconds = duration * 60
        selected = []
        total_duration = 0
        
        for track in tracks:
            track_duration = track.get('duration', 0)
            if total_duration + track_duration <= target_seconds:
                selected.append(track)
                total_duration += track_duration
            
            if len(selected) >= count:
                break
        
        return selected
    else:
        # Just select by count
        return tracks[:count]


def _parse_playlist_file(playlist_path: Path) -> List[Dict[str, Any]]:
    """Parse a playlist file."""
    tracks = []
    
    if playlist_path.suffix == '.json':
        with open(playlist_path, 'r') as f:
            data = json.load(f)
            return data.get('tracks', [])
    
    # Parse M3U/PLS format
    with open(playlist_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('['):
            # This is a file path
            if line.startswith('File'):  # PLS format
                parts = line.split('=', 1)
                if len(parts) == 2:
                    line = parts[1]
            
            track_path = Path(line)
            tracks.append({
                'file_path': str(track_path),
                'filename': track_path.name
            })
    
    return tracks


def _optimize_track_order(tracks: List[Dict[str, Any]], 
                         analysis: Dict[str, Any], verbose: bool) -> List[Dict[str, Any]]:
    """Optimize track order based on analysis."""
    # Simple optimization: group by similar characteristics
    # In a real implementation, this would use the AI analysis
    
    # For now, just return tracks as-is
    # TODO: Implement sophisticated ordering based on energy flow, key compatibility, etc.
    return tracks


def _save_as_m3u(playlist_data: Dict[str, Any], output_path: Path, 
                absolute_paths: bool = False):
    """Save playlist as M3U file."""
    lines = ['#EXTM3U\n']
    lines.append(f'#PLAYLIST:{playlist_data.get("name", "Playlist")}\n')
    
    for track in playlist_data.get('tracks', []):
        # Add extended info if available
        duration = int(track.get('duration', -1))
        artist = track.get('artist', 'Unknown Artist')
        title = track.get('title', track.get('filename', 'Unknown'))
        lines.append(f'#EXTINF:{duration},{artist} - {title}\n')
        
        # Add file path
        file_path = track.get('file_path', '')
        if not absolute_paths:
            file_path = Path(file_path).name
        lines.append(f'{file_path}\n')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def _save_as_pls(playlist_data: Dict[str, Any], output_path: Path, 
                absolute_paths: bool = False):
    """Save playlist as PLS file."""
    lines = ['[playlist]\n']
    tracks = playlist_data.get('tracks', [])
    
    for i, track in enumerate(tracks, 1):
        file_path = track.get('file_path', '')
        if not absolute_paths:
            file_path = Path(file_path).name
        
        lines.append(f'File{i}={file_path}\n')
        
        title = track.get('title', track.get('filename', 'Unknown'))
        lines.append(f'Title{i}={title}\n')
        
        duration = int(track.get('duration', -1))
        lines.append(f'Length{i}={duration}\n')
    
    lines.append(f'NumberOfEntries={len(tracks)}\n')
    lines.append('Version=2\n')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def _save_as_xspf(playlist_data: Dict[str, Any], output_path: Path, 
                 absolute_paths: bool = False):
    """Save playlist as XSPF (XML Shareable Playlist Format) file."""
    from xml.etree import ElementTree as ET
    from xml.dom import minidom
    
    # Create root element
    playlist = ET.Element('playlist', version='1', xmlns='http://xspf.org/ns/0/')
    
    # Add title
    title = ET.SubElement(playlist, 'title')
    title.text = playlist_data.get('name', 'Playlist')
    
    # Add track list
    track_list = ET.SubElement(playlist, 'trackList')
    
    for track_data in playlist_data.get('tracks', []):
        track = ET.SubElement(track_list, 'track')
        
        # Add location
        location = ET.SubElement(track, 'location')
        file_path = track_data.get('file_path', '')
        if not absolute_paths:
            file_path = Path(file_path).name
        location.text = f'file://{file_path}'
        
        # Add title
        if 'title' in track_data:
            title_elem = ET.SubElement(track, 'title')
            title_elem.text = track_data['title']
        
        # Add artist/creator
        if 'artist' in track_data:
            creator = ET.SubElement(track, 'creator')
            creator.text = track_data['artist']
        
        # Add album
        if 'album' in track_data:
            album = ET.SubElement(track, 'album')
            album.text = track_data['album']
        
        # Add duration (in milliseconds)
        if 'duration' in track_data:
            duration = ET.SubElement(track, 'duration')
            duration.text = str(int(track_data['duration'] * 1000))
    
    # Pretty print XML
    xml_str = minidom.parseString(ET.tostring(playlist)).toprettyxml(indent='  ')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_str)