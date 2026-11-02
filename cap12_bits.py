#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 70 · Dieciseis o treinta y dos bits: medido en tu maquina, no en una tabla.

Carga el motor con cada tipo de numero (de uno en uno, para no tener los dos en memoria), genera las
mismas frases varias veces y da la mediana de segundos por segundo de audio y la memoria de la
tarjeta. En la serie: 16 bits 3,71 y 32 bits 3,23, con la mitad de memoria en 16. La diferencia
puede caer del otro lado en tu tarjeta: por eso se mide (Capitulo 7, nunca con una sola muestra).

Necesita qwen-tts y el modelo descargado. La referencia lleva su .txt al lado.
Uso:  python cap12_bits.py samples/mi_voz.wav ruta/al/modelo [tomas]
"""
import gc
import statistics as st
import sys
import time
from pathlib import Path

FRASES = ["Hola, esto es una prueba corta.", "La voz se mide en semitonos, no en hercios."]


def medir(modelo, ref, tipo, tomas):
    import torch
    from qwen_tts import Qwen3TTSModel
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    m = Qwen3TTSModel.from_pretrained(modelo, device_map=dispositivo, dtype=tipo)
    voz = m.create_voice_clone_prompt(ref_audio=str(ref), ref_text=ref.with_suffix(".txt").read_text(
        encoding="utf-8").strip())
    rtf = []
    for _ in range(tomas):
        for f in FRASES:
            t0 = time.perf_counter()
            wavs, sr = m.generate_voice_clone(f, "Spanish", voice_clone_prompt=voz)
            rtf.append((time.perf_counter() - t0) / (len(wavs[0]) / sr))
    memoria = torch.cuda.max_memory_allocated() / 2**30 if dispositivo != "cpu" else float("nan")
    del m, voz
    gc.collect()
    if dispositivo != "cpu":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    return rtf, memoria


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    ref, tomas = Path(sys.argv[1]), int(sys.argv[3]) if len(sys.argv) > 3 else 3
    try:
        import torch
    except ImportError as e:
        sys.exit(f"Falta el motor: {e}. Ver el Capitulo 8: entorno propio para el motor.")
    for nombre, tipo in (("16 bits", torch.bfloat16), ("32 bits", torch.float32)):
        rtf, memoria = medir(sys.argv[2], ref, tipo, tomas)
        print(f"{nombre}: mediana {st.median(rtf):.2f} s por segundo de audio "
              f"(de {min(rtf):.2f} a {max(rtf):.2f}, {len(rtf)} muestras) | tarjeta {memoria:.1f} GB")
    print("Si los rangos se pisan, la diferencia es ruido: quedate con el que gasta menos memoria.")


if __name__ == "__main__":
    main()
