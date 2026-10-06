#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 46 · Mide cada etapa, con percentiles y no con medias (taller 8.2 del libro).

Copia la clase Telemetria en tu programa, o importala si este archivo esta en la misma carpeta.
Sin argumentos hace una demostracion con etapas de mentira para que veas el informe.

Uso:  python cap08_telemetria.py
"""
import time
from contextlib import contextmanager

import numpy as np


class Telemetria:
    """Apunta cuanto tarda cada etapa, cada vez, y lo resume con percentiles."""

    def __init__(self):
        self.muestras = {}

    @contextmanager
    def etapa(self, nombre):
        t0 = time.perf_counter()
        try:
            yield
        finally:
            self.muestras.setdefault(nombre, []).append((time.perf_counter() - t0) * 1000)

    def informe(self, nombre):
        s = np.array(self.muestras.get(nombre, [0.0]))
        return {"p50_ms": round(float(np.percentile(s, 50)), 1),
                "p95_ms": round(float(np.percentile(s, 95)), 1), "n": len(s)}


def main():
    tele = Telemetria()
    with tele.etapa("arranque"):
        time.sleep(0.3)                       # aqui iria cargar el modelo, una vez
    for i in range(40):
        with tele.etapa("sintesis"):
            # una de cada diez, lenta: lo que una media esconde y el p95 enseña
            time.sleep(0.25 if i % 10 == 9 else 0.05)
    for nombre in tele.muestras:
        print(f"{nombre:10s} {tele.informe(nombre)}")
    media = np.mean(tele.muestras["sintesis"])
    print(f"\nmedia de la sintesis: {media:.0f} ms. Mira el p95: esas son las veces que alguien espera.")


if __name__ == "__main__":
    main()
