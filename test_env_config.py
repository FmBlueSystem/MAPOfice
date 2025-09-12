#!/usr/bin/env python3
"""Test que .env configuracion funciona correctamente"""

import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

def test_env_configuration():
    """Test que todas las variables del .env se cargan correctamente"""
    
    print("🔍 Testing .env configuration...")
    
    # Check Claude API key
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    if claude_key:
        print(f"✅ ANTHROPIC_API_KEY loaded: {claude_key[:15]}...")
    else:
        print("❌ ANTHROPIC_API_KEY not found")
    
    # Check LLM provider setting
    llm_provider = os.getenv('LLM_PROVIDER')
    print(f"🤖 LLM_PROVIDER: {llm_provider}")
    
    # Check other settings
    print(f"🔄 LLM_FALLBACK_ENABLED: {os.getenv('LLM_FALLBACK_ENABLED')}")
    print(f"🎯 ANTHROPIC_MODEL: {os.getenv('ANTHROPIC_MODEL')}")
    
    # Test that our LLM system can use these variables
    print("\n🚀 Testing LLM provider creation...")
    
    try:
        from src.analysis.llm_provider import get_recommended_configs
        
        configs = get_recommended_configs()
        
        if configs:
            print(f"✅ Found {len(configs)} available LLM configurations:")
            for i, config in enumerate(configs, 1):
                print(f"   {i}. {config.provider.value}: {config.model}")
                
            # Test the first (preferred) configuration
            first_config = configs[0]
            if first_config.provider.value == 'anthropic':
                print("🎯 ✅ Claude is the preferred provider!")
            else:
                print(f"⚠️  Preferred provider is {first_config.provider.value}, not Claude")
                
        else:
            print("❌ No LLM configurations available")
            
    except Exception as e:
        print(f"❌ Error testing LLM configs: {e}")
    
    print("\n" + "="*50)
    print("🎵 Ready to test with a real track analysis...")
    
    return claude_key is not None

if __name__ == "__main__":
    success = test_env_configuration()
    
    if success:
        print("✅ .env configuration is working!")
        print("\n🚀 To launch the app:")
        print("  source .venv/bin/activate")
        print("  python -m src.ui.enhanced_main_window")
    else:
        print("❌ .env configuration has issues")