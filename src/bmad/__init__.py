"""
BMAD (Bayesian Music Analysis and Decision) Methodology Framework
===============================================================

This unified framework consolidates all BMAD methodology implementations
from tools/bmad/ into an integrated system that works with the new CLI.

BMAD Components:
- Core methodology engine
- Certification validation system  
- Real data optimization cycles
- Prompt optimization system
- Pure metadata analysis
- Integration with unified CLI system

Consolidated from:
- bmad_100_certification_validator.py
- bmad_demo_certification.py  
- bmad_prompt_optimization.py
- bmad_pure_metadata_optimizer.py
- bmad_real_data_optimizer.py
"""

__version__ = "1.0.0"

from .core import BMADEngine, BMADConfig, BMADResult
from .certification import CertificationValidator, CertificationReport
from .optimization import PromptOptimizer, DataOptimizer, OptimizationCycle
from .metadata import MetadataAnalyzer, PureMetadataExtractor

__all__ = [
    'BMADEngine',
    'BMADConfig', 
    'BMADResult',
    'CertificationValidator',
    'CertificationReport',
    'PromptOptimizer',
    'DataOptimizer',
    'OptimizationCycle',
    'MetadataAnalyzer',
    'PureMetadataExtractor'
]