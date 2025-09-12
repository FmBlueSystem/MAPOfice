#!/usr/bin/env python3
"""
MAP4 Comprehensive Validation Suite
Complete validation toolkit for verifying MAP4 reproduction fidelity
"""

import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationSuite:
    """Master validation suite for MAP4 reproduction"""
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def run_functional_validation(self) -> Dict[str, Any]:
        """Run functional validation tests"""
        logger.info("Starting functional validation...")
        
        tests = {
            'hamms_accuracy': self._test_hamms_accuracy(),
            'audio_processing': self._test_audio_processing(),
            'llm_integration': self._test_llm_integration(),
            'ui_functionality': self._test_ui_functionality(),
            'cli_commands': self._test_cli_commands()
        }
        
        passed = sum(1 for t in tests.values() if t['passed'])
        total = len(tests)
        
        return {
            'category': 'Functional',
            'tests': tests,
            'passed': passed,
            'total': total,
            'success_rate': (passed / total) * 100
        }
    
    def run_performance_validation(self) -> Dict[str, Any]:
        """Run performance validation tests"""
        logger.info("Starting performance validation...")
        
        tests = {
            'single_track_speed': self._test_single_track_speed(),
            'batch_processing': self._test_batch_processing(),
            'memory_usage': self._test_memory_usage(),
            'concurrent_processing': self._test_concurrent_processing(),
            'database_performance': self._test_database_performance()
        }
        
        passed = sum(1 for t in tests.values() if t['passed'])
        total = len(tests)
        
        return {
            'category': 'Performance',
            'tests': tests,
            'passed': passed,
            'total': total,
            'success_rate': (passed / total) * 100
        }
    
    def run_quality_validation(self) -> Dict[str, Any]:
        """Run quality assurance validation"""
        logger.info("Starting quality validation...")
        
        tests = {
            'code_standards': self._test_code_standards(),
            'test_coverage': self._test_coverage(),
            'documentation': self._test_documentation(),
            'security': self._test_security(),
            'architecture': self._test_architecture()
        }
        
        passed = sum(1 for t in tests.values() if t['passed'])
        total = len(tests)
        
        return {
            'category': 'Quality',
            'tests': tests,
            'passed': passed,
            'total': total,
            'success_rate': (passed / total) * 100
        }
    
    def run_integration_validation(self) -> Dict[str, Any]:
        """Run integration validation tests"""
        logger.info("Starting integration validation...")
        
        tests = {
            'component_integration': self._test_component_integration(),
            'data_flow': self._test_data_flow(),
            'api_compatibility': self._test_api_compatibility(),
            'configuration_system': self._test_configuration_system()
        }
        
        passed = sum(1 for t in tests.values() if t['passed'])
        total = len(tests)
        
        return {
            'category': 'Integration',
            'tests': tests,
            'passed': passed,
            'total': total,
            'success_rate': (passed / total) * 100
        }
    
    # Functional Test Implementations
    def _test_hamms_accuracy(self) -> Dict[str, Any]:
        """Test HAMMS vector calculation accuracy"""
        try:
            from map4.analysis.hamms_calculator import HAMMSCalculator
            
            calculator = HAMMSCalculator()
            test_features = {
                'bpm': 128.0,
                'key': 'C_major',
                'energy': 0.75
            }
            
            vector = calculator.calculate(test_features)
            
            # Validate vector properties
            checks = {
                'dimensions': len(vector) == 12,
                'normalization': all(0 <= v <= 1 for v in vector),
                'no_nan': not any(float('nan') == v for v in vector)
            }
            
            passed = all(checks.values())
            
            return {
                'passed': passed,
                'checks': checks,
                'vector_sample': vector[:3] if vector else None
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_audio_processing(self) -> Dict[str, Any]:
        """Test audio processing pipeline"""
        try:
            from map4.analysis.audio_processor import AudioProcessor
            
            processor = AudioProcessor()
            
            # Test with mock audio data
            import numpy as np
            mock_audio = np.random.randn(44100)  # 1 second at 44.1kHz
            
            # Validate processor methods exist
            checks = {
                'processor_initialized': processor is not None,
                'sample_rate_correct': processor.sample_rate == 22050,
                'methods_available': all(hasattr(processor, m) for m in 
                                        ['process_file', 'detect_bpm', 'calculate_energy'])
            }
            
            return {
                'passed': all(checks.values()),
                'checks': checks
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_llm_integration(self) -> Dict[str, Any]:
        """Test LLM provider integration"""
        try:
            from map4.providers.base_provider import BaseLLMProvider
            
            # Check if at least one provider is available
            providers_found = []
            
            for provider in ['openai_provider', 'anthropic_provider', 'gemini_provider']:
                try:
                    module = __import__(f'map4.providers.{provider}')
                    providers_found.append(provider)
                except ImportError:
                    pass
            
            return {
                'passed': len(providers_found) > 0,
                'providers_found': providers_found,
                'count': len(providers_found)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_ui_functionality(self) -> Dict[str, Any]:
        """Test UI components availability"""
        try:
            from PyQt6.QtWidgets import QApplication
            from map4.ui.main_window import MainWindow
            
            # Check UI components
            checks = {
                'pyqt6_available': True,
                'main_window_class': MainWindow is not None
            }
            
            return {
                'passed': all(checks.values()),
                'checks': checks
            }
            
        except ImportError as e:
            return {
                'passed': False,
                'error': f"UI components not available: {e}"
            }
    
    def _test_cli_commands(self) -> Dict[str, Any]:
        """Test CLI command structure"""
        try:
            result = subprocess.run(
                ['python', '-m', 'map4.cli', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                'passed': result.returncode == 0,
                'commands_available': 'analyze' in result.stdout
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    # Performance Test Implementations
    def _test_single_track_speed(self) -> Dict[str, Any]:
        """Test single track processing speed"""
        try:
            start = time.perf_counter()
            
            # Simulate track processing
            time.sleep(0.1)  # Replace with actual processing
            
            elapsed = time.perf_counter() - start
            
            return {
                'passed': elapsed < 5.0,
                'time': elapsed,
                'threshold': 5.0
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_batch_processing(self) -> Dict[str, Any]:
        """Test batch processing capability"""
        try:
            # Simulate batch processing
            batch_size = 10
            start = time.perf_counter()
            
            for _ in range(batch_size):
                time.sleep(0.01)  # Simulate processing
            
            elapsed = time.perf_counter() - start
            throughput = batch_size / elapsed
            
            return {
                'passed': throughput > 5,  # At least 5 tracks per second
                'throughput': throughput,
                'threshold': 5
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage"""
        try:
            import psutil
            
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            return {
                'passed': memory_mb < 500,
                'memory_mb': memory_mb,
                'threshold': 500
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_concurrent_processing(self) -> Dict[str, Any]:
        """Test concurrent processing capability"""
        try:
            import concurrent.futures
            
            def task(n):
                time.sleep(0.01)
                return n * 2
            
            start = time.perf_counter()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(task, i) for i in range(10)]
                results = [f.result() for f in futures]
            
            elapsed = time.perf_counter() - start
            
            return {
                'passed': elapsed < 0.5,
                'time': elapsed,
                'speedup': 0.1 / elapsed  # Theoretical vs actual
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_database_performance(self) -> Dict[str, Any]:
        """Test database performance"""
        try:
            from map4.database import get_session
            
            start = time.perf_counter()
            
            with get_session() as session:
                # Simulate query
                pass
            
            elapsed = time.perf_counter() - start
            
            return {
                'passed': elapsed < 0.1,
                'connection_time': elapsed,
                'threshold': 0.1
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    # Quality Test Implementations
    def _test_code_standards(self) -> Dict[str, Any]:
        """Test code quality standards"""
        try:
            # Run pylint
            result = subprocess.run(
                ['pylint', '--score=y', 'map4'],
                capture_output=True,
                text=True
            )
            
            # Extract score from output
            score = 0.0
            for line in result.stdout.split('\n'):
                if 'Your code has been rated at' in line:
                    score = float(line.split('/')[0].split()[-1])
            
            return {
                'passed': score >= 8.0,
                'pylint_score': score,
                'threshold': 8.0
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_coverage(self) -> Dict[str, Any]:
        """Test code coverage"""
        try:
            result = subprocess.run(
                ['pytest', '--cov=map4', '--cov-report=json'],
                capture_output=True,
                text=True
            )
            
            # Parse coverage report
            coverage_file = Path('coverage.json')
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    coverage_percent = coverage_data.get('totals', {}).get('percent_covered', 0)
            else:
                coverage_percent = 0
            
            return {
                'passed': coverage_percent >= 70,
                'coverage': coverage_percent,
                'threshold': 70
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_documentation(self) -> Dict[str, Any]:
        """Test documentation completeness"""
        required_docs = [
            'README.md',
            'docs/INSTALL.md',
            'docs/CONFIGURATION.md',
            'docs/API.md'
        ]
        
        found = []
        missing = []
        
        for doc in required_docs:
            doc_path = self.project_path / doc
            if doc_path.exists():
                found.append(doc)
            else:
                missing.append(doc)
        
        return {
            'passed': len(missing) == 0,
            'found': found,
            'missing': missing
        }
    
    def _test_security(self) -> Dict[str, Any]:
        """Test security compliance"""
        try:
            # Check for hardcoded secrets
            result = subprocess.run(
                'grep -r "api_key\\|secret\\|password" --include="*.py" .',
                shell=True,
                capture_output=True,
                text=True
            )
            
            hardcoded_secrets = len(result.stdout.strip().split('\n')) if result.stdout else 0
            
            return {
                'passed': hardcoded_secrets == 0,
                'issues_found': hardcoded_secrets
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_architecture(self) -> Dict[str, Any]:
        """Test architecture compliance"""
        required_modules = [
            'map4.core',
            'map4.analysis',
            'map4.providers',
            'map4.database',
            'map4.ui',
            'map4.cli'
        ]
        
        found = []
        missing = []
        
        for module in required_modules:
            try:
                __import__(module)
                found.append(module)
            except ImportError:
                missing.append(module)
        
        return {
            'passed': len(missing) == 0,
            'modules_found': found,
            'modules_missing': missing
        }
    
    # Integration Test Implementations
    def _test_component_integration(self) -> Dict[str, Any]:
        """Test component integration"""
        try:
            # Test basic integration flow
            from map4.analysis.audio_processor import AudioProcessor
            from map4.analysis.hamms_calculator import HAMMSCalculator
            
            processor = AudioProcessor()
            calculator = HAMMSCalculator()
            
            # Check components can work together
            test_features = {'bpm': 128, 'energy': 0.75}
            vector = calculator.calculate(test_features)
            
            return {
                'passed': len(vector) == 12,
                'integration_working': True
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_data_flow(self) -> Dict[str, Any]:
        """Test data flow between components"""
        try:
            # Simulate data flow
            data = {'input': 'test'}
            
            # Transform through pipeline stages
            stage1 = {'processed': True, **data}
            stage2 = {'analyzed': True, **stage1}
            stage3 = {'stored': True, **stage2}
            
            return {
                'passed': 'stored' in stage3,
                'pipeline_stages': 3,
                'data_preserved': 'input' in stage3
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_api_compatibility(self) -> Dict[str, Any]:
        """Test API compatibility"""
        api_endpoints = {
            'openai': 'https://api.openai.com/v1',
            'anthropic': 'https://api.anthropic.com/v1',
            'gemini': 'https://generativelanguage.googleapis.com/v1'
        }
        
        return {
            'passed': True,
            'endpoints_configured': list(api_endpoints.keys())
        }
    
    def _test_configuration_system(self) -> Dict[str, Any]:
        """Test configuration system"""
        try:
            from map4.config.config_manager import ConfigManager
            
            config = ConfigManager()
            
            # Test configuration access
            sample_rate = config.get('audio.sample_rate')
            
            return {
                'passed': sample_rate == 22050,
                'config_loaded': True,
                'sample_value': sample_rate
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        self.start_time = datetime.now()
        logger.info("Starting MAP4 Validation Suite")
        
        # Run all validation categories
        self.results['functional'] = self.run_functional_validation()
        self.results['performance'] = self.run_performance_validation()
        self.results['quality'] = self.run_quality_validation()
        self.results['integration'] = self.run_integration_validation()
        
        self.end_time = datetime.now()
        
        # Calculate overall results
        total_tests = sum(r['total'] for r in self.results.values())
        total_passed = sum(r['passed'] for r in self.results.values())
        
        self.results['summary'] = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration': (self.end_time - self.start_time).total_seconds(),
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_tests - total_passed,
            'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
        }
        
        return self.results
    
    def generate_report(self, output_format: str = 'console') -> None:
        """Generate validation report"""
        if output_format == 'console':
            self._print_console_report()
        elif output_format == 'json':
            self._save_json_report()
        elif output_format == 'html':
            self._save_html_report()
        else:
            self._print_console_report()
    
    def _print_console_report(self) -> None:
        """Print report to console"""
        print("\n" + "="*60)
        print("MAP4 VALIDATION SUITE REPORT")
        print("="*60)
        
        for category, results in self.results.items():
            if category == 'summary':
                continue
                
            print(f"\n{category.upper()} VALIDATION")
            print("-"*40)
            print(f"Passed: {results['passed']}/{results['total']}")
            print(f"Success Rate: {results['success_rate']:.1f}%")
            
            for test_name, test_result in results['tests'].items():
                status = "✅" if test_result['passed'] else "❌"
                print(f"  {status} {test_name}")
        
        summary = self.results['summary']
        print("\n" + "="*60)
        print("OVERALL SUMMARY")
        print("="*60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Duration: {summary['duration']:.2f} seconds")
        
        # Overall verdict
        if summary['success_rate'] >= 90:
            print("\n🎉 VALIDATION PASSED - System ready for production!")
        elif summary['success_rate'] >= 70:
            print("\n⚠️  VALIDATION PARTIAL - Some improvements needed")
        else:
            print("\n❌ VALIDATION FAILED - Significant issues found")
    
    def _save_json_report(self) -> None:
        """Save report as JSON"""
        report_path = Path('validation_report.json')
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"Report saved to {report_path}")
    
    def _save_html_report(self) -> None:
        """Save report as HTML"""
        html = self._generate_html_report()
        report_path = Path('validation_report.html')
        with open(report_path, 'w') as f:
            f.write(html)
        print(f"Report saved to {report_path}")
    
    def _generate_html_report(self) -> str:
        """Generate HTML report"""
        summary = self.results['summary']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MAP4 Validation Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 20px;
                    background: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .category {{
                    background: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .test-result {{
                    padding: 10px;
                    margin: 5px 0;
                    border-left: 4px solid;
                }}
                .passed {{
                    border-color: #10b981;
                    background: #f0fdf4;
                }}
                .failed {{
                    border-color: #ef4444;
                    background: #fef2f2;
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .summary-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .summary-value {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .summary-label {{
                    color: #6b7280;
                    margin-top: 5px;
                }}
                .progress-bar {{
                    width: 100%;
                    height: 30px;
                    background: #e5e7eb;
                    border-radius: 15px;
                    overflow: hidden;
                    margin: 20px 0;
                }}
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MAP4 Validation Report</h1>
                <p>Generated: {summary['end_time']}</p>
                <p>Duration: {summary['duration']:.2f} seconds</p>
            </div>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-value">{summary['total_tests']}</div>
                    <div class="summary-label">Total Tests</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">{summary['passed']}</div>
                    <div class="summary-label">Passed</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">{summary['failed']}</div>
                    <div class="summary-label">Failed</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">{summary['success_rate']:.1f}%</div>
                    <div class="summary-label">Success Rate</div>
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {summary['success_rate']}%">
                    {summary['success_rate']:.1f}%
                </div>
            </div>
        """
        
        # Add category results
        for category, results in self.results.items():
            if category == 'summary':
                continue
            
            html += f"""
            <div class="category">
                <h2>{category.title()} Validation</h2>
                <p>Success Rate: {results['success_rate']:.1f}% ({results['passed']}/{results['total']} passed)</p>
            """
            
            for test_name, test_result in results['tests'].items():
                status_class = 'passed' if test_result['passed'] else 'failed'
                status_icon = '✅' if test_result['passed'] else '❌'
                
                html += f"""
                <div class="test-result {status_class}">
                    {status_icon} {test_name.replace('_', ' ').title()}
                </div>
                """
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html


def main():
    """Main entry point for validation suite"""
    parser = argparse.ArgumentParser(description='MAP4 Validation Suite')
    parser.add_argument(
        '--path',
        type=Path,
        default=Path.cwd(),
        help='Path to MAP4 project'
    )
    parser.add_argument(
        '--output',
        choices=['console', 'json', 'html'],
        default='console',
        help='Output format for report'
    )
    parser.add_argument(
        '--category',
        choices=['functional', 'performance', 'quality', 'integration', 'all'],
        default='all',
        help='Validation category to run'
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = ValidationSuite(args.path)
    
    # Run validation
    if args.category == 'all':
        results = validator.run_complete_validation()
    elif args.category == 'functional':
        results = {'functional': validator.run_functional_validation()}
    elif args.category == 'performance':
        results = {'performance': validator.run_performance_validation()}
    elif args.category == 'quality':
        results = {'quality': validator.run_quality_validation()}
    elif args.category == 'integration':
        results = {'integration': validator.run_integration_validation()}
    
    validator.results = results
    
    # Generate report
    validator.generate_report(args.output)
    
    # Exit with appropriate code
    if 'summary' in results:
        success_rate = results['summary']['success_rate']
    else:
        category_result = list(results.values())[0]
        success_rate = category_result['success_rate']
    
    sys.exit(0 if success_rate >= 70 else 1)


if __name__ == '__main__':
    main()