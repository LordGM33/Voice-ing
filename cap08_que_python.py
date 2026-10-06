#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 43 y 44 · ¿Que Python estas usando de verdad, y que le falta? Y pedirle trabajo a otro.

Sin argumentos: dice que Python ejecuta esto, que paquetes de la serie tiene y cuales faltan, y
apunta las versiones en outputs/entorno.txt para poder rehacer el entorno igual dentro de meses.
Con la ruta de OTRO Python: le pide que ejecute un script y te trae el final del error si falla.

Uso:  python cap08_que_python.py
      python cap08_que_python.py ruta/al/otro/python script.py [argumentos...]
"""
import importlib.metadata as md
import importlib.util
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)

PAQUETES = {"numpy": "numpy", "scipy": "scipy", "librosa": "librosa", "soundfile": "soundfile",
            "matplotlib": "matplotlib", "faster_whisper": "faster-whisper", "torch": "torch"}


def este_entorno():
    print(f"Python: {sys.executable}  ({sys.version.split()[0]})\n")
    lineas, faltan = [f"python=={sys.version.split()[0]}"], []
    for modulo, distribucion in PAQUETES.items():
        if importlib.util.find_spec(modulo) is None:
            faltan.append(modulo)
            print(f"  {modulo:16s} falta")
            continue
        version = md.version(distribucion)
        lineas.append(f"{distribucion}=={version}")
        print(f"  {modulo:16s} {version}")
    destino = OUTPUTS / "entorno.txt"
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\nfaltan: {faltan or 'nada'}")
    print(f"escrito: {destino.relative_to(BASE)}  (con esto rehaces el entorno igual)")


def pedir_a_otro(python, argumentos):
    r = subprocess.run([python, *argumentos], capture_output=True, text=True)
    print(r.stdout[-1500:])
    if r.returncode != 0:
        print(f"el otro Python termino con error ({r.returncode}). El final:\n{r.stderr[-600:]}")


def main():
    if len(sys.argv) > 2:
        pedir_a_otro(sys.argv[1], sys.argv[2:])
    else:
        este_entorno()


if __name__ == "__main__":
    main()
