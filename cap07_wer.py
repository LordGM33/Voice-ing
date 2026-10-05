#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taller 7.1 · WER round-trip: la metrica que decide.

Transcribe un audio y lo compara con el texto que se pidio. Es la puerta de
calidad mas barata que existe: si la voz no se entiende, no sirve por bonita
que suene. La primera ejecucion descarga el modelo de reconocimiento.

Uso:  python cap07_wer.py ruta_audio.wav "el texto que se pidio"
      python cap07_wer.py ruta_audio.wav          usa el .txt del mismo nombre
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

TAMANO_MODELO = "small"      # 'base' es mas rapido, 'medium' mas preciso


def normalizar(s):
    """Para comparar solo lo que importa: sin signos, sin mayusculas, sin dobles espacios."""
    s = re.sub(r"[¿?¡!.,;:…\"'()]", " ", s.lower())
    return " ".join(s.split())


def wer(referencia, hipotesis):
    """Errores por palabra: distancia de edicion entre las palabras esperadas."""
    r, h = normalizar(referencia).split(), normalizar(hipotesis).split()
    return distancia(r, h) / max(1, len(r))


def distancia(r, h):
    """Palabras cambiadas, que faltan y que sobran: el minimo de las tres que convierte r en h."""
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            coste = 0 if r[i - 1] == h[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + coste)
    return d[len(r)][len(h)]


def main():
    if len(sys.argv) > 1:
        audio = Path(sys.argv[1])
    else:
        audios = sorted(SAMPLES.glob("*.wav"))
        if not audios:
            print("Uso: python cap07_wer.py ruta_audio.wav \"texto esperado\"")
            return
        audio = audios[0]
        print(f"sin argumentos: uso {audio.name}")

    if len(sys.argv) > 2:
        esperado = sys.argv[2]
    else:
        txt = audio.with_suffix(".txt")
        if not txt.exists():
            print(f"Falta el texto esperado. Pasalo como segundo argumento o crea {txt.name}")
            return
        esperado = txt.read_text(encoding="utf-8").strip()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Falta faster-whisper. Instalalo con:  pip install faster-whisper")
        return

    print(f"transcribiendo {audio.name} (la primera vez descarga el modelo)...")
    modelo = WhisperModel(TAMANO_MODELO, device="cpu", compute_type="int8")
    segmentos, _ = modelo.transcribe(str(audio), language="es")
    oido = " ".join(s.text.strip() for s in segmentos)

    e = wer(esperado, oido)
    print(f"\nse pidio:    {esperado[:100]}")
    print(f"se entendio: {oido.strip()[:100]}")
    print(f"\nWER: {e * 100:.1f} %")
    if e < 0.05:
        print("excelente: practicamente todo se entiende")
    elif e < 0.15:
        print("aceptable para produccion")
    else:
        print("alto: revisa la pronunciacion antes que cualquier otra cosa")
    print("\nRecuerda que el WER depende tambien del reconocedor: sirve para comparar")
    print("motores entre si con el mismo ASR, no como verdad absoluta.")

    destino = OUTPUTS / f"wer_{audio.stem}.txt"
    destino.write_text(f"esperado\t{esperado}\noido\t{oido.strip()}\nwer_pct\t{e*100:.1f}",
                       encoding="utf-8")
    print(f"escrito: {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
