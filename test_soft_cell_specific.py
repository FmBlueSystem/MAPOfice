#!/usr/bin/env python3
"""Test específico para Soft Cell para ver qué está prediciendo Claude"""

import os
from dotenv import load_dotenv
from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

load_dotenv()

def test_soft_cell_prediction():
    """Test específico de Soft Cell para debug"""
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No API key")
        return
    
    config = LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        api_key=api_key,
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.1
    )
    
    provider = LLMProviderFactory.create_provider(config)
    
    # Datos reales de Soft Cell del metadata
    track_data = {
        'title': 'Tainted Love / Where Did Our Love Go? (Extended Version)',
        'artist': 'Soft Cell',
        'bpm': 120,
        'energy': 0.7,
        'key': 'Unknown',
        'date': '2002',  # Metadata real (reedición)
        'hamms_vector': [0.5] * 12
    }
    
    print("🔍 Testing Soft Cell specifically...")
    print(f"Track: {track_data['artist']} - {track_data['title']}")
    print(f"Metadata year: {track_data['date']}")
    print()
    
    result = provider.analyze_track(track_data)
    
    if result.success:
        print("✅ Claude Response:")
        print(f"Raw response: {result.raw_response}")
        print()
        print("📊 Parsed content:")
        for key, value in result.content.items():
            print(f"   {key}: {value}")
        
        # Check specific fields
        predicted_genre = result.content.get('genre', '')
        predicted_era = result.content.get('era', '')
        predicted_year = result.content.get('date_verification', {}).get('known_original_year')
        is_reissue = result.content.get('date_verification', {}).get('is_likely_reissue', False)
        confidence = result.content.get('confidence', 0)
        
        print(f"\n🎯 Key predictions:")
        print(f"   Genre: {predicted_genre}")
        print(f"   Era: {predicted_era}")
        print(f"   Original year: {predicted_year}")
        print(f"   Is reissue: {is_reissue}")
        print(f"   Confidence: {confidence}")
        
        print(f"\n🤔 Analysis:")
        if is_reissue and predicted_year and predicted_year < 2002:
            print("✅ Claude CORRECTLY detected this is a reissue!")
            print(f"   Original: {predicted_year}, Metadata: 2002")
        else:
            print("❌ Claude didn't detect reissue properly")
            
    else:
        print(f"❌ Analysis failed: {result.error_message}")

if __name__ == "__main__":
    test_soft_cell_prediction()