# PLAN: Implementación HAMMS v3.0 + OpenAI GPT-4

## 📋 **ARQUITECTURA TÉCNICA**

### Stack Tecnológico Adicional
```yaml
Nuevas Dependencies:
  - openai>=1.0.0          # OpenAI GPT-4 API
  - numpy>=1.24.0          # Vectores HAMMS avanzados
  - scikit-learn>=1.3.0    # Similarity calculations
  - python-dotenv>=1.0.0   # Environment variables
  - plotly>=5.17.0         # Radar charts interactivos
  
Database:
  - SQLAlchemy>=2.0.0      # Ya existente, nuevas tablas
  - Alembic>=1.12.0        # Migrations (nuevo)
```

### Estructura de Archivos
```
src/
├── analysis/                    # Nuevo módulo de análisis avanzado
│   ├── __init__.py
│   ├── hamms_v3.py             # HAMMS v3.0 implementation
│   ├── openai_enricher.py      # OpenAI integration
│   └── similarity_engine.py    # Advanced similarity
├── models/
│   ├── hamms_advanced.py       # Modelo HAMMS v3.0
│   └── ai_analysis.py          # Modelo AI analysis
├── ui/
│   ├── components/
│   │   ├── hamms_radar.py      # Radar chart component
│   │   └── ai_panel.py         # AI analysis panel
│   └── dialogs/
│       └── hamms_config.py     # Configuración HAMMS
├── migrations/                  # Database migrations
│   ├── __init__.py
│   └── 001_hamms_v3_tables.py
└── config/
    ├── __init__.py
    └── openai_config.py        # OpenAI configuration
```

## 🏗️ **COMPONENTES PRINCIPALES**

### 1. HAMMSAnalyzerV3 (src/analysis/hamms_v3.py)

#### Interface
```python
class HAMMSAnalyzerV3:
    """HAMMS v3.0 - 12-dimensional vector analysis system"""
    
    def __init__(self, db_path: str):
        self.db = Storage.from_path(db_path)
        self.dimension_weights = DIMENSION_WEIGHTS
        self.cache = {}
    
    def calculate_extended_vector(self, track_data: Dict) -> np.ndarray:
        """Calculate 12-dimensional HAMMS vector"""
        # Core: BPM, Key, Energy (ya existe)
        # Extended: 9 nuevas dimensiones
        pass
    
    def calculate_similarity(self, v1: np.ndarray, v2: np.ndarray) -> Dict:
        """Calculate weighted similarity between vectors"""
        # Euclidean + Cosine + weighted average
        pass
    
    def get_compatible_tracks(self, seed_track: Dict, limit: int = 20) -> List[Dict]:
        """Get compatible tracks using 12D analysis"""
        pass
```

#### Cálculo de Dimensiones Avanzadas
```python
def _calculate_rhythmic_pattern(self, genre: str, bpm: float) -> float:
    """Calculate rhythmic complexity based on genre and BPM"""
    rhythm_map = {
        'house': 0.7, 'techno': 0.8, 'trance': 0.6,
        'pop': 0.4, 'rock': 0.5, 'jazz': 0.9
    }
    base = rhythm_map.get(genre.lower(), 0.5)
    # BPM influence: faster = more complex
    bpm_factor = min(1.0, (bpm - 60) / 140)
    return np.clip(base + (bpm_factor * 0.2), 0, 1)

def _calculate_spectral_centroid(self, genre: str, energy: float) -> float:
    """Calculate brightness/timbre"""
    # Electronic genres = higher spectral centroid
    electronic_genres = ['house', 'techno', 'trance', 'edm']
    base = 0.7 if genre.lower() in electronic_genres else 0.4
    return np.clip(base + (energy * 0.3), 0, 1)

def _calculate_harmonic_complexity(self, key: str) -> float:
    """Calculate key complexity"""
    # Minor keys generally more complex
    if 'A' in key:  # Minor key in Camelot
        return 0.6
    return 0.4  # Major key
```

### 2. OpenAI Enricher (src/analysis/openai_enricher.py)

#### Interface Principal
```python
class OpenAIEnricher:
    """OpenAI GPT-4 integration for metadata enrichment"""
    
    def __init__(self, api_key: str = None):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4"
        self.cache = {}
    
    def enrich_track(self, track_data: Dict, hamms_data: Dict) -> Dict:
        """Complete track enrichment using AI"""
        pass
    
    def analyze_genre(self, track_data: Dict, hamms_vector: List[float]) -> Dict:
        """Genre classification using AI"""
        pass
    
    def analyze_mood(self, track_data: Dict) -> Dict:
        """Mood and emotional analysis"""
        pass
```

