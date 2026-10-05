#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodios 36 y 37 · Tus frases de prueba, fijas y con version, y dos motores comparados.

Sin argumentos crea outputs/frases_v1.json con ocho frases de ejemplo para que pongas las tuyas.
Una version guardada NO se sobrescribe nunca: si cambias una frase, es la v2.

Para comparar motores, pon en samples/<motor>/ un wav por frase (1.wav, 2.wav...) y:
      python cap07_frases_de_prueba.py comparar v1 motorA motorB
Mismas frases, mismo reconocedor; lo unico que cambia es el motor. Se juzga por la media.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
OUTPUTS = BASE / "outputs"
SAMPLES.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

# cada una esta por algo que puede fallar; cambialas por las tuyas antes de la primera medida
EJEMPLO = [
    "¿Vos qué opinás? ¿Nos vemos el viernes a las siete?",   # voseo y una pregunta
    "¡Qué chivo verte por aquí!",                            # modismo y exclamacion
    "Son las siete y media del doce de octubre.",            # hora y fecha
    "Cuesta veinticinco dólares con cincuenta.",              # numeros
    "Puchica, se me olvidó otra vez.",                        # modismo
    "La reunión fue larga, pero salió bien.",                 # pausa de coma
    "¿De verdad lo hiciste tú solo?",                         # pregunta con enfasis
    "Esto es Voice-ing, el taller de la serie.",              # el nombre del proyecto
]


def ruta(version):
    return OUTPUTS / f"frases_{version}.json"


def crear(version="v1"):
    if ruta(version).exists():
        print(f"{ruta(version).name} ya existe y NO se toca: lo medido con ella dejaria de ser comparable.")
        print("Si quieres cambiar una frase, crea la siguiente version.")
        return
    ruta(version).write_text(json.dumps(EJEMPLO, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"escrito: {ruta(version).relative_to(BASE)}  (8 frases de ejemplo: cambialas por las tuyas)")


def palabras(s):
    return re.sub(r"[¿?¡!.,;:…\"'()«»]", " ", s.lower()).split()


def wer(esperado, oido):
    r, h = palabras(esperado), palabras(oido)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        previo, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            previo, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, previo + (r[i - 1] != h[j - 1]))
    return d[len(h)] / max(1, len(r))


def comparar(version, motores):
    from faster_whisper import WhisperModel
    frases = json.loads(ruta(version).read_text(encoding="utf-8"))
    m = WhisperModel("small", device="cpu", compute_type="int8")
    for motor in motores:
        errores = []
        for n, frase in enumerate(frases, 1):
            wav = SAMPLES / motor / f"{n}.wav"
            if not wav.exists():
                print(f"  falta {wav.relative_to(BASE)}")
                continue
            tramos, _ = m.transcribe(str(wav), language="es")
            errores.append(wer(frase, " ".join(t.text for t in tramos)))
        if errores:
            print(f"{motor:16s} {len(errores)} frases   WER medio {sum(errores) / len(errores) * 100:5.1f} %"
                  f"   (de {min(errores) * 100:.0f} a {max(errores) * 100:.0f} %)")


def main():
    if len(sys.argv) > 3 and sys.argv[1] == "comparar":
        comparar(sys.argv[2], sys.argv[3:])
    else:
        crear(sys.argv[1] if len(sys.argv) > 1 else "v1")


if __name__ == "__main__":
    main()
