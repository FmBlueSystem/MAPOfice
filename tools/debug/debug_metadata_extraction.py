#!/usr/bin/env python3
"""Debug metadata extraction - check why showing Unknown - Unknown"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.lib import audio_processing

def test_metadata_extraction():
    """Test metadata extraction from the files being processed"""
    
    print("🔍 DEBUGGING METADATA EXTRACTION")
    print("="*60)
    
    # Test files that are showing "Unknown - Unknown"
    test_files = [
        "Afrika Bambaataa, The Soulsonic Force - Planet Rock.flac",
        "Beastie Boys - Sabotage (Remastered 2009).flac", 
        "Eric B. & Rakim - Paid In Full.flac"
    ]
    
    base_path = "/Volumes/My Passport/Ojo otra vez muscia de Tidal Original descarga de musica/Consolidado2025"
    
    for filename in test_files:
        print(f"\n🎵 Testing: {filename}")
        print("-" * 50)
        
        # Try to find the file (it might be in different subdirectories)
        found_file = None
        for root, dirs, files in os.walk(base_path):
            if filename in files:
                found_file = os.path.join(root, filename)
                break
        
        if not found_file:
            print(f"   ❌ File not found in {base_path}")
            continue
            
        print(f"   📁 Found at: {found_file}")
        
        try:
            # Use our audio processing to analyze
            result = audio_processing.analyze_track(found_file)
            
            print(f"   📊 Analysis result keys: {list(result.keys())}")
            print(f"   📋 Title: '{result.get('title', 'NOT FOUND')}'")
            print(f"   👤 Artist: '{result.get('artist', 'NOT FOUND')}'")
            print(f"   💿 Album: '{result.get('album', 'NOT FOUND')}'")
            print(f"   📅 ISRC: '{result.get('isrc', 'NOT FOUND')}'")
            print(f"   📊 BPM: {result.get('bmp', 'NOT FOUND')}")
            print(f"   🎹 Key: '{result.get('key', 'NOT FOUND')}'")
            
            # Check if title/artist are empty strings vs None vs missing
            title = result.get('title')
            artist = result.get('artist')
            
            if title is None:
                print("   ⚠️  Title is None")
            elif title == "":
                print("   ⚠️  Title is empty string")
            elif title == "Unknown":
                print("   ⚠️  Title is 'Unknown'")
            else:
                print(f"   ✅ Title looks good: '{title}'")
                
            if artist is None:
                print("   ⚠️  Artist is None")
            elif artist == "":
                print("   ⚠️  Artist is empty string")
            elif artist == "Unknown":
                print("   ⚠️  Artist is 'Unknown'")
            else:
                print(f"   ✅ Artist looks good: '{artist}'")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_metadata_extraction()