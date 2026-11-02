#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 87 · Declarar lo que es: que etiqueta de IA lleva dentro tu video.

Lee el paquete XMP escondido en el MP4 y dice su DigitalSourceType (la etiqueta de IPTC para maquinas):
  trainedAlgorithmicMedia                -> la pieza entera la genero una IA;
  compositeWithTrainedAlgorithmicMedia   -> mezcla de material generado y real.
Declara lo que tu pieza es, no lo que mejor detecta la red. En la serie, los 24 videos de los capitulos 10 a 13
dicen mezcla. Que una red lea esta etiqueta no esta garantizado: la declaracion que viaja siempre es el pie.

Solo biblioteca estandar.
Uso:  python cap14_declarar.py mi_video.mp4
"""
import re
import sys
from pathlib import Path


def leer_xmp(ruta):
    datos = Path(ruta).read_bytes()
    inicio, fin = datos.find(b"<x:xmpmeta"), datos.find(b"</x:xmpmeta>")
    return datos[inicio:fin + 12].decode("utf-8", "replace") if inicio >= 0 and fin > inicio else ""


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    xmp = leer_xmp(sys.argv[1])
    tipo = re.search(r"digitalsourcetype/(\w+)", xmp)
    if not tipo:
        raise SystemExit("sin etiqueta de IA dentro del archivo: declaralo al menos en el pie")
    print(f"dentro del archivo: {tipo.group(1)}")
    if tipo.group(1) == "trainedAlgorithmicMedia":
        print("dice que TODO es generado: si hay graficas o grabaciones reales, es falso")


if __name__ == "__main__":
    main()
