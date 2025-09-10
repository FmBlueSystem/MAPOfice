#!/usr/bin/env python3
"""
Re-analyze Music Tracks with Historically Accurate Genre Classification

This script re-processes existing tracks in the database using the improved
OpenAI prompt that provides historically accurate genre classifications.

Usage:
    python scripts/reanalyze_with_historical_accuracy.py [--dry-run] [--limit N]
    
Examples:
    python scripts/reanalyze_with_historical_accuracy.py --dry-run
    python scripts/reanalyze_with_historical_accuracy.py --limit 10
    python scripts/reanalyze_with_historical_accuracy.py
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.services.enhanced_analyzer import create_enhanced_analyzer
from src.services.metadata_writer import metadata_writer
from src.models.ai_analysis import AIAnalysis


def main():
    parser = argparse.ArgumentParser(description='Re-analyze tracks with historically accurate genres')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without making changes')
    parser.add_argument('--limit', type=int, help='Limit number of tracks to process')
    parser.add_argument('--force-all', action='store_true', help='Re-analyze all tracks, not just problematic ones')
    
    args = parser.parse_args()
    
    print("=== RE-ANALYSIS WITH HISTORICAL ACCURACY ===")
    print()
    
    # Initialize analyzer
    try:
        analyzer = create_enhanced_analyzer(enable_ai=True)
        if not analyzer.ai_enricher:
            print("❌ OpenAI enricher not available. Check API key and quota.")
            return 1
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return 1
    
    # Find tracks that need re-analysis
    problematic_genres = ['Electronic']  # Genres that need historical correction
    
    with analyzer.storage.session() as session:
        if args.force_all:
            # Re-analyze all tracks with AI analysis
            tracks_to_process = session.query(AIAnalysis).all()
            print(f"Found {len(tracks_to_process)} tracks with AI analysis (re-analyzing ALL)")
        else:
            # Find tracks with problematic genre classifications
            tracks_to_process = session.query(AIAnalysis).filter(
                AIAnalysis.genre.in_(problematic_genres)
            ).all()
            print(f"Found {len(tracks_to_process)} tracks with potentially inaccurate genre classifications:")
            for genre in problematic_genres:
                count = session.query(AIAnalysis).filter(AIAnalysis.genre == genre).count()
                print(f"  - {genre}: {count} tracks")
    
    if not tracks_to_process:
        print("✅ No tracks need re-analysis")
        return 0
        
    # Apply limit if specified
    if args.limit and args.limit < len(tracks_to_process):
        tracks_to_process = tracks_to_process[:args.limit]
        print(f"Processing limited to {args.limit} tracks")
        
    print()
    
    if args.dry_run:
        print("=== DRY RUN - NO CHANGES WILL BE MADE ===")
        for i, ai_analysis in enumerate(tracks_to_process, 1):
            track = ai_analysis.track
            if track and track.path:
                filename = Path(track.path).name
                print(f"[{i}] Would re-analyze: {filename}")
                print(f"    Current: {ai_analysis.genre} → {ai_analysis.subgenre}")
        print()
        print(f"Total tracks that would be re-analyzed: {len(tracks_to_process)}")
        return 0
    
    # Perform re-analysis
    print("Starting re-analysis...")
    print()
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, ai_analysis in enumerate(tracks_to_process, 1):
        track = ai_analysis.track
        if not track or not track.path:
            print(f"[{i}/{len(tracks_to_process)}] ⚠️ Track missing file path, skipping")
            skipped_count += 1
            continue
            
        if not os.path.exists(track.path):
            print(f"[{i}/{len(tracks_to_process)}] ⚠️ File not found: {Path(track.path).name}")
            skipped_count += 1
            continue
            
        try:
            filename = Path(track.path).name
            old_genre = ai_analysis.genre
            old_subgenre = ai_analysis.subgenre
            
            print(f"[{i}/{len(tracks_to_process)}] Re-analyzing: {filename}")
            print(f"    Old classification: {old_genre} → {old_subgenre}")
            
            # Force re-analysis with the improved prompt
            result = analyzer.analyze_track(track.path, force_reanalysis=True)
            
            if result.success and result.genre:
                print(f"    New classification: {result.genre} → {result.subgenre}")
                
                # Check if classification changed
                if result.genre != old_genre or result.subgenre != old_subgenre:
                    print("    📝 Classification updated!")
                    
                    # Update metadata in audio file
                    metadata = {
                        'genre': result.genre,
                        'subgenre': result.subgenre,
                        'mood': result.mood,
                        'era': result.era,
                        'tags': ', '.join(result.tags) if result.tags else None
                    }
                    metadata = {k: v for k, v in metadata.items() if v is not None}
                    
                    if metadata:
                        metadata_success = metadata_writer.write_analysis_to_file(track.path, metadata)
                        if metadata_success:
                            print("    ✅ Metadata written to file")
                        else:
                            print("    ⚠️ Failed to write metadata to file")
                else:
                    print("    ℹ️ No classification change")
                
                updated_count += 1
            else:
                print(f"    ❌ Re-analysis failed: {result.error_message or 'Unknown error'}")
                error_count += 1
                
        except Exception as e:
            print(f"[{i}/{len(tracks_to_process)}] ❌ Error: {str(e)}")
            error_count += 1
            
        print()
    
    # Summary
    print("=== RE-ANALYSIS SUMMARY ===")
    print(f"✅ Successfully processed: {updated_count} tracks")
    print(f"⚠️ Skipped: {skipped_count} tracks")
    print(f"❌ Errors: {error_count} tracks")
    print(f"📊 Total: {updated_count + skipped_count + error_count} tracks")
    print()
    
    if updated_count > 0:
        print("🎉 Re-analysis complete with historically accurate genres!")
        print("Examples of corrections that should now appear:")
        print("  • A Flock Of Seagulls: Electronic → New Wave")
        print("  • 2 Unlimited: Electronic → Eurodance") 
        print("  • Gary Numan: Electronic → Synth-pop")
        print("  • Kraftwerk (70s): Electronic → Krautrock")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())