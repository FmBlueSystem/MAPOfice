# SPECIFICATION: Sistema HAMMS v3.0 + Integración OpenAI GPT-4

## 🎯 **WHAT & WHY**

### Objetivo Principal
Implementar Sistema HAMMS v3.0 (12 dimensiones) y integración OpenAI GPT-4 para alcanzar paridad con la documentación técnica y elevar las capacidades de análisis musical de la aplicación.

### Justificación del Negocio
- **Gap Crítico**: Documentación promete funcionalidades que no existen
- **Valor Agregado**: Análisis musical avanzado con 12 dimensiones vs actual básico
- **Diferenciación**: Integración IA para enriquecimiento de metadata automático
- **Compliance**: Sincronizar realidad con documentación técnica oficial

### Success Criteria
1. **HAMMS v3.0**: Vector de 12 dimensiones funcionando completamente
2. **OpenAI Integration**: Enriquecimiento automático de metadata funcionando
3. **Database Schema**: Actualizado para soportar nuevas funcionalidades
4. **UI Components**: Interfaz para visualizar análisis avanzado
5. **API Integration**: Pipeline completo de análisis IA integrado

### Casos de Uso Principales
1. **Análisis Avanzado**: Usuario analiza track → obtiene vector HAMMS 12D + metadata IA
2. **Comparación Inteligente**: Sistema usa IA para sugerir tracks similares con contexto
3. **Enriquecimiento Automático**: Metadata incompleta → IA completa automáticamente
4. **Visualización**: Usuario ve análisis HAMMS 12D en radar chart interactivo

## 📐 **ESPECIFICACIONES TÉCNICAS**

### HAMMS v3.0 - 12 Dimensiones
```python
HAMMS_DIMENSIONS = {
    'bpm': 'Tempo normalizado (60-200 BPM → 0-1)',
    'key': 'Posición en rueda Camelot (1A-12B → 0-1)',
    'energy': 'Nivel de energía (0-1)',
    'danceability': 'Factor de bailabilidad (0-1)',
    'valence': 'Positividad musical (0-1)',
    'acousticness': 'Acústico vs electrónico (0-1)',
    'instrumentalness': 'Vocal vs instrumental (0-1)',
    'rhythmic_pattern': 'Complejidad rítmica (0-1)',
    'spectral_centroid': 'Brillo/timbre (0-1)',
    'tempo_stability': 'Consistencia del tempo (0-1)',
    'harmonic_complexity': 'Complejidad armónica (0-1)',
    'dynamic_range': 'Rango dinámico (0-1)'
}

DIMENSION_WEIGHTS = {
    'bpm': 1.3,
    'key': 1.4,
    'energy': 1.2,
    'danceability': 0.9,
    'valence': 0.8,
    'acousticness': 0.6,
    'instrumentalness': 0.5,
    'rhythmic_pattern': 1.1,
    'spectral_centroid': 0.7,
    'tempo_stability': 0.9,
    'harmonic_complexity': 0.8,
    'dynamic_range': 0.6
}
```

### OpenAI GPT-4 Integration
```yaml
openai_config:
  model: "gpt-4"
  max_tokens: 1000
  temperature: 0.1
  
  prompts:
    genre_analysis: |
      Analyze the musical characteristics and classify the genre.
      Track data: {track_metadata}
      HAMMS vector: {hamms_12d}
      Return JSON: {"genre": "...", "subgenre": "...", "confidence": 0.95}
    
    mood_analysis: |
      Determine emotional characteristics and mood.
      Consider: energy={energy}, valence={valence}, tempo={bpm}
      Return JSON: {"mood": "...", "era": "...", "tags": [...]}
```

### Database Schema Updates
```sql
-- Nueva tabla para HAMMS v3.0
CREATE TABLE hamms_advanced (
    track_id INTEGER PRIMARY KEY,
    vector_12d TEXT,              -- JSON: [0.1, 0.8, 0.7, ...]
    dimension_scores TEXT,        -- JSON: {"bpm": 0.1, "key": 0.8, ...}
    similarity_cache TEXT,       -- JSON: pre-computed similarities
    ml_confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);

-- Nueva tabla para análisis IA
CREATE TABLE ai_analysis (
    track_id INTEGER PRIMARY KEY,
    genre TEXT,
    subgenre TEXT,
    mood TEXT,
    era TEXT,
    tags TEXT,                   -- JSON array
    ai_confidence REAL,
    openai_response TEXT,        -- Full response for debugging
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);
```

## 🔧 **COMPONENTES A IMPLEMENTAR**

### 1. HAMMSAnalyzerV3 Class
- `calculate_extended_vector()`: Calcula vector 12D
- `calculate_similarity()`: Similarity con weights
- `get_dimension_weights()`: Pesos por dimensión
- `normalize_features()`: Normalización avanzada

### 2. OpenAIEnricher Class
- `enrich_track()`: Enriquecimiento completo
- `analyze_genre()`: Clasificación de género
- `analyze_mood()`: Análisis emocional
- `batch_enrich()`: Procesamiento por lotes

### 3. Database Integration
- Migration scripts para nuevas tablas
- Updated storage.py para HAMMS v3.0
- Nuevos métodos para AI analysis

### 4. UI Components
- HAMMSRadarChart: Visualización 12D
- AIAnalysisPanel: Mostrar resultados IA
- CompatibilityMatrix: Matriz de similitud

## 🎨 **INTERFAZ USUARIO**

### HAMMS v3.0 Visualization
```
┌─ HAMMS Analysis v3.0 ────────────────────────────────┐
│                                                      │
│    🎯 12-Dimensional Analysis                        │
│                                                      │
│    ○ BPM (1.3): ████████████░░░ 0.85                │
│    ○ Key (1.4): ██████████░░░░░ 0.67                │
│    ○ Energy (1.2): ████████████████░ 0.91           │
│    ○ Danceability: ██████████████░░░ 0.78           │
│    ○ Valence: █████████░░░░░░░░░ 0.45                │
│                                                      │
│    [🔄 Recalculate] [📊 Show Radar] [🔍 Similar]    │
└──────────────────────────────────────────────────────┘
```

### AI Enrichment Panel
```
┌─ AI Analysis (GPT-4) ────────────────────────────────┐
│ 🤖 Genre: Progressive House (95% confidence)         │
│ 🎭 Mood: Energetic, Uplifting                       │
│ 📅 Era: 2020s                                       │
│ 🏷️ Tags: [electronic, dancefloor, peak-time]       │
│                                                      │
│ 📝 AI Insights:                                     │
│ "This track features modern progressive house        │
│  elements with a driving bassline and euphoric      │
│  breakdowns typical of contemporary festival music." │
│                                                      │
│ [🔄 Re-analyze] [✏️ Edit] [💾 Save]                 │
└──────────────────────────────────────────────────────┘
```

## 📊 **MÉTRICAS DE ÉXITO**

### Funcionales
- ✅ Vector HAMMS 12D calculado correctamente
- ✅ Integración OpenAI funcionando sin errores
- ✅ Database schema actualizado y migraciones exitosas
- ✅ UI components rendering correctamente
- ✅ Pipeline análisis IA integrado en workflow

### Performance
- ⚡ HAMMS calculation < 500ms por track
- ⚡ OpenAI enrichment < 5s por track
- ⚡ Database queries < 100ms
- ⚡ UI updates < 50ms

### Calidad
- 🎯 Code coverage > 80%
- 🎯 Zero critical bugs
- 🎯 All quality gates passing
- 🎯 Documentation updated

## 🚫 **OUT OF SCOPE**

- Sistema de clustering ML avanzado
- FastAPI web API
- Workers asíncronos con Celery
- Análisis de letras/lyrics
- Integración con servicios externos (Spotify, etc.)

## 🎖️ **ACCEPTANCE CRITERIA**

### HAMMS v3.0
- [ ] Calcula correctamente las 12 dimensiones
- [ ] Aplica weights apropiados por dimensión
- [ ] Similarity calculation funciona correctamente
- [ ] Database storage para vector 12D
- [ ] UI visualization con radar chart

### OpenAI Integration
- [ ] API key configuration segura
- [ ] Prompts optimizados para análisis musical
- [ ] Error handling robusto
- [ ] Rate limiting implementado
- [ ] Results caching para eficiencia

### Database Schema
- [ ] Migration scripts ejecutan sin errores
- [ ] Nuevas tablas creadas correctamente
- [ ] Foreign key constraints funcionando
- [ ] Indices de performance agregados
- [ ] Backward compatibility mantenida

### UI Components
- [ ] HAMMS radar chart interactivo
- [ ] AI analysis panel con resultados formateados
- [ ] Integration con existing UI workflow
- [ ] Responsive design para MacBook Pro 13"
- [ ] Error states y loading indicators

---

**Specification Status**: ✅ READY FOR IMPLEMENTATION  
**Estimated Effort**: 16-20 hours  
**Priority**: HIGH  
**Dependencies**: OpenAI API key required