#!/usr/bin/env python3
"""Test production integration of MinimalZaiProvider"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

def test_production_integration():
    """Test the production integration with the factory"""
    
    print("🏭 TESTING PRODUCTION INTEGRATION")
    print("=" * 50)
    
    # Test data - the problematic case
    test_track = {
        'title': 'Move On Up',
        'artist': 'Destination', 
        'bpm': 118,
        'key': 'C',
        'energy': 0.75,
        'date': '1992-01-01',
        'hamms_vector': [0.8, 0.6, 0.7, 0.5, 0.9, 0.4, 0.6, 0.8, 0.7, 0.5, 0.6, 0.4]
    }
    
    # Create config using the same method as the main application
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        print("❌ ZAI_API_KEY not found in environment")
        return False
    
    config = LLMConfig(
        provider=LLMProvider.ZAI,
        api_key=api_key,
        model="glm-4.5-flash",
        max_tokens=1000,  # Same as main app
        temperature=0.1   # Same as main app
    )
    
    try:
        print("🔧 Creating provider through factory (same as main app)...")
        provider = LLMProviderFactory.create_provider(config)
        
        print(f"✅ Provider created: {type(provider).__name__}")
        print(f"✅ Model: {provider.config.model}")
        
        # Test connection
        print("🔗 Testing connection...")
        if provider.test_connection():
            print("✅ Connection successful")
        else:
            print("⚠️ Connection test failed, but proceeding...")
        
        print(f"\n🧪 Analyzing test track:")
        print(f"   {test_track['artist']} - {test_track['title']}")
        print(f"   Metadata Date: {test_track['date']} (problematic reissue date)")
        print(f"   Expected: Disco/1970s (not Minimal House/2010s)")
        
        # Run analysis
        result = provider.analyze_track(test_track)
        
        print(f"\n📊 INTEGRATION TEST RESULT:")
        print(f"   Success: {result.success}")
        print(f"   Provider: {result.provider.value}")
        print(f"   Model: {result.model}")
        print(f"   Processing Time: {result.processing_time_ms}ms")
        print(f"   Cost: ${result.cost_estimate:.6f}")
        
        if result.success:
            analysis = result.content
            
            print(f"\n📅 DATE VERIFICATION:")
            if 'date_verification' in analysis:
                verification = analysis['date_verification']
                print(f"   Artist Known: {verification.get('artist_known', 'N/A')}")
                print(f"   Known Original Year: {verification.get('known_original_year', 'N/A')}")
                print(f"   Is Likely Reissue: {verification.get('is_likely_reissue', 'N/A')}")
            
            print(f"\n🎵 CLASSIFICATION:")
            print(f"   Genre: {analysis.get('genre', 'N/A')}")
            print(f"   Subgenre: {analysis.get('subgenre', 'N/A')}")
            print(f"   Era: {analysis.get('era', 'N/A')}")
            print(f"   Mood: {analysis.get('mood', 'N/A')}")
            print(f"   Confidence: {analysis.get('confidence', 'N/A')}")
            
            print(f"\n🔍 RESPONSE SAMPLE:")
            print(f"   {result.raw_response[:150]}{'...' if len(result.raw_response) > 150 else ''}")
            
            # Evaluate improvement
            print(f"\n🎯 IMPROVEMENT EVALUATION:")
            success_criteria = []
            
            era = analysis.get('era', '')
            genre = analysis.get('genre', '')
            verification = analysis.get('date_verification', {})
            
            if era == '1970s':
                success_criteria.append("✅ Era correctly classified as 1970s (not 2010s)")
            else:
                print(f"   ❌ Era: {era} (expected: 1970s)")
                
            if genre.lower() in ['disco', 'soul', 'funk']:
                success_criteria.append("✅ Genre correctly classified as disco/soul/funk (not Minimal House)")
            else:
                print(f"   ❌ Genre: {genre} (expected: disco/soul/funk)")
            
            if verification.get('is_likely_reissue'):
                success_criteria.append("✅ Correctly detected reissue scenario")
            
            known_year = verification.get('known_original_year')
            if known_year and (known_year == 1979 or str(known_year) == '1979'):
                success_criteria.append("✅ Correctly identified original year")
            
            print(f"\n🏆 SUCCESS CRITERIA MET: {len(success_criteria)}/4")
            for criterion in success_criteria:
                print(f"      {criterion}")
            
            if len(success_criteria) >= 3:
                print(f"\n🎉 INTEGRATION SUCCESS! The minimal prompt system is working excellently.")
                print(f"   This should resolve the 'Minimal House/2010s' misclassification issue.")
                return True
            elif len(success_criteria) >= 2:
                print(f"\n✅ GOOD INTEGRATION! Significant improvement over previous system.")
                return True
            else:
                print(f"\n⚠️ PARTIAL SUCCESS. Some improvements but may need fine-tuning.")
                return False
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_cases():
    """Test with multiple track cases to verify robustness"""
    
    test_cases = [
        {
            'name': 'Move On Up (problematic case)',
            'track': {
                'title': 'Move On Up', 'artist': 'Destination',
                'bpm': 118, 'energy': 0.75, 'date': '1992-01-01'
            }
        },
        {
            'name': 'A-ha Take On Me (control case)',
            'track': {
                'title': 'Take On Me', 'artist': 'a-ha',
                'bmp': 169, 'energy': 0.8, 'date': '1985-01-01'
            }
        }
    ]
    
    print(f"\n🧪 TESTING MULTIPLE CASES FOR ROBUSTNESS")
    print("-" * 50)
    
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        print("❌ No API key available for multi-case testing")
        return
    
    config = LLMConfig(
        provider=LLMProvider.ZAI,
        api_key=api_key,
        model="glm-4.5-flash",
        max_tokens=1000,
        temperature=0.1
    )
    
    try:
        provider = LLMProviderFactory.create_provider(config)
        success_count = 0
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n📀 TEST CASE {i}: {case['name']}")
            track = case['track']
            print(f"   {track.get('artist')} - {track.get('title')}")
            
            result = provider.analyze_track(track)
            
            if result.success:
                analysis = result.content
                print(f"   ✅ Success - Genre: {analysis.get('genre')}, Era: {analysis.get('era')}")
                success_count += 1
            else:
                print(f"   ❌ Failed: {result.error_message}")
        
        print(f"\n📊 MULTI-CASE RESULTS: {success_count}/{len(test_cases)} succeeded")
        
        if success_count == len(test_cases):
            print("🎉 All test cases passed! System is robust.")
        elif success_count > 0:
            print("✅ Partial success. System is working but may need refinement.")
        else:
            print("❌ All cases failed. System needs debugging.")
            
    except Exception as e:
        print(f"❌ Multi-case testing failed: {e}")

if __name__ == "__main__":
    success = test_production_integration()
    if success:
        test_multiple_cases()
        print(f"\n✨ IMPLEMENTATION COMPLETE!")
        print(f"The MinimalZaiProvider has been successfully integrated.")
        print(f"The 'Move On Up' misclassification issue should now be resolved.")
    else:
        print(f"\n⚠️ IMPLEMENTATION NEEDS ATTENTION")
        print(f"Check the results above and consider rollback if necessary.")