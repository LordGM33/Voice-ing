#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 92 · Los resultados: la entonacion de todas tus narraciones, frente a tu referencia.

Mide el rango de entonacion (semitonos, como cap05_entonacion.py) de cada audio de una carpeta, da la mediana,
el minimo y el maximo, y cuenta cuantos quedan por debajo de tu umbral. En la serie: 63 episodios, mediana 4,22
frente a 4,59 de la referencia, ninguno por debajo de 4; y 20 de ellos se narraron mas de una vez.

Necesita librosa.
Uso:  python cap15_resultados.py carpeta_de_narraciones [referencia.wav] [umbral]
"""
import statistics as st
import sys
from pathlib import Path

import librosa
import numpy as np


def entonacion(ruta):
    x, sr = librosa.load(ruta, sr=24000, mono=True)
    f0, _, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]
    return float(np.std(12 * np.log2(f0 / np.median(f0)))) if len(f0) >= 10 else 0.0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    umbral = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    valores = {}
    for wav in sorted(Path(sys.argv[1]).glob("*.wav")):
        valores[wav.stem] = entonacion(wav)
        print(f"{wav.stem:40s} {valores[wav.stem]:.2f}")
    if not valores:
        sys.exit("no hay .wav en esa carpeta")
    v = list(valores.values())
    print(f"\n{len(v)} audios: mediana {st.median(v):.2f}, de {min(v):.2f} a {max(v):.2f}; "
          f"{sum(x < umbral for x in v)} por debajo de {umbral:g}")
    if len(sys.argv) > 2:
        print(f"tu referencia: {entonacion(sys.argv[2]):.2f}")


if __name__ == "__main__":
    main()
