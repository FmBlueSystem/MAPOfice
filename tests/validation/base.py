"""
Base classes and utilities for validation testing
"""

import json
import time
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TestResult:
    """Standard test result structure"""
    test_name: str
    success: bool
    duration: float
    details: Dict[str, Any]
    error_message: Optional[str] = None
    
@dataclass 
class ValidationReport:
    """Consolidated validation report"""
    test_suite: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_duration: float
    results: list
    summary: Dict[str, Any]

class BaseValidationTest(ABC):
    """Base class for all validation tests"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.start_time = None
        self.end_time = None
        
    @abstractmethod
    def setup(self) -> bool:
        """Setup test environment. Return True if successful."""
        pass
        
    @abstractmethod
    def run_test(self) -> TestResult:
        """Run the actual test. Return TestResult."""
        pass
        
    def teardown(self):
        """Cleanup after test"""
        pass
        
    def execute(self) -> TestResult:
        """Execute complete test lifecycle"""
        self.start_time = time.time()
        
        try:
            # Setup
            if not self.setup():
                return TestResult(
                    test_name=self.name,
                    success=False,
                    duration=0,
                    details={},
                    error_message="Setup failed"
                )
            
            # Run test
            result = self.run_test()
            
            # Add timing
            self.end_time = time.time()
            if result:
                result.duration = self.end_time - self.start_time
                
            return result
            
        except Exception as e:
            self.end_time = time.time()
            return TestResult(
                test_name=self.name,
                success=False,
                duration=self.end_time - self.start_time if self.start_time else 0,
                details={},
                error_message=str(e)
            )
        finally:
            self.teardown()

class TestTrackData:
    """Standard test track data"""
    
    @staticmethod
    def get_stayin_alive() -> Dict[str, Any]:
        """Famous track for known-result testing"""
        return {
            'title': "Stayin' Alive",
            'artist': "Bee Gees",
            'bpm': 104,
            'key': "F minor", 
            'energy': 0.8,
            'date': "1992",  # Reissue date - original 1977
            'hamms_vector': [0.5, 0.7, 0.6, 0.8, 0.4, 0.9, 0.7, 0.5, 0.6, 0.8, 0.7, 0.4]
        }
    
    @staticmethod
    def get_move_on_up() -> Dict[str, Any]:
        """Complex track for reissue detection testing"""
        return {
            'title': 'Move On Up',
            'artist': 'Destination',
            'bpm': 118,
            'key': 'C',
            'energy': 0.75,
            'date': '1992-01-01',  # Star-Funk compilation - original 1979
            'hamms_vector': [0.8, 0.6, 0.7, 0.5, 0.9, 0.4, 0.6, 0.8, 0.7, 0.5, 0.6, 0.4]
        }
    
    @staticmethod
    def get_test_tracks() -> List[Dict[str, Any]]:
        """Collection of test tracks for comprehensive testing"""
        return [
            TestTrackData.get_stayin_alive(),
            TestTrackData.get_move_on_up(),
            {
                'title': 'Unknown Track',
                'artist': 'Unknown Artist',
                'bpm': 120,
                'key': 'C major',
                'energy': 0.6,
                'date': '2023',
                'hamms_vector': [0.5] * 12
            }
        ]

class APIKeyManager:
    """Centralized API key management for tests"""
    
    @staticmethod
    def get_anthropic_key() -> Optional[str]:
        return os.getenv('ANTHROPIC_API_KEY')
    
    @staticmethod 
    def get_zai_key() -> Optional[str]:
        return os.getenv('ZAI_API_KEY')
        
    @staticmethod
    def get_openai_key() -> Optional[str]:
        return os.getenv('OPENAI_API_KEY')
        
    @staticmethod
    def check_required_keys(providers: List[str]) -> Dict[str, bool]:
        """Check which API keys are available"""
        key_map = {
            'anthropic': APIKeyManager.get_anthropic_key(),
            'zai': APIKeyManager.get_zai_key(), 
            'openai': APIKeyManager.get_openai_key()
        }
        
        return {provider: key_map.get(provider) is not None 
                for provider in providers}

class JSONExtractor:
    """Robust JSON extraction for LLM responses"""
    
    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response with fallback strategies"""
        import re
        
        try:
            # Strategy 1: XML-style tags <json>...</json>
            match = re.search(r"<json>(.*?)</json>", text, flags=re.DOTALL)
            if match:
                candidate = match.group(1).strip()
                return json.loads(candidate)
            
            # Strategy 2: First { to last }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = text[start:end+1]
                return json.loads(candidate)
                
            # Strategy 3: Look for common JSON patterns
            json_patterns = [
                r'(\{[^{}]*"[^"]*"[^{}]*\})',
                r'(\{.*?"success".*?\})',
                r'(\{.*?"genre".*?\})'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, text, re.DOTALL)
                for match in matches:
                    try:
                        return json.loads(match)
                    except json.JSONDecodeError:
                        continue
                        
            raise ValueError("No valid JSON found in response")
            
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to extract valid JSON: {e}")