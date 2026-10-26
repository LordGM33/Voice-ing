#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 64 · Otro reconocedor, mas ligero: Parakeet, en trozos de 8 segundos.

Licencia de los pesos CC BY 4.0 (atribucion). En la serie: 1,2 a 1,3 GB de la tarjeta y 0,03 s por
segundo de audio. Con trozos de 30 s escribia partes en ingles sin avisar; con trozos de 8 s, en
español, con un 12 y un 18 % de error (parte de ese error es del troceo fijo, que corta palabras).
Por eso al final se comprueba el idioma de lo escrito con una cuenta tosca de palabras comunes.

Uso:  python cap11_parakeet.py samples/mi_voz.wav [segundos_por_trozo] [carpeta_del_modelo]
      (necesita torch y transformers 5 o posterior; descarga nvidia/parakeet-tdt-0.6b-v3)
"""
import sys

import librosa

MODELO = "nvidia/parakeet-tdt-0.6b-v3"
ESPANOL = {"de", "la", "que", "el", "en", "y", "los", "se", "no", "un", "una", "es", "por", "con", "lo"}


def cargar(modelo=MODELO):
    import torch
    from transformers import AutoProcessor, ParakeetForTDT
    disp = "cuda" if torch.cuda.is_available() else "cpu"
    tipo = torch.float16 if disp == "cuda" else torch.float32
    proc = AutoProcessor.from_pretrained(modelo)
    return proc, ParakeetForTDT.from_pretrained(modelo, torch_dtype=tipo).to(disp), disp, tipo


def oir(modelo, proc, trozo, disp, tipo):
    import torch
    entrada = proc(trozo, sampling_rate=16000, return_tensors="pt").to(disp, tipo)
    with torch.inference_mode():
        ids = modelo.generate(**entrada)
    return proc.batch_decode(ids.sequences, skip_special_tokens=True)[0]


def parece_espanol(texto):
    p = texto.lower().split()
    return sum(w in ESPANOL for w in p) / max(1, len(p)) > 0.15


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    seg = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    x, _ = librosa.load(sys.argv[1], sr=16000, mono=True)
    proc, modelo, disp, tipo = cargar(sys.argv[3] if len(sys.argv) > 3 else MODELO)
    trozos = [x[i:i + seg * 16000] for i in range(0, len(x), seg * 16000)]
    textos = [oir(modelo, proc, t, disp, tipo) for t in trozos]
    for i, t in enumerate(textos):
        marca = "" if parece_espanol(t) else "   <- ¿no es español?"
        print(f"[{i * seg:4d} s] {t}{marca}")


if __name__ == "__main__":
    main()
