#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 74 · Donde se va el tiempo de tu cadena.

Le das cuando empezo y acabo cada etapa (en segundos o en hora HH:MM:SS) y te dice cuanto duro cada
una, que parte del total se lleva y cual es el cuello. Optimizar otra etapa no acorta nada. Sin
argumentos usa la noche del capitulo 11 de la serie: narrar se llevo el 97 %; montar, el 3 %.

Solo biblioteca estandar.
Uso:  python cap12_cuello.py narrar=22:10:00-01:37:00 montar=01:37:00-01:44:18
"""
import sys

SERIE = {"narrar": (0, 12420), "subtitular y montar": (12420, 12858)}


def segundos(t):
    if ":" not in t:
        return float(t)
    h, m, s = (float(p) for p in t.split(":"))
    return h * 3600 + m * 60 + s


def leer(args):
    etapas = {}
    for a in args:
        nombre, _, tramo = a.partition("=")
        ini, _, fin = tramo.partition("-")
        etapas[nombre] = (segundos(ini), segundos(fin))
    return etapas


def main():
    etapas = leer(sys.argv[1:]) if len(sys.argv) > 1 else SERIE
    # una etapa que cruza la medianoche acaba "antes" de empezar
    dura = {e: (fin - ini) % 86400 for e, (ini, fin) in etapas.items()}
    total = sum(dura.values())
    for e, d in sorted(dura.items(), key=lambda kv: -kv[1]):
        print(f"{e:>22}: {d / 60:7.1f} min  {100 * d / total:3.0f} %")
    print(f"el cuello: {max(dura, key=dura.get)}")


if __name__ == "__main__":
    main()
