#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 86 y 88 · El filtro de salida, y fallar dentro del personaje.

1) Revisa el texto antes de sintetizarlo con una lista de palabras prohibidas, como palabras enteras: el filtro
   del libro buscaba trozos y en la serie freno 27 de 118 guiones buenos («odio» dentro de «episodio»).
2) Pasalo por textos que sabes buenos (una carpeta de .txt) y cuenta cuantos frena por error: ni las palabras
   enteras entienden lo que lees («el motor arma un molde» es el verbo armar).
3) Si frena, la voz no se calla ni lee un error: dice una frase del personaje, generada antes y guardada.

Solo biblioteca estandar.
Uso:  python cap14_filtro.py "texto a revisar"
      python cap14_filtro.py --buenos carpeta_con_txt
"""
import re
import sys
from pathlib import Path

PROHIBIDAS = ["odio", "arma", "mata", "droga"]   # cambia la lista por la de tu proyecto
FRASE_DEL_PERSONAJE = "Mejor cambiemos de tema, va."


def frenan(texto, enteras=True):
    bajo = texto.lower()
    if enteras:
        return [p for p in PROHIBIDAS if re.search(rf"\b{p}\b", bajo)]
    return [p for p in PROHIBIDAS if p in bajo]


def buenos(carpeta):
    textos = [f.read_text(encoding="utf-8") for f in sorted(Path(carpeta).glob("*.txt"))]
    trozos = sum(bool(frenan(t, enteras=False)) for t in textos)
    enteras = [(f.name, frenan(f.read_text(encoding="utf-8"))) for f in sorted(Path(carpeta).glob("*.txt"))]
    enteras = [e for e in enteras if e[1]]
    print(f"{len(textos)} textos buenos: buscando trozos frena {trozos}; con palabras enteras, {len(enteras)}")
    for nombre, palabras in enteras:
        print(f"  {nombre}: {palabras}  <- miralo a mano")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    if sys.argv[1] == "--buenos":
        buenos(sys.argv[2])
        return
    texto = " ".join(sys.argv[1:])
    malas = frenan(texto)
    if malas:
        print(f"frenado por {malas}: la voz dice «{FRASE_DEL_PERSONAJE}» y el texto va a revisar")
    else:
        print("seguro: se sintetiza")


if __name__ == "__main__":
    main()
