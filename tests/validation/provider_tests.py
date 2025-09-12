"""
Provider Validation Tests
=========================

Consolidates all provider-specific tests from tools/validation/
- test_claude_provider.py
- test_enhanced_zai.py  
- test_multi_llm_integration.py
- test_zai_connection.py
- test_simple_zai.py
- test_quick_zai.py

Tests provider functionality, compatibility, and performance.
"""

import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tests.validation.base import BaseValidationTest, TestResult, TestTrackData, APIKeyManager, JSONExtractor
from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

@dataclass
class ProviderTestConfig:
    """Configuration for provider testing"""
    provider: str
    model: str
    api_key: str
    max_tokens: int = 1000
    temperature: float = 0.1

class ClaudeProviderTest(BaseValidationTest):
    """Test Claude (Anthropic) provider functionality"""
    
    def __init__(self):
        super().__init__(
            "Claude Provider Test",
            "Test Claude Haiku model for music analysis accuracy and reliability"
        )
        self.config = None
        self.provider = None
        
    def setup(self) -> bool:
        """Setup Claude provider"""
        api_key = APIKeyManager.get_anthropic_key()
        if not api_key:
            return False
            
        try:
            self.config = LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                api_key=api_key,
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.1
            )
            
            self.provider = LLMProviderFactory.create_provider(self.config)
            return True
            
        except Exception:
            return False
            
    def run_test(self) -> TestResult:
        """Run Claude provider test"""
        try:
            test_track = TestTrackData.get_stayin_alive()
            result = self.provider.analyze_track(test_track)
            
            if not result.success:
                return TestResult(
                    test_name=self.name,
                    success=False,
                    duration=0,
                    details={},
                    error_message=result.error_message
                )
            
            # Validate response quality
            confidence = result.content.get('confidence', 0)
            original_year = result.content.get('date_verification', {}).get('known_original_year')
            genre = result.content.get('genre', '')
            
            quality_score = 0
            if confidence > 0.8:
                quality_score += 40
            elif confidence > 0.6:
                quality_score += 20
                
            if original_year and original_year == 1977:
                quality_score += 30
                
            if genre.lower() in ['disco', 'pop', 'dance']:
                quality_score += 30
                
            details = {
                'confidence': confidence,
                'original_year': original_year,
                'genre': genre,
                'quality_score': quality_score,
                'processing_time_ms': result.processing_time_ms,
                'cost_estimate': result.cost_estimate,
                'tokens_used': result.tokens_used
            }
            
            return TestResult(
                test_name=self.name,
                success=quality_score >= 60,  # Require good quality
                duration=0,  # Will be set by base class
                details=details
            )
            
        except Exception as e:
            return TestResult(
                test_name=self.name,
                success=False,
                duration=0,
                details={},
                error_message=str(e)
            )

