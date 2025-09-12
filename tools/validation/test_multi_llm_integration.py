#!/usr/bin/env python3
"""Test MultiLLMEnricher integration with Claude provider"""

import os
from dotenv import load_dotenv
from src.analysis.multi_llm_enricher import MultiLLMEnricher

load_dotenv()

def test_multi_llm_integration():
    """Test that Claude is properly integrated as preferred provider"""
    
    print("🧪 TESTING MULTI-LLM INTEGRATION")
    print("="*60)
    
    # Check environment variables
    print("📋 Environment Variables:")
    print(f"   LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
    print(f"   ANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
    print(f"   ZAI_API_KEY: {'SET' if os.getenv('ZAI_API_KEY') else 'NOT SET'}")
    
    # Test MultiLLMEnricher with anthropic preference
    print(f"\n🤖 Creating MultiLLMEnricher with preferred provider: 'anthropic'")
    enricher = MultiLLMEnricher(preferred_provider="anthropic")
    
    # Check available providers
    available = enricher.get_available_providers()
    print(f"📊 Available providers: {available}")
    
    # Check current provider
    if enricher.current_provider:
        current = enricher.current_provider.config.provider.value
        model = enricher.current_provider.config.model
        print(f"🎯 Current provider: {current}")
        print(f"🤖 Current model: {model}")
        
        if current == "anthropic":
            print("✅ SUCCESS: Claude is the primary provider!")
        else:
            print(f"❌ PROBLEM: Expected 'anthropic', got '{current}'")
    else:
        print("❌ No current provider set")
    
    # Test with a sample track
    if enricher.current_provider and enricher.current_provider.config.provider.value == "anthropic":
        print(f"\n🎵 Testing analysis with Claude...")
        
        sample_track = {
            'title': 'Venus (Extended Version)',
            'artist': 'Bananarama',
            'bpm': 129.2,
            'energy': 0.206,
            'key': 'E',
            'date': '1986',
            'hamms_vector': [0.075, 0.079, 0.079, 0.076, 0.092, 0.081, 0.088, 0.088, 0.088, 0.080, 0.083, 0.090]
        }
        
        result = enricher.analyze_track(sample_track)
        
        if result.success:
            print("✅ Claude analysis successful!")
            print(f"   🎭 Genre: {result.genre}")
            print(f"   📅 Era: {result.era}")
            print(f"   📊 Confidence: {result.ai_confidence}")
            print(f"   🤖 Model: {result.ai_model}")
            print(f"   🔗 Provider: {result.provider}")
        else:
            print(f"❌ Claude analysis failed: {result.error_message}")

if __name__ == "__main__":
    test_multi_llm_integration()