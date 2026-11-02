#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 85 · La huella de cada audio: registrar lo que generas para demostrar despues su origen.

`anota` calcula la huella (sha256) de un audio y la anade a outputs/registro.jsonl con el texto y la hora; nunca
borra lineas. `busca` dice si un audio esta en tu registro. En la serie: una narracion de 5,8 MB da su huella en
3 milesimas. La huella no sobrevive a un recorte o una compresion: para eso haria falta una marca de agua, que
este script no pone.

Solo biblioteca estandar.
Uso:  python cap14_registro.py anota outputs/sintesis.wav "lo que dijo la voz"
      python cap14_registro.py busca audio_sospechoso.wav
"""
import hashlib
import json
import sys
import time
from pathlib import Path

REGISTRO = Path(__file__).resolve().parent / "outputs" / "registro.jsonl"


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def anota(ruta, texto):
    t0 = time.perf_counter()
    h = huella(ruta)
    REGISTRO.parent.mkdir(exist_ok=True)
    with REGISTRO.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"sha256": h, "archivo": Path(ruta).name, "texto": texto,
                            "cuando": time.strftime("%Y-%m-%d %H:%M")}, ensure_ascii=False) + "\n")
    print(f"anotado {Path(ruta).name}: {h[:16]}... en {time.perf_counter() - t0:.4f} s")


def busca(ruta):
    h = huella(ruta)
    lineas = REGISTRO.read_text(encoding="utf-8").splitlines() if REGISTRO.exists() else []
    hallado = [json.loads(l) for l in lineas if json.loads(l)["sha256"] == h]
    if hallado:
        print(f"salio de tu sistema: {hallado[0]['cuando']}, «{hallado[0]['texto'][:60]}»")
    else:
        print("no esta en tu registro: no salio de tu sistema tal cual (o lo recortaron)")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("anota", "busca"):
        print(__doc__)
        return
    if sys.argv[1] == "anota":
        anota(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    else:
        busca(sys.argv[2])


if __name__ == "__main__":
    main()
