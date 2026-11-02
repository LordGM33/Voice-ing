#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 80 · El audio que recibe el avatar: que cumpla el contrato antes de entregarlo.

Comprueba frecuencia, canales y pico (el contrato del Capitulo 8, cap08_contrato_audio.py) y mide el
silencio al principio y al final: el avatar mueve la boca desde el primer instante del fichero, asi
que un silencio largo delante desincroniza. En la serie: 24 000 Hz, un canal; 0,42 y 0,47 s.

Necesita numpy y soundfile.
Uso:  python cap13_avatar.py outputs/sintesis.wav [frecuencia]
"""
import sys

import numpy as np
import soundfile as sf

UMBRAL = 0.01


def revisar(x, sr, esperada):
    fallos = []
    if sr != esperada:
        fallos.append(f"frecuencia {sr} Hz, el avatar espera {esperada}")
    if x.ndim != 1:
        fallos.append(f"{x.shape[1]} canales, el avatar espera uno")
    if np.abs(x).max() >= 0.9:
        fallos.append(f"pico {np.abs(x).max():.2f}: deja margen, por debajo de 0,9")
    return fallos


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    esperada = int(sys.argv[2]) if len(sys.argv) > 2 else 24_000
    x, sr = sf.read(sys.argv[1])
    voz = np.flatnonzero(np.abs(x if x.ndim == 1 else x.mean(axis=1)) > UMBRAL)
    if len(voz) == 0:
        sys.exit("no hay voz: todo esta por debajo del umbral")
    print(f"{sr} Hz, {1 if x.ndim == 1 else x.shape[1]} canal(es), {len(x) / sr:.2f} s")
    print(f"silencio: {voz[0] / sr:.2f} s al principio, {(len(x) - voz[-1]) / sr:.2f} s al final")
    fallos = revisar(x, sr, esperada)
    if fallos:
        raise SystemExit("no se entrega: " + "; ".join(fallos))
    print("cumple el contrato")


if __name__ == "__main__":
    main()
