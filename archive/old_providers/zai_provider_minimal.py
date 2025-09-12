"""Optimized Z.ai Provider with minimal prompts for better GLM-4.5-Flash performance"""

from __future__ import annotations

import json
import time
import re
from typing import Dict, Any, Optional

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

from src.analysis.llm_provider import BaseLLMProvider, LLMConfig, LLMResponse, LLMProvider


class MinimalZaiProvider(BaseLLMProvider):
    """Optimized Z.ai provider with minimal prompts and smart fallbacks"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        
        if ZaiClient is None:
            raise ImportError(
                "zai-sdk package is required for Z.ai support. "
                "Install it with: pip install zai-sdk"
            )
        
        self.client = ZaiClient(api_key=config.api_key)
        self.pricing = {"input": 0.00, "output": 0.00}  # GLM-4.5-Flash is free
        
    def _extract_json_fast(self, text: str) -> Dict[str, Any]:
        """Fast JSON extraction optimized for short responses"""
        if not text or not text.strip():
            raise ValueError("Empty response")
        
        # Strategy 1: Direct JSON parsing (most common with minimal prompts)
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract from first { to last }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"No valid JSON in: {text[:100]}...")
    
    def _create_minimal_prompt(self, track_data: Dict[str, Any]) -> Dict[str, str]:
        """Create optimized minimal prompt with few-shot examples"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        energy = track_data.get('energy', 0.0)
        date = track_data.get('date', 'Unknown')
        
        # Strategy A: Few-shot with relevant examples (best for famous tracks)
        system_a = "Music expert. JSON only."
        user_a = f"""Examples:
Beatles - Hey Jude | 1968 → {{"genre":"rock","era":"1960s","original":1968}}
Curtis Mayfield - Move On Up | 1970 → {{"genre":"soul","era":"1970s","original":1970}}
Bee Gees - Stayin' Alive | 1977 → {{"genre":"disco","era":"1970s","original":1977}}

{artist} - {title} | {date} → """
        
        # Strategy B: Direct with example (fallback)
        system_b = "JSON format only."
        user_b = f"""{artist} - {title} | BPM: {bpm} | Energy: {energy:.1f} | Date: {date}

Example: {{"genre":"disco","era":"1970s","original":1979,"reissue":true}}

Analyze:"""
        
        return {
            "strategy_a": {"system": system_a, "user": user_a},
            "strategy_b": {"system": system_b, "user": user_b}
        }
    
    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        return 0.0  # Free model
    
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze track using minimal prompts with smart fallbacks"""
        start_time = time.time()
        
        try:
            self._wait_for_rate_limit()
            
            prompts = self._create_minimal_prompt(track_data)
            
            # Try Strategy A first (few-shot)
            result = self._try_strategy(prompts["strategy_a"], track_data, start_time, "few-shot")
            if result and result.success:
                return result
            
            # Fallback to Strategy B
            result = self._try_strategy(prompts["strategy_b"], track_data, start_time, "example")
            if result and result.success:
                return result
            
            # Ultimate fallback
            return self._create_fallback_response(track_data, start_time)
                
        except Exception as e:
            return self._create_error_response(str(e), track_data, start_time)
    
    def _try_strategy(self, prompt: Dict[str, str], track_data: Dict[str, Any], 
                     start_time: float, strategy_name: str) -> Optional[LLMResponse]:
        """Try a specific prompt strategy"""
        try:
            messages = [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]}
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=0.0,  # Maximum consistency
                max_tokens=150    # Short responses expected
            )
            
            if response and response.choices:
                message = response.choices[0].message
                content = message.content or getattr(message, 'reasoning_content', '') or ""
                
                if content:
                    try:
                        parsed_json = self._extract_json_fast(content)
                        normalized_json = self._normalize_response(parsed_json, track_data)
                        
                        processing_time = int((time.time() - start_time) * 1000)
                        
                        return LLMResponse(
                            success=True,
                            content=normalized_json,
                            raw_response=f"[{strategy_name}] {content}",
                            provider=LLMProvider.ZAI,
                            model=self.config.model,
                            processing_time_ms=processing_time,
                            tokens_used=self._estimate_tokens(prompt["user"] + content),
                            cost_estimate=0.0
                        )
                    except ValueError:
                        # JSON parsing failed, try next strategy
                        return None
                        
        except Exception:
            return None
        
        return None
    
    def _normalize_response(self, parsed_json: Dict[str, Any], track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize response to expected format with date verification"""
        metadata_date = track_data.get('date', 'Unknown')
        original_year = parsed_json.get('original') or parsed_json.get('known_year')
        
        # Determine if it's a reissue
        is_reissue = False
        if original_year and metadata_date:
            try:
                metadata_year = int(str(metadata_date)[:4])
                if original_year < metadata_year - 2:  # 2+ years difference suggests reissue
                    is_reissue = True
            except (ValueError, TypeError):
                pass
        
        return {
            "date_verification": {
                "artist_known": original_year is not None,
                "known_original_year": original_year,
                "metadata_year": metadata_date,
                "is_likely_reissue": is_reissue
            },
            "genre": parsed_json.get("genre", "unknown"),
            "subgenre": parsed_json.get("subgenre", parsed_json.get("genre", "unknown")),
            "era": self._determine_era(original_year, metadata_date),
            "mood": parsed_json.get("mood", "moderate"),
            "confidence": 0.85 if original_year else 0.6,
            "analysis_notes": f"Minimal prompt analysis ({'reissue detected' if is_reissue else 'standard analysis'})"
        }
    
    def _determine_era(self, original_year, metadata_date):
        """Determine era based on original year or metadata"""
        year_to_use = original_year
        
        if not year_to_use and metadata_date:
            try:
                year_to_use = int(str(metadata_date)[:4])
            except (ValueError, TypeError):
                return "unknown"
        
        if not year_to_use:
            return "unknown"
        
        decade = (year_to_use // 10) * 10
        return f"{decade}s"
    
    def _create_fallback_response(self, track_data: Dict[str, Any], start_time: float) -> LLMResponse:
        """Create fallback response when all strategies fail"""
        processing_time = int((time.time() - start_time) * 1000)
        
        # Basic analysis from audio features
        bpm = track_data.get('bpm', 120)
        energy = track_data.get('energy', 0.5)
        
        if bpm >= 110 and bpm <= 130 and energy > 0.6:
            genre = "disco"
        elif energy > 0.7:
            genre = "dance"
        else:
            genre = "pop"
        
        fallback_content = {
            "date_verification": {
                "artist_known": False,
                "known_original_year": None,
                "metadata_year": track_data.get('date', 'Unknown'),
                "is_likely_reissue": False
            },
            "genre": genre,
            "subgenre": f"{genre} fusion",
            "era": "unknown",
            "mood": "moderate",
            "confidence": 0.3,
            "analysis_notes": "Fallback analysis based on audio features"
        }
        
        return LLMResponse(
            success=True,
            content=fallback_content,
            raw_response="[fallback] Basic audio feature analysis",
            provider=LLMProvider.ZAI,
            model=self.config.model,
            processing_time_ms=processing_time,
            tokens_used=50,
            cost_estimate=0.0
        )
    
    def _create_error_response(self, error_msg: str, track_data: Dict[str, Any], start_time: float) -> LLMResponse:
        """Create error response"""
        processing_time = int((time.time() - start_time) * 1000)
        
        return LLMResponse(
            success=False,
            content={},
            raw_response="",
            provider=LLMProvider.ZAI,
            model=self.config.model,
            processing_time_ms=processing_time,
            error_message=f"Minimal Z.ai analysis failed: {error_msg}"
        )
    
    def test_connection(self) -> bool:
        """Test connection with minimal prompt"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "JSON only."},
                    {"role": "user", "content": 'Test → {"status":"ok"}'}
                ],
                max_tokens=20
            )
            return response is not None and len(response.choices) > 0
        except Exception:
            return False