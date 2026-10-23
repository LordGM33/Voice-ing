#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 55 · La fase que falta: del mel al sonido con Griffin-Lim.

Saca el espectrograma de mel (80 bandas) de tu audio, lo devuelve a sonido inventando la fase y
compara las dos versiones con dos medidas:
  - la entonacion (varST, como cap05_entonacion.py), que en la serie cayo de 4,46 a 3,60 semitonos;
  - la distancia log-espectral, que solo mira la energia de cada banda y por eso puede dar la version
    reconstruida por MAS parecida al original justo cuando lo que se perdio es la fase.
Escribe outputs/griffin_lim.wav para que lo escuches al lado del original.

Uso:  python cap10_fase.py samples/mi_voz.wav
"""
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

BASE = Path(__file__).resolve().parent
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)
SR = 24000


def var_st(x, sr):
    f0, _, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]
    return float(np.std(12 * np.log2(f0 / np.median(f0)))) if len(f0) > 10 else 0.0


def distancia_db(a, b):
    n = min(len(a), len(b))
    A = np.abs(librosa.stft(a[:n], n_fft=1024, hop_length=256)) ** 2 + 1e-10
    B = np.abs(librosa.stft(b[:n], n_fft=1024, hop_length=256)) ** 2 + 1e-10
    return float(np.mean(np.sqrt(np.mean((10 * np.log10(A / B)) ** 2, axis=0))))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    x, _ = librosa.load(sys.argv[1], sr=SR, mono=True)
    mel = librosa.feature.melspectrogram(y=x, sr=SR, n_fft=1024, hop_length=256, n_mels=80)
    y = librosa.feature.inverse.mel_to_audio(mel, sr=SR, n_fft=1024, hop_length=256, n_iter=32)
    print(f"entonacion: original {var_st(x, SR):.2f} st | Griffin-Lim {var_st(y, SR):.2f} st")
    print(f"distancia al original: {distancia_db(x, y):.1f} dB (esta medida no ve la fase)")
    destino = OUTPUTS / "griffin_lim.wav"
    sf.write(destino, y, SR)
    print(f"escrito: {destino.relative_to(BASE)}  (escuchalo al lado del original)")


if __name__ == "__main__":
    main()
