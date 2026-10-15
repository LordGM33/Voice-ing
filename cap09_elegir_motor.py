#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 47 a 49 · Elegir un motor de voz por dentro, no por su demo.

rubrica   las seis preguntas del libro en outputs/rubrica.json; las rellenas con TUS medidas y el
          script te dice cuales siguen sin contestar (una pregunta vacia no es un si).
licencias la licencia que declara cada libreria de este Python, y las que no son permisivas.
variante  que version del modelo descargaste (config.json) y la licencia de sus pesos (README).

Uso:  python cap09_elegir_motor.py rubrica
      python cap09_elegir_motor.py licencias
      python cap09_elegir_motor.py variante ruta/a/la/carpeta/del/modelo
"""
import importlib.metadata as md
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)

PREGUNTAS = {
    "identidad": "¿copia tu voz? (verificador de hablante y tu oido; la ficha casera del cap. 4 no sirve)",
    "idioma": "¿entiende tu idioma? (WER round-trip, cap07_wer.py)",
    "entonacion": "¿tiene entonacion? (varST, cap05_entonacion.py)",
    "coste": "¿cuanto cuesta? (segundos de calculo por segundo de audio, cap08_telemetria.py)",
    "streaming": "¿habla mientras genera? (probado, no leido en la ficha)",
    "licencia": "¿te deja usarlo? (codigo Y pesos, por separado)",
}
# Prefijos de licencias que no piden nada si repartes la libreria dentro de tu programa.
PERMISIVAS = ("MIT", "BSD", "Apache", "ISC", "PSF", "Zlib", "0BSD", "CC0", "Unlicense")


def rubrica():
    ruta = OUTPUTS / "rubrica.json"
    if not ruta.exists():
        ruta.write_text(json.dumps({p: None for p in PREGUNTAS}, indent=2), encoding="utf-8")
        print(f"creado {ruta.relative_to(BASE)}: rellenalo con tus medidas y vuelve a ejecutar.\n")
    respuestas = json.loads(ruta.read_text(encoding="utf-8"))
    vacias = [p for p in PREGUNTAS if respuestas.get(p) in (None, "")]
    for p, como in PREGUNTAS.items():
        print(f"  {p:11s} {respuestas.get(p)!s:>12}   {como}")
    print(f"\nsin contestar: {', '.join(vacias) or 'ninguna'}")
    if vacias:
        print("No elijas el motor todavia: lo que no has medido es trabajo pendiente.")


def licencia_de(dist):
    m = dist.metadata
    return m.get("License-Expression") or m.get("License") or "?"


def licencias():
    revisar = []
    for dist in sorted(md.distributions(), key=lambda d: d.metadata["Name"].lower()):
        lic = " ".join(licencia_de(dist).split())[:40]
        if not lic.startswith(PERMISIVAS):
            revisar.append((dist.metadata["Name"], lic))
    print(f"Python: {sys.executable}\n")
    for nombre, lic in revisar:
        nota = "no la declara: leela en su repositorio" if lic == "?" else "leer antes de distribuir"
        print(f"  {nombre:28s} {lic:40s} {nota}")
    print(f"\n{len(revisar)} librerias que revisar a mano. Para probar en tu equipo da igual;"
          " para repartirlas dentro de tu programa, no.")


def variante(carpeta):
    carpeta = Path(carpeta)
    config = json.loads((carpeta / "config.json").read_text(encoding="utf-8"))
    tipo = config.get("tts_model_type") or config.get("model_type")
    print(f"tipo de modelo: {tipo}")
    readme = carpeta / "README.md"
    if readme.exists():
        lic = re.search(r"^license:\s*(\S+)", readme.read_text(encoding="utf-8"), re.M)
        print(f"licencia de los pesos (ficha): {lic.group(1) if lic else 'no la dice: buscala'}")
    if tipo != "base":
        print("Esta version no clona una voz desde tu grabacion: la que clona es la «base».")


def main():
    orden = sys.argv[1] if len(sys.argv) > 1 else ""
    if orden == "rubrica":
        rubrica()
    elif orden == "licencias":
        licencias()
    elif orden == "variante" and len(sys.argv) > 2:
        variante(sys.argv[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
