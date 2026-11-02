#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 76 · Una referencia por estado: cambiar de emocion es cambiar de datos.

Prepara una voz con cada referencia (alegre.wav, cansado.wav... cada una con su .txt exacto), dice la
misma frase con cada una varias veces y compara ritmo y entonacion de lo generado. En la serie la
velocidad viajo de la referencia a la voz clonada; la entonacion quedo dentro del ruido entre tomas.
Por eso se miden varias tomas: una sola no distingue un estado de la suerte.

Necesita qwen-tts y el modelo descargado.
Uso:  python cap13_estados.py ruta/al/modelo samples/alegre.wav samples/cansado.wav [...]
"""
import statistics as st
import sys
from pathlib import Path

import numpy as np

from cap13_emocion import entonacion

FRASE = "Hoy te cuento como suena la misma frase cuando cambias de estado de animo."
TOMAS = 4


def motor(modelo):
    import torch
    from qwen_tts import Qwen3TTSModel
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    return Qwen3TTSModel.from_pretrained(modelo, device_map=dispositivo, dtype=torch.bfloat16)


def medir_estado(m, ref):
    voz = m.create_voice_clone_prompt(ref_audio=str(ref), ref_text=ref.with_suffix(".txt").read_text(
        encoding="utf-8").strip())
    ritmos, rangos = [], []
    for _ in range(TOMAS):
        wavs, sr = m.generate_voice_clone(FRASE, "Spanish", voice_clone_prompt=voz)
        x = np.asarray(wavs[0], dtype=np.float32)
        ritmos.append(len(FRASE.split()) / (len(x) / sr))
        rangos.append(entonacion(x, sr))
    return ritmos, rangos


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return
    refs = [Path(a) for a in sys.argv[2:]]
    falta = [r.with_suffix(".txt").name for r in refs if not r.with_suffix(".txt").exists()]
    if falta:
        sys.exit(f"Falta el texto exacto de: {', '.join(falta)}")
    try:
        m = motor(sys.argv[1])
    except ImportError as e:
        sys.exit(f"Falta el motor: {e}. Ver el Capitulo 8: entorno propio para el motor.")
    for ref in refs:
        ritmos, rangos = medir_estado(m, ref)
        print(f"{ref.stem:<14} {st.mean(ritmos):.2f} palabras/s (+-{st.stdev(ritmos):.2f}) | "
              f"{st.mean(rangos):.2f} semitonos (+-{st.stdev(rangos):.2f})")
    print("Si la diferencia entre estados es menor que el +- de cada uno, ese numero no viajo.")


if __name__ == "__main__":
    main()
