#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 53 · Una perilla del motor se juzga por el reparto de varias tomas, no por la mejor.

Genera N tomas de la misma frase con los valores de fabrica y otras N con la perilla subida, mide la
entonacion (varST) de cada una y dice si los dos repartos se solapan. Si se solapan, la "mejora"
cabe en el azar. En la serie (20 tomas por lado) ninguna temperatura a 1,1 subio la entonacion.

Necesita GPU y el motor, como cap09_sintetizar.py.

Uso:  python cap09_perillas.py "frase" --modelo ruta/al/modelo [--ref samples/mi_voz.wav]
          [--perilla subtalker_temperature=1.1] [--n 5]
"""
import argparse
import statistics
import sys

from cap09_sintetizar import MODELO_POR_DEFECTO, elegir_referencia, post_proceso, var_st


def argumentos():
    ap = argparse.ArgumentParser()
    ap.add_argument("frase")
    ap.add_argument("--modelo", default=MODELO_POR_DEFECTO)
    ap.add_argument("--ref", default=None)
    ap.add_argument("--perilla", default="subtalker_temperature=1.1",
                    help="nombre=valor; temperature es la de que se dice, subtalker_temperature la de como suena")
    ap.add_argument("--n", type=int, default=5, help="tomas por lado (menos de 5 no dice nada)")
    a = ap.parse_args()
    if not a.modelo:
        sys.exit("Indica la carpeta del modelo con --modelo o la variable VOICEING_MODELO.")
    nombre, _, valor = a.perilla.partition("=")
    return a, {nombre: float(valor)}


def cargar(modelo_dir, ref_wav):
    import torch
    from qwen_tts import Qwen3TTSModel
    ref_txt = ref_wav.with_suffix(".txt")
    if not ref_txt.exists():
        sys.exit(f"Falta {ref_txt.name}: la transcripcion EXACTA de la referencia (Capitulo 4).")
    m = Qwen3TTSModel.from_pretrained(modelo_dir, device_map="cuda:0", dtype=torch.bfloat16,
                                      attn_implementation="sdpa")
    voz = m.create_voice_clone_prompt(ref_audio=str(ref_wav),
                                      ref_text=ref_txt.read_text(encoding="utf-8").strip())
    return m, voz


def tomas(m, voz, frase, n, **ajustes):
    salida = []
    for _ in range(n):
        wavs, sr = m.generate_voice_clone(frase, "Spanish", voice_clone_prompt=voz, **ajustes)
        salida.append(var_st(post_proceso(wavs[0], sr), sr))
    return salida


def main():
    a, perilla = argumentos()
    m, voz = cargar(a.modelo, elegir_referencia(a.ref))
    fabrica = tomas(m, voz, a.frase, a.n)
    subida = tomas(m, voz, a.frase, a.n, **perilla)
    for nombre, v in (("de fabrica", fabrica), (f"con {a.perilla}", subida)):
        print(f"{nombre:34s} media {statistics.mean(v):.2f}   de {min(v):.2f} a {max(v):.2f}")
    if min(subida) <= max(fabrica) and min(fabrica) <= max(subida):
        print("\nLos repartos se solapan: la diferencia cabe en el azar. Deja los valores de fabrica.")
    else:
        print("\nNo se solapan: repitelo con otras frases antes de creertelo (una muestra no basta, cap. 7).")


if __name__ == "__main__":
    main()
