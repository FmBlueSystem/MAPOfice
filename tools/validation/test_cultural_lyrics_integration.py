#!/usr/bin/env python3
"""
Test script for Cultural Context and Lyrics Analysis Integration
in the Music Analyzer Pro playlist generation system.

This tests the new scoring functions and enhanced playlist generation
with cultural context and lyrics data integration.
"""

import sys
import os
sys.path.append('/Users/freddymolina/Desktop/MAP 4')

from src.services.playlist import (
    cultural_context_score,
    lyrics_similarity_score, 
    cohesion_score,
    generate_enhanced_playlist
)

def create_sample_track(
    path="test_track.mp3",
    artist="Test Artist", 
    title="Test Song",
    bpm=120,
    hamms=None,
    cultural_context=None,
    lyrics=None
):
    """Create a sample track for testing"""
    if hamms is None:
        hamms = [0.7, 0.6, 0.8, 0.75, 0.6, 0.3, 0.2, 0.8, 0.7, 0.9, 0.65, 0.8]
    
    track = {
        "path": path,
        "artist": artist,
        "title": title,
        "bpm": bpm,
        "key": "G",  # Added required key field
        "energy": 0.8,
        "hamms": hamms,
        "subgenre": "Tech House",
        "era": "2020s",
        "mood": "Energetic"
    }
    
    if cultural_context:
        track["cultural_context"] = cultural_context
    
    if lyrics:
        track["lyrics"] = lyrics
        
    return track

def test_cultural_context_scoring():
    """Test cultural context similarity scoring"""
    print("🧪 Testing Cultural Context Scoring...")
    
    # Create tracks with similar cultural contexts
    cultural_data_1 = {
        "club_scenes": ["house", "techno", "edm_2020s"],
        "production_markers": ["streaming_mix", "loudness_era", "sample_based_breaks"],
        "media_formats": ["streaming", "mp3"],
        "distribution_channels": ["editorial_playlists", "social_media"]
    }
    
    cultural_data_2 = {
        "club_scenes": ["house", "tech_house", "edm_2020s"],
        "production_markers": ["streaming_mix", "loudness_era", "digital_mastering"],
        "media_formats": ["streaming", "mp3", "wav"],
        "distribution_channels": ["editorial_playlists", "blogs_p2p"]
    }
    
    track1 = create_sample_track("track1.mp3", cultural_context=cultural_data_1)
    track2 = create_sample_track("track2.mp3", cultural_context=cultural_data_2)
    
    score = cultural_context_score(track1, track2)
    print(f"   Cultural similarity score: {score:.3f}")
    
    # Test with missing data
    track3 = create_sample_track("track3.mp3")  # No cultural context
    score_missing = cultural_context_score(track1, track3)
    print(f"   Score with missing data: {score_missing:.3f}")
    
    assert 0.0 <= score <= 1.0, "Score should be between 0 and 1"
    assert score_missing == 0.5, "Missing data should return neutral score"
    print("   ✅ Cultural context scoring tests passed!")

def test_lyrics_similarity_scoring():
    """Test lyrics similarity scoring"""
    print("🧪 Testing Lyrics Similarity Scoring...")
    
    # Create tracks with similar lyrics
    lyrics_data_1 = {
        "available": True,
        "confidence": 0.85,
        "language": "en",
        "common_phrases": ["dance floor", "feel the beat", "tonight", "music loud"],
        "rhyme_seeds": ["ight", "eat", "oor", "ay"]
    }
    
    lyrics_data_2 = {
        "available": True,
        "confidence": 0.90,
        "language": "en", 
        "common_phrases": ["dance floor", "party night", "feel alive", "music loud"],
        "rhyme_seeds": ["ight", "oor", "ive", "ay"]
    }
    
    track1 = create_sample_track("track1.mp3", lyrics=lyrics_data_1)
    track2 = create_sample_track("track2.mp3", lyrics=lyrics_data_2)
    
    score = lyrics_similarity_score(track1, track2)
    print(f"   Lyrics similarity score: {score:.3f}")
    
    # Test with low confidence
    lyrics_low_conf = lyrics_data_1.copy()
    lyrics_low_conf["confidence"] = 0.3
    track3 = create_sample_track("track3.mp3", lyrics=lyrics_low_conf)
    score_low_conf = lyrics_similarity_score(track1, track3)
    print(f"   Score with low confidence: {score_low_conf:.3f}")
    
    assert 0.0 <= score <= 1.0, "Score should be between 0 and 1"
    assert score_low_conf == 0.5, "Low confidence should return neutral score"
    print("   ✅ Lyrics similarity scoring tests passed!")

