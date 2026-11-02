#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 78, 79 y 81 · Conversar: cuando suena la primera palabra.

1) El parrafo entero de una vez frente a solo su primera clausula: para conversar manda la segunda.
   En la serie: entero, de 51 a 77 s; la primera clausula, de 5 a 7 s.
2) Trocear no ahorra, reparte: los trozos sumados tardan lo mismo o mas que el parrafo entero
   (de 73 a 77 s en la serie), pero el primero ya puede sonar mientras se generan los demas.
3) Una muletilla generada una vez y guardada suena al instante; generarla en el momento cuesta
   lo mismo que cualquier clausula (1,2 s de audio tardaron 4,6 s en la serie).

Necesita qwen-tts y el modelo descargado. La referencia lleva su .txt al lado.
Uso:  python cap13_conversar.py samples/mi_voz.wav ruta/al/modelo ["parrafo"]
"""
import re
import sys
import time
from pathlib import Path

PARRAFO = ("Cuando hablas con alguien, no esperas a que piense toda la respuesta: empieza a hablar, "
           "y mientras habla, piensa lo que sigue.")
MULETILLA = "Mmm, déjame ver."


def preparar(modelo, ref):
    import torch
    from qwen_tts import Qwen3TTSModel
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    m = Qwen3TTSModel.from_pretrained(modelo, device_map=dispositivo, dtype=torch.bfloat16)
    voz = m.create_voice_clone_prompt(ref_audio=str(ref), ref_text=ref.with_suffix(".txt").read_text(
        encoding="utf-8").strip())

    def generar(texto):
        t0 = time.perf_counter()
        m.generate_voice_clone(texto, "Spanish", voice_clone_prompt=voz)
        return time.perf_counter() - t0
    return generar


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    parrafo = sys.argv[3] if len(sys.argv) > 3 else PARRAFO
    try:
        generar = preparar(sys.argv[2], Path(sys.argv[1]))
    except ImportError as e:
        sys.exit(f"Falta el motor: {e}. Ver el Capitulo 8: entorno propio para el motor.")
    trozos = re.split(r"(?<=[.?!,:;])\s+", parrafo)
    entero = generar(parrafo)
    tiempos = [generar(t) for t in trozos]
    print(f"entero: {entero:.1f} s hasta la primera palabra")
    print(f"troceado en {len(trozos)}: {tiempos[0]:.1f} s hasta la primera; {sum(tiempos):.1f} s sumados")
    print(f"muletilla generada en el momento: {generar(MULETILLA):.1f} s; guardada en memoria: 0")


if __name__ == "__main__":
    main()
