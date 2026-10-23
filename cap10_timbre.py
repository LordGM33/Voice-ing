#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 58 a 60 · La conversion de voz cambia quien suena, no lo que se dice.

1) Cambia el tono de tu audio +-N semitonos (un cambio de timbre de juguete, no RVC) y pasa las
   versiones por el reconocedor: las palabras casi no cambian. En la serie, +-4 st: de 0 % a 6 % y 2 %.
2) La regla de decision del episodio 59: la conversion se queda solo si el parecido sube mas que lo
   que varia la medida. Sin una medida de parecido (un verificador de voces), no se decide.

Uso:  python cap10_timbre.py samples/mi_voz.wav [semitonos]      (necesita faster-whisper)
"""
import sys
from pathlib import Path

import librosa
import numpy as np

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from cap07_wer import wer  # noqa: E402

SR = 24000


def oir(asr, x):
    segs, _ = asr.transcribe(librosa.resample(x, orig_sr=SR, target_sr=16000), language="es")
    return " ".join(s.text.strip() for s in segs)


def usar_conversion(parecido_sin, parecido_con, ruido):
    """Episodio 59: si la mejora no supera lo que varia la medida, la conversion no se queda."""
    return parecido_con - parecido_sin > ruido


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    from faster_whisper import WhisperModel
    n = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
    asr = WhisperModel("small", device="cpu", compute_type="int8")
    x, _ = librosa.load(sys.argv[1], sr=SR, mono=True)
    original = oir(asr, x)
    for st in (-n, n):
        otra = librosa.effects.pitch_shift(x, sr=SR, n_steps=st)
        f0, _, _ = librosa.pyin(otra, fmin=60, fmax=500, sr=SR)
        print(f"{st:+.0f} st: tono {np.nanmedian(f0):.0f} Hz, error de palabras {wer(original, oir(asr, otra)):.1%}")
    print("Si son las palabras lo que falla, cambia de motor: la conversion no lo arregla.")


if __name__ == "__main__":
    main()
