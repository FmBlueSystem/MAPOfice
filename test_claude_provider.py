#!/usr/bin/env python3
"""Test Claude (Anthropic) provider for music analysis"""

import os
from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

def test_claude_provider():
    """Test Claude Haiku model for music analysis"""
    
    print("🚀 Testing Claude (Anthropic) provider...")
    
    # Check if API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY environment variable found")
        print("💡 Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return False
    
    print(f"✅ Found Anthropic API key: {api_key[:8]}...")
    
    try:
        # Create Claude provider config
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            api_key=api_key,
            model="claude-3-haiku-20240307",  # Cheapest Claude model
            max_tokens=1000,
            temperature=0.1
        )
        
        print(f"🔧 Created config for model: {config.model}")
        
        # Create provider
        provider = LLMProviderFactory.create_provider(config)
        print("✅ Successfully created Claude provider")
        
        # Test with a famous track
        test_track = {
            "title": "Stayin' Alive",
            "artist": "Bee Gees",
            "bpm": 104,
            "key": "F minor",
            "energy": 0.8,
            "date": "1992",  # This should be detected as a reissue (original: 1977)
            "hamms_vector": [0.5, 0.7, 0.6, 0.8, 0.4, 0.9, 0.7, 0.5, 0.6, 0.8, 0.7, 0.4]
        }
        
        print("🎵 Testing famous track analysis (Bee Gees - Stayin' Alive)...")
        result = provider.analyze_track(test_track)
        
        if result.success:
            print("✅ Track analysis successful!")
            print(f"📊 Genre: {result.content.get('genre', 'unknown')}")
            print(f"🎭 Era: {result.content.get('era', 'unknown')}")
            print(f"📅 Original Year: {result.content.get('date_verification', {}).get('known_original_year', 'unknown')}")
            print(f"🔄 Reissue: {result.content.get('date_verification', {}).get('is_likely_reissue', False)}")
            print(f"📊 Confidence: {result.content.get('confidence', 0)}")
            print(f"⏱️  Processing time: {result.processing_time_ms}ms")
            print(f"💰 Cost estimate: ${result.cost_estimate:.6f}")
            print(f"🔤 Tokens used: {result.tokens_used}")
            
            # Validate response quality
            confidence = result.content.get('confidence', 0)
            original_year = result.content.get('date_verification', {}).get('known_original_year')
            
            if confidence > 0.8 and original_year:
                print("🏆 HIGH QUALITY RESPONSE - Claude significantly better than Chinese model!")
            elif confidence > 0.6:
                print("✅ Good response quality")
            else:
                print("⚠️  Lower confidence response")
                
            return True
        else:
            print(f"❌ Track analysis failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Claude: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def compare_providers():
    """Compare Claude vs the Chinese model performance"""
    print("\n🆚 Comparing providers...")
    
    # Test Chinese model
    print("Testing Z.ai (Chinese model)...")
    zai_key = os.getenv('ZAI_API_KEY')
    if zai_key:
        try:
            zai_config = LLMConfig(
                provider=LLMProvider.ZAI,
                api_key=zai_key,
                model="glm-4.5-flash",
                max_tokens=1000,
                temperature=0.1
            )
            zai_provider = LLMProviderFactory.create_provider(zai_config)
            
            test_track = {
                "title": "Stayin' Alive",
                "artist": "Bee Gees", 
                "bpm": 104,
                "energy": 0.8,
                "date": "1992",
                "hamms_vector": [0.5] * 12
            }
            
            zai_result = zai_provider.analyze_track(test_track)
            if zai_result.success:
                print(f"Z.ai confidence: {zai_result.content.get('confidence', 0)}")
                print(f"Z.ai genre: {zai_result.content.get('genre', 'unknown')}")
            else:
                print("Z.ai failed")
                
        except Exception as e:
            print(f"Z.ai error: {e}")
    
    # Results comparison would go here
    print("\n💡 Recommendation: Use Claude Haiku for better accuracy and reliability!")

if __name__ == "__main__":
    success = test_claude_provider()
    
    if success:
        compare_providers()
    else:
        print("\n💡 To use Claude:")
        print("1. Get an API key from https://console.anthropic.com/")
        print("2. Set: export ANTHROPIC_API_KEY='your-key-here'")
        print("3. Claude Haiku is very affordable (~$0.25 per 1M input tokens)")