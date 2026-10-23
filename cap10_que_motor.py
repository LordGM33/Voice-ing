#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 54 y 56 · ¿Tu motor dibuja mel o escribe codigos? Y por cuantos bits pasa tu voz.

Lee el config.json de la carpeta de un modelo de voz y dice a que familia pertenece:
  - esquema clasico: un espectrograma de mel y un vocoder que lo pasa a onda;
  - codec neuronal: codigos discretos (varios libros) y un decodificador que los pasa a onda.
Si es un codec, calcula tramas por segundo y bits por segundo frente a un WAV de 16 bits.
Medido en la serie con Qwen3-TTS-Tokenizer-12Hz: 12,5 tramas/s x 16 libros = unos 2212 bit/s (174 veces menos).

Uso:  python cap10_que_motor.py ruta/a/la/carpeta/del/modelo
Solo biblioteca estandar.
"""
import json
import math
import sys
from pathlib import Path


def buscar(cfg, *claves):
    """Primer valor que aparezca con alguna de esas claves, mirando tambien un nivel por dentro."""
    for k in claves:
        if k in cfg:
            return cfg[k]
    for v in cfg.values():
        if isinstance(v, dict):
            for k in claves:
                if k in v:
                    return v[k]
    return None


def informe(cfg):
    sr = buscar(cfg, "output_sample_rate", "sampling_rate", "sample_rate")
    salto = buscar(cfg, "decode_upsample_rate", "hop_length", "hop_size")
    libros = buscar(cfg, "num_quantizers", "n_codebooks", "num_codebooks")
    tam = buscar(cfg, "codebook_size")
    mel = buscar(cfg, "num_mels", "n_mels", "mel_bins")
    if libros and tam and sr and salto:
        tramas = sr / salto
        semantico = buscar(cfg, "semantic_codebook_size")
        bits = (math.log2(semantico) + (libros - 1) * math.log2(tam)) if semantico else libros * math.log2(tam)
        print("familia: codec neuronal (codigos y decodificador)")
        print(f"  {tramas:g} tramas por segundo, {libros} numeros en cada una ({1000 / tramas:.0f} ms por trama)")
        print(f"  {bits * tramas:.0f} bits por segundo; un WAV de 16 bits a {sr} Hz son {sr * 16}")
        print(f"  {sr * 16 / (bits * tramas):.0f} veces menos")
    elif mel:
        print(f"familia: esquema clasico (mel de {mel} bandas y vocoder)")
    elif buscar(cfg, "tokenizer_type"):
        # El modelo principal de Qwen3-TTS solo nombra su codec; los numeros estan en la carpeta de este.
        nombre = buscar(cfg, "tokenizer_type")
        print(f"usa el codec '{nombre}': pasa la carpeta de ese tokenizador")
    else:
        print("no lo se por esta configuracion: busca 'mel' o 'codebook' en la ficha del modelo")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    carpeta = Path(sys.argv[1])
    cfg = json.loads((carpeta / "config.json").read_text(encoding="utf-8"))
    informe(cfg)


if __name__ == "__main__":
    main()
