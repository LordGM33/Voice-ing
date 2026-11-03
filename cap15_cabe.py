#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 90 · ¿Cabe de verdad? Lo que dice la caja frente a lo que queda libre en tu tarjeta.

Para cada tarjeta: memoria total, la que queda libre ahora y si cabe lo que necesitas con un margen para el
escritorio (en la serie se comio de 1,6 a 1,9 GB de la tarjeta pequena; el libro decia de 0,4 a 1,4). Si te
pasas, Windows no da error: usa memoria normal y todo va mucho mas lento.

Necesita torch con CUDA.
Uso:  python cap15_cabe.py [GB que necesitas] [margen en GB]      (por ejemplo: 5.2 1.5)
"""
import sys


def main():
    necesito = float(sys.argv[1]) if len(sys.argv) > 1 else 5.2
    margen = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    try:
        import torch
    except ImportError as e:
        sys.exit(f"Falta torch: {e}")
    if not torch.cuda.is_available():
        sys.exit("No hay tarjeta con CUDA: el motor iria en el procesador (Capitulo 12, episodio 69)")
    for i in range(torch.cuda.device_count()):
        total = torch.cuda.get_device_properties(i).total_memory / 2**30
        libre = torch.cuda.mem_get_info(i)[0] / 2**30
        veredicto = "cabe" if libre >= necesito + margen else "NO cabe con margen"
        print(f"tarjeta {i} ({torch.cuda.get_device_name(i)}): {total:.1f} GB en la caja, {libre:.1f} libres "
              f"-> {veredicto} ({necesito:g} + {margen:g} GB)")


if __name__ == "__main__":
    main()
