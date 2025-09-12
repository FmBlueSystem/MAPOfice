"""
BMAD Metadata Analysis System
=============================

Consolidates metadata analysis functionality from:
- bmad_pure_metadata_optimizer.py
"""

import json
import os
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MetadataExtractionResult:
    """Result of metadata extraction"""
    success: bool
    completeness: float
    fields_extracted: Dict[str, Any]
    quality_score: float
    issues: List[str]
    processing_time: float

@dataclass
class PureMetadataTrack:
    """Track data from pure metadata extraction"""
    filename: str
    title: str
    artist: str
    album: str
    year: Optional[int]
    genre_metadata: str
    duration: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'filename': self.filename,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'year': self.year,
            'genre_metadata': self.genre_metadata,
            'duration': self.duration
        }

class MetadataAnalyzer:
    """
    BMAD metadata analysis system
    
    Focuses on extracting and validating metadata without LLM inference.
    Consolidates functionality from bmad_pure_metadata_optimizer.py
    """
    
    def __init__(self):
        self.known_genres = self._initialize_genre_mapping()
        self.era_mapping = self._initialize_era_mapping()
        
    def analyze_pure_metadata(self, track: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze pure metadata without LLM inference
        
        Args:
            track: Track metadata dictionary
            
        Returns:
            Analysis result with metadata validation
        """
        start_time = time.time()
        
        try:
            # Extract and validate basic metadata
            extraction_result = self._extract_metadata_fields(track)
            
            # Validate data quality
            quality_score = self._calculate_quality_score(extraction_result.fields_extracted)
            
            # Classify era based on year
            era = self._classify_era(extraction_result.fields_extracted.get('year'))
            
            # Normalize genre
            normalized_genre = self._normalize_genre(extraction_result.fields_extracted.get('genre', ''))
            
            processing_time = time.time() - start_time
            
            analysis_result = {
                'success': extraction_result.success and quality_score > 0.5,
                'completeness': extraction_result.completeness,
                'quality_score': quality_score,
                'metadata': extraction_result.fields_extracted,
                'era': era,
                'normalized_genre': normalized_genre,
                'issues': extraction_result.issues,
                'processing_time': processing_time
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                'success': False,
                'completeness': 0.0,
                'quality_score': 0.0,
                'metadata': {},
                'era': 'unknown',
                'normalized_genre': 'unknown',
                'issues': [str(e)],
                'processing_time': time.time() - start_time
            }
    
    def _extract_metadata_fields(self, track: Dict[str, Any]) -> MetadataExtractionResult:
        """Extract and validate metadata fields"""
        
        fields = {}
        issues = []
        
        # Required fields
        required_fields = ['title', 'artist']
        for field in required_fields:
            value = track.get(field)
            if value:
                fields[field] = str(value).strip()
            else:
                issues.append(f"Missing required field: {field}")
        
        # Optional metadata fields
        optional_fields = {
            'album': str,
            'year': self._parse_year,
            'genre': str,
            'duration': float,
            'track_number': int,
            'disc_number': int
        }
        
        for field, parser in optional_fields.items():
            value = track.get(field)
            if value:
                try:
                    parsed_value = parser(value) if parser != str else str(value).strip()
                    fields[field] = parsed_value
                except (ValueError, TypeError):
                    issues.append(f"Invalid {field} format: {value}")
        
        # Calculate completeness
        total_possible = len(required_fields) + len(optional_fields)
        extracted_count = len(fields)
        completeness = extracted_count / total_possible
        
        success = all(field in fields for field in required_fields)
        
        return MetadataExtractionResult(
            success=success,
            completeness=completeness,
            fields_extracted=fields,
            quality_score=0.0,  # Will be calculated separately
            issues=issues,
            processing_time=0.0  # Will be set by caller
        )
    
    def _parse_year(self, year_value: Any) -> Optional[int]:
        """Parse year from various formats"""
        if isinstance(year_value, int):
            return year_value
        
        if isinstance(year_value, str):
            # Handle date strings like "2023-01-01" or "2023"
            year_str = year_value.split('-')[0].strip()
            try:
                year = int(year_str)
                # Validate reasonable year range
                if 1900 <= year <= datetime.now().year + 1:
                    return year
            except ValueError:
                pass
        
        return None
    
    def _calculate_quality_score(self, fields: Dict[str, Any]) -> float:
        """Calculate metadata quality score"""
        quality_score = 1.0
        
        # Check title quality
        title = fields.get('title', '')
        if not title:
            quality_score -= 0.3
        elif len(title.strip()) < 2:
            quality_score -= 0.2
        
        # Check artist quality
        artist = fields.get('artist', '')
        if not artist:
            quality_score -= 0.3
        elif len(artist.strip()) < 2:
            quality_score -= 0.2
        
        # Check year reasonableness
        year = fields.get('year')
        if year:
            current_year = datetime.now().year
            if not (1900 <= year <= current_year + 1):
                quality_score -= 0.1
        
        # Check genre validity
        genre = fields.get('genre', '').lower()
        if genre and genre not in self.known_genres:
            quality_score -= 0.05
        
        # Check duration reasonableness (if present)
        duration = fields.get('duration', 0)
        if duration:
            # Reasonable song length: 30 seconds to 20 minutes
            if not (30 <= duration <= 1200):
                quality_score -= 0.1
        
        return max(0.0, quality_score)
    
    def _classify_era(self, year: Optional[int]) -> str:
        """Classify musical era based on year"""
        if not year:
            return 'unknown'
        
        for era, (start, end) in self.era_mapping.items():
            if start <= year <= end:
                return era
        
        return 'unknown'
    
    def _normalize_genre(self, genre: str) -> str:
        """Normalize genre to canonical form"""
        if not genre:
            return 'unknown'
        
        genre_lower = genre.lower().strip()
        
        # Direct mapping
        if genre_lower in self.known_genres:
            return self.known_genres[genre_lower]
        
        # Fuzzy matching for common variations
        genre_mappings = {
            'electronic': ['electro', 'electronica', 'edm'],
            'hip hop': ['hip-hop', 'hiphop', 'rap'],
            'r&b': ['rnb', 'r and b', 'rhythm and blues'],
            'rock': ['rock music', 'rock n roll', 'rock and roll'],
            'pop': ['pop music', 'popular'],
            'dance': ['dance music', 'club'],
            'house': ['house music'],
            'techno': ['techno music'],
            'disco': ['disco music']
        }
        
        for canonical, variations in genre_mappings.items():
            if genre_lower in variations:
                return canonical
            for variation in variations:
                if variation in genre_lower:
                    return canonical
        
        # If no mapping found, return cleaned version
        return genre_lower
    
    def _initialize_genre_mapping(self) -> Dict[str, str]:
        """Initialize known genre mapping"""
        return {
            # Electronic genres
            'electronic': 'electronic',
            'house': 'house',
            'techno': 'techno',
            'trance': 'trance',
            'ambient': 'ambient',
            'drum and bass': 'drum_and_bass',
            'dubstep': 'dubstep',
            'garage': 'garage',
            
            # Pop/Rock genres
            'pop': 'pop',
            'rock': 'rock',
            'indie': 'indie',
            'alternative': 'alternative',
            'punk': 'punk',
            'metal': 'metal',
            
            # Urban genres
            'hip hop': 'hip_hop',
            'rap': 'hip_hop',
            'r&b': 'r_and_b',
            'soul': 'soul',
            'funk': 'funk',
            
            # Dance genres
            'disco': 'disco',
            'dance': 'dance',
            'club': 'dance',
            
            # Other genres
            'jazz': 'jazz',
            'classical': 'classical',
            'country': 'country',
            'folk': 'folk',
            'reggae': 'reggae',
            'latin': 'latin'
        }
    
    def _initialize_era_mapping(self) -> Dict[str, tuple]:
        """Initialize era to year range mapping"""
        return {
            '1950s': (1950, 1959),
            '1960s': (1960, 1969),
            '1970s': (1970, 1979),
            '1980s': (1980, 1989),
            '1990s': (1990, 1999),
            '2000s': (2000, 2009),
            '2010s': (2010, 2019),
            '2020s': (2020, 2029)
        }

class PureMetadataExtractor:
    """
    Extract metadata from track data without any LLM inference
    
    This is the "pure" extraction that relies only on existing metadata
    and does not add any AI-generated information.
    """
    
    def __init__(self, metadata_file: Optional[str] = None):
        self.metadata_file = metadata_file
        self.analyzer = MetadataAnalyzer()
        
    def extract_from_tracks(self, tracks: List[Dict[str, Any]]) -> List[PureMetadataTrack]:
        """
        Extract pure metadata from list of tracks
        
        Args:
            tracks: List of track dictionaries
            
        Returns:
            List of PureMetadataTrack objects
        """
        extracted_tracks = []
        
        for track in tracks:
            try:
                pure_track = self._extract_single_track(track)
                if pure_track:
                    extracted_tracks.append(pure_track)
            except Exception:
                continue  # Skip problematic tracks
                
        return extracted_tracks
    
    def _extract_single_track(self, track: Dict[str, Any]) -> Optional[PureMetadataTrack]:
        """Extract metadata from single track"""
        
        # Analyze metadata
        analysis = self.analyzer.analyze_pure_metadata(track)
        
        if not analysis['success']:
            return None
            
        metadata = analysis['metadata']
        
        # Create PureMetadataTrack object
        pure_track = PureMetadataTrack(
            filename=track.get('filename', 'unknown'),
            title=metadata.get('title', ''),
            artist=metadata.get('artist', ''),
            album=metadata.get('album', ''),
            year=metadata.get('year'),
            genre_metadata=metadata.get('genre', ''),
            duration=metadata.get('duration', 0.0)
        )
        
        return pure_track
    
    def save_extracted_metadata(self, tracks: List[PureMetadataTrack], output_file: str) -> bool:
        """Save extracted metadata to JSON file"""
        try:
            track_data = [track.to_dict() for track in tracks]
            
            output = {
                'extraction_timestamp': datetime.now().isoformat(),
                'tracks_extracted': len(tracks),
                'tracks': track_data
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception:
            return False
    
    def load_extracted_metadata(self, input_file: str) -> List[PureMetadataTrack]:
        """Load previously extracted metadata from JSON file"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tracks = []
            for track_data in data.get('tracks', []):
                track = PureMetadataTrack(
                    filename=track_data.get('filename', ''),
                    title=track_data.get('title', ''),
                    artist=track_data.get('artist', ''),
                    album=track_data.get('album', ''),
                    year=track_data.get('year'),
                    genre_metadata=track_data.get('genre_metadata', ''),
                    duration=track_data.get('duration', 0.0)
                )
                tracks.append(track)
                
            return tracks
            
        except Exception:
            return []

def create_sample_metadata_dataset(count: int = 20) -> List[Dict[str, Any]]:
    """Create sample metadata dataset for testing"""
    import random
    
    sample_tracks = [
        {'title': 'Stayin\' Alive', 'artist': 'Bee Gees', 'year': 1977, 'genre': 'Disco'},
        {'title': 'I Will Survive', 'artist': 'Gloria Gaynor', 'year': 1978, 'genre': 'Disco'},
        {'title': 'Le Freak', 'artist': 'Chic', 'year': 1978, 'genre': 'Disco'},
        {'title': 'Love Train', 'artist': 'The O\'Jays', 'year': 1972, 'genre': 'Soul'},
        {'title': 'Move On Up', 'artist': 'Curtis Mayfield', 'year': 1970, 'genre': 'Soul'},
        {'title': 'I Want Your Love', 'artist': 'Chic', 'year': 1978, 'genre': 'Disco'},
        {'title': 'Dancing Queen', 'artist': 'ABBA', 'year': 1976, 'genre': 'Pop'},
        {'title': 'September', 'artist': 'Earth Wind & Fire', 'year': 1978, 'genre': 'Funk'},
        {'title': 'Good Times', 'artist': 'Chic', 'year': 1979, 'genre': 'Disco'},
        {'title': 'Funky Town', 'artist': 'Lipps Inc.', 'year': 1980, 'genre': 'Disco'}
    ]
    
    # Generate dataset with some variations
    dataset = []
    for i in range(count):
        base_track = random.choice(sample_tracks)
        
        track = {
            'filename': f'track_{i+1:03d}.mp3',
            'title': base_track['title'],
            'artist': base_track['artist'],
            'album': f'Album {i % 5 + 1}',
            'year': base_track['year'],
            'genre': base_track['genre'],
            'duration': random.uniform(180, 360),  # 3-6 minutes
            'track_number': (i % 12) + 1
        }
        
        # Add some missing data to simulate real-world conditions
        if random.random() < 0.1:  # 10% missing album
            track.pop('album', None)
        if random.random() < 0.05:  # 5% missing year
            track.pop('year', None)
        if random.random() < 0.15:  # 15% missing genre
            track.pop('genre', None)
            
        dataset.append(track)
    
    return dataset