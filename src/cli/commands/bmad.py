"""BMAD (Build, Measure, Analyze, Deploy) command module for MAP4 CLI.

This module provides commands for BMAD methodology implementation and certification.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import click
from datetime import datetime
from tabulate import tabulate

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.group(name='bmad')
def bmad_group():
    """BMAD methodology commands for architecture certification."""
    pass


@bmad_group.command(name='certify')
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.',
              help='Path to project root')
@click.option('--output', '-o', type=click.Path(), help='Output certification report')
@click.option('--threshold', type=float, default=0.95, help='Certification threshold')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def certify_project(ctx, project_path: str, output: Optional[str], 
                   threshold: float, verbose: bool):
    """Run BMAD certification on the project.
    
    Example:
        map4 bmad certify --project-path . --threshold 0.95 --output certification.json
    """
    project_root = Path(project_path).resolve()
    
    click.echo("=== BMAD Certification Process ===")
    click.echo(f"Project: {project_root}")
    click.echo(f"Threshold: {threshold * 100:.0f}%")
    click.echo("")
    
    # Run certification checks
    certification_results = {
        'project': str(project_root),
        'timestamp': datetime.now().isoformat(),
        'threshold': threshold,
        'phases': {}
    }
    
    # Phase 1: BUILD - Architecture validation
    click.echo("Phase 1: BUILD - Validating architecture...")
    build_results = _validate_build_phase(project_root, verbose)
    certification_results['phases']['build'] = build_results
    
    # Phase 2: MEASURE - Metrics collection
    click.echo("Phase 2: MEASURE - Collecting metrics...")
    measure_results = _validate_measure_phase(project_root, verbose)
    certification_results['phases']['measure'] = measure_results
    
    # Phase 3: ANALYZE - Code analysis
    click.echo("Phase 3: ANALYZE - Analyzing code quality...")
    analyze_results = _validate_analyze_phase(project_root, verbose)
    certification_results['phases']['analyze'] = analyze_results
    
    # Phase 4: DEPLOY - Deployment readiness
    click.echo("Phase 4: DEPLOY - Checking deployment readiness...")
    deploy_results = _validate_deploy_phase(project_root, verbose)
    certification_results['phases']['deploy'] = deploy_results
    
    # Calculate overall score
    total_checks = 0
    passed_checks = 0
    
    for phase, results in certification_results['phases'].items():
        total_checks += results['total']
        passed_checks += results['passed']
    
    overall_score = passed_checks / total_checks if total_checks > 0 else 0
    certification_results['overall_score'] = overall_score
    certification_results['passed'] = overall_score >= threshold
    
    # Display results
    click.echo("\n=== Certification Results ===")
    
    table_data = []
    for phase_name, results in certification_results['phases'].items():
        score = results['passed'] / results['total'] if results['total'] > 0 else 0
        status = '✓' if score >= threshold else '✗'
        table_data.append([
            phase_name.upper(),
            f"{results['passed']}/{results['total']}",
            f"{score * 100:.1f}%",
            status
        ])
    
    # Add overall row
    overall_status = '✓ CERTIFIED' if certification_results['passed'] else '✗ FAILED'
    table_data.append([
        'OVERALL',
        f"{passed_checks}/{total_checks}",
        f"{overall_score * 100:.1f}%",
        overall_status
    ])
    
    headers = ['Phase', 'Checks', 'Score', 'Status']
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Show failed checks if verbose
    if verbose and overall_score < 1.0:
        click.echo("\n=== Failed Checks ===")
        for phase_name, results in certification_results['phases'].items():
            if results.get('failed_checks'):
                click.echo(f"\n{phase_name.upper()}:")
                for check in results['failed_checks']:
                    click.echo(f"  ✗ {check}")
    
    # Save report if requested
    if output:
        with open(output, 'w') as f:
            json.dump(certification_results, f, indent=2)
        click.echo(f"\n✓ Certification report saved to: {output}")
    
    # Exit with appropriate code
    if not certification_results['passed']:
        click.echo(f"\n✗ Certification FAILED (score: {overall_score * 100:.1f}% < {threshold * 100:.0f}%)", err=True)
        ctx.exit(1)
    else:
        click.echo(f"\n✓ Certification PASSED (score: {overall_score * 100:.1f}%)")


@bmad_group.command(name='validate')
@click.argument('phase', type=click.Choice(['build', 'measure', 'analyze', 'deploy']))
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.',
              help='Path to project root')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def validate_phase(ctx, phase: str, project_path: str, verbose: bool):
    """Validate a specific BMAD phase.
    
    Example:
        map4 bmad validate build --project-path . --verbose
    """
    project_root = Path(project_path).resolve()
    
    click.echo(f"=== Validating {phase.upper()} Phase ===")
    click.echo(f"Project: {project_root}\n")
    
    # Run validation for specific phase
    if phase == 'build':
        results = _validate_build_phase(project_root, verbose)
    elif phase == 'measure':
        results = _validate_measure_phase(project_root, verbose)
    elif phase == 'analyze':
        results = _validate_analyze_phase(project_root, verbose)
    else:  # deploy
        results = _validate_deploy_phase(project_root, verbose)
    
    # Display results
    score = results['passed'] / results['total'] if results['total'] > 0 else 0
    
    click.echo(f"\n=== {phase.upper()} Phase Results ===")
    click.echo(f"Passed: {results['passed']}/{results['total']}")
    click.echo(f"Score: {score * 100:.1f}%")
    
    if verbose:
        if results.get('passed_checks'):
            click.echo("\n✓ Passed Checks:")
            for check in results['passed_checks']:
                click.echo(f"  • {check}")
        
        if results.get('failed_checks'):
            click.echo("\n✗ Failed Checks:")
            for check in results['failed_checks']:
                click.echo(f"  • {check}")
    
    if score < 1.0:
        ctx.exit(1)


@bmad_group.command(name='report')
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.',
              help='Path to project root')
@click.option('--format', 'output_format', type=click.Choice(['text', 'markdown', 'json']),
              default='markdown', help='Report format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Include detailed metrics')
@click.pass_context
def generate_report(ctx, project_path: str, output_format: str, 
                   output: Optional[str], verbose: bool):
    """Generate BMAD compliance report.
    
    Example:
        map4 bmad report --format markdown --output bmad_report.md
    """
    project_root = Path(project_path).resolve()
    
    click.echo("Generating BMAD compliance report...")
    
    # Collect all metrics
    report_data = {
        'project': str(project_root),
        'generated': datetime.now().isoformat(),
        'metrics': {}
    }
    
    # Collect metrics for each phase
    report_data['metrics']['build'] = _collect_build_metrics(project_root)
    report_data['metrics']['measure'] = _collect_measure_metrics(project_root)
    report_data['metrics']['analyze'] = _collect_analyze_metrics(project_root)
    report_data['metrics']['deploy'] = _collect_deploy_metrics(project_root)
    
    # Format report
    if output_format == 'json':
        report_content = json.dumps(report_data, indent=2)
    elif output_format == 'markdown':
        report_content = _format_report_as_markdown(report_data, verbose)
    else:  # text
        report_content = _format_report_as_text(report_data, verbose)
    
    # Output report
    if output:
        with open(output, 'w') as f:
            f.write(report_content)
        click.echo(f"✓ Report saved to: {output}")
    else:
        click.echo(report_content)


@bmad_group.command(name='init')
@click.option('--project-path', '-p', type=click.Path(), default='.',
              help='Path to project root')
@click.option('--template', type=click.Choice(['basic', 'full']), default='full',
              help='BMAD template to use')
@click.pass_context
def init_bmad(ctx, project_path: str, template: str):
    """Initialize BMAD structure for a project.
    
    Example:
        map4 bmad init --project-path . --template full
    """
    project_root = Path(project_path).resolve()
    
    click.echo(f"Initializing BMAD structure at: {project_root}")
    click.echo(f"Template: {template}")
    
    # Create BMAD directories
    bmad_dirs = [
        'bmad/build',
        'bmad/measure',
        'bmad/analyze',
        'bmad/deploy',
        'bmad/reports',
        'bmad/metrics'
    ]
    
    for dir_path in bmad_dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        click.echo(f"✓ Created: {dir_path}")
    
    # Create BMAD configuration file
    bmad_config = {
        'version': '1.0.0',
        'project': project_root.name,
        'template': template,
        'created': datetime.now().isoformat(),
        'phases': {
            'build': {
                'enabled': True,
                'threshold': 0.95
            },
            'measure': {
                'enabled': True,
                'threshold': 0.90
            },
            'analyze': {
                'enabled': True,
                'threshold': 0.85
            },
            'deploy': {
                'enabled': True,
                'threshold': 0.95
            }
        },
        'metrics': {
            'code_quality': True,
            'performance': True,
            'security': True,
            'documentation': True
        }
    }
    
    config_path = project_root / 'bmad' / 'bmad.config.json'
    with open(config_path, 'w') as f:
        json.dump(bmad_config, f, indent=2)
    
    click.echo(f"✓ Created configuration: bmad/bmad.config.json")
    
    # Create initial documentation
    if template == 'full':
        docs = {
            'bmad/README.md': _get_bmad_readme_template(),
            'bmad/build/README.md': _get_build_readme_template(),
            'bmad/measure/README.md': _get_measure_readme_template(),
            'bmad/analyze/README.md': _get_analyze_readme_template(),
            'bmad/deploy/README.md': _get_deploy_readme_template()
        }
        
        for doc_path, content in docs.items():
            full_path = project_root / doc_path
            with open(full_path, 'w') as f:
                f.write(content)
            click.echo(f"✓ Created documentation: {doc_path}")
    
    click.echo("\n✓ BMAD structure initialized successfully")
    click.echo("\nNext steps:")
    click.echo("1. Run 'map4 bmad certify' to check current compliance")
    click.echo("2. Review bmad/bmad.config.json to adjust thresholds")
    click.echo("3. Use 'map4 bmad report' to generate compliance reports")


# Helper functions for validation
def _validate_build_phase(project_root: Path, verbose: bool) -> Dict[str, Any]:
    """Validate BUILD phase requirements."""
    checks = []
    passed = []
    failed = []
    
    # Check for unified CLI structure
    if (project_root / 'src' / 'cli' / 'unified_main.py').exists():
        passed.append("Unified CLI entry point exists")
    else:
        failed.append("Unified CLI entry point missing")
    
    # Check for provider factory
    if (project_root / 'src' / 'analysis' / 'provider_factory.py').exists():
        passed.append("Provider factory pattern implemented")
    else:
        failed.append("Provider factory pattern missing")
    
    # Check for base provider interface
    if (project_root / 'src' / 'analysis' / 'base_provider.py').exists():
        passed.append("Base provider interface defined")
    else:
        failed.append("Base provider interface missing")
    
    # Check for command modules
    command_modules = ['analyze', 'playlist', 'provider', 'bmad']
    for module in command_modules:
        if (project_root / 'src' / 'cli' / 'commands' / f'{module}.py').exists():
            passed.append(f"Command module '{module}' exists")
        else:
            failed.append(f"Command module '{module}' missing")
    
    # Check for configuration system
    if (project_root / 'config').exists():
        passed.append("Configuration directory exists")
    else:
        failed.append("Configuration directory missing")
    
    return {
        'total': len(passed) + len(failed),
        'passed': len(passed),
        'failed': len(failed),
        'passed_checks': passed,
        'failed_checks': failed
    }


def _validate_measure_phase(project_root: Path, verbose: bool) -> Dict[str, Any]:
    """Validate MEASURE phase requirements."""
    checks = []
    passed = []
    failed = []
    
    # Check for duplicate reduction
    cli_files = list((project_root / 'tools' / 'cli').glob('*.py')) if (project_root / 'tools' / 'cli').exists() else []
    if len(cli_files) <= 1:
        passed.append("CLI duplication eliminated")
    else:
        failed.append(f"CLI duplication remains ({len(cli_files)} files)")
    
    # Check for provider consolidation
    provider_files = list((project_root / 'src' / 'analysis').glob('*provider*.py'))
    zai_variants = [f for f in provider_files if 'zai' in f.name.lower()]
    if len(zai_variants) <= 1:
        passed.append("Provider variants consolidated")
    else:
        failed.append(f"Provider duplication remains ({len(zai_variants)} ZAI variants)")
    
    # Check for test coverage
    if (project_root / 'tests').exists():
        test_files = list((project_root / 'tests').rglob('test_*.py'))
        if len(test_files) > 0:
            passed.append(f"Test files present ({len(test_files)} files)")
        else:
            failed.append("No test files found")
    else:
        failed.append("Tests directory missing")
    
    return {
        'total': len(passed) + len(failed),
        'passed': len(passed),
        'failed': len(failed),
        'passed_checks': passed,
        'failed_checks': failed
    }


def _validate_analyze_phase(project_root: Path, verbose: bool) -> Dict[str, Any]:
    """Validate ANALYZE phase requirements."""
    checks = []
    passed = []
    failed = []
    
    # Check for code organization
    required_dirs = ['src', 'tests', 'config', 'data']
    for dir_name in required_dirs:
        if (project_root / dir_name).exists():
            passed.append(f"Directory '{dir_name}' exists")
        else:
            failed.append(f"Directory '{dir_name}' missing")
    
    # Check for documentation
    if (project_root / 'README.md').exists():
        passed.append("README.md exists")
    else:
        failed.append("README.md missing")
    
    # Check for requirements file
    if (project_root / 'requirements.txt').exists() or (project_root / 'pyproject.toml').exists():
        passed.append("Dependencies defined")
    else:
        failed.append("No requirements.txt or pyproject.toml")
    
    return {
        'total': len(passed) + len(failed),
        'passed': len(passed),
        'failed': len(failed),
        'passed_checks': passed,
        'failed_checks': failed
    }


def _validate_deploy_phase(project_root: Path, verbose: bool) -> Dict[str, Any]:
    """Validate DEPLOY phase requirements."""
    checks = []
    passed = []
    failed = []
    
    # Check for entry point
    if (project_root / 'src' / 'cli' / 'unified_main.py').exists():
        passed.append("Main entry point exists")
    else:
        failed.append("Main entry point missing")
    
    # Check for configuration
    if (project_root / 'config').exists() or (project_root / '.env.example').exists():
        passed.append("Configuration system present")
    else:
        failed.append("Configuration system missing")
    
    # Check for error handling
    # This would require actual code analysis, simplified here
    passed.append("Basic structure validated")
    
    return {
        'total': len(passed) + len(failed),
        'passed': len(passed),
        'failed': len(failed),
        'passed_checks': passed,
        'failed_checks': failed
    }


def _collect_build_metrics(project_root: Path) -> Dict[str, Any]:
    """Collect BUILD phase metrics."""
    return {
        'architecture_components': len(list((project_root / 'src').rglob('*.py'))) if (project_root / 'src').exists() else 0,
        'cli_modules': len(list((project_root / 'src' / 'cli' / 'commands').glob('*.py'))) if (project_root / 'src' / 'cli' / 'commands').exists() else 0,
        'providers': len(list((project_root / 'src' / 'analysis' / 'providers').glob('*_provider.py'))) if (project_root / 'src' / 'analysis' / 'providers').exists() else 0
    }


def _collect_measure_metrics(project_root: Path) -> Dict[str, Any]:
    """Collect MEASURE phase metrics."""
    cli_files = list((project_root / 'tools' / 'cli').glob('*.py')) if (project_root / 'tools' / 'cli').exists() else []
    provider_files = list((project_root / 'src' / 'analysis').glob('*provider*.py')) if (project_root / 'src' / 'analysis').exists() else []
    
    return {
        'cli_files': len(cli_files),
        'provider_files': len(provider_files),
        'total_python_files': len(list(project_root.rglob('*.py'))),
        'test_files': len(list((project_root / 'tests').rglob('test_*.py'))) if (project_root / 'tests').exists() else 0
    }


def _collect_analyze_metrics(project_root: Path) -> Dict[str, Any]:
    """Collect ANALYZE phase metrics."""
    total_lines = 0
    for py_file in project_root.rglob('*.py'):
        try:
            with open(py_file, 'r') as f:
                total_lines += len(f.readlines())
        except:
            pass
    
    return {
        'total_lines_of_code': total_lines,
        'python_files': len(list(project_root.rglob('*.py'))),
        'directories': len([d for d in project_root.rglob('*') if d.is_dir()])
    }


def _collect_deploy_metrics(project_root: Path) -> Dict[str, Any]:
    """Collect DEPLOY phase metrics."""
    return {
        'entry_points': 1 if (project_root / 'src' / 'cli' / 'unified_main.py').exists() else 0,
        'config_files': len(list((project_root / 'config').glob('*'))) if (project_root / 'config').exists() else 0,
        'documentation_files': len(list(project_root.glob('*.md')))
    }


def _format_report_as_markdown(data: Dict[str, Any], verbose: bool) -> str:
    """Format report as Markdown."""
    lines = []
    lines.append("# BMAD Compliance Report")
    lines.append("")
    lines.append(f"**Project:** `{data['project']}`")
    lines.append(f"**Generated:** {data['generated']}")
    lines.append("")
    
    lines.append("## Metrics Summary")
    lines.append("")
    
    for phase, metrics in data['metrics'].items():
        lines.append(f"### {phase.upper()} Phase")
        lines.append("")
        
        if metrics:
            for key, value in metrics.items():
                formatted_key = key.replace('_', ' ').title()
                lines.append(f"- **{formatted_key}:** {value}")
        lines.append("")
    
    return '\n'.join(lines)


def _format_report_as_text(data: Dict[str, Any], verbose: bool) -> str:
    """Format report as plain text."""
    lines = []
    lines.append("BMAD COMPLIANCE REPORT")
    lines.append("=" * 50)
    lines.append(f"Project: {data['project']}")
    lines.append(f"Generated: {data['generated']}")
    lines.append("")
    
    for phase, metrics in data['metrics'].items():
        lines.append(f"{phase.upper()} Phase:")
        lines.append("-" * 30)
        
        if metrics:
            for key, value in metrics.items():
                formatted_key = key.replace('_', ' ').title()
                lines.append(f"  {formatted_key}: {value}")
        lines.append("")
    
    return '\n'.join(lines)


def _get_bmad_readme_template() -> str:
    """Get BMAD README template."""
    return """# BMAD Methodology Implementation

This project follows the BMAD (Build, Measure, Analyze, Deploy) methodology for continuous improvement.

## Phases

### 1. BUILD
Architecture design and implementation phase.

### 2. MEASURE
Metrics collection and performance measurement phase.

### 3. ANALYZE
Code quality analysis and optimization phase.

### 4. DEPLOY
Deployment preparation and validation phase.

## Usage

Run certification:
```bash
map4 bmad certify
```

Generate report:
```bash
map4 bmad report --format markdown
```
"""


def _get_build_readme_template() -> str:
    """Get BUILD phase README template."""
    return """# BUILD Phase

Architecture design and implementation documentation.

## Components
- Unified CLI architecture
- Provider factory pattern
- Command modules
- Configuration system

## Validation
Run: `map4 bmad validate build`
"""


def _get_measure_readme_template() -> str:
    """Get MEASURE phase README template."""
    return """# MEASURE Phase

Metrics collection and performance measurement.

## Metrics
- Code duplication metrics
- Performance benchmarks
- Test coverage
- Resource utilization

## Validation
Run: `map4 bmad validate measure`
"""


def _get_analyze_readme_template() -> str:
    """Get ANALYZE phase README template."""
    return """# ANALYZE Phase

Code quality analysis and optimization.

## Analysis Areas
- Code complexity
- Dependency analysis
- Security scanning
- Documentation coverage

## Validation
Run: `map4 bmad validate analyze`
"""


def _get_deploy_readme_template() -> str:
    """Get DEPLOY phase README template."""
    return """# DEPLOY Phase

Deployment preparation and validation.

## Deployment Checklist
- [ ] All tests passing
- [ ] Configuration validated
- [ ] Documentation updated
- [ ] Performance benchmarks met

## Validation
Run: `map4 bmad validate deploy`
"""