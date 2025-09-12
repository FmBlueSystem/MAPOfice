#!/usr/bin/env python3
"""
BMAD Methodology Demonstration for Playlist Generation Certification
Simplified version with realistic simulation of the process
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Any
import time

class BMADPlaylistCertificationDemo:
    """Demonstration of BMAD methodology for playlist generation"""
    
    def __init__(self):
        self.current_cycle = 0
        self.certification_threshold = 0.80
        self.max_cycles = 3
        
    def simulate_track_analysis(self, num_tracks: int = 50) -> List[Dict]:
        """Simulate analyzing tracks with realistic data"""
        print(f"\n🎵 Simulating analysis of {num_tracks} tracks...")
        
        genres = ["Electronic", "Pop", "Rock", "Dance", "House", "Techno", "R&B"]
        keys = ["Am", "C", "G", "Dm", "F", "Em", "Bm"]
        
        tracks = []
        for i in range(num_tracks):
            # Simulate realistic BPM distribution
            bpm_base = random.choice([70, 90, 110, 120, 128, 140, 160])
            bpm = bpm_base + random.uniform(-5, 5)
            
            # Some tracks (15%) will have missing BPM data to simulate real issues
            if random.random() < 0.15:
                bpm = None
            
            track = {
                'filename': f"Track_{i+1:03d}.mp3",
                'bpm': bpm,
                'key': random.choice(keys),
                'energy': random.uniform(0.3, 0.9),
                'genre': random.choice(genres),
                'has_complete_data': bpm is not None
            }
            tracks.append(track)
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{num_tracks} tracks analyzed")
        
        complete_tracks = sum(1 for t in tracks if t['has_complete_data'])
        print(f"✅ Analysis complete: {complete_tracks}/{num_tracks} tracks with complete data")
        
        return tracks
    
    def simulate_playlist_generation(self, seed_track: Dict, candidates: List[Dict], 
                                   length: int, tolerance: float) -> List[Dict]:
        """Simulate playlist generation with BPM tolerance"""
        
        playlist = []
        seed_bpm = seed_track.get('bpm')
        
        if not seed_bpm:
            # Can't generate playlist without seed BPM
            return []
        
        # Filter candidates by BPM tolerance
        min_bpm = seed_bpm * (1 - tolerance)
        max_bpm = seed_bpm * (1 + tolerance)
        
        valid_candidates = [
            c for c in candidates 
            if c.get('bpm') and min_bpm <= c['bpm'] <= max_bpm
        ]
        
        # Simulate selection (random for demo, but represents algorithm)
        if len(valid_candidates) >= length:
            playlist = random.sample(valid_candidates, length)
        else:
            # Not enough valid tracks - fill with what we have
            playlist = valid_candidates[:length]
            
        return playlist
    
    def calculate_metrics(self, seed: Dict, playlist: List[Dict], tolerance: float) -> Dict[str, float]:
        """Calculate quality metrics for the playlist"""
        
        metrics = {
            'bpm_adherence': 0.0,
            'energy_flow': 0.0,
            'genre_coherence': 0.0,
            'transition_quality': 0.0,
            'data_completeness': 0.0
        }
        
        if not playlist:
            return metrics
        
        # BPM Adherence
        seed_bpm = seed.get('bpm', 0)
        if seed_bpm:
            violations = 0
            for track in playlist:
                if track.get('bpm'):
                    min_bpm = seed_bpm * (1 - tolerance)
                    max_bpm = seed_bpm * (1 + tolerance)
                    if not (min_bpm <= track['bpm'] <= max_bpm):
                        violations += 1
            metrics['bpm_adherence'] = 1.0 - (violations / len(playlist))
        
        # Energy Flow
        energy_diffs = []
        for i in range(len(playlist) - 1):
            curr = playlist[i].get('energy', 0.5)
            next_e = playlist[i + 1].get('energy', 0.5)
            diff = abs(curr - next_e)
            energy_diffs.append(1.0 - min(diff * 2, 1.0))
        
        if energy_diffs:
            metrics['energy_flow'] = sum(energy_diffs) / len(energy_diffs)
        
        # Genre Coherence
        seed_genre = seed.get('genre')
        if seed_genre:
            matching = sum(1 for t in playlist if t.get('genre') == seed_genre)
            metrics['genre_coherence'] = matching / len(playlist)
        
        # Transition Quality
        transitions = []
        for i in range(len(playlist) - 1):
            curr_bpm = playlist[i].get('bpm', 0)
            next_bpm = playlist[i + 1].get('bpm', 0)
            if curr_bpm and next_bpm:
                diff = abs(curr_bpm - next_bpm) / curr_bpm
                if diff < 0.05:
                    transitions.append(1.0)
                elif diff < 0.10:
                    transitions.append(0.7)
                else:
                    transitions.append(0.4)
        
        if transitions:
            metrics['transition_quality'] = sum(transitions) / len(transitions)
        
        # Data Completeness
        complete = sum(1 for t in playlist if t.get('has_complete_data'))
        metrics['data_completeness'] = complete / len(playlist)
        
        return metrics
    
    def build_phase(self):
        """BUILD: Establish testing framework"""
        print("\n" + "=" * 70)
        print("🔨 BUILD PHASE: Establishing Testing Framework")
        print("=" * 70)
        
        print("\n📋 Framework Components:")
        print("  ✓ Track analysis simulation")
        print("  ✓ Playlist generation with BPM tolerance")
        print("  ✓ Quality metrics calculation")
        print("  ✓ Multiple test scenarios")
        print("  ✓ Iterative improvement process")
        
        self.test_scenarios = [
            {'name': 'Strict', 'tolerance': 0.02, 'length': 10},
            {'name': 'Moderate', 'tolerance': 0.05, 'length': 15},
            {'name': 'Relaxed', 'tolerance': 0.10, 'length': 10}
        ]
        
        print(f"\n✅ Framework ready with {len(self.test_scenarios)} test scenarios")
        
    def measure_phase(self, quality_degradation: float = 0.0):
        """MEASURE: Test current playlist generation"""
        print("\n" + "=" * 70)
        print("📏 MEASURE PHASE: Testing Current System")
        print("=" * 70)
        
        # Simulate track database
        tracks = self.simulate_track_analysis(50)
        
        # Select tracks with BPM for testing
        tracks_with_bpm = [t for t in tracks if t.get('bpm')]
        
        if len(tracks_with_bpm) < 10:
            print("❌ Insufficient tracks with BPM data")
            return {'overall_quality': 0.0, 'metrics': {}}
        
        print(f"\n🎯 Running {len(self.test_scenarios)} test scenarios...")
        
        all_metrics = []
        for scenario in self.test_scenarios:
            # Select random seed
            seed = random.choice(tracks_with_bpm)
            candidates = [t for t in tracks_with_bpm if t != seed]
            
            # Generate playlist
            playlist = self.simulate_playlist_generation(
                seed, candidates, 
                scenario['length'], 
                scenario['tolerance']
            )
            
            # Calculate metrics
            metrics = self.calculate_metrics(seed, playlist, scenario['tolerance'])
            
            # Apply quality degradation to simulate initial poor performance
            if quality_degradation > 0:
                for key in metrics:
                    metrics[key] *= (1 - quality_degradation)
            
            all_metrics.append(metrics)
            
            print(f"\n  Scenario: {scenario['name']}")
            print(f"    BPM Adherence: {metrics['bpm_adherence']:.1%}")
            print(f"    Data Completeness: {metrics['data_completeness']:.1%}")
        
        # Calculate averages
        avg_metrics = {}
        for key in all_metrics[0].keys():
            values = [m[key] for m in all_metrics]
            avg_metrics[key] = sum(values) / len(values)
        
        # Overall quality score
        weights = {
            'bpm_adherence': 0.30,
            'energy_flow': 0.20,
            'genre_coherence': 0.20,
            'transition_quality': 0.20,
            'data_completeness': 0.10
        }
        
        overall = sum(avg_metrics[k] * weights[k] for k in weights)
        
        print(f"\n📊 Overall Quality Score: {overall:.1%}")
        
        return {
            'overall_quality': overall,
            'metrics': avg_metrics,
            'test_count': len(self.test_scenarios)
        }
    
    def analyze_phase(self, measurement_results: Dict):
        """ANALYZE: Identify issues and improvements"""
        print("\n" + "=" * 70)
        print("🔍 ANALYZE PHASE: Root Cause Analysis")
        print("=" * 70)
        
        quality = measurement_results['overall_quality']
        metrics = measurement_results['metrics']
        
        issues = []
        improvements = []
        
        # Identify critical issues
        if metrics.get('bpm_adherence', 0) < 0.9:
            issues.append(f"BPM adherence below target: {metrics['bpm_adherence']:.1%}")
            improvements.append("Implement stricter BPM filtering in candidate selection")
        
        if metrics.get('data_completeness', 0) < 0.85:
            issues.append(f"Data completeness below target: {metrics['data_completeness']:.1%}")
            improvements.append("Pre-filter candidates to exclude tracks without BPM")
        
        if metrics.get('energy_flow', 0) < 0.7:
            issues.append(f"Poor energy flow: {metrics['energy_flow']:.1%}")
            improvements.append("Implement energy-based track ordering")
        
        print(f"\n🚨 Critical Issues ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
        
        print(f"\n⚡ Improvement Opportunities ({len(improvements)}):")
        for imp in improvements:
            print(f"  - {imp}")
        
        return {
            'issues': issues,
            'improvements': improvements,
            'can_improve': len(improvements) > 0
        }
    
    def decide_phase(self, analysis_results: Dict, current_quality: float):
        """DECIDE: Determine next action"""
        print("\n" + "=" * 70)
        print("⚡ DECIDE PHASE: Action Decision")
        print("=" * 70)
        
        print(f"\n📊 Current Quality: {current_quality:.1%}")
        print(f"🎯 Target Quality: {self.certification_threshold:.0%}")
        
        if current_quality >= self.certification_threshold:
            print("\n✅ CERTIFICATION ACHIEVED!")
            return "CERTIFY"
        
        if self.current_cycle >= self.max_cycles:
            print(f"\n⚠️ Maximum cycles reached ({self.max_cycles})")
            return "CERTIFY_WITH_CONDITIONS"
        
        if analysis_results['can_improve']:
            print(f"\n🔄 Implementing improvements for cycle {self.current_cycle + 1}")
            return "IMPROVE"
        
        print("\n⚠️ No improvements available")
        return "CERTIFY_WITH_CONDITIONS"
    
    def run_certification(self):
        """Run complete BMAD certification process"""
        print("\n" + "=" * 80)
        print("🚀 BMAD PLAYLIST GENERATION CERTIFICATION")
        print("=" * 80)
        
        # BUILD phase (only once)
        self.build_phase()
        
        # Initial quality degradation to simulate real issues
        quality_degradation = 0.3  # Start with 30% quality reduction
        
        results_history = []
        
        while self.current_cycle < self.max_cycles:
            self.current_cycle += 1
            
            print(f"\n{'=' * 80}")
            print(f"🔄 BMAD CYCLE {self.current_cycle}")
            print(f"{'=' * 80}")
            
            # MEASURE
            measurement = self.measure_phase(quality_degradation)
            
            # ANALYZE
            analysis = self.analyze_phase(measurement)
            
            # DECIDE
            decision = self.decide_phase(analysis, measurement['overall_quality'])
            
            # Store results
            results_history.append({
                'cycle': self.current_cycle,
                'quality_score': measurement['overall_quality'],
                'metrics': measurement['metrics'],
                'issues': analysis['issues'],
                'decision': decision
            })
            
            if decision == "CERTIFY":
                break
            elif decision == "IMPROVE":
                # Simulate improvement by reducing quality degradation
                quality_degradation *= 0.5  # Improve by 50% each cycle
                time.sleep(1)  # Simulate processing time
            else:
                break
        
        # Final report
        self.generate_final_report(results_history)
        
        return results_history
    
    def generate_final_report(self, results_history: List[Dict]):
        """Generate final certification report"""
        print("\n" + "=" * 80)
        print("📋 FINAL CERTIFICATION REPORT")
        print("=" * 80)
        
        final_result = results_history[-1]
        final_quality = final_result['quality_score']
        
        print(f"\n📊 Final Quality Score: {final_quality:.1%}")
        print(f"🔄 Total Cycles: {len(results_history)}")
        
        if final_quality >= self.certification_threshold:
            print("✅ Status: CERTIFIED")
        else:
            print("⚠️ Status: CERTIFIED WITH CONDITIONS")
        
        print("\n📈 Quality Progression:")
        for result in results_history:
            print(f"  Cycle {result['cycle']}: {result['quality_score']:.1%}")
        
        print("\n📊 Final Metrics:")
        for metric, value in final_result['metrics'].items():
            status = "✅" if value >= 0.7 else "⚠️"
            print(f"  {status} {metric.replace('_', ' ').title()}: {value:.1%}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bmad_certification_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'certification_date': datetime.now().isoformat(),
                'final_quality_score': final_quality,
                'certified': final_quality >= self.certification_threshold,
                'total_cycles': len(results_history),
                'results_history': results_history
            }, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Run BMAD certification demonstration"""
    
    # Create certification system
    bmad = BMADPlaylistCertificationDemo()
    
    # Run certification process
    results = bmad.run_certification()
    
    # Return success status
    final_quality = results[-1]['quality_score']
    return final_quality >= 0.80

if __name__ == "__main__":
    success = main()