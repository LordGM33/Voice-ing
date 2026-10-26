#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 65 y 66 · El texto de tu referencia: entero, y revisado a mano.

1) Episodio 65: ¿esta entero? Se habla a dos o tres palabras por segundo; si el texto da menos de 1,5
   por segundo de grabacion, falta texto. En la serie, clonar con el texto exacto dio un 4,5 % de error
   de palabras; con el del reconocedor, 3,0 %; recortado a 15 de 42 palabras, 99 %: el motor soltaba
   sonidos sin sentido.
2) Episodio 66: el reconocedor hace el borrador y tu lo corriges escuchando. El script te enseña solo
   las palabras en que no coinciden: esas se escuchan otra vez. La puntuacion no cuenta aqui.

Uso:  python cap11_referencia.py samples/mi_voz.wav samples/mi_voz.txt     (la revision necesita faster-whisper)
"""
import difflib
import sys
from pathlib import Path

import soundfile as sf

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from cap07_wer import normalizar  # noqa: E402

MINIMO = 1.5   # palabras por segundo


def entero(texto, segundos):
    """Episodio 65: con menos de 1,5 palabras por segundo, el texto no cubre la grabacion."""
    ritmo = len(texto.split()) / segundos
    print(f"{len(texto.split())} palabras en {segundos:.1f} s: {ritmo:.1f} por segundo")
    return ritmo >= MINIMO


def borrador(audio):
    from faster_whisper import WhisperModel
    asr = WhisperModel("small", device="cpu", compute_type="int8")
    return " ".join(t.text.strip() for t in asr.transcribe(audio, language="es")[0])


def diferencias(borr, corregido):
    """Episodio 66: palabra por palabra, solo lo que no coincide."""
    cambios = difflib.ndiff(normalizar(borr).split(), normalizar(corregido).split())
    return [c for c in cambios if c[0] in "+-"]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    texto = Path(sys.argv[2]).read_text(encoding="utf-8")
    if not entero(texto, sf.info(sys.argv[1]).duration):
        raise SystemExit("falta texto: escribe todo lo que dices en la grabacion, no un resumen")
    otras = diferencias(borrador(sys.argv[1]), texto)
    print("coinciden todas las palabras" if not otras else "escucha otra vez: " + " ".join(otras))


if __name__ == "__main__":
    main()
