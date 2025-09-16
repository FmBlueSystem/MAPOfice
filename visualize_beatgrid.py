#!/usr/bin/env python3
"""
Visualize Beatgrid and Downbeats from Serato
Shows a visual representation of beats and downbeats (bar starts).
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.metadata import extract_precomputed_metadata


def visualize_beatgrid(file_path: str, duration_sec: float = 30.0):
    """
    Visualize the beatgrid and downbeats for a track.

    Args:
        file_path: Path to audio file
        duration_sec: How many seconds to visualize (default 30)
    """
    print(f"\n{'='*80}")
    print(f"BEATGRID VISUALIZATION: {os.path.basename(file_path)}")
    print(f"{'='*80}")

    # Extract metadata
    metadata = extract_precomputed_metadata(file_path)

    if not metadata:
        print("ERROR: Could not extract metadata")
        return

    # Get beatgrid
    beatgrid = metadata.get('beatgrid')
    if not beatgrid:
        print("No beatgrid found in file")
        return

    print(f"\n📊 BEATGRID INFO:")
    print(f"  BPM: {beatgrid.bpm if hasattr(beatgrid, 'bpm') else 'Unknown'}")
    print(f"  Time Signature: {beatgrid.time_signature if hasattr(beatgrid, 'time_signature') else '4/4'}")

    # Get beats and downbeats
    beats = beatgrid.beats if hasattr(beatgrid, 'beats') else []
    downbeats = beatgrid.downbeats if hasattr(beatgrid, 'downbeats') else []

    # If no explicit downbeats, calculate from beats (every 4 beats in 4/4)
    if not downbeats and beats:
        downbeats = [beats[i] for i in range(0, len(beats), 4)]
        print(f"  Downbeats: Calculated from beats (4/4 assumed)")
    else:
        print(f"  Downbeats: Extracted from Serato")

    if not beats:
        print("\nNo beat positions available")
        return

    print(f"\n  Total Beats: {len(beats)}")
    print(f"  Total Bars: {len(downbeats)}")

    # Visual representation
    print(f"\n📍 VISUAL BEATGRID (First {duration_sec} seconds):")
    print("  Time:  0....5....10...15...20...25...30")
    print("         |    |    |    |    |    |    |")

    # Create timeline
    resolution = 40  # characters for 30 seconds
    timeline_beats = ['.' for _ in range(resolution)]
    timeline_downbeats = [' ' for _ in range(resolution)]

    # Mark beats
    for beat in beats:
        if beat > duration_sec:
            break
        pos = int((beat / duration_sec) * (resolution - 1))
        if 0 <= pos < resolution:
            timeline_beats[pos] = '|'

    # Mark downbeats
    for downbeat in downbeats:
        if downbeat > duration_sec:
            break
        pos = int((downbeat / duration_sec) * (resolution - 1))
        if 0 <= pos < resolution:
            timeline_downbeats[pos] = '▼'
            timeline_beats[pos] = '█'  # Stronger marker for downbeat

    print("  Bars:  " + ''.join(timeline_downbeats))
    print("  Beats: " + ''.join(timeline_beats))

    # Show bar structure
    print(f"\n🎵 BAR STRUCTURE (First 8 bars):")
    for i, downbeat in enumerate(downbeats[:8]):
        bar_num = i + 1

        # Get beats in this bar
        bar_beats = []
        start_beat_idx = i * 4  # Assuming 4/4
        for j in range(4):
            if start_beat_idx + j < len(beats):
                bar_beats.append(beats[start_beat_idx + j])

        if bar_beats:
            print(f"  Bar {bar_num:2d}: {downbeat:6.3f}s |", end="")
            for beat_idx, beat in enumerate(bar_beats):
                if beat_idx == 0:
                    print(f" [1]={beat:.3f}s", end="")
                else:
                    print(f" {beat_idx+1}={beat:.3f}s", end="")
            print()

    # Show phase alignment
    if downbeats:
        print(f"\n🔄 PHASE ALIGNMENT:")
        print(f"  First downbeat at: {downbeats[0]:.3f}s")
        if len(downbeats) > 1:
            bar_duration = downbeats[1] - downbeats[0]
            bars_per_phrase = 8  # Standard phrase length
            phrase_duration = bar_duration * bars_per_phrase
            print(f"  Bar duration: {bar_duration:.3f}s")
            print(f"  8-bar phrase duration: {phrase_duration:.3f}s")

            # Show phrase markers
            print(f"\n  PHRASE MARKERS (8-bar phrases):")
            for phrase_num in range(min(4, len(downbeats) // 8)):
                phrase_start = downbeats[phrase_num * 8] if phrase_num * 8 < len(downbeats) else None
                if phrase_start:
                    print(f"    Phrase {phrase_num + 1}: {phrase_start:.3f}s")

    # Show cue points in relation to bars
    cue_points = metadata.get('cue_points', [])
    if cue_points and downbeats:
        print(f"\n🎯 CUE POINTS ALIGNED TO BARS:")
        for cue in cue_points[:8]:
            if hasattr(cue, 'position_ms'):
                cue_pos_sec = cue.position_ms / 1000
            else:
                cue_pos_sec = getattr(cue, 'position', 0) / 1000

            # Find nearest bar
            nearest_bar = 0
            for i, downbeat in enumerate(downbeats):
                if downbeat > cue_pos_sec:
                    nearest_bar = i
                    break

            cue_name = getattr(cue, 'name', '') or getattr(cue, 'type', 'Cue')
            print(f"    {cue_name}: {cue_pos_sec:.3f}s (Bar {nearest_bar + 1})")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python visualize_beatgrid.py <audio_file>")
        print("\nExample:")
        print("  python visualize_beatgrid.py /path/to/track.mp3")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"Error: {file_path} is not a valid file")
        sys.exit(1)

    # Optional: duration to visualize
    duration = 30.0
    if len(sys.argv) > 2:
        try:
            duration = float(sys.argv[2])
        except ValueError:
            duration = 30.0

    visualize_beatgrid(file_path, duration)


if __name__ == "__main__":
    main()