#!/usr/bin/env python3
"""Test Z.ai with ultra-simple prompts"""

import os
try:
    from zai import ZaiClient
except ImportError:
    print("❌ zai-sdk not available")
    exit(1)

def test_simple_prompt():
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        print("❌ No API key")
        return
    
    client = ZaiClient(api_key=api_key)
    
    # Ultra simple test
    try:
        response = client.chat.completions.create(
            model="glm-4.5-flash",
            messages=[
                {"role": "system", "content": "You are a music expert. Always respond in JSON format."},
                {"role": "user", "content": 'Beatles - Hey Jude from 1968. Respond: {"genre": "rock", "era": "1960s"}'}
            ],
            temperature=0.0,
            max_tokens=100
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"✅ Response: {content}")
            
            # Try to parse JSON
            import json
            try:
                parsed = json.loads(content)
                print(f"✅ Valid JSON: {parsed}")
            except:
                print(f"❌ Invalid JSON in response")
        else:
            print("❌ No response")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_prompt()