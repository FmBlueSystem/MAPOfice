# Music Analyzer Pro - Enhanced Edition Usage Guide

## 🚀 HAMMS v3.0 + OpenAI Integration

Este documento describe cómo usar la versión enhanced de Music Analyzer Pro con HAMMS v3.0 y integración OpenAI GPT-4.

## 📋 Características Principales

### ✅ Implementado y Funcional
- **HAMMS v3.0 (12 dimensiones)**: Análisis armónico avanzado con vectores de 12 dimensiones
- **Integración OpenAI GPT-4**: Enriquecimiento automático con género, mood, era y tags
- **Radar Chart Interactivo**: Visualización de vectores HAMMS con Plotly
- **Base de Datos Avanzada**: Almacenamiento de análisis HAMMS y AI con migraciones
- **UI Enhanced**: Interfaz mejorada con tabs y controles avanzados
- **Análisis por Lotes**: Procesamiento de múltiples pistas con progreso detallado

### 🔧 Configuración de OpenAI

Para habilitar el análisis con IA, configure su API key:

```bash
# Añadir a ~/.bashrc o ~/.zshrc
export OPENAI_API_KEY="sk-your-openai-api-key-here"
export OPENAI_MODEL="gpt-4"
export OPENAI_MAX_TOKENS="1000"
export OPENAI_TEMPERATURE="0.1"
```

## 🎯 Comandos de Uso

### Lanzar UI Enhanced
```bash
# UI completa con HAMMS v3.0 + OpenAI
make enhanced-ui

# O directamente
./scripts/enhanced_ui
```

### Lanzar UI Clásica (compatibilidad)
```bash
# UI original sin características enhanced
make ui
```

### Pruebas de Integración AI
```bash
# Probar integración completa con un archivo
export OPENAI_API_KEY="sk-..."
./scripts/test_ai_integration /path/to/song.mp3

# O usando make
make test-ai
```

## 📊 Sistema HAMMS v3.0

### Dimensiones del Vector (12D)

| Dimensión | Rango | Descripción | Peso |
|-----------|-------|-------------|------|
| **BPM** | [0,1] | Tempo normalizado (60-200 BPM) | 1.3 |
| **Key** | [0,1] | Posición en rueda Camelot | 1.4 |
| **Energy** | [0,1] | Nivel de energía RMS | 1.2 |
| **Danceability** | [0,1] | Aptitud para baile | 0.9 |
| **Valence** | [0,1] | Positividad musical | 0.8 |
| **Acousticness** | [0,1] | Contenido acústico vs electrónico | 0.6 |
| **Instrumentalness** | [0,1] | Probabilidad instrumental | 0.5 |
| **Rhythmic Pattern** | [0,1] | Complejidad rítmica | 1.1 |
| **Spectral Centroid** | [0,1] | Brillo del sonido | 0.7 |
| **Tempo Stability** | [0,1] | Estabilidad temporal | 0.9 |
| **Harmonic Complexity** | [0,1] | Complejidad armónica | 0.8 |
| **Dynamic Range** | [0,1] | Rango dinámico | 0.6 |

### Fórmula de Similitud
```
similitud = 0.6 × sim_euclidiana + 0.4 × sim_coseno
```

## 🤖 Integración OpenAI GPT-4

### Campos de Análisis AI
- **Genre**: Género musical principal
- **Subgenre**: Subgénero específico  
- **Mood**: Estado emocional
- **Era**: Época/década musical
- **Tags**: Etiquetas descriptivas
- **Confidence**: Confianza del AI (0-1)

### Ejemplo de Respuesta AI
```json
{
  "genre": "Electronic",
  "subgenre": "Deep House", 
  "mood": "Energetic",
  "era": "2020s",
  "tags": ["upbeat", "danceable", "electronic"],
  "confidence": 0.85
}
```

## 🎨 Radar Chart Interactive

### Características
- **Visualización 12D**: Representación polar de vectores HAMMS
- **Modo Comparación**: Visualizar múltiples pistas simultáneamente
- **Controles Dinámicos**: Ajustar opacidad, fill, y dimensiones visibles
- **Export**: PNG, HTML interactivo
- **Hover Info**: Información detallada al pasar mouse

### Uso del Radar Chart
1. Ejecutar análisis enhanced en pistas de audio
2. Ir a tab "HAMMS Visualization" 
3. Seleccionar pistas desde "Analysis Results"
4. Click "Visualize Selected" para mostrar en radar
5. Activar "Comparison Mode" para múltiples pistas

## 💾 Base de Datos Enhanced

### Nuevas Tablas
- **hamms_advanced**: Vectores 12D + dimensiones + cache de similitud
- **ai_analysis**: Análisis OpenAI + metadata + timestamps

### Migraciones Automáticas
```bash
# Las migraciones se ejecutan automáticamente
# Ubicación: alembic/versions/
# Comando manual: alembic upgrade head
```

## 🔍 Workflow de Análisis Complete

### Proceso Paso a Paso
1. **Análisis Básico**: BPM, key, energy con librosa
2. **HAMMS v3.0**: Cálculo de vector 12D con pesos
3. **OpenAI Enrichment**: Análisis semántico con GPT-4
4. **Almacenamiento**: Guardar en base de datos con relaciones
5. **Visualización**: Mostrar en radar chart interactivo

### Pipeline de Datos
```
Audio → librosa → {bpm, key, energy} → HAMMS v3.0 → 12D Vector
                                                    ↓
Database ← AI Analysis ← OpenAI GPT-4 ← track_data + HAMMS
```

## 📈 Rendimiento

### Tiempos Estimados (por pista)
- **Análisis básico**: ~2-5 segundos
- **HAMMS v3.0**: ~0.1 segundos  
- **OpenAI enrichment**: ~3-8 segundos
- **Total enhanced**: ~5-13 segundos

### Configuración de Performance
```bash
# Variables de entorno para optimización
export AI_BATCH_SIZE=5              # Pistas por lote AI
export AI_TIMEOUT_SECONDS=30        # Timeout OpenAI 
export AI_RATE_LIMIT_RPM=60         # Límite de requests/min
export HAMMS_CACHE_SIZE=1000        # Cache de similitud
```

## 🐛 Solución de Problemas

### OpenAI API Issues
```bash
# Verificar API key
echo $OPENAI_API_KEY

# Test de conectividad
./scripts/test_ai_integration /path/to/test.mp3
```

### Errores Comunes
- **"OpenAI Not Configured"**: Configurar OPENAI_API_KEY
- **"PyQt6 Import Error"**: Instalar PyQt6-WebEngine
- **"Database Migration Error"**: Verificar permisos en data/
- **"HAMMS Vector Invalid"**: Verificar formato de audio soportado

### Logs y Debugging
```bash
# Ejecutar con debug
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
./scripts/enhanced_ui
```

## 🎯 Casos de Uso

### DJ/Producer Workflow
1. Analizar biblioteca musical completa
2. Usar radar chart para identificar pistas similares
3. Generar playlists basadas en similitud HAMMS
4. Enriquecer metadata con análisis AI

### Investigación Musical
1. Análizar evolución de géneros en el tiempo
2. Comparar características entre artistas
3. Estudiar patrones en vectores HAMMS
4. Exportar datos para análisis estadístico

## 📞 Soporte

Para problemas o mejoras:
- Revisar logs en ventana de análisis
- Ejecutar script de pruebas: `./scripts/test_ai_integration`
- Verificar configuración de API keys
- Consultar documentación de HAMMS v3.0

---

**¡El sistema enhanced está listo para uso con API key de OpenAI!**