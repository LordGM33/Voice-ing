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
| `cap04_misma_voz.py` | 4 | ¿Son la misma voz? MFCC y coseno, bien y mal hecho (serie, ep. 16 y 17) | base |
| `cap05_prosodia.py` | 5 | Repara puntuación, revisa tildes y decide segmentación | solo stdlib |
| `cap05_entonacion.py` | 5 | Cuánto se mueve tu voz, en semitonos, y la alarma de voz plana con tu umbral (serie, ep. 19 y 24) | base |
| `cap06_cadena.py` | 6 | Una cadena de voz con contratos y un motor de mentira que corre en cualquier portátil; mide su factor de tiempo real (serie, ep. 26 a 31 y 33) | solo numpy |
| `cap07_wer.py` | 7 | WER round-trip: la métrica que decide | ASR |
| `cap07_de_quien_es.py` | 7 | Separa los errores del WER: tildes, cifras y guiones (del instrumento) y lo que hay que escuchar (serie, ep. 34 y 35) | ASR |
| `cap07_frases_de_prueba.py` | 7 | Tus ocho frases fijas con versión, y dos motores comparados por la media (serie, ep. 36 y 37) | ASR para comparar |
| `cap07_contra_la_persona.py` | 7 | Tu voz clonada contra tu grabación: qué se aleja más de un 20 % (serie, ep. 38) | base |
| `cap07_una_muestra.py` | 7 | Varias muestras por configuración: ¿la diferencia es mayor que el azar? (serie, ep. 39) | base |
| `cap08_contrato_audio.py` | 8 | El contrato de audio: tus audios a 24 000 Hz, un canal y pico a -1 dB; y oír el error de leer a otra frecuencia (serie, ep. 41 y 42) | base |
| `cap08_que_python.py` | 8 | Qué Python usas, qué le falta y sus versiones apuntadas; y pedirle trabajo a otro Python (serie, ep. 43 y 44) | solo stdlib |
| `cap08_telemetria.py` | 8 | Mide cada etapa con percentiles, no con medias (serie, ep. 46) | numpy |
| `cap09_elegir_motor.py` | 9 | Las seis preguntas para elegir motor (y cuáles no has contestado), la licencia de cada librería de tu entorno y qué versión del modelo descargaste (serie, ep. 47 a 49) | solo stdlib |
| `cap09_texto_limpio.py` | 9 | Antes de sintetizar: acotaciones que el motor leería, tildes perdidas, voseo sin tilde y signos de apertura (serie, ep. 50) | solo stdlib |
| `cap09_normalizacion.py` | 9 | Normaliza números, decimales, horas, dominios y etiquetas, y avisa de lo que no sabe decir (serie, ep. 51) | num2words |
| `cap09_sintetizar.py` | 9 | Sintetiza con tu voz clonada: el adaptador (serie, ep. 52) | GPU y motor |
| `cap09_perillas.py` | 9 | Una perilla del motor contra los valores de fábrica, por el reparto de varias tomas (serie, ep. 53) | GPU y motor |

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

## La serie «Construye tu voz de IA»

Los scripts marcados «serie» son el código que se enseña en pantalla en la serie diaria
de vídeos que sigue el libro capítulo a capítulo (Instagram, Facebook y TikTok). Cada
línea que sale en un vídeo se ejecutó tal cual antes de publicarse.

## Correcciones

Cuando una medición nueva contradice algo, se corrige aquí y se dice:

- **5-oct-2026 · `cap04_qa_grabacion.py`**: pedía 25 dB de relación señal-ruido y tramos
  de 6 a 30 s; ahora pide lo que dice el libro, más de 30 dB y de 8 a 25 s. Y avisa
  cuando el audio tiene silencio digital (ceros exactos, típico del audio sintetizado):
  ahí el SNR sale altísimo y no significa nada. Recorte y ruido se miran por separado.
- **5-oct-2026 · `cap04_calidad_fuente.py`**: los rangos clínicos del jitter son para
  una vocal sostenida, no para una lectura; el script ya no los presenta como referencia
  para cualquier grabación.
- **5-oct-2026 · coseno sobre MFCC**: la media de los 20 coeficientes no mide identidad,
  mide volumen (el coeficiente 0). `cap04_misma_voz.py` enseña las dos formas.

- **15-oct-2026 · `cap09_normalizacion.py`**: no trataba los decimales. «2.4» salía «dos.cuatro»
  y «2.5 %», «dos por ciento». Ahora dice «dos punto cuatro» y «dos punto cinco por ciento», y al
  final lista lo que no sabe decir (un usuario con guion bajo, por ejemplo) para que lo escribas a
  mano. Y `num2words`, que usa este script, tiene licencia LGPL: sin problema para practicar; si
  lo metes en algo que vas a distribuir, lee lo que pide (serie, ep. 48).

## Nota sobre las mediciones

Las métricas acústicas de estos scripts son aproximaciones suficientes para
comparar grabaciones entre sí y tomar decisiones. Para precisión clínica se usan
herramientas de fonética especializadas, que el libro menciona en el Capítulo 7.

## Proyecto

Estos scripts salen de un proyecto real de avatar autónomo: twincastia.com
