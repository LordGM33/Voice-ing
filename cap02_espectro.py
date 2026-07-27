#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 2.3 · Del tiempo a la frecuencia.

Toma un audio y muestra que frecuencias lo componen (transformada de Fourier).
Guarda una grafica del espectro.

Uso:  python cap02_espectro.py [ruta_wav]
      sin argumento usa el primer audio de samples/
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)


def elegir_audio():
    """Usa el argumento, o el primer audio de samples/, o crea uno de demostracion."""
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
    print(f"audio: {ruta.name}  {len(x)/sr:.2f} s a {sr} Hz")

    # se analiza un tramo corto y estable del centro
    n = min(len(x), 4096)
    tramo = x[len(x) // 2: len(x) // 2 + n] * np.hanning(n)
    espectro = np.abs(np.fft.rfft(tramo))
    frecs = np.fft.rfftfreq(n, 1 / sr)
    db = 20 * np.log10(espectro + 1e-10)

    pico = frecs[int(np.argmax(espectro))]
    print(f"frecuencia dominante del tramo: {pico:.1f} Hz")

    plt.figure(figsize=(9, 3.4))
    plt.plot(frecs, db, linewidth=0.9)
    plt.xlim(0, 5000)
    plt.xlabel("frecuencia (Hz)")
    plt.ylabel("magnitud (dB)")
    plt.title(f"Espectro de {ruta.name}")
    plt.tight_layout()
    destino = OUTPUTS / "espectro.png"
    plt.savefig(destino, dpi=140)
    print(f"escrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
