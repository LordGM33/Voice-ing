#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 50 · La emocion no se escribe: revisa el texto antes de mandarlo al motor.

Un modelo que clona no entiende instrucciones: un «(con alegria)» delante lo lee en voz alta
(medido en la serie: 20 de 20 tomas). Y sin tildes el acento se mueve: «queres» en vez de «querés»
(0 de 5 tomas bien). Este script lo detecta antes de sintetizar; no corrige nada por ti.

Uso:  python cap09_texto_limpio.py "texto a revisar"
      python cap09_texto_limpio.py guion.txt
"""
import re
import sys
from pathlib import Path

# Voseo sin tilde. Solo formas que sin tilde no existen con tu: «sabes» u «opinas» si existen,
# y marcarlas daria falsos avisos a quien escribe en tu.
VOSEO_SIN_TILDE = {"queres": "querés", "tenes": "tenés", "podes": "podés", "venis": "venís",
                   "decis": "decís", "pensas": "pensás"}


def problemas(texto):
    salida = []
    for acot in re.findall(r"\([^)]*\)|\[[^\]]*\]", texto):
        salida.append(f"acotacion {acot!r}: el motor la va a leer; quitala")
    if len(texto.split()) > 8 and not re.search(r"[áéíóúÁÉÍÓÚ]", texto):
        salida.append("ni una tilde en todo el texto: casi seguro que se perdieron")
    for palabra in re.findall(r"\b\w+\b", texto.lower()):
        bien = VOSEO_SIN_TILDE.get(palabra)
        if bien:
            salida.append(f"«{palabra}» sin tilde: el acento cae mal; escribe «{bien}»")
    for signo, apertura in (("?", "¿"), ("!", "¡")):
        if texto.count(signo) > texto.count(apertura):
            salida.append(f"falta algun «{apertura}»: la entonacion de la frase empieza ahi")
    return salida


def main():
    sys.stdout.reconfigure(encoding="utf-8")   # las comillas y las tildes, legibles en Windows
    if len(sys.argv) < 2:
        print(__doc__)
        return
    arg = sys.argv[1]
    texto = Path(arg).read_text(encoding="utf-8") if Path(arg).is_file() else arg
    encontrados = problemas(texto)
    for p in encontrados:
        print(f"  - {p}")
    print("texto limpio: listo para el motor" if not encontrados else
          f"\n{len(encontrados)} cosas que arreglar antes de sintetizar")


if __name__ == "__main__":
    main()
