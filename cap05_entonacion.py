#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 19 y 24 · Cuanto se mueve tu voz, y la alarma de voz plana.

Mide cada audio de samples/ en semitonos, no en hercios: el mismo movimiento de tono
mide el doble de hercios en una voz aguda que en una grave, y en semitonos vale lo mismo.
La alarma de voz plana usa TU umbral, medido en tus grabaciones, no uno fijo.

Uso:  python cap05_entonacion.py               mide y te ensena la mas plana
      python cap05_entonacion.py --umbral 6    marca PLANA lo que quede por debajo
"""
import argparse
from pathlib import Path

import numpy as np
import librosa

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)


def medir(ruta):
    x, sr = librosa.load(ruta, sr=None, mono=True)
    f0, _, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]          # en el silencio no hay tono
    if len(f0) < 10:
        return None
    p5, p95 = np.percentile(f0, 5), np.percentile(f0, 95)
    return {"mediana_hz": float(np.median(f0)),
            "varst": float(np.std(12 * np.log2(f0 / np.median(f0)))),
            "rango_hz": float(p95 - p5),
            "rango_st": float(12 * np.log2(p95 / p5))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--umbral", type=float, help="rango minimo en semitonos (el tuyo)")
    args = ap.parse_args()

    audios = sorted(list(SAMPLES.glob("*.wav")) + list(SAMPLES.glob("*.flac")))
    if not audios:
        print("samples/ esta vacia. Graba un texto leido y el mismo contado con tus palabras,")
        print("ponlos ahi (leido.wav, contado.wav) y vuelve a ejecutar.")
        return

    print(f"{'archivo':30s} {'mediana':>8s} {'varST':>6s} {'rango Hz':>9s} {'rango st':>9s}")
    filas = {}
    for a in audios:
        r = medir(a)
        if r is None:
            print(f"{a.name[:30]:30s} sin voz suficiente para medir")
            continue
        filas[a.name] = r
        marca = ""
        if args.umbral is not None and r["rango_st"] < args.umbral:
            marca = "  PLANA"
        print(f"{a.name[:30]:30s} {r['mediana_hz']:6.0f}Hz {r['varst']:6.2f} "
              f"{r['rango_hz']:9.1f} {r['rango_st']:9.1f}{marca}")
    if not filas:
        return

    plana = min(filas, key=lambda k: filas[k]["rango_st"])
    print(f"\nLa mas plana: {plana} ({filas[plana]['rango_st']:.1f} st).")
    if args.umbral is None:
        print("Tu umbral sale de aqui: escucha tus grabaciones y ponlo por debajo de la mas")
        print("plana que des por buena. Luego: python cap05_entonacion.py --umbral <ese numero>")
    print("Compara las columnas: en hercios una voz grave parece plana con la misma melodia.")

    destino = OUTPUTS / "entonacion.txt"
    lineas = ["archivo\tmediana_hz\tvarst\trango_hz\trango_st"]
    lineas += [f"{k}\t{v['mediana_hz']:.1f}\t{v['varst']:.2f}\t{v['rango_hz']:.1f}\t"
               f"{v['rango_st']:.2f}" for k, v in filas.items()]
    destino.write_text("\n".join(lineas), encoding="utf-8")
    print(f"escrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
