# BMAD FASE 3: ANALYZE - Análisis Profundo y Plan de Mejoras

## Instrucciones para el Agente

### Objetivo
Realizar análisis profundo de las métricas capturadas, identificar root causes de problemas y crear un plan de mejoras específico y priorizado.

### Tareas a Ejecutar

#### 1. Cargar y Analizar Resultados de Medición
```bash
# Activar entorno virtual
source .venv/bin/activate

# Análisis profundo de los resultados
echo "🔍 Iniciando análisis profundo de resultados..."

python -c "
import json
import os
import statistics
from datetime import datetime

# Cargar datos de medición
try:
    with open('measure_phase_output.json', 'r') as f:
        measure_data = json.load(f)
    print('✅ Datos de medición cargados')
except FileNotFoundError:
    print('❌ No se encontraron datos de medición. Ejecutar MEASURE primero.')
    exit(1)

print(f'\\n📊 ANÁLISIS PROFUNDO - {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}')
print('=' * 60)

# Análisis de estado de certificación
cert_status = measure_data.get('certification_status', False)
final_score = measure_data.get('final_quality_score', 0)

print(f'🎯 Estado de Certificación: {\"✅ APROBADO\" if cert_status else \"❌ REPROBADO\"}')
print(f'📈 Puntuación Final: {final_score:.2%}')

# Análisis de métricas detalladas
if 'detailed_metrics' in measure_data:
    metrics = measure_data['detailed_metrics']
    print(f'\\n📏 MÉTRICAS DETALLADAS:')
    
    bpm_adherence = metrics.get('bmp_adherence', 0)
    energy_flow = metrics.get('energy_flow', 0) 
    genre_coherence = metrics.get('genre_coherence', 0)
    data_completeness = metrics.get('data_completeness', 0)
    
    print(f'  🎵 Adherencia BPM: {bmp_adherence:.2%} {\"> 90%\" if bmp_adherence >= 0.9 else \"< 90% ⚠️\"}')
    print(f'  ⚡ Flujo Energético: {energy_flow:.2%} {\"> 70%\" if energy_flow >= 0.7 else \"< 70% ⚠️\"}')
    print(f'  🎭 Coherencia Género: {genre_coherence:.2%} {\"> 70%\" if genre_coherence >= 0.7 else \"< 70% ⚠️\"}')
    print(f'  📊 Completitud Datos: {data_completeness:.2%} {\"> 85%\" if data_completeness >= 0.85 else \"< 85% ⚠️\"}')
    
    # Identificar métricas críticas
    critical_metrics = []
    if bmp_adherence < 0.9:
        critical_metrics.append(('Adherencia BPM', bmp_adherence, 0.9))
    if energy_flow < 0.7:
        critical_metrics.append(('Flujo Energético', energy_flow, 0.7))
    if genre_coherence < 0.7:
        critical_metrics.append(('Coherencia Género', genre_coherence, 0.7))
    if data_completeness < 0.85:
        critical_metrics.append(('Completitud Datos', data_completeness, 0.85))
    
    if critical_metrics:
        print(f'\\n🚨 MÉTRICAS CRÍTICAS ({len(critical_metrics)}):')
        for metric_name, current_value, required_value in critical_metrics:
            gap = required_value - current_value
            print(f'  - {metric_name}: {current_value:.2%} (brecha: {gap:.2%})')
    else:
        print(f'\\n✅ Todas las métricas cumplen los criterios mínimos')

# Análisis de issues críticos
critical_issues = measure_data.get('critical_issues', [])
print(f'\\n🔥 ISSUES CRÍTICOS ({len(critical_issues)}):')
if critical_issues:
    for i, issue in enumerate(critical_issues, 1):
        print(f'  {i}. {issue}')
else:
    print('  ✅ No hay issues críticos identificados')

# Análisis de oportunidades de mejora
improvements = measure_data.get('improvement_opportunities', [])
print(f'\\n⚡ OPORTUNIDADES DE MEJORA ({len(improvements)}):')
if improvements:
    for i, improvement in enumerate(improvements, 1):
        print(f'  {i}. {improvement}')
else:
    print('  ✅ No hay oportunidades de mejora identificadas')

print('\\n✅ Análisis profundo completado')
"
```

