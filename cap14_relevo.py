#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 82 · ¿Llega a tiempo el relevo? La conversion de voz por trozos, como llega del microfono.

Corta tu audio en trozos (de 0,1 a 1 s), los convierte uno a uno con la conversion de juguete del Capitulo 10
(subir el tono) y mide cuanto tarda cada trozo frente a lo que dura. Por debajo de 1, llega a tiempo. Y mide
aparte la primera llamada: en la serie tardo de 3 a 10 s, porque el programa se prepara la primera vez. Por eso
el conversor se calienta antes de abrir el microfono. Un conversor de verdad pesa mucho mas que este juguete.

Necesita librosa.
Uso:  python cap14_relevo.py samples/mi_voz.wav [semitonos]
"""
import statistics as st
import sys
import time

import librosa
import numpy as np


def convertir(trozo, sr, semitonos):
    return librosa.effects.pitch_shift(trozo, sr=sr, n_steps=semitonos)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    semitonos = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
    x, sr = librosa.load(sys.argv[1], sr=24000, mono=True)
    t0 = time.perf_counter()
    convertir(np.zeros(sr // 2, dtype=np.float32), sr, semitonos)
    print(f"primera llamada (calentar): {time.perf_counter() - t0:.2f} s")
    for dura in (0.1, 0.25, 0.5, 1.0):
        n = int(dura * sr)
        trozos = [x[i:i + n] for i in range(0, len(x) - n, n)][:30]
        tiempos = []
        for t in trozos:
            t0 = time.perf_counter()
            convertir(t, sr, semitonos)
            tiempos.append(time.perf_counter() - t0)
        rtf = st.median(tiempos) / dura
        print(f"trozo de {dura:g} s: {rtf:.3f} s por segundo de audio (peor {max(tiempos) / dura:.3f})"
              f" -> {'llega a tiempo' if max(tiempos) < dura else 'NO llega'}")


if __name__ == "__main__":
    main()
