#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 61 a 63 · El reconocedor: cada palabra con su momento, cuanto tarda y en que idioma te oyo.

1) Transcribe con el momento de cada palabra (asi salen los subtitulos de la serie) y avisa de las
   palabras que duran cero: en la serie, esas eran las que habia que ir a escuchar.
2) Cuanto tarda por segundo de audio. En la serie: pequeño en la tarjeta 0,045; en el procesador 0,34;
   el grande, hasta 4,5 veces mas que el pequeño, con el mismo error en dos narraciones.
3) Sin decirle el idioma, cual creyo oir y con que seguridad. Si no es el tuyo, para.

Uso:  python cap11_reconocedor.py samples/mi_voz.wav [small|large-v3] [es]     (necesita faster-whisper)
"""
import sys
import time

import librosa


def reconocedor(tam):
    """En la tarjeta si la hay (7,5 veces mas rapido en la serie); si no, en el procesador."""
    from faster_whisper import WhisperModel
    try:
        return WhisperModel(tam, device="cuda", compute_type="float16"), "tarjeta"
    except (RuntimeError, ValueError):
        return WhisperModel(tam, device="cpu", compute_type="int8"), "procesador"


def palabras(asr, x, idioma):
    tramos, info = asr.transcribe(x, language=idioma, word_timestamps=True)
    return [p for t in tramos for p in t.words], info


def que_idioma(asr, x, esperado):
    """Episodio 63: lo deja adivinar y comprueba. No adivinar bien no da error: escribe otra cosa."""
    _, info = asr.transcribe(x)
    print(f"sin decirle el idioma: {info.language} ({info.language_probability:.1%})")
    if info.language != esperado:
        raise SystemExit(f"creyo oir {info.language}, no {esperado}: fija el idioma al transcribir")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    tam = sys.argv[2] if len(sys.argv) > 2 else "small"
    idioma = sys.argv[3] if len(sys.argv) > 3 else "es"
    x, _ = librosa.load(sys.argv[1], sr=16000, mono=True)
    asr, donde = reconocedor(tam)
    que_idioma(asr, x, idioma)
    t0 = time.perf_counter()
    lista, _ = palabras(asr, x, idioma)
    tarda = time.perf_counter() - t0
    for p in lista:
        aviso = "   <- dura cero: escuchala" if p.end - p.start < 0.01 else ""
        print(f"{p.start:7.2f} {p.end:7.2f} {p.word}{aviso}")
    print(f"\n{tam} en el {donde}: {tarda / (len(x) / 16000):.3f} s por segundo de audio, {len(lista)} palabras")


if __name__ == "__main__":
    main()
