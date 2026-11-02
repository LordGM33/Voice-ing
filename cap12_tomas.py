#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 72 y 73 · La mejor de varias tomas, y cuantas tomas valen la pena.

1) Genera la misma frase varias veces, mide la entonacion de cada toma (rango en semitonos, como
   cap05_entonacion.py) y se queda con la mas cercana a tu referencia, no con la de rango mas alto.
   Escribe outputs/mejor_toma.wav.
2) Con esas tomas, cuantas veces saldria plana (menos de 3 semitonos) la elegida si generaras 1, 3,
   5 u 8. En la serie: 53, 16, 4 y 0 %. Mas tomas cuestan mas tiempo: para donde deje de mejorar.

Necesita qwen-tts y el modelo descargado. La referencia lleva su .txt al lado.
Uso:  python cap12_tomas.py samples/mi_voz.wav ruta/al/modelo ["frase"] [tomas]
"""
import random
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

BASE = Path(__file__).resolve().parent
OUTPUTS = BASE / "outputs"
FRASE = "Hoy vamos a medir si tu voz clonada suena viva o suena plana."
PLANA = 3.0


def entonacion(x, sr):
    f0, _, _ = librosa.pyin(np.asarray(x, dtype=np.float32), fmin=60, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]
    return float(np.std(12 * np.log2(f0 / np.median(f0)))) if len(f0) >= 10 else 0.0


def generar_tomas(modelo, ref, frase, n):
    import torch
    from qwen_tts import Qwen3TTSModel
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    m = Qwen3TTSModel.from_pretrained(modelo, device_map=dispositivo, dtype=torch.bfloat16)
    voz = m.create_voice_clone_prompt(ref_audio=str(ref), ref_text=ref.with_suffix(".txt").read_text(
        encoding="utf-8").strip())
    tomas = []
    for i in range(n):
        wavs, sr = m.generate_voice_clone(frase, "Spanish", voice_clone_prompt=voz)
        tomas.append((wavs[0], sr, entonacion(wavs[0], sr)))
        print(f"  toma {i + 1}: {tomas[-1][2]:.2f} semitonos")
    return tomas


def boletos(rangos, tu_rango):
    """Episodio 73: elegir entre n tomas sacadas al azar de las que hay, muchas veces."""
    def elegida(n):
        return min(random.sample(rangos, n), key=lambda r: abs(r - tu_rango))
    for n in (1, 3, 5, 8):
        if n <= len(rangos):
            planas = sum(elegida(n) < PLANA for _ in range(5000)) / 5000
            print(f"  con {n} tomas: sale plana el {planas:.0%} de las veces")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    ref = Path(sys.argv[1])
    frase = sys.argv[3] if len(sys.argv) > 3 else FRASE
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    x, sr = librosa.load(ref, sr=None, mono=True)
    tu_rango = entonacion(x, sr)
    print(f"tu referencia: {tu_rango:.2f} semitonos")
    try:
        tomas = generar_tomas(sys.argv[2], ref, frase, n)
    except ImportError as e:
        sys.exit(f"Falta el motor: {e}. Ver el Capitulo 8: entorno propio para el motor.")
    mejor = min(tomas, key=lambda t: abs(t[2] - tu_rango))
    OUTPUTS.mkdir(exist_ok=True)
    sf.write(OUTPUTS / "mejor_toma.wav", mejor[0], mejor[1])
    print(f"elegida: {mejor[2]:.2f} semitonos -> outputs/mejor_toma.wav")
    boletos([t[2] for t in tomas], tu_rango)


if __name__ == "__main__":
    main()
