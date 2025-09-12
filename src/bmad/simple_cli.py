"""
BMAD Simple CLI (no dependencies)
=================================

Simplified version for testing consolidation without external dependencies.
"""

import sys
from src.bmad.core import create_bmad_engine, BMADMode
from src.bmad.certification import simulate_certification_demo

def bmad_demo():
    """Run BMAD demo"""
    print("🎵 BMAD Demo")
    try:
        report = simulate_certification_demo(10)
        print(f"✅ Demo successful - Accuracy: {report.accuracy:.2%}")
        return True
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def bmad_validate():
    """Run BMAD validation"""
    print("🔍 BMAD Validation")
    try:
        engine = create_bmad_engine(BMADMode.VALIDATION)
        test_track = {'title': 'Test', 'artist': 'Artist'}
        result = engine.execute([test_track])
        print(f"✅ Validation successful - Success: {result.success}")
        return True
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        bmad_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == 'validate':
        bmad_validate()
    else:
        print("Available commands: demo, validate")