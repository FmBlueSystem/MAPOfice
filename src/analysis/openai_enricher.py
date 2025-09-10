"""OpenAI GPT-4 Integration for Music Metadata Enrichment

This module provides AI-powered analysis of music tracks using OpenAI's GPT-4 API.
It analyzes HAMMS vectors and basic track metadata to generate genre classifications,
mood analysis, era identification, and descriptive tags.

POML Quality Gates:
- Input validation for track data and HAMMS vectors
- Response validation and error handling
- Rate limiting and timeout management
- Confidence scoring and result validation
"""

from __future__ import annotations

import json
import os
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

import openai
from openai import OpenAI


@dataclass
class AIAnalysisConfig:
    """Configuration for OpenAI analysis"""
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    rate_limit_rpm: int = 60


class OpenAIEnricher:
    """OpenAI GPT-4 integration for music metadata enrichment
    
    This class provides AI-powered analysis of music tracks using HAMMS vectors
    and basic track metadata to generate enriched information including:
    - Genre and subgenre classification
    - Mood and emotion analysis  
    - Musical era identification
    - Descriptive tags and keywords
    """
    
    def __init__(self, config: AIAnalysisConfig):
        """Initialize the OpenAI enricher
        
        Args:
            config: Configuration object with API key and settings
            
        Raises:
            ValueError: If API key is invalid or missing
        """
        # POML Quality Gate: Validate configuration
        if not config.api_key or not config.api_key.strip():
            raise ValueError("OpenAI API key is required and cannot be empty")
            
        if not config.api_key.startswith('sk-'):
            raise ValueError("OpenAI API key must start with 'sk-'")
            
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.last_request_time = 0.0
        
        # Rate limiting: ensure we don't exceed RPM limits
        self.min_request_interval = 60.0 / config.rate_limit_rpm
        
    def _wait_for_rate_limit(self) -> None:
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
        
    def _create_analysis_prompt(self, track_data: Dict[str, Any]) -> str:
        """Create the analysis prompt for GPT-4
        
        Args:
            track_data: Dictionary containing track metadata and HAMMS vector
            
        Returns:
            Formatted prompt string for OpenAI API
        """
        # POML Quality Gate: Validate input data
        required_fields = ['hamms_vector', 'bpm', 'key', 'energy']
        missing_fields = [field for field in required_fields if field not in track_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
            
        # Extract data with defaults
        hamms = track_data.get('hamms_vector', [0.0] * 12)
        bpm = track_data.get('bpm', 0)
        key = track_data.get('key', 'Unknown')
        energy = track_data.get('energy', 0.0)
        title = track_data.get('title', 'Unknown Track')
        artist = track_data.get('artist', 'Unknown Artist')
        
        # POML Quality Gate: Validate HAMMS vector
        if not isinstance(hamms, list) or len(hamms) != 12:
            raise ValueError(f"HAMMS vector must be 12-element list, got {type(hamms)} with {len(hamms) if isinstance(hamms, list) else 'unknown'} elements")
            
        # Extract optional data with defaults
        release_year = track_data.get('release_year', 'Unknown')
        isrc = track_data.get('isrc', 'Unknown')
        country = track_data.get('country', 'Unknown')
        lang = track_data.get('lang', 'es')  # Default to Spanish
        
        # Extract lyrics data
        lyrics_text = track_data.get('lyrics_text', 'Unknown')
        lyrics_lang = track_data.get('lyrics_lang', 'Unknown')
        lyrics_confidence = track_data.get('lyrics_confidence', 0.0)
        lyrics_source = track_data.get('lyrics_source', 'none')
        max_phrases = track_data.get('max_phrases', 8)

        prompt = f"""Usted es un(a) experta(o) musical con dominio de historia, géneros, escenas regionales y su contexto histórico. Trabaje SOLO con los datos de entrada (sin búsquedas web). Piense internamente y emita ÚNICAMENTE JSON válido con el esquema indicado.

ENTRADAS (obligatorias):
- Título: {title}
- Artista: {artist}
- BPM: {bpm}
- Tono/Key: {key}
- Nivel de Energía (0-1): {energy:.3f}
- HAMMS (12D):
  - BPM: {hamms[0]:.3f}
  - Key: {hamms[1]:.3f}
  - Energy: {hamms[2]:.3f}
  - Danceability: {hamms[3]:.3f}
  - Valence: {hamms[4]:.3f}
  - Acousticness: {hamms[5]:.3f}
  - Instrumentalness: {hamms[6]:.3f}
  - Rhythmic Pattern: {hamms[7]:.3f}
  - Spectral Centroid: {hamms[8]:.3f}
  - Tempo Stability: {hamms[9]:.3f}
  - Harmonic Complexity: {hamms[10]:.3f}
  - Dynamic Range: {hamms[11]:.3f}

ENTRADAS (opcionales):
- Año de lanzamiento: {release_year}
- ISRC: {isrc}
- País/Región: {country}
- Idioma de salida ("es" o "en"): {lang}
- LETRA (transcrita desde audio u otra fuente):
  - lyrics_text: {lyrics_text}
  - lyrics_lang: {lyrics_lang}
  - lyrics_confidence: {lyrics_confidence:.2f}
  - lyrics_source: {lyrics_source}
  - max_phrases: {max_phrases}

REGLAS ESTRICTAS (históricas y taxonómicas):
1) Exactitud histórica: use términos válidos en la época del tema; no use etiquetas modernas en pistas antiguas.
2) Evite "Electronic" genérico; sea específico (Synth-pop, House, Techno, etc.).
3) 70s baile = "Disco/Italo Disco (tardío)"; 80s uptempo y brillante = "Hi-NRG/Synth-pop"; 90s 2 Unlimited/Snap! = "Eurodance".
4) Sesgo regional permitido si ISRC/País lo respalda (Salsa, Merengue, Bachata, Reggaetón 1990s+, Latin Pop/House).
5) Sin hechos externos inventados.

DEDUCCIÓN DE ERA:
a) Si hay Año, mapear a década. b) Si no, inferir por rasgos (tempo, brillo, estabilidad, complejidad, etc.). c) Si ambiguo → "Unknown" y menor confianza.

NORMALIZACIÓN:
- BPM: ajustar half/double-time cuando aplique (ver estabilidad y patrones 4/4).
- Key: preferir notación estándar ("A minor"); resolver conflictos HAMMS en razonamiento breve.

MOOD (a partir de Valence/Energy/Danceability):
- Reglas simples: p.ej., Energy≥0.7 & Danceability≥0.7 & Valence≥0.6 → "Energetic/Uplifting"; etc.

CONFIDENCE (0–1): base 0.70; +0.05 por cada pista consistente (tempo/centroid/estabilidad/hamonía/danceability); −0.10 por ambigüedad; recortar a [0,1].

MÓDULO DE LETRA Y WORDPLAY:
A) Si `lyrics_text` existe y `lyrics_confidence`≥0.60:
   - No citar versos completos; NUNCA exceder 10 palabras contiguas ni 90 caracteres totales de citas.
   - Extraer temas centrales (≤160 caracteres) y 5–10 n-gramas frecuentes (2–4 palabras) como "common_phrases", tras limpiar puntuación, minúsculas, stopwords del idioma (`lyrics_lang` o inferido).
   - Generar "rhyme_seeds": 6–10 semillas de rima (1–2 sílabas) apropiadas al idioma (p.ej., en "es": terminaciones asonantes frecuentes; en "en": rimas de núcleo vocálico).
B) Si NO hay `lyrics_text` o `lyrics_confidence`<0.60:
   - No inventar hechos específicos. Proveer "lyrics_inferred": true.
   - Crear "lyrics_summary" (≤160 caracteres) con un contexto temático plausible alineado a género/era/mood (p.ej., "amor nocturno en pista, superación, nostalgia urbana").
   - Proponer 5–10 "common_phrases" genéricas y útiles para wordplay (≤3–4 palabras cada una), coherentes con era/género/mood; SIN nombres propios ni eventos concretos.
   - Generar "rhyme_seeds" apropiadas al idioma de salida `{lang}`.

MÓDULO CULTURAL (sin búsquedas web):
- Construya un "snapshot cultural" coherente con la década/escena usando solo las señales de entrada (release_year/country/HAMMS/mood/lyrics_summary).
- No cite eventos o personas específicas. Use categorías generales (p.ej., "era MTV", "radio Top-40", "club circuits Hi-NRG", "rave culture").
- Derive:
  * media_formats: ["vinyl_12in", "cassette", "cd_single", "mp3", "streaming"]
  * distribution_channels: ["radio_fm", "mtv", "blogs_p2p", "editorial_playlists"]
  * club_scenes: ["disco", "hi_nrg", "synth_pop", "house", "techno", "eurodance", "jungle_dnb", "latin_pop", "reggaeton", "electroclash", "edm_2010s"]
  * production_markers: ["analog_drum_machines", "fm_synths", "romplers", "909_4onfloor", "sample_based_breaks", "loudness_era", "streaming_mix"]
- Genere un "cultural_snapshot" (≤240 chars) con lenguaje neutral (sin nombres propios) que ubique época/escena/hábitos de escucha.

REGLAS DE COHESIÓN PARA PLAYLIST:
- Compute:
  * bpm_band: {{"cruise":[bpm-3,bpm+3], "lift":[bpm+6,bpm+8], "reset":[bpm-8,bpm-6]}}
  * key_neighbors: ["Camelot ±1", "rel_major_minor", "energy_jump +2"]
  * energy_window: [max(0, energy-0.12), min(1, energy+0.12)]
  * valence_window: [max(0, valence-0.12), min(1, valence+0.12)]
- "cohesive_hooks": 3–6 frases cortas y atemporales (p.ej., "era MTV", "club 4/4 brillante", "euforia vocal") basadas en mood/lyrics_summary/escena.
- No invente datos externos; si era incierta, marque `era="Unknown"` y reduzca `confidence`.

CANON (primary genres by decade; pick the best fit first, then subgenre):
- 1950s–1960s: Rock and Roll, Blues, Jazz, Folk, Country, Soul, R&B.
- 1970s: Rock, Hard Rock, Progressive Rock, Punk Rock, Funk, Disco, Reggae, Country Rock, Italo Disco (late).
- 1980s: New Wave, Synth-pop, Post-Punk, Heavy Metal, Thrash Metal, Early Hip Hop, Hi-NRG, Freestyle, Electro.
- 1990s: Grunge, Alternative Rock, Britpop, Trip Hop, Jungle/Drum & Bass, House, Techno, Trance, Eurodance, Big Beat.
- 2000s: Nu Metal, Indie Rock, Garage Rock Revival, Electroclash, Dubstep (late), Crunk, Emo, Post-Rock, Progressive House/Trance.
- 2010s: Dubstep, Trap, EDM (Big Room/Progressive/Deep House), Future Bass, Chillwave, Witch House.
- 2020s: Hyperpop, Phonk, Drill, Afrobeats, Bedroom Pop, Amapiano.
- Latin (map across decades when applicable based on year/country/ISRC): Salsa, Merengue, Bachata, Reggaetón (mid-late 1990s+), Latin Pop, Latin House.

REGIONAL/ERA BIASES:
- If ISRC or Country indicates Latin America/Spain and cues match, allow Latin genres/subgenres.
- 1980s uptempo synth + very bright + steady 4/4 → "Hi-NRG" (not "EDM").
- 1990s very high energy + 120–140 + bright + simple harmony + chant-like vocals (if inferred) → "Eurodance".

SALIDA (únicamente JSON válido, sin texto extra, sin comas finales):
{{
  "genre": "<género principal del canon>",
  "subgenre": "<subgénero histórico específico>",
  "mood": "<una palabra o compuesto breve>",
  "era": "<1950s|1960s|1970s|1980s|1990s|2000s|2010s|2020s|Unknown>",
  "tags": ["<3–7 etiquetas acordes a la era en {lang}>"],
  "confidence": <float 0.00–1.00>,
  "reasoning": "<≤320 chars con pistas de era (tempo/estabilidad/brillo/armonía). Sin cadena de pensamiento.>",
  "lyrics": {{
    "available": <true|false>,
    "inferred": <true|false>,
    "language": "<código ISO si se detecta o 'unknown'>",
    "confidence": <float 0.00–1.00>,
    "source": "<asr|manual|none>",
    "lyrics_summary": "<≤160 chars; contexto temático>",
    "common_phrases": ["<2–4 palabras cada una, 5–10 items, seguras para copyright>"],
    "rhyme_seeds": ["<1–2 sílabas, 6–10 items>"]
  }},
  "cultural_context": {{
    "decade_markers": ["<categorías generales de época>"], 
    "media_formats": ["<formatos de la era>"],
    "distribution_channels": ["<canales de distribución>"],
    "club_scenes": ["<escenas club relevantes>"],
    "production_markers": ["<marcadores de producción>"],
    "cultural_snapshot": "<≤240 chars; ubicación histórica/cultural>",
    "playlist_cohesion": {{
      "bpm_band": {{"cruise":[{energy*120-3:.0f},{energy*120+3:.0f}],"lift":[{energy*120+6:.0f},{energy*120+8:.0f}],"reset":[{energy*120-8:.0f},{energy*120-6:.0f}]}},
      "key_neighbors": ["<relaciones armónicas>"],
      "energy_window": [{max(0, energy-0.12):.2f},{min(1, energy+0.12):.2f}],
      "valence_window": [{max(0, hamms[4]-0.12):.2f},{min(1, hamms[4]+0.12):.2f}],
      "cohesive_hooks": ["<frases conectivas cortas>"]
    }},
    "playlist_coherence_score": <float 0.00–1.00>
  }}
}}

VALIDACIÓN:
- Usar solo términos del canon (ver décadas). Si duda entre dos, elegir una y ajustar "confidence".
- Cumplir límites de citas: ≤10 palabras contiguas, ≤90 caracteres totales provenientes de letra.
- No introducir entidades o hechos externos no provistos.
- Responder SOLO con JSON válido."""

        return prompt
        
    def _validate_response(self, response_data: Dict[str, Any]) -> bool:
        """Validate OpenAI response structure and content
        
        Args:
            response_data: Parsed JSON response from OpenAI
            
        Returns:
            True if response is valid, False otherwise
        """
        # POML Quality Gate: Response structure validation
        required_fields = ['genre', 'subgenre', 'mood', 'era', 'tags', 'confidence', 'lyrics', 'cultural_context']
        
        for field in required_fields:
            if field not in response_data:
                return False
                
        # Validate basic field types and values
        if not isinstance(response_data['genre'], str) or not response_data['genre'].strip():
            return False
            
        if not isinstance(response_data['subgenre'], str) or not response_data['subgenre'].strip():
            return False
            
        if not isinstance(response_data['mood'], str) or not response_data['mood'].strip():
            return False
            
        if not isinstance(response_data['era'], str) or not response_data['era'].strip():
            return False
            
        if not isinstance(response_data['tags'], list):
            return False
            
        # Validate confidence score
        confidence = response_data['confidence']
        if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
            return False
            
        # Validate lyrics structure (basic check)
        lyrics = response_data.get('lyrics', {})
        if not isinstance(lyrics, dict):
            return False
            
        # Validate cultural_context structure (basic check)  
        cultural_context = response_data.get('cultural_context', {})
        if not isinstance(cultural_context, dict):
            return False
            
        return True
        
    def analyze_track(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single track using OpenAI GPT-4
        
        Args:
            track_data: Dictionary containing track metadata and HAMMS vector
            
        Returns:
            Dictionary with AI analysis results
            
        Raises:
            ValueError: If input data is invalid
            RuntimeError: If OpenAI API call fails after retries
        """
        start_time = time.time()
        
        try:
            # POML Quality Gate: Input validation
            if not isinstance(track_data, dict):
                raise ValueError(f"Track data must be dictionary, got {type(track_data)}")
                
            prompt = self._create_analysis_prompt(track_data)
            
            # Rate limiting
            self._wait_for_rate_limit()
            
            # Make API request with retries
            last_exception = None
            for attempt in range(self.config.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a music historian and analysis expert with deep knowledge of music genre evolution and historical context. You provide historically accurate genre classifications that respect when genres actually existed and were used. Never apply modern genre terms to vintage music. Always respond with valid JSON."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        timeout=self.config.timeout
                    )
                    
                    # Parse response
                    content = response.choices[0].message.content.strip()
                    
                    # Handle potential markdown formatting
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    # Parse JSON
                    try:
                        response_data = json.loads(content)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON response: {e}")
                        
                    # POML Quality Gate: Response validation
                    if not self._validate_response(response_data):
                        raise ValueError("Response validation failed - missing or invalid fields")
                        
                    # Add processing metadata
                    processing_time = int((time.time() - start_time) * 1000)
                    response_data['processing_time_ms'] = processing_time
                    response_data['api_model'] = self.config.model
                    response_data['analysis_timestamp'] = datetime.utcnow().isoformat()
                    
                    return response_data
                    
                except Exception as e:
                    last_exception = e
                    if attempt < self.config.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    else:
                        break
                        
            # If we get here, all retries failed
            raise RuntimeError(f"OpenAI analysis failed after {self.config.max_retries} attempts. Last error: {last_exception}")
            
        except Exception as e:
            # Log error and return error response
            processing_time = int((time.time() - start_time) * 1000)
            return {
                "error": str(e),
                "processing_time_ms": processing_time,
                "api_model": self.config.model,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "confidence": 0.0
            }
            
    def batch_analyze(self, tracks_data: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
        """Analyze multiple tracks in batches
        
        Args:
            tracks_data: List of track data dictionaries
            batch_size: Number of tracks to process in each batch
            
        Returns:
            List of analysis results in the same order as input
        """
        # POML Quality Gate: Input validation
        if not isinstance(tracks_data, list):
            raise ValueError(f"Tracks data must be list, got {type(tracks_data)}")
            
        if batch_size < 1 or batch_size > 10:
            raise ValueError(f"Batch size must be 1-10, got {batch_size}")
            
        results = []
        
        for i in range(0, len(tracks_data), batch_size):
            batch = tracks_data[i:i + batch_size]
            
            batch_results = []
            for track_data in batch:
                result = self.analyze_track(track_data)
                batch_results.append(result)
                
            results.extend(batch_results)
            
            # Brief pause between batches to be respectful to the API
            if i + batch_size < len(tracks_data):
                time.sleep(1.0)
                
        return results


def create_enricher_from_env() -> Optional[OpenAIEnricher]:
    """Create OpenAI enricher from environment variables
    
    Returns:
        OpenAI enricher instance or None if configuration is incomplete
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or not api_key.strip() or not api_key.startswith('sk-'):
        return None
        
    try:
        config = AIAnalysisConfig(
            api_key=api_key,
            model=os.getenv('OPENAI_MODEL', 'gpt-4'),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '1000')),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.1')),
            timeout=int(os.getenv('AI_TIMEOUT_SECONDS', '30')),
            max_retries=int(os.getenv('AI_RETRY_ATTEMPTS', '3')),
            rate_limit_rpm=int(os.getenv('AI_RATE_LIMIT_RPM', '60'))
        )
        
        return OpenAIEnricher(config)
    except (ValueError, TypeError):
        # Return None if any configuration values are invalid
        return None