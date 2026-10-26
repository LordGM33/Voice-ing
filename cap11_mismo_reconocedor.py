#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 67 · Para comparar versiones, siempre el mismo reconocedor.

El mismo audio dio un 3,0 % de error de palabras con un reconocedor y un 1,9 % con otro: el audio no
cambio, cambio quien lo escuchaba. Asi que se fija UN reconocedor, con sus ajustes, y todas las
versiones se miden con el contra el mismo guion. Las cifras se comparan entre si, no con las de otra
herramienta.

Uso:  python cap11_mismo_reconocedor.py guion.txt version_a.wav version_b.wav [...]   (necesita faster-whisper)
"""
import sys
from pathlib import Path

import librosa

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from cap07_wer import wer  # noqa: E402


def medir(asr, audio, guion):
    x, _ = librosa.load(audio, sr=16000, mono=True)
    return wer(guion, " ".join(t.text.strip() for t in asr.transcribe(x, language="es", beam_size=5)[0]))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    from faster_whisper import WhisperModel
    asr = WhisperModel("small", device="cpu", compute_type="int8")   # siempre el mismo
    guion = Path(sys.argv[1]).read_text(encoding="utf-8")
    errores = {Path(a).name: medir(asr, a, guion) for a in sys.argv[2:]}
    for nombre, e in sorted(errores.items(), key=lambda kv: kv[1]):
        print(f"{e:6.1%}  {nombre}")
    print("Con dos muestras por version, una diferencia de un punto puede ser ruido (episodio 39).")


if __name__ == "__main__":
    main()
