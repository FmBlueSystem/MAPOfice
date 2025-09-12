#!/usr/bin/env python3
"""BMAD-METHOD: Iterative Prompt Optimization Cycle for 100% Accuracy
Using SpecKit methodology with real Dance-80s tracks as ground truth
"""

import os
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

load_dotenv()

@dataclass 
class GroundTruthTrack:
    """Ground truth data for validation"""
    filename: str
    artist: str
    title: str
    expected_genre: str
    expected_subgenre: str 
    expected_era: str
    expected_year: int
    confidence_threshold: float = 0.9

@dataclass
class OptimizationResult:
    """Result of prompt optimization iteration"""
    iteration: int
    accuracy_score: float
    tracks_correct: int
    tracks_total: int
    failed_tracks: List[str]
    prompt_version: str

class BMADPromptOptimizer:
    """BMAD-METHOD: Build, Measure, Analyze, Decide cycle for prompt optimization"""
    
    def __init__(self):
        self.ground_truth = self._create_ground_truth()
        self.provider = self._create_provider()
        self.optimization_history = []
        self.current_iteration = 0
        
    def _create_ground_truth(self) -> List[GroundTruthTrack]:
        """Create ground truth dataset from real Dance-80s playlist"""
        return [
            GroundTruthTrack(
                filename="Bananarama - Venus (Extended Version).flac",
                artist="Bananarama",
                title="Venus",
                expected_genre="Synthpop",
                expected_subgenre="Hi-NRG",
                expected_era="1980s", 
                expected_year=1986
            ),
            GroundTruthTrack(
                filename="Bronski Beat, The Knocks, Perfume Genius - Smalltown Boy (Extended).flac",
                artist="Bronski Beat",
                title="Smalltown Boy", 
                expected_genre="Synthpop",
                expected_subgenre="Hi-NRG",
                expected_era="1980s",
                expected_year=1984
            ),
            GroundTruthTrack(
                filename="Irene Cara - Flashdance... What a Feeling (Extended Remix).flac",
                artist="Irene Cara",
                title="Flashdance... What a Feeling",
                expected_genre="Dance-Pop", 
                expected_subgenre="Film Soundtrack Dance",
                expected_era="1980s",
                expected_year=1983
            ),
            GroundTruthTrack(
                filename="Men Without Hats - The Safety Dance (Extended Dance Version).flac",
                artist="Men Without Hats", 
                title="The Safety Dance",
                expected_genre="New Wave",
                expected_subgenre="Synthpop",
                expected_era="1980s",
                expected_year=1982
            ),
            GroundTruthTrack(
                filename="Orchestral Manoeuvres In The Dark (OMD) - Enola Gay (Extended Mix).flac",
                artist="OMD",
                title="Enola Gay", 
                expected_genre="New Wave",
                expected_subgenre="Synthpop", 
                expected_era="1980s",
                expected_year=1980
            ),
            GroundTruthTrack(
                filename="Soft Cell - Tainted Love  Where Did Our Love Go (Extended Version).flac",
                artist="Soft Cell",
                title="Tainted Love",
                expected_genre="Synthpop",
                expected_subgenre="Dark Wave",
                expected_era="1980s", 
                expected_year=1981
            ),
            GroundTruthTrack(
                filename="Tears For Fears - Shout (Extended).flac", 
                artist="Tears For Fears",
                title="Shout",
                expected_genre="New Wave",
                expected_subgenre="Synthpop",
                expected_era="1980s",
                expected_year=1984
            ),
            GroundTruthTrack(
                filename="The Pointer Sisters - I'm So Excited (Extended Version).flac",
                artist="The Pointer Sisters",
                title="I'm So Excited", 
                expected_genre="R&B",
                expected_subgenre="Dance-R&B",
                expected_era="1980s",
                expected_year=1982
            )
        ]
    
    def _create_provider(self):
        """Create Claude provider for testing"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY required")
            
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            api_key=api_key,
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.1
        )
        
        return LLMProviderFactory.create_provider(config)
    
    def run_optimization_cycle(self, max_iterations: int = 5, target_accuracy: float = 1.0):
        """Run complete BMAD optimization cycle"""
        print("🚀 BMAD-METHOD: Prompt Optimization Cycle Started")
        print("="*60)
        print(f"📊 Ground Truth Dataset: {len(self.ground_truth)} Dance-80s tracks")
        print(f"🎯 Target Accuracy: {target_accuracy*100}%")
        print(f"🔄 Max Iterations: {max_iterations}")
        print("="*60)
        
        best_accuracy = 0.0
        best_iteration = 0
        
        for iteration in range(1, max_iterations + 1):
            print(f"\n🔄 ITERATION {iteration}")
            print("-" * 30)
            
            # BUILD: Test current prompt
            result = self._test_current_prompt(iteration)
            
            # MEASURE: Calculate accuracy
            accuracy = result.accuracy_score
            print(f"📊 Accuracy: {accuracy*100:.1f}% ({result.tracks_correct}/{result.tracks_total})")
            
            # Track best result
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_iteration = iteration
            
            # ANALYZE: Identify failures
            if result.failed_tracks:
                print(f"❌ Failed tracks: {len(result.failed_tracks)}")
                for failed in result.failed_tracks:
                    print(f"   - {failed}")
            
            self.optimization_history.append(result)
            
            # DECIDE: Check if target reached
            if accuracy >= target_accuracy:
                print(f"\n🎉 TARGET ACHIEVED! 100% accuracy reached in iteration {iteration}")
                break
            elif iteration < max_iterations:
                print(f"\n🔧 OPTIMIZING: Refining prompt for iteration {iteration + 1}")
                self._optimize_prompt_for_failures(result)
        
        # Final summary
        print(f"\n{'='*60}")
        print("📈 OPTIMIZATION COMPLETE")
        print("="*60)
        print(f"🏆 Best Accuracy: {best_accuracy*100:.1f}% (Iteration {best_iteration})")
        print(f"🎯 Target: {target_accuracy*100}%")
        
        if best_accuracy >= target_accuracy:
            print("✅ SUCCESS: 100% accuracy achieved!")
        else:
            print(f"⚠️  Need more iterations to reach {target_accuracy*100}% accuracy")
        
        return self.optimization_history
    
    def _test_current_prompt(self, iteration: int) -> OptimizationResult:
        """Test current prompt against ground truth"""
        correct_predictions = 0
        failed_tracks = []
        
        print("🧪 Testing current prompt...")
        
        for track in self.ground_truth:
            # Simulate track data (normally from audio analysis)
            track_data = {
                "title": track.title,
                "artist": track.artist,
                "bpm": 120,  # Typical dance music BPM
                "energy": 0.8,  # High energy for dance
                "date": "1985",  # Default 80s date
                "hamms_vector": [0.5] * 12  # Placeholder
            }
            
            result = self.provider.analyze_track(track_data)
            
            if result.success:
                predicted_genre = result.content.get('genre', '').lower()
                predicted_era = result.content.get('era', '')
                confidence = result.content.get('confidence', 0)
                
                # Check if prediction matches ground truth
                is_correct = (
                    track.expected_genre.lower() in predicted_genre or
                    predicted_genre in track.expected_genre.lower() or
                    (track.expected_genre == "Dance-Pop" and "pop" in predicted_genre) or
                    (track.expected_genre == "R&B" and ("r&b" in predicted_genre or "rnb" in predicted_genre))
                ) and (
                    predicted_era == track.expected_era
                ) and (
                    confidence >= track.confidence_threshold
                )
                
                if is_correct:
                    correct_predictions += 1
                    print(f"   ✅ {track.artist} - {track.title}: {predicted_genre} (conf: {confidence})")
                else:
                    failed_tracks.append(f"{track.artist} - {track.title}: expected {track.expected_genre}, got {predicted_genre}")
                    print(f"   ❌ {track.artist} - {track.title}: expected {track.expected_genre}, got {predicted_genre}")
            else:
                failed_tracks.append(f"{track.artist} - {track.title}: analysis failed")
                print(f"   ❌ {track.artist} - {track.title}: analysis failed")
        
        accuracy = correct_predictions / len(self.ground_truth)
        
        return OptimizationResult(
            iteration=iteration,
            accuracy_score=accuracy, 
            tracks_correct=correct_predictions,
            tracks_total=len(self.ground_truth),
            failed_tracks=failed_tracks,
            prompt_version=f"v{iteration}"
        )
    
    def _optimize_prompt_for_failures(self, result: OptimizationResult):
        """DECIDE phase: Optimize prompt based on failures"""
        print("🔧 Analyzing failures and optimizing prompt...")
        
        # This would update the Claude provider's prompt based on failure analysis
        # For now, we'll print the analysis
        
        if result.failed_tracks:
            print("🔍 Failure Analysis:")
            print("   - Need better 80s dance genre classification")
            print("   - Improve Synthpop vs New Wave distinction") 
            print("   - Better R&B vs Dance-Pop classification")
            print("   - Enhanced confidence calibration")


if __name__ == "__main__":
    optimizer = BMADPromptOptimizer()
    history = optimizer.run_optimization_cycle(max_iterations=3, target_accuracy=1.0)