#### 2. Identificar Root Causes y Prioridades
```bash
echo "🎯 Identificando root causes y priorizando mejoras..."

python -c "
import json

# Cargar datos
with open('measure_phase_output.json', 'r') as f:
    measure_data = json.load(f)

# Análisis de root causes basado en métricas
root_causes = []
improvement_priorities = []

metrics = measure_data.get('detailed_metrics', {})
critical_issues = measure_data.get('critical_issues', [])

# Root cause analysis
if metrics.get('bmp_adherence', 1) < 0.9:
    root_causes.append({
        'issue': 'Violaciones de tolerancia BPM',
        'root_cause': 'Algoritmo de filtrado BPM insuficiente o datos BPM faltantes',
        'impact': 'ALTO',
        'urgency': 'CRÍTICO'
    })

if metrics.get('data_completeness', 1) < 0.85:
    root_causes.append({
        'issue': 'Datos incompletos en tracks',
        'root_cause': 'Procesamiento de audio incompleto o archivos corruptos',
        'impact': 'ALTO', 
        'urgency': 'CRÍTICO'
    })

if metrics.get('energy_flow', 1) < 0.7:
    root_causes.append({
        'issue': 'Transiciones energéticas abruptas',
        'root_cause': 'Falta de algoritmo de suavizado de transiciones',
        'impact': 'MEDIO',
        'urgency': 'ALTO'
    })

if metrics.get('genre_coherence', 1) < 0.7:
    root_causes.append({
        'issue': 'Mezcla incoherente de géneros',
        'root_cause': 'Ponderación de género insuficiente en selección',
        'impact': 'MEDIO',
        'urgency': 'MEDIO'
    })

print('🔍 ROOT CAUSE ANALYSIS:')
print('=' * 40)

for i, cause in enumerate(root_causes, 1):
    print(f'{i}. {cause[\"issue\"]}')
    print(f'   Root Cause: {cause[\"root_cause\"]}')
    print(f'   Impacto: {cause[\"impact\"]} | Urgencia: {cause[\"urgency\"]}\\n')

# Priorización basada en impacto y urgencia
priority_matrix = {
    ('ALTO', 'CRÍTICO'): 'P1 - CRÍTICO',
    ('ALTO', 'ALTO'): 'P2 - ALTO', 
    ('MEDIO', 'CRÍTICO'): 'P2 - ALTO',
    ('MEDIO', 'ALTO'): 'P3 - MEDIO',
    ('MEDIO', 'MEDIO'): 'P4 - BAJO'
}

prioritized_causes = []
for cause in root_causes:
    priority = priority_matrix.get((cause['impact'], cause['urgency']), 'P4 - BAJO')
    prioritized_causes.append({
        **cause,
        'priority': priority
    })

# Ordenar por prioridad
priority_order = {'P1 - CRÍTICO': 1, 'P2 - ALTO': 2, 'P3 - MEDIO': 3, 'P4 - BAJO': 4}
prioritized_causes.sort(key=lambda x: priority_order.get(x['priority'], 5))

print('📋 PRIORIZACIÓN DE MEJORAS:')
print('=' * 30)

for cause in prioritized_causes:
    print(f'{cause[\"priority\"]}: {cause[\"issue\"]}')

# Guardar análisis
analysis_result = {
    'timestamp': measure_data.get('measurement_timestamp'),
    'root_causes': root_causes,
    'prioritized_improvements': prioritized_causes,
    'certification_gap_analysis': {
        'current_score': measure_data.get('final_quality_score', 0),
        'target_score': 0.8,
        'gap': max(0, 0.8 - measure_data.get('final_quality_score', 0))
    }
}

with open('analyze_phase_output.json', 'w') as f:
    json.dump(analysis_result, f, indent=2)

print('\\n✅ Análisis de root causes guardado en: analyze_phase_output.json')
"
```

