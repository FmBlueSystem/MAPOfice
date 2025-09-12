#!/usr/bin/env python3
"""Debug audio analysis - check what's actually happening"""

import os
import sys
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def debug_audio_analysis():
    """Debug the audio analysis pipeline"""
    
    print("🔍 DEBUGGING AUDIO ANALYSIS PIPELINE")
    print("="*60)
    
    # Test file
    test_file = '/Volumes/My Passport/Abibleoteca/Consolidado2025/Playlists/Dance - 80s - 2025-08-17/Bananarama - Venus (Extended Version).flac'
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📁 Testing with: {os.path.basename(test_file)}")
    
    # Try importing the audio processing module
    print("\n1️⃣ Testing import...")
    try:
        from src.lib import audio_processing
        print("✅ Import successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return
    
    # Try calling the analyze_track function
    print("\n2️⃣ Testing analyze_track function...")
    try:
        print("🎧 Calling audio_processing.analyze_track()...")
        result = audio_processing.analyze_track(test_file)
        print(f"✅ Function call completed")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Show the actual result
        if isinstance(result, dict):
            for key, value in result.items():
                if key == 'hamms_vector' and isinstance(value, list):
                    print(f"   {key}: [{len(value)} elements] {value[:3] if len(value) > 3 else value}")
                else:
                    print(f"   {key}: {value}")
        else:
            print(f"📊 Result: {result}")
            
    except Exception as e:
        print(f"❌ analyze_track failed: {e}")
        traceback.print_exc()
        
        # Let's also check what dependencies might be missing
        print("\n🔍 Checking audio dependencies...")
        
        deps_to_check = ['librosa', 'numpy', 'scipy']
        for dep in deps_to_check:
            try:
                __import__(dep)
                print(f"   ✅ {dep} available")
            except ImportError:
                print(f"   ❌ {dep} missing")
    
    # Let's also read the audio_processing.py source to understand what it expects
    print(f"\n3️⃣ Checking audio_processing.py implementation...")
    
    try:
        with open('src/lib/audio_processing.py', 'r') as f:
            content = f.read()
            
        # Look for imports
        print("🔍 Checking imports in audio_processing.py:")
        lines = content.split('\n')
        for i, line in enumerate(lines[:20]):  # First 20 lines
            if 'import' in line:
                print(f"   Line {i+1}: {line}")
                
    except Exception as e:
        print(f"❌ Could not read audio_processing.py: {e}")

if __name__ == "__main__":
    debug_audio_analysis()