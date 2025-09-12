# BMAD FASE 2: MEASURE - Medición del Estado Actual

## Instrucciones para el Agente

### Objetivo
Ejecutar el framework de pruebas y capturar métricas comprehensivas del estado actual de la generación de playlists.

### Tareas a Ejecutar

#### 1. Ejecutar el Script de Certificación BMAD Completo
```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar el script completo de certificación BMAD
echo "🚀 Iniciando proceso completo de certificación BMAD..."

python playlist_bmad_certification.py 2>&1 | tee bmad_execution_log.txt

# Verificar que se generaron resultados
echo "📊 Verificando resultados generados..."
ls -la playlist_bmad_results_*.json 2>/dev/null || echo "⚠️ No se encontraron archivos de resultados"
```

#### 2. Analizar Resultados de la Medición
```bash
# Extraer métricas clave de los resultados generados
echo "🔍 Analizando resultados de medición..."

python -c "
import json
import glob
import os
from datetime import datetime

# Buscar el archivo de resultados más reciente
result_files = glob.glob('playlist_bmad_results_*.json')
if not result_files:
    print('❌ No se encontraron archivos de resultados')
    exit(1)

latest_file = max(result_files, key=os.path.getctime)
print(f'📁 Analizando: {latest_file}')

try:
    with open(latest_file, 'r') as f:
        results = json.load(f)
    
    print(f\"\\n📊 RESULTADOS DE MEDICIÓN:\")
    print(f\"Total de ciclos ejecutados: {results.get('total_cycles', 'N/A')}\")
    print(f\"Certificación alcanzada: {results.get('certification_achieved', False)}\")
    print(f\"Puntuación final de calidad: {results.get('final_quality_score', 0):.2%}\")
    
    if 'cycle_results' in results and results['cycle_results']:
        last_cycle = results['cycle_results'][-1]
        if 'analysis_result' in last_cycle:
            analysis = last_cycle['analysis_result']
            
            print(f\"\\n🎯 MÉTRICAS DETALLADAS (Último Ciclo):\")
            if 'detailed_metrics' in analysis:
                metrics = analysis['detailed_metrics']
                print(f\"  Adherencia BPM: {metrics.get('bpm_adherence', 0):.2%}\")
                print(f\"  Flujo energético: {metrics.get('energy_flow', 0):.2%}\")
                print(f\"  Coherencia género: {metrics.get('genre_coherence', 0):.2%}\")
                print(f\"  Completitud datos: {metrics.get('data_completeness', 0):.2%}\")
            
            print(f\"\\n🚨 ISSUES CRÍTICOS: {len(analysis.get('critical_issues', []))}\")
            for issue in analysis.get('critical_issues', []):
                print(f\"  - {issue}\")
            
            print(f\"\\n⚡ OPORTUNIDADES DE MEJORA: {len(analysis.get('improvement_opportunities', []))}\")
            for opp in analysis.get('improvement_opportunities', []):
                print(f\"  - {opp}\")
                
    print(f\"\\n✅ Análisis de medición completado\")
    
except Exception as e:
    print(f'❌ Error analizando resultados: {e}')
"
```

#### 3. Generar Reporte de Estado Actual
```bash
# Crear reporte consolidado del estado actual
echo "📋 Generando reporte de estado actual..."

cat > current_state_report.md << 'EOF'
# Reporte de Estado Actual - Generación de Playlists

## Fecha de Medición
$(date '+%Y-%m-%d %H:%M:%S')

## Resumen Ejecutivo
EOF

# Agregar métricas al reporte
python -c "
import json
import glob
import os
from datetime import datetime

result_files = glob.glob('playlist_bmad_results_*.json')
if result_files:
    latest_file = max(result_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r') as f:
            results = json.load(f)
        
        with open('current_state_report.md', 'a') as report:
            report.write(f'\\n### Resultados de Certificación\\n')
            report.write(f'- **Total de Ciclos:** {results.get(\"total_cycles\", \"N/A\")}\\n')
            report.write(f'- **Certificación Alcanzada:** {\"✅ Sí\" if results.get(\"certification_achieved\") else \"❌ No\"}\\n')
            report.write(f'- **Puntuación Final:** {results.get(\"final_quality_score\", 0):.2%}\\n\\n')
            
            if 'cycle_results' in results and results['cycle_results']:
                last_cycle = results['cycle_results'][-1]
                if 'analysis_result' in last_cycle:
                    analysis = last_cycle['analysis_result']
                    
                    report.write(f'### Métricas Detalladas\\n')
                    if 'detailed_metrics' in analysis:
                        metrics = analysis['detailed_metrics']
                        report.write(f'- **Adherencia BPM:** {metrics.get(\"bmp_adherence\", 0):.2%}\\n')
                        report.write(f'- **Flujo Energético:** {metrics.get(\"energy_flow\", 0):.2%}\\n')
                        report.write(f'- **Coherencia Género:** {metrics.get(\"genre_coherence\", 0):.2%}\\n')
                        report.write(f'- **Completitud Datos:** {metrics.get(\"data_completeness\", 0):.2%}\\n\\n')
                    
                    report.write(f'### Issues Críticos\\n')
                    for issue in analysis.get('critical_issues', []):
                        report.write(f'- {issue}\\n')
                    
                    report.write(f'\\n### Oportunidades de Mejora\\n')
                    for opp in analysis.get('improvement_opportunities', []):
                        report.write(f'- {opp}\\n')
        
        print('✅ Reporte de estado actual generado: current_state_report.md')
        
    except Exception as e:
        print(f'❌ Error generando reporte: {e}')
else:
    print('❌ No se encontraron resultados para el reporte')
"
```

#### 4. Validar Calidad de Datos de Medición
```bash
# Verificar la integridad y calidad de los datos capturados
echo "🔍 Validando calidad de datos de medición..."

python -c "
import json
import glob
import os

result_files = glob.glob('playlist_bmad_results_*.json')
if not result_files:
    print('❌ No hay datos para validar')
    exit(1)

latest_file = max(result_files, key=os.path.getctime)

try:
    with open(latest_file, 'r') as f:
        results = json.load(f)
    
    # Validaciones de integridad
    validations = []
    
    # 1. Estructura básica
    required_keys = ['total_cycles', 'certification_achieved', 'final_quality_score', 'cycle_results']
    missing_keys = [key for key in required_keys if key not in results]
    if missing_keys:
        validations.append(f'❌ Claves faltantes: {missing_keys}')
    else:
        validations.append('✅ Estructura básica completa')
    
    # 2. Datos de ciclos
    if 'cycle_results' in results and results['cycle_results']:
        cycle_count = len(results['cycle_results'])
        validations.append(f'✅ {cycle_count} ciclo(s) de datos capturados')
        
        # Verificar último ciclo
        last_cycle = results['cycle_results'][-1]
        if 'analysis_result' in last_cycle:
            validations.append('✅ Análisis del último ciclo disponible')
        else:
            validations.append('❌ Análisis del último ciclo faltante')
    else:
        validations.append('❌ No hay datos de ciclos')
    
    # 3. Métricas de calidad
    final_score = results.get('final_quality_score', 0)
    if isinstance(final_score, (int, float)) and 0 <= final_score <= 1:
        validations.append(f'✅ Puntuación de calidad válida: {final_score:.2%}')
    else:
        validations.append(f'❌ Puntuación de calidad inválida: {final_score}')
    
    print('📊 VALIDACIÓN DE DATOS:')
    for validation in validations:
        print(f'  {validation}')
    
    # Determinar si los datos son suficientes para análisis
    data_quality_score = len([v for v in validations if v.startswith('✅')]) / len(validations)
    print(f'\\n📈 Puntuación de Calidad de Datos: {data_quality_score:.2%}')
    
    if data_quality_score >= 0.8:
        print('✅ DATOS LISTOS PARA FASE ANALYZE')
    else:
        print('⚠️ DATOS NECESITAN MEJORA ANTES DE ANÁLISIS')
        
except Exception as e:
    print(f'❌ Error en validación: {e}')
"
```

#### 5. Preparar Datos para Fase de Análisis
```bash
# Crear resumen estructurado para la fase de análisis
echo "📋 Preparando datos para fase ANALYZE..."

python -c "
import json
import glob
import os

result_files = glob.glob('playlist_bmad_results_*.json')
if result_files:
    latest_file = max(result_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r') as f:
            results = json.load(f)
        
        # Crear resumen para análisis
        analysis_input = {
            'measurement_timestamp': os.path.getctime(latest_file),
            'certification_status': results.get('certification_achieved', False),
            'final_quality_score': results.get('final_quality_score', 0),
            'total_cycles_executed': results.get('total_cycles', 0),
            'ready_for_analysis': True
        }
        
        if 'cycle_results' in results and results['cycle_results']:
            last_cycle = results['cycle_results'][-1]
            if 'analysis_result' in last_cycle:
                analysis_result = last_cycle['analysis_result']
                analysis_input.update({
                    'critical_issues': analysis_result.get('critical_issues', []),
                    'improvement_opportunities': analysis_result.get('improvement_opportunities', []),
                    'detailed_metrics': analysis_result.get('detailed_metrics', {})
                })
        
        # Guardar para la siguiente fase
        with open('measure_phase_output.json', 'w') as f:
            json.dump(analysis_input, f, indent=2)
        
        print('✅ Datos preparados para ANALYZE: measure_phase_output.json')
        
    except Exception as e:
        print(f'❌ Error preparando datos: {e}')
else:
    print('❌ No hay resultados para preparar')
"

echo "📊 FASE MEASURE completada. Resultados disponibles en:"
echo "  - bmad_execution_log.txt"
echo "  - playlist_bmad_results_*.json" 
echo "  - current_state_report.md"
echo "  - measure_phase_output.json"
```

### Criterios de Éxito para MEASURE Phase
- ✅ Script BMAD ejecutado completamente
- ✅ Métricas de calidad capturadas
- ✅ Issues críticos identificados
- ✅ Oportunidades de mejora documentadas
- ✅ Reporte de estado actual generado
- ✅ Datos validados para análisis

### Resultado Esperado
Conjunto completo de métricas y datos sobre el estado actual de la generación de playlists, listo para análisis profundo en la siguiente fase.

### Próximo Paso
Una vez completada exitosamente esta fase MEASURE, proceder a ejecutar `bmad_phase3_analyze.md` para el análisis profundo de los resultados.