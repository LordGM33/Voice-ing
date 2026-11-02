#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 77 · Detectar y rechazar, no corregir: el texto sin tildes vuelve a quien lo escribio.

Un motor de voz lee «como» y «cómo» distinto: sin la tilde, la pregunta suena a afirmacion. Este
guardarrail no adivina tildes; solo avisa de lo que seguro esta mal: palabras que sin tilde no
existen y el interrogativo que abre una pregunta. En la serie: 104 guiones, 0 falsos avisos; sobre
los mismos textos sin tildes, caza 4 de cada 10 frases. Las demas (el/él, mas/más) no las ve.

Solo biblioteca estandar.
Uso:  python cap13_tildes.py "¿Como lo hiciste? Despues lo pruebo."      o      python cap13_tildes.py guion.txt
"""
import re
import sys
from pathlib import Path

# "video" falta a proposito: sin tilde es lo correcto en America
SOLO_CON_TILDE = {"tambien", "despues", "ademas", "aqui", "alli", "asi", "facil", "dificil", "rapido", "numero",
                  "musica", "ultimo", "ultima", "telefono", "pagina", "metodo", "codigo", "tecnica", "practica",
                  "capitulo", "queres", "tenes", "podes", "decis", "venis", "pensas", "aca", "segun", "jamas",
                  "quizas", "detras", "algun", "ningun"}
INTERROGATIVOS = {"que", "como", "cuando", "donde", "cuanto", "cuanta", "cuantos", "quien", "cual", "por que"}


def detectar(texto):
    malas = [p for p in re.findall(r"\b\w+\b", texto.lower()) if p in SOLO_CON_TILDE or re.fullmatch(r"\w+cion", p)]
    # solo el que abre la pregunta: en «¿Tenés una serie que no puedas dejar?» el «que» es relativo
    malas += [m.group(1) for m in re.finditer(r"¿\s*(por que|\w+)", texto.lower()) if m.group(1) in INTERROGATIVOS]
    return malas


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    arg = sys.argv[1]
    texto = Path(arg).read_text(encoding="utf-8") if Path(arg).is_file() else " ".join(sys.argv[1:])
    malas = detectar(texto)
    if malas:
        raise SystemExit(f"escribelo otra vez, con tildes: {malas}")
    print("pasa: no hay ninguna de las que este guardarrail sabe ver")


if __name__ == "__main__":
    main()
