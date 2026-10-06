#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 41 y 42 · El contrato de audio: una sola frecuencia dentro, y a archivo en los bordes.

Lee tus audios de samples/, dice como vienen de verdad (frecuencia, canales, pico) y los deja en
outputs/ a 24 000 Hz, un canal, pico a -1 dB del maximo y enteros de 16 bits.
Con --mal_leido escribe ademas el primero leido a 16 000 Hz, para que oigas el error que nada avisa.

Uso:  python cap08_contrato_audio.py [--mal_leido]
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

SR = 24_000          # la frecuencia del contrato, la misma para todo el programa
MARGEN_DB = -1.0     # el pico se deja un decibelio por debajo del maximo


def al_contrato(ruta):
    """Lee preguntando la frecuencia, pasa a un canal y convierte solo si no coincide."""
    x, sr = sf.read(str(ruta), dtype="float32")
    canales = 1 if x.ndim == 1 else x.shape[1]
    if canales > 1:
        x = x.mean(axis=1)
    if sr != SR:
        x = librosa.resample(x, orig_sr=sr, target_sr=SR)
    return x, sr, canales


def al_borde(x, destino):
    """Ajusta el volumen en decimales y pasa a enteros una sola vez, al guardar."""
    pico = float(np.max(np.abs(x)))
    if pico > 0:
        x = x * (10 ** (MARGEN_DB / 20) / pico)
    sf.write(str(destino), x, SR, subtype="PCM_16")


def main():
    audios = sorted(list(SAMPLES.glob("*.wav")) + list(SAMPLES.glob("*.flac")))
    if not audios:
        print("Pon algun audio en samples/ y vuelve a ejecutar.")
        return
    print(f"{'archivo':30s} {'venia a':>9s} {'canales':>8s} {'pico dB':>8s}  ->  contrato")
    for a in audios:
        x, sr, canales = al_contrato(a)
        pico = 20 * np.log10(max(float(np.max(np.abs(sf.read(str(a))[0]))), 1e-9))
        al_borde(x, OUTPUTS / f"contrato_{a.stem}.wav")
        print(f"{a.name[:30]:30s} {sr:7d} Hz {canales:8d} {pico:8.2f}  ->  {SR} Hz, 1 canal, -1 dB")
    if "--mal_leido" in sys.argv:
        x, _ = sf.read(str(OUTPUTS / f"contrato_{audios[0].stem}.wav"), dtype="float32")
        sf.write(str(OUTPUTS / "mal_leido_a_16000.wav"), x, 16_000, subtype="PCM_16")
        print(f"\nescrito outputs/mal_leido_a_16000.wav: los mismos numeros leidos a 16 000.")
        print("Escuchalo: 1,5 veces mas largo y unos 7 semitonos mas grave. Ningun programa se queja.")


if __name__ == "__main__":
    main()
