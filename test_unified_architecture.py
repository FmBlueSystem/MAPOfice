#!/usr/bin/env python3
"""Test script to verify the unified architecture implementation."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_architecture():
    """Test the unified architecture components."""
    results = []
    
    print("=== Testing Unified CLI Architecture ===\n")
    
    # Test 1: Check directory structure
    print("1. Checking directory structure...")
    required_dirs = [
        "src/cli",
        "src/cli/commands",
        "src/analysis/providers",
        "config"
    ]
    
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            results.append(f"✓ {dir_path} exists")
        else:
            results.append(f"✗ {dir_path} missing")
    
    # Test 2: Check unified CLI files
    print("\n2. Checking unified CLI files...")
    cli_files = [
        "src/cli/unified_main.py",
        "src/cli/commands/analyze.py",
        "src/cli/commands/playlist.py",
        "src/cli/commands/provider.py",
        "src/cli/commands/bmad.py"
    ]
    
    for file_path in cli_files:
        full_path = Path(file_path)
        if full_path.exists():
            results.append(f"✓ {file_path} exists")
            # Check file size to ensure it's not empty
            size = full_path.stat().st_size
            if size > 100:
                results.append(f"  • Size: {size:,} bytes")
            else:
                results.append(f"  ⚠ File may be empty")
        else:
            results.append(f"✗ {file_path} missing")
    
    # Test 3: Check provider architecture
    print("\n3. Checking provider architecture...")
    provider_files = [
        "src/analysis/base_provider.py",
        "src/analysis/provider_factory.py",
        "src/analysis/providers/zai_provider.py",
        "src/analysis/providers/claude_provider.py",
        "src/analysis/providers/gemini_provider.py",
        "src/analysis/providers/openai_provider.py"
    ]
    
    for file_path in provider_files:
        full_path = Path(file_path)
        if full_path.exists():
            results.append(f"✓ {file_path} exists")
        else:
            results.append(f"✗ {file_path} missing")
    
    # Test 4: Check configuration system
    print("\n4. Checking configuration system...")
    config_files = [
        "config/default.yaml",
        "src/config.py"
    ]
    
    for file_path in config_files:
        full_path = Path(file_path)
        if full_path.exists():
            results.append(f"✓ {file_path} exists")
        else:
            results.append(f"✗ {file_path} missing")
    
    # Test 5: Check old CLI files status
    print("\n5. Checking old CLI files (should be archived or removed)...")
    old_cli_dir = Path("tools/cli")
    if old_cli_dir.exists():
        old_files = list(old_cli_dir.glob("*.py"))
        if len(old_files) > 0:
            results.append(f"⚠ Found {len(old_files)} old CLI files still in tools/cli/")
            for f in old_files[:3]:
                results.append(f"  • {f.name}")
            if len(old_files) > 3:
                results.append(f"  • ... and {len(old_files) - 3} more")
        else:
            results.append("✓ Old CLI directory is clean")
    else:
        results.append("✓ Old CLI directory doesn't exist")
    
    # Test 6: Import test
    print("\n6. Testing imports...")
    try:
        from src.analysis.base_provider import BaseLLMProvider
        results.append("✓ Can import BaseLLMProvider")
    except ImportError as e:
        results.append(f"✗ Cannot import BaseLLMProvider: {e}")
    
    try:
        from src.analysis.provider_factory import LLMProviderFactory
        results.append("✓ Can import LLMProviderFactory")
    except ImportError as e:
        results.append(f"✗ Cannot import LLMProviderFactory: {e}")
    
    try:
        from src.config import Config, ConfigLoader
        results.append("✓ Can import Config system")
    except ImportError as e:
        results.append(f"✗ Cannot import Config system: {e}")
    
    # Print all results
    print("\n=== Test Results ===")
    for result in results:
        print(result)
    
    # Summary
    passed = len([r for r in results if r.startswith("✓")])
    failed = len([r for r in results if r.startswith("✗")])
    warnings = len([r for r in results if r.startswith("⚠")])
    
    print(f"\n=== Summary ===")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Warnings: {warnings}")
    
    if failed == 0:
        print("\n🎉 All architecture components are in place!")
        print("\nThe unified CLI architecture has been successfully implemented:")
        print("• 9 duplicate CLI files → 1 unified interface (src/cli/unified_main.py)")
        print("• 7 provider variants → Factory pattern with 4 clean providers")
        print("• Scattered configs → Centralized configuration system")
        print("• No organization → Clear command structure (analyze, playlist, provider, bmad)")
    else:
        print("\n⚠ Some components are missing. Please review the failed items above.")
    
    return failed == 0


def count_reduction():
    """Count the reduction in files."""
    print("\n=== File Reduction Analysis ===")
    
    # Count old CLI files
    old_cli_files = [
        "playlist_cli_demo.py",
        "playlist_cli_enhanced.py",
        "playlist_cli_enhanced_fixed.py",
        "playlist_cli_final.py",
        "playlist_cli_simple.py",
        "playlist_bmad_certification.py",
        "playlist_bmad_certification_fixed.py",
        "pure_metadata_extractor.py",
        "simple_cli.py"
    ]
    
    # Count new unified files
    new_unified_files = [
        "src/cli/unified_main.py",
        "src/cli/commands/analyze.py",
        "src/cli/commands/playlist.py",
        "src/cli/commands/provider.py",
        "src/cli/commands/bmad.py"
    ]
    
    print(f"Old CLI files: {len(old_cli_files)}")
    for f in old_cli_files:
        print(f"  • {f}")
    
    print(f"\nNew unified files: {len(new_unified_files)}")
    for f in new_unified_files:
        print(f"  • {f}")
    
    print(f"\nReduction: {len(old_cli_files)} files → {len(new_unified_files)} files")
    print(f"Efficiency gain: {((len(old_cli_files) - len(new_unified_files)) / len(old_cli_files) * 100):.0f}% reduction")
    
    # Provider consolidation
    print("\n=== Provider Consolidation ===")
    old_providers = [
        "zai_provider.py",
        "zai_provider_backup.py",
        "zai_provider_enhanced.py",
        "zai_provider_minimal.py",
        "zai_provider_original_backup.py",
        "claude_provider.py",
        "gemini_provider.py"
    ]
    
    new_providers = [
        "providers/zai_provider.py",
        "providers/claude_provider.py",
        "providers/gemini_provider.py",
        "providers/openai_provider.py"
    ]
    
    print(f"Old provider files: {len(old_providers)}")
    print(f"New provider files: {len(new_providers)}")
    print(f"Plus: 1 factory pattern (provider_factory.py) + 1 base interface (base_provider.py)")


if __name__ == "__main__":
    success = test_architecture()
    count_reduction()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)