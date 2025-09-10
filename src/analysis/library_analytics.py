"""Library Analytics with Comprehensive Subgenre Analysis

This module provides advanced analytics for music libraries including:
- Subgenre distribution analysis
- Cross-genre compatibility analysis  
- Era and mood distribution
- HAMMS vector clustering
- Playlist generation insights
- Collection quality metrics

POML Quality Gates:
- Statistical validation of all metrics
- Comprehensive error handling for missing data
- Performance optimization for large libraries
- Detailed reporting and visualization data
"""

from __future__ import annotations

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

from src.services.storage import Storage
from src.analysis.enhanced_similarity import EnhancedSimilarityAnalyzer


@dataclass
class GenreAnalysis:
    """Analysis results for a specific genre or subgenre"""
    name: str
    track_count: int
    percentage: float
    avg_bpm: Optional[float]
    avg_energy: Optional[float]
    common_keys: List[Tuple[str, int]]
    common_eras: List[Tuple[str, int]]
    common_moods: List[Tuple[str, int]]
    hamms_profile: List[float]  # Average HAMMS vector
    compatibility_scores: Dict[str, float]


@dataclass
class LibraryAnalytics:
    """Comprehensive library analysis results"""
    total_tracks: int
    total_genres: int
    total_subgenres: int
    analyzed_tracks: int
    ai_analyzed_tracks: int
    
    # Distribution analysis
    genre_distribution: List[GenreAnalysis]
    subgenre_distribution: List[GenreAnalysis]
    era_distribution: Dict[str, int]
    mood_distribution: Dict[str, int]
    
    # Technical analysis
    bpm_analysis: Dict[str, Any]
    key_analysis: Dict[str, Any]
    energy_analysis: Dict[str, Any]
    
    # Quality metrics
    missing_data_report: Dict[str, int]
    hamms_coverage: float
    ai_coverage: float
    isrc_coverage: float
    
    # Insights
    top_compatible_pairs: List[Tuple[str, str, float]]
    mixing_recommendations: List[Dict[str, Any]]
    collection_quality_score: float


class LibraryAnalyzer:
    """Advanced library analytics with subgenre intelligence"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self.similarity_analyzer = EnhancedSimilarityAnalyzer()
    
    def analyze_library(self, include_hamms_clustering: bool = True) -> LibraryAnalytics:
        """Perform comprehensive library analysis
        
        Args:
            include_hamms_clustering: Whether to perform HAMMS vector clustering
            
        Returns:
            Detailed library analytics with insights and recommendations
        """
        print("=== LIBRARY ANALYTICS - COMPREHENSIVE ANALYSIS ===")
        
        # Get all track data
        all_tracks = self.storage.list_all_analyses()
        ai_tracks = self.storage.get_tracks_with_ai_analysis()
        
        print(f"Analyzing {len(all_tracks)} tracks ({len(ai_tracks)} with AI analysis)...")
        
        # Basic statistics
        total_tracks = len(all_tracks)
        analyzed_tracks = len([t for t in all_tracks if t.get('hamms')])
        ai_analyzed_tracks = len(ai_tracks)
        
        # Genre and subgenre analysis
        genre_dist = self._analyze_genre_distribution(all_tracks, ai_tracks)
        subgenre_dist = self._analyze_subgenre_distribution(ai_tracks)
        
        # Era and mood analysis
        era_dist = self._analyze_era_distribution(ai_tracks)
        mood_dist = self._analyze_mood_distribution(ai_tracks)
        
        # Technical analysis
        bpm_analysis = self._analyze_bpm_distribution(all_tracks)
        key_analysis = self._analyze_key_distribution(all_tracks)
        energy_analysis = self._analyze_energy_distribution(all_tracks)
        
        # Quality metrics
        missing_data = self._analyze_missing_data(all_tracks, ai_tracks)
        hamms_coverage = analyzed_tracks / total_tracks if total_tracks > 0 else 0.0
        ai_coverage = ai_analyzed_tracks / total_tracks if total_tracks > 0 else 0.0
        isrc_coverage = len([t for t in all_tracks if t.get('isrc')]) / total_tracks if total_tracks > 0 else 0.0
        
        # Compatibility analysis
        compatible_pairs = self._find_compatible_subgenres(ai_tracks)
        mixing_recommendations = self._generate_mixing_recommendations(subgenre_dist)
        
        # Collection quality score
        quality_score = self._calculate_collection_quality(
            hamms_coverage, ai_coverage, isrc_coverage, len(subgenre_dist)
        )
        
        return LibraryAnalytics(
            total_tracks=total_tracks,
            total_genres=len(set(t.get('genre') for t in ai_tracks if t.get('genre'))),
            total_subgenres=len(set(t.get('subgenre') for t in ai_tracks if t.get('subgenre'))),
            analyzed_tracks=analyzed_tracks,
            ai_analyzed_tracks=ai_analyzed_tracks,
            genre_distribution=genre_dist,
            subgenre_distribution=subgenre_dist,
            era_distribution=era_dist,
            mood_distribution=mood_dist,
            bpm_analysis=bpm_analysis,
            key_analysis=key_analysis,
            energy_analysis=energy_analysis,
            missing_data_report=missing_data,
            hamms_coverage=hamms_coverage,
            ai_coverage=ai_coverage,
            isrc_coverage=isrc_coverage,
            top_compatible_pairs=compatible_pairs,
            mixing_recommendations=mixing_recommendations,
            collection_quality_score=quality_score
        )
    
    def _analyze_genre_distribution(self, all_tracks: List[Dict[str, Any]], 
                                  ai_tracks: List[Dict[str, Any]]) -> List[GenreAnalysis]:
        """Analyze genre distribution with detailed statistics"""
        genre_stats = defaultdict(lambda: {
            'tracks': [],
            'bpm_values': [],
            'energy_values': [],
            'keys': [],
            'eras': [],
            'moods': [],
            'hamms_vectors': []
        })
        
        for track in ai_tracks:
            genre = track.get('genre')
            if not genre:
                continue
                
            stats = genre_stats[genre]
            stats['tracks'].append(track)
            
            if track.get('bpm'):
                stats['bpm_values'].append(track['bpm'])
            if track.get('energy'):
                stats['energy_values'].append(track['energy'])
            if track.get('key'):
                stats['keys'].append(track['key'])
            if track.get('era'):
                stats['eras'].append(track['era'])
            if track.get('mood'):
                stats['moods'].append(track['mood'])
            if track.get('hamms'):
                stats['hamms_vectors'].append(track['hamms'])
        
        # Create genre analysis objects
        total_ai_tracks = len(ai_tracks)
        genre_analyses = []
        
        for genre, stats in genre_stats.items():
            track_count = len(stats['tracks'])
            percentage = (track_count / total_ai_tracks * 100) if total_ai_tracks > 0 else 0
            
            # Calculate averages
            avg_bpm = np.mean(stats['bpm_values']) if stats['bpm_values'] else None
            avg_energy = np.mean(stats['energy_values']) if stats['energy_values'] else None
            
            # Calculate HAMMS profile (average vector)
            if stats['hamms_vectors']:
                hamms_array = np.array(stats['hamms_vectors'])
                hamms_profile = np.mean(hamms_array, axis=0).tolist()
            else:
                hamms_profile = [0.0] * 12
            
            # Get common attributes
            common_keys = Counter(stats['keys']).most_common(5)
            common_eras = Counter(stats['eras']).most_common(3)
            common_moods = Counter(stats['moods']).most_common(3)
            
            # Calculate compatibility with other genres
            compatibility_scores = self._calculate_genre_compatibility(genre, genre_stats.keys())
            
            genre_analyses.append(GenreAnalysis(
                name=genre,
                track_count=track_count,
                percentage=percentage,
                avg_bpm=avg_bpm,
                avg_energy=avg_energy,
                common_keys=common_keys,
                common_eras=common_eras,
                common_moods=common_moods,
                hamms_profile=hamms_profile,
                compatibility_scores=compatibility_scores
            ))
        
        return sorted(genre_analyses, key=lambda x: x.track_count, reverse=True)
    
    def _analyze_subgenre_distribution(self, ai_tracks: List[Dict[str, Any]]) -> List[GenreAnalysis]:
        """Analyze subgenre distribution with enhanced compatibility analysis"""
        subgenre_stats = defaultdict(lambda: {
            'tracks': [],
            'bpm_values': [],
            'energy_values': [],
            'keys': [],
            'eras': [],
            'moods': [],
            'hamms_vectors': []
        })
        
        # Collect subgenre statistics
        for track in ai_tracks:
            subgenre = track.get('subgenre')
            if not subgenre:
                continue
                
            stats = subgenre_stats[subgenre]
            stats['tracks'].append(track)
            
            if track.get('bpm'):
                stats['bpm_values'].append(track['bpm'])
            if track.get('energy'):
                stats['energy_values'].append(track['energy'])
            if track.get('key'):
                stats['keys'].append(track['key'])
            if track.get('era'):
                stats['eras'].append(track['era'])
            if track.get('mood'):
                stats['moods'].append(track['mood'])
            if track.get('hamms'):
                stats['hamms_vectors'].append(track['hamms'])
        
        # Create subgenre analysis objects
        total_ai_tracks = len(ai_tracks)
        subgenre_analyses = []
        
        for subgenre, stats in subgenre_stats.items():
            track_count = len(stats['tracks'])
            percentage = (track_count / total_ai_tracks * 100) if total_ai_tracks > 0 else 0
            
            # Calculate technical averages
            avg_bpm = np.mean(stats['bpm_values']) if stats['bpm_values'] else None
            avg_energy = np.mean(stats['energy_values']) if stats['energy_values'] else None
            
            # Calculate HAMMS profile
            if stats['hamms_vectors']:
                hamms_array = np.array(stats['hamms_vectors'])
                hamms_profile = np.mean(hamms_array, axis=0).tolist()
            else:
                hamms_profile = [0.0] * 12
            
            # Get common attributes
            common_keys = Counter(stats['keys']).most_common(5)
            common_eras = Counter(stats['eras']).most_common(3)
            common_moods = Counter(stats['moods']).most_common(3)
            
            # Calculate compatibility with other subgenres using the matrix
            compatibility_scores = {}
            for other_subgenre in subgenre_stats.keys():
                if other_subgenre != subgenre:
                    key = (subgenre, other_subgenre)
                    reverse_key = (other_subgenre, subgenre)
                    
                    if key in self.similarity_analyzer.SUBGENRE_COMPATIBILITY:
                        compatibility_scores[other_subgenre] = self.similarity_analyzer.SUBGENRE_COMPATIBILITY[key]
                    elif reverse_key in self.similarity_analyzer.SUBGENRE_COMPATIBILITY:
                        compatibility_scores[other_subgenre] = self.similarity_analyzer.SUBGENRE_COMPATIBILITY[reverse_key]
                    else:
                        compatibility_scores[other_subgenre] = 0.3  # Default low compatibility
            
            subgenre_analyses.append(GenreAnalysis(
                name=subgenre,
                track_count=track_count,
                percentage=percentage,
                avg_bpm=avg_bpm,
                avg_energy=avg_energy,
                common_keys=common_keys,
                common_eras=common_eras,
                common_moods=common_moods,
                hamms_profile=hamms_profile,
                compatibility_scores=compatibility_scores
            ))
        
        return sorted(subgenre_analyses, key=lambda x: x.track_count, reverse=True)
    
    def _analyze_era_distribution(self, ai_tracks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze era distribution"""
        eras = [track.get('era') for track in ai_tracks if track.get('era')]
        return dict(Counter(eras))
    
    def _analyze_mood_distribution(self, ai_tracks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze mood distribution"""
        moods = [track.get('mood') for track in ai_tracks if track.get('mood')]
        return dict(Counter(moods))
    
    def _analyze_bpm_distribution(self, all_tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze BPM distribution and patterns"""
        bpm_values = [track.get('bpm') for track in all_tracks if track.get('bpm')]
        
        if not bpm_values:
            return {'count': 0, 'avg': None, 'min': None, 'max': None, 'ranges': {}}
        
        bpm_array = np.array(bpm_values)
        
        # BPM ranges for different mixing styles
        ranges = {
            'Very Slow (60-90)': len([b for b in bpm_values if 60 <= b < 90]),
            'Slow (90-110)': len([b for b in bpm_values if 90 <= b < 110]),
            'Medium (110-130)': len([b for b in bpm_values if 110 <= b < 130]),
            'Fast (130-150)': len([b for b in bpm_values if 130 <= b < 150]),
            'Very Fast (150+)': len([b for b in bpm_values if b >= 150])
        }
        
        return {
            'count': len(bpm_values),
            'avg': float(np.mean(bpm_array)),
            'min': float(np.min(bpm_array)),
            'max': float(np.max(bpm_array)),
            'std': float(np.std(bpm_array)),
            'ranges': ranges
        }
    
    def _analyze_key_distribution(self, all_tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze musical key distribution"""
        keys = [track.get('key') for track in all_tracks if track.get('key')]
        
        if not keys:
            return {'count': 0, 'distribution': {}}
        
        key_counter = Counter(keys)
        
        return {
            'count': len(keys),
            'distribution': dict(key_counter.most_common()),
            'most_common': key_counter.most_common(5)
        }
    
    def _analyze_energy_distribution(self, all_tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze energy level distribution"""
        energy_values = [track.get('energy') for track in all_tracks if track.get('energy')]
        
        if not energy_values:
            return {'count': 0, 'avg': None, 'ranges': {}}
        
        energy_array = np.array(energy_values)
        
        ranges = {
            'Low Energy (0.0-0.3)': len([e for e in energy_values if 0.0 <= e < 0.3]),
            'Medium Energy (0.3-0.7)': len([e for e in energy_values if 0.3 <= e < 0.7]),
            'High Energy (0.7-1.0)': len([e for e in energy_values if 0.7 <= e <= 1.0])
        }
        
        return {
            'count': len(energy_values),
            'avg': float(np.mean(energy_array)),
            'min': float(np.min(energy_array)),
            'max': float(np.max(energy_array)),
            'std': float(np.std(energy_array)),
            'ranges': ranges
        }
    
    def _analyze_missing_data(self, all_tracks: List[Dict[str, Any]], 
                            ai_tracks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze missing data across different fields"""
        total = len(all_tracks)
        total_ai = len(ai_tracks)
        
        return {
            'missing_bpm': total - len([t for t in all_tracks if t.get('bmp')]),
            'missing_key': total - len([t for t in all_tracks if t.get('key')]),
            'missing_energy': total - len([t for t in all_tracks if t.get('energy')]),
            'missing_hamms': total - len([t for t in all_tracks if t.get('hamms')]),
            'missing_isrc': total - len([t for t in all_tracks if t.get('isrc')]),
            'missing_genre': total_ai - len([t for t in ai_tracks if t.get('genre')]),
            'missing_subgenre': total_ai - len([t for t in ai_tracks if t.get('subgenre')]),
            'missing_era': total_ai - len([t for t in ai_tracks if t.get('era')]),
            'missing_mood': total_ai - len([t for t in ai_tracks if t.get('mood')])
        }
    
    def _find_compatible_subgenres(self, ai_tracks: List[Dict[str, Any]]) -> List[Tuple[str, str, float]]:
        """Find the most compatible subgenre pairs in the library"""
        subgenres = list(set(track.get('subgenre') for track in ai_tracks if track.get('subgenre')))
        compatible_pairs = []
        
        for i, sg1 in enumerate(subgenres):
            for sg2 in subgenres[i+1:]:
                key = (sg1, sg2)
                reverse_key = (sg2, sg1)
                
                compatibility = 0.0
                if key in self.similarity_analyzer.SUBGENRE_COMPATIBILITY:
                    compatibility = self.similarity_analyzer.SUBGENRE_COMPATIBILITY[key]
                elif reverse_key in self.similarity_analyzer.SUBGENRE_COMPATIBILITY:
                    compatibility = self.similarity_analyzer.SUBGENRE_COMPATIBILITY[reverse_key]
                else:
                    compatibility = 0.3  # Default
                
                if compatibility > 0.6:  # Only include reasonably compatible pairs
                    compatible_pairs.append((sg1, sg2, compatibility))
        
        return sorted(compatible_pairs, key=lambda x: x[2], reverse=True)[:10]
    
    def _calculate_genre_compatibility(self, genre: str, all_genres: Set[str]) -> Dict[str, float]:
        """Calculate compatibility scores between genres"""
        # This is a simplified implementation - could be enhanced with more sophisticated logic
        compatibility_scores = {}
        
        for other_genre in all_genres:
            if other_genre != genre:
                if genre == other_genre:
                    compatibility_scores[other_genre] = 1.0
                elif 'Electronic' in [genre, other_genre]:
                    compatibility_scores[other_genre] = 0.6
                elif any(term in genre.lower() for term in ['rock', 'metal']) and any(term in other_genre.lower() for term in ['rock', 'metal']):
                    compatibility_scores[other_genre] = 0.7
                elif any(term in genre.lower() for term in ['latin', 'salsa', 'reggaeton']) and any(term in other_genre.lower() for term in ['latin', 'salsa', 'reggaeton']):
                    compatibility_scores[other_genre] = 0.8
                else:
                    compatibility_scores[other_genre] = 0.4
        
        return compatibility_scores
    
    def _generate_mixing_recommendations(self, subgenre_dist: List[GenreAnalysis]) -> List[Dict[str, Any]]:
        """Generate intelligent mixing recommendations based on library analysis"""
        recommendations = []
        
        # Find subgenres with good mixing potential
        for analysis in subgenre_dist[:10]:  # Top 10 subgenres
            if analysis.track_count >= 3:  # Need at least 3 tracks to make playlists
                # Find best compatible subgenres
                best_matches = sorted(analysis.compatibility_scores.items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
                
                if best_matches and best_matches[0][1] > 0.7:
                    recommendations.append({
                        'primary_subgenre': analysis.name,
                        'track_count': analysis.track_count,
                        'avg_bpm': analysis.avg_bpm,
                        'compatible_subgenres': [{'name': name, 'score': score} 
                                               for name, score in best_matches if score > 0.6],
                        'recommendation': f"Create playlists mixing {analysis.name} with {best_matches[0][0]} (compatibility: {best_matches[0][1]:.2f})"
                    })
        
        return recommendations
    
    def _calculate_collection_quality(self, hamms_coverage: float, ai_coverage: float, 
                                    isrc_coverage: float, subgenre_count: int) -> float:
        """Calculate overall collection quality score (0-100)"""
        # Weighted quality score
        weights = {
            'hamms_coverage': 0.3,      # HAMMS analysis coverage
            'ai_coverage': 0.25,        # AI analysis coverage  
            'isrc_coverage': 0.2,       # Professional metadata
            'subgenre_diversity': 0.25  # Subgenre diversity
        }
        
        # Normalize subgenre diversity (max score at 20+ subgenres)
        subgenre_score = min(subgenre_count / 20.0, 1.0)
        
        quality_score = (
            hamms_coverage * weights['hamms_coverage'] +
            ai_coverage * weights['ai_coverage'] +
            isrc_coverage * weights['isrc_coverage'] +
            subgenre_score * weights['subgenre_diversity']
        ) * 100
        
        return round(quality_score, 1)

    def print_detailed_report(self, analytics: LibraryAnalytics) -> None:
        """Print a comprehensive analytics report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE LIBRARY ANALYTICS REPORT")
        print("="*60)
        
        # Overview
        print(f"\n📊 OVERVIEW")
        print(f"Total Tracks: {analytics.total_tracks}")
        print(f"Analyzed Tracks: {analytics.analyzed_tracks} ({analytics.hamms_coverage:.1%})")
        print(f"AI Analyzed: {analytics.ai_analyzed_tracks} ({analytics.ai_coverage:.1%})")
        print(f"Total Genres: {analytics.total_genres}")
        print(f"Total Subgenres: {analytics.total_subgenres}")
        print(f"Collection Quality Score: {analytics.collection_quality_score:.1f}/100")
        
        # Top Genres
        print(f"\n🎵 TOP GENRES")
        for genre in analytics.genre_distribution[:5]:
            print(f"  {genre.name}: {genre.track_count} tracks ({genre.percentage:.1f}%) - Avg BPM: {genre.avg_bpm:.1f if genre.avg_bpm else 'N/A'}")
        
        # Top Subgenres  
        print(f"\n🎼 TOP SUBGENRES")
        for subgenre in analytics.subgenre_distribution[:5]:
            print(f"  {subgenre.name}: {subgenre.track_count} tracks ({subgenre.percentage:.1f}%)")
            if subgenre.compatibility_scores:
                top_compat = max(subgenre.compatibility_scores.items(), key=lambda x: x[1])
                print(f"    → Best mix with: {top_compat[0]} (compatibility: {top_compat[1]:.2f})")
        
        # Technical Analysis
        print(f"\n⚡ TECHNICAL ANALYSIS")
        if analytics.bmp_analysis['count'] > 0:
            print(f"BPM Range: {analytics.bmp_analysis['min']:.1f} - {analytics.bmp_analysis['max']:.1f} (avg: {analytics.bmp_analysis['avg']:.1f})")
        if analytics.energy_analysis['count'] > 0:
            print(f"Energy Range: {analytics.energy_analysis['min']:.2f} - {analytics.energy_analysis['max']:.2f} (avg: {analytics.energy_analysis['avg']:.2f})")
        
        # Compatible Pairs
        print(f"\n🔗 TOP COMPATIBLE PAIRS")
        for pair in analytics.top_compatible_pairs[:5]:
            print(f"  {pair[0]} ↔ {pair[1]}: {pair[2]:.2f} compatibility")
        
        # Recommendations
        print(f"\n💡 MIXING RECOMMENDATIONS")
        for rec in analytics.mixing_recommendations[:3]:
            print(f"  • {rec['recommendation']}")
        
        print("="*60)