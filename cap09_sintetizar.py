#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 9.2 · Sintetizar con tu voz clonada.

Es el unico script del taller que necesita GPU y el motor descargado. Reune todo
lo anterior: perfil de referencia, texto normalizado y preparado, sintesis con
clonacion, post-proceso sobrio y, si se pide, best-of-N.

Requisitos:
  pip install torch qwen-tts        (ver el Capitulo 8: entorno propio para el motor)
  el checkpoint del modelo descargado en local

Uso:
  python cap09_sintetizar.py "texto a decir"
  python cap09_sintetizar.py "texto" --ref samples/mi_voz.wav --n 3
  python cap09_sintetizar.py "texto" --modelo C:/ruta/al/modelo
"""
import argparse
import os
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

# se puede fijar con la variable de entorno VOICEING_MODELO
MODELO_POR_DEFECTO = os.environ.get("VOICEING_MODELO", "")
PAD_S = 0.4


def var_st(x, sr):
    f0, _, _ = librosa.pyin(x.astype(np.float32), fmin=60, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]
    if len(f0) < 10:
        return 0.0
    return float(np.std(12 * np.log2(f0 / np.median(f0))))


def post_proceso(wav, sr):
    """Sobrio a proposito: recortar silencios y normalizar. Nada de efectos."""
    wav = np.asarray(wav, dtype=np.float32)
    wav, _ = librosa.effects.trim(wav, top_db=30)
    pico = float(np.max(np.abs(wav))) or 1.0
    return wav * (0.89 / pico)


def elegir_referencia(arg):
    if arg:
        return Path(arg)
    audios = sorted(SAMPLES.glob("*.wav"))
    if not audios:
        print("No hay referencia. Pon tu grabacion en samples/ y su .txt al lado.")
        sys.exit(1)
    return audios[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("texto", help="lo que quieres que diga")
    ap.add_argument("--ref", default=None, help="audio de referencia (por defecto el primero de samples/)")
    ap.add_argument("--modelo", default=MODELO_POR_DEFECTO, help="carpeta del checkpoint del motor")
    ap.add_argument("--n", type=int, default=1, help="candidatos a generar y elegir el mejor")
    args = ap.parse_args()

    if not args.modelo:
        print("Indica la carpeta del modelo con --modelo o la variable VOICEING_MODELO.")
        sys.exit(1)

    ref_wav = elegir_referencia(args.ref)
    ref_txt = ref_wav.with_suffix(".txt")
    if not ref_txt.exists():
        print(f"Falta {ref_txt.name}: la transcripcion EXACTA de la referencia.")
        print("Sin ella la clonacion se degrada mucho (Capitulo 4).")
        sys.exit(1)
    referencia_texto = ref_txt.read_text(encoding="utf-8").strip()

    try:
        import torch
        from qwen_tts import Qwen3TTSModel
    except ImportError as e:
        print(f"Falta una dependencia del motor: {e}")
        print("Este script necesita GPU y el motor instalado. El resto del taller no.")
        sys.exit(1)

    print(f"referencia: {ref_wav.name}")
    print(f"cargando el modelo en GPU...")
    # CRITICO: sin device_map el modelo carga en CPU y va unas veinte veces mas lento.
    # Si el proceso ocupa varios GB de RAM del sistema en vez de VRAM, es esto.
    modelo = Qwen3TTSModel.from_pretrained(
        args.modelo, device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa")
    prompt = modelo.create_voice_clone_prompt(
        ref_audio=str(ref_wav), ref_text=referencia_texto, x_vector_only_mode=False)

    xr, srr = sf.read(ref_wav)
    objetivo = var_st(xr if xr.ndim == 1 else xr.mean(axis=1), srr)

    candidatos = []
    for i in range(max(1, args.n)):
        wavs, sr = modelo.generate_voice_clone(
            text=args.texto, language="Spanish", voice_clone_prompt=prompt)
        w = post_proceso(wavs[0], sr)
        v = var_st(w, sr)
        candidatos.append((abs(v - objetivo), v, w, sr))
        print(f"  candidato {i+1}: varST {v:.2f}")

    # se elige el mas cercano al humano, no el de varST mas alto:
    # un rango desbocado no es expresividad, es tono inestable
    _, mejor_v, audio, sr = min(candidatos, key=lambda c: c[0])
    pad = np.zeros(int(PAD_S * sr), dtype=np.float32)
    audio = np.concatenate([pad, audio, pad])

    destino = OUTPUTS / "sintesis.wav"
    sf.write(destino, audio, sr)
    print(f"\nreferencia humana varST {objetivo:.2f} | elegido {mejor_v:.2f}")
    print(f"duracion {len(audio)/sr:.1f} s")
    print(f"escrito: {destino.relative_to(BASE)}")
    print("\nComprueba el resultado con:  python cap07_wer.py outputs/sintesis.wav \"<tu texto>\"")


if __name__ == "__main__":
    main()
