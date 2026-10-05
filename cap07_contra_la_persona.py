#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 38 · Tu voz clonada, medida contra ti y no contra los libros.

Graba una frase, genera la misma con tu voz clonada y compara: rango entonativo, cuanto calla
y cuanto es tono frente a soplo. Marca lo que se aleja mas de un 20 %: esa es tu siguiente tarea.
Para jitter y shimmer finos, `cap04_calidad_fuente.py` sobre los dos audios.

Uso:  python cap07_contra_la_persona.py humano.wav sintesis.wav
"""
import sys
from pathlib import Path

import numpy as np
import librosa

BASE = Path(__file__).resolve().parent
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)


def medir(ruta):
    x, sr = librosa.load(ruta, sr=None, mono=True)
    f0, sonoro, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]
    e = librosa.feature.rms(y=x)[0]
    db = 20 * np.log10(e / (e.max() + 1e-12) + 1e-12)
    armonico = librosa.effects.harmonic(x)
    resto = x - armonico
    return {
        "varST": float(np.std(12 * np.log2(f0 / np.median(f0)))),
        "rango_st": float(12 * np.log2(np.percentile(f0, 95) / np.percentile(f0, 5))),
        "silencio_pct": float(np.mean(db < -40) * 100),
        "tono_soplo_db": float(10 * np.log10(np.sum(armonico ** 2) / (np.sum(resto ** 2) + 1e-12))),
    }


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    humano, sintesis = medir(sys.argv[1]), medir(sys.argv[2])
    print(f"{'medida':16s} {'persona':>9s} {'sintesis':>9s} {'sint/pers':>10s}")
    filas = []
    for k in humano:
        r = sintesis[k] / humano[k] if humano[k] else float("nan")
        marca = "  <- se aleja" if abs(r - 1) > 0.2 else ""
        print(f"{k:16s} {humano[k]:9.2f} {sintesis[k]:9.2f} {r:10.2f}{marca}")
        filas.append(f"{k}\t{humano[k]:.3f}\t{sintesis[k]:.3f}\t{r:.3f}")
    print("\n1.00 es igual que la persona. En Eva se alejaban el rango (0.72) y el silencio (1.24),")
    print("y NO estaba 'demasiado limpia', que era lo que se sospechaba.")
    print("Una sola pareja no es un veredicto: repitelo con varias frases (cap07_una_muestra.py).")
    destino = OUTPUTS / "contra_la_persona.txt"
    destino.write_text("medida\tpersona\tsintesis\tratio\n" + "\n".join(filas), encoding="utf-8")
    print(f"escrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
