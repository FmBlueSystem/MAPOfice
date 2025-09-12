#!/usr/bin/env python3
"""Quick test of Z.ai connection with the glm-4.5-flash model"""

import os
from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

def test_zai_model():
    """Test the Chinese GLM-4.5-Flash model"""
    
    # Check if API key is available
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        print("❌ No ZAI_API_KEY environment variable found")
        return False
    
    print(f"✅ Found ZAI API key: {api_key[:8]}...")
    
    try:
        # Create Z.ai provider config
        config = LLMConfig(
            provider=LLMProvider.ZAI,
            api_key=api_key,
            model="glm-4.5-flash",  # The Chinese model you mentioned
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"🔧 Created config for model: {config.model}")
        
        # Create provider
        provider = LLMProviderFactory.create_provider(config)
        print("✅ Successfully created Z.ai provider")
        
        # Test connection
        print("🔍 Testing connection...")
        is_connected = provider.test_connection()
        
        if is_connected:
            print("✅ Z.ai connection successful!")
            
            # Test a simple track analysis
            test_track = {
                "title": "Test Song",
                "artist": "Test Artist", 
                "bpm": 120,
                "key": "C major",
                "energy": 0.7,
                "date": "2024",
                "hamms_vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.8, 0.6]
            }
            
            print("🎵 Testing track analysis...")
            result = provider.analyze_track(test_track)
            
            if result.success:
                print("✅ Track analysis successful!")
                print(f"📊 Result: {result.content}")
                print(f"⏱️  Processing time: {result.processing_time_ms}ms")
                return True
            else:
                print(f"❌ Track analysis failed: {result.error_message}")
                return False
        else:
            print("❌ Z.ai connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Z.ai: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Z.ai GLM-4.5-Flash model...")
    success = test_zai_model()
    
    if not success:
        print("\n💡 Possible solutions:")
        print("1. Check if ZAI_API_KEY is correctly set")
        print("2. Verify Z.ai service is available")
        print("3. Try switching to OpenAI or Gemini provider")
        print("4. Check internet connection")