#### 3. Crear Plan de Mejoras Específico
```bash
echo "📋 Creando plan de mejoras específico..."

python -c "
import json
from datetime import datetime, timedelta

# Cargar análisis
with open('analyze_phase_output.json', 'r') as f:
    analysis = json.load(f)

# Crear plan de mejoras detallado
improvement_plan = {
    'plan_version': '1.0',
    'created_date': datetime.now().isoformat(),
    'target_completion': (datetime.now() + timedelta(days=7)).isoformat(),
    'current_score': analysis['certification_gap_analysis']['current_score'],
    'target_score': analysis['certification_gap_analysis']['target_score'],
    'improvements': []
}

# Mapear mejoras específicas por root cause
improvement_mapping = {
    'Violaciones de tolerancia BPM': {
        'solution': 'Mejorar algoritmo de filtrado BPM',
        'implementation': [
            'Implementar validación estricta de BPM antes de selección',
            'Agregar lógica de pre-filtrado por rangos BPM',
            'Mejorar cálculo de tolerancia con margenes dinámicos'
        ],
        'estimated_effort': '2-3 días',
        'expected_impact': '+15% en adherencia BPM'
    },
    'Datos incompletos en tracks': {
        'solution': 'Mejorar pipeline de procesamiento de datos',
        'implementation': [
            'Implementar validación de completitud pre-generación',
            'Agregar reprocesamiento automático de tracks incompletos',
            'Crear fallbacks para datos faltantes'
        ],
        'estimated_effort': '3-4 días',
        'expected_impact': '+20% en completitud de datos'
    },
    'Transiciones energéticas abruptas': {
        'solution': 'Implementar algoritmo de suavizado energético',
        'implementation': [
            'Desarrollar función de scoring de transiciones',
            'Implementar ordenamiento por suavidad energética',
            'Agregar penalización por cambios abruptos'
        ],
        'estimated_effort': '2 días',
        'expected_impact': '+25% en flujo energético'
    },
    'Mezcla incoherente de géneros': {
        'solution': 'Mejorar ponderación de géneros',
        'implementation': [
            'Implementar clustering por género',
            'Agregar scoring de coherencia genérica',
            'Configurar pesos por importancia de género'
        ],
        'estimated_effort': '1-2 días',
        'expected_impact': '+30% en coherencia de género'
    }
}

# Crear mejoras priorizadas
for cause in analysis['prioritized_improvements']:
    issue = cause['issue']
    if issue in improvement_mapping:
        mapping = improvement_mapping[issue]
        
        improvement = {
            'priority': cause['priority'],
            'issue': issue,
            'root_cause': cause['root_cause'],
            'solution': mapping['solution'],
            'implementation_steps': mapping['implementation'],
            'estimated_effort': mapping['estimated_effort'],
            'expected_impact': mapping['expected_impact'],
            'assigned_to': 'Development Team',
            'status': 'Planned'
        }
        
        improvement_plan['improvements'].append(improvement)

# Guardar plan
with open('improvement_plan.json', 'w') as f:
    json.dump(improvement_plan, f, indent=2)

print('📋 PLAN DE MEJORAS CREADO')
print('=' * 25)

for improvement in improvement_plan['improvements']:
    print(f'{improvement[\"priority\"]}: {improvement[\"solution\"]}')
    print(f'  Esfuerzo: {improvement[\"estimated_effort\"]}')
    print(f'  Impacto: {improvement[\"expected_impact\"]}\\n')

print(f'✅ Plan detallado guardado en: improvement_plan.json')
"
```

#### 4. Generar Reporte de Análisis Completo
```bash
echo "📊 Generando reporte de análisis completo..."

cat > analysis_report.md << 'EOF'
# Reporte de Análisis BMAD - Generación de Playlists

## Fecha de Análisis
$(date '+%Y-%m-%d %H:%M:%S')

## Resumen Ejecutivo

EOF

# Agregar contenido del análisis al reporte
python -c "
import json

# Cargar datos
try:
    with open('measure_phase_output.json', 'r') as f:
        measure_data = json.load(f)
    with open('analyze_phase_output.json', 'r') as f:
        analysis = json.load(f)
    with open('improvement_plan.json', 'r') as f:
        plan = json.load(f)
        
    with open('analysis_report.md', 'a') as report:
        # Agregar resumen ejecutivo
        cert_status = measure_data.get('certification_status', False)
        final_score = measure_data.get('final_quality_score', 0)
        
        report.write(f'### Estado Actual\\n')
        report.write(f'- **Certificación:** {\"✅ Aprobada\" if cert_status else \"❌ Pendiente\"}\\n')
        report.write(f'- **Puntuación Global:** {final_score:.2%}\\n')
        report.write(f'- **Brecha a Objetivo:** {max(0, 0.8 - final_score):.2%}\\n\\n')
        
        # Métricas críticas
        if 'detailed_metrics' in measure_data:
            metrics = measure_data['detailed_metrics']
            report.write(f'### Métricas Críticas\\n')
            report.write(f'- **Adherencia BPM:** {metrics.get(\"bmp_adherence\", 0):.2%}\\n')
            report.write(f'- **Flujo Energético:** {metrics.get(\"energy_flow\", 0):.2%}\\n')
            report.write(f'- **Coherencia Género:** {metrics.get(\"genre_coherence\", 0):.2%}\\n')
            report.write(f'- **Completitud Datos:** {metrics.get(\"data_completeness\", 0):.2%}\\n\\n')
        
        # Root causes
        report.write(f'### Root Causes Identificados\\n')
        for i, cause in enumerate(analysis['root_causes'], 1):
            report.write(f'{i}. **{cause[\"issue\"]}**\\n')
            report.write(f'   - Root Cause: {cause[\"root_cause\"]}\\n')
            report.write(f'   - Impacto: {cause[\"impact\"]} | Urgencia: {cause[\"urgency\"]}\\n\\n')
        
        # Plan de mejoras
        report.write(f'### Plan de Mejoras Priorizado\\n')
        for improvement in plan['improvements']:
            report.write(f'#### {improvement[\"priority\"]}: {improvement[\"solution\"]}\\n')
            report.write(f'- **Esfuerzo Estimado:** {improvement[\"estimated_effort\"]}\\n')
            report.write(f'- **Impacto Esperado:** {improvement[\"expected_impact\"]}\\n')
            report.write(f'- **Pasos de Implementación:**\\n')
            for step in improvement['implementation_steps']:
                report.write(f'  - {step}\\n')
            report.write('\\n')
        
        # Recomendaciones
        report.write(f'### Recomendaciones\\n')
        report.write(f'1. **Prioridad Inmediata:** Resolver issues críticos (P1)\\n')
        report.write(f'2. **Mediano Plazo:** Implementar mejoras de alto impacto (P2)\\n') 
        report.write(f'3. **Largo Plazo:** Optimizaciones adicionales (P3-P4)\\n')
        report.write(f'4. **Monitoreo:** Establecer métricas de seguimiento continuo\\n\\n')
        
        # Next steps
        report.write(f'### Próximos Pasos\\n')
        report.write(f'1. Proceder a FASE 4: DECIDE para implementar mejoras\\n')
        report.write(f'2. Ejecutar plan de mejoras en orden de prioridad\\n')
        report.write(f'3. Validar mejoras con nuevas mediciones\\n')
        report.write(f'4. Iterar hasta alcanzar certificación\\n')
        
    print('✅ Reporte de análisis completo generado: analysis_report.md')
    
except Exception as e:
    print(f'❌ Error generando reporte: {e}')
"

echo "📋 FASE ANALYZE completada. Resultados disponibles en:"
echo "  - analyze_phase_output.json"
echo "  - improvement_plan.json"
echo "  - analysis_report.md"
```

### Criterios de Éxito para ANALYZE Phase
- ✅ Root causes identificados con precisión
- ✅ Métricas críticas analizadas
- ✅ Plan de mejoras priorizado creado
- ✅ Estimaciones de esfuerzo e impacto definidas
- ✅ Reporte de análisis completo generado
- ✅ Datos estructurados para fase DECIDE

### Resultado Esperado
Plan de mejoras específico, priorizado y detallado que guíe la implementación en la fase DECIDE, con análisis profundo de root causes y estimaciones realistas.

### Próximo Paso
Una vez completada exitosamente esta fase ANALYZE, proceder a ejecutar `bmad_phase4_decide.md` para implementar las mejoras identificadas.