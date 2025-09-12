#!/usr/bin/env python3
"""Test improved LLM prompt for more accurate era and genre classification"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analysis.zai_provider import ZaiProvider
from src.analysis.llm_provider import LLMConfig, LLMProvider

def test_improved_classifications():
    """Test improved LLM prompt with known examples"""
    
    # Configure Z.ai with FREE model
    config = LLMConfig(
        provider=LLMProvider.ZAI,
        api_key='7a044e0cddc24efa8cc389d9bb341303.6ZNIoCWQzPd5SELo',
        model='glm-4.5-flash',
        max_tokens=200,
        temperature=0.1
    )

    provider = ZaiProvider(config)
    
    # Test cases with known correct classifications
    test_cases = [
        {
            "name": "The Police - De Do Do Do, De Da Da Da",
            "data": {
                'hamms_vector': [0.6, 0.4, 0.8, 0.3, 0.7, 0.5, 0.6, 0.2, 0.8, 0.4, 0.6, 0.7],
                'bpm': 147,
                'key': '11B',
                'energy': 0.6,
                'title': 'De Do Do Do, De Da Da Da',
                'artist': 'The Police'
            },
            "expected": {
                "genre": "New Wave",
                "era": "1980s"
            }
        },
        {
            "name": "A Flock of Seagulls - Space Age Love Song",
            "data": {
                'hamms_vector': [0.5, 0.3, 0.7, 0.2, 0.8, 0.4, 0.6, 0.1, 0.9, 0.3, 0.5, 0.7],
                'bpm': 140,
                'key': '10B',
                'energy': 0.7,
                'title': 'Space Age Love Song',
                'artist': 'A Flock of Seagulls'
            },
            "expected": {
                "genre": "Synthpop",
                "era": "1980s"
            }
        },
        {
            "name": "Beatles - Hey Jude (test 1960s classification)",
            "data": {
                'hamms_vector': [0.7, 0.6, 0.5, 0.4, 0.6, 0.7, 0.5, 0.3, 0.6, 0.8, 0.4, 0.5],
                'bpm': 72,
                'key': 'F',
                'energy': 0.5,
                'title': 'Hey Jude',
                'artist': 'The Beatles'
            },
            "expected": {
                "genre": "Rock",
                "era": "1960s"
            }
        }
    ]

    print("🧪 Testing improved LLM prompt for era and genre accuracy...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        response = provider.analyze_track(test_case['data'])
        
        if response.success:
            print(f"✅ Analysis successful!")
            print(f"🎭 Genre: {response.content.get('genre')}")
            print(f"🎵 Subgenre: {response.content.get('subgenre')}")
            print(f"📅 Era: {response.content.get('era')}")
            print(f"😊 Mood: {response.content.get('mood')}")
            print(f"🏷️  Tags: {response.content.get('tags')}")
            print(f"💪 Confidence: {response.content.get('confidence')}")
            
            # Check accuracy
            expected = test_case['expected']
            actual_genre = response.content.get('genre', '')
            actual_era = response.content.get('era', '')
            
            genre_match = expected['genre'].lower() in actual_genre.lower()
            era_match = expected['era'] == actual_era
            
            print(f"\n📊 Accuracy Check:")
            print(f"   Genre: {'✅' if genre_match else '❌'} Expected: {expected['genre']}, Got: {actual_genre}")
            print(f"   Era: {'✅' if era_match else '❌'} Expected: {expected['era']}, Got: {actual_era}")
            
        else:
            print(f"❌ Analysis failed: {response.error_message}")
            
        print("\n" + "=" * 60)

if __name__ == '__main__':
    test_improved_classifications()