class ZaiProviderTest(BaseValidationTest):
    """Test Zai (Chinese GLM) provider with fallback orchestration"""
    
    def __init__(self):
        super().__init__(
            "Zai Provider Test", 
            "Test GLM-4.5-Flash with A→B fallback system for reliability"
        )
        self.client = None
        self.api_key = None
        
    def setup(self) -> bool:
        """Setup Zai provider"""
        self.api_key = APIKeyManager.get_zai_key()
        if not self.api_key or not ZaiClient:
            return False
            
        try:
            self.client = ZaiClient(api_key=self.api_key)
            return True
        except Exception:
            return False
            
    def run_test(self) -> TestResult:
        """Run Zai provider test with fallback"""
        try:
            test_track = TestTrackData.get_move_on_up()
            
            # Try enhanced system with fallback
            result = self._analyze_track_with_fallback(test_track)
            
            if 'error' in result:
                return TestResult(
                    test_name=self.name,
                    success=False,
                    duration=0,
                    details={},
                    error_message=result['error']
                )
            
            # Validate response
            success = False
            quality_details = {}
            
            if 'date_verification' in result:
                verification = result['date_verification']
                known_year = verification.get('known_original_year')
                is_reissue = verification.get('is_likely_reissue', False)
                era = result.get('era', '')
                
                # Check for correct identification
                if (known_year == 1979 and is_reissue) or era == '1970s':
                    success = True
                    
                quality_details = {
                    'artist_known': verification.get('artist_known', False),
                    'known_original_year': known_year,
                    'is_likely_reissue': is_reissue,
                    'era': era,
                    'genre': result.get('genre', ''),
                    'mood': result.get('mood', '')
                }
            
            return TestResult(
                test_name=self.name,
                success=success,
                duration=0,
                details=quality_details
            )
            
        except Exception as e:
            return TestResult(
                test_name=self.name,
                success=False,
                duration=0,
                details={},
                error_message=str(e)
            )
    
    def _analyze_track_with_fallback(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement A→B fallback orchestration"""
        
        # Try Version A (detailed with XML tags)
        try:
            result = self._try_version_a(track_data)
            if result:
                return result
        except Exception:
            pass
            
        # Fallback to Version B (ultra-minimal)
        try:
            result = self._try_version_b(track_data)
            return result
        except Exception as e:
            return {"error": f"Both versions failed: {e}"}
    
    def _try_version_a(self, track_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try Version A (detailed prompt with XML tags)"""
        system_prompt = """Eres un validador musical. PIENSA en silencio y NO muestres tu razonamiento.
Responde con JSON VÁLIDO y NADA MÁS.
NO incluyas explicaciones, saludos, listas, Markdown, ni fences (```).

Salidas permitidas:
1) UNA ÚNICA línea JSON entre las etiquetas <json> y </json>.
2) Booleans en minúscula (true/false). Usa null cuando no sepas.

Formato EXACTO:
<json>{"date_verification":{"artist_known":true/false,"known_original_year":1234|null,"metadata_year":"YYYY"|"YYYY-MM-DD"|null,"is_likely_reissue":true/false},"genre":"...","subgenre":"...","era":"1950s|1960s|1970s|1980s|1990s|2000s|2010s|2020s","mood":"..."}</json>"""
        
        user_prompt = f"""Track: {track_data['artist']} - "{track_data['title']}"
BPM: {track_data['bpm']}, Key: {track_data['key']}, Energy: {track_data['energy']:.3f}
Metadata Date: {track_data['date']}

RESPONDE SOLO con el bloque <json>...</json> descrito."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model="glm-4.5-flash",
            messages=messages,
            temperature=0.1,
            max_tokens=800
        )
        
        if response and response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            content_text = message.content or ""
            
            # Handle GLM-4.5-Flash reasoning_content
            if not content_text and hasattr(message, 'reasoning_content'):
                content_text = message.reasoning_content or ""
            
            # Try to extract JSON
            return JSONExtractor.extract_json(content_text)
        
        return None
    
    def _try_version_b(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Try Version B (ultra-minimal fallback)"""
        system_prompt = """DEVUELVE SOLO JSON (una línea), SIN NADA MÁS.

Reglas:
- Booleans en minúscula.
- Usa null si no sabes.
- No texto adicional, no Markdown, no comentarios."""
        
        user_prompt = f"""{track_data['artist']} - "{track_data['title']}" | BPM {track_data['bpm']} | Key {track_data['key']} | Energy {track_data['energy']:.3f} | Metadata {track_data['date']}

{{"artist_known":true/false,"known_year":1234|null,"is_reissue":true/false,"genre":"...","subgenre":"...","era":"1950s|1960s|1970s|1980s|1990s|2000s|2010s|2020s","mood":"..."}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model="glm-4.5-flash",
            messages=messages,
            temperature=0.0,
            max_tokens=500
        )
        
        if response and response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            content_text = message.content or ""
            
            if not content_text and hasattr(message, 'reasoning_content'):
                content_text = message.reasoning_content or ""
                
            # Extract and normalize JSON
            simple_json = JSONExtractor.extract_json(content_text)
            return self._normalize_version_b_response(simple_json, track_data)
        
        raise Exception("No response from Version B")
    
    def _normalize_version_b_response(self, simple_json: Dict[str, Any], track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Version B simplified response to full format"""
        metadata_date = track_data.get('date', 'Unknown')
        
        # Handle both Version A and Version B formats
        if 'date_verification' in simple_json:
            return simple_json
        
        # Convert Version B to Version A format
        return {
            "date_verification": {
                "artist_known": simple_json.get("artist_known", False),
                "known_original_year": simple_json.get("known_year"),
                "metadata_year": metadata_date,
                "is_likely_reissue": simple_json.get("is_reissue", False)
            },
            "genre": simple_json.get("genre", "unknown"),
            "subgenre": simple_json.get("subgenre", "unknown"), 
            "era": simple_json.get("era", "unknown"),
            "mood": simple_json.get("mood", "unknown")
        }

class MultiProviderIntegrationTest(BaseValidationTest):
    """Test multi-provider integration and comparison"""
    
    def __init__(self):
        super().__init__(
            "Multi-Provider Integration Test",
            "Test integration and comparison between different LLM providers"
        )
        self.available_providers = {}
        
    def setup(self) -> bool:
        """Setup multiple providers"""
        available_keys = APIKeyManager.check_required_keys(['anthropic', 'zai'])
        
        if available_keys['anthropic']:
            try:
                config = LLMConfig(
                    provider=LLMProvider.ANTHROPIC,
                    api_key=APIKeyManager.get_anthropic_key(),
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    temperature=0.1
                )
                self.available_providers['claude'] = LLMProviderFactory.create_provider(config)
            except Exception:
                pass
                
        if available_keys['zai'] and ZaiClient:
            try:
                self.available_providers['zai'] = ZaiClient(api_key=APIKeyManager.get_zai_key())
            except Exception:
                pass
                
        return len(self.available_providers) >= 1
        
    def run_test(self) -> TestResult:
        """Run multi-provider comparison test"""
        try:
            test_track = TestTrackData.get_stayin_alive()
            results = {}
            
            # Test each available provider
            for provider_name, provider in self.available_providers.items():
                try:
                    if provider_name == 'claude':
                        result = provider.analyze_track(test_track)
                        if result.success:
                            results[provider_name] = {
                                'confidence': result.content.get('confidence', 0),
                                'genre': result.content.get('genre', ''),
                                'processing_time': result.processing_time_ms,
                                'cost': result.cost_estimate
                            }
                    elif provider_name == 'zai':
                        # Use simplified Zai test
                        zai_test = ZaiProviderTest()
                        zai_test.client = provider
                        zai_result = zai_test._analyze_track_with_fallback(test_track)
                        if 'error' not in zai_result:
                            results[provider_name] = {
                                'confidence': 0.7,  # Estimated
                                'genre': zai_result.get('genre', ''),
                                'processing_time': 2000,  # Estimated
                                'cost': 0.0  # Free
                            }
                except Exception:
                    continue
            
            success = len(results) > 0
            
            return TestResult(
                test_name=self.name,
                success=success,
                duration=0,
                details={
                    'providers_tested': list(results.keys()),
                    'provider_results': results,
                    'comparison': self._compare_providers(results)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name=self.name,
                success=False,
                duration=0,
                details={},
                error_message=str(e)
            )
    
    def _compare_providers(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Compare provider performance"""
        if len(results) < 2:
            return {"message": "Need at least 2 providers for comparison"}
            
        comparison = {}
        
        # Find fastest provider
        if 'claude' in results and 'zai' in results:
            claude_time = results['claude']['processing_time']
            zai_time = results['zai']['processing_time'] 
            
            comparison['speed_winner'] = 'claude' if claude_time < zai_time else 'zai'
            comparison['cost_winner'] = 'zai'  # Always free
            
            # Quality comparison (simplified)
            claude_conf = results['claude']['confidence']
            comparison['quality_winner'] = 'claude' if claude_conf > 0.7 else 'tie'
            
        return comparison

# Test Suite Orchestrator
class ProviderTestSuite:
    """Orchestrates all provider tests"""
    
    def __init__(self):
        self.tests = [
            ClaudeProviderTest(),
            ZaiProviderTest(), 
            MultiProviderIntegrationTest()
        ]
        
    def run_all_tests(self):
        """Run all provider tests"""
        results = []
        
        print("🚀 Running Provider Test Suite")
        print("=" * 50)
        
        for test in self.tests:
            print(f"\n🔄 Running {test.name}...")
            
            result = test.execute()
            results.append(result)
            
            if result.success:
                print(f"✅ {test.name}: PASSED")
            else:
                print(f"❌ {test.name}: FAILED - {result.error_message}")
                
        return results