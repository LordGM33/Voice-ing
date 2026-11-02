#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 68, 69 y 71 · Donde corre tu modelo, cuanto tarda en arrancar y cuanto por frase.

1) Carga el motor una vez y mide cada arranque: los pesos y la voz (en la serie, de 9 a 20 s antes
   de la primera palabra; por eso se carga una vez y se generan muchas).
2) Comprueba donde quedaron los pesos y cuanta memoria del sistema ocupa el proceso. En el
   procesador, casi 8 GB y 4 veces mas lento: si la memoria se dispara, no esta en la tarjeta.
3) Para publicar manda el tiempo por segundo de audio de la frase entera; para conversar, cuanto
   tarda el primer trozo (hasta la primera coma).

Necesita qwen-tts y psutil, y el modelo descargado. La referencia lleva su .txt al lado (Capitulo 4).
Uso:  python cap12_donde_corre.py samples/mi_voz.wav ruta/al/modelo ["frase, con una coma"]
"""
import os
import sys
import time
from pathlib import Path

FRASE = "Hola, esto es una prueba corta para medir cuanto tarda."


def cargar(modelo, ref):
    """Episodio 71: los dos arranques, medidos por separado."""
    import torch
    from qwen_tts import Qwen3TTSModel
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    t0 = time.perf_counter()
    m = Qwen3TTSModel.from_pretrained(modelo, device_map=dispositivo, dtype=torch.bfloat16)
    t1 = time.perf_counter()
    voz = m.create_voice_clone_prompt(ref_audio=str(ref), ref_text=ref.with_suffix(".txt").read_text(
        encoding="utf-8").strip())
    t2 = time.perf_counter()
    print(f"cargar los pesos {t1 - t0:.1f} s | preparar tu voz {t2 - t1:.1f} s: una vez, no por frase")
    return m, voz


def donde(m):
    """Episodio 69: sin device_map se queda en el procesador sin avisar."""
    import psutil
    print(f"los pesos estan en: {next(m.model.parameters()).device}")
    print(f"memoria del proceso: {psutil.Process(os.getpid()).memory_info().rss / 2**30:.1f} GB")


def cuanto(m, voz, frase):
    """Episodio 68: entera para publicar; el primer trozo para conversar."""
    def generar(texto):
        t0 = time.perf_counter()
        wavs, sr = m.generate_voice_clone(texto, "Spanish", voice_clone_prompt=voz)
        return time.perf_counter() - t0, len(wavs[0]) / sr
    tarda, dura = generar(frase)
    primero, _ = generar(frase.split(",")[0])
    print(f"frase entera: {tarda / dura:.2f} s por segundo de audio ({tarda:.1f} s para {dura:.1f} s)")
    print(f"primer trozo: {primero:.1f} s hasta tener algo que decir")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    ref = Path(sys.argv[1])
    if not ref.with_suffix(".txt").exists():
        sys.exit(f"Falta {ref.with_suffix('.txt').name}: la transcripcion exacta de la referencia.")
    try:
        m, voz = cargar(sys.argv[2], ref)
    except ImportError as e:
        sys.exit(f"Falta el motor: {e}. Ver el Capitulo 8: entorno propio para el motor.")
    donde(m)
    cuanto(m, voz, sys.argv[3] if len(sys.argv) > 3 else FRASE)


if __name__ == "__main__":
    main()
