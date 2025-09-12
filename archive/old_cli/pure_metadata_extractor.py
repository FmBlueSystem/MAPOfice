#!/usr/bin/env python3
"""Pure Metadata Extractor - NO CHEATING, NO INFERENCE
Extracts ONLY real metadata from audio files using mutagen
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json

try:
    from mutagen import File
    from mutagen.flac import FLAC
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3NoHeaderError
except ImportError:
    print("❌ mutagen required: pip install mutagen")
    sys.exit(1)

@dataclass
class PureMetadata:
    """Pure metadata extracted from audio file - NO INFERENCE"""
    filepath: str
    filename: str
    
    # Basic metadata (if available)
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    albumartist: Optional[str] = None
    date: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    
    # Technical metadata
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    
    # All raw metadata for analysis
    raw_metadata: Dict[str, Any] = None


class PureMetadataExtractor:
    """Extracts ONLY real metadata from audio files - NO CHEATING"""
    
    def __init__(self):
        pass
    
    def extract_from_directory(self, directory: str) -> List[PureMetadata]:
        """Extract pure metadata from all audio files in directory"""
        directory_path = Path(directory)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        print(f"🎵 PURE METADATA EXTRACTION from: {directory}")
        print("="*80)
        print("⚠️  NO CHEATING: Only real metadata from audio files")
        print("⚠️  NO INFERENCE: No guessing from filenames or paths")
        print("="*80)
        
        audio_files = (
            list(directory_path.glob("*.flac")) +
            list(directory_path.glob("*.mp3")) + 
            list(directory_path.glob("*.wav")) +
            list(directory_path.glob("*.m4a"))
        )
        
        print(f"📁 Found {len(audio_files)} audio files")
        
        extracted_metadata = []
        
        for file_path in audio_files:
            print(f"\n🔍 Extracting from: {file_path.name}")
            
            try:
                metadata = self._extract_pure_metadata(file_path)
                extracted_metadata.append(metadata)
                
                # Display what we actually found
                print(f"   📋 Title: {metadata.title or 'NOT IN METADATA'}")
                print(f"   👤 Artist: {metadata.artist or 'NOT IN METADATA'}")
                print(f"   💿 Album: {metadata.album or 'NOT IN METADATA'}")
                print(f"   📅 Year: {metadata.year or 'NOT IN METADATA'}")
                print(f"   🎭 Genre: {metadata.genre or 'NOT IN METADATA'}")
                print(f"   ⏱️  Duration: {metadata.duration:.1f}s" if metadata.duration else "   ⏱️  Duration: NOT AVAILABLE")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                # Still add the file with minimal metadata
                metadata = PureMetadata(
                    filepath=str(file_path),
                    filename=file_path.name,
                    raw_metadata={'error': str(e)}
                )
                extracted_metadata.append(metadata)
        
        print(f"\n✅ Extracted metadata from {len(extracted_metadata)} files")
        return extracted_metadata
    
    def _extract_pure_metadata(self, file_path: Path) -> PureMetadata:
        """Extract pure metadata from single audio file"""
        
        # Use mutagen to read metadata
        audio_file = File(str(file_path))
        
        if audio_file is None:
            raise ValueError("Could not read audio metadata")
        
        # Extract basic metadata (these are REAL metadata fields)
        metadata = PureMetadata(
            filepath=str(file_path),
            filename=file_path.name
        )
        
        # Common metadata fields across formats
        metadata_fields = {
            'title': ['TIT2', 'TITLE', '\xa9nam'],
            'artist': ['TPE1', 'ARTIST', '\xa9ART'],
            'album': ['TALB', 'ALBUM', '\xa9alb'],
            'albumartist': ['TPE2', 'ALBUMARTIST', 'aART'],
            'date': ['TDRC', 'DATE', '\xa9day'],
            'genre': ['TCON', 'GENRE', '\xa9gen']
        }
        
        # Extract metadata fields
        for field_name, possible_keys in metadata_fields.items():
            value = None
            
            # Try each possible key for this field
            for key in possible_keys:
                if key in audio_file:
                    raw_value = audio_file[key]
                    if isinstance(raw_value, list) and raw_value:
                        value = str(raw_value[0])
                    else:
                        value = str(raw_value)
                    break
            
            # Set the field
            setattr(metadata, field_name, value)
        
        # Extract year from date if available
        if metadata.date:
            try:
                # Extract year from various date formats
                date_str = metadata.date
                if '-' in date_str:
                    year_part = date_str.split('-')[0]
                else:
                    year_part = date_str[:4] if len(date_str) >= 4 else date_str
                
                metadata.year = int(year_part)
            except (ValueError, TypeError):
                pass
        
        # Technical metadata
        info = audio_file.info
        if info:
            metadata.duration = getattr(info, 'length', None)
            metadata.bitrate = getattr(info, 'bitrate', None) 
            metadata.sample_rate = getattr(info, 'sample_rate', None)
            metadata.channels = getattr(info, 'channels', None)
        
        # Store all raw metadata for analysis
        metadata.raw_metadata = dict(audio_file)
        
        return metadata
    
    def save_metadata_to_json(self, metadata_list: List[PureMetadata], output_file: str):
        """Save extracted metadata to JSON file"""
        print(f"\n💾 Saving metadata to: {output_file}")
        
        # Convert to serializable format
        serializable_data = []
        for metadata in metadata_list:
            data = asdict(metadata)
            # Convert raw_metadata to strings for JSON serialization
            if data['raw_metadata']:
                data['raw_metadata'] = {k: str(v) for k, v in data['raw_metadata'].items()}
            serializable_data.append(data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Metadata saved successfully")
    
    def validate_metadata_completeness(self, metadata_list: List[PureMetadata]):
        """Validate how complete the metadata is"""
        print(f"\n📊 METADATA COMPLETENESS ANALYSIS")
        print("="*60)
        
        total_files = len(metadata_list)
        
        completeness = {
            'title': 0,
            'artist': 0,
            'album': 0,
            'year': 0,
            'genre': 0,
            'duration': 0
        }
        
        for metadata in metadata_list:
            if metadata.title: completeness['title'] += 1
            if metadata.artist: completeness['artist'] += 1
            if metadata.album: completeness['album'] += 1
            if metadata.year: completeness['year'] += 1
            if metadata.genre: completeness['genre'] += 1
            if metadata.duration: completeness['duration'] += 1
        
        print(f"📋 Total files: {total_files}")
        for field, count in completeness.items():
            percentage = (count / total_files) * 100
            print(f"   {field.upper()}: {count}/{total_files} ({percentage:.1f}%)")
        
        # Identify files with missing critical metadata
        missing_critical = []
        for metadata in metadata_list:
            if not metadata.artist or not metadata.title:
                missing_critical.append(metadata.filename)
        
        if missing_critical:
            print(f"\n⚠️  Files missing critical metadata (artist/title):")
            for filename in missing_critical:
                print(f"   - {filename}")
        else:
            print(f"\n✅ All files have critical metadata (artist/title)")


def main():
    """Main execution"""
    music_directory = '/Volumes/My Passport/Abibleoteca/Consolidado2025/Playlists/Dance - 80s - 2025-08-17'
    
    if not os.path.exists(music_directory):
        print(f"❌ Directory not found: {music_directory}")
        return
    
    extractor = PureMetadataExtractor()
    
    # Extract pure metadata
    metadata_list = extractor.extract_from_directory(music_directory)
    
    # Validate completeness
    extractor.validate_metadata_completeness(metadata_list)
    
    # Save to file for analysis
    output_file = "pure_metadata_dance_80s.json"
    extractor.save_metadata_to_json(metadata_list, output_file)
    
    print(f"\n🎯 PURE METADATA EXTRACTED")
    print("="*60)
    print("✅ NO cheating - only real metadata from files")
    print("✅ NO inference - no guessing from names")
    print(f"✅ Data saved to: {output_file}")
    print("\n🔄 Ready for BMAD optimization cycle with pure data")


if __name__ == "__main__":
    main()