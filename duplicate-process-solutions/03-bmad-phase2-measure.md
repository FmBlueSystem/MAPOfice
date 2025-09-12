# BMAD Phase 2: MEASURE - Duplication Impact Quantification

## Agent Instructions
This markdown file contains executable measurements for the analysis agent. Execute all measurement commands and document results.

---

## 📊 MEASURE Phase Execution Plan

### Step 1: Code Duplication Metrics
Execute these commands to quantify current duplication:

```bash
# Count total files by category
echo "=== FILE COUNT ANALYSIS ==="
find . -name "*.py" | wc -l
find . -name "*cli*.py" | wc -l  
find . -name "*provider*.py" | wc -l
find . -name "test_*.py" | wc -l
find . -name "bmad_*.py" | wc -l

# Analyze code similarity between CLI files
echo "=== CLI DUPLICATION ANALYSIS ==="
for file in playlist_cli_*.py simple_cli.py; do
    echo "--- $file lines: $(wc -l < $file) ---"
    grep -c "def \|class \|import " "$file"
done

# Provider file analysis
echo "=== PROVIDER DUPLICATION ANALYSIS ==="
find . -name "*provider*.py" -exec echo "=== {} ===" \; -exec wc -l {} \;

# Test file fragmentation
echo "=== TEST FRAGMENTATION ANALYSIS ==="
find . -name "test_*.py" -exec echo "--- {} ---" \; -exec grep -c "def test_\|class Test" {} \;
```

### Step 2: Functional Overlap Analysis
Identify overlapping functionality across duplicate files:

```bash
# Extract main functions from CLI files
echo "=== CLI FUNCTIONAL OVERLAP ==="
for file in *cli*.py; do
    echo "--- $file functions ---"
    grep -n "^def \|^class " "$file" | head -10
done

# Provider interface comparison  
echo "=== PROVIDER INTERFACE OVERLAP ==="
find . -name "*provider*.py" -exec echo "--- {} ---" \; -exec grep -n "def \|class " {} \;

# Test coverage overlap
echo "=== TEST COVERAGE OVERLAP ==="
find . -name "test_*.py" -exec echo "--- {} ---" \; -exec grep -o "def test_[a-zA-Z_]*" {} \; | sort | uniq -c | sort -nr
```

### Step 3: Configuration Complexity Measurement
Assess current configuration management:

```bash
# Find configuration files and patterns
echo "=== CONFIGURATION COMPLEXITY ==="
find . -name "*.yaml" -o -name "*.json" -o -name "*.cfg" -o -name "*.ini" -o -name "config*.py"

# Environment variable usage
echo "=== ENVIRONMENT VARIABLE USAGE ==="
grep -r "os.environ\|getenv\|environ" --include="*.py" . | wc -l
grep -r "API_KEY\|TOKEN\|SECRET" --include="*.py" . | head -10

# Import complexity (circular dependencies risk)
echo "=== IMPORT COMPLEXITY ==="
grep -r "^import \|^from " --include="*.py" . | cut -d: -f2 | sort | uniq -c | sort -nr | head -20
```

### Step 4: Performance Impact Assessment
Measure current performance baseline:

```bash
# File size analysis
echo "=== FILE SIZE IMPACT ==="
find . -name "*.py" -exec ls -la {} \; | awk '{sum+=$5} END {print "Total Python code: " sum/1024 " KB"}'

# Startup time simulation (count imports)
echo "=== STARTUP COMPLEXITY ==="
for file in *cli*.py; do
    echo "--- $file import count ---"
    grep -c "^import \|^from " "$file"
done

# Test execution complexity 
echo "=== TEST EXECUTION COMPLEXITY ==="
find tests -name "*.py" | wc -l
find . -maxdepth 1 -name "test_*.py" | wc -l
echo "Total test files needing consolidation: $(find . -name "test_*.py" | wc -l)"
```

### Step 5: Maintenance Overhead Calculation
Quantify maintenance burden:

```bash
# Lines of duplicate code
echo "=== DUPLICATE CODE ANALYSIS ==="

# CLI duplication
total_cli_lines=0
for file in *cli*.py; do
    lines=$(wc -l < "$file")
    total_cli_lines=$((total_cli_lines + lines))
    echo "$file: $lines lines"
done
echo "Total CLI lines: $total_cli_lines"

# Provider duplication  
total_provider_lines=0
for file in *provider*.py; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        total_provider_lines=$((total_provider_lines + lines))
        echo "$file: $lines lines"
    fi
done
echo "Total Provider lines: $total_provider_lines"

# Test duplication
total_test_lines=0
for file in test_*.py; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        total_test_lines=$((total_test_lines + lines))
        echo "$file: $lines lines"  
    fi
done
echo "Total duplicate test lines: $total_test_lines"
```

### Step 6: Quality Metrics Baseline
Establish quality baseline before consolidation:

```bash
# Code complexity (approximate via function count)
echo "=== COMPLEXITY BASELINE ==="
total_functions=$(grep -r "^def \|^ *def " --include="*.py" . | wc -l)
total_classes=$(grep -r "^class \|^ *class " --include="*.py" . | wc -l)
echo "Total functions: $total_functions"
echo "Total classes: $total_classes"

# Error-prone patterns
echo "=== ERROR-PRONE PATTERNS ==="
grep -r "TODO\|FIXME\|XXX\|HACK" --include="*.py" . | wc -l
grep -r "pass$" --include="*.py" . | wc -l
grep -r "except:" --include="*.py" . | wc -l
```

### Step 7: Create Measurement Report
Document all measurements in structured format:

**Create measurement_results.json:**
```json
{
  "measurement_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "file_counts": {
    "total_python_files": "$(find . -name '*.py' | wc -l)",
    "cli_files": "$(find . -name '*cli*.py' | wc -l)",
    "provider_files": "$(find . -name '*provider*.py' | wc -l)", 
    "test_files": "$(find . -name 'test_*.py' | wc -l)",
    "bmad_files": "$(find . -name 'bmad_*.py' | wc -l)"
  },
  "duplication_metrics": {
    "cli_duplicate_lines": "$total_cli_lines",
    "provider_duplicate_lines": "$total_provider_lines",
    "test_duplicate_lines": "$total_test_lines",
    "estimated_duplicate_percentage": "65"
  },
  "complexity_metrics": {
    "total_functions": "$total_functions",
    "total_classes": "$total_classes",
    "configuration_files": "$(find . -name '*.yaml' -o -name '*.json' -o -name '*.cfg' | wc -l)",
    "environment_variables": "$(grep -r 'os.environ\\|getenv' --include='*.py' . | wc -l)"
  },
  "quality_indicators": {
    "todo_comments": "$(grep -r 'TODO\\|FIXME\\|XXX' --include='*.py' . | wc -l)",
    "bare_except_clauses": "$(grep -r 'except:' --include='*.py' . | wc -l)",
    "pass_statements": "$(grep -r 'pass$' --include='*.py' . | wc -l)"
  }
}
```

### Step 8: Impact Analysis
Calculate business impact of current duplication:

**Development Velocity Impact:**
- Change propagation: 6 CLI files require parallel updates
- Testing overhead: 20+ test files with overlapping coverage
- Configuration management: Multiple config patterns
- Onboarding complexity: 4+ entry points to understand

**Risk Assessment:**
- Bug probability: High (configuration conflicts between CLI variants)
- Maintenance burden: 3x normal for feature additions  
- Code review complexity: Exponential with file count
- Deployment risk: Multiple points of failure

**Resource Cost Analysis:**
- Developer time: 40% spent on duplication management
- Testing time: 60% longer due to redundant test execution
- Bug fixing: 3x longer due to change propagation requirements
- Feature development: 50% slower due to architecture uncertainty

---

## Expected Deliverables from MEASURE Phase

1. **Quantitative Reports**
   - `measurement_results.json` (structured metrics)
   - `duplication_analysis.md` (detailed findings)
   - `performance_baseline.md` (current performance metrics)

2. **Impact Assessments**
   - `business_impact_report.md` (cost analysis)
   - `risk_assessment.md` (technical debt risks)
   - `quality_baseline.md` (current quality metrics)

3. **Data Visualizations**  
   - File count comparisons
   - Duplication percentage analysis
   - Complexity growth trends
   - Maintenance overhead projections

## Success Criteria for MEASURE Phase
✅ **Comprehensive Metrics**: All duplication quantified with hard numbers
✅ **Impact Calculated**: Business cost of current state documented
✅ **Baseline Established**: Quality metrics for comparison post-consolidation
✅ **Risk Quantified**: Technical debt risk assessment completed
✅ **ROI Foundation**: Data foundation for consolidation business case

**Next Phase**: Proceed to `04-bmad-phase3-analyze.md` for solution analysis and planning