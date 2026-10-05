#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 26 a 31 · Una cadena de voz con contratos, y un motor de mentira para probarla.

Lo que viaja (SegmentoHabla), lo que sale (TrozoAudio), el puerto (Sintetizador) y un
adaptador que no carga ningun modelo: un pitido por palabra. Corre en cualquier portatil.
Cambiar al motor de verdad es cambiar una linea; el resto de la cadena no se entera.

Uso:  python cap06_cadena.py "tu texto aqui"
      python cap06_cadena.py            usa un texto de ejemplo
"""
import re
import sys
import time
import wave
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError, dataclass, field
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)

SR_CONTRATO = 24_000       # dentro de la cadena, siempre esta
EJEMPLO = "Hola a todos. ¿Qué tal? Vamos allá."


@dataclass(frozen=True)
class IndicacionProsodia:
    pausa_antes_ms: int = 0
    enfasis: float = 0.0
    velocidad: float = 1.0
    tono_st: float = 0.0           # lo aplica el motor
    respirar_despues: bool = False


@dataclass(frozen=True)
class SegmentoHabla:
    texto: str
    emocion: str = "neutral"
    intensidad: float = 0.5
    prosodia: IndicacionProsodia = field(default_factory=IndicacionProsodia)


@dataclass(frozen=True)
class TrozoAudio:
    muestras: np.ndarray           # entre -1 y 1, un solo canal
    sr: int
    orden: int = 0
    es_final: bool = False


class Sintetizador(ABC):           # el puerto
    @abstractmethod
    def sintetizar(self, segmentos, perfil): ...


class MotorDePitidos(Sintetizador):    # adaptador de mentira
    def sintetizar(self, segmentos, perfil):
        n = len(" ".join(s.texto for s in segmentos).split())
        pitido = np.sin(np.arange(2400) * 0.3).astype(np.float32)
        hueco = np.zeros(1200, np.float32)
        return TrozoAudio(np.concatenate([pitido, hueco] * n), SR_CONTRATO)


def planificar(texto):
    """El como: una frase por segmento, cortando detras de cada punto, pregunta o exclamacion."""
    frases = re.split(r"(?<=[.?!])\s+", texto.strip())
    return [SegmentoHabla(f) for f in frases if f]


def postproceso(trozo):
    """Recorta el silencio del final e iguala el volumen a un pico de 0.9."""
    x = np.trim_zeros(trozo.muestras, "b")
    pico = float(np.max(np.abs(x))) if len(x) else 0.0
    if pico > 0:
        x = x * (0.9 / pico)
    return TrozoAudio(x.astype(np.float32), trozo.sr, trozo.orden, es_final=True)


def guardar_wav(trozo, ruta):
    datos = (np.clip(trozo.muestras, -1, 1) * 32767).astype("<i2")
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(trozo.sr)
        w.writeframes(datos.tobytes())


def main():
    texto = sys.argv[1] if len(sys.argv) > 1 else EJEMPLO
    perfil = None                  # el motor de pitidos no necesita voz de referencia

    segmentos = planificar(texto)
    motor = MotorDePitidos()       # para probar, sin tarjeta grafica
    # motor = MotorQwen()          # el de verdad: un adaptador mas del mismo puerto
    t0 = time.perf_counter()
    audio = postproceso(motor.sintetizar(segmentos, perfil))
    # episodio 33: segundos de computo por segundo de audio; por debajo de 1, mas rapido que tiempo real
    rtf = (time.perf_counter() - t0) / (len(audio.muestras) / audio.sr)

    palabras = len(texto.split())
    print(f"{len(segmentos)} segmento(s), {palabras} palabra(s) -> "
          f"{len(audio.muestras) / audio.sr:.2f} s de pitidos a {audio.sr} Hz")
    print(f"factor de tiempo real {rtf:.5f}: diminuto, porque no hace casi nada. "
          "Mide el de tu motor de verdad.")
    try:
        segmentos[0].texto = "otra cosa"
    except FrozenInstanceError:
        print("frozen=True: el segmento no se deja cambiar por el camino")

    destino = OUTPUTS / "cadena_pitidos.wav"
    guardar_wav(audio, destino)
    print(f"escrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