#### Prompts Optimizados
```python
GENRE_ANALYSIS_PROMPT = """
You are a professional music analyst. Analyze the track characteristics and provide genre classification.

Track Information:
- Title: {title}
- Artist: {artist}
- BPM: {bpm}
- Key: {key}
- Energy: {energy}
- HAMMS Vector (12D): {hamms_vector}

Provide analysis in this exact JSON format:
{{
    "genre": "primary_genre",
    "subgenre": "specific_subgenre",
    "confidence": 0.95,
    "reasoning": "Brief explanation of classification"
}}

Focus on electronic music genres: House, Techno, Trance, Progressive, etc.
"""

MOOD_ANALYSIS_PROMPT = """
Analyze the emotional characteristics of this track:

Track: {title} by {artist}
BPM: {bpm}, Key: {key}, Energy: {energy}
Valence: {valence}, Danceability: {danceability}

Provide mood analysis in JSON format:
{{
    "mood": "primary_mood",
    "energy_level": "high/medium/low",
    "era": "estimated_era",
    "tags": ["tag1", "tag2", "tag3"],
    "context": "usage_context",
    "description": "brief_description"
}}
"""
```

### 3. Database Models (src/models/)

#### HAMMS Advanced Model
```python
class HAMMSAdvanced(Base):
    __tablename__ = "hamms_advanced"
    
    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    vector_12d = Column(Text)  # JSON: [0.1, 0.8, 0.7, ...]
    dimension_scores = Column(Text)  # JSON: {"bpm": 0.1, "key": 0.8}
    similarity_cache = Column(Text)  # Pre-computed similarities
    ml_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    track = relationship("TrackORM", back_populates="hamms_advanced")
```

#### AI Analysis Model
```python
class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    
    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    genre = Column(String)
    subgenre = Column(String)
    mood = Column(String)
    era = Column(String)
    tags = Column(Text)  # JSON array
    ai_confidence = Column(Float)
    openai_response = Column(Text)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    track = relationship("TrackORM", back_populates="ai_analysis")
```

### 4. UI Components (src/ui/components/)

#### HAMMS Radar Chart
```python
class HAMMSRadarChart(QWidget):
    """Interactive radar chart for 12D HAMMS visualization"""
    
    def __init__(self):
        super().__init__()
        self.web_view = QWebEngineView()  # Para Plotly
        self.setup_ui()
    
    def update_hamms_data(self, hamms_vector: List[float], dimension_names: List[str]):
        """Update radar chart with new HAMMS data"""
        # Generate Plotly radar chart
        fig = go.Figure(data=go.Scatterpolar(
            r=hamms_vector,
            theta=dimension_names,
            fill='toself',
            name='HAMMS v3.0'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            )
        )
        
        html = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html)
```

#### AI Analysis Panel
```python
class AIAnalysisPanel(QWidget):
    """Panel for displaying AI analysis results"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        self.ai_header = QLabel("🤖 AI Analysis (GPT-4)")
        self.ai_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Genre info
        self.genre_label = QLabel()
        self.mood_label = QLabel()
        self.era_label = QLabel()
        self.tags_label = QLabel()
        
        # AI insights text
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        
        # Action buttons
        self.refresh_btn = QPushButton("🔄 Re-analyze")
        self.edit_btn = QPushButton("✏️ Edit")
        self.save_btn = QPushButton("💾 Save")
        
        layout.addWidget(self.ai_header)
        layout.addWidget(self.genre_label)
        layout.addWidget(self.mood_label)
        layout.addWidget(self.era_label)
        layout.addWidget(self.tags_label)
        layout.addWidget(self.insights_text)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def update_ai_analysis(self, analysis: Dict):
        """Update panel with AI analysis results"""
        self.genre_label.setText(f"🎵 Genre: {analysis.get('genre')} ({analysis.get('confidence', 0)*100:.0f}% confidence)")
        self.mood_label.setText(f"🎭 Mood: {analysis.get('mood')}")
        self.era_label.setText(f"📅 Era: {analysis.get('era')}")
        self.tags_label.setText(f"🏷️ Tags: {', '.join(analysis.get('tags', []))}")
        self.insights_text.setText(analysis.get('description', ''))
```

## 🔄 **INTEGRATION WORKFLOW**

### Pipeline de Análisis Actualizado
```python
def enhanced_analysis_pipeline(file_path: str) -> Dict:
    """Enhanced analysis pipeline with HAMMS v3.0 + AI"""
    
    # 1. Basic audio analysis (existing)
    basic_results = analyze_track(file_path)
    
    # 2. HAMMS v3.0 calculation (new)
    hamms_analyzer = HAMMSAnalyzerV3()
    hamms_vector = hamms_analyzer.calculate_extended_vector(basic_results)
    
    # 3. Store HAMMS advanced data
    hamms_data = {
        'vector_12d': hamms_vector.tolist(),
        'dimension_scores': dict(zip(DIMENSION_NAMES, hamms_vector)),
        'ml_confidence': 0.95
    }
    
    # 4. AI enrichment (new)
    ai_enricher = OpenAIEnricher()
    ai_results = ai_enricher.enrich_track(basic_results, hamms_data)
    
    # 5. Combined results
    return {
        'basic': basic_results,
        'hamms_v3': hamms_data,
        'ai_analysis': ai_results
    }
```

### UI Integration Points
```python
# En MainWindow.__init__()
self.hamms_radar = HAMMSRadarChart()
self.ai_panel = AIAnalysisPanel()
self.center_panel.addWidget(self.hamms_radar)
self.right_panel.addWidget(self.ai_panel)

# En track selection handler
def on_track_selected(self, track_data):
    # Load HAMMS v3.0 data
    hamms_data = self.hamms_analyzer.get_hamms_data(track_data['id'])
    if hamms_data:
        self.hamms_radar.update_hamms_data(
            hamms_data['vector_12d'], 
            DIMENSION_NAMES
        )
    
    # Load AI analysis
    ai_data = self.storage.get_ai_analysis(track_data['id'])
    if ai_data:
        self.ai_panel.update_ai_analysis(ai_data)
```

## ⚙️ **CONFIGURACIÓN REQUERIDA**

### Environment Variables
```bash
# .env file
OPENAI_API_KEY=sk-...
HAMMS_CACHE_SIZE=1000
AI_BATCH_SIZE=5
AI_RETRY_ATTEMPTS=3
AI_TIMEOUT_SECONDS=30
```

### Configuration Files
```yaml
# config/hamms_v3_config.yaml
hamms_v3:
  dimensions:
    weights: *DIMENSION_WEIGHTS*
  similarity:
    algorithm: "weighted_euclidean_cosine"
    threshold: 0.7
  caching:
    enabled: true
    max_size: 1000
    ttl_seconds: 3600

# config/openai_config.yaml  
openai:
  model: "gpt-4"
  max_tokens: 1000
  temperature: 0.1
  batch_size: 5
  rate_limit:
    requests_per_minute: 60
    tokens_per_minute: 50000
```

## 🗄️ **DATABASE MIGRATIONS**

### Migration Script
```python
# migrations/001_hamms_v3_tables.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create hamms_advanced table
    op.create_table(
        'hamms_advanced',
        sa.Column('track_id', sa.Integer, sa.ForeignKey('tracks.id'), primary_key=True),
        sa.Column('vector_12d', sa.Text),
        sa.Column('dimension_scores', sa.Text),
        sa.Column('similarity_cache', sa.Text),
        sa.Column('ml_confidence', sa.Float),
        sa.Column('created_at', sa.DateTime, default=sa.func.current_timestamp())
    )
    
    # Create ai_analysis table
    op.create_table(
        'ai_analysis',
        sa.Column('track_id', sa.Integer, sa.ForeignKey('tracks.id'), primary_key=True),
        sa.Column('genre', sa.String),
        sa.Column('subgenre', sa.String),
        sa.Column('mood', sa.String),
        sa.Column('era', sa.String),
        sa.Column('tags', sa.Text),
        sa.Column('ai_confidence', sa.Float),
        sa.Column('openai_response', sa.Text),
        sa.Column('analysis_date', sa.DateTime, default=sa.func.current_timestamp())
    )
    
    # Create indices
    op.create_index('idx_hamms_track_id', 'hamms_advanced', ['track_id'])
    op.create_index('idx_ai_track_id', 'ai_analysis', ['track_id'])
    op.create_index('idx_ai_genre', 'ai_analysis', ['genre'])

def downgrade():
    op.drop_table('hamms_advanced')
    op.drop_table('ai_analysis')
```

## 🔧 **DEPLOYMENT STRATEGY**

### Phase 1: Core Implementation (8 hours)
1. HAMMSAnalyzerV3 class (3 hours)
2. Database models + migrations (2 hours)
3. OpenAI integration basics (3 hours)

### Phase 2: UI Components (6 hours)
1. HAMMS radar chart component (3 hours)
2. AI analysis panel (2 hours)
3. Integration with existing UI (1 hour)

### Phase 3: Pipeline Integration (4 hours)
1. Enhanced analysis workflow (2 hours)
2. Error handling + caching (1 hour)
3. Testing + validation (1 hour)

### Phase 4: Polish + Documentation (2 hours)
1. Configuration files (30 min)
2. Update documentation (1 hour)
3. Final testing (30 min)

**Total Estimated Time: 20 hours**

## ✅ **QUALITY GATES**

### Code Quality
- [ ] Type hints en todas las funciones públicas
- [ ] Docstrings con formato Google style
- [ ] Unit tests con >80% coverage
- [ ] Quality gates passing (ya implementado)

### Performance
- [ ] HAMMS calculation <500ms
- [ ] OpenAI API calls con timeout y retry logic
- [ ] Database queries optimizadas con indices
- [ ] UI updates sin blocking

### Integration
- [ ] Backward compatibility mantenida
- [ ] Existing workflows no afectados
- [ ] Error handling robusto
- [ ] Graceful degradation si OpenAI no disponible

---

**Plan Status**: ✅ READY FOR EXECUTION  
**Methodology**: Spec-Kit + POML + BMAD  
**Next Step**: Ejecutar TASKS.md