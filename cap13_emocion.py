#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 75 · La emocion, en tres numeros: cuanto sube y baja, a que ritmo y con que fuerza.

Para cada audio de samples/ (o los que le pases) con su .txt al lado: rango de entonacion en semitonos
(como cap05_entonacion.py), palabras por segundo y cuanto varia la energia en dB. Graba la misma
frase alegre, cansado y neutro y compara: en mis lecturas, de 3,95 a 5,04 semitonos y de 2,0 a 2,5
palabras por segundo. Si dos estados dan los mismos numeros, el motor no podra distinguirlos.

Uso:  python cap13_emocion.py [samples/alegre.wav samples/cansado.wav ...]
"""
import sys
from pathlib import Path

import librosa
import numpy as np

SAMPLES = Path(__file__).resolve().parent / "samples"


def entonacion(x, sr):
    f0, _, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]
    return float(np.std(12 * np.log2(f0 / np.median(f0)))) if len(f0) >= 10 else 0.0


def tres_numeros(ruta):
    x, sr = librosa.load(ruta, sr=24_000, mono=True)
    txt = ruta.with_suffix(".txt")
    ritmo = len(txt.read_text(encoding="utf-8").split()) / (len(x) / sr) if txt.exists() else float("nan")
    fuerza = float(np.std(20 * np.log10(librosa.feature.rms(y=x)[0] + 1e-9)))
    return entonacion(x, sr), ritmo, fuerza


def main():
    rutas = [Path(a) for a in sys.argv[1:]] or sorted(SAMPLES.glob("*.wav"))
    if not rutas:
        print(__doc__)
        return
    print(f"{'audio':<28} {'semitonos':>9} {'palabras/s':>10} {'energia dB':>10}")
    for r in rutas:
        st, ritmo, fuerza = tres_numeros(r)
        print(f"{r.name:<28} {st:9.2f} {ritmo:10.2f} {fuerza:10.2f}")
    print("palabras/s sale nan si falta el .txt con el texto exacto de ese audio.")


if __name__ == "__main__":
    main()