def test_cohesion_scoring():
    """Test playlist cohesion scoring"""
    print("🧪 Testing Playlist Cohesion Scoring...")
    
    # Create tracks with cohesion data
    cohesion_data_1 = {
        "playlist_cohesion": {
            "bpm_band": {"cruise": [117, 123], "lift": [126, 128], "reset": [112, 114]},
            "energy_window": [0.7, 0.9],
            "valence_window": [0.5, 0.8],
            "cohesive_hooks": ["club energy", "peak time", "dance floor"]
        }
    }
    
    cohesion_data_2 = {
        "playlist_cohesion": {
            "bpm_band": {"cruise": [118, 124], "lift": [127, 129], "reset": [113, 115]},
            "energy_window": [0.75, 0.85],
            "valence_window": [0.6, 0.9],
            "cohesive_hooks": ["club energy", "night vibes", "dance floor"]
        }
    }
    
    track1 = create_sample_track("track1.mp3", bpm=120)
    track1["cultural_context"] = cohesion_data_1
    track1["energy"] = 0.8
    track1["hamms"] = [0.7, 0.6, 0.8, 0.75, 0.65, 0.3, 0.2, 0.8, 0.7, 0.9, 0.65, 0.8]  # valence = 0.65
    
    track2 = create_sample_track("track2.mp3", bpm=122)  # Within cruise range
    track2["cultural_context"] = cohesion_data_2
    track2["energy"] = 0.82
    track2["hamms"] = [0.7, 0.6, 0.8, 0.75, 0.7, 0.3, 0.2, 0.8, 0.7, 0.9, 0.65, 0.8]  # valence = 0.7
    
    score = cohesion_score(track1, track2)
    print(f"   Cohesion score: {score:.3f}")
    
    assert 0.0 <= score <= 1.0, "Score should be between 0 and 1"
    print("   ✅ Playlist cohesion scoring tests passed!")

def test_enhanced_playlist_generation():
    """Test enhanced playlist generation with cultural and lyrics data"""
    print("🧪 Testing Enhanced Playlist Generation...")
    
    # Create a seed track with full cultural and lyrics data
    seed = create_sample_track(
        "seed.mp3", "DJ Producer", "Club Anthem", 128,
        cultural_context={
            "club_scenes": ["house", "tech_house"],
            "production_markers": ["streaming_mix", "loudness_era"],
            "media_formats": ["streaming", "mp3"],
            "distribution_channels": ["editorial_playlists"],
            "playlist_cohesion": {
                "bpm_band": {"cruise": [125, 131], "lift": [134, 136], "reset": [120, 122]},
                "energy_window": [0.7, 0.9],
                "valence_window": [0.6, 0.8],
                "cohesive_hooks": ["peak time", "club energy"]
            }
        },
        lyrics={
            "available": True,
            "confidence": 0.9,
            "language": "en",
            "common_phrases": ["dance all night", "feel the beat", "club vibes"],
            "rhyme_seeds": ["ight", "eat", "eat", "ibe"]
        }
    )
    
    # Create candidate tracks
    candidates = []
    for i in range(15):
        candidate = create_sample_track(
            f"candidate_{i}.mp3", f"Artist {i}", f"Track {i}", 125 + (i % 10),
            cultural_context={
                "club_scenes": ["house", "techno"] if i % 2 == 0 else ["tech_house", "progressive"],
                "production_markers": ["streaming_mix", "digital_mastering"],
                "media_formats": ["streaming", "mp3"],
                "distribution_channels": ["editorial_playlists"],
                "playlist_cohesion": {
                    "bpm_band": {"cruise": [122 + i, 128 + i], "lift": [131 + i, 133 + i], "reset": [117 + i, 119 + i]},
                    "energy_window": [0.6 + (i * 0.02), 0.8 + (i * 0.02)],
                    "valence_window": [0.5 + (i * 0.02), 0.7 + (i * 0.02)],
                    "cohesive_hooks": ["club energy"] if i % 3 == 0 else ["dance vibes"]
                }
            },
            lyrics={
                "available": True,
                "confidence": 0.8 + (i * 0.01),
                "language": "en",
                "common_phrases": ["dance floor", "beat drop"] if i % 2 == 0 else ["party time", "feel alive"],
                "rhyme_seeds": ["oor", "op"] if i % 2 == 0 else ["ime", "ive"]
            }
        )
        candidates.append(candidate)
    
    try:
        # Generate playlist with custom weights
        playlist = generate_enhanced_playlist(
            seed=seed,
            candidates=candidates,
            length=5,
            cultural_weight=0.15,
            lyrics_weight=0.15,
            hamms_weight=0.25,
            subgenre_weight=0.20,
            era_weight=0.15,
            mood_weight=0.10
        )
        
        print(f"   Generated playlist with {len(playlist)} tracks")
        for i, track in enumerate(playlist):
            print(f"   {i+1}. {track['artist']} - {track['title']} ({track['bpm']} BPM)")
        
        assert len(playlist) >= 1, "Should generate at least the seed track"
        assert playlist[0] == seed, "First track should be the seed"
        print("   ✅ Enhanced playlist generation tests passed!")
        
    except Exception as e:
        print(f"   ❌ Enhanced playlist generation failed: {e}")
        raise

def main():
    """Run all tests"""
    print("🎵 Testing Cultural Context and Lyrics Analysis Integration")
    print("=" * 60)
    
    try:
        test_cultural_context_scoring()
        print()
        test_lyrics_similarity_scoring() 
        print()
        test_cohesion_scoring()
        print()
        test_enhanced_playlist_generation()
        print()
        print("🎉 All tests passed! Cultural context and lyrics integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()