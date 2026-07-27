#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 2.6 y 8.1 · Reporte de audio.

La herramienta de diagnostico que se reutiliza durante todo el libro: describe un
audio en numeros y avisa de los dos problemas que no tienen arreglo posterior,
el recorte digital y el exceso de ruido de fondo.

Uso:  python cap02_reporte_audio.py [ruta_wav]
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


def reporte(x, sr):
    """Devuelve un diccionario con lo que hay que saber de un audio."""
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)
    pico = float(np.max(np.abs(x))) if len(x) else 0.0
    rms = float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0
    a_db = lambda v: 20 * np.log10(max(v, 1e-10))

    # piso de ruido frente a voz, por ventanas de 50 ms
    w = max(1, int(0.05 * sr))
    n = len(x) // w
    energia = np.sqrt(np.mean(x[:n * w].reshape(n, w) ** 2, axis=1)) if n else np.array([0.0])
    ruido = float(np.percentile(energia, 5))
    voz = float(np.percentile(energia, 90))

    f0, _, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0v = f0[~np.isnan(f0)]

    return {
        "duracion_s": round(len(x) / sr, 2),
        "sr": sr,
        "pico": round(pico, 3),
        "pico_dbfs": round(a_db(pico), 1),
        "rms_dbfs": round(a_db(rms), 1),
        "recorte_pct": round(float(np.mean(np.abs(x) > 0.999)) * 100, 3),
        "snr_db": round(a_db(voz) - a_db(ruido), 1),
        "silencio_pct": round(float(np.mean(energia < ruido * 2)) * 100, 1),
        "f0_mediana_hz": round(float(np.median(f0v)), 1) if len(f0v) > 10 else None,
        "varst": round(float(np.std(12 * np.log2(f0v / np.median(f0v)))), 2) if len(f0v) > 10 else None,
    }


def elegir_audio():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    audios = sorted(list(SAMPLES.glob("*.wav")) + list(SAMPLES.glob("*.flac")))
    if audios:
        return audios[0]
    print("samples/ esta vacia: genero un audio de demostracion.")
    sr = 24_000
    t = np.linspace(0, 2.0, int(sr * 2), endpoint=False)
    x = 0.4 * sum((1.0 / k) * np.sin(2 * np.pi * 120 * k * t) for k in range(1, 25))
    x = x / np.max(np.abs(x)) * 0.4
    ruta = SAMPLES / "demo_vocal.wav"
    sf.write(ruta, x, sr)
    return ruta


def main():
    ruta = elegir_audio()
    x, sr = sf.read(ruta)
    r = reporte(x, sr)
    print(f"\n{ruta.name}")
    for k, v in r.items():
        print(f"  {k:16s} {v}")

    print("\nlectura:")
    if r["recorte_pct"] > 0:
        print("  ATENCION: hay recorte digital, la grabacion esta saturada y no se arregla despues")
    else:
        print("  sin recorte digital")
    if r["snr_db"] < 25:
        print(f"  ATENCION: relacion senal/ruido baja ({r['snr_db']} dB), conviene regrabar mas en silencio")
    else:
        print(f"  ruido de fondo bajo ({r['snr_db']} dB de margen)")
    if r["rms_dbfs"] < -30:
        print("  nivel bajo, pero eso se corrige normalizando: no es motivo para regrabar")

    destino = OUTPUTS / f"reporte_{ruta.stem}.txt"
    destino.write_text("\n".join(f"{k}\t{v}" for k, v in r.items()), encoding="utf-8")
    print(f"\nescrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
