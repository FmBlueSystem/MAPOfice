"""Audio Metadata Writer Service

This module provides functionality to write genre, subgenre, and other analysis
results directly to audio file metadata/tags.

Supports: MP3, FLAC, OGG, MP4/M4A, and other formats via mutagen
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AudioMetadataWriter:
    """Service to write analysis results to audio file metadata"""
    
    def __init__(self):
        """Initialize metadata writer"""
        try:
            import mutagen
            from mutagen.id3 import ID3NoHeaderError, ID3, TCON, TPOS, TXXX
            from mutagen.flac import FLAC
            from mutagen.oggvorbis import OggVorbis  
            from mutagen.mp4 import MP4
            
            self.mutagen = mutagen
            self.ID3NoHeaderError = ID3NoHeaderError
            self.ID3 = ID3
            self.TCON = TCON  # Genre
            self.TPOS = TPOS  # Disc number (we'll use for subgenre)
            self.TXXX = TXXX  # User-defined text
            self.FLAC = FLAC
            self.OggVorbis = OggVorbis
            self.MP4 = MP4
            
            self.available = True
            logger.info("✓ Mutagen available - metadata writing enabled")
            
        except ImportError:
            self.available = False
            logger.warning("⚠️ Mutagen not available - metadata writing disabled")
    
    def write_analysis_to_file(self, file_path: str, analysis_data: Dict[str, Any]) -> bool:
        """
        Write analysis results to audio file metadata
        
        Args:
            file_path: Path to audio file
            analysis_data: Dictionary containing genre, subgenre, mood, etc.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            logger.error("Mutagen not available - cannot write metadata")
            return False
            
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        try:
            # Create backup info
            logger.info(f"📝 Writing metadata to: {Path(file_path).name}")
            
            # Get file extension
            ext = Path(file_path).suffix.lower()
            
            if ext == '.mp3':
                return self._write_mp3_metadata(file_path, analysis_data)
            elif ext == '.flac':
                return self._write_flac_metadata(file_path, analysis_data)
            elif ext in ['.ogg', '.oga']:
                return self._write_ogg_metadata(file_path, analysis_data)
            elif ext in ['.m4a', '.mp4', '.aac']:
                return self._write_mp4_metadata(file_path, analysis_data)
            else:
                logger.warning(f"Unsupported format for metadata writing: {ext}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing metadata to {file_path}: {str(e)}")
            return False
    
    def _write_mp3_metadata(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Write metadata to MP3 file"""
        try:
            # Load or create ID3 tags
            try:
                tags = self.ID3(file_path)
            except self.ID3NoHeaderError:
                tags = self.ID3()
            
            # Write genre
            if data.get('genre'):
                tags.add(self.TCON(encoding=3, text=[data['genre']]))
                logger.info(f"  📁 Genre: {data['genre']}")
            
            # Write subgenre as custom field
            if data.get('subgenre'):
                tags.add(self.TXXX(encoding=3, desc='SUBGENRE', text=[data['subgenre']]))
                logger.info(f"  🎵 Subgenre: {data['subgenre']}")
            
            # Write mood as custom field
            if data.get('mood'):
                tags.add(self.TXXX(encoding=3, desc='MOOD', text=[data['mood']]))
                logger.info(f"  😊 Mood: {data['mood']}")
                
            # Write era as custom field
            if data.get('era'):
                tags.add(self.TXXX(encoding=3, desc='ERA', text=[data['era']]))
                logger.info(f"  📅 Era: {data['era']}")
                
            # Write AI analysis marker
            tags.add(self.TXXX(encoding=3, desc='AI_ANALYZED', text=['Music Analyzer Pro v3.0']))
            
            # Save tags
            tags.save(file_path)
            return True
            
        except Exception as e:
            logger.error(f"Error writing MP3 metadata: {str(e)}")
            return False
    
    def _write_flac_metadata(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Write metadata to FLAC file"""
        try:
            audio = self.FLAC(file_path)
            
            # Write genre
            if data.get('genre'):
                audio['GENRE'] = data['genre']
                logger.info(f"  📁 Genre: {data['genre']}")
            
            # Write subgenre
            if data.get('subgenre'):
                audio['SUBGENRE'] = data['subgenre']
                logger.info(f"  🎵 Subgenre: {data['subgenre']}")
            
            # Write mood
            if data.get('mood'):
                audio['MOOD'] = data['mood']
                logger.info(f"  😊 Mood: {data['mood']}")
                
            # Write era
            if data.get('era'):
                audio['ERA'] = data['era']
                logger.info(f"  📅 Era: {data['era']}")
                
            # Write AI analysis marker
            audio['AI_ANALYZED'] = 'Music Analyzer Pro v3.0'
            
            # Save
            audio.save()
            return True
            
        except Exception as e:
            logger.error(f"Error writing FLAC metadata: {str(e)}")
            return False
    
    def _write_ogg_metadata(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Write metadata to OGG file"""
        try:
            audio = self.OggVorbis(file_path)
            
            # Write genre
            if data.get('genre'):
                audio['GENRE'] = data['genre']
                logger.info(f"  📁 Genre: {data['genre']}")
            
            # Write subgenre
            if data.get('subgenre'):
                audio['SUBGENRE'] = data['subgenre']
                logger.info(f"  🎵 Subgenre: {data['subgenre']}")
            
            # Write mood
            if data.get('mood'):
                audio['MOOD'] = data['mood']
                logger.info(f"  😊 Mood: {data['mood']}")
                
            # Write era
            if data.get('era'):
                audio['ERA'] = data['era']
                logger.info(f"  📅 Era: {data['era']}")
                
            # Write AI analysis marker
            audio['AI_ANALYZED'] = 'Music Analyzer Pro v3.0'
            
            # Save
            audio.save()
            return True
            
        except Exception as e:
            logger.error(f"Error writing OGG metadata: {str(e)}")
            return False
    
    def _write_mp4_metadata(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Write metadata to MP4/M4A file"""
        try:
            audio = self.MP4(file_path)
            
            # Write genre
            if data.get('genre'):
                audio['\xa9gen'] = data['genre']  # MP4 genre tag
                logger.info(f"  📁 Genre: {data['genre']}")
            
            # Write custom fields for subgenre, mood, era
            if data.get('subgenre'):
                audio['----:com.apple.iTunes:SUBGENRE'] = data['subgenre'].encode('utf-8')
                logger.info(f"  🎵 Subgenre: {data['subgenre']}")
            
            if data.get('mood'):
                audio['----:com.apple.iTunes:MOOD'] = data['mood'].encode('utf-8')
                logger.info(f"  😊 Mood: {data['mood']}")
                
            if data.get('era'):
                audio['----:com.apple.iTunes:ERA'] = data['era'].encode('utf-8')
                logger.info(f"  📅 Era: {data['era']}")
                
            # Write AI analysis marker
            audio['----:com.apple.iTunes:AI_ANALYZED'] = 'Music Analyzer Pro v3.0'.encode('utf-8')
            
            # Save
            audio.save()
            return True
            
        except Exception as e:
            logger.error(f"Error writing MP4 metadata: {str(e)}")
            return False
    
    def batch_write_metadata(self, analysis_results: list) -> Dict[str, int]:
        """
        Write metadata to multiple files
        
        Args:
            analysis_results: List of dicts with 'file_path' and analysis data
            
        Returns:
            Dict with success/failure counts
        """
        if not self.available:
            return {'success': 0, 'failed': 0, 'error': 'Mutagen not available'}
        
        stats = {'success': 0, 'failed': 0}
        
        for result in analysis_results:
            file_path = result.get('file_path')
            if not file_path:
                continue
                
            if self.write_analysis_to_file(file_path, result):
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        logger.info(f"📊 Batch metadata writing complete: {stats['success']} success, {stats['failed']} failed")
        return stats


# Global instance
metadata_writer = AudioMetadataWriter()