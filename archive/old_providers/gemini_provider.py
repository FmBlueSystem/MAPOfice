"""Google Gemini Provider Implementation for Multi-LLM Architecture"""

from __future__ import annotations

import json
import time
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from src.analysis.llm_provider import BaseLLMProvider, LLMConfig, LLMResponse, LLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """Initialize Gemini provider
        
        Args:
            config: Configuration for Gemini API
            
        Raises:
            ImportError: If google-generativeai package is not installed
            ValueError: If configuration is invalid
        """
        super().__init__(config)
        
        if genai is None:
            raise ImportError(
                "google-generativeai package is required for Gemini support. "
                "Install it with: pip install google-generativeai"
            )
        
        # Configure Gemini API
        genai.configure(api_key=config.api_key)
        
        # Initialize the model
        generation_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
            "response_mime_type": "application/json",
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        self.model = genai.GenerativeModel(
            model_name=config.model,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Gemini pricing per million tokens (as of 2025)
        self.pricing = self._get_model_pricing(config.model)
        
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing information for Gemini models
        
        Args:
            model: Model name
            
        Returns:
            Dictionary with input_cost and output_cost per million tokens
        """
        pricing_map = {
            "gemini-1.5-pro": {"input": 2.5, "output": 10.0},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-pro": {"input": 0.5, "output": 1.5},
        }
        
        return pricing_map.get(model, {"input": 2.5, "output": 10.0})  # Default pricing
        
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze track using Google Gemini
        
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
                    response = self.model.generate_content(
                        prompt,
                        request_options={"timeout": self.config.timeout}
                    )
                    
                    # Check if response was blocked
                    if response.candidates and response.candidates[0].finish_reason == "SAFETY":
                        last_error = "Response blocked due to safety filters"
                        continue
                        
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    last_error = f"API error: {str(e)}"
                    if "quota" in str(e).lower() or "rate" in str(e).lower():
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    
                    if attempt == self.config.max_retries - 1:
                        break
                    continue
            
            if response is None or not response.text:
                processing_time_ms = int((time.time() - start_time) * 1000)
                return LLMResponse(
                    success=False,
                    content={},
                    raw_response="",
                    provider=LLMProvider.GEMINI,
                    model=self.config.model,
                    processing_time_ms=processing_time_ms,
                    error_message=last_error or "No response generated"
                )
            
            # Extract response content
            raw_content = response.text.strip()
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
                    provider=LLMProvider.GEMINI,
                    model=self.config.model,
                    processing_time_ms=processing_time_ms,
                    error_message=f"Failed to parse JSON response: {str(e)}"
                )
            
            # Estimate tokens and cost (Gemini doesn't provide exact token counts)
            estimated_prompt_tokens = len(prompt.split()) * 1.3  # Rough estimate
            estimated_response_tokens = len(raw_content.split()) * 1.3  # Rough estimate
            
            cost_estimate = self._estimate_cost(
                int(estimated_prompt_tokens),
                int(estimated_response_tokens)
            )
            
            return LLMResponse(
                success=True,
                content=content,
                raw_response=raw_content,
                provider=LLMProvider.GEMINI,
                model=self.config.model,
                processing_time_ms=processing_time_ms,
                tokens_used=int(estimated_prompt_tokens + estimated_response_tokens),
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=False,
                content={},
                raw_response="",
                provider=LLMProvider.GEMINI,
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