#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 56 y 57 · Ida y vuelta por el codec del motor, y cuanto tarda el vocoder.

Convierte tu audio en los codigos del tokenizador de Qwen3-TTS y los devuelve a sonido. Dice cuantos
codigos salen por segundo y cuanto tarda cada mitad; escribe outputs/codec_ida_vuelta.wav para
escuchar. En la serie, decodificar costo 0,03 s por segundo de audio, frente a 2,4 de la sintesis
entera: el vocoder se lleva poco mas del 1 % del tiempo.

Necesita qwen-tts y el tokenizador descargado (Qwen3-TTS-Tokenizer-12Hz). Corre en GPU si la hay.
Uso:  python cap10_codec.py samples/mi_voz.wav ruta/a/Qwen3-TTS-Tokenizer-12Hz
"""
import sys
import time
from pathlib import Path

import librosa
import soundfile as sf

BASE = Path(__file__).resolve().parent
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)
SR = 24000


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    try:
        import torch
        from qwen_tts import Qwen3TTSTokenizer
    except ImportError as e:
        sys.exit(f"Falta el motor: {e}. Ver el Capitulo 8: entorno propio para el motor.")
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    tok = Qwen3TTSTokenizer.from_pretrained(sys.argv[2], device_map=dispositivo)
    x, _ = librosa.load(sys.argv[1], sr=SR, mono=True)
    segundos = len(x) / SR
    t0 = time.perf_counter()
    codigos = tok.encode(x, sr=SR)
    t1 = time.perf_counter()
    wavs, sr = tok.decode(codigos)
    t2 = time.perf_counter()
    print(f"{len(codigos.audio_codes[0]) / segundos:.1f} codigos por segundo, "
          f"{codigos.audio_codes[0].shape[-1]} numeros en cada uno ({dispositivo})")
    print(f"codificar {t1 - t0:.2f} s | decodificar {t2 - t1:.2f} s "
          f"= {(t2 - t1) / segundos:.3f} s por segundo de audio")
    destino = OUTPUTS / "codec_ida_vuelta.wav"
    sf.write(destino, wavs[0], sr)
    print(f"escrito: {destino.relative_to(BASE)}  (pasalo por cap07_wer.py y cap05_entonacion.py)")


if __name__ == "__main__":
    main()
