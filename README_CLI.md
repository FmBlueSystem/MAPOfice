# Music Analyzer Pro - CLI Guide

## 📖 Descripción

El CLI de Music Analyzer Pro permite procesar carpetas completas de música sin interfaz gráfica, ideal para análisis en lote y automatización.

## 🚀 Uso Básico

```bash
# Activar el entorno virtual
source .venv/bin/activate

# Análisis básico de una carpeta
python cli_analyzer.py "/path/to/music/folder"

# Análisis con exportación a CSV
python cli_analyzer.py "/path/to/music" --export results.csv
```

## 📋 Opciones Disponibles

| Opción | Descripción |
|--------|-------------|
| `--no-validation` | Saltar validación de metadatos obligatorios ⚠️ |
| `--force` | Forzar re-análisis de archivos ya procesados |
| `--export FILE` | Exportar resultados a archivo CSV |
| `--formats FORMATS` | Formatos específicos (ej: mp3,flac,wav) |
| `--no-recursive` | No buscar en subcarpetas |
| `--no-ai` | Solo análisis HAMMS (sin IA) |
| `--quiet` | Salida mínima |

## 💡 Ejemplos de Uso

### 1. Análisis Completo con IA
```bash
python cli_analyzer.py "/Users/music/collection" --export complete_analysis.csv
```

### 2. Solo Formatos Específicos
```bash
python cli_analyzer.py "/Users/music" --formats "mp3,flac" --export mp3_flac_only.csv
```

### 3. Sin Validación (Para Archivos Incompletos)
```bash
python cli_analyzer.py "/Users/music" --no-validation --export all_files.csv
```

### 4. Re-análisis Completo
```bash
python cli_analyzer.py "/Users/music" --force --export reanalysis.csv
```

### 5. Solo HAMMS (Sin IA)
```bash
python cli_analyzer.py "/Users/music" --no-ai --export hamms_only.csv
```

### 6. Análisis Silencioso
```bash
python cli_analyzer.py "/Users/music" --quiet --export results.csv
```

## 📊 Salida del Programa

### Información de Progreso
- 📁 Carpeta procesada
- 🎯 Estado de validación
- 🤖 Estado de análisis IA
- 🔄 Estado de re-análisis

### Resultados por Archivo
- ✅ Éxito con género detectado
- ❌ Error de validación (metadatos faltantes)
- 💥 Error de procesamiento

### Resumen Final
- 📊 Total de archivos encontrados
- ⚡ Archivos procesados
- ✅ Procesados exitosamente  
- 🤖 Enriquecidos con IA
- ❌ Rechazados por validación
- 💥 Errores de procesamiento
- 📈 Tasa de éxito

## 📁 Formato del CSV Exportado

| Campo | Descripción |
|-------|-------------|
| `file_path` | Ruta completa del archivo |
| `file_name` | Nombre del archivo |
| `success` | true/false - si el análisis fue exitoso |
| `title` | Título de la canción |
| `artist` | Artista |
| `album` | Álbum |
| `bpm` | Tempo (beats por minuto) |
| `key` | Clave musical |
| `energy` | Nivel de energía (0.0-1.0) |
| `genre` | Género principal (IA) |
| `subgenre` | Subgénero específico (IA) |
| `mood` | Estado de ánimo (IA) |
| `era` | Era musical (IA) |
| `tags` | Etiquetas descriptivas (IA) |
| `hamms_confidence` | Confianza HAMMS (0.0-1.0) |
| `ai_confidence` | Confianza IA (0.0-1.0) |
| `processing_time_ms` | Tiempo de procesamiento en ms |
| `error_message` | Mensaje de error (si aplica) |

## ⚠️ Validación de Metadatos

Por defecto, el CLI requiere que todos los archivos tengan:
- **BPM** (tempo)
- **Key** (clave musical)  
- **Energy** (nivel de energía 0.0-1.0)
- **Comments** (comentarios no vacíos)

### Para Procesar Archivos Sin Metadatos Completos:
```bash
python cli_analyzer.py "/path/to/music" --no-validation
```

**⚠️ Nota**: Usar `--no-validation` puede resultar en análisis menos precisos.

## 🔧 Casos de Uso Comunes

### Análisis de Biblioteca Musical Completa
```bash
# Análisis completo con todas las funciones
python cli_analyzer.py "/Users/$(whoami)/Music" \
    --export "music_library_$(date +%Y%m%d).csv"
```

### Procesamiento de Nuevas Descargas
```bash
# Solo archivos nuevos, formatos específicos
python cli_analyzer.py "/Users/Downloads/Music" \
    --formats "mp3,m4a,flac" \
    --export "new_music.csv"
```

### Re-análisis con Prompt Mejorado
```bash
# Forzar re-análisis para usar el prompt mejorado
python cli_analyzer.py "/Users/music/1970s" \
    --force \
    --export "reanalyzed_1970s.csv"
```

### Análisis Rápido HAMMS Solo
```bash
# Para análisis técnico rápido sin IA
python cli_analyzer.py "/Users/music/test" \
    --no-ai \
    --quiet \
    --export "hamms_technical.csv"
```

## 🚨 Códigos de Salida

- `0`: Éxito
- `1`: Error (carpeta no encontrada, fallo crítico, etc.)

## 📝 Logging

El CLI proporciona logging detallado en tiempo real:
- Progreso archivo por archivo
- Errores de validación específicos
- Tiempo total de procesamiento
- Estadísticas finales

Use `--quiet` para salida mínima en scripts automatizados.

---

**💡 Tip**: Combina con `cron` o scripts automatizados para análisis periódicos de nuevas descargas musicales.