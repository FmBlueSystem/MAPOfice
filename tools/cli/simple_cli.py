#!/usr/bin/env python3
"""Simple CLI using exact same logic as UI

This CLI reuses the exact same functions and logic that the UI uses,
without any additional validation layers.
"""

import os
import sys
import time
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import same services as UI
from src.services.enhanced_analyzer import EnhancedAnalyzer, EnhancedAnalysisResult
from src.services.storage import Storage
from src.services.metadata_writer import metadata_writer
from src.analysis.multi_llm_enricher import is_multi_llm_available


@dataclass
class SimpleCLIConfig:
    """Simple CLI configuration"""
    folder_path: str
    export_file: Optional[str] = None
    formats: List[str] = None
    recursive: bool = True
    enable_ai: bool = True
    force_reanalysis: bool = False
    write_metadata: bool = False
    verbose: bool = True


class SimpleCLI:
    """Simple CLI using same logic as UI"""
    
    SUPPORTED_FORMATS = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma'}
    
    def __init__(self, config: SimpleCLIConfig):
        self.config = config
        # Use EXACT same initialization as UI (skip validation like UI does)
        self.storage = Storage.from_path("data/music.db")
        self.enhanced_analyzer = EnhancedAnalyzer(self.storage, enable_ai=config.enable_ai, skip_validation=True)
        self.ai_available = is_multi_llm_available()
        self.results: List[EnhancedAnalysisResult] = []
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'successful': 0,
            'ai_enriched': 0,
            'errors': 0
        }
        
    def print_header(self):
        """Print CLI header"""
        print("🎵 Simple Music Analyzer CLI - Using UI Logic")
        print("=" * 60)
        print(f"📁 Folder: {self.config.folder_path}")
        print(f"🤖 AI Analysis: {'Enabled' if self.config.enable_ai else 'Disabled'}")
        print(f"🔄 Force Reanalysis: {'Yes' if self.config.force_reanalysis else 'No'}")
        print(f"📝 Write Metadata: {'Yes' if self.config.write_metadata else 'No'}")
        print(f"🌐 Multi-LLM Available: {'Yes' if self.ai_available else 'No'}")
        print("=" * 60)
        print()
        
    def find_audio_files(self) -> List[str]:
        """Find all audio files in the specified folder"""
        print("🔍 Scanning for audio files...")
        
        audio_files = []
        folder_path = Path(self.config.folder_path)
        
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {self.config.folder_path}")
            
        # Get file extensions to search for
        if self.config.formats:
            extensions = {f'.{fmt.lower()}' for fmt in self.config.formats}
        else:
            extensions = self.SUPPORTED_FORMATS
            
        # Search for files
        pattern = "**/*" if self.config.recursive else "*"
        
        for file_path in folder_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                audio_files.append(str(file_path))
                
        audio_files.sort()  # Sort for consistent processing order
        
        print(f"📊 Found {len(audio_files)} audio files")
        if self.config.formats:
            print(f"📋 Formats: {', '.join(self.config.formats)}")
        print()
        
        return audio_files
        
    def analyze_files(self, audio_files: List[str]):
        """Analyze all audio files using EXACT same logic as UI"""
        total = len(audio_files)
        self.stats['total_files'] = total
        
        if total == 0:
            print("⚠️ No audio files found to process")
            return
            
        print(f"🚀 Starting analysis of {total} files...")
        print("=" * 60)
        
        start_time = time.time()
        
        for i, file_path in enumerate(audio_files, 1):
            file_name = Path(file_path).name
            
            if self.config.verbose:
                print(f"📄 [{i:3d}/{total:3d}] {file_name}")
            
            try:
                # Use EXACT same call as UI - no validation
                def llm_callback(provider: str, status: str):
                    if self.config.verbose:
                        print(f"     🔄 {provider}: {status}")
                
                # Call exact same function as UI
                result = self.enhanced_analyzer.analyze_track(
                    file_path, 
                    force_reanalysis=self.config.force_reanalysis,
                    llm_progress_callback=llm_callback
                )
                
                self.results.append(result)
                self.stats['processed'] += 1
                
                if result.success:
                    self.stats['successful'] += 1
                    if result.genre:  # Has AI enrichment
                        self.stats['ai_enriched'] += 1
                    
                    # Write metadata to file if requested
                    if self.config.write_metadata and result.success:
                        self._write_metadata_to_file(result)
                    
                    if self.config.verbose:
                        genre_info = f" | {result.genre}" if result.genre else ""
                        print(f"     ✅ Success{genre_info}")
                else:
                    self.stats['errors'] += 1
                    if self.config.verbose:
                        print(f"     ❌ Error: {result.error_message}")
                            
            except Exception as e:
                self.stats['errors'] += 1
                if self.config.verbose:
                    print(f"     💥 Exception: {str(e)}")
                    
                # Create error result
                error_result = EnhancedAnalysisResult(
                    track_path=file_path,
                    success=False,
                    error_message=str(e),
                    title=Path(file_path).stem
                )
                self.results.append(error_result)
                
            # Progress indicator for non-verbose mode
            if not self.config.verbose and i % 10 == 0:
                print(f"Progress: {i}/{total} ({(i/total)*100:.1f}%)")
                
        elapsed_time = time.time() - start_time
        print("=" * 60)
        print(f"⏱️ Analysis completed in {elapsed_time:.1f} seconds")
        print()
        
    def print_summary(self):
        """Print analysis summary"""
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"📁 Total files found: {self.stats['total_files']}")
        print(f"⚡ Files processed: {self.stats['processed']}")
        print(f"✅ Successful: {self.stats['successful']}")
        print(f"🤖 AI enriched: {self.stats['ai_enriched']}")
        print(f"💥 Errors: {self.stats['errors']}")
        
        # Success rate
        if self.stats['processed'] > 0:
            success_rate = (self.stats['successful'] / self.stats['processed']) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
            
            if self.stats['successful'] > 0:
                ai_rate = (self.stats['ai_enriched'] / self.stats['successful']) * 100
                print(f"🎯 AI enrichment rate: {ai_rate:.1f}%")
                
        print("=" * 60)
            
    def export_results(self):
        """Export results to CSV file"""
        if not self.config.export_file:
            return
            
        print(f"📤 Exporting results to {self.config.export_file}...")
        
        try:
            with open(self.config.export_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'file_path', 'file_name', 'success', 'title', 'artist', 'album',
                    'bpm', 'key', 'energy', 'genre', 'subgenre', 'mood', 'era',
                    'tags', 'hamms_confidence', 'ai_confidence', 'processing_time_ms',
                    'error_message'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in self.results:
                    row = {
                        'file_path': result.track_path,
                        'file_name': Path(result.track_path).name,
                        'success': result.success,
                        'title': result.title,
                        'artist': result.artist,
                        'album': result.album,
                        'bpm': result.bpm,
                        'key': result.key,
                        'energy': result.energy,
                        'genre': result.genre,
                        'subgenre': result.subgenre,
                        'mood': result.mood,
                        'era': result.era,
                        'tags': ', '.join(result.tags) if result.tags else '',
                        'hamms_confidence': result.hamms_confidence,
                        'ai_confidence': result.ai_confidence,
                        'processing_time_ms': result.processing_time_ms,
                        'error_message': result.error_message or ''
                    }
                    writer.writerow(row)
                    
            print(f"✅ Results exported successfully!")
            
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
            
    def run(self):
        """Run the complete analysis process"""
        try:
            self.print_header()
            
            # Find audio files
            audio_files = self.find_audio_files()
            
            # Analyze files using EXACT same logic as UI
            self.analyze_files(audio_files)
            
            # Print summary
            self.print_summary()
            
            # Export results if requested
            self.export_results()
            
            return True
            
        except Exception as e:
            print(f"💥 Fatal error: {str(e)}")
            return False
            
    def _write_metadata_to_file(self, result: EnhancedAnalysisResult) -> None:
        """Write analysis results to audio file metadata"""
        try:
            metadata = {
                'genre': result.genre,
                'bpm': str(result.bpm) if result.bpm else None,
                'key': result.key,
                'energy': str(result.energy) if result.energy else None,
                'mood': result.mood,
                'era': result.era,
                'subgenre': result.subgenre
            }
            
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            if metadata:
                success = metadata_writer.write_analysis_to_file(result.track_path, metadata)
                if success:
                    if self.config.verbose:
                        print(f"     📝 Metadata written to file")
                else:
                    if self.config.verbose:
                        print(f"     ⚠️ Failed to write metadata")
            
        except Exception as e:
            if self.config.verbose:
                print(f"     ⚠️ Error writing metadata: {str(e)}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Simple CLI using exact same logic as UI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "/Users/music/collection"
  %(prog)s "/Users/music/collection" --export results.csv --formats mp3,flac
  %(prog)s "/Users/music/collection" --no-ai --force
        """
    )
    
    parser.add_argument(
        'folder',
        help='Path to folder containing audio files'
    )
    
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export results to CSV file'
    )
    
    parser.add_argument(
        '--formats',
        metavar='FORMATS',
        help='Comma-separated list of audio formats (e.g., mp3,flac,wav)'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subfolders recursively'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI analysis (HAMMS only)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true', 
        help='Force reanalysis of already processed files'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output (less verbose)'
    )
    
    parser.add_argument(
        '--write-metadata',
        action='store_true',
        help='Write analysis results to audio file metadata'
    )
    
    args = parser.parse_args()
    
    # Parse formats
    formats = None
    if args.formats:
        formats = [fmt.strip() for fmt in args.formats.split(',')]
        
    # Create configuration
    config = SimpleCLIConfig(
        folder_path=args.folder,
        export_file=args.export,
        formats=formats,
        recursive=not args.no_recursive,
        enable_ai=not args.no_ai,
        force_reanalysis=args.force,
        write_metadata=getattr(args, 'write_metadata', False),
        verbose=not args.quiet
    )
    
    # Run analysis
    cli = SimpleCLI(config)
    success = cli.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()