#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 4.1 · Calidad de fuente: jitter, shimmer y HNR.

Mide la micro-imperfeccion de una voz. Sirve para dos cosas: comprobar que una
grabacion es sana y, mas adelante, comparar una sintesis contra la persona a la
que imita. Una sintesis mas perfecta que el humano es sospechosa.

Uso:  python cap04_calidad_fuente.py [ruta_wav]
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


SALTO = 128


def rachas_sonoras(fiable):
    """Tramos sonoros continuos de al menos 6 marcos, para no mezclar palabras distintas."""
    rachas, actual = [], []
    for i, ok in enumerate(fiable):
        if ok:
            actual.append(i)
        else:
            if len(actual) >= 6:
                rachas.append(actual)
            actual = []
    if len(actual) >= 6:
        rachas.append(actual)
    return rachas


def jitter_pct(f0, rachas):
    """Variacion de F0 entre tramos sonoros CONSECUTIVOS."""
    por_racha = [np.mean(np.abs(np.diff(f0[r]))) / np.mean(f0[r]) for r in rachas]
    return float(np.median(por_racha)) * 100


def shimmer_pct(x, sr, f0, rachas):
    """Variacion de la amplitud de pico entre CICLOS ADYACENTES.

    Se avanza periodo a periodo por la senal, no al ritmo de los tramos del analisis de F0.
    """
    sh_racha = []
    for r in rachas:
        ini_m, fin_m = r[0] * SALTO, min(len(x), (r[-1] + 1) * SALTO)
        periodo = int(sr / float(np.median(f0[r])))
        if periodo < 2 or fin_m - ini_m < periodo * 5:
            continue
        picos = [float(np.max(np.abs(x[p:p + periodo])))
                 for p in range(ini_m, fin_m - periodo, periodo)]
        picos = np.array([p for p in picos if p > 0])
        if len(picos) > 4:
            sh_racha.append(np.mean(np.abs(np.diff(picos))) / np.mean(picos))
    return float(np.median(sh_racha)) * 100 if sh_racha else 0.0


def hnr_marco(x, sr, centro, f0_i):
    """HNR de un marco por autocorrelacion: cuanta energia es periodica frente a ruido."""
    ventana = int(0.04 * sr)
    a, b = centro - ventana // 2, centro + ventana // 2
    if a < 0 or b > len(x):
        return None
    tramo = x[a:b] * np.hanning(b - a)
    tramo = tramo - np.mean(tramo)
    r = np.correlate(tramo, tramo, mode="full")[len(tramo) - 1:]
    if r[0] <= 0:
        return None
    r = r / r[0]
    lag = int(sr / f0_i)
    ini_l, fin_l = max(1, int(lag * 0.8)), min(len(r) - 1, int(lag * 1.2))
    if fin_l <= ini_l:
        return None
    pico = min(max(float(np.max(r[ini_l:fin_l])), 1e-6), 0.999)
    return 10 * np.log10(pico / (1 - pico))


def calidad_fuente(x, sr):
    """jitter y shimmer en porcentaje, HNR en dB, rango entonativo en semitonos.

    Las tres medidas se calculan SOLO sobre los tramos sonoros y consecutivos.
    Incluir silencios y transiciones es el error clasico: infla el shimmer y
    hunde el HNR hasta valores que no significan nada.
    """
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)

    f0, sonoro, prob = librosa.pyin(x, fmin=60, fmax=350, sr=sr, hop_length=SALTO)
    if sonoro is None or np.sum(sonoro) < 10:
        return None
    # solo tramos con voz clara: los bordes de palabra ensucian las tres medidas
    rachas = rachas_sonoras(sonoro & (prob > 0.70) & ~np.isnan(f0))
    if not rachas:
        return None

    jitter = jitter_pct(f0, rachas)
    shimmer = shimmer_pct(x, sr, f0, rachas)
    hnrs = [hnr_marco(x, sr, i * SALTO, f0[i]) for r in rachas for i in r]
    hnrs = [h for h in hnrs if h is not None]
    hnr = float(np.median(hnrs)) if hnrs else 0.0

    f0v = f0[~np.isnan(f0)]
    varst = float(np.std(12 * np.log2(f0v / np.median(f0v))))

    return {"f0_mediana_hz": round(float(np.median(f0v)), 1),
            "jitter_pct": round(jitter, 2),
            "shimmer_pct": round(shimmer, 2),
            "hnr_db": round(hnr, 1),
            "varst_semitonos": round(varst, 2),
            "tramos_sonoros": int(sum(len(r) for r in rachas))}


def elegir_audio():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    audios = sorted(list(SAMPLES.glob("*.wav")) + list(SAMPLES.glob("*.flac")))
    if not audios:
        print("Pon una grabacion tuya en samples/ y vuelve a ejecutar.")
        print("Si aun no tienes ninguna, corre antes: python cap03_fuente_filtro.py")
        sys.exit(1)
    return audios[0]


def main():
    ruta = elegir_audio()
    x, sr = sf.read(ruta)
    r = calidad_fuente(x, sr)
    if r is None:
        print(f"{ruta.name}: no se detecto voz suficiente para medir.")
        return

    print(f"\n{ruta.name}")
    for k, v in r.items():
        print(f"  {k:18s} {v}")

    print("\nNota: son aproximaciones suficientes para comparar grabaciones entre si.")
    print("Para precision clinica se usan herramientas de fonetica especializadas.")
    print("\nOJO con el material: los rangos clinicos (jitter por debajo del 1 % en voz sana)")
    print("se definen sobre una VOCAL SOSTENIDA (una 'aaa' larga y estable). Sobre habla corrida,")
    print("como una lectura, el numero se mezcla con la entonacion y no se compara con esos")
    print("rangos. Para comparar grabaciones entre si, usa siempre el mismo tipo de material.")
    print("  un jitter muy bajo con HNR muy alto es senal de voz sintetica demasiado limpia")

    destino = OUTPUTS / f"calidad_{ruta.stem}.txt"
    destino.write_text("\n".join(f"{k}\t{v}" for k, v in r.items()), encoding="utf-8")
    print(f"\nescrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
