#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 2.1 · El sonido como array.

Construye un tono puro desde cero para ver que "sonido" es, en este sistema,
un array de numeros. Guarda el WAV para que puedas escucharlo.

Uso:  python cap02_onda.py [frecuencia_hz]
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

SR = 24_000
FRECUENCIA = float(sys.argv[1]) if len(sys.argv) > 1 else 220.0


def main():
    t = np.linspace(0, 1.0, SR, endpoint=False)
    x = 0.5 * np.sin(2 * np.pi * FRECUENCIA * t)

    print(f"array: shape={x.shape}  dtype={x.dtype}")
    print(f"un segundo de audio a {SR} Hz son {len(x)} numeros")
    print(f"x[0]={x[0]:+.4f}  x[1]={x[1]:+.4f}  x[2]={x[2]:+.4f}   "
          f"(la presion en los instantes 0, 1/{SR} y 2/{SR} de segundo)")
    print(f"minimo {x.min():+.3f}  maximo {x.max():+.3f}")

    destino = OUTPUTS / f"tono_{int(FRECUENCIA)}hz.wav"
    sf.write(destino, x, SR)
    print(f"\nescrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
