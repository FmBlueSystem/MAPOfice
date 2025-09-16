# Sistema de Exportación Profesional - MAP4

## 🎯 Descripción General

El Sistema de Exportación Profesional de MAP4 permite exportar resultados de análisis musical en múltiples formatos, con plantillas personalizables y opciones de branding profesional.

## 📊 Formatos Soportados

### HTML (Reportes Profesionales)
- **Uso**: Reportes visuales con gráficos y estilos profesionales
- **Características**:
  - Diseño responsive
  - Gráficos interactivos
  - Estilos personalizables
  - Compatible con impresión

### CSV (Excel Compatible)
- **Uso**: Análisis de datos en hojas de cálculo
- **Características**:
  - Columnas personalizables
  - Compatible con Excel/Google Sheets
  - UTF-8 encoding
  - Datos planos para análisis

### JSON (Machine Readable)
- **Uso**: Integración con otros sistemas
- **Características**:
  - Estructura jerárquica completa
  - Metadatos incluidos
  - Pretty-print opcional
  - API-ready

## 🎨 Plantillas Disponibles

### 1. Standard Analysis Report
Reporte completo de análisis con:
- Estadísticas generales
- Tabla de tracks detallada
- Información de BPM, Key, Energy
- HAMMS scores

### 2. DJ Setlist Template
Diseñado para DJs con:
- Diseño nocturno elegante
- Time markers
- Transiciones entre tracks
- BPM y Key prominentes

### 3. Radio Show Template
Para programas de radio con:
- Segmentos organizados
- Tiempos de emisión
- Información del host
- Lista de reproducción estructurada

### 4. Music Library Report
Análisis de biblioteca completa:
- Distribución por géneros
- Top artistas
- Estadísticas globales
- Gráficos de distribución

### 5. Compatibility Matrix
Matriz de compatibilidad visual:
- Scores de compatibilidad
- Código de colores
- Vista de matriz completa
- Leyenda interpretativa

## 🚀 Uso desde la UI

### Exportación Básica

1. **Analizar Tracks**
   - Cargar y analizar tu música
   - Esperar a que termine el análisis

2. **Click en "Export Results"**
   - Se abre el diálogo de exportación

3. **Seleccionar Formato**
   - HTML Report (Professional)
   - CSV (Excel Compatible)
   - JSON (Machine Readable)
   - All Formats (Multiple Files)

4. **Elegir Plantilla** (para HTML)
   - Standard Analysis
   - DJ Setlist
   - Radio Show
   - Library Report

5. **Opciones Adicionales**
   - Include Charts & Visualizations
   - Include HAMMS Analysis

6. **Click OK**
   - Los archivos se guardan en `exports/`

## 💻 Uso Programático

### Ejemplo Básico

```python
from src.services.export_manager import ExportManager

# Crear instancia
export_mgr = ExportManager()

# Datos de tracks
tracks = [
    {
        'name': 'Track 1',
        'artist': 'Artist 1',
        'bpm': 128,
        'key': 'Am'
    }
]

# Exportar a HTML
file_path = export_mgr.export_analysis_report(
    tracks,
    title="Mi Análisis",
    format="html"
)
```

### Exportación Batch

```python
# Múltiples datasets
datasets = [
    {'name': 'house_tracks', 'data': house_tracks},
    {'name': 'techno_tracks', 'data': techno_tracks}
]

# Exportar en múltiples formatos
results = export_mgr.batch_export(
    datasets,
    formats=['html', 'csv', 'json']
)
```

### Plantillas Personalizadas

```python
from src.services.export_templates import ExportTemplates

templates = ExportTemplates()

# DJ Setlist
html = templates.dj_setlist_template(
    tracks,
    event_info={
        'name': 'Summer Festival 2024',
        'venue': 'Beach Club',
        'date': '2024-07-15'
    }
)

# Radio Show
html = templates.radio_show_template(
    segments=[
        {
            'name': 'Opening',
            'start_time': '00:00',
            'end_time': '15:00',
            'tracks': opening_tracks
        }
    ],
    show_info={
        'name': 'Electronic Vibes',
        'host': 'DJ Master',
        'episode': '042'
    }
)
```

### Exportación con Branding

```python
# Configuración de marca
brand_config = {
    'company_name': 'Mi Estudio',
    'logo': 'path/to/logo.png',
    'colors': {
        'primary': '#667eea',
        'secondary': '#764ba2'
    }
}

# Exportar con branding
file_path = export_mgr.export_with_branding(
    tracks,
    format='html',
    brand_config=brand_config
)
```

## 📁 Estructura de Directorios

```
exports/
├── pdf/          # Reportes PDF (futuro)
├── excel/        # Archivos CSV/Excel
├── json/         # Exportaciones JSON
├── reports/      # Reportes HTML
└── templates/    # Plantillas personalizadas
```

## 🔧 Configuración Avanzada

### Columnas CSV Personalizadas

```python
# Seleccionar columnas específicas
export_mgr.export_to_csv(
    tracks,
    columns=['name', 'artist', 'bpm', 'key']
)
```

### JSON Pretty vs Compact

```python
# JSON compacto (menor tamaño)
export_mgr.export_to_json(data, pretty=False)

# JSON formateado (legible)
export_mgr.export_to_json(data, pretty=True)
```

## 🎯 Casos de Uso

### Para DJs
- Exportar setlists con tiempos y transiciones
- Generar reportes de compatibilidad
- Crear playlists profesionales

### Para Productores
- Analizar bibliotecas completas
- Exportar datos para análisis externo
- Documentar colecciones musicales

### Para Radios
- Generar reportes de programación
- Documentar emisiones
- Crear logs de reproducción

### Para Análisis
- Exportar a CSV para Excel
- JSON para integración API
- HTML para presentaciones

## 📊 Ejemplos de Salida

### HTML Report
- Diseño profesional con gradientes
- Tablas interactivas
- Estadísticas visuales
- Compatible con impresión

### CSV Export
```csv
name,artist,bpm,key,energy
Track 1,Artist 1,128,Am,0.85
Track 2,Artist 2,124,C,0.72
```

### JSON Export
```json
{
  "metadata": {
    "version": "2.0",
    "export_date": "2024-01-15",
    "total_tracks": 2
  },
  "tracks": [
    {
      "name": "Track 1",
      "artist": "Artist 1",
      "bpm": 128,
      "key": "Am",
      "energy": 0.85
    }
  ]
}
```

## 🧪 Testing

```bash
# Ejecutar tests
python3 -m unittest tests.test_export_manager -v

# Tests incluidos:
# ✓ Exportación JSON
# ✓ Exportación CSV
# ✓ Reportes HTML
# ✓ Batch export
# ✓ Plantillas personalizadas
# ✓ Manejo de caracteres especiales
# ✓ Datos vacíos
```

## 🚀 Mejoras Futuras

- [ ] Exportación PDF nativa
- [ ] Gráficos interactivos con Plotly
- [ ] Exportación Excel con formato (.xlsx)
- [ ] Templates drag & drop
- [ ] API REST para exportación
- [ ] Exportación a la nube
- [ ] Firmas digitales
- [ ] Watermarks personalizables

## 📝 Notas Técnicas

- **Encoding**: UTF-8 para todos los formatos
- **HTML Escaping**: Automático para seguridad
- **CSV Delimiter**: Coma (,) estándar
- **JSON Indent**: 2 espacios por defecto
- **File Naming**: Timestamp automático
- **Directory Creation**: Automática si no existe

---

**Versión**: 1.0.0
**Última Actualización**: Enero 2025
**Autor**: MAP4 Development Team