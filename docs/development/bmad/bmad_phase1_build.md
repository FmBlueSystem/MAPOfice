# BMAD FASE 1: BUILD - Framework de Pruebas para Playlists

## Instrucciones para el Agente

### Objetivo
Crear y validar el framework sistemático de pruebas para certificar la generación de playlists usando metodología BMAD.

### Tareas a Ejecutar

#### 1. Validar el Script de Certificación BMAD
```bash
# Activar entorno virtual
source .venv/bin/activate

# Verificar que el script de certificación existe y es ejecutable
ls -la playlist_bmad_certification.py

# Probar la importación de módulos
python -c "
import sys
sys.path.append('/Users/freddymolina/Desktop/MAP 4')
try:
    from src.services.enhanced_analyzer import create_enhanced_analyzer
    from src.services.playlist_generator import PlaylistGenerator
    from src.services.compatibility_service import CompatibilityService
    print('✅ Todos los módulos importados correctamente')
except ImportError as e:
    print(f'❌ Error de importación: {e}')
"
```

#### 2. Verificar Disponibilidad de Archivos de Audio para Pruebas
```bash
# Buscar archivos de audio en las carpetas de prueba
echo "🔍 Buscando archivos de audio para pruebas..."

# Verificar carpeta principal
find "/Volumes/My Passport/Abibleoteca/Consolidado2025/Tracks" -name "*.flac" -o -name "*.m4a" -o -name "*.mp3" | head -10

# Contar archivos disponibles
TRACK_COUNT=$(find "/Volumes/My Passport/Abibleoteca/Consolidado2025/Tracks" -name "*.flac" -o -name "*.m4a" -o -name "*.mp3" | wc -l)
echo "📊 Total de archivos encontrados: $TRACK_COUNT"

if [ $TRACK_COUNT -lt 10 ]; then
    echo "⚠️ Se necesitan al menos 10 archivos para pruebas completas"
else
    echo "✅ Suficientes archivos para pruebas"
fi
```

#### 3. Ejecutar Prueba Preliminar del Framework
```bash
# Ejecutar una prueba rápida del framework BMAD
echo "🧪 Ejecutando prueba preliminar del framework..."

python -c "
import sys
sys.path.append('/Users/freddymolina/Desktop/MAP 4')
import os
import glob
from pathlib import Path

# Buscar archivos de prueba
test_paths = [
    '/Volumes/My Passport/Abibleoteca/Consolidado2025/Tracks',
]

tracks = []
for base_path in test_paths:
    if os.path.exists(base_path):
        for pattern in ['*.flac', '*.m4a', '*.mp3']:
            found = glob.glob(os.path.join(base_path, pattern))
            tracks.extend(found)
            if len(tracks) >= 5:
                break
    if len(tracks) >= 5:
        break

print(f'🎵 Encontrados {len(tracks)} archivos para pruebas')
if tracks:
    print('📁 Archivos de ejemplo:')
    for i, track in enumerate(tracks[:3]):
        print(f'  {i+1}. {Path(track).name}')
        
if len(tracks) >= 5:
    print('✅ Framework BUILD: LISTO PARA EJECUCIÓN')
else:
    print('❌ Framework BUILD: INSUFICIENTES ARCHIVOS')
"
```

#### 4. Crear Archivo de Configuración de Pruebas
```bash
# Crear configuración específica para las pruebas BMAD
cat > bmad_test_config.json << 'EOF'
{
  "test_scenarios": [
    {
      "name": "strict_tolerance",
      "description": "Prueba con tolerancia BPM estricta del 2%",
      "playlist_length": 10,
      "bpm_tolerance": 0.02,
      "expected_quality_threshold": 0.85
    },
    {
      "name": "moderate_tolerance", 
      "description": "Prueba con tolerancia BPM moderada del 5%",
      "playlist_length": 15,
      "bpm_tolerance": 0.05,
      "expected_quality_threshold": 0.75
    },
    {
      "name": "relaxed_tolerance",
      "description": "Prueba con tolerancia BPM relajada del 10%", 
      "playlist_length": 20,
      "bmp_tolerance": 0.10,
      "expected_quality_threshold": 0.70
    }
  ],
  "quality_metrics": {
    "bmp_adherence_weight": 0.30,
    "energy_flow_weight": 0.20,
    "genre_coherence_weight": 0.20,
    "transition_quality_weight": 0.20,
    "data_completeness_weight": 0.10
  },
  "certification_criteria": {
    "overall_quality_minimum": 0.80,
    "bmp_adherence_minimum": 0.90,
    "data_completeness_minimum": 0.85,
    "energy_flow_minimum": 0.70,
    "genre_coherence_minimum": 0.70
  }
}
EOF

echo "✅ Archivo de configuración creado: bmad_test_config.json"
```

#### 5. Validar Servicios Requeridos
```bash
# Verificar que todos los servicios necesarios estén disponibles
echo "🔧 Validando servicios requeridos..."

python -c "
import sys
sys.path.append('/Users/freddymolina/Desktop/MAP 4')

try:
    from src.services.enhanced_analyzer import create_enhanced_analyzer
    analyzer = create_enhanced_analyzer()
    print('✅ EnhancedAnalyzer: Disponible')
except Exception as e:
    print(f'❌ EnhancedAnalyzer: Error - {e}')

try:
    from src.services.playlist_generator import PlaylistGenerator
    generator = PlaylistGenerator()
    print('✅ PlaylistGenerator: Disponible')
except Exception as e:
    print(f'❌ PlaylistGenerator: Error - {e}')

try:
    from src.services.compatibility_service import CompatibilityService
    compatibility = CompatibilityService()
    print('✅ CompatibilityService: Disponible')
except Exception as e:
    print(f'❌ CompatibilityService: Error - {e}')
"
```

### Criterios de Éxito para BUILD Phase
- ✅ Script de certificación BMAD validado
- ✅ Mínimo 10 archivos de audio disponibles
- ✅ Todos los servicios requeridos funcionando
- ✅ Configuración de pruebas creada
- ✅ Prueba preliminar exitosa

### Resultado Esperado
Al completar esta fase, el framework estará completamente preparado para ejecutar las pruebas de generación de playlists con métricas de calidad comprehensivas.

### Próximo Paso
Una vez completada exitosamente esta fase BUILD, proceder a ejecutar `bmad_phase2_measure.md` para comenzar las mediciones del estado actual.