#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 34 y 35 · El error de ida y vuelta, y de quien es cada error.

Transcribe un audio, lo compara con el texto que se pidio y separa los errores en montones:
tildes y guiones (son del normalizador), numeros en cifras (son del reconocedor) y el resto,
que es lo unico que hay que ir a escuchar. En la serie, 38 de 99 errores no eran de la voz.

Uso:  python cap07_de_quien_es.py audio.wav "el texto que se pidio"
      python cap07_de_quien_es.py audio.wav          usa el .txt del mismo nombre
"""
import re
import sys
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)

NUMEROS = {"cero", "uno", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
           "nueve", "diez", "veinte", "treinta", "cien", "mil", "millon", "millones"}


def palabras(s):
    """Minusculas y sin signos, pero CON tildes: asi se ve cuanto error es solo de ortografia."""
    return re.sub(r"[¿?¡!.,;:…\"'()«»]", " ", s.lower()).split()


def sin_tildes(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def alinear(r, h):
    """Pares (esperado, oido) que no cuadran, por distancia de edicion entre palabras."""
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (r[i - 1] != h[j - 1]))
    pares, i, j = [], len(r), len(h)
    while i or j:
        if i and j and d[i][j] == d[i - 1][j - 1] + (r[i - 1] != h[j - 1]):
            if r[i - 1] != h[j - 1]:
                pares.append((r[i - 1], h[j - 1]))
            i, j = i - 1, j - 1
        elif i and d[i][j] == d[i - 1][j] + 1:
            pares.append((r[i - 1], ""))
            i -= 1
        else:
            pares.append(("", h[j - 1]))
            j -= 1
    return pares[::-1]


def monton(esperado, oido):
    if esperado and oido and sin_tildes(esperado) == sin_tildes(oido):
        return "tilde"
    if oido.isdigit() or (not oido and sin_tildes(esperado) in NUMEROS):
        return "cifra"
    if "-" in esperado or "-" in oido:
        return "guion"
    return "escuchar"


def transcribir(audio):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    tramos, _ = m.transcribe(str(audio), language="es")
    return " ".join(t.text.strip() for t in tramos)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    audio = Path(sys.argv[1])
    if len(sys.argv) > 2:
        esperado = sys.argv[2]
    elif audio.with_suffix(".txt").exists():
        esperado = audio.with_suffix(".txt").read_text(encoding="utf-8")
    else:
        print(f"Falta el texto: pasalo como segundo argumento o crea {audio.with_suffix('.txt').name}")
        return

    print(f"transcribiendo {audio.name} (la primera vez descarga el modelo)...")
    r = palabras(esperado)
    pares = alinear(r, palabras(transcribir(audio)))
    montones = {"tilde": [], "cifra": [], "guion": [], "escuchar": []}
    for a, b in pares:
        montones[monton(a, b)].append(f"{a or '-'} -> {b or '-'}")

    print(f"\n{len(r)} palabras, {len(pares)} errores: WER {len(pares) / max(1, len(r)) * 100:.1f} %")
    for nombre, lista in montones.items():
        print(f"\n{nombre:9s} {len(lista):3d}   {', '.join(lista[:12])}")
    reales = len(montones["escuchar"])
    print(f"\nsin tildes, cifras ni guiones: WER {reales / max(1, len(r)) * 100:.1f} %")
    print("Los del monton 'escuchar' pueden ser de la voz O del reconocedor (no conoce el voseo,")
    print("completa palabras que no oyo enteras). Para saber de quien es, escucha ese trozo.")

    destino = OUTPUTS / f"de_quien_es_{audio.stem}.txt"
    destino.write_text("\n".join(f"{k}\t{v}" for k, l in montones.items() for v in l), encoding="utf-8")
    print(f"\nescrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
