#!/usr/bin/env python3
"""
Test Music Structure Analysis
Analyzes and visualizes the structure of a track (intro, verse, chorus, drop, etc.)
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.structure_analyzer import StructureAnalyzer
from src.services.metadata import extract_precomputed_metadata
import json


def test_structure_analysis(audio_path: str):
    """Test structure analysis on an audio file."""

    print(f"\n{'='*80}")
    print(f"MUSIC STRUCTURE ANALYSIS: {os.path.basename(audio_path)}")
    print(f"{'='*80}")

    # Initialize analyzer
    analyzer = StructureAnalyzer(sr=22050, hop_length=512)

    # Get existing cue points from MIK/Serato if available
    print("\n📋 Checking for existing cue points...")
    metadata = extract_precomputed_metadata(audio_path)
    existing_cues = metadata.get('cue_points', [])

    if existing_cues:
        print(f"  Found {len(existing_cues)} existing cue points from MIK/Serato")

    # Analyze structure
    print("\n🎵 Analyzing musical structure...")
    print("  This may take 10-30 seconds depending on track length...")

    result = analyzer.analyze(audio_path, existing_cues)

    # Display sections
    print(f"\n📊 DETECTED SECTIONS ({len(result['sections'])} found):")
    print(f"  {'Time':<12} {'Label':<12} {'Energy':<8} {'Confidence'}")
    print("  " + "-"*45)

    for section in result['sections']:
        start = section['start']
        end = section['end']
        label = section['label'].upper()
        energy = section.get('energy', 0)
        confidence = section.get('confidence', 0)

        # Format time as MM:SS
        start_min = int(start // 60)
        start_sec = int(start % 60)
        end_min = int(end // 60)
        end_sec = int(end % 60)

        time_str = f"{start_min:02d}:{start_sec:02d}-{end_min:02d}:{end_sec:02d}"

        # Color code by section type
        emoji = {
            'INTRO': '🎹',
            'VERSE': '🎵',
            'CHORUS': '🎤',
            'DROP': '🔥',
            'BREAKDOWN': '💫',
            'BUILDUP': '📈',
            'BRIDGE': '🌉',
            'OUTRO': '🎬'
        }.get(label, '🎶')

        print(f"  {time_str:<12} {emoji} {label:<10} {energy:>6.3f}  {confidence:>6.1%}")

    # Display DJ points
    dj_points = result.get('dj_points', {})
    if dj_points:
        print(f"\n🎚️ DJ MIX POINTS:")

        if dj_points.get('mix_in_point'):
            time = dj_points['mix_in_point']
            print(f"  Mix In:      {int(time//60):02d}:{int(time%60):02d} ◀️")

        if dj_points.get('first_drop'):
            time = dj_points['first_drop']
            print(f"  First Drop:  {int(time//60):02d}:{int(time%60):02d} 🔥")

        if dj_points.get('main_drop'):
            time = dj_points['main_drop']
            print(f"  Main Drop:   {int(time//60):02d}:{int(time%60):02d} 🔥🔥")

        if dj_points.get('breakdown_start'):
            time = dj_points['breakdown_start']
            print(f"  Breakdown:   {int(time//60):02d}:{int(time%60):02d} 💫")

        if dj_points.get('mix_out_point'):
            time = dj_points['mix_out_point']
            print(f"  Mix Out:     {int(time//60):02d}:{int(time%60):02d} ▶️")

    # Display loop points
    loop_points = dj_points.get('loop_points', [])
    if loop_points:
        print(f"\n🔄 SUGGESTED LOOP POINTS ({len(loop_points)} found):")
        for i, loop in enumerate(loop_points[:5]):  # Show first 5
            start = loop['start']
            bars = loop['bars']
            print(f"  Loop {i+1}: {int(start//60):02d}:{int(start%60):02d} ({bars} bars)")

    # Structure summary
    print(f"\n📈 STRUCTURE SUMMARY:")
    print(f"  Tempo: {result.get('tempo', 'Unknown'):.1f} BPM")

    # Count section types
    section_counts = {}
    for section in result['sections']:
        label = section['label']
        section_counts[label] = section_counts.get(label, 0) + 1

    print(f"  Section distribution:")
    for label, count in sorted(section_counts.items()):
        print(f"    - {label}: {count}")

    # Energy flow
    energy_flow = [s.get('energy', 0) for s in result['sections']]
    if energy_flow:
        avg_energy = sum(energy_flow) / len(energy_flow)
        max_energy = max(energy_flow)
        min_energy = min(energy_flow)

        print(f"\n  Energy profile:")
        print(f"    - Average: {avg_energy:.3f}")
        print(f"    - Peak: {max_energy:.3f}")
        print(f"    - Minimum: {min_energy:.3f}")

    # Visual timeline
    print(f"\n🎼 VISUAL TIMELINE:")
    timeline = create_visual_timeline(result['sections'])
    print(timeline)

    return result


def create_visual_timeline(sections, width=60):
    """Create a visual timeline of the track structure."""

    if not sections:
        return "  No sections detected"

    # Get total duration
    total_duration = sections[-1]['end']

    # Create timeline string
    timeline = "  "

    # Map section types to characters
    char_map = {
        'intro': 'I',
        'verse': 'V',
        'chorus': 'C',
        'drop': 'D',
        'breakdown': 'B',
        'buildup': 'U',
        'bridge': 'R',
        'outro': 'O',
        'section': '-'
    }

    for section in sections:
        # Calculate width for this section
        section_width = int((section['end'] - section['start']) / total_duration * width)
        section_width = max(1, section_width)  # At least 1 character

        # Get character for this section type
        char = char_map.get(section['label'], '?')

        # Add to timeline
        timeline += char * section_width

    # Ensure we don't exceed width
    timeline = timeline[:width+2]

    # Add legend
    legend = "\n  Legend: I=Intro V=Verse C=Chorus D=Drop B=Breakdown U=Buildup O=Outro"

    return timeline + legend


def main():
    """Main function."""

    if len(sys.argv) < 2:
        print("Usage: python test_structure_analysis.py <audio_file>")
        print("\nExample:")
        print("  python test_structure_analysis.py /path/to/track.mp3")
        sys.exit(1)

    audio_path = sys.argv[1]

    if not os.path.isfile(audio_path):
        print(f"Error: {audio_path} is not a valid file")
        sys.exit(1)

    try:
        test_structure_analysis(audio_path)
    except Exception as e:
        print(f"\nError analyzing structure: {e}")
        print("\nMake sure you have librosa installed:")
        print("  pip install librosa scikit-learn scipy")
        sys.exit(1)


if __name__ == "__main__":
    main()