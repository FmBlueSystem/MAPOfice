#!/usr/bin/env python3
"""Final test of 'Move On Up' by Destination with complete A→B fallback system"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.analysis.llm_provider import LLMConfig, LLMProvider
from src.analysis.zai_provider_enhanced import EnhancedZaiProvider

def test_move_on_up_enhanced():
    """Test the complete enhanced system with Move On Up by Destination"""
    
    # Test track data - the problematic case
    test_track = {
        'title': 'Move On Up',
        'artist': 'Destination', 
        'bpm': 118,
        'key': 'C',
        'energy': 0.75,
        'date': '1992-01-01',  # Star-Funk compilation date (incorrect metadata)
        'hamms_vector': [0.8, 0.6, 0.7, 0.5, 0.9, 0.4, 0.6, 0.8, 0.7, 0.5, 0.6, 0.4]
    }
    
    print("🎯 TESTING COMPLETE A→B FALLBACK SYSTEM")
    print("=" * 60)
    print(f"Track: {test_track['artist']} - {test_track['title']}")
    print(f"Metadata Date: {test_track['date']} (should be flagged as reissue)")
    print(f"Expected: Original 1979 disco, not 1992 Minimal House")
    print(f"BPM: {test_track['bpm']}, Energy: {test_track['energy']}")
    print("-" * 60)
    
    # Configure enhanced Z.ai provider
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        print("❌ ZAI_API_KEY not found in environment")
        return
    
    config = LLMConfig(
        provider=LLMProvider.ZAI,
        api_key=api_key,
        model="glm-4.5-flash",
        max_tokens=800,
        temperature=0.1
    )
    
    try:
        provider = EnhancedZaiProvider(config)
        print("✅ Enhanced Z.ai provider initialized")
        
        # Test connection
        if provider.test_connection():
            print("✅ Z.ai connection successful")
        else:
            print("⚠️ Z.ai connection test failed, proceeding anyway")
        
        print("\n🚀 Running enhanced analysis...")
        
        result = provider.analyze_track(test_track)
        
        print(f"\n📊 RESULT:")
        print(f"   Success: {result.success}")
        print(f"   Processing Time: {result.processing_time_ms}ms")
        cost_str = f"${result.cost_estimate:.6f}" if result.cost_estimate is not None else "N/A"
        print(f"   Cost Estimate: {cost_str}")
        
        if result.success:
            analysis = result.content
            
            print(f"\n📅 DATE VERIFICATION:")
            if 'date_verification' in analysis:
                verification = analysis['date_verification']
                print(f"   Artist Known: {verification.get('artist_known', 'N/A')}")
                print(f"   Known Original Year: {verification.get('known_original_year', 'N/A')}")
                print(f"   Metadata Year: {verification.get('metadata_year', 'N/A')}")
                print(f"   Is Likely Reissue: {verification.get('is_likely_reissue', 'N/A')}")
            else:
                print("   ⚠️ No date verification data found")
            
            print(f"\n🎵 GENRE CLASSIFICATION:")
            print(f"   Genre: {analysis.get('genre', 'N/A')}")
            print(f"   Subgenre: {analysis.get('subgenre', 'N/A')}")
            print(f"   Era: {analysis.get('era', 'N/A')}")
            print(f"   Mood: {analysis.get('mood', 'N/A')}")
            
            print(f"\n🔍 RAW RESPONSE (first 300 chars):")
            print(f"   {result.raw_response[:300]}...")
            
            # Evaluate the result
            print(f"\n🎯 EVALUATION:")
            
            era = analysis.get('era', '')
            genre = analysis.get('genre', '')
            verification = analysis.get('date_verification', {})
            known_year = verification.get('known_original_year')
            is_reissue = verification.get('is_likely_reissue', False)
            
            success_criteria = []
            
            if known_year == 1979:
                success_criteria.append("✅ Correctly identified 1979 as original year")
            elif known_year is not None and str(known_year) in ['1979', 1979]:
                success_criteria.append("✅ Recognized original year (format variation)")
            
            if is_reissue:
                success_criteria.append("✅ Correctly flagged 1992 as reissue/compilation")
            
            if era == '1970s':
                success_criteria.append("✅ Era correctly classified as 1970s")
            
            if genre.lower() in ['disco', 'soul', 'funk']:
                success_criteria.append("✅ Genre correctly classified as disco/soul/funk")
            
            if success_criteria:
                print(f"   {len(success_criteria)} success criteria met:")
                for criterion in success_criteria:
                    print(f"      {criterion}")
                
                if len(success_criteria) >= 3:
                    print(f"\n🎉 EXCELLENT SUCCESS! The system correctly handled the reissue scenario.")
                    print(f"   This fixes the 'Minimal House/2010s' misclassification issue.")
                elif len(success_criteria) >= 2:
                    print(f"\n✅ GOOD SUCCESS! Major improvement over previous classification.")
                else:
                    print(f"\n⚠️ PARTIAL SUCCESS. Some improvements but needs refinement.")
            else:
                print(f"   ❌ No key success criteria met")
                print(f"   Era: {era} (expected: 1970s)")
                print(f"   Genre: {genre} (expected: disco/soul/funk)")
                print(f"   Known Year: {known_year} (expected: 1979)")
                print(f"   Is Reissue: {is_reissue} (expected: True)")
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_move_on_up_enhanced()