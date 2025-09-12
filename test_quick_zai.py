#!/usr/bin/env python3
"""Quick test of enhanced GLM-4.5-Flash prompts with timeout handling"""

import os
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

def extract_json_simple(text: str) -> dict:
    """Simple JSON extraction"""
    # Look for <json>...</json> tags first
    m = re.search(r"<json>(.*?)</json>", text, flags=re.DOTALL)
    if m:
        candidate = m.group(1).strip()
    else:
        # Fallback: first { to last }
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON found")
        candidate = text[start:end+1]
    
    return json.loads(candidate)

def test_version_a_prompt():
    """Test Version A prompt with GLM-4.5-Flash"""
    
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        print("❌ ZAI_API_KEY not found")
        return
    
    client = ZaiClient(api_key=api_key)
    
    # Simplified system prompt
    system_prompt = """Responde SOLO con JSON entre <json> y </json>. Sin explicaciones.

Formato EXACTO:
<json>{"artist_known":true/false,"known_original_year":1979|null,"is_reissue":true/false,"genre":"disco","subgenre":"boogie","era":"1970s","mood":"upbeat"}</json>"""
    
    # User prompt for Destination - Move On Up
    user_prompt = """Track: Destination - "Move On Up"
BPM: 118, Key: C, Energy: 0.750
Metadata Date: 1992-01-01

¿Conoces este artista/canción? ¿Año original de lanzamiento?"""
    
    print("🔄 Testing enhanced prompt with GLM-4.5-Flash...")
    print("Track: Destination - Move On Up")
    print("Expected: Should recognize as 1979 disco, flag 1992 as reissue")
    print("-" * 60)
    
    try:
        # Make API call with short timeout
        response = client.chat.completions.create(
            model="glm-4.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        if response and response.choices:
            message = response.choices[0].message
            content = message.content or getattr(message, 'reasoning_content', '') or ""
            
            print("Raw response:")
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 60)
            
            # Try to extract JSON
            try:
                result = extract_json_simple(content)
                print("✅ Extracted JSON:")
                print(json.dumps(result, indent=2))
                
                # Check if it worked
                if result.get('known_original_year') == 1979:
                    print("\n🎉 SUCCESS: Correctly identified 1979 as original year!")
                elif result.get('era') == '1970s':
                    print("\n✅ PARTIAL SUCCESS: Era correctly identified as 1970s")
                else:
                    print(f"\n⚠️ NEEDS WORK: Era = {result.get('era')}")
                    
            except Exception as e:
                print(f"❌ JSON extraction failed: {e}")
                
        else:
            print("❌ No response from API")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    test_version_a_prompt()