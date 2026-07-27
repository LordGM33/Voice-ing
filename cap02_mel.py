#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 2.5 · El espectrograma mel.

Como cambia el espectro a lo largo del tiempo, en la escala en la que oye el oido.
Es la representacion con la que trabajan casi todos los modelos de voz.

Uso:  python cap02_mel.py [ruta_wav]
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)


def elegir_audio():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    audios = sorted(list(SAMPLES.glob("*.wav")) + list(SAMPLES.glob("*.flac")))
    if audios:
        return audios[0]
    print("samples/ esta vacia: genero una vocal sintetica para la demostracion.")
    sr = 24_000
    t = np.linspace(0, 1.5, int(sr * 1.5), endpoint=False)
    x = sum((1.0 / k) * np.sin(2 * np.pi * 120 * k * t) for k in range(1, 25))
    x = 0.4 * x / np.max(np.abs(x))
    ruta = SAMPLES / "demo_vocal.wav"
    sf.write(ruta, x, sr)
    return ruta


def main():
    ruta = elegir_audio()
    x, sr = sf.read(ruta)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)

    S = librosa.feature.melspectrogram(y=x, sr=sr, n_mels=80, fmax=8000)
    S_db = librosa.power_to_db(S, ref=np.max)
    print(f"mel: {S_db.shape[0]} bandas x {S_db.shape[1]} ventanas de tiempo")
    print(f"rango: {S_db.min():.1f} a {S_db.max():.1f} dB")

    plt.figure(figsize=(10, 3.6))
    librosa.display.specshow(S_db, sr=sr, x_axis="time", y_axis="mel", fmax=8000)
    plt.colorbar(format="%+2.0f dB")
    plt.title(f"Espectrograma mel de {ruta.name}")
    plt.tight_layout()
    destino = OUTPUTS / "espectrograma_mel.png"
    plt.savefig(destino, dpi=140)
    print(f"escrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
