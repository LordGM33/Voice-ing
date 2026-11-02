#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 83 · Tu voz es una llave: que no llegue nunca a un repositorio publico.

Busca archivos de audio en lo que vas a publicar (los archivos del repositorio) y tambien en toda su historia:
lo que borras en una version sigue en la anterior. Si encuentra alguno, sale con error para que no publiques.
En la serie: 12 versiones del repositorio de ejercicios y ningun audio en su historia.

Solo biblioteca estandar y git.
Uso:  python cap14_tu_voz_no_se_publica.py [carpeta del repositorio]
"""
import re
import subprocess
import sys

AUDIO = re.compile(r"\.(wav|mp3|flac|ogg|m4a|opus)$", re.I)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    ahora = [f for f in git(repo, "ls-files").splitlines() if AUDIO.search(f)]
    historia = sorted({f for f in git(repo, "log", "--all", "--name-only", "--pretty=format:").splitlines()
                       if AUDIO.search(f)})
    versiones = git(repo, "rev-list", "--all", "--count").strip()
    print(f"{versiones} versiones revisadas")
    if ahora or historia:
        raise SystemExit(f"no publiques tu voz: ahora {ahora}, en la historia {historia}")
    print("ningun audio, ni ahora ni en la historia")


if __name__ == "__main__":
    main()
