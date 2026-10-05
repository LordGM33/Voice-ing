#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 16 y 17 · Veinte numeros que son tu timbre, y si dos tramos son la misma voz.

Compara pares de audios por coseno sobre sus MFCC, de dos formas para que veas el error:
con la media de los 20 coeficientes sale casi 1 para todo, porque el coeficiente 0 es
volumen y aplasta a los demas. Sin el 0 y tipificado, separa de verdad.

Uso:  python cap04_misma_voz.py               compara todos los audios de samples/
      python cap04_misma_voz.py a.wav b.wav   compara esos dos
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import librosa

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

def coeficientes(ruta):
    x, sr = librosa.load(ruta, sr=None, mono=True)
    return librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20)


def ficha_ingenua(m):
    return m.mean(axis=1)


def ficha_tipificada(m):
    # fuera el coeficiente 0, que es volumen, y cada uno a su escala
    return m[1:].mean(axis=1) / (m[1:].std(axis=1) + 1e-9)


def coseno(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def elegir_audios():
    if len(sys.argv) > 2:
        return [Path(sys.argv[1]), Path(sys.argv[2])]
    audios = sorted(list(SAMPLES.glob("*.wav")) + list(SAMPLES.glob("*.flac")))
    if len(audios) < 2:
        print("Hacen falta al menos dos audios en samples/.")
        print("Lo ideal: dos tramos tuyos y uno de otra persona (con su permiso).")
        sys.exit(1)
    return audios


def main():
    audios = elegir_audios()
    m = {a: coeficientes(a) for a in audios}
    print(f"{'par':52s} {'ingenua':>8s} {'sin 0':>8s}")
    filas = []
    for a, b in itertools.combinations(audios, 2):
        ing = coseno(ficha_ingenua(m[a]), ficha_ingenua(m[b]))
        tip = coseno(ficha_tipificada(m[a]), ficha_tipificada(m[b]))
        par = f"{a.name[:25]} / {b.name[:24]}"
        print(f"{par:52s} {ing:8.3f} {tip:8.3f}")
        filas.append(f"{a.name}\t{b.name}\t{ing:.3f}\t{tip:.3f}")

    print("\nLa columna 'ingenua' sale casi 1 en todos los pares: no mide identidad, mide volumen.")
    print("Antes de creerte una medida de similitud, pasale un par que SABES que es de dos")
    print("personas distintas. Si no lo separa, la medida no mide.")
    print("Mira la separacion, no un umbral fijo: con esta ficha la misma voz ronda 0.98, pero")
    print("dos voces clonadas distintas midieron 0.74 y 0.77, alrededor del 0.75 que se usa con")
    print("embeddings entrenados. Aqui ese umbral no decide.")
    print("Y es un apano casero: cambia de microfono o de habitacion y se cae. Un embedding")
    print("entrenado (ECAPA, capitulo 4 del libro) no.")

    destino = OUTPUTS / "misma_voz.txt"
    destino.write_text("a\tb\tingenua\tsin_0_tipificada\n" + "\n".join(filas),
                       encoding="utf-8")
    print(f"\nescrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
