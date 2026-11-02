#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serie, episodio 84 · Un permiso con alcance: no se sintetiza nada fuera de lo acordado.

El permiso para clonar una voz responde tres preguntas: para que, hasta cuando y si se puede retirar. Este
script lo guarda en permiso.json (si no existe, crea uno de ejemplo para que lo rellenes) y comprueba un uso
antes de sintetizar: si esta fuera, sale con error. Si la persona es menor de edad, firman tambien sus padres.

Solo biblioteca estandar.
Uso:  python cap14_permiso.py "videos de clase" [AAAA-MM-DD]
"""
import datetime
import json
import sys
from pathlib import Path

PERMISO = Path(__file__).resolve().parent / "samples" / "permiso.json"   # datos personales: fuera del repo
EJEMPLO = {"quien": "nombre de quien presta la voz", "para": ["videos de clase"], "hasta": "2027-12-31",
           "revocable": True, "retirado": False, "firmado": "AAAA-MM-DD"}


def leer():
    if not PERMISO.exists():
        PERMISO.write_text(json.dumps(EJEMPLO, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"creado {PERMISO.name} de ejemplo: rellenalo con el permiso real, por escrito")
    return json.loads(PERMISO.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    uso = sys.argv[1]
    fecha = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
    p = leer()
    if p.get("retirado"):
        raise PermissionError("la persona retiro el permiso: no se sintetiza nada")
    if uso not in p["para"] or fecha > p["hasta"]:
        raise PermissionError(f"fuera del permiso: {uso!r} el {fecha} (vale para {p['para']} hasta {p['hasta']})")
    print(f"dentro del permiso: {uso!r} el {fecha}")


if __name__ == "__main__":
    main()
