#!/usr/bin/env python3
"""Debug Z.ai GLM-4.5-Flash responses to understand parsing issues"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

def debug_zai_raw_response():
    """Debug raw Z.ai response to understand the exact format"""
    
    if ZaiClient is None:
        print("❌ zai-sdk package is not installed")
        return
    
    client = ZaiClient(api_key='7a044e0cddc24efa8cc389d9bb341303.6ZNIoCWQzPd5SELo')
    
    # Simple test prompt first
    messages = [
        {"role": "system", "content": "You are a music analyst. Respond only with valid JSON."},
        {"role": "user", "content": """Analyze The Police - "De Do Do Do, De Da Da Da" (BPM: 147, Key: 11B, Energy: 0.6).

Return JSON with:
{
  "genre": "specific genre",
  "subgenre": "specific subgenre", 
  "era": "decade like 1980s",
  "mood": "mood description"
}"""}
    ]
    
    print("🔍 Testing Z.ai GLM-4.5-Flash raw response...")
    print("=" * 60)
    
    try:
        response = client.chat.completions.create(
            model='glm-4.5-flash',
            messages=messages,
            max_tokens=300,
            temperature=0.1
        )
        
        print("📤 Raw API Response:")
        print(f"Model: {response.model}")
        print(f"Choices count: {len(response.choices)}")
        
        if response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            print(f"\n📨 Message object attributes:")
            print(f"  - role: {message.role}")
            print(f"  - content: '{message.content}'")
            print(f"  - content length: {len(message.content) if message.content else 0}")
            
            if hasattr(message, 'reasoning_content'):
                print(f"  - reasoning_content: '{message.reasoning_content}'")
                print(f"  - reasoning length: {len(message.reasoning_content) if message.reasoning_content else 0}")
            
            print(f"\n📄 Full content field:")
            print(f"'{message.content}'")
            
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                print(f"\n🧠 Full reasoning_content field:")
                print(f"'{message.reasoning_content}'")
                
                # Try to extract JSON manually
                reasoning = message.reasoning_content
                print(f"\n🔍 Searching for JSON in reasoning_content...")
                
                # Look for JSON patterns
                import re
                
                # Try different JSON extraction patterns
                patterns = [
                    r'\{[^{}]*\}',  # Simple single-level JSON
                    r'\{(?:[^{}]|{[^{}]*})*\}',  # Nested JSON
                    r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
                    r'(\{.*?\})',  # Any JSON-like structure
                ]
                
                for i, pattern in enumerate(patterns):
                    matches = re.findall(pattern, reasoning, re.DOTALL)
                    print(f"  Pattern {i+1}: {pattern}")
                    print(f"  Matches found: {len(matches)}")
                    for j, match in enumerate(matches):
                        print(f"    Match {j+1}: {match[:100]}...")
                        try:
                            parsed = json.loads(match)
                            print(f"    ✅ Valid JSON: {parsed}")
                        except:
                            print(f"    ❌ Invalid JSON")
        
        print(f"\n💰 Usage: {response.usage}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    debug_zai_raw_response()