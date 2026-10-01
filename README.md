# Voice-ing

Scripts del taller del libro **Diseño y construcción de sistemas de audio para IA**
(serie *Desarrollo de Avatares IA Autónomos*, libro 1).

Cada script es **independiente**: podés descargar uno solo y funciona. También
podés clonar el repositorio completo y usarlos en orden, capítulo a capítulo.

## Cómo se usa

Descargá los scripts (uno o todos) en una carpeta cualquiera. Esa carpeta es la
raíz. Al ejecutar cualquier script por primera vez se crean solas dos carpetas:

```
la-carpeta-donde-los-pusiste/
├── cap02_onda.py ...        los scripts
├── samples/                 tus grabaciones (se crea sola)
└── outputs/                 todo lo que generan (se crea sola)
```

No hay rutas que configurar. Los scripts buscan en `samples/` y escriben en
`outputs/`, siempre relativo a donde está el propio script.

## Tus grabaciones

Poné en `samples/` tus audios en WAV. Por cada `grabacion.wav` conviene tener un
`grabacion.txt` con **lo que realmente se dijo**, palabra por palabra. Esa
transcripción exacta es la lección central del Capítulo 4 y sin ella la
clonación se degrada mucho.

Si `samples/` está vacía, los scripts de demostración generan un audio sintético
para que puedas probarlos igual.

## Los scripts, en orden

| Script | Capítulo | Qué hace | Necesita |
|---|---|---|---|
| `cap02_onda.py` | 2 | Construye un tono desde cero: el sonido como array | base |
| `cap02_espectro.py` | 2 | Qué frecuencias componen un audio | base |
| `cap02_mel.py` | 2 | Espectrograma mel, la vista que usan los modelos | base |
| `cap02_reporte_audio.py` | 2 y 8 | Reporte completo de un audio y sus problemas | base |
| `cap03_fuente_filtro.py` | 3 | Sintetiza una vocal: fuente glótica más formantes | base |
| `cap04_calidad_fuente.py` | 4 | Jitter, shimmer y HNR: la micro-imperfección | base |
| `cap04_qa_grabacion.py` | 4 | Revisa todas tus grabaciones y elige candidata | base |
| `cap04_perfil_vocal.py` | 4 | Registra tus referencias en `perfiles.json` | base |
| `cap05_prosodia.py` | 5 | Repara puntuación, revisa tildes y decide segmentación | solo stdlib |
| `cap07_wer.py` | 7 | WER round-trip: la métrica que decide | ASR |
| `cap09_normalizacion.py` | 9 | Normaliza números, horas, dominios y etiquetas | num2words |
| `cap09_sintetizar.py` | 9 | Sintetiza con tu voz clonada | GPU y motor |

## Instalación

Base (todo menos los dos últimos), corre en cualquier equipo sin GPU:

```
pip install numpy scipy librosa soundfile matplotlib
```

Para el WER: `pip install faster-whisper`
Para la normalización: `pip install num2words`
Para sintetizar: ver el Capítulo 8 del libro, que explica por qué el motor va en
su propio entorno virtual.

O de una vez: `pip install -r requirements.txt`

## Nota sobre las mediciones

Las métricas acústicas de estos scripts son aproximaciones suficientes para
comparar grabaciones entre sí y tomar decisiones. Para precisión clínica se usan
herramientas de fonética especializadas, que el libro menciona en el Capítulo 7.

## Proyecto

Estos scripts salen de un proyecto real de avatar autónomo: twincastia.com
