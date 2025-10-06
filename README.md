# 🧠 Proyecto: Scraper y Transcriptor de Clases VIU

## 📋 Descripción general
Este proyecto automatiza el proceso de **descarga y transcripción de videos de clases** desde la plataforma **Blackboard** de la **Universidad Internacional de Valencia (VIU)**.  
Integra un **módulo de web scraping** basado en `Selenium` para obtener los videos de las asignaturas y un **módulo de transcripción** con `OpenAI Whisper`, que convierte las clases en texto con marcas temporales.

---

## 🧩 Estructura del proyecto

```
Scrapping_videos/
│
├── main_improved_v3.py           # Script principal para el scraping de videos desde Blackboard
├── transcriptor_videos.py        # Transcripción por lotes con Whisper (procesa audios de 5 min)
├── whisper_benchmark.py          # Benchmark para evaluar el rendimiento local de Whisper
├── requirements.txt              # Dependencias del entorno
└── README.md                     # Documentación del proyecto
```

---

## 🚀 Funcionalidades principales

### 1️⃣ Automatización del scraping (`main_improved_v3.py`)
- Login automático en Blackboard usando credenciales seguras.
- Navegación por cursos y descarga de grabaciones.
- Prevención de sobrescrituras en nombres duplicados.
- Registro detallado del proceso en `webscrapping_improved_v3.log`.

### 2️⃣ Transcripción con Whisper (`transcriptor_videos.py`)
- Extrae el audio de los videos (`ffmpeg`) y lo convierte a formato `.wav`.
- Divide los audios en segmentos de 5 minutos para un procesamiento más estable.
- Genera archivos `.txt` con **marcas temporales cada minuto**.
- Muestra una **barra de progreso** con `tqdm` para monitorear el avance.

### 3️⃣ Benchmark de rendimiento (`whisper_benchmark.py`)
- Permite probar diferentes modelos de Whisper (`small`, `medium`).
- Evalúa tiempos de carga, transcripción y rendimiento relativo en CPU.
- Útil para determinar el mejor modelo según los recursos locales.

---

## ⚙️ Requisitos

### 🔧 Herramientas necesarias
- **Python 3.9+**
- **FFmpeg** (para extracción y conversión de audio)
- **Google Chrome** y **ChromeDriver**
- **Git** (para control de versiones)

### 📦 Instalación de dependencias
Instala todo con:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` incluye, entre otros:
- `selenium`
- `beautifulsoup4`
- `requests`
- `tqdm`
- `openai-whisper`
- `ffmpeg-python`

---

## 🧰 Instalación adicional

### 🖥️ Instalar FFmpeg en Windows
1. Descarga el archivo ZIP desde: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Extrae el contenido (por ejemplo en `C:\ffmpeg`).
3. Agrega `C:\ffmpeg\bin` a las **Variables de entorno del sistema** → `Path`.
4. Verifica la instalación:
   ```bash
   ffmpeg -version
   ```

### 🌐 Instalar ChromeDriver
1. Identifica tu versión de Chrome: escribe `chrome://settings/help` en la barra del navegador.
2. Descarga el `chromedriver.exe` correspondiente desde: [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)
3. Coloca el ejecutable dentro del directorio del proyecto o en una carpeta incluida en el `PATH`.

---

## 🔐 Manejo de credenciales

Para mayor seguridad, las credenciales de Blackboard deben gestionarse mediante **variables de entorno**.

### En Windows (PowerShell)
```bash
setx BLACKBOARD_USER "tu_usuario_viu"
setx BLACKBOARD_PASS "tu_contraseña_viu"
```

### En Linux / macOS
```bash
export BLACKBOARD_USER="tu_usuario_viu"
export BLACKBOARD_PASS="tu_contraseña_viu"
```

> 🔒 El script `main_improved_v3.py` lee automáticamente estas variables, evitando exponer datos sensibles en el código.

---

## 🧾 Ejecución de scripts

### 1️⃣ Descargar videos
```bash
python main_improved_v3.py
```

### 2️⃣ Transcribir clases
```bash
python transcriptor_videos.py "ruta_videos" "ruta_audios" "ruta_transcripciones"
```

### 3️⃣ Evaluar rendimiento del modelo
```bash
python whisper_benchmark.py
```

---

## 📂 Ejemplo de estructura generada

```
videos/
├── 03MBID_Procesamiento de datos masivos/
│   ├── 2025-06-02.mp4
│   ├── Audios/
│   │   ├── 2025-06-02.wav
│   └── Transcripciones/
│       ├── 2025-06-02.txt
```

Cada archivo `.txt` contiene las transcripciones completas con marcas como:
```
[⏱️ 00:00]
Bienvenidos a la clase...

[⏱️ 05:00]
Continuamos con la segunda parte...
```

---

## 📊 Logs

Los logs se almacenan automáticamente en:
- `webscrapping_improved_v3.log` (scraping)
- `transcripcion_videos.log` (transcripción)
- `whisper_benchmark.log` (benchmark)

---

## 💡 Recomendaciones
- Ejecuta los scripts desde un entorno virtual (`venv` o `conda`).
- Evita procesar más de 2–3 videos simultáneamente en CPU.
- Si tus videos son largos (más de 1 hora), usa el procesamiento por lotes que ya está implementado.

---

## 🧑‍💻 Autor
**Hernán Montes**  
Universidad Internacional de Valencia – Máster en Big Data y Ciencia de Datos  
📧 montesino77@gmail.com  
