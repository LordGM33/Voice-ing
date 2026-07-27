#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 4.3 · El perfil vocal.

Registra tus referencias en un unico archivo de configuracion. Cambiar de voz
pasa a ser cambiar un campo, no tocar codigo. Cada perfil exige el par
audio + transcripcion EXACTA, que es la leccion central del capitulo.

Para cada audio de samples/ busca su .txt con el mismo nombre. Si falta, avisa.

Uso:  python cap04_perfil_vocal.py
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)
PERFILES = OUTPUTS / "perfiles.json"


def medir(ruta):
    x, sr = sf.read(ruta)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)
    f0, _, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0v = f0[~np.isnan(f0)]
    return {
        "duracion_s": round(len(x) / sr, 1),
        "sr": sr,
        "f0_mediana_hz": round(float(np.median(f0v)), 1) if len(f0v) > 10 else None,
        "varst": round(float(np.std(12 * np.log2(f0v / np.median(f0v)))), 2) if len(f0v) > 10 else None,
    }


def main():
    audios = sorted(SAMPLES.glob("*.wav"))
    if not audios:
        print("samples/ esta vacia. Pon ahi tus grabaciones y sus transcripciones.")
        return

    perfiles, sin_texto = {}, []
    for a in audios:
        txt = a.with_suffix(".txt")
        if not txt.exists():
            sin_texto.append(a.name)
            continue
        transcripcion = txt.read_text(encoding="utf-8").strip()
        datos = medir(a)
        perfiles[a.stem] = {
            "estado": "candidato",
            "ref_wav": f"samples/{a.name}",
            "ref_text": transcripcion,
            **datos,
        }

    if not perfiles:
        print("No encontre ningun par audio + transcripcion.")
        print("Por cada grabacion.wav debe existir un grabacion.txt con lo que se dijo,")
        print("palabra por palabra. Sin eso la clonacion se degrada mucho.")
        if sin_texto:
            print("\nSin transcripcion:", ", ".join(sin_texto))
        return

    # el de mayor rango entonativo queda propuesto como activo
    activo = max(perfiles, key=lambda k: perfiles[k]["varst"] or 0)
    perfiles[activo]["estado"] = "activo"

    registro = {
        "_nota": "Cambiar de voz de referencia es cambiar el campo 'activo'.",
        "_transcripcion": "ref_text debe ser lo que se dijo, no lo que se pensaba decir.",
        "activo": activo,
        "perfiles": perfiles,
    }
    PERFILES.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(perfiles)} perfil(es) registrados\n")
    for nombre, p in perfiles.items():
        marca = "  <- activo" if p["estado"] == "activo" else ""
        print(f"  {nombre:26s} {p['duracion_s']:5.1f}s  F0 {p['f0_mediana_hz']}Hz  "
              f"varST {p['varst']}{marca}")
        print(f"     texto: {p['ref_text'][:64]}...")
    if sin_texto:
        print("\nSin transcripcion (ignorados):", ", ".join(sin_texto))
    print(f"\nescrito: {PERFILES.relative_to(BASE)}")


if __name__ == "__main__":
    main()
