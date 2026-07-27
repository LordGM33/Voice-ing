#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 4.4 · Control de la grabacion de referencia.

Revisa TODOS los audios de samples/ y dice cuales sirven como referencia de
clonacion y cual es el mejor candidato. Correlo antes de gastar tiempo clonando.

Uso:  python cap04_qa_grabacion.py
"""
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

# criterios de aceptacion
SNR_MINIMO = 25.0        # dB de margen sobre el ruido de fondo
DUR_MINIMA = 6.0         # segundos
DUR_MAXIMA = 30.0        # mas largo no aporta y complica el recorte


def analizar(ruta):
    x, sr = sf.read(ruta)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)
    dur = len(x) / sr
    recorte = float(np.mean(np.abs(x) > 0.999)) * 100

    w = max(1, int(0.05 * sr))
    n = len(x) // w
    e = np.sqrt(np.mean(x[:n * w].reshape(n, w) ** 2, axis=1)) if n else np.array([1e-9])
    snr = 20 * np.log10(np.percentile(e, 90) / (np.percentile(e, 5) + 1e-12))

    f0, _, _ = librosa.pyin(x, fmin=60, fmax=350, sr=sr)
    f0v = f0[~np.isnan(f0)]
    varst = float(np.std(12 * np.log2(f0v / np.median(f0v)))) if len(f0v) > 10 else 0.0

    problemas = []
    if recorte > 0:
        problemas.append("recorte digital")
    if snr < SNR_MINIMO:
        problemas.append(f"ruido alto ({snr:.0f} dB)")
    if dur < DUR_MINIMA:
        problemas.append(f"muy corto ({dur:.1f} s)")
    if dur > DUR_MAXIMA:
        problemas.append(f"muy largo ({dur:.1f} s)")

    return {"archivo": ruta.name, "dur_s": round(dur, 1), "snr_db": round(float(snr), 1),
            "recorte_pct": round(recorte, 3), "varst": round(varst, 2),
            "sirve": not problemas, "problemas": ", ".join(problemas) or "-"}


def main():
    audios = sorted(list(SAMPLES.glob("*.wav")) + list(SAMPLES.glob("*.flac")))
    if not audios:
        print("samples/ esta vacia.")
        print("Graba tus tramos siguiendo la guia del Capitulo 4 y ponlos ahi.")
        return

    print(f"{'archivo':34s} {'dur':>6s} {'SNR':>7s} {'recorte':>8s} {'varST':>6s}  estado")
    filas = []
    for a in audios:
        r = analizar(a)
        filas.append(r)
        estado = "sirve" if r["sirve"] else r["problemas"]
        print(f"{r['archivo'][:34]:34s} {r['dur_s']:5.1f}s {r['snr_db']:6.1f} "
              f"{r['recorte_pct']:7.2f}% {r['varst']:6.2f}  {estado}")

    validos = [f for f in filas if f["sirve"]]
    print()
    if not validos:
        print("Ninguna grabacion pasa el control. Lo mas comun es ruido de fondo:")
        print("apaga ventiladores, cierra ventanas y repite la toma.")
        return

    mejor = max(validos, key=lambda f: f["varst"])
    print(f"Mejor candidata a referencia: {mejor['archivo']}  (varST {mejor['varst']})")
    print("Mas rango entonativo en la referencia significa mas expresividad en el clon.")
    print("La eleccion final la hace tu oido cuando compares las sintesis (Capitulo 9).")

    destino = OUTPUTS / "qa_grabacion.txt"
    lineas = ["archivo\tdur_s\tsnr_db\trecorte_pct\tvarst\tsirve\tproblemas"]
    lineas += ["\t".join(str(f[k]) for k in ("archivo", "dur_s", "snr_db", "recorte_pct",
                                             "varst", "sirve", "problemas")) for f in filas]
    destino.write_text("\n".join(lineas), encoding="utf-8")
    print(f"escrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
