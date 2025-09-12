#!/usr/bin/env python3
"""Test script for date verification system with Move On Up by Destination"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

def test_date_verification():
    """Test the new date verification system with Move On Up by Destination"""
    
    # Create test track data with metadata date from compilation
    test_track = {
        'title': 'Move On Up',
        'artist': 'Destination', 
        'bpm': 118,
        'key': 'C',
        'energy': 0.75,
        'date': '1992-01-01',  # This is the Star-Funk compilation date, not original
        'hamms_vector': [0.8, 0.6, 0.7, 0.5, 0.9, 0.4, 0.6, 0.8, 0.7, 0.5, 0.6, 0.4]
    }
    
    # Configure Z.ai provider
    config = LLMConfig(
        provider=LLMProvider.ZAI,
        api_key=os.getenv('ZAI_API_KEY'),
        model="glm-4.5-flash",
        max_tokens=800,
        temperature=0.1
    )
    
    try:
        # Create provider and analyze
        provider = LLMProviderFactory.create_provider(config)
        print("🔄 Testing date verification system...")
        print(f"Track: {test_track['artist']} - {test_track['title']}")
        print(f"Metadata Date: {test_track['date']}")
        print(f"BPM: {test_track['bpm']}, Energy: {test_track['energy']}")
        print("-" * 60)
        
        result = provider.analyze_track(test_track)
        
        if result.success:
            print("✅ Analysis successful!")
            print(f"Raw response: {result.raw_response}")
            print("-" * 60)
            
            # Extract and display the verification results
            analysis = result.content
            print("📅 DATE VERIFICATION RESULTS:")
            
            if 'date_verification' in analysis:
                verification = analysis['date_verification']
                print(f"   Artist Known: {verification.get('artist_known', 'N/A')}")
                print(f"   Track Known: {verification.get('track_known', 'N/A')}")
                print(f"   Known Original Year: {verification.get('known_original_year', 'N/A')}")
                print(f"   Metadata Year: {verification.get('metadata_year', 'N/A')}")
                print(f"   Is Likely Reissue: {verification.get('is_likely_reissue', 'N/A')}")
                print(f"   Notes: {verification.get('verification_notes', 'N/A')}")
            else:
                print("   ❌ No date verification data found")
            
            print("\n🎵 GENRE CLASSIFICATION:")
            print(f"   Genre: {analysis.get('genre', 'N/A')}")
            print(f"   Subgenre: {analysis.get('subgenre', 'N/A')}")
            print(f"   Era: {analysis.get('era', 'N/A')}")
            print(f"   Mood: {analysis.get('mood', 'N/A')}")
            
            # Check the simplified verification results
            artist_known = analysis.get('artist_known', False)
            known_year = analysis.get('known_year')
            is_reissue = analysis.get('is_reissue', False)
            era = analysis.get('era')
            genre = analysis.get('genre')
            
            print(f"   Artist Known: {artist_known}")
            print(f"   Known Year: {known_year}")
            print(f"   Is Reissue: {is_reissue}")
            
            # Check if the verification worked correctly
            if era == '1970s' and genre == 'disco':
                print("\n✅ SUCCESS: Correctly classified as 1970s Disco despite 1992 metadata!")
                print("   This fixes the previous 'Minimal House' / '2010s' misclassification")
            elif era == '1970s':
                print("\n✅ PARTIAL SUCCESS: Era correctly classified as 1970s")
            else:
                print(f"\n⚠️  NEEDS WORK: Era classified as {era}, expected 1970s")
            
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_date_verification()