#!/usr/bin/env python3
"""
Test script for DJ metadata extraction from Serato and Mixed In Key.
Run this on your music files to test the new functionality.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.metadata import extract_precomputed_metadata
from src.models.dj_metadata import DJMetadata, CueType


def test_file(file_path: str):
    """Test metadata extraction on a single file."""
    print(f"\n{'='*60}")
    print(f"Testing: {os.path.basename(file_path)}")
    print(f"{'='*60}")

    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return

    # Extract metadata
    metadata = extract_precomputed_metadata(file_path)

    if not metadata:
        print("No metadata extracted (is mutagen installed?)")
        return

    # Display basic metadata
    print("\n📊 BASIC METADATA:")
    print(f"  BPM: {metadata.get('bpm', 'Not found')}")
    print(f"  Key: {metadata.get('initial_key', 'Not found')}")
    print(f"  Camelot: {metadata.get('camelot_key', 'Not found')}")
    print(f"  Energy: {metadata.get('energy_level', 'Not found')}")
    print(f"  Mood: {metadata.get('mood', 'Not found')}")
    print(f"  Danceability: {metadata.get('danceability', 'Not found')}")
    print(f"  Analysis Source: {metadata.get('analysis_source', 'Unknown')}")

    # Display beatgrid if present
    if 'beatgrid' in metadata:
        beatgrid = metadata['beatgrid']
        print("\n🎵 BEATGRID:")
        print(f"  BPM: {beatgrid.bpm if hasattr(beatgrid, 'bpm') else 'N/A'}")
        print(f"  Time Signature: {beatgrid.time_signature if hasattr(beatgrid, 'time_signature') else '4/4'}")
        print(f"  First Beat: {beatgrid.first_beat_position if hasattr(beatgrid, 'first_beat_position') else 'N/A'}s")

        # Show downbeats (bar starts)
        if hasattr(beatgrid, 'first_downbeat_position'):
            print(f"  First Downbeat: {beatgrid.first_downbeat_position}s")

        if hasattr(beatgrid, 'downbeats') and beatgrid.downbeats:
            print(f"  \n  📍 DOWNBEATS (Bar starts): {len(beatgrid.downbeats)} bars")
            print(f"  First 8 bars at: {[f'{d:.2f}s' for d in beatgrid.downbeats[:8]]}")
        elif hasattr(beatgrid, 'beats') and beatgrid.beats:
            # Calculate downbeats from beats if not explicitly provided
            calculated_downbeats = [beatgrid.beats[i] for i in range(0, len(beatgrid.beats), 4)]
            print(f"  \n  📍 DOWNBEATS (Calculated): {len(calculated_downbeats)} bars")
            print(f"  First 8 bars at: {[f'{d:.2f}s' for d in calculated_downbeats[:8]]}")

        if hasattr(beatgrid, 'beats') and beatgrid.beats:
            print(f"  \n  Total Beats: {len(beatgrid.beats)}")
            print(f"  First 8 beats: {[f'{b:.3f}s' for b in beatgrid.beats[:8]]}")

        if hasattr(beatgrid, 'bars_count'):
            print(f"  Total Bars: {beatgrid.bars_count}")

    # Display cue points if present
    if 'cue_points' in metadata:
        cues = metadata['cue_points']
        print(f"\n🎯 CUE POINTS ({len(cues)} found):")
        for cue in cues[:8]:  # Show first 8
            if hasattr(cue, 'to_dict'):
                cue_dict = cue.to_dict()
            else:
                cue_dict = cue.__dict__ if hasattr(cue, '__dict__') else {}

            pos_ms = cue_dict.get('position_ms', 0)
            pos_sec = pos_ms / 1000 if pos_ms else 0
            name = cue_dict.get('name', '')
            cue_type = cue_dict.get('type', 'cue')
            index = cue_dict.get('index', '')
            color = cue_dict.get('color', '')

            print(f"    [{index}] {pos_sec:.2f}s - {cue_type} {name} {color}")

    # Display loops if present
    if 'loops' in metadata:
        loops = metadata['loops']
        print(f"\n🔄 LOOPS ({len(loops)} found):")
        for loop in loops[:5]:  # Show first 5
            if hasattr(loop, 'to_dict'):
                loop_dict = loop.to_dict()
            else:
                loop_dict = loop.__dict__ if hasattr(loop, '__dict__') else {}

            start_ms = loop_dict.get('start_position_ms', 0)
            end_ms = loop_dict.get('end_position_ms', 0)
            start_sec = start_ms / 1000 if start_ms else 0
            end_sec = end_ms / 1000 if end_ms else 0
            color = loop_dict.get('color', '')
            enabled = loop_dict.get('enabled', False)

            print(f"    {start_sec:.2f}s - {end_sec:.2f}s {'[ACTIVE]' if enabled else ''} {color}")

    # Display Serato-specific data
    if 'serato' in metadata:
        serato = metadata['serato']
        print("\n💿 SERATO DATA:")
        print(f"  Has Beatgrid: {'beatgrid' in serato}")
        print(f"  Has Cues: {'cues' in serato}")
        print(f"  Has Loops: {'loops' in serato}")
        print(f"  Has Autotags: {'autotags' in serato}")
        if 'autotags' in serato:
            print(f"    Auto BPM: {serato['autotags'].get('auto_bpm', 'N/A')}")
            print(f"    Auto Key: {serato['autotags'].get('auto_key', 'N/A')}")

    # Display Mixed In Key specific data
    if 'mixedinkey' in metadata:
        mik = metadata['mixedinkey']
        print("\n🎹 MIXED IN KEY DATA:")
        print(f"  Energy: {mik.get('energy', 'N/A')}")
        print(f"  Camelot: {mik.get('camelot', 'N/A')}")
        print(f"  Mood: {mik.get('mood', 'N/A')}")
        print(f"  Danceability: {mik.get('danceability', 'N/A')}")
        if 'compatible_keys' in mik:
            print(f"  Compatible Keys: {', '.join(mik['compatible_keys'])}")
        if 'cues' in mik:
            print(f"  MIK Cues: {len(mik['cues'])} points")

    # Display raw comment if it contains DJ info
    if 'comment' in metadata:
        comment = metadata['comment']
        if any(keyword in comment.lower() for keyword in ['energy', 'cue', 'intro', 'outro', 'drop']):
            print(f"\n📝 COMMENT (DJ Info):")
            print(f"  {comment[:200]}...")


def test_directory(directory: str):
    """Test all audio files in a directory."""
    audio_extensions = {'.mp3', '.m4a', '.flac', '.wav', '.aiff', '.mp4'}

    files_found = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in audio_extensions:
                files_found.append(os.path.join(root, file))

    if not files_found:
        print(f"No audio files found in {directory}")
        return

    print(f"\nFound {len(files_found)} audio files")
    print(f"Testing first 5 files...\n")

    for file_path in files_found[:5]:
        try:
            test_file(file_path)
        except Exception as e:
            print(f"\nERROR processing {file_path}: {e}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python test_dj_metadata.py <audio_file_or_directory>")
        print("\nExample:")
        print("  python test_dj_metadata.py /path/to/music.mp3")
        print("  python test_dj_metadata.py /path/to/music/folder/")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isfile(path):
        test_file(path)
    elif os.path.isdir(path):
        test_directory(path)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()