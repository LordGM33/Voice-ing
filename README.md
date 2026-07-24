# Voice-ing

Repositorio companion del libro **Ingenieria de Voz para Avatares Autonomos** (Libro I de la serie
*Arquitectura de un Avatar Autonomo Basado en IA*).

Siguiendo el taller del libro (Capitulo 0), el lector construye este paquete pieza a pieza: un
sistema basico de generacion y clonacion de voz con normalizacion de texto en espanol, clonacion
zero-shot desde una referencia propia, plan de prosodia y QA por medicion (WER round-trip).

Proyecto: https://twincastia.com

## Estructura

```
voiceing/        el sistema (cada archivo indica el Taller del libro que lo construye)
experimentos/    demos didacticas por capitulo
requirements.txt dependencias por bloques (base / motor / opcional)
```

## Estado

En preparacion junto con la edicion en curso del libro. Cada modulo declara en su docstring el
Taller que lo construye; el contenido se ira completando y versionando aqui.
