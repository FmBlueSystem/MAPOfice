#!/usr/bin/env python3
"""Ultra-minimal test focusing on JSON extraction from GLM-4.5-Flash"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

try:
    from zai import ZaiClient
except ImportError:
    print("❌ zai-sdk not available")
    exit(1)

def test_ultra_minimal():
    """Test with the most minimal prompt possible"""
    
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        print("❌ ZAI_API_KEY not found")
        return
    
    client = ZaiClient(api_key=api_key)
    
    # Ultra-minimal system prompt
    system_prompt = """JSON ONLY. NO TEXT."""
    
    # Ultra-minimal user prompt
    user_prompt = """Destination - "Move On Up" | BPM 118 | Energy 0.75 | Date 1992

{"genre": "disco", "era": "1970s", "known_year": 1979, "is_reissue": true}"""
    
    print("🧪 TESTING ULTRA-MINIMAL GLM-4.5-FLASH PROMPT")
    print("=" * 50)
    print("System:", system_prompt)
    print("User:", user_prompt)
    print("-" * 50)
    
    try:
        response = client.chat.completions.create(
            model="glm-4.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=200
        )
        
        if response and response.choices:
            message = response.choices[0].message
            content = message.content or getattr(message, 'reasoning_content', '') or ""
            
            print("✅ Raw response received:")
            print(f"Length: {len(content)} chars")
            print(f"Content: {content}")
            print("-" * 50)
            
            # Try to parse as JSON
            try:
                # Find JSON in response
                start = content.find("{")
                end = content.rfind("}") + 1
                
                if start != -1 and end > start:
                    json_str = content[start:end]
                    print(f"Extracted JSON: {json_str}")
                    
                    result = json.loads(json_str)
                    print("✅ JSON parsing successful!")
                    print(json.dumps(result, indent=2))
                    
                    # Check specific fields
                    if result.get('genre') == 'disco':
                        print("✅ Genre: disco (correct!)")
                    if result.get('era') == '1970s':
                        print("✅ Era: 1970s (correct!)")
                    if result.get('known_year') == 1979:
                        print("✅ Known year: 1979 (correct!)")
                    if result.get('is_reissue'):
                        print("✅ Is reissue: true (correct!)")
                else:
                    print("❌ No JSON structure found")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
        else:
            print("❌ No response from API")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    test_ultra_minimal()