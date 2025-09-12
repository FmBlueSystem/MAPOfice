"""Anthropic Claude Provider for Music Analysis"""

from __future__ import annotations

import json
import time
from typing import Dict, Any

try:
    import anthropic
except ImportError:
    anthropic = None

from src.analysis.llm_provider import BaseLLMProvider, LLMConfig, LLMResponse, LLMProvider


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider for music analysis"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        
        if anthropic is None:
            raise ImportError(
                "anthropic package is required for Claude support. "
                "Install it with: pip install anthropic"
            )
        
        self.client = anthropic.Anthropic(api_key=config.api_key)
        
        # Claude pricing (as of 2024) - compatible with MultiLLM format
        pricing_by_model = {
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075}
        }
        
        # Set pricing for current model (MultiLLM compatibility)
        self.pricing = pricing_by_model.get(config.model, pricing_by_model["claude-3-haiku-20240307"])
        
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from Claude's response"""
        if not text or not text.strip():
            raise ValueError("Empty response from Claude")
        
        text = text.strip()
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Find JSON block within ```json```
        import re
        json_match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Extract from first { to last }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"No valid JSON found in Claude response: {text[:200]}...")
    
    def _create_optimized_prompt(self, track_data: Dict[str, Any]) -> str:
        """Create an optimized prompt for Claude Haiku with comprehensive genre guidelines"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        energy = track_data.get('energy', 0.0)
        date = track_data.get('date', 'Unknown')
        
        return f"""Analyze this music track and return ONLY a JSON response:

Track: {artist} - {title}
BPM: {bpm}
Energy: {energy:.2f}
Date: {date}

CRITICAL: Determine the original release year if you know this artist/track, then classify accurately.

Required JSON format:
{{
    "date_verification": {{
        "artist_known": true/false,
        "known_original_year": 1979 or null,
        "metadata_year": "{date}",
        "is_likely_reissue": true/false
    }},
    "genre": "specific primary genre",
    "subgenre": "more specific classification",
    "era": "decade based on ORIGINAL year (1960s, 1970s, etc)",
    "mood": "emotional atmosphere",
    "confidence": 0.85,
    "analysis_notes": "brief explanation"
}}

**Genre Classification Guidelines:**

**Primary Genres to Consider:**
- **Rock**: Classic Rock, Hard Rock, Progressive Rock, Alternative Rock
- **Pop**: Pop Rock, Synthpop, Adult Contemporary
- **Electronic**: House, Techno, Ambient, IDM, Downtempo
- **Hip-Hop**: East Coast, West Coast, Conscious Rap, Trap
- **R&B/Soul**: Classic Soul, Contemporary R&B, Neo-Soul, Motown
- **Disco**: Only for 1970s dance music with characteristic 4/4 beat
- **New Wave**: Post-punk influenced 1980s alternative with synthesizers
- **Punk**: Fast, aggressive, raw sound (1970s-1980s)
- **Jazz**: Traditional, Fusion, Contemporary, Smooth Jazz
- **Folk**: Traditional, Contemporary, Singer-Songwriter
- **Country**: Traditional, Contemporary, Country Rock
- **Metal**: Heavy Metal, Death Metal, Black Metal, Progressive Metal
- **Reggae**: Traditional, Dancehall, Ska
- **Blues**: Traditional, Electric, Delta, Chicago
- **Classical**: Baroque, Romantic, Contemporary Classical

**BPM Guidelines:**
- 60-80: Ballads, Ambient, some Hip-Hop
- 80-100: Soul, R&B, some Pop, Blues
- 100-120: Rock, Pop Rock, some Dance
- 120-130: House, Disco, Pop Dance, Techno
- 130-140: Trance, Hard Rock, some Metal
- 140+: Punk, Drum & Bass, Speed Metal, Hardcore

**Energy Level Guidelines:**
- 0.0-0.2: Ambient, Meditation, Slow Ballads
- 0.2-0.4: Jazz, Classical, Folk, Acoustic
- 0.4-0.6: Pop, Soul, Country, Soft Rock
- 0.6-0.8: Rock, Dance, Hip-Hop, R&B
- 0.8-1.0: Metal, Punk, Hard Dance, Aggressive Electronic

**Era-Based Genre Evolution:**
- 1960s: Rock, Folk, Motown, Psychedelic
- 1970s: Disco, Punk, Progressive Rock, Funk
- 1980s: New Wave, Synthpop, Hair Metal, Hip-Hop emergence
- 1990s: Grunge, Alternative, House, Gangsta Rap
- 2000s: Nu-Metal, Contemporary R&B, Trance
- 2010s+: EDM, Trap, Indie Electronic

**DO NOT default to Disco unless:**
- BPM 110-130 AND high energy AND 1970s era AND characteristic disco instrumentation

Return only the JSON, no other text."""
    
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze track using Claude"""
        start_time = time.time()
        
        try:
            self._wait_for_rate_limit()
            
            prompt = self._create_optimized_prompt(track_data)
            
            # Use Claude with optimized settings
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract response content
            response_text = ""
            if message.content:
                for content_block in message.content:
                    if hasattr(content_block, 'text'):
                        response_text += content_block.text
            
            if not response_text:
                raise ValueError("Empty response from Claude")
            
            # Parse JSON response
            parsed_json = self._extract_json_from_response(response_text)
            
            # Calculate processing time and tokens
            processing_time = int((time.time() - start_time) * 1000)
            input_tokens = message.usage.input_tokens if hasattr(message, 'usage') else self._estimate_tokens(prompt)
            output_tokens = message.usage.output_tokens if hasattr(message, 'usage') else self._estimate_tokens(response_text)
            
            return LLMResponse(
                success=True,
                content=parsed_json,
                raw_response=response_text,
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                processing_time_ms=processing_time,
                tokens_used=input_tokens + output_tokens,
                cost_estimate=self._estimate_cost(input_tokens, output_tokens)
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=False,
                content={},
                raw_response="",
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                processing_time_ms=processing_time,
                error_message=f"Claude analysis failed: {str(e)}"
            )
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (Claude uses ~4 chars per token)"""
        return len(text) // 4
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost based on Claude pricing"""
        model_pricing = self.pricing.get(self.config.model, {
            "input": 0.00025,  # Default to Haiku pricing
            "output": 0.00125
        })
        
        input_cost = (prompt_tokens / 1000) * model_pricing["input"]
        output_cost = (response_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost