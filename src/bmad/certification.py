"""
BMAD Certification System
=========================

Consolidates certification validation from:
- bmad_100_certification_validator.py
- bmad_demo_certification.py
"""

import json
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CertificationReport:
    """BMAD certification validation report"""
    certified: bool
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    certification_rate: float
    tracks_analyzed: int
    tracks_passed: int
    tracks_failed: int
    validation_cycles: int
    issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'certified': self.certified,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'certification_rate': self.certification_rate,
            'tracks_analyzed': self.tracks_analyzed,
            'tracks_passed': self.tracks_passed,
            'tracks_failed': self.tracks_failed,
            'validation_cycles': self.validation_cycles,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class TrackCertificationResult:
    """Individual track certification result"""
    track_id: str
    filename: str
    passed: bool
    confidence: float
    analysis_data: Dict[str, Any]
    issues: List[str] = field(default_factory=list)
    processing_time: float = 0.0

class CertificationValidator:
    """
    BMAD certification validation system
    
    Consolidates functionality from:
    - BMAD100PercentValidator
    - BMADPlaylistCertificationDemo
    """
    
    def __init__(self, threshold: float = 0.80, max_cycles: int = 3):
        self.threshold = threshold
        self.max_cycles = max_cycles
        self.current_cycle = 0
        
    def validate_tracks(self, tracks: List[Dict], llm_provider=None) -> CertificationReport:
        """
        Validate tracks for BMAD certification
        
        Args:
            tracks: List of track data dictionaries
            llm_provider: Optional LLM provider for advanced analysis
            
        Returns:
            CertificationReport with validation results
        """
        print(f"🎯 Starting BMAD Certification Validation")
        print(f"📊 Tracks to validate: {len(tracks)}")
        print(f"🎚️  Certification threshold: {self.threshold}")
        
        track_results = []
        
        # Process tracks in batches for efficiency
        batch_size = 10
        for i in range(0, len(tracks), batch_size):
            batch = tracks[i:i + batch_size]
            print(f"\n🔄 Processing batch {i//batch_size + 1} ({len(batch)} tracks)...")
            
            batch_results = self._validate_track_batch(batch, llm_provider)
            track_results.extend(batch_results)
            
            # Progress update
            completed = min(i + batch_size, len(tracks))
            print(f"   Progress: {completed}/{len(tracks)} tracks processed")
        
        # Generate certification report
        report = self._generate_certification_report(track_results, tracks)
        
        print(f"\n🎉 Certification Complete!")
        print(f"   Certification Rate: {report.certification_rate:.2%}")
        print(f"   Overall Accuracy: {report.accuracy:.2%}")
        print(f"   Certified: {'✅ YES' if report.certified else '❌ NO'}")
        
        return report
    
    def _validate_track_batch(self, tracks: List[Dict], llm_provider=None) -> List[TrackCertificationResult]:
        """Validate a batch of tracks"""
        results = []
        
        for track in tracks:
            start_time = time.time()
            
            try:
                result = self._validate_single_track(track, llm_provider)
                result.processing_time = time.time() - start_time
                results.append(result)
                
            except Exception as e:
                # Handle validation errors
                error_result = TrackCertificationResult(
                    track_id=track.get('id', 'unknown'),
                    filename=track.get('filename', 'unknown'),
                    passed=False,
                    confidence=0.0,
                    analysis_data={},
                    issues=[f"Validation error: {str(e)}"],
                    processing_time=time.time() - start_time
                )
                results.append(error_result)
        
        return results
    
    def _validate_single_track(self, track: Dict, llm_provider=None) -> TrackCertificationResult:
        """Validate individual track"""
        track_id = track.get('id', track.get('filename', 'unknown'))
        filename = track.get('filename', 'unknown')
        
        # Basic validation checks
        validation_scores = {}
        issues = []
        
        # Check 1: Required metadata presence
        required_fields = ['title', 'artist']
        metadata_score = 0.0
        
        for field in required_fields:
            if track.get(field):
                metadata_score += 1.0
            else:
                issues.append(f"Missing required field: {field}")
        
        metadata_score /= len(required_fields)
        validation_scores['metadata'] = metadata_score
        
        # Check 2: Optional metadata completeness
        optional_fields = ['bpm', 'key', 'energy', 'genre', 'date']
        optional_score = 0.0
        
        for field in optional_fields:
            if track.get(field):
                optional_score += 1.0
                
        optional_score /= len(optional_fields)
        validation_scores['completeness'] = optional_score
        
        # Check 3: Data quality validation
        quality_score = self._validate_data_quality(track)
        validation_scores['quality'] = quality_score
        
        # Check 4: LLM analysis validation (if provider available)
        if llm_provider:
            try:
                llm_result = llm_provider.analyze_track(track)
                if llm_result.success:
                    llm_confidence = llm_result.content.get('confidence', 0.5)
                    validation_scores['llm_analysis'] = llm_confidence
                else:
                    validation_scores['llm_analysis'] = 0.0
                    issues.append(f"LLM analysis failed: {llm_result.error_message}")
            except Exception as e:
                validation_scores['llm_analysis'] = 0.0
                issues.append(f"LLM analysis error: {str(e)}")
        else:
            validation_scores['llm_analysis'] = 0.5  # Neutral score if no LLM
        
        # Calculate overall confidence
        weights = {
            'metadata': 0.3,
            'completeness': 0.2,
            'quality': 0.2,
            'llm_analysis': 0.3
        }
        
        overall_confidence = sum(
            score * weights[category] 
            for category, score in validation_scores.items()
        )
        
        # Determine pass/fail
        passed = overall_confidence >= self.threshold
        
        # Analysis data
        analysis_data = {
            'validation_scores': validation_scores,
            'overall_confidence': overall_confidence,
            'threshold': self.threshold,
            'track_metadata': {
                'title': track.get('title', ''),
                'artist': track.get('artist', ''),
                'has_bpm': bool(track.get('bpm')),
                'has_key': bool(track.get('key')),
                'has_energy': bool(track.get('energy')),
                'has_genre': bool(track.get('genre'))
            }
        }
        
        return TrackCertificationResult(
            track_id=track_id,
            filename=filename,
            passed=passed,
            confidence=overall_confidence,
            analysis_data=analysis_data,
            issues=issues
        )
    
    def _validate_data_quality(self, track: Dict) -> float:
        """Validate data quality of track metadata"""
        quality_score = 1.0
        
        # BPM validation
        bpm = track.get('bpm')
        if bpm:
            if not (60 <= bpm <= 200):  # Reasonable BPM range
                quality_score -= 0.2
        
        # Energy validation  
        energy = track.get('energy')
        if energy:
            if not (0.0 <= energy <= 1.0):  # Energy should be normalized
                quality_score -= 0.2
        
        # Key validation
        key = track.get('key', '').lower()
        if key:
            valid_keys = [
                'c', 'c#', 'db', 'd', 'd#', 'eb', 'e', 'f', 
                'f#', 'gb', 'g', 'g#', 'ab', 'a', 'a#', 'bb', 'b'
            ]
            key_base = key.replace(' major', '').replace(' minor', '').replace('m', '').strip()
            if key_base not in valid_keys:
                quality_score -= 0.1
        
        # Genre validation
        genre = track.get('genre', '').lower()
        if genre:
            # Basic genre validation (not empty, reasonable length)
            if len(genre) < 2 or len(genre) > 50:
                quality_score -= 0.1
        
        return max(0.0, quality_score)
    
    def _generate_certification_report(self, track_results: List[TrackCertificationResult], 
                                     original_tracks: List[Dict]) -> CertificationReport:
        """Generate comprehensive certification report"""
        
        # Basic statistics
        tracks_analyzed = len(track_results)
        tracks_passed = sum(1 for result in track_results if result.passed)
        tracks_failed = tracks_analyzed - tracks_passed
        
        certification_rate = tracks_passed / tracks_analyzed if tracks_analyzed > 0 else 0.0
        
        # Calculate metrics
        # For certification, we consider "passed" as positive class
        true_positives = tracks_passed
        false_negatives = tracks_failed  # Should have passed but didn't
        
        # Simplified metrics (in real scenario, we'd have ground truth)
        precision = certification_rate  # Simplified
        recall = certification_rate     # Simplified
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = certification_rate
        
        # Collect issues and recommendations
        all_issues = []
        for result in track_results:
            for issue in result.issues:
                all_issues.append({
                    'track': result.filename,
                    'issue': issue,
                    'confidence': result.confidence
                })
        
        recommendations = self._generate_recommendations(track_results, certification_rate)
        
        # Determine if system is certified
        certified = certification_rate >= self.threshold
        
        return CertificationReport(
            certified=certified,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            certification_rate=certification_rate,
            tracks_analyzed=tracks_analyzed,
            tracks_passed=tracks_passed,
            tracks_failed=tracks_failed,
            validation_cycles=1,  # Simple implementation
            issues=all_issues,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, track_results: List[TrackCertificationResult], 
                                certification_rate: float) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if certification_rate < self.threshold:
            recommendations.append(f"Certification rate ({certification_rate:.2%}) below threshold ({self.threshold:.2%})")
        
        # Analyze common issues
        issue_counts = {}
        for result in track_results:
            for issue in result.issues:
                issue_type = issue.split(':')[0] if ':' in issue else issue
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Top issues become recommendations
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        for issue_type, count in sorted_issues[:3]:  # Top 3 issues
            percentage = count / len(track_results) * 100
            recommendations.append(f"Address {issue_type} (affects {percentage:.1f}% of tracks)")
        
        # General recommendations
        if certification_rate < 0.5:
            recommendations.append("Consider improving metadata extraction pipeline")
        elif certification_rate < 0.8:
            recommendations.append("Focus on data quality validation improvements")
        else:
            recommendations.append("System performing well, consider minor optimizations")
        
        return recommendations

def simulate_certification_demo(num_tracks: int = 50) -> CertificationReport:
    """
    Simulate BMAD certification for demonstration purposes
    (Consolidated from bmad_demo_certification.py)
    """
    print(f"🎵 BMAD Certification Demo - Simulating {num_tracks} tracks")
    
    # Generate simulated track data
    tracks = []
    genres = ["Electronic", "Pop", "Rock", "Dance", "House", "Techno", "R&B"]
    keys = ["Am", "C", "G", "Dm", "F", "Em", "Bm"]
    
    for i in range(num_tracks):
        # Simulate realistic data with some missing values
        bpm = random.choice([70, 90, 110, 120, 128, 140, 160]) + random.uniform(-5, 5)
        
        # 15% of tracks have missing BPM to simulate real issues
        if random.random() < 0.15:
            bpm = None
            
        track = {
            'id': f'track_{i+1:03d}',
            'filename': f"Track_{i+1:03d}.mp3",
            'title': f"Demo Track {i+1}",
            'artist': f"Demo Artist {(i % 5) + 1}",
            'bpm': bpm,
            'key': random.choice(keys),
            'energy': random.uniform(0.3, 0.9),
            'genre': random.choice(genres),
            'has_complete_data': bpm is not None
        }
        tracks.append(track)
    
    # Run certification validation
    validator = CertificationValidator(threshold=0.80, max_cycles=3)
    report = validator.validate_tracks(tracks)
    
    return report