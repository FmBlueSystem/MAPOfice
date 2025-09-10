"""Z.ai Provider Implementation for Multi-LLM Architecture"""

from __future__ import annotations

import json
import time
from typing import Dict, Any, Optional

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

from src.analysis.llm_provider import BaseLLMProvider, LLMConfig, LLMResponse, LLMProvider


class ZaiProvider(BaseLLMProvider):
    """Z.ai provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """Initialize Z.ai provider
        
        Args:
            config: Configuration for Z.ai API
            
        Raises:
            ImportError: If zai-sdk package is not installed
            ValueError: If configuration is invalid
        """
        super().__init__(config)
        
        if ZaiClient is None:
            raise ImportError(
                "zai-sdk package is required for Z.ai support. "
                "Install it with: pip install zai-sdk"
            )
        
        # Initialize Z.ai client
        self.client = ZaiClient(api_key=config.api_key)
        
        # Z.ai pricing per million tokens (estimated based on competitive pricing)
        self.pricing = self._get_model_pricing(config.model)
        
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing information for Z.ai models
        
        Args:
            model: Model name
            
        Returns:
            Dictionary with 'input' and 'output' pricing per million tokens
        """
        # Z.ai pricing - estimated based on market rates
        pricing_map = {
            "glm-4.5": {"input": 1.00, "output": 3.00},        # Flagship model
            "glm-4.5v": {"input": 1.20, "output": 3.60},       # Visual reasoning
            "glm-4-32b-0414-128k": {"input": 0.50, "output": 1.50},  # Cost-effective
            "default": {"input": 1.00, "output": 3.00}
        }
        
        return pricing_map.get(model, pricing_map["default"])
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count (rough approximation)
        """
        # Rough estimation: ~4 characters per token for most languages
        return len(text) // 4
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost of the API call (abstract method implementation)
        
        Args:
            prompt_tokens: Number of input tokens
            response_tokens: Number of output tokens
            
        Returns:
            Cost estimate in USD
        """
        input_cost = (prompt_tokens / 1_000_000) * self.pricing["input"]
        output_cost = (response_tokens / 1_000_000) * self.pricing["output"]
        return input_cost + output_cost
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost estimate for API call (convenience method)
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost estimate in USD
        """
        return self._estimate_cost(input_tokens, output_tokens)
    
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze track using Z.ai API
        
        Args:
            track_data: Dictionary containing track information
            
        Returns:
            LLMResponse with analysis results
        """
        start_time = time.time()
        
        try:
            # Wait for rate limiting
            self._wait_for_rate_limit()
            
            # Create the prompt
            prompt = self._create_music_analysis_prompt(track_data)
            
            # Prepare messages for Z.ai
            messages = [
                {
                    "role": "system", 
                    "content": "You are an expert music analyst. Analyze music tracks and provide detailed genre, mood, and era classification. Always respond with valid JSON."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # Make API call to Z.ai
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            # Extract response content
            if response and response.choices and len(response.choices) > 0:
                content_text = response.choices[0].message.content
                raw_response = content_text
                
                # Parse JSON response
                try:
                    content_json = json.loads(content_text)
                except json.JSONDecodeError as e:
                    return LLMResponse(
                        success=False,
                        content={},
                        raw_response=content_text,
                        provider=LLMProvider.ZAI,
                        model=self.config.model,
                        processing_time_ms=int((time.time() - start_time) * 1000),
                        error_message=f"Failed to parse JSON response: {e}"
                    )
                
                # Calculate cost estimate
                input_tokens = self._estimate_tokens(prompt)
                output_tokens = self._estimate_tokens(content_text)
                cost_estimate = self._calculate_cost(input_tokens, output_tokens)
                
                processing_time = int((time.time() - start_time) * 1000)
                
                return LLMResponse(
                    success=True,
                    content=content_json,
                    raw_response=raw_response,
                    provider=LLMProvider.ZAI,
                    model=self.config.model,
                    processing_time_ms=processing_time,
                    tokens_used=input_tokens + output_tokens,
                    cost_estimate=cost_estimate
                )
            else:
                return LLMResponse(
                    success=False,
                    content={},
                    raw_response="",
                    provider=LLMProvider.ZAI,
                    model=self.config.model,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    error_message="Empty response from Z.ai API"
                )
                
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=False,
                content={},
                raw_response="",
                provider=LLMProvider.ZAI,
                model=self.config.model,
                processing_time_ms=processing_time,
                error_message=f"Z.ai API error: {str(e)}"
            )
    
    def get_cost_estimates(self) -> Dict[str, float]:
        """Get cost estimates for this provider
        
        Returns:
            Dictionary with cost per million tokens
        """
        return {
            "input_cost_per_1M": self.pricing["input"],
            "output_cost_per_1M": self.pricing["output"]
        }
    
    def test_connection(self) -> bool:
        """Test connection to Z.ai API
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test request
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, respond with just 'OK'"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=10
            )
            
            return response is not None and len(response.choices) > 0
        except Exception as e:
            print(f"Z.ai connection test failed: {e}")
            return False