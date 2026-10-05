#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 39 · Una muestra no es un veredicto.

Genera la misma frase varias veces con cada configuracion y ponlas en samples/ como A_1.wav,
A_2.wav... y B_1.wav, B_2.wav... Este script mide la expresividad (varST) de cada una y dice si
la diferencia entre A y B es mayor que lo que mueve el azar dentro de cada una.
En Eva, la misma configuracion dio de 2.12 a 3.54 semitonos.

Uso:  python cap07_una_muestra.py            compara A_* contra B_*
      python cap07_una_muestra.py X Y        compara X_* contra Y_*
"""
import sys
from pathlib import Path

import numpy as np
import librosa

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)


def var_st(ruta):
    x, sr = librosa.load(ruta, sr=None, mono=True)
    f0, _, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]
    return float(np.std(12 * np.log2(f0 / np.median(f0)))) if len(f0) > 10 else float("nan")


def grupo(prefijo):
    audios = sorted(SAMPLES.glob(f"{prefijo}_*.wav"))
    return [var_st(a) for a in audios]


def main():
    a, b = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("A", "B")
    va, vb = grupo(a), grupo(b)
    if len(va) < 3 or len(vb) < 3:
        print(f"Hacen falta al menos 3 muestras de cada lado en samples/ ({a}_1.wav... y {b}_1.wav...).")
        print(f"Hay {len(va)} y {len(vb)}. Con una de cada lado, cualquier resultado puede ser azar.")
        return
    for nombre, v in ((a, va), (b, vb)):
        print(f"{nombre}: {len(v)} muestras   media {np.mean(v):.2f}   de {min(v):.2f} a {max(v):.2f}"
              f"   (margen del azar {max(v) - min(v):.2f})")
    diferencia = abs(np.mean(vb) - np.mean(va))
    margen = max(max(va) - min(va), max(vb) - min(vb))
    print(f"\ndiferencia entre medias: {diferencia:.2f} semitonos")
    if diferencia < margen:
        print("cabe dentro de lo que mueve el azar: con estas muestras NO puedes decir que una gane.")
    else:
        print("es mayor que el margen del azar de cada lado: aqui si hay algo, pero confirmalo con mas.")
    destino = OUTPUTS / "una_muestra.txt"
    destino.write_text(f"{a}\t{va}\n{b}\t{vb}\ndiferencia\t{diferencia:.3f}\nmargen\t{margen:.3f}",
                       encoding="utf-8")
    print(f"escrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
