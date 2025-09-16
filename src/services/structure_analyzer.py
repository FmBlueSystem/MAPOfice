"""
Music Structure Analyzer
Detects musical sections (intro, verse, chorus, drop, breakdown, etc.) using librosa.

Uses multiple techniques:
- Self-Similarity Matrix (SSM) for detecting repeated sections
- Spectral novelty for detecting changes
- Energy analysis for drops/breakdowns
- Harmonic analysis for verse/chorus distinction
"""

import numpy as np
import librosa
import librosa.display
from scipy.signal import find_peaks
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class StructureAnalyzer:
    """Analyzes musical structure to detect sections."""

    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        Initialize the structure analyzer.

        Args:
            sr: Sample rate for analysis
            hop_length: Hop length for feature extraction
        """
        self.sr = sr
        self.hop_length = hop_length

    def analyze(self, audio_path: str,
                existing_cues: Optional[List] = None) -> Dict:
        """
        Analyze the complete structure of a track.

        Args:
            audio_path: Path to audio file
            existing_cues: Existing cue points from MIK/Serato to refine

        Returns:
            Dictionary with detected sections and their properties
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sr, mono=True)

            # Extract multiple features for robust analysis
            features = self._extract_features(y, sr)

            # Detect section boundaries
            boundaries = self._detect_boundaries(features)

            # Classify sections
            sections = self._classify_sections(features, boundaries, y)

            # Refine with existing cues if available
            if existing_cues:
                sections = self._refine_with_cues(sections, existing_cues)

            # Detect special DJ-relevant points
            dj_points = self._detect_dj_points(features, sections)

            return {
                'sections': sections,
                'dj_points': dj_points,
                'boundaries': boundaries,
                'tempo': features.get('tempo', 120)
            }

        except Exception as e:
            logger.error(f"Failed to analyze structure: {e}")
            return {'sections': [], 'dj_points': [], 'boundaries': []}

    def _extract_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract multiple audio features for structure analysis."""

        features = {}

        # 1. Tempo and beats (essential for electronic music)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
        features['tempo'] = tempo
        features['beats'] = beats

        # 2. Chroma features (harmonic content)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
        features['chroma'] = chroma

        # 3. MFCC (timbre/instrumentation changes)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
        features['mfcc'] = mfcc

        # 4. RMS Energy (for drops/breakdowns)
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
        features['rms'] = rms

        # 5. Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)[0]
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=self.hop_length)

        features['spectral_centroid'] = spectral_centroid
        features['spectral_rolloff'] = spectral_rolloff
        features['spectral_contrast'] = spectral_contrast

        # 6. Zero crossing rate (percussiveness)
        zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)[0]
        features['zcr'] = zcr

        # 7. Onset strength (for detecting new sections)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        features['onset_strength'] = onset_env

        # 8. Tempogram (tempo stability)
        tempogram = librosa.feature.tempogram(y=y, sr=sr, hop_length=self.hop_length)
        features['tempogram'] = tempogram

        return features

    def _detect_boundaries(self, features: Dict) -> List[float]:
        """
        Detect section boundaries using multiple methods.
        """

        # 1. Self-Similarity Matrix approach
        ssm_boundaries = self._ssm_boundaries(features)

        # 2. Spectral novelty approach
        novelty_boundaries = self._novelty_boundaries(features)

        # 3. Energy-based boundaries
        energy_boundaries = self._energy_boundaries(features)

        # Combine and deduplicate boundaries
        all_boundaries = []

        # Weight different detection methods
        for b in ssm_boundaries:
            all_boundaries.append((b, 3))  # High confidence
        for b in novelty_boundaries:
            all_boundaries.append((b, 2))  # Medium confidence
        for b in energy_boundaries:
            all_boundaries.append((b, 1))  # Low confidence

        # Merge nearby boundaries (within 2 seconds)
        merged_boundaries = self._merge_boundaries(all_boundaries, threshold=2.0)

        return sorted(merged_boundaries)

    def _ssm_boundaries(self, features: Dict) -> List[float]:
        """Detect boundaries using Self-Similarity Matrix."""

        # Combine features for SSM
        chroma = features['chroma']
        mfcc = features['mfcc']

        # Stack features
        feature_matrix = np.vstack([chroma, mfcc[:5, :]])  # Use first 5 MFCCs

        # Compute self-similarity matrix
        ssm = librosa.segment.recurrence_matrix(
            feature_matrix,
            mode='affinity',
            metric='cosine',
            sparse=False
        )

        # Detect checkerboard patterns (indicating sections)
        # Using spectral clustering on the SSM
        k = min(8, ssm.shape[0] // 100)  # Adaptive number of segments
        if k > 1:
            boundaries = librosa.segment.agglomerative(feature_matrix, k=k)

            # Convert to time
            boundary_times = librosa.frames_to_time(
                boundaries,
                sr=self.sr,
                hop_length=self.hop_length
            )

            return boundary_times.tolist()

        return []

    def _novelty_boundaries(self, features: Dict) -> List[float]:
        """Detect boundaries using spectral novelty."""

        # Compute novelty curve from multiple features
        chroma = features['chroma']
        mfcc = features['mfcc']

        # Chroma novelty
        chroma_lag = librosa.segment.recurrence_matrix(
            chroma,
            width=3,
            mode='affinity',
            metric='cosine'
        )
        chroma_novelty = np.sum(np.diff(chroma_lag, axis=0), axis=1)

        # MFCC novelty (timbre changes)
        mfcc_lag = librosa.segment.recurrence_matrix(
            mfcc,
            width=3,
            mode='affinity',
            metric='euclidean'
        )
        mfcc_novelty = np.sum(np.diff(mfcc_lag, axis=0), axis=1)

        # Combine novelty curves
        novelty = chroma_novelty + mfcc_novelty

        # Find peaks in novelty
        peaks, properties = find_peaks(
            novelty,
            height=np.percentile(novelty, 75),
            distance=int(4 * self.sr / self.hop_length)  # Min 4 seconds between boundaries
        )

        # Convert to time
        boundary_times = librosa.frames_to_time(
            peaks,
            sr=self.sr,
            hop_length=self.hop_length
        )

        return boundary_times.tolist()

    def _energy_boundaries(self, features: Dict) -> List[float]:
        """Detect boundaries based on energy changes."""

        rms = features['rms']

        # Smooth energy
        from scipy.ndimage import gaussian_filter1d
        rms_smooth = gaussian_filter1d(rms, sigma=10)

        # Compute energy derivative
        energy_diff = np.diff(rms_smooth)

        # Find significant changes
        threshold = np.std(energy_diff) * 1.5

        # Find peaks in absolute difference
        peaks_up, _ = find_peaks(energy_diff, height=threshold)
        peaks_down, _ = find_peaks(-energy_diff, height=threshold)

        # Combine
        all_peaks = np.concatenate([peaks_up, peaks_down])

        # Convert to time
        boundary_times = librosa.frames_to_time(
            all_peaks,
            sr=self.sr,
            hop_length=self.hop_length
        )

        return boundary_times.tolist()

    def _merge_boundaries(self, boundaries_weighted: List[Tuple[float, int]],
                         threshold: float = 2.0) -> List[float]:
        """Merge nearby boundaries based on confidence weights."""

        if not boundaries_weighted:
            return []

        # Sort by time
        boundaries_weighted.sort(key=lambda x: x[0])

        merged = []
        current_cluster = [boundaries_weighted[0]]

        for boundary, weight in boundaries_weighted[1:]:
            # Check if close to current cluster
            if boundary - current_cluster[-1][0] < threshold:
                current_cluster.append((boundary, weight))
            else:
                # Process current cluster
                if current_cluster:
                    # Weighted average position
                    total_weight = sum(w for _, w in current_cluster)
                    weighted_pos = sum(b * w for b, w in current_cluster) / total_weight
                    merged.append(weighted_pos)

                # Start new cluster
                current_cluster = [(boundary, weight)]

        # Don't forget last cluster
        if current_cluster:
            total_weight = sum(w for _, w in current_cluster)
            weighted_pos = sum(b * w for b, w in current_cluster) / total_weight
            merged.append(weighted_pos)

        return merged

    def _classify_sections(self, features: Dict, boundaries: List[float],
                          y: np.ndarray) -> List[Dict]:
        """
        Classify each section based on its characteristics.
        """

        sections = []
        boundaries = [0] + boundaries + [len(y) / self.sr]  # Add start and end

        for i in range(len(boundaries) - 1):
            start_time = boundaries[i]
            end_time = boundaries[i + 1]

            # Get frame indices for this section
            start_frame = librosa.time_to_frames(start_time, sr=self.sr, hop_length=self.hop_length)
            end_frame = librosa.time_to_frames(end_time, sr=self.sr, hop_length=self.hop_length)

            # Analyze section characteristics
            section_features = self._analyze_section(
                features, start_frame, end_frame, i, len(boundaries) - 2
            )

            # Classify based on features
            label = self._classify_section_type(section_features, i, len(boundaries) - 2)

            sections.append({
                'start': start_time,
                'end': end_time,
                'label': label,
                'confidence': section_features.get('confidence', 0.5),
                'energy': section_features.get('avg_energy', 0),
                'harmonic_stability': section_features.get('harmonic_stability', 0),
                'percussiveness': section_features.get('percussiveness', 0)
            })

        return sections

    def _analyze_section(self, features: Dict, start_frame: int,
                        end_frame: int, section_idx: int, total_sections: int) -> Dict:
        """Analyze characteristics of a section."""

        analysis = {}

        # Energy analysis
        rms_section = features['rms'][start_frame:end_frame]
        if len(rms_section) > 0:
            analysis['avg_energy'] = np.mean(rms_section)
            analysis['energy_variance'] = np.var(rms_section)
            analysis['energy_trend'] = np.polyfit(range(len(rms_section)), rms_section, 1)[0] if len(rms_section) > 1 else 0

        # Harmonic analysis
        chroma_section = features['chroma'][:, start_frame:end_frame]
        if chroma_section.shape[1] > 0:
            # Harmonic stability (how consistent the harmony is)
            chroma_var = np.mean(np.var(chroma_section, axis=1))
            analysis['harmonic_stability'] = 1.0 / (1.0 + chroma_var)

            # Dominant pitch class
            avg_chroma = np.mean(chroma_section, axis=1)
            analysis['dominant_pitch'] = np.argmax(avg_chroma)

        # Spectral analysis
        centroid_section = features['spectral_centroid'][start_frame:end_frame]
        if len(centroid_section) > 0:
            analysis['brightness'] = np.mean(centroid_section)
            analysis['brightness_variance'] = np.var(centroid_section)

        # Percussiveness
        zcr_section = features['zcr'][start_frame:end_frame]
        onset_section = features['onset_strength'][start_frame:end_frame]
        if len(zcr_section) > 0:
            analysis['percussiveness'] = np.mean(zcr_section) * np.mean(onset_section)

        # Position in track
        analysis['position_ratio'] = section_idx / max(1, total_sections)
        analysis['is_first'] = section_idx == 0
        analysis['is_last'] = section_idx == total_sections - 1

        return analysis

    def _classify_section_type(self, features: Dict, section_idx: int,
                              total_sections: int) -> str:
        """
        Classify section type based on features.
        Optimized for electronic/dance music.
        """

        energy = features.get('avg_energy', 0)
        energy_trend = features.get('energy_trend', 0)
        brightness = features.get('brightness', 0)
        harmonic_stability = features.get('harmonic_stability', 0)
        percussiveness = features.get('percussiveness', 0)
        position = features.get('position_ratio', 0.5)

        # Normalize features (rough normalization based on typical values)
        energy_norm = min(1.0, energy * 10)  # RMS typically 0.0-0.1
        brightness_norm = min(1.0, brightness / 4000)  # Centroid typically 0-4000 Hz

        # Classification rules (optimized for electronic/dance music)

        # INTRO: Low energy at start
        if features.get('is_first') and energy_norm < 0.4:
            return 'intro'

        # OUTRO: At end with decreasing energy
        if features.get('is_last') and (energy_norm < 0.4 or energy_trend < -0.001):
            return 'outro'

        # BREAKDOWN: Very low energy in middle sections
        if 0.2 < position < 0.8 and energy_norm < 0.3:
            return 'breakdown'

        # BUILDUP: Rising energy and brightness
        if energy_trend > 0.001 and brightness_norm > 0.6:
            return 'buildup'

        # DROP: High energy, high percussiveness, follows buildup
        if energy_norm > 0.7 and percussiveness > 0.5:
            return 'drop'

        # CHORUS: High energy, stable harmony
        if energy_norm > 0.6 and harmonic_stability > 0.6:
            return 'chorus'

        # VERSE: Moderate energy, stable
        if 0.3 < energy_norm < 0.6 and harmonic_stability > 0.5:
            return 'verse'

        # BRIDGE: Transitional, moderate features
        if 0.4 < position < 0.7 and 0.4 < energy_norm < 0.6:
            return 'bridge'

        # Default
        return 'section'

    def _detect_dj_points(self, features: Dict, sections: List[Dict]) -> Dict:
        """
        Detect special points relevant for DJs.
        """

        dj_points = {
            'mix_in_point': None,
            'mix_out_point': None,
            'first_drop': None,
            'main_drop': None,
            'breakdown_start': None,
            'vocal_start': None,
            'loop_points': []
        }

        # Find first suitable mix-in point (after intro)
        for section in sections:
            if section['label'] in ['verse', 'buildup'] and section['start'] > 15:
                dj_points['mix_in_point'] = section['start']
                break

        # Find mix-out point (before outro or last breakdown)
        for section in reversed(sections):
            if section['label'] in ['verse', 'breakdown'] and section['end'] < sections[-1]['end'] - 15:
                dj_points['mix_out_point'] = section['start']
                break

        # Find drops
        drops = [s for s in sections if s['label'] == 'drop']
        if drops:
            dj_points['first_drop'] = drops[0]['start']
            # Main drop is usually the highest energy one
            main_drop = max(drops, key=lambda x: x.get('energy', 0))
            dj_points['main_drop'] = main_drop['start']

        # Find first breakdown
        breakdowns = [s for s in sections if s['label'] == 'breakdown']
        if breakdowns:
            dj_points['breakdown_start'] = breakdowns[0]['start']

        # Detect good loop points (stable 8-bar sections)
        tempo = features.get('tempo', 120)
        bar_duration = (60 / tempo) * 4  # 4 beats per bar
        eight_bar_duration = bar_duration * 8

        for section in sections:
            if section['label'] in ['verse', 'chorus'] and \
               (section['end'] - section['start']) >= eight_bar_duration:
                # Find 8-bar segments within section
                loop_start = section['start']
                while loop_start + eight_bar_duration <= section['end']:
                    dj_points['loop_points'].append({
                        'start': loop_start,
                        'end': loop_start + eight_bar_duration,
                        'bars': 8
                    })
                    loop_start += eight_bar_duration

        return dj_points

    def _refine_with_cues(self, sections: List[Dict],
                         existing_cues: List) -> List[Dict]:
        """
        Refine detected sections with existing cue points from MIK/Serato.
        """

        refined = sections.copy()

        for cue in existing_cues:
            cue_time = cue.position_ms / 1000 if hasattr(cue, 'position_ms') else cue.get('position', 0) / 1000
            cue_type = cue.type if hasattr(cue, 'type') else cue.get('type', '')
            cue_name = cue.name if hasattr(cue, 'name') else cue.get('name', '')

            # Map cue types to section labels
            label_map = {
                'intro': 'intro',
                'outro': 'outro',
                'drop': 'drop',
                'breakdown': 'breakdown',
                'buildup': 'buildup',
                'verse': 'verse',
                'chorus': 'chorus'
            }

            # Find closest section to this cue
            min_distance = float('inf')
            closest_section = None

            for section in refined:
                # Check if cue is within section
                if section['start'] <= cue_time <= section['end']:
                    closest_section = section
                    break

                # Or find closest boundary
                dist = min(abs(section['start'] - cue_time),
                          abs(section['end'] - cue_time))
                if dist < min_distance:
                    min_distance = dist
                    closest_section = section

            # Update section label if we have a match
            if closest_section and min_distance < 2.0:  # Within 2 seconds
                for key, value in label_map.items():
                    if key in cue_type.lower() or key in cue_name.lower():
                        closest_section['label'] = value
                        closest_section['confidence'] = min(1.0, closest_section.get('confidence', 0.5) + 0.3)
                        break

        return refined