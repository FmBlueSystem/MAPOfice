#!/usr/bin/env python3
"""Validate Real Audio Analysis - Test that we're actually analyzing audio files
Extracts BPM, key, energy, and HAMMS vectors from real audio data
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.lib import audio_processing
    from src.services.analyzer import Analyzer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Make sure audio processing libraries are installed")
    sys.exit(1)

@dataclass
class RealAudioFeatures:
    """Real audio features extracted from audio data"""
    filepath: str
    filename: str
    
    # Metadata
    title: str
    artist: str
    
    # Real audio analysis features
    bpm: float
    key: str 
    energy: float
    hamms_vector: List[float]
    
    # Technical info
    duration: float
    sample_rate: int
    
    # Validation flags
    analysis_success: bool
    error_message: str = ""

class RealAudioValidator:
    """Validates that we're doing real audio analysis, not just metadata"""
    
    def __init__(self):
        # We'll use the audio_processing module directly
        pass
    
    def validate_real_audio_analysis(self, music_directory: str) -> List[RealAudioFeatures]:
        """Validate real audio analysis on actual files"""
        
        print("🎵 VALIDATING REAL AUDIO ANALYSIS")
        print("="*80)
        print("🔍 Testing BPM, Key, Energy extraction from audio data")
        print("🔍 Testing HAMMS vector calculation from audio features")
        print("⚠️  This will FAIL if we're only using metadata!")
        print("="*80)
        
        music_path = Path(music_directory)
        if not music_path.exists():
            raise FileNotFoundError(f"Music directory not found: {music_directory}")
        
        audio_files = (
            list(music_path.glob("*.flac")) +
            list(music_path.glob("*.mp3")) +
            list(music_path.glob("*.wav"))
        )
        
        print(f"📁 Found {len(audio_files)} audio files")
        
        analysis_results = []
        
        for audio_file in audio_files:
            print(f"\n🔍 REAL AUDIO ANALYSIS: {audio_file.name}")
            print("-" * 60)
            
            try:
                # Use our audio processor to get REAL audio features
                print("   🎧 Extracting audio features...")
                audio_features = audio_processing.analyze_track(str(audio_file))
                
                # Check if we got real audio analysis results
                if audio_features and 'bpm' in audio_features and audio_features['bpm'] != 0:
                    # Validate that we got REAL audio analysis, not just metadata
                    real_features = RealAudioFeatures(
                        filepath=str(audio_file),
                        filename=audio_file.name,
                        title=audio_features.get('title', 'Unknown'),
                        artist=audio_features.get('artist', 'Unknown'),
                        bpm=audio_features.get('bpm', 0.0),
                        key=audio_features.get('key', 'Unknown'),
                        energy=audio_features.get('energy', 0.0),
                        hamms_vector=audio_features.get('hamms', []),
                        duration=0.0,  # Not provided by current analysis
                        sample_rate=0,  # Not provided by current analysis
                        analysis_success=True
                    )
                    
                    # Display extracted features
                    print(f"   📊 BPM: {real_features.bpm:.1f}")
                    print(f"   🎹 Key: {real_features.key}")
                    print(f"   ⚡ Energy: {real_features.energy:.3f}")
                    print(f"   📈 HAMMS dims: {len(real_features.hamms_vector)}")
                    print(f"   ⏱️  Duration: {real_features.duration:.1f}s")
                    print(f"   📻 Sample rate: {real_features.sample_rate} Hz")
                    
                    # Validate that these are REAL extracted features
                    self._validate_real_features(real_features)
                    
                else:
                    error_msg = "No BPM extracted or invalid audio analysis"
                    print(f"   ❌ Audio analysis failed: {error_msg}")
                    real_features = RealAudioFeatures(
                        filepath=str(audio_file),
                        filename=audio_file.name,
                        title="Unknown",
                        artist="Unknown", 
                        bpm=0.0,
                        key="Unknown",
                        energy=0.0,
                        hamms_vector=[],
                        duration=0.0,
                        sample_rate=0,
                        analysis_success=False,
                        error_message=error_msg
                    )
                
                analysis_results.append(real_features)
                
            except Exception as e:
                print(f"   ❌ Exception during analysis: {e}")
                error_features = RealAudioFeatures(
                    filepath=str(audio_file),
                    filename=audio_file.name,
                    title="Unknown",
                    artist="Unknown",
                    bpm=0.0,
                    key="Unknown", 
                    energy=0.0,
                    hamms_vector=[],
                    duration=0.0,
                    sample_rate=0,
                    analysis_success=False,
                    error_message=str(e)
                )
                analysis_results.append(error_features)
        
        # Summary validation
        self._generate_validation_summary(analysis_results)
        
        return analysis_results
    
    def _validate_real_features(self, features: RealAudioFeatures):
        """Validate that we got real audio features, not defaults"""
        
        validation_issues = []
        
        # Check BPM - should not be default values
        if features.bpm == 0.0 or features.bpm == 120.0:
            validation_issues.append("BPM might be default/placeholder")
        elif features.bpm < 60 or features.bpm > 200:
            validation_issues.append(f"BPM unusual: {features.bpm}")
        else:
            print(f"   ✅ BPM looks real: {features.bpm:.1f}")
        
        # Check energy - should be calculated from audio
        if features.energy == 0.0 or features.energy == 0.5:
            validation_issues.append("Energy might be default/placeholder")
        else:
            print(f"   ✅ Energy looks real: {features.energy:.3f}")
        
        # Check HAMMS vector
        if not features.hamms_vector:
            validation_issues.append("No HAMMS vector calculated")
        elif len(features.hamms_vector) != 12:
            validation_issues.append(f"HAMMS vector wrong size: {len(features.hamms_vector)}")
        elif all(v == 0.5 for v in features.hamms_vector):
            validation_issues.append("HAMMS vector looks like placeholder")
        else:
            print(f"   ✅ HAMMS vector looks real: [{features.hamms_vector[0]:.3f}, {features.hamms_vector[1]:.3f}, ...]")
        
        # Check key detection
        if features.key == "Unknown" or features.key == "":
            validation_issues.append("Key not detected")
        else:
            print(f"   ✅ Key detected: {features.key}")
        
        # Report validation issues
        if validation_issues:
            print(f"   ⚠️  Validation concerns:")
            for issue in validation_issues:
                print(f"      - {issue}")
        else:
            print(f"   🎯 All features look REAL (not placeholders)")
    
    def _generate_validation_summary(self, results: List[RealAudioFeatures]):
        """Generate summary of real audio analysis validation"""
        
        print(f"\n{'='*80}")
        print("📊 REAL AUDIO ANALYSIS VALIDATION SUMMARY")
        print("="*80)
        
        total_files = len(results)
        successful_analyses = sum(1 for r in results if r.analysis_success)
        failed_analyses = total_files - successful_analyses
        
        print(f"📁 Total files: {total_files}")
        print(f"✅ Successful analyses: {successful_analyses}")
        print(f"❌ Failed analyses: {failed_analyses}")
        
        if successful_analyses > 0:
            # Analyze feature quality
            real_bpm_count = sum(1 for r in results if r.analysis_success and r.bpm > 0 and r.bpm != 120.0)
            real_energy_count = sum(1 for r in results if r.analysis_success and r.energy > 0 and r.energy != 0.5)
            real_hamms_count = sum(1 for r in results if r.analysis_success and len(r.hamms_vector) == 12 and not all(v == 0.5 for v in r.hamms_vector))
            key_detected_count = sum(1 for r in results if r.analysis_success and r.key != "Unknown")
            
            print(f"\n🎯 FEATURE QUALITY:")
            print(f"   📊 Real BPM extracted: {real_bpm_count}/{successful_analyses}")
            print(f"   ⚡ Real Energy extracted: {real_energy_count}/{successful_analyses}")
            print(f"   📈 Real HAMMS vectors: {real_hamms_count}/{successful_analyses}")
            print(f"   🎹 Keys detected: {key_detected_count}/{successful_analyses}")
            
            # Overall assessment
            quality_score = (real_bpm_count + real_energy_count + real_hamms_count + key_detected_count) / (4 * successful_analyses)
            
            print(f"\n🏆 OVERALL AUDIO ANALYSIS QUALITY: {quality_score*100:.1f}%")
            
            if quality_score > 0.8:
                print("✅ EXCELLENT: Real audio analysis is working properly!")
            elif quality_score > 0.6:
                print("✅ GOOD: Mostly real audio analysis")
            elif quality_score > 0.4:
                print("⚠️  FAIR: Some real analysis, some placeholders")
            else:
                print("❌ POOR: Mostly placeholder values - check audio processing")
        
        if failed_analyses > 0:
            print(f"\n❌ FAILED ANALYSES:")
            for result in results:
                if not result.analysis_success:
                    print(f"   - {result.filename}: {result.error_message}")
    
    def test_integration_with_claude(self, results: List[RealAudioFeatures]):
        """Test that real audio features work with Claude analysis"""
        
        print(f"\n🧠 TESTING INTEGRATION WITH CLAUDE")
        print("="*60)
        
        from dotenv import load_dotenv
        from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory
        
        load_dotenv()
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("❌ No ANTHROPIC_API_KEY - skipping Claude integration test")
            return
        
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            api_key=api_key,
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.1
        )
        
        provider = LLMProviderFactory.create_provider(config)
        
        # Test with first successful analysis
        test_track = next((r for r in results if r.analysis_success), None)
        if not test_track:
            print("❌ No successful audio analysis to test with Claude")
            return
        
        print(f"🎵 Testing Claude with REAL audio features from: {test_track.filename}")
        
        # Use REAL extracted features
        track_data = {
            'title': test_track.title,
            'artist': test_track.artist,
            'bpm': test_track.bpm,  # REAL BPM from audio
            'energy': test_track.energy,  # REAL energy from audio
            'key': test_track.key,  # REAL key from audio
            'date': '1985',  # We don't have year from audio analysis
            'hamms_vector': test_track.hamms_vector  # REAL HAMMS from audio
        }
        
        print(f"   📊 Using REAL features: BPM={track_data['bpm']:.1f}, Energy={track_data['energy']:.3f}")
        
        result = provider.analyze_track(track_data)
        
        if result.success:
            print("✅ Claude analysis successful with REAL audio features!")
            print(f"   🎭 Genre: {result.content.get('genre', 'Unknown')}")
            print(f"   📅 Era: {result.content.get('era', 'Unknown')}")  
            print(f"   📊 Confidence: {result.content.get('confidence', 0)}")
            print("🎯 END-TO-END PIPELINE WORKING: Real audio → Claude analysis")
        else:
            print(f"❌ Claude analysis failed: {result.error_message}")


def main():
    """Main validation function"""
    music_directory = '/Volumes/My Passport/Abibleoteca/Consolidado2025/Playlists/Dance - 80s - 2025-08-17'
    
    if not os.path.exists(music_directory):
        print(f"❌ Music directory not found: {music_directory}")
        return
    
    validator = RealAudioValidator()
    
    # Validate real audio analysis
    results = validator.validate_real_audio_analysis(music_directory)
    
    # Test integration with Claude
    validator.test_integration_with_claude(results)
    
    print(f"\n🎯 VALIDATION COMPLETE")
    print("="*60)
    print("If features look real (not placeholders), the pipeline is working correctly!")


if __name__ == "__main__":
    main()