from __future__ import annotations

from typing import Tuple
from pathlib import Path

import numpy as np
import librosa

# Make pyqtgraph optional to avoid blocking enhanced UI
try:
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtWidgets
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    # Dummy classes for when pyqtgraph is not available
    class QtWidgets:
        class QDialog:
            def __init__(self): pass
    pg = None


class VisualsDialog(QtWidgets.QDialog):
    def __init__(self, audio_path: str):
        super().__init__()
        self.setWindowTitle(f"Visuals - {Path(audio_path).name}")
        self.resize(900, 600)

        y, sr = librosa.load(audio_path, sr=None, mono=True)
        if y.size == 0:
            y = np.zeros(2048, dtype=float)
            sr = 44100

        # Spectrogram (log-mel like)
        S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
        S_db = librosa.amplitude_to_db(S, ref=np.max)

        # Chroma
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = chroma.mean(axis=1)

        layout = QtWidgets.QVBoxLayout(self)
        plt1 = pg.PlotWidget(title="Spectrogram (dB)")
        img = pg.ImageItem()
        plt1.addItem(img)
        img.setImage(S_db)  # y-axis bins, x-axis frames
        plt1.setLabel('bottom', 'Frames')
        plt1.setLabel('left', 'Bins')

        plt2 = pg.PlotWidget(title="Chroma (mean)")
        x = np.arange(12)
        bg = pg.BarGraphItem(x=x, height=chroma_mean, width=0.8)
        plt2.addItem(bg)
        plt2.setLabel('bottom', 'Pitch Class (C..B)')

        layout.addWidget(plt1)
        layout.addWidget(plt2)


def show_visuals(audio_path: str):
    if not PYQTGRAPH_AVAILABLE:
        print(f"WARNING: pyqtgraph not available, cannot show visuals for {audio_path}")
        return
    
    dlg = VisualsDialog(audio_path)
    dlg.exec()

