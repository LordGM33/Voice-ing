#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 5.2 · Planificador de prosodia.

Prepara el texto antes de que lo vea el motor. Hace dos cosas y evita una tercera:
  repara la puntuacion, porque el motor entona a partir de los signos
  segmenta solo si el texto es muy largo, en bloques grandes
  NO trocea en grupos cortos: eso aplana la entonacion (hallazgo medido del libro)

Uso:  python cap05_prosodia.py "tu texto aqui"
      python cap05_prosodia.py            usa un texto de ejemplo
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

UMBRAL_SEGMENTO = 320     # por debajo de esto, una sola pasada del motor
BLOQUE = 340

EJEMPLO = ("Que hace que una voz suene viva? Es el timbre, o la forma de hablar? "
           "La diferencia es enorme cuando la escuchas de cerca! El ritmo, las pausas "
           "y la entonacion cuentan una historia que las palabras, por si solas, no "
           "pueden contar.")


def reparar_puntuacion(texto):
    """Anade los signos de apertura del espanol si faltan. El motor los necesita."""
    partes = re.split(r"(?<=[\.\?\!…])\s+", texto.strip())
    salida = []
    for p in partes:
        if p.endswith("?") and not p.lstrip().startswith("¿"):
            p = "¿" + p
        if p.endswith("!") and not p.lstrip().startswith("¡"):
            p = "¡" + p
        salida.append(p)
    return " ".join(salida)


def segmentar(texto):
    """Divide solo si hace falta, y en bloques grandes que respeten la frase."""
    if len(texto) <= UMBRAL_SEGMENTO:
        return [texto]
    frases = re.split(r"(?<=[\.\?\!…])\s+", texto.strip())
    bloques, actual = [], ""
    for f in frases:
        if actual and len(actual) + len(f) + 1 > BLOQUE:
            bloques.append(actual.strip())
            actual = f
        else:
            actual = (actual + " " + f).strip()
    if actual:
        bloques.append(actual)
    return bloques


def revisar_tildes(texto):
    """Marca palabras cuya forma sin tilde no existe en espanol. Detecta, no corrige."""
    sospechosas = {"aqui": "aquí", "estan": "están", "dia": "día", "musica": "música",
                   "cafe": "café", "tambien": "también", "asi": "así", "facil": "fácil",
                   "dificil": "difícil", "rapido": "rápido", "numero": "número",
                   "practica": "práctica", "metrica": "métrica", "tecnica": "técnica",
                   "fisica": "física", "energia": "energía", "clonacion": "clonación",
                   "entonacion": "entonación", "sintesis": "síntesis", "que": None}
    fallos = []
    for palabra in re.findall(r"\b[a-záéíóúüñ]+\b", texto.lower()):
        correcta = sospechosas.get(palabra)
        if correcta:
            fallos.append((palabra, correcta))
    return sorted(set(fallos))


def main():
    texto = sys.argv[1] if len(sys.argv) > 1 else EJEMPLO
    print(f"entrada: {len(texto)} caracteres\n")

    fallos = revisar_tildes(texto)
    if fallos:
        print("posibles tildes faltantes (se rechaza, no se corrige solo:")
        print("restituir tildes es ambiguo y un acento mal puesto cambia el significado):")
        for mal, bien in fallos:
            print(f"  {mal} -> {bien}")
        print()

    reparado = reparar_puntuacion(texto)
    if reparado != texto:
        print("puntuacion reparada (se anadieron signos de apertura)")

    bloques = segmentar(reparado)
    if len(bloques) == 1:
        print(f"una sola pasada del motor: {len(reparado)} caracteres, por debajo de {UMBRAL_SEGMENTO}")
    else:
        print(f"se segmenta en {len(bloques)} bloques grandes (el texto supera {UMBRAL_SEGMENTO}):")
        for i, b in enumerate(bloques, 1):
            print(f"  bloque {i}: {len(b)} caracteres")

    destino = OUTPUTS / "texto_preparado.txt"
    destino.write_text("\n\n".join(bloques), encoding="utf-8")
    print(f"\nescrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
