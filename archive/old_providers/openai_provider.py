"""OpenAI Provider Implementation for Multi-LLM Architecture"""

from __future__ import annotations

import json
import time
from typing import Dict, Any, Optional

import openai
from openai import OpenAI

from src.analysis.llm_provider import BaseLLMProvider, LLMConfig, LLMResponse, LLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """Initialize OpenAI provider
        
        Args:
            config: Configuration for OpenAI API
            
        Raises:
            ValueError: If API key format is invalid
        """
        super().__init__(config)
        
        # Additional validation for OpenAI keys
        if not config.api_key.startswith('sk-'):
            raise ValueError("OpenAI API key must start with 'sk-'")
            
        self.client = OpenAI(api_key=config.api_key)
        
        # OpenAI pricing per million tokens (as of 2025)
        self.pricing = self._get_model_pricing(config.model)
        
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing information for OpenAI models
        
        Args:
            model: Model name
            
        Returns:
            Dictionary with input_cost and output_cost per million tokens
        """
        pricing_map = {
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0}, 
            "gpt-4o": {"input": 2.5, "output": 10.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        }
        
        return pricing_map.get(model, {"input": 10.0, "output": 30.0})  # Default pricing
        
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze track using OpenAI
        
        Args:
            track_data: Track metadata and HAMMS vector
            
        Returns:
            Standardized LLM response
        """
        start_time = time.time()
        
        try:
            # Rate limiting
            self._wait_for_rate_limit()
            
            # Create prompt
            prompt = self._create_music_analysis_prompt(track_data)
            
            # Make API call with retries
            response = None
            last_error = None
            
            for attempt in range(self.config.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert music analyst specializing in genre classification, mood analysis, and musical era identification. Always respond with valid JSON."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        timeout=self.config.timeout
                    )
                    break  # Success, exit retry loop
                    
                except openai.RateLimitError as e:
                    last_error = f"Rate limit exceeded: {str(e)}"
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                    
                except openai.APITimeoutError as e:
                    last_error = f"Request timeout: {str(e)}"
                    continue
                    
                except Exception as e:
                    last_error = f"API error: {str(e)}"
                    if attempt == self.config.max_retries - 1:
                        break
                    continue
            
            if response is None:
                processing_time_ms = int((time.time() - start_time) * 1000)
                return LLMResponse(
                    success=False,
                    content={},
                    raw_response="",
                    provider=LLMProvider.OPENAI,
                    model=self.config.model,
                    processing_time_ms=processing_time_ms,
                    error_message=last_error
                )
            
            # Extract response content
            raw_content = response.choices[0].message.content.strip()
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Parse JSON response
            try:
                # Clean the response - remove markdown code blocks if present
                if raw_content.startswith("```json"):
                    raw_content = raw_content[7:]
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3]
                    
                content = json.loads(raw_content.strip())
                
                # Validate required fields
                required_fields = ["genre", "subgenre", "mood", "confidence"]
                for field in required_fields:
                    if field not in content:
                        content[field] = "Unknown" if field != "confidence" else 0.5
                        
            except json.JSONDecodeError as e:
                return LLMResponse(
                    success=False,
                    content={},
                    raw_response=raw_content,
                    provider=LLMProvider.OPENAI,
                    model=self.config.model,
                    processing_time_ms=processing_time_ms,
                    error_message=f"Failed to parse JSON response: {str(e)}"
                )
            
            # Calculate cost and tokens
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
            cost_estimate = self._estimate_cost(
                response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                response.usage.completion_tokens if hasattr(response, 'usage') else 0
            )
            
            return LLMResponse(
                success=True,
                content=content,
                raw_response=raw_content,
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                processing_time_ms=processing_time_ms,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=False,
                content={},
                raw_response="",
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                processing_time_ms=processing_time_ms,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate cost based on token usage
        
        Args:
            prompt_tokens: Number of input tokens
            response_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        input_cost = (prompt_tokens / 1_000_000) * self.pricing["input"]
        output_cost = (response_tokens / 1_000_000) * self.pricing["output"]
        return input_cost + output_cost