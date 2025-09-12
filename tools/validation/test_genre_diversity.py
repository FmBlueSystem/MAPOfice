#!/usr/bin/env python3
"""Test genre diversity - verify Claude doesn't classify everything as Disco"""

import os
from dotenv import load_dotenv
from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

load_dotenv()

def test_diverse_genres():
    """Test with tracks that should NOT be classified as Disco"""
    
    print("🎵 Testing Genre Diversity - Fixing Disco Bias")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found")
        return
    
    # Create Claude provider
    config = LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        api_key=api_key,
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.1
    )
    
    provider = LLMProviderFactory.create_provider(config)
    
    # Diverse test tracks that should NOT be Disco
    test_tracks = [
        {
            "title": "Smells Like Teen Spirit",
            "artist": "Nirvana", 
            "bpm": 116,
            "energy": 0.9,
            "date": "1991",
            "expected_genre": "Grunge/Alternative Rock"
        },
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "bpm": 72,
            "energy": 0.7,
            "date": "1975", 
            "expected_genre": "Progressive Rock/Art Rock"
        },
        {
            "title": "Billie Jean",
            "artist": "Michael Jackson",
            "bpm": 117,
            "energy": 0.8,
            "date": "1982",
            "expected_genre": "Pop/R&B"
        },
        {
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "bpm": 125,
            "energy": 0.8,
            "date": "1987",
            "expected_genre": "Hard Rock/Heavy Metal"
        },
        {
            "title": "Blue Monday",
            "artist": "New Order",
            "bpm": 120,
            "energy": 0.7,
            "date": "1983",
            "expected_genre": "New Wave/Electronic"
        },
        {
            "title": "What's Going On",
            "artist": "Marvin Gaye",
            "bpm": 96,
            "energy": 0.5,
            "date": "1971",
            "expected_genre": "Soul/R&B"
        }
    ]
    
    results = []
    disco_count = 0
    
    for track in test_tracks:
        print(f"\n🎵 Testing: {track['artist']} - {track['title']}")
        print(f"   Expected: {track['expected_genre']}")
        
        result = provider.analyze_track(track)
        
        if result.success:
            genre = result.content.get('genre', 'unknown')
            confidence = result.content.get('confidence', 0)
            era = result.content.get('era', 'unknown')
            
            print(f"   🤖 Claude: {genre} (confidence: {confidence})")
            print(f"   📅 Era: {era}")
            
            # Check if incorrectly classified as disco
            if 'disco' in genre.lower():
                print(f"   ❌ INCORRECTLY classified as Disco!")
                disco_count += 1
            else:
                print(f"   ✅ Correctly avoided Disco classification")
            
            results.append({
                'track': f"{track['artist']} - {track['title']}",
                'expected': track['expected_genre'],
                'actual': genre,
                'confidence': confidence,
                'is_disco': 'disco' in genre.lower()
            })
        else:
            print(f"   ❌ Analysis failed: {result.error_message}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    total_tracks = len(test_tracks)
    correct_non_disco = total_tracks - disco_count
    
    print(f"Total tracks tested: {total_tracks}")
    print(f"Correctly NOT classified as Disco: {correct_non_disco}")
    print(f"Incorrectly classified as Disco: {disco_count}")
    print(f"Success rate: {(correct_non_disco/total_tracks)*100:.1f}%")
    
    if disco_count == 0:
        print("\n🎉 SUCCESS! No inappropriate Disco classifications!")
        print("✅ Genre diversity problem FIXED!")
    elif disco_count <= 1:
        print("\n✅ Good! Minimal disco bias (1 false positive)")
    else:
        print(f"\n⚠️  Still some disco bias ({disco_count} false positives)")
    
    print("\nDetailed results:")
    for r in results:
        status = "❌ DISCO" if r['is_disco'] else "✅ Good"
        print(f"  {status} {r['track']}: {r['actual']} (conf: {r['confidence']})")
    
    return disco_count == 0

if __name__ == "__main__":
    success = test_diverse_genres()
    
    if success:
        print("\n🚀 Ready to use the app with improved genre classification!")
    else:
        print("\n💡 May need further prompt refinement for specific cases")