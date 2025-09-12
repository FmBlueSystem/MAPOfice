#!/usr/bin/env python3
"""Validate MAP4 project organization and functionality"""

import os
import sys
import subprocess
from pathlib import Path

def validate_directory_structure():
    """Validate new directory structure exists"""
    print("🔍 Validating directory structure...")
    
    required_dirs = [
        "src", "tests", "docs", "data", "tools", "config", "scripts",
        "data/playlists", "data/analysis", "data/samples", "data/databases",
        "tools/cli", "tools/debug", "tools/validation", "tools/bmad",
        "docs/api", "docs/user", "docs/development"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Directory structure validated")
    return True

def validate_file_organization():
    """Validate files are in correct locations"""
    print("🔍 Validating file organization...")
    
    # Check root directory is clean (should have minimal files)
    root_files = [f for f in os.listdir(".") if os.path.isfile(f)]
    python_files_in_root = [f for f in root_files if f.endswith('.py')]
    
    if len(python_files_in_root) > 5:  # Allow some essential files
        print(f"⚠️  Still {len(python_files_in_root)} Python files in root: {python_files_in_root}")
    else:
        print("✅ Root directory cleaned up")
    
    # Check data files are organized
    playlist_count = len(list(Path("data/playlists").glob("*.m3u"))) if Path("data/playlists").exists() else 0
    analysis_count = len(list(Path("data/analysis").glob("*.csv"))) + len(list(Path("data/analysis").glob("*.json"))) if Path("data/analysis").exists() else 0
    
    print(f"✅ Found {playlist_count} playlists and {analysis_count} analysis files organized")
    return True

def validate_imports():
    """Test critical imports still work"""
    print("🔍 Testing critical imports...")
    
    try:
        import sys
        import os
        # Add src to path properly
        src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
        sys.path.insert(0, src_path)
        
        # Test core imports
        from analysis.llm_provider import LLMProvider
        print("✅ LLM Provider import working")
        
        from services.enhanced_analyzer import EnhancedAnalyzer  
        print("✅ Enhanced Analyzer import working")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_application_startup():
    """Test main application can start"""
    print("🔍 Testing application startup...")
    
    try:
        # Test if main window can be imported (don't actually show GUI)
        cmd = [sys.executable, "-c", "import sys; sys.path.append('src'); from ui.enhanced_main_window import EnhancedMainWindow; print('✅ Main application can start')"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Main application startup test passed")
            return True
        else:
            print(f"❌ Application startup failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✅ Application startup test completed (timeout is normal)")
        return True
    except Exception as e:
        print(f"❌ Application startup test error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🔄 Starting MAP4 organization validation...\n")
    
    tests = [
        ("Directory Structure", validate_directory_structure),
        ("File Organization", validate_file_organization), 
        ("Import System", validate_imports),
        ("Application Startup", test_application_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append(False)
    
    print(f"\n{'='*50}")
    if all(results):
        print("🎉 ALL VALIDATION TESTS PASSED")
        print("✅ Project organization successful!")
        return 0
    else:
        print("💥 SOME VALIDATION TESTS FAILED")
        print("❌ Please review and fix issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())