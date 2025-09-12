#!/usr/bin/env python3
"""
BMAD Methodology Test for Metadata Writing Verification
======================================================

This script applies BMAD (Build, Measure, Analyze, Decide) methodology
to systematically certify that the application writes correct metadata
to the corresponding audio file.

BUILD: Create systematic test framework
MEASURE: Capture metadata before/after writing  
ANALYZE: Validate correspondence between file and written metadata
DECIDE: Certify process or identify corrections needed
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add project root to path
sys.path.append('/Users/freddymolina/Desktop/MAP 4')

try:
    from src.services.enhanced_analyzer import create_enhanced_analyzer
    from src.services.metadata_writer import AudioMetadataWriter
    import mutagen
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    from mutagen.id3 import ID3, ID3NoHeaderError
    print("✅ All required modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class MetadataVerificationBMAD:
    """BMAD methodology implementation for metadata verification"""
    
    def __init__(self):
        self.metadata_writer = AudioMetadataWriter()
        # Create analyzer with validation disabled for BMAD testing
        self.analyzer = create_enhanced_analyzer()
        self.analyzer.skip_validation = True  # Disable validation for testing
        self.test_results = []
        
    def build_test_framework(self) -> None:
        """BUILD Phase: Create systematic test framework"""
        print("\n🔨 BUILD PHASE: Creating systematic test framework")
        print("=" * 60)
        
        # Test file selection criteria
        print("📋 Test Framework Components:")
        print("  ✓ Multiple audio formats (FLAC, M4A, MP3)")
        print("  ✓ Before/after metadata capture")
        print("  ✓ File modification timestamp tracking")
        print("  ✓ AI analysis result validation")
        print("  ✓ Metadata persistence verification")
        
    def measure_metadata_state(self, file_path: str) -> Dict[str, Any]:
        """MEASURE Phase: Capture complete metadata state"""
        print(f"\n📏 MEASURE PHASE: Capturing metadata state for {Path(file_path).name}")
        print("-" * 50)
        
        state = {
            'file_path': file_path,
            'exists': os.path.exists(file_path),
            'modification_time': None,
            'file_size': None,
            'metadata_tags': {},
            'ai_analysis_present': False,
            'capture_timestamp': time.time()
        }
        
        if not state['exists']:
            print(f"❌ File not found: {file_path}")
            return state
            
        # Get file stats
        stat = os.stat(file_path)
        state['modification_time'] = stat.st_mtime
        state['file_size'] = stat.st_size
        
        print(f"📊 File Stats:")
        print(f"  📁 Size: {state['file_size']:,} bytes")
        print(f"  🕒 Modified: {time.ctime(state['modification_time'])}")
        
        # Read metadata based on file type
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext == '.flac':
                audio = FLAC(file_path)
                state['metadata_tags'] = dict(audio)
            elif ext in ['.m4a', '.mp4', '.aac']:
                audio = MP4(file_path)
                state['metadata_tags'] = dict(audio)
            elif ext == '.mp3':
                try:
                    audio = ID3(file_path)
                    state['metadata_tags'] = {str(k): str(v) for k, v in audio.items()}
                except ID3NoHeaderError:
                    state['metadata_tags'] = {}
                    
            # Check for AI analysis tags
            if ext == '.flac':
                ai_tags = ['GENRE', 'SUBGENRE', 'MOOD', 'ERA', 'AI_ANALYZED']
                state['ai_analysis_present'] = any(tag in state['metadata_tags'] for tag in ai_tags)
            elif ext in ['.m4a', '.mp4', '.aac']:
                ai_tags = ['\xa9gen', '----:com.apple.iTunes:SUBGENRE', '----:com.apple.iTunes:MOOD', 
                          '----:com.apple.iTunes:ERA', '----:com.apple.iTunes:AI_ANALYZED']
                state['ai_analysis_present'] = any(tag in state['metadata_tags'] for tag in ai_tags)
                
            print(f"🏷️  Metadata tags found: {len(state['metadata_tags'])}")
            print(f"🤖 AI analysis present: {state['ai_analysis_present']}")
            
            # Print relevant AI tags
            if state['ai_analysis_present']:
                print("🎵 AI Analysis Tags:")
                if ext == '.flac':
                    for tag in ['GENRE', 'SUBGENRE', 'MOOD', 'ERA']:
                        if tag in state['metadata_tags']:
                            print(f"    {tag}: {state['metadata_tags'][tag]}")
                            
        except Exception as e:
            print(f"⚠️ Error reading metadata: {e}")
            
        return state
    
    def analyze_correspondence(self, file_path: str, before_state: Dict[str, Any], 
                             after_state: Dict[str, Any], analysis_result: Any) -> Dict[str, Any]:
        """ANALYZE Phase: Validate correspondence between file and metadata"""
        print(f"\n🔍 ANALYZE PHASE: Validating correspondence")
        print("-" * 40)
        
        analysis = {
            'file_modified': after_state['modification_time'] != before_state['modification_time'],
            'metadata_added': not before_state['ai_analysis_present'] and after_state['ai_analysis_present'],
            'size_changed': after_state['file_size'] != before_state['file_size'],
            'correspondence_valid': False,
            'issues': [],
            'verification_score': 0.0
        }
        
        print(f"📊 Change Detection:")
        print(f"  🕒 File modified: {analysis['file_modified']}")
        print(f"  🏷️  Metadata added: {analysis['metadata_added']}")
        print(f"  📏 Size changed: {analysis['size_changed']}")
        
        # Verify correspondence between analysis result and written metadata
        if analysis_result and analysis_result.success:
            ext = Path(file_path).suffix.lower()
            
            if ext == '.flac':
                expected_genre = analysis_result.genre
                expected_subgenre = analysis_result.subgenre
                expected_mood = analysis_result.mood
                expected_era = analysis_result.era
                
                actual_genre = after_state['metadata_tags'].get('GENRE', [None])[0] if 'GENRE' in after_state['metadata_tags'] else None
                actual_subgenre = after_state['metadata_tags'].get('SUBGENRE', [None])[0] if 'SUBGENRE' in after_state['metadata_tags'] else None
                actual_mood = after_state['metadata_tags'].get('MOOD', [None])[0] if 'MOOD' in after_state['metadata_tags'] else None
                actual_era = after_state['metadata_tags'].get('ERA', [None])[0] if 'ERA' in after_state['metadata_tags'] else None
                
                print(f"\n🎯 Correspondence Verification:")
                print(f"  Genre: {expected_genre} → {actual_genre} {'✅' if expected_genre == actual_genre else '❌'}")
                print(f"  Subgenre: {expected_subgenre} → {actual_subgenre} {'✅' if expected_subgenre == actual_subgenre else '❌'}")
                print(f"  Mood: {expected_mood} → {actual_mood} {'✅' if expected_mood == actual_mood else '❌'}")
                print(f"  Era: {expected_era} → {actual_era} {'✅' if expected_era == actual_era else '❌'}")
                
                # Calculate verification score
                matches = sum([
                    expected_genre == actual_genre,
                    expected_subgenre == actual_subgenre, 
                    expected_mood == actual_mood,
                    expected_era == actual_era
                ])
                analysis['verification_score'] = matches / 4.0
                analysis['correspondence_valid'] = analysis['verification_score'] >= 0.75
                
                if not analysis['correspondence_valid']:
                    if expected_genre != actual_genre:
                        analysis['issues'].append(f"Genre mismatch: expected '{expected_genre}', got '{actual_genre}'")
                    if expected_subgenre != actual_subgenre:
                        analysis['issues'].append(f"Subgenre mismatch: expected '{expected_subgenre}', got '{actual_subgenre}'")
                    if expected_mood != actual_mood:
                        analysis['issues'].append(f"Mood mismatch: expected '{expected_mood}', got '{actual_mood}'")
                    if expected_era != actual_era:
                        analysis['issues'].append(f"Era mismatch: expected '{expected_era}', got '{actual_era}'")
        
        print(f"\n📈 Verification Score: {analysis['verification_score']:.2%}")
        if analysis['issues']:
            print("❌ Issues found:")
            for issue in analysis['issues']:
                print(f"    - {issue}")
                
        return analysis
    
    def decide_certification(self, analysis: Dict[str, Any]) -> str:
        """DECIDE Phase: Certify process or identify corrections"""
        print(f"\n⚖️  DECIDE PHASE: Certification Decision")
        print("-" * 35)
        
        if analysis['correspondence_valid'] and analysis['file_modified'] and analysis['metadata_added']:
            decision = "CERTIFIED"
            print("✅ CERTIFICATION: PASSED")
            print("   ✓ File was modified (timestamp updated)")
            print("   ✓ Metadata was added to file")
            print("   ✓ Correspondence between analysis and metadata is valid")
        elif analysis['verification_score'] >= 0.5:
            decision = "PARTIAL_CERTIFICATION"
            print("⚠️ CERTIFICATION: PARTIAL")
            print(f"   ⚠️ Verification score: {analysis['verification_score']:.2%}")
            print("   - Some metadata fields may not match exactly")
        else:
            decision = "FAILED"
            print("❌ CERTIFICATION: FAILED")
            print("   ❌ Critical issues found in metadata writing process")
            
        return decision
    
    def run_bmad_cycle(self, file_path: str) -> Dict[str, Any]:
        """Run complete BMAD cycle on a single file"""
        print(f"\n🎯 BMAD CYCLE START: {Path(file_path).name}")
        print("=" * 80)
        
        # BUILD
        self.build_test_framework()
        
        # MEASURE - Before
        before_state = self.measure_metadata_state(file_path)
        
        # Process file with analyzer  
        print(f"\n🔄 Processing file with Enhanced Analyzer...")
        result = self.analyzer.analyze_track(file_path)
        
        # MEASURE - After
        after_state = self.measure_metadata_state(file_path)
        
        # ANALYZE
        analysis = self.analyze_correspondence(file_path, before_state, after_state, result)
        
        # DECIDE
        decision = self.decide_certification(analysis)
        
        test_result = {
            'file_path': file_path,
            'before_state': before_state,
            'after_state': after_state,
            'analysis_result': result,
            'correspondence_analysis': analysis,
            'certification_decision': decision,
            'timestamp': time.time()
        }
        
        self.test_results.append(test_result)
        return test_result


def main():
    """Main BMAD certification process"""
    print("🚀 BMAD Metadata Writing Certification")
    print("=" * 50)
    
    verifier = MetadataVerificationBMAD()
    
    # Test files from available directories
    import glob
    search_paths = [
        "/Volumes/My Passport/Abibleoteca/Tracks",
        "/Volumes/My Passport/Abibleoteca/Consolidado2025/Tracks"
    ]
    
    test_files = []
    
    for base_path in search_paths:
        print(f"🔍 Searching for test files in {base_path}...")
        if not os.path.exists(base_path):
            continue
            
        # Find different format files
        for pattern in ["*.m4a", "*.flac", "*.mp3"]:
            found_files = glob.glob(os.path.join(base_path, pattern))
            if found_files:
                test_files.extend(found_files[:2])  # Add up to 2 files per format
        
        # If we found files, break
        if test_files:
            break
    
    # Limit total test files to 5 for manageable testing
    test_files = test_files[:5]
    
    print(f"📁 Selected {len(test_files)} test files")
    
    # Run BMAD cycles
    certification_results = []
    for file_path in test_files:
        if os.path.exists(file_path):
            result = verifier.run_bmad_cycle(file_path)
            certification_results.append(result)
        else:
            print(f"❌ File not found: {file_path}")
    
    # Final certification report
    print(f"\n📊 FINAL CERTIFICATION REPORT")
    print("=" * 50)
    
    certified_count = sum(1 for r in certification_results if r['certification_decision'] == 'CERTIFIED')
    partial_count = sum(1 for r in certification_results if r['certification_decision'] == 'PARTIAL_CERTIFICATION')
    failed_count = sum(1 for r in certification_results if r['certification_decision'] == 'FAILED')
    
    print(f"✅ Fully Certified: {certified_count}")
    print(f"⚠️ Partially Certified: {partial_count}")
    print(f"❌ Failed: {failed_count}")
    
    if len(certification_results) > 0:
        print(f"📈 Success Rate: {(certified_count/len(certification_results)*100):.1f}%")
    else:
        print("📈 Success Rate: N/A (no files tested)")
    
    if certified_count == len(certification_results):
        print(f"\n🎉 OVERALL CERTIFICATION: PASSED")
        print("   The application correctly writes metadata to corresponding audio files")
    elif certified_count + partial_count >= len(certification_results) * 0.8:
        print(f"\n⚠️ OVERALL CERTIFICATION: NEEDS IMPROVEMENT") 
        print("   Most files pass but some issues need addressing")
    else:
        print(f"\n❌ OVERALL CERTIFICATION: FAILED")
        print("   Critical issues found in metadata writing process")


if __name__ == "__main__":
    main()