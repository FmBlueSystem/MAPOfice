# MAP4 Deployment Validation Checklist

## Overview
This comprehensive checklist ensures reproduced MAP4 applications are production-ready, secure, and maintainable. Each section includes validation criteria, verification procedures, and automated checks.

## 1. Pre-Deployment Requirements

### Environment Readiness

#### System Requirements Validation
```bash
#!/bin/bash
# System requirements check script

echo "MAP4 Deployment Validation"
echo "=========================="

# Python version check
PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.8"

if (( $(echo "$PYTHON_VERSION >= $REQUIRED_VERSION" | bc -l) )); then
    echo "✅ Python version: $PYTHON_VERSION (Required: >= $REQUIRED_VERSION)"
else
    echo "❌ Python version: $PYTHON_VERSION (Required: >= $REQUIRED_VERSION)"
    exit 1
fi

# Memory check
TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
REQUIRED_MEM=4096

if [ $TOTAL_MEM -ge $REQUIRED_MEM ]; then
    echo "✅ Memory: ${TOTAL_MEM}MB (Required: >= ${REQUIRED_MEM}MB)"
else
    echo "❌ Memory: ${TOTAL_MEM}MB (Required: >= ${REQUIRED_MEM}MB)"
fi

# Disk space check
AVAILABLE_SPACE=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
REQUIRED_SPACE=10

if [ $AVAILABLE_SPACE -ge $REQUIRED_SPACE ]; then
    echo "✅ Disk space: ${AVAILABLE_SPACE}GB (Required: >= ${REQUIRED_SPACE}GB)"
else
    echo "❌ Disk space: ${AVAILABLE_SPACE}GB (Required: >= ${REQUIRED_SPACE}GB)"
fi

# Audio libraries check
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg installed"
else
    echo "❌ FFmpeg not found"
fi
```

**Checklist:**
- [ ] Python 3.8+ installed
- [ ] Minimum 4GB RAM available
- [ ] Minimum 10GB disk space
- [ ] FFmpeg installed
- [ ] Audio codecs available
- [ ] Database engine installed (SQLite/PostgreSQL)

### Dependency Verification

#### Python Package Validation
```python
#!/usr/bin/env python3
"""
Dependency verification script
"""

import pkg_resources
import sys

REQUIRED_PACKAGES = {
    'librosa': '0.10.1',
    'sqlalchemy': '2.0.23',
    'PyQt6': '6.0.0',
    'click': '8.1.7',
    'numpy': '1.20.0',
    'requests': '2.28.0'
}

def check_dependencies():
    """Check all required dependencies are installed"""
    missing = []
    outdated = []
    
    for package, min_version in REQUIRED_PACKAGES.items():
        try:
            installed = pkg_resources.get_distribution(package)
            if pkg_resources.parse_version(installed.version) < pkg_resources.parse_version(min_version):
                outdated.append(f"{package} ({installed.version} < {min_version})")
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    if missing:
        print("❌ Missing packages:")
        for pkg in missing:
            print(f"   - {pkg}")
    
    if outdated:
        print("⚠️  Outdated packages:")
        for pkg in outdated:
            print(f"   - {pkg}")
    
    if not missing and not outdated:
        print("✅ All dependencies satisfied")
        return True
    
    return False

if __name__ == '__main__':
    success = check_dependencies()
    sys.exit(0 if success else 1)
```

**Checklist:**
- [ ] All required packages installed
- [ ] Package versions meet minimum requirements
- [ ] No conflicting dependencies
- [ ] Virtual environment configured
- [ ] Requirements.txt up to date

## 2. Configuration Validation

### Application Configuration

#### Configuration File Validation
```python
#!/usr/bin/env python3
"""
Configuration validation script
"""

import yaml
import json
import os
from pathlib import Path

class ConfigValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_config_file(self, config_path):
        """Validate configuration file"""
        if not Path(config_path).exists():
            self.errors.append(f"Config file not found: {config_path}")
            return False
        
        try:
            with open(config_path) as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                elif config_path.endswith('.json'):
                    config = json.load(f)
                else:
                    self.errors.append("Unsupported config format")
                    return False
            
            # Validate required sections
            required_sections = ['audio', 'database', 'analysis', 'providers']
            for section in required_sections:
                if section not in config:
                    self.errors.append(f"Missing config section: {section}")
            
            # Validate audio settings
            if 'audio' in config:
                if config['audio'].get('sample_rate', 0) < 16000:
                    self.warnings.append("Low sample rate may affect quality")
            
            # Validate database settings
            if 'database' in config:
                if not config['database'].get('url'):
                    self.errors.append("Database URL not configured")
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Config parse error: {e}")
            return False
    
    def validate_environment_variables(self):
        """Validate environment variables"""
        required_env_vars = []
        optional_env_vars = [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'GEMINI_API_KEY'
        ]
        
        for var in required_env_vars:
            if not os.getenv(var):
                self.errors.append(f"Required env var not set: {var}")
        
        api_keys_found = 0
        for var in optional_env_vars:
            if os.getenv(var):
                api_keys_found += 1
        
        if api_keys_found == 0:
            self.warnings.append("No LLM API keys configured")
        
        return len(self.errors) == 0
    
    def generate_report(self):
        """Generate validation report"""
        print("\nConfiguration Validation Report")
        print("="*40)
        
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ Configuration valid")
        
        return len(self.errors) == 0

if __name__ == '__main__':
    validator = ConfigValidator()
    validator.validate_config_file('config.yaml')
    validator.validate_environment_variables()
    success = validator.generate_report()
    sys.exit(0 if success else 1)
```

**Checklist:**
- [ ] Configuration file exists and is valid
- [ ] All required settings present
- [ ] Database connection string configured
- [ ] API keys securely stored
- [ ] Logging configuration set
- [ ] Resource limits defined

## 3. Security Compliance

### Security Validation

#### Security Audit Script
```python
#!/usr/bin/env python3
"""
Security compliance validation
"""

import os
import stat
import subprocess
from pathlib import Path

class SecurityAuditor:
    def __init__(self):
        self.issues = []
        self.critical = []
    
    def check_file_permissions(self, directory='.'):
        """Check for insecure file permissions"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = Path(root) / file
                mode = filepath.stat().st_mode
                
                # Check for world-writable files
                if mode & stat.S_IWOTH:
                    self.issues.append(f"World-writable file: {filepath}")
                
                # Check for API key files
                if 'key' in file.lower() or 'secret' in file.lower():
                    if mode & stat.S_IROTH:
                        self.critical.append(f"Sensitive file readable by others: {filepath}")
    
    def check_hardcoded_secrets(self):
        """Scan for hardcoded secrets"""
        patterns = [
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']'
        ]
        
        try:
            for pattern in patterns:
                result = subprocess.run(
                    f'grep -r -E "{pattern}" --include="*.py" .',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    self.critical.append(f"Potential hardcoded secret found")
        except Exception as e:
            self.issues.append(f"Secret scan failed: {e}")
    
    def check_dependency_vulnerabilities(self):
        """Check for known vulnerabilities in dependencies"""
        try:
            result = subprocess.run(
                'pip-audit --format json',
                shell=True,
                capture_output=True,
                text=True
            )
            
            import json
            vulnerabilities = json.loads(result.stdout)
            
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'UNKNOWN')
                if severity in ['CRITICAL', 'HIGH']:
                    self.critical.append(f"{vuln['name']}: {vuln['description']}")
                else:
                    self.issues.append(f"{vuln['name']}: {vuln['description']}")
        except Exception as e:
            self.issues.append(f"Vulnerability scan failed: {e}")
    
    def check_api_security(self):
        """Check API security configurations"""
        checks = {
            'HTTPS enforcement': self._check_https_enforcement(),
            'Rate limiting': self._check_rate_limiting(),
            'Input validation': self._check_input_validation(),
            'Authentication': self._check_authentication()
        }
        
        for check, passed in checks.items():
            if not passed:
                self.issues.append(f"Failed security check: {check}")
    
    def _check_https_enforcement(self):
        """Check if HTTPS is enforced"""
        # Check for HTTP URLs in code
        result = subprocess.run(
            'grep -r "http://" --include="*.py" . | grep -v localhost',
            shell=True,
            capture_output=True
        )
        return result.returncode != 0
    
    def _check_rate_limiting(self):
        """Check if rate limiting is implemented"""
        result = subprocess.run(
            'grep -r "rate_limit\\|RateLimit" --include="*.py" .',
            shell=True,
            capture_output=True
        )
        return result.returncode == 0
    
    def _check_input_validation(self):
        """Check if input validation is implemented"""
        result = subprocess.run(
            'grep -r "validate\\|sanitize" --include="*.py" .',
            shell=True,
            capture_output=True
        )
        return result.returncode == 0
    
    def _check_authentication(self):
        """Check if authentication is properly implemented"""
        result = subprocess.run(
            'grep -r "authenticate\\|api_key\\|token" --include="*.py" .',
            shell=True,
            capture_output=True
        )
        return result.returncode == 0
    
    def generate_report(self):
        """Generate security audit report"""
        print("\nSecurity Audit Report")
        print("="*40)
        
        if self.critical:
            print("\n🚨 CRITICAL Issues:")
            for issue in self.critical:
                print(f"   - {issue}")
        
        if self.issues:
            print("\n⚠️  Security Issues:")
            for issue in self.issues:
                print(f"   - {issue}")
        
        if not self.critical and not self.issues:
            print("✅ No security issues found")
        
        return len(self.critical) == 0

if __name__ == '__main__':
    auditor = SecurityAuditor()
    auditor.check_file_permissions()
    auditor.check_hardcoded_secrets()
    auditor.check_dependency_vulnerabilities()
    auditor.check_api_security()
    success = auditor.generate_report()
    sys.exit(0 if success else 1)
```

**Security Checklist:**
- [ ] No hardcoded secrets or API keys
- [ ] File permissions properly set
- [ ] No known vulnerabilities in dependencies
- [ ] HTTPS enforced for API calls
- [ ] Input validation implemented
- [ ] Rate limiting configured
- [ ] Authentication mechanisms in place
- [ ] Logging sanitized (no sensitive data)
- [ ] SQL injection prevention implemented
- [ ] Path traversal prevention in place

## 4. Performance Readiness

### Performance Validation

```python
#!/usr/bin/env python3
"""
Performance readiness validation
"""

import time
import psutil
import concurrent.futures
from pathlib import Path

class PerformanceValidator:
    def __init__(self):
        self.results = {}
    
    def validate_startup_time(self):
        """Validate application startup time"""
        start = time.time()
        
        # Import main modules
        import map4.core
        import map4.analysis
        import map4.database
        
        startup_time = time.time() - start
        
        self.results['startup_time'] = {
            'value': startup_time,
            'passed': startup_time < 5.0,
            'threshold': 5.0
        }
        
        return startup_time < 5.0
    
    def validate_resource_usage(self):
        """Validate resource usage"""
        process = psutil.Process()
        
        # Check memory usage
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.results['memory_usage'] = {
            'value': memory_mb,
            'passed': memory_mb < 500,
            'threshold': 500
        }
        
        # Check CPU usage
        cpu_percent = process.cpu_percent(interval=1)
        self.results['cpu_usage'] = {
            'value': cpu_percent,
            'passed': cpu_percent < 50,
            'threshold': 50
        }
        
        return memory_mb < 500 and cpu_percent < 50
    
    def validate_concurrent_processing(self):
        """Validate concurrent processing capability"""
        def dummy_task(n):
            time.sleep(0.1)
            return n * 2
        
        start = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(dummy_task, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        execution_time = time.time() - start
        
        self.results['concurrent_processing'] = {
            'value': execution_time,
            'passed': execution_time < 1.0,
            'threshold': 1.0
        }
        
        return execution_time < 1.0
    
    def validate_database_performance(self):
        """Validate database performance"""
        from map4.database import get_session
        
        # Test connection time
        start = time.time()
        with get_session() as session:
            pass
        connection_time = time.time() - start
        
        self.results['db_connection'] = {
            'value': connection_time,
            'passed': connection_time < 0.1,
            'threshold': 0.1
        }
        
        return connection_time < 0.1
    
    def generate_report(self):
        """Generate performance validation report"""
        print("\nPerformance Validation Report")
        print("="*40)
        
        all_passed = True
        
        for test, result in self.results.items():
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {test}: {result['value']:.3f} (threshold: {result['threshold']})")
            all_passed = all_passed and result['passed']
        
        return all_passed

if __name__ == '__main__':
    validator = PerformanceValidator()
    validator.validate_startup_time()
    validator.validate_resource_usage()
    validator.validate_concurrent_processing()
    validator.validate_database_performance()
    success = validator.generate_report()
    sys.exit(0 if success else 1)
```

**Performance Checklist:**
- [ ] Startup time < 5 seconds
- [ ] Memory usage < 500MB idle
- [ ] CPU usage < 50% idle
- [ ] Database connection < 100ms
- [ ] Concurrent processing functional
- [ ] No memory leaks detected
- [ ] Cache mechanisms working
- [ ] Resource limits configured

## 5. Database Readiness

### Database Validation

```bash
#!/bin/bash
# Database validation script

echo "Database Validation"
echo "=================="

# Check database exists
if [ -f "map4.db" ]; then
    echo "✅ Database file exists"
else
    echo "❌ Database file not found"
    exit 1
fi

# Check database size
DB_SIZE=$(du -m map4.db | cut -f1)
echo "ℹ️  Database size: ${DB_SIZE}MB"

# Verify schema
python3 << EOF
from map4.database import engine, Base
from sqlalchemy import inspect

inspector = inspect(engine)
required_tables = ['tracks', 'analyses', 'hamms_vectors', 'ai_analyses']
missing_tables = []

for table in required_tables:
    if table not in inspector.get_table_names():
        missing_tables.append(table)

if missing_tables:
    print(f"❌ Missing tables: {missing_tables}")
    exit(1)
else:
    print("✅ All required tables present")

# Check indexes
for table in required_tables:
    indexes = inspector.get_indexes(table)
    if indexes:
        print(f"✅ Table '{table}' has {len(indexes)} indexes")
    else:
        print(f"⚠️  Table '{table}' has no indexes")
EOF

# Test database backup
cp map4.db map4.db.backup
if [ $? -eq 0 ]; then
    echo "✅ Database backup successful"
    rm map4.db.backup
else
    echo "❌ Database backup failed"
fi
```

**Database Checklist:**
- [ ] Database schema created
- [ ] All tables present
- [ ] Indexes created for performance
- [ ] Foreign key constraints configured
- [ ] Backup mechanism tested
- [ ] Migration scripts ready
- [ ] Connection pool configured
- [ ] Transaction management tested

## 6. Monitoring and Logging

### Logging Configuration Validation

```python
#!/usr/bin/env python3
"""
Logging and monitoring validation
"""

import logging
import os
from pathlib import Path

def validate_logging():
    """Validate logging configuration"""
    checks = {
        'log_directory': Path('logs').exists(),
        'log_rotation': check_log_rotation(),
        'log_levels': check_log_levels(),
        'sensitive_data': check_sensitive_data_logging()
    }
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    return all(checks.values())

def check_log_rotation():
    """Check if log rotation is configured"""
    # Check for rotation configuration
    config_file = Path('logging.conf')
    if config_file.exists():
        with open(config_file) as f:
            return 'RotatingFileHandler' in f.read()
    return False

def check_log_levels():
    """Check if appropriate log levels are set"""
    logger = logging.getLogger('map4')
    return logger.level <= logging.INFO

def check_sensitive_data_logging():
    """Check that sensitive data is not logged"""
    # Scan recent logs for sensitive patterns
    log_files = Path('logs').glob('*.log')
    sensitive_patterns = ['api_key', 'password', 'secret', 'token']
    
    for log_file in log_files:
        with open(log_file) as f:
            content = f.read().lower()
            for pattern in sensitive_patterns:
                if pattern in content:
                    return False
    return True

if __name__ == '__main__':
    success = validate_logging()
    sys.exit(0 if success else 1)
```

**Monitoring Checklist:**
- [ ] Logging configured and working
- [ ] Log rotation implemented
- [ ] Appropriate log levels set
- [ ] No sensitive data in logs
- [ ] Error alerting configured
- [ ] Performance metrics collected
- [ ] Health check endpoint available
- [ ] Monitoring dashboard accessible

## 7. Documentation Completeness

### Documentation Validation

```bash
#!/bin/bash
# Documentation validation script

echo "Documentation Validation"
echo "======================="

# Check for essential documentation files
REQUIRED_DOCS=(
    "README.md"
    "INSTALL.md"
    "CONFIGURATION.md"
    "API.md"
    "TROUBLESHOOTING.md"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "docs/$doc" ]; then
        echo "✅ $doc present"
    else
        echo "❌ $doc missing"
    fi
done

# Check API documentation generation
if command -v sphinx-build &> /dev/null; then
    echo "✅ Sphinx installed for API docs"
    
    # Try to build docs
    cd docs
    sphinx-build -b html . _build/html > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ API documentation builds successfully"
    else
        echo "❌ API documentation build failed"
    fi
    cd ..
else
    echo "⚠️  Sphinx not installed"
fi

# Check for inline documentation
PYTHON_FILES=$(find map4 -name "*.py" | wc -l)
DOCUMENTED=$(grep -l '"""' map4/**/*.py | wc -l)
PERCENTAGE=$((DOCUMENTED * 100 / PYTHON_FILES))

echo "ℹ️  Python files with docstrings: $PERCENTAGE%"
```

**Documentation Checklist:**
- [ ] README with installation instructions
- [ ] Configuration documentation
- [ ] API reference documentation
- [ ] User manual/guide
- [ ] Troubleshooting guide
- [ ] Deployment instructions
- [ ] Code comments adequate
- [ ] Docstrings for all public APIs

## 8. Final Deployment Validation

### Master Deployment Validator

```python
#!/usr/bin/env python3
"""
Master deployment validation script
Runs all validation checks and generates final report
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

class DeploymentValidator:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
    
    def run_validation(self, name, script):
        """Run a validation script"""
        print(f"\nRunning {name}...")
        result = subprocess.run(
            f'python3 {script}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        self.results[name] = {
            'passed': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr
        }
        
        return result.returncode == 0
    
    def run_all_validations(self):
        """Run all deployment validations"""
        validations = [
            ('System Requirements', 'validate_system.py'),
            ('Dependencies', 'validate_dependencies.py'),
            ('Configuration', 'validate_config.py'),
            ('Security', 'validate_security.py'),
            ('Performance', 'validate_performance.py'),
            ('Database', 'validate_database.py'),
            ('Logging', 'validate_logging.py'),
            ('Documentation', 'validate_docs.py')
        ]
        
        passed_count = 0
        failed_count = 0
        
        for name, script in validations:
            if self.run_validation(name, script):
                passed_count += 1
                print(f"✅ {name} validation passed")
            else:
                failed_count += 1
                print(f"❌ {name} validation failed")
        
        self.results['summary'] = {
            'total': len(validations),
            'passed': passed_count,
            'failed': failed_count,
            'timestamp': datetime.now().isoformat(),
            'duration': (datetime.now() - self.start_time).total_seconds()
        }
        
        return failed_count == 0
    
    def generate_report(self):
        """Generate deployment validation report"""
        report_path = Path('deployment_validation_report.json')
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("\n" + "="*50)
        print("DEPLOYMENT VALIDATION SUMMARY")
        print("="*50)
        print(f"Total Checks: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        print(f"Duration: {self.results['summary']['duration']:.2f} seconds")
        print(f"\nDetailed report: {report_path}")
        
        # Generate deployment decision
        if self.results['summary']['failed'] == 0:
            print("\n🚀 DEPLOYMENT APPROVED - All validations passed!")
            return True
        else:
            print("\n🛑 DEPLOYMENT BLOCKED - Fix validation failures first!")
            return False

if __name__ == '__main__':
    validator = DeploymentValidator()
    all_passed = validator.run_all_validations()
    deployment_approved = validator.generate_report()
    
    sys.exit(0 if deployment_approved else 1)
```

## Final Deployment Checklist

### Critical Requirements (Must Pass)
- [ ] All system requirements met
- [ ] All dependencies installed and correct versions
- [ ] Configuration valid and complete
- [ ] No critical security issues
- [ ] Database schema correct and indexed
- [ ] Core functionality tests pass
- [ ] API authentication working

### Important Requirements (Should Pass)
- [ ] Performance benchmarks met
- [ ] Logging properly configured
- [ ] Documentation complete
- [ ] Backup procedures tested
- [ ] Monitoring configured
- [ ] Error handling comprehensive

### Nice to Have (Recommended)
- [ ] Automated deployment scripts
- [ ] Rollback procedures documented
- [ ] Performance profiling complete
- [ ] Load testing performed
- [ ] Security audit passed
- [ ] User acceptance testing complete

## Deployment Decision Matrix

| Category | Status | Required | Decision |
|----------|--------|----------|----------|
| System Requirements | ✅/❌ | Critical | Block if failed |
| Dependencies | ✅/❌ | Critical | Block if failed |
| Security | ✅/❌ | Critical | Block if critical issues |
| Configuration | ✅/❌ | Critical | Block if failed |
| Database | ✅/❌ | Critical | Block if failed |
| Performance | ✅/❌ | Important | Warn if failed |
| Documentation | ✅/❌ | Important | Warn if incomplete |
| Monitoring | ✅/❌ | Recommended | Note if missing |

## Post-Deployment Validation

After deployment, validate:
1. Application starts successfully
2. Health check endpoint responds
3. Core features functional
4. Logs being generated
5. Monitoring active
6. Backup scheduled
7. Users can access system
8. Performance acceptable

This comprehensive deployment validation checklist ensures MAP4 reproductions are production-ready and maintainable.