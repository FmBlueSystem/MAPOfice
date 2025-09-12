"""
Unified Validation Test Runner
==============================

Master test runner that consolidates all validation functionality from tools/validation/
Replaces the 24+ individual validation scripts with organized test suites.

Usage:
    python -m tests.validation.runner                    # Run all tests
    python -m tests.validation.runner --suite provider   # Run specific suite
    python -m tests.validation.runner --quick            # Run quick tests only
    python -m tests.validation.runner --report           # Generate detailed report
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tests.validation.base import ValidationReport, TestResult
from tests.validation.provider_tests import ProviderTestSuite
from tests.validation.integration_tests import IntegrationTestSuite
from tests.validation.quality_tests import QualityTestSuite
from tests.validation.configuration_tests import ConfigurationTestSuite

@dataclass
class ValidationSummary:
    """Overall validation summary"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_duration: float
    success_rate: float
    suites_run: List[str]
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]

class UnifiedValidationRunner:
    """
    Unified validation test runner
    
    Consolidates functionality from all validation scripts:
    ✅ test_claude_provider.py → ProviderTestSuite
    ✅ test_enhanced_zai.py → ProviderTestSuite  
    ✅ test_multi_llm_integration.py → ProviderTestSuite
    ✅ test_persistent_scanner.py → IntegrationTestSuite
    ✅ test_production_integration.py → IntegrationTestSuite
    ✅ validate_real_audio_analysis.py → IntegrationTestSuite
    ✅ test_improved_prompt.py → QualityTestSuite
    ✅ test_prompt_comparison.py → QualityTestSuite
    ✅ test_genre_diversity.py → QualityTestSuite
    ✅ test_json_extraction.py → QualityTestSuite
    ✅ test_cultural_lyrics_integration.py → QualityTestSuite
    ✅ test_env_config.py → ConfigurationTestSuite
    ✅ test_implementation_status.py → ConfigurationTestSuite
    ✅ test_date_verification.py → ConfigurationTestSuite
    ✅ And 11 more scripts consolidated into organized suites...
    """
    
    def __init__(self):
        self.available_suites = {
            'provider': ProviderTestSuite,
            'integration': IntegrationTestSuite,
            'quality': QualityTestSuite,
            'configuration': ConfigurationTestSuite
        }
        
    def run_validation(self, 
                      suites: Optional[List[str]] = None,
                      quick_mode: bool = False,
                      audio_directory: Optional[str] = None,
                      generate_report: bool = False,
                      output_file: Optional[str] = None) -> ValidationSummary:
        """
        Run validation test suites
        
        Args:
            suites: List of suite names to run (None = all)
            quick_mode: Run only essential tests
            audio_directory: Directory with real audio files for testing
            generate_report: Generate detailed validation report
            output_file: File to save validation report
            
        Returns:
            ValidationSummary with overall results
        """
        
        print("🎯 MAP4 Unified Validation System")
        print("=" * 60)
        print(f"📊 Consolidates 24+ validation scripts into organized test framework")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        start_time = time.time()
        
        # Determine which suites to run
        if suites is None:
            suites_to_run = list(self.available_suites.keys())
        else:
            suites_to_run = [suite for suite in suites if suite in self.available_suites]
            if not suites_to_run:
                print("❌ No valid test suites specified")
                return self._create_empty_summary()
        
        if quick_mode:
            print("⚡ Quick mode: Running essential tests only")
            suites_to_run = ['configuration', 'provider']  # Essential suites
        
        print(f"🎯 Test suites to run: {', '.join(suites_to_run)}")
        print("")
        
        # Run test suites
        all_results = []
        suite_summaries = {}
        
        for suite_name in suites_to_run:
            print(f"\n{'='*20} {suite_name.upper()} TESTS {'='*20}")
            
            suite_class = self.available_suites[suite_name]
            
            # Initialize suite with parameters
            if suite_name == 'integration' and audio_directory:
                suite = suite_class(audio_directory)
            else:
                suite = suite_class()
            
            # Run suite tests
            suite_results = suite.run_all_tests()
            all_results.extend(suite_results)
            
            # Create suite summary
            suite_summary = self._create_suite_summary(suite_name, suite_results)
            suite_summaries[suite_name] = suite_summary
            
            print(f"\n📊 {suite_name.capitalize()} Suite Summary:")
            print(f"   Tests run: {suite_summary['total_tests']}")
            print(f"   Passed: {suite_summary['passed_tests']}")
            print(f"   Failed: {suite_summary['failed_tests']}")
            print(f"   Success rate: {suite_summary['success_rate']:.1%}")
        
        # Generate overall summary
        total_duration = time.time() - start_time
        summary = self._create_overall_summary(all_results, suites_to_run, total_duration)
        
        # Print final results
        print(f"\n{'='*60}")
        print("🎯 OVERALL VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"📊 Total tests run: {summary.total_tests}")
        print(f"✅ Tests passed: {summary.passed_tests}")
        print(f"❌ Tests failed: {summary.failed_tests}")
        print(f"⏭️  Tests skipped: {summary.skipped_tests}")
        print(f"⏱️  Total duration: {summary.total_duration:.2f}s")
        print(f"📈 Success rate: {summary.success_rate:.1%}")
        
        if summary.success_rate >= 0.9:
            print(f"\n🎉 EXCELLENT: System validation highly successful!")
        elif summary.success_rate >= 0.8:
            print(f"\n✅ GOOD: System validation successful with minor issues")
        elif summary.success_rate >= 0.7:
            print(f"\n⚠️  ACCEPTABLE: System validation passed with some concerns")
        else:
            print(f"\n❌ NEEDS ATTENTION: System validation found significant issues")
        
        # Show recommendations
        if summary.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, recommendation in enumerate(summary.recommendations[:5], 1):
                print(f"   {i}. {recommendation}")
        
        # Generate report if requested
        if generate_report:
            report_data = self._generate_detailed_report(summary, suite_summaries, all_results)
            
            if output_file:
                self._save_report(report_data, output_file)
                print(f"\n📄 Detailed report saved to: {output_file}")
            else:
                print(f"\n📄 Detailed report available in return data")
        
        print(f"\n🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return summary
    
    def _create_suite_summary(self, suite_name: str, results: list) -> Dict[str, Any]:
        """Create summary for individual test suite"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        success_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        
        return {
            'suite_name': suite_name,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'test_results': results
        }
    
    def _create_overall_summary(self, all_results: list, 
                               suites_run: List[str], total_duration: float) -> ValidationSummary:
        """Create overall validation summary"""
        
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.success)
        failed_tests = sum(1 for r in all_results if not r.success and r.error_message)
        skipped_tests = total_tests - passed_tests - failed_tests
        success_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        
        # Collect issues
        issues_found = []
        for result in all_results:
            if not result.success and result.error_message:
                issues_found.append({
                    'test_name': result.test_name,
                    'error': result.error_message,
                    'severity': 'error'
                })
        
        # Generate recommendations
        recommendations = self._generate_overall_recommendations(all_results, success_rate)
        
        return ValidationSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            total_duration=total_duration,
            success_rate=success_rate,
            suites_run=suites_run,
            issues_found=issues_found,
            recommendations=recommendations
        )
    
    def _generate_overall_recommendations(self, results: list, success_rate: float) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        # Analyze failure patterns
        failed_tests = [r for r in results if not r.success]
        
        if success_rate < 0.7:
            recommendations.append("Address critical system issues before production deployment")
        
        # Provider-specific recommendations
        provider_failures = [r for r in failed_tests if 'provider' in r.test_name.lower()]
        if provider_failures:
            recommendations.append("Configure and test LLM provider connections")
        
        # Configuration recommendations
        config_failures = [r for r in failed_tests if 'config' in r.test_name.lower()]
        if config_failures:
            recommendations.append("Review system configuration and environment setup")
        
        # Integration recommendations
        integration_failures = [r for r in failed_tests if 'integration' in r.test_name.lower()]
        if integration_failures:
            recommendations.append("Check system integration and component connectivity")
        
        # Quality recommendations
        quality_failures = [r for r in failed_tests if 'quality' in r.test_name.lower()]
        if quality_failures:
            recommendations.append("Optimize prompt quality and output consistency")
        
        if success_rate >= 0.9:
            recommendations.append("System validation excellent - ready for production")
        elif not recommendations:
            recommendations.append("System validation successful - monitor for continuous improvement")
        
        return recommendations
    
    def _generate_detailed_report(self, summary: ValidationSummary, 
                                 suite_summaries: Dict[str, Any],
                                 all_results: list) -> Dict[str, Any]:
        """Generate detailed validation report"""
        return {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'consolidation_info': 'Replaces 24+ individual validation scripts',
                'framework_version': '1.0.0'
            },
            'executive_summary': {
                'total_tests': summary.total_tests,
                'success_rate': summary.success_rate,
                'duration': summary.total_duration,
                'suites_tested': summary.suites_run,
                'overall_status': 'PASS' if summary.success_rate >= 0.8 else 'FAIL'
            },
            'suite_details': suite_summaries,
            'detailed_results': [
                {
                    'test_name': r.test_name,
                    'success': r.success,
                    'duration': r.duration,
                    'details': r.details,
                    'error_message': r.error_message
                }
                for r in all_results
            ],
            'issues_analysis': {
                'total_issues': len(summary.issues_found),
                'issues_by_severity': self._categorize_issues(summary.issues_found),
                'top_issues': summary.issues_found[:10]  # Top 10 issues
            },
            'recommendations': {
                'immediate_actions': summary.recommendations[:3],
                'long_term_improvements': summary.recommendations[3:],
                'consolidation_benefits': [
                    'Eliminated 24+ duplicate validation scripts',
                    'Unified testing framework with consistent reporting',
                    'Improved test organization and maintainability',
                    'Better coverage through systematic test categorization'
                ]
            }
        }
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize issues by severity"""
        categories = {'error': 0, 'warning': 0, 'info': 0}
        
        for issue in issues:
            severity = issue.get('severity', 'error')
            if severity in categories:
                categories[severity] += 1
        
        return categories
    
    def _save_report(self, report_data: Dict[str, Any], output_file: str):
        """Save detailed report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"⚠️  Could not save report to {output_file}: {e}")
    
    def _create_empty_summary(self) -> ValidationSummary:
        """Create empty summary for error cases"""
        return ValidationSummary(
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            total_duration=0.0,
            success_rate=0.0,
            suites_run=[],
            issues_found=[],
            recommendations=["Fix test suite configuration"]
        )

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MAP4 Unified Validation System - Consolidates 24+ validation scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Test Suites:
  provider      - LLM provider functionality (Claude, ZAI, etc.)
  integration   - System integration and real-world testing
  quality       - Output quality, prompts, and accuracy
  configuration - Environment, config, and system status

Examples:
  python -m tests.validation.runner                           # Run all tests
  python -m tests.validation.runner --suite provider quality  # Run specific suites
  python -m tests.validation.runner --quick                   # Essential tests only
  python -m tests.validation.runner --report                  # Generate detailed report

Replaces these individual scripts:
  ✅ test_claude_provider.py, test_enhanced_zai.py, test_multi_llm_integration.py
  ✅ test_persistent_scanner.py, validate_real_audio_analysis.py, test_production_integration.py
  ✅ test_improved_prompt.py, test_json_extraction.py, test_genre_diversity.py
  ✅ test_env_config.py, test_date_verification.py, test_implementation_status.py
  ✅ And 13+ more validation scripts consolidated into organized framework
        """
    )
    
    parser.add_argument(
        '--suite', 
        nargs='*',
        choices=['provider', 'integration', 'quality', 'configuration'],
        help='Specific test suites to run (default: all)'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run only essential/quick tests'
    )
    
    parser.add_argument(
        '--audio-dir',
        type=str,
        help='Directory containing real audio files for integration testing'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed validation report'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for detailed report (JSON format)'
    )
    
    parser.add_argument(
        '--list-tests',
        action='store_true',
        help='List all available tests and exit'
    )
    
    args = parser.parse_args()
    
    runner = UnifiedValidationRunner()
    
    if args.list_tests:
        print("📋 Available Test Suites and Tests:")
        print("")
        
        for suite_name, suite_class in runner.available_suites.items():
            print(f"🔹 {suite_name.upper()} SUITE:")
            suite = suite_class()
            for test in suite.tests:
                print(f"   • {test.name}")
            print("")
        
        print("💡 Use --suite to run specific suites")
        print("📊 Total: 24+ individual validation scripts consolidated")
        return 0
    
    try:
        # Run validation
        summary = runner.run_validation(
            suites=args.suite,
            quick_mode=args.quick,
            audio_directory=args.audio_dir,
            generate_report=args.report,
            output_file=args.output
        )
        
        # Return appropriate exit code
        if summary.success_rate >= 0.8:
            return 0  # Success
        elif summary.success_rate >= 0.6:
            return 1  # Partial success
        else:
            return 2  # Significant issues
            
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())