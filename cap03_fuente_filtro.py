#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 3.1 y 3.2 · Fuente y filtro.

Sintetiza una vocal desde cero en dos pasos, como hace el cuerpo: primero la
senal glotica (la fuente, con sus imperfecciones) y despues el filtro de
formantes (el tracto vocal). Escuchar los dos WAV seguidos explica el modelo
mejor que cualquier parrafo.

Uso:  python cap03_fuente_filtro.py [vocal]     vocal: a, e, i, o, u
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import lfilter

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

SR = 24_000
# primeros dos formantes tipicos de cada vocal, en Hz
VOCALES = {"a": (730, 1090), "e": (530, 1840), "i": (270, 2290),
           "o": (570, 840), "u": (300, 870)}


def fuente_glotica(f0, dur, jitter=0.012, shimmer=0.03, soplo=0.02):
    """La vibracion de las cuerdas: armonicos decrecientes mas imperfeccion."""
    n = int(SR * dur)
    # jitter: la frecuencia no es constante, deriva ciclo a ciclo
    deriva = jitter * np.cumsum(np.random.randn(n)) / np.sqrt(n)
    f0_t = f0 * (1.0 + deriva)
    fase = 2 * np.pi * np.cumsum(f0_t) / SR
    x = sum((1.0 / k) * np.sin(k * fase) for k in range(1, 31))   # caida ~ -6 dB/octava
    x *= (1.0 + shimmer * np.random.randn(n))                     # shimmer: varia la amplitud
    x += soplo * np.random.randn(n)                               # aire que escapa
    return x / (np.max(np.abs(x)) + 1e-9)


def filtro_formantes(x, formantes, ancho=90.0):
    """El tracto vocal: resonancias que realzan ciertas frecuencias."""
    y = x.copy()
    for f in formantes:
        r = np.exp(-np.pi * ancho / SR)
        theta = 2 * np.pi * f / SR
        a = [1.0, -2 * r * np.cos(theta), r * r]
        y = lfilter([1.0 - r], a, y)
    return y / (np.max(np.abs(y)) + 1e-9)


def main():
    vocal = (sys.argv[1] if len(sys.argv) > 1 else "a").lower()
    if vocal not in VOCALES:
        print(f"vocal '{vocal}' no reconocida, uso 'a'. Opciones: {', '.join(VOCALES)}")
        vocal = "a"
    formantes = VOCALES[vocal]

    fuente = fuente_glotica(f0=120.0, dur=1.2)
    vocal_wav = filtro_formantes(fuente, formantes)

    sf.write(OUTPUTS / "fuente_glotica.wav", 0.6 * fuente, SR)
    sf.write(OUTPUTS / f"vocal_{vocal}.wav", 0.6 * vocal_wav, SR)

    print(f"vocal '{vocal}' con formantes en {formantes[0]} y {formantes[1]} Hz")
    print("  fuente_glotica.wav  ->  zumbido crudo, sin identidad")
    print(f"  vocal_{vocal}.wav        ->  el mismo zumbido pasado por el tracto vocal")
    print("\nLa fuente pone el tono; el filtro pone la vocal y la identidad.")
    print(f"escritos en: {OUTPUTS.relative_to(BASE)}")


if __name__ == "__main__":
    main()
