"""Enhanced Music Analysis Service

This service combines HAMMS v3.0 analysis with OpenAI GPT-4 enrichment
to provide comprehensive music analysis including both technical and semantic metadata.

POML Quality Gates:
- Input validation and error handling
- Database transaction management
- Analysis result validation
- Performance monitoring and logging
"""

from __future__ import annotations

import os
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from src.analysis.hamms_v3 import HAMMSAnalyzerV3
from src.analysis.multi_llm_enricher import MultiLLMEnricher
from src.services.storage import Storage
from src.services.metadata_writer import metadata_writer
from src.models.hamms_advanced import HAMMSAdvanced
from src.services.storage import AIAnalysis


@dataclass
class EnhancedAnalysisResult:
    """Complete analysis result combining HAMMS and AI analysis"""
    track_path: str
    success: bool
    
    # Basic track metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    
    # HAMMS v3.0 results
    hamms_vector: List[float] = None
    hamms_confidence: float = 0.0
    hamms_dimensions: Dict[str, float] = None
    
    # AI analysis results
    genre: Optional[str] = None
    subgenre: Optional[str] = None
    mood: Optional[str] = None
    era: Optional[str] = None
    tags: List[str] = None
    ai_confidence: Optional[float] = None
    
    # Processing metadata
    processing_time_ms: int = 0
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class EnhancedAnalyzer:
    """Enhanced music analyzer combining HAMMS v3.0 and OpenAI enrichment
    
    This service provides a complete music analysis pipeline that:
    1. Extracts basic audio features (BPM, key, energy)
    2. Calculates 12-dimensional HAMMS vectors
    3. Optionally enriches with AI-generated metadata
    4. Stores all results in the database with proper relationships
    """
    
    def __init__(self, storage: Storage, enable_ai: bool = True):
        """Initialize the enhanced analyzer
        
        Args:
            storage: Database storage instance
            enable_ai: Whether to enable OpenAI enrichment
        """
        self.storage = storage
        self.hamms_analyzer = HAMMSAnalyzerV3()
        self.enable_ai = enable_ai
        
        # Initialize Multi-LLM enricher if available and requested
        self.ai_enricher = None
        if enable_ai:
            # Get preferred provider from environment or use default
            preferred_provider = os.getenv('LLM_PROVIDER', 'gemini')
            
            self.ai_enricher = MultiLLMEnricher(preferred_provider=preferred_provider)
            
            if not self.ai_enricher.get_available_providers():
                print("WARNING: No LLM providers configured. AI enrichment disabled.")
                print("Configure GEMINI_API_KEY or OPENAI_API_KEY in .env file to enable AI analysis.")
                self.enable_ai = False
            else:
                available = ", ".join(self.ai_enricher.get_available_providers())
                print(f"✅ Multi-LLM initialized with providers: {available}")
                
                # Show cost estimates
                estimates = self.ai_enricher.get_cost_estimates()
                print("💰 Cost estimates per 1M tokens:")
                for provider, costs in estimates.items():
                    print(f"  {provider.title()}: ${costs['input_cost_per_1M']:.3f} input / ${costs['output_cost_per_1M']:.3f} output")
    
    def _get_track_metadata(self, track_path: str) -> Dict[str, Any]:
        """Get basic track metadata from database"""
        try:
            track_data = self.storage.get_analysis_by_path(track_path)
            if track_data:
                return {
                    'title': track_data.get('title'),
                    'artist': track_data.get('artist'),
                    'album': track_data.get('album'),
                    'bpm': track_data.get('bpm'),
                    'key': track_data.get('key')
                }
        except:
            pass
        
        # Fallback to extracting metadata directly from file
        metadata = self._extract_file_metadata(track_path)
        return {
            'title': metadata.get('title') or Path(track_path).stem,
            'artist': metadata.get('artist') or "Unknown Artist",
            'album': metadata.get('album') or "Unknown Album",
            'bpm': metadata.get('bpm'),
            'key': metadata.get('key')
        }
    
    def _extract_file_metadata(self, track_path: str) -> Dict[str, Any]:
        """Extract basic metadata directly from audio file using mutagen
        
        Args:
            track_path: Path to the audio file
            
        Returns:
            Dictionary with title, artist, album metadata
        """
        try:
            import mutagen
            
            audio_file = mutagen.File(track_path)
            if not audio_file:
                return {}
                
            metadata = {}
            
            # Common tag mappings for different formats
            title_tags = ['TIT2', 'TITLE', '\xa9nam']  # ID3, Vorbis, MP4
            artist_tags = ['TPE1', 'ARTIST', '\xa9ART']  # ID3, Vorbis, MP4  
            album_tags = ['TALB', 'ALBUM', '\xa9alb']   # ID3, Vorbis, MP4
            
            # Extract title
            for tag in title_tags:
                if tag in audio_file:
                    value = audio_file[tag]
                    metadata['title'] = str(value[0]) if isinstance(value, list) else str(value)
                    break
                    
            # Extract artist
            for tag in artist_tags:
                if tag in audio_file:
                    value = audio_file[tag]
                    metadata['artist'] = str(value[0]) if isinstance(value, list) else str(value)
                    break
                    
            # Extract album
            for tag in album_tags:
                if tag in audio_file:
                    value = audio_file[tag]
                    metadata['album'] = str(value[0]) if isinstance(value, list) else str(value)
                    break
                    
            return metadata
            
        except ImportError:
            print("⚠️ Mutagen not available - basic metadata extraction disabled")
            return {}
        except Exception as e:
            print(f"⚠️ Error extracting metadata from {track_path}: {e}")
            return {}
    
    def analyze_track(self, track_path: str, force_reanalysis: bool = False) -> EnhancedAnalysisResult:
        """Perform complete analysis on a single track
        
        Args:
            track_path: Path to the audio file
            force_reanalysis: Whether to force re-analysis even if cached results exist
            
        Returns:
            Complete analysis results
        """
        start_time = time.time()
        
        try:
            # POML Quality Gate: Input validation
            if not isinstance(track_path, str) or not track_path.strip():
                raise ValueError("Track path must be non-empty string")
                
            path_obj = Path(track_path)
            if not path_obj.exists():
                raise FileNotFoundError(f"Track file not found: {track_path}")
                
            # Get track metadata
            metadata = self._get_track_metadata(track_path)
                
            # Check for existing analysis unless forced
            if not force_reanalysis:
                existing = self._get_existing_analysis(track_path)
                if existing is not None:
                    # Update existing result with metadata
                    existing.title = metadata['title']
                    existing.artist = metadata['artist']
                    existing.album = metadata['album']
                    existing.bpm = metadata['bpm']
                    existing.key = metadata['key']
                    return existing
            
            # Perform HAMMS analysis
            print(f"Analyzing track: {path_obj.name}")
            hamms_result = self.hamms_analyzer.analyze_track(track_path)
            
            # POML Quality Gate: Validate HAMMS results
            if not hamms_result.get('success', False):
                error_msg = hamms_result.get('error', 'HAMMS analysis failed')
                return EnhancedAnalysisResult(
                    track_path=track_path,
                    success=False,
                    title=metadata['title'],
                    artist=metadata['artist'],
                    album=metadata['album'],
                    bpm=metadata['bpm'],
                    key=metadata['key'],
                    hamms_vector=[0.0] * 12,
                    hamms_confidence=0.0,
                    hamms_dimensions={},
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    error_message=error_msg
                )
            
            # Extract HAMMS data
            hamms_vector = hamms_result.get('hamms_vector', [0.0] * 12)
            hamms_confidence = hamms_result.get('confidence', 0.0)
            hamms_dimensions = hamms_result.get('dimensions', {})
            
            # Initialize result with HAMMS data and metadata
            result = EnhancedAnalysisResult(
                track_path=track_path,
                success=True,
                title=metadata['title'],
                artist=metadata['artist'],
                album=metadata['album'],
                bpm=metadata['bpm'] or hamms_dimensions.get('bpm'),
                key=metadata['key'] or hamms_dimensions.get('key'),
                hamms_vector=hamms_vector,
                hamms_confidence=hamms_confidence,
                hamms_dimensions=hamms_dimensions
            )
            
            # Perform AI enrichment if enabled
            if self.enable_ai and self.ai_enricher is not None:
                try:
                    print(f"  AI enrichment: {path_obj.name}")
                    ai_result = self._perform_ai_analysis(hamms_result)
                    
                    # Update result with AI data
                    result.genre = ai_result.get('genre')
                    result.subgenre = ai_result.get('subgenre') 
                    result.mood = ai_result.get('mood')
                    result.era = ai_result.get('era')
                    result.tags = ai_result.get('tags', [])
                    result.ai_confidence = ai_result.get('confidence')
                    
                except Exception as e:
                    print(f"  WARNING: AI enrichment failed: {e}")
                    result.ai_confidence = 0.0
            
            # Store results in database
            self._store_analysis_results(result)
            
            # Update processing time
            result.processing_time_ms = int((time.time() - start_time) * 1000)
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"ERROR: Analysis failed for {track_path}: {error_msg}")
            
            # Get metadata even on error
            try:
                metadata = self._get_track_metadata(track_path)
            except:
                metadata = {'title': Path(track_path).stem, 'artist': "Unknown Artist", 'album': "Unknown Album", 'bpm': None, 'key': None}
            
            return EnhancedAnalysisResult(
                track_path=track_path,
                success=False,
                title=metadata['title'],
                artist=metadata['artist'],
                album=metadata['album'],
                bpm=metadata['bpm'],
                key=metadata['key'],
                hamms_vector=[0.0] * 12,
                hamms_confidence=0.0,
                hamms_dimensions={},
                processing_time_ms=int((time.time() - start_time) * 1000),
                error_message=error_msg
            )
    
    def _get_existing_analysis(self, track_path: str) -> Optional[EnhancedAnalysisResult]:
        """Check for existing analysis results in the database
        
        Args:
            track_path: Path to the audio file
            
        Returns:
            Existing analysis results or None if not found
        """
        try:
            # Get track from database
            track = self.storage.get_track_by_path(track_path)
            if not track:
                return None
                
            # Check for HAMMS analysis
            if not hasattr(track, 'hamms_advanced') or not track.hamms_advanced:
                return None
                
            hamms_data = track.hamms_advanced
            
            # Build result from stored data
            result = EnhancedAnalysisResult(
                track_path=track_path,
                success=True,
                title=track.title,
                artist=track.artist,
                album=track.album,
                bpm=track.bpm,
                key=track.initial_key,
                hamms_vector=hamms_data.get_vector_12d(),
                hamms_confidence=hamms_data.ml_confidence or 0.0,
                hamms_dimensions=hamms_data.get_dimension_scores()
            )
            
            # Add AI analysis if available
            if hasattr(track, 'ai_analysis') and track.ai_analysis:
                ai_data = track.ai_analysis
                result.genre = ai_data.genre
                result.subgenre = ai_data.subgenre
                result.mood = ai_data.mood
                result.era = ai_data.era
                result.tags = ai_data.get_tags()
                result.ai_confidence = ai_data.ai_confidence
            
            print(f"  Using cached analysis: {Path(track_path).name}")
            return result
            
        except Exception as e:
            print(f"  WARNING: Failed to load cached analysis: {e}")
            return None
    
    def _perform_ai_analysis(self, hamms_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI enrichment analysis
        
        Args:
            hamms_result: Results from HAMMS analysis
            
        Returns:
            AI analysis results
        """
        # POML Quality Gate: Validate AI enricher
        if not self.ai_enricher:
            raise RuntimeError("AI enricher not available")
            
        # Prepare track data for AI analysis
        track_data = {
            'hamms_vector': hamms_result.get('hamms_vector', [0.0] * 12),
            'bpm': hamms_result.get('bpm', 0),
            'key': hamms_result.get('key', 'Unknown'),
            'energy': hamms_result.get('energy', 0.0),
            'title': hamms_result.get('title', 'Unknown'),
            'artist': hamms_result.get('artist', 'Unknown')
        }
        
        # Perform AI analysis
        enrichment_result = self.ai_enricher.analyze_track(track_data)
        
        # POML Quality Gate: Check for AI errors
        if not enrichment_result.success:
            raise RuntimeError(f"AI analysis failed: {enrichment_result.error_message}")
            
        # Convert enrichment result to expected format
        ai_result = {
            'genre': enrichment_result.genre,
            'subgenre': enrichment_result.subgenre,
            'mood': enrichment_result.mood,
            'era': enrichment_result.era,
            'tags': enrichment_result.tags,
            'confidence': enrichment_result.ai_confidence,
            'ai_model': enrichment_result.ai_model,
            'provider': enrichment_result.provider,
            'processing_time_ms': enrichment_result.processing_time_ms,
            'cost_estimate': enrichment_result.cost_estimate
        }
            
        return ai_result
    
    def _store_analysis_results(self, result: EnhancedAnalysisResult) -> None:
        """Store analysis results in the database
        
        Args:
            result: Complete analysis results to store
        """
        try:
            with self.storage.session() as session:
                # Get or create track record
                track = self.storage.get_track_by_path(result.track_path)
                if not track:
                    track = self.storage.upsert_track(result.track_path)
                
                # Store HAMMS analysis
                hamms_record = HAMMSAdvanced()
                hamms_record.track_id = track.id
                hamms_record.set_vector_12d(result.hamms_vector)
                hamms_record.set_dimension_scores(result.hamms_dimensions)
                hamms_record.ml_confidence = result.hamms_confidence
                
                # Store or update existing HAMMS record
                existing_hamms = session.query(HAMMSAdvanced).filter_by(track_id=track.id).first()
                if existing_hamms:
                    existing_hamms.set_vector_12d(result.hamms_vector)
                    existing_hamms.set_dimension_scores(result.hamms_dimensions)
                    existing_hamms.ml_confidence = result.hamms_confidence
                else:
                    session.add(hamms_record)
                
                # Store AI analysis if available
                if result.genre is not None:
                    # Prepare AI response data for storage
                    ai_response_data = {
                        'genre': result.genre,
                        'subgenre': result.subgenre,
                        'mood': result.mood,
                        'era': result.era,
                        'tags': result.tags,
                        'confidence': result.ai_confidence
                    }
                    
                    # Create AI analysis record
                    ai_record = AIAnalysis.from_openai_response(
                        track_id=track.id,
                        response_data=ai_response_data,
                        processing_time_ms=result.processing_time_ms
                    )
                    
                    # Store or update existing AI record
                    existing_ai = session.query(AIAnalysis).filter_by(track_id=track.id).first()
                    if existing_ai:
                        existing_ai.genre = result.genre
                        existing_ai.subgenre = result.subgenre
                        existing_ai.mood = result.mood
                        existing_ai.era = result.era
                        existing_ai.set_tags(result.tags)
                        existing_ai.ai_confidence = result.ai_confidence
                    else:
                        session.add(ai_record)
                
                session.commit()
                
                # Write metadata to audio file after successful database storage
                if result.success and result.genre is not None:
                    self._write_metadata_to_file(result)
                
        except Exception as e:
            print(f"WARNING: Failed to store analysis results: {e}")
            # Don't raise - allow the analysis to complete even if storage fails
    
    def batch_analyze(self, track_paths: List[str], force_reanalysis: bool = False) -> List[EnhancedAnalysisResult]:
        """Analyze multiple tracks in batch
        
        Args:
            track_paths: List of paths to audio files
            force_reanalysis: Whether to force re-analysis of existing tracks
            
        Returns:
            List of analysis results in the same order as input
        """
        # POML Quality Gate: Input validation
        if not isinstance(track_paths, list):
            raise ValueError(f"Track paths must be list, got {type(track_paths)}")
            
        if len(track_paths) == 0:
            return []
            
        results = []
        print(f"Starting batch analysis of {len(track_paths)} tracks...")
        
        for i, track_path in enumerate(track_paths, 1):
            print(f"\n[{i}/{len(track_paths)}] Processing: {Path(track_path).name}")
            
            result = self.analyze_track(track_path, force_reanalysis)
            results.append(result)
            
            # Brief pause between tracks to be respectful to APIs
            if i < len(track_paths) and self.enable_ai:
                time.sleep(0.5)
        
        # Summary
        successful = sum(1 for r in results if r.success)
        print(f"\nBatch analysis complete: {successful}/{len(results)} tracks successful")
        
        return results
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of analysis results in the database
        
        Returns:
            Summary statistics
        """
        with self.storage.session() as session:
            total_tracks = session.query(HAMMSAdvanced).count()
            total_ai = session.query(AIAnalysis).count()
            
            # Get genre distribution
            genre_counts = {}
            for record in session.query(AIAnalysis).all():
                if record.genre:
                    genre_counts[record.genre] = genre_counts.get(record.genre, 0) + 1
            
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'total_tracks_analyzed': total_tracks,
                'total_ai_enriched': total_ai,
                'ai_coverage_percent': round((total_ai / total_tracks * 100) if total_tracks > 0 else 0, 1),
                'top_genres': top_genres,
                'ai_enabled': self.enable_ai
            }
    
    def _write_metadata_to_file(self, result: EnhancedAnalysisResult) -> None:
        """Write analysis results to audio file metadata
        
        Args:
            result: Analysis results to write to file
        """
        try:
            # Prepare metadata dictionary
            metadata = {
                'genre': result.genre,
                'subgenre': result.subgenre,
                'mood': result.mood,
                'era': result.era,
                'tags': ', '.join(result.tags) if result.tags else None
            }
            
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            if metadata:
                success = metadata_writer.write_analysis_to_file(result.track_path, metadata)
                if success:
                    print(f"  ✓ Metadata written to file: {Path(result.track_path).name}")
                else:
                    print(f"  ⚠️ Failed to write metadata to: {Path(result.track_path).name}")
            
        except Exception as e:
            print(f"  ⚠️ Error writing metadata to {result.track_path}: {str(e)}")
            # Don't raise - metadata writing failure shouldn't stop the analysis


def create_enhanced_analyzer(db_path: str = "data/music.db", enable_ai: bool = True) -> EnhancedAnalyzer:
    """Create an enhanced analyzer instance
    
    Args:
        db_path: Path to the SQLite database
        enable_ai: Whether to enable AI enrichment
        
    Returns:
        Configured enhanced analyzer
    """
    storage = Storage.from_path(db_path)
    return EnhancedAnalyzer(storage, enable_ai)