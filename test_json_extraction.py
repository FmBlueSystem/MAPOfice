#!/usr/bin/env python3
"""Test the robust JSON extraction improvements"""

import json
import re
from typing import Dict, Any

def _extract_json_robust(text: str) -> Dict[str, Any]:
    """Enhanced JSON extraction with multiple fallback strategies"""
    if not text or not text.strip():
        raise ValueError("Empty text provided")
    
    # Strategy 1: Clean markdown code blocks (existing logic)
    clean_text = text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    
    # Strategy 2: Try direct JSON parsing first
    try:
        return json.loads(clean_text.strip())
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Look for <json>...</json> tags (for enhanced prompts)
    m = re.search(r"<json>(.*?)</json>", text, flags=re.DOTALL)
    if m:
        try:
            candidate = m.group(1).strip()
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    
    # Strategy 4: Extract from first { to last } (original fallback)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            candidate = text[start:end+1]
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    
    # Strategy 5: Try to find any JSON-like structure with regex
    json_patterns = [
        r'\{[^{}]*\}',  # Simple single-level JSON
        r'\{(?:[^{}]|{[^{}]*})*\}',  # Nested JSON structures
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # If all strategies fail, raise error
    raise ValueError(f"No valid JSON found in text: {text[:200]}...")

def test_problematic_cases():
    """Test cases based on actual errors from the logs"""
    
    test_cases = [
        # Case 1: Unterminated string
        ('Unterminated string case', '''
        I'll analyze this track based on the information provided.
        
        {
          "genre": "electronic",
          "subgenre": "house
          "era": "2000s",
          "mood": "energetic"
        }
        '''),
        
        # Case 2: Empty response (line 1 column 1 char 0)
        ('Empty response case', ''),
        
        # Case 3: JSON with explanation
        ('JSON with explanation', '''
        Based on the track information provided, here's my analysis:
        
        The track appears to be from the electronic dance music genre.
        
        <json>
        {
          "genre": "electronic",
          "subgenre": "house",
          "era": "2000s", 
          "mood": "energetic"
        }
        </json>
        
        This classification is based on the BPM and energy levels.
        '''),
        
        # Case 4: Multiple JSON blocks
        ('Multiple JSON blocks', '''
        Here are some options:
        
        {"genre": "rock", "era": "1980s"}
        
        But actually, this seems more like:
        
        {"genre": "electronic", "subgenre": "synthpop", "era": "1980s", "mood": "upbeat"}
        '''),
        
        # Case 5: Markdown code block
        ('Markdown code block', '''
        Here's the analysis:
        
        ```json
        {
          "genre": "disco",
          "subgenre": "boogie",
          "era": "1970s",
          "mood": "upbeat"
        }
        ```
        '''),
    ]
    
    print("🧪 Testing Robust JSON Extraction")
    print("=" * 50)
    
    success_count = 0
    total_count = len(test_cases)
    
    for name, test_input in test_cases:
        print(f"\n🔬 Test: {name}")
        print(f"Input: {test_input[:100].strip()}...")
        
        try:
            result = _extract_json_robust(test_input)
            print(f"✅ SUCCESS: {json.dumps(result, indent=2)}")
            success_count += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print(f"\n📊 RESULTS: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 All tests passed! The robust JSON extraction should handle most GLM-4.5-Flash issues.")
    elif success_count > total_count * 0.8:
        print("✅ Most tests passed! Significant improvement expected.")
    else:
        print("⚠️ Some tests failed. Additional refinement may be needed.")

if __name__ == "__main__":
    test_problematic_cases()