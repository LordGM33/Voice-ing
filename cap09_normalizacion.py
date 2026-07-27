#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 9.1 · Normalizacion de texto en espanol.

Lo que se escribe no es lo que se dice. Numeros, horas, porcentajes, direcciones
web y arrobas se escriben de una forma y se pronuncian de otra. Si no se
convierten antes, el motor improvisa, y suele improvisar mal.

Uso:  python cap09_normalizacion.py "tu texto"
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

try:
    from num2words import num2words
except ImportError:
    print("Falta num2words. Instalalo con:  pip install num2words")
    sys.exit(1)

EJEMPLO = ("A las 7:30 publicamos el 15% de los 1250 audios en twincastia.com, "
           "escribinos a hola@twincastia.com o busca #IngenieriaDeVoz. "
           "El motor costo $0 y corre en 1 GPU.")


def numero(n):
    """El 1 se lee 'un' delante de un sustantivo, que es el caso habitual.
    La concordancia de genero (un/una) depende del sustantivo y queda para
    revision humana: es una limitacion conocida de cualquier normalizador simple."""
    n = int(n)
    return "un" if n == 1 else num2words(n, lang="es")


def normalizar(texto):
    t = texto

    # horas: 7:30 -> las siete y treinta
    def _hora(m):
        h, mi = int(m.group(1)), int(m.group(2))
        if mi == 0:
            return f"{numero(h)} en punto"
        return f"{numero(h)} y {numero(mi)}"
    t = re.sub(r"\b(\d{1,2}):(\d{2})\b", _hora, t)

    # porcentajes
    t = re.sub(r"(\d+(?:[.,]\d+)?)\s*%",
               lambda m: f"{numero(float(m.group(1).replace(',', '.')))} por ciento", t)

    # dinero
    t = re.sub(r"\$\s*(\d+)", lambda m: f"{numero(m.group(1))} dolares", t)

    # correos y dominios
    t = t.replace("@", " arroba ")
    t = re.sub(r"\b([\w\.]+)\.(com|net|org|sv|io)\b",
               lambda m: f"{m.group(1).replace('.', ' punto ')} punto {m.group(2)}", t)

    # etiquetas
    t = re.sub(r"#(\w+)", lambda m: f"almohadilla {m.group(1)}", t)

    # numeros sueltos que queden
    t = re.sub(r"\b\d+\b", lambda m: numero(m.group(0)), t)

    # espacios sobrantes
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t


def main():
    texto = sys.argv[1] if len(sys.argv) > 1 else EJEMPLO
    salida = normalizar(texto)
    print("antes:")
    print(f"  {texto}\n")
    print("despues:")
    print(f"  {salida}")

    destino = OUTPUTS / "texto_normalizado.txt"
    destino.write_text(salida, encoding="utf-8")
    print(f"\nescrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
