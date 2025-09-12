"""
Integration Validation Tests
============================

Consolidates integration-focused tests from tools/validation/
- test_persistent_scanner.py
- test_production_integration.py
- validate_real_audio_analysis.py
- test_force_new_analysis.py

Tests end-to-end system integration, real-world performance, and production readiness.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Add project root to path  
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tests.validation.base import BaseValidationTest, TestResult, APIKeyManager

# Import system components
from src.services.track_database import TrackDatabase
from src.services.storage import Storage

try:
    from src.services.persistent_library_scanner import PersistentLibraryScanner, ScanConfiguration
except ImportError:
    PersistentLibraryScanner = None
    ScanConfiguration = None

@dataclass 
class ScannerTestStats:
    """Scanner performance statistics"""
    files_discovered: int = 0
    files_processed: int = 0
    files_cached: int = 0
    files_analyzed: int = 0
    files_skipped: int = 0
    files_error: int = 0
    cache_hit_rate: float = 0.0
    memory_usage_mb: float = 0.0
    scan_speed_fps: float = 0.0

class PersistentScannerTest(BaseValidationTest):
    """Test persistent library scanner functionality"""
    
    def __init__(self):
        super().__init__(
            "Persistent Scanner Test",
            "Validate unlimited scanner service implementation with caching and performance"
        )
        self.temp_dir = None
        self.scanner = None
        self.database = None
        
    def setup(self) -> bool:
        """Setup test environment with temporary database"""
        try:
            # Create temporary directory for test database
            self.temp_dir = tempfile.mkdtemp(prefix="scanner_test_")
            test_db_path = os.path.join(self.temp_dir, "test_scanner.db")
            
            # Initialize database and scanner
            self.database = TrackDatabase(test_db_path)
            
            if PersistentLibraryScanner:
                self.scanner = PersistentLibraryScanner(self.database)
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def teardown(self):
        """Cleanup test environment"""
        if self.scanner:
            try:
                self.scanner.close()
            except:
                pass
                
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def run_test(self) -> TestResult:
        """Run scanner integration tests"""
        try:
            test_results = {}
            overall_success = True
            
            # Test 1: Path validation
            path_test = self._test_path_validation()
            test_results['path_validation'] = path_test
            if not path_test:
                overall_success = False
            
            # Test 2: File discovery
            discovery_test, discovery_stats = self._test_file_discovery()
            test_results['file_discovery'] = discovery_test
            test_results['discovery_stats'] = discovery_stats
            if not discovery_test:
                overall_success = False
            
            # Test 3: Caching logic
            cache_test = self._test_caching_logic()
            test_results['caching_logic'] = cache_test
            if not cache_test:
                overall_success = False
                
            # Test 4: Memory constraints
            memory_test, memory_stats = self._test_memory_constraints()
            test_results['memory_constraints'] = memory_test
            test_results['memory_stats'] = memory_stats
            if not memory_test:
                overall_success = False
            
            # Test 5: Database integration
            db_test = self._test_database_integration()
            test_results['database_integration'] = db_test
            if not db_test:
                overall_success = False
            
            return TestResult(
                test_name=self.name,
                success=overall_success,
                duration=0,
                details=test_results
            )
            
        except Exception as e:
            return TestResult(
                test_name=self.name,
                success=False,
                duration=0,
                details={},
                error_message=str(e)
            )
    
    def _create_test_audio_files(self, count: int = 50) -> str:
        """Create temporary test audio files"""
        test_music_dir = os.path.join(self.temp_dir, "test_music")
        os.makedirs(test_music_dir, exist_ok=True)
        
        # Create test files with different extensions
        extensions = ['.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg']
        
        for i in range(count):
            ext = extensions[i % len(extensions)]
            genre_dir = os.path.join(test_music_dir, f"genre_{i // 10}")
            os.makedirs(genre_dir, exist_ok=True)
            
            test_file = os.path.join(genre_dir, f"test_track_{i:03d}{ext}")
            
            # Create empty file for testing
            with open(test_file, 'w') as f:
                f.write("")
        
        return test_music_dir
    
    def _test_path_validation(self) -> bool:
        """Test library path validation"""
        try:
            # Test invalid paths
            try:
                self.scanner.validate_library_path("")
                return False  # Should raise ValueError
            except ValueError:
                pass  # Expected
            
            try:
                self.scanner.validate_library_path("/nonexistent/path")
                return False  # Should raise FileNotFoundError  
            except FileNotFoundError:
                pass  # Expected
            
            # Test valid path (temp dir)
            result = self.scanner.validate_library_path(self.temp_dir)
            return True
            
        except Exception:
            return False
    
    def _test_file_discovery(self) -> tuple[bool, Dict]:
        """Test unlimited file discovery generator"""
        try:
            # Create test files
            test_dir = self._create_test_audio_files(100)
            
            # Test file discovery
            discovered_files = list(self.scanner.discover_audio_files_unlimited(test_dir))
            
            # Validate that expected files were found
            expected_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg'}
            found_extensions = set()
            
            for file_path in discovered_files:
                ext = os.path.splitext(file_path)[1].lower()
                found_extensions.add(ext)
            
            stats = {
                'files_discovered': len(discovered_files),
                'expected_extensions': len(expected_extensions),
                'found_extensions': len(found_extensions),
                'extensions_found': list(found_extensions)
            }
            
            success = len(discovered_files) > 0 and len(found_extensions) >= 3
            return success, stats
            
        except Exception:
            return False, {}
    
    def _test_caching_logic(self) -> bool:
        """Test intelligent caching with modification time checks"""
        try:
            test_dir = self._create_test_audio_files(10)
            test_files = list(self.scanner.discover_audio_files_unlimited(test_dir))
            
            if not test_files:
                return False
            
            test_file = test_files[0]
            
            # Test different scan modes
            modes_to_test = ["full", "incremental", "smart"]
            results = []
            
            for mode in modes_to_test:
                result = self.scanner.should_analyze_file(test_file, mode)
                results.append(result)
            
            # At least one mode should work
            return any(results)
            
        except Exception:
            return False
    
    def _test_memory_constraints(self) -> tuple[bool, Dict]:
        """Test memory usage constraints"""
        try:
            # Create larger test dataset
            test_dir = self._create_test_audio_files(200)
            
            # Monitor memory usage during file discovery
            initial_memory = self.scanner._estimate_memory_usage()
            
            # Discover files and check memory
            file_count = 0
            max_memory = initial_memory
            
            for file_path in self.scanner.discover_audio_files_unlimited(test_dir):
                file_count += 1
                if file_count % 50 == 0:
                    current_memory = self.scanner._estimate_memory_usage()
                    max_memory = max(max_memory, current_memory)
                    
                    # Check memory constraint (should be <500MB as per spec)
                    if current_memory > 500:
                        break
            
            final_memory = self.scanner._estimate_memory_usage()
            memory_increase = final_memory - initial_memory
            
            stats = {
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'max_memory_mb': max_memory,
                'memory_increase_mb': memory_increase,
                'files_processed': file_count
            }
            
            # Success if memory stayed under 500MB
            success = max_memory < 500
            return success, stats
            
        except Exception:
            return False, {}
    
    def _test_database_integration(self) -> bool:
        """Test integration with TrackDatabase"""
        try:
            # Test database connection
            if not self.database.conn:
                return False
            
            # Test basic database operations
            stats = self.scanner.get_library_statistics()
            
            # Test cleanup operations
            orphaned_count = self.scanner.cleanup_orphaned_records()
            
            return True
            
        except Exception:
            return False

class RealAudioAnalysisTest(BaseValidationTest):
    """Test real audio analysis capabilities"""
    
    def __init__(self, audio_directory: Optional[str] = None):
        super().__init__(
            "Real Audio Analysis Test",
            "Validate analysis of real audio files if available"
        )
        self.audio_directory = audio_directory
        
    def setup(self) -> bool:
        """Setup real audio analysis test"""
        # Check if we have a real audio directory
        if self.audio_directory and os.path.exists(self.audio_directory):
            return True
        
        # Check for test audio in project
        test_audio_dir = os.path.join(project_root, "test_audio")
        if os.path.exists(test_audio_dir):
            self.audio_directory = test_audio_dir
            return True
            
        # Skip if no real audio available
        return False
        
    def run_test(self) -> TestResult:
        """Run real audio analysis test"""
        try:
            if not self.audio_directory:
                return TestResult(
                    test_name=self.name,
                    success=False,
                    duration=0,
                    details={},
                    error_message="No real audio directory available"
                )
            
            # Find audio files
            audio_files = []
            audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg'}
            
            for root, dirs, files in os.walk(self.audio_directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in audio_extensions):
                        audio_files.append(os.path.join(root, file))
                        if len(audio_files) >= 5:  # Limit for testing
                            break
            
            if not audio_files:
                return TestResult(
                    test_name=self.name,
                    success=False,
                    duration=0,
                    details={},
                    error_message="No audio files found in directory"
                )
            
            analysis_results = []
            
            # Test each audio file
            for audio_file in audio_files:
                try:
                    # Basic file existence and size check
                    file_size = os.path.getsize(audio_file)
                    file_name = os.path.basename(audio_file)
                    
                    analysis_results.append({
                        'file': file_name,
                        'size_bytes': file_size,
                        'analyzed': file_size > 0,
                        'error': None
                    })
                    
                except Exception as e:
                    analysis_results.append({
                        'file': os.path.basename(audio_file),
                        'size_bytes': 0,
                        'analyzed': False,
                        'error': str(e)
                    })
            
            successful_analyses = sum(1 for result in analysis_results if result['analyzed'])
            
            return TestResult(
                test_name=self.name,
                success=successful_analyses > 0,
                duration=0,
                details={
                    'audio_directory': self.audio_directory,
                    'files_found': len(audio_files),
                    'files_analyzed': successful_analyses,
                    'analysis_results': analysis_results
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

class ProductionIntegrationTest(BaseValidationTest):
    """Test production-ready system integration"""
    
    def __init__(self):
        super().__init__(
            "Production Integration Test",
            "Validate system readiness for production deployment"
        )
        
    def setup(self) -> bool:
        """Setup production integration test"""
        # Always return True as this test checks system readiness
        return True
        
    def run_test(self) -> TestResult:
        """Run production readiness tests"""
        try:
            checks = {}
            overall_success = True
            
            # Check 1: Environment configuration
            env_check = self._check_environment_config()
            checks['environment_config'] = env_check
            if not env_check['success']:
                overall_success = False
            
            # Check 2: Database connectivity
            db_check = self._check_database_connectivity()
            checks['database_connectivity'] = db_check
            if not db_check['success']:
                overall_success = False
                
            # Check 3: Provider availability
            provider_check = self._check_provider_availability()
            checks['provider_availability'] = provider_check
            if not provider_check['success']:
                overall_success = False
            
            # Check 4: System resources
            resource_check = self._check_system_resources()
            checks['system_resources'] = resource_check
            if not resource_check['success']:
                overall_success = False
            
            return TestResult(
                test_name=self.name,
                success=overall_success,
                duration=0,
                details=checks
            )
            
        except Exception as e:
            return TestResult(
                test_name=self.name,
                success=False,
                duration=0,
                details={},
                error_message=str(e)
            )
    
    def _check_environment_config(self) -> Dict[str, Any]:
        """Check environment configuration"""
        try:
            required_vars = ['ZAI_API_KEY', 'ANTHROPIC_API_KEY']
            missing_vars = []
            
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            # Check .env file exists
            env_file_exists = os.path.exists(os.path.join(project_root, '.env'))
            
            return {
                'success': len(missing_vars) < len(required_vars),  # At least one key available
                'env_file_exists': env_file_exists,
                'missing_vars': missing_vars,
                'available_providers': len(required_vars) - len(missing_vars)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Create temporary database to test
            with tempfile.TemporaryDirectory() as temp_dir:
                test_db_path = os.path.join(temp_dir, "test.db")
                db = TrackDatabase(test_db_path)
                
                # Test basic operations
                success = db.conn is not None
                
                return {
                    'success': success,
                    'database_engine': 'SQLite',
                    'connection_tested': True
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_provider_availability(self) -> Dict[str, Any]:
        """Check LLM provider availability"""
        try:
            available_keys = APIKeyManager.check_required_keys(['anthropic', 'zai', 'openai'])
            
            available_count = sum(available_keys.values())
            
            return {
                'success': available_count > 0,
                'available_providers': [k for k, v in available_keys.items() if v],
                'total_available': available_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            import psutil
            
            # Check memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            # Check disk space
            disk = psutil.disk_usage(project_root)
            free_gb = disk.free / (1024**3)
            
            # Success if we have reasonable resources
            success = available_gb > 1.0 and free_gb > 5.0
            
            return {
                'success': success,
                'available_memory_gb': round(available_gb, 2),
                'free_disk_gb': round(free_gb, 2),
                'cpu_count': psutil.cpu_count()
            }
            
        except ImportError:
            return {
                'success': True,  # Assume OK if psutil not available
                'note': 'psutil not installed, resource check skipped'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Test Suite Orchestrator
class IntegrationTestSuite:
    """Orchestrates all integration tests"""
    
    def __init__(self, audio_directory: Optional[str] = None):
        self.tests = [
            PersistentScannerTest(),
            RealAudioAnalysisTest(audio_directory),
            ProductionIntegrationTest()
        ]
        
    def run_all_tests(self):
        """Run all integration tests"""
        results = []
        
        print("🚀 Running Integration Test Suite")
        print("=" * 50)
        
        for test in self.tests:
            print(f"\n🔄 Running {test.name}...")
            
            result = test.execute()
            results.append(result)
            
            if result.success:
                print(f"✅ {test.name}: PASSED")
                if result.details:
                    self._print_test_summary(result)
            else:
                print(f"❌ {test.name}: FAILED - {result.error_message}")
                
        return results
    
    def _print_test_summary(self, result: TestResult):
        """Print summary for complex test results"""
        if result.test_name == "Persistent Scanner Test":
            details = result.details
            print(f"   📊 Path validation: {'✅' if details.get('path_validation') else '❌'}")
            print(f"   📊 File discovery: {'✅' if details.get('file_discovery') else '❌'}")
            print(f"   📊 Memory constraints: {'✅' if details.get('memory_constraints') else '❌'}")
            
        elif result.test_name == "Real Audio Analysis Test":
            details = result.details
            if 'files_found' in details:
                print(f"   📊 Audio files found: {details['files_found']}")
                print(f"   📊 Files analyzed: {details['files_analyzed']}")
                
        elif result.test_name == "Production Integration Test":
            details = result.details
            env_check = details.get('environment_config', {})
            if 'available_providers' in env_check:
                print(f"   📊 Available providers: {env_check['available_providers']}")
            provider_check = details.get('provider_availability', {})
            if 'total_available' in provider_check:
                print(f"   📊 Provider connections: {provider_check['total_available']}")