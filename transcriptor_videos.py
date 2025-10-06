import os
import sys
import time
import math
import logging
import subprocess
from pathlib import Path
from tqdm import tqdm
import tempfile


# === CONFIGURACIÓN DE LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('transcripcion_videos_vulkan.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class WhisperTranscriberVulkan:
    def __init__(self, videos_dir, audios_dir, transcripts_dir, whisper_cli_path, model_path):
        self.videos_dir = Path(videos_dir)
        self.audios_dir = Path(audios_dir)
        self.transcripts_dir = Path(transcripts_dir)
        self.whisper_cli_path = Path(whisper_cli_path)
        self.model_path = Path(model_path)

        self.audios_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=== CONFIGURACIÓN DEL ENTORNO ===")
        logger.info(f"📂 Videos: {self.videos_dir.resolve()}")
        logger.info(f"🎧 Audios: {self.audios_dir.resolve()}")
        logger.info(f"📝 Transcripciones: {self.transcripts_dir.resolve()}")
        logger.info(f"🧠 Binario Whisper: {self.whisper_cli_path.resolve()}")
        logger.info(f"🧩 Modelo: {self.model_path.resolve()}")
        logger.info("🚀 Backend activo: Vulkan (AMD GPU detectada automáticamente)")

    # --- EXTRAER AUDIO DE VIDEO ---
    def extract_audio(self, video_path):
        try:
            audio_path = self.audios_dir / f"{video_path.stem}.wav"
            if audio_path.exists():
                return audio_path
            cmd = [
                "ffmpeg", "-i", str(video_path),
                "-ac", "1", "-ar", "16000", "-y", str(audio_path)
            ]
            subprocess.run(cmd, capture_output=True, text=True)
            return audio_path
        except Exception as e:
            logger.error(f"Error extrayendo audio: {e}")
            return None

    # --- OBTENER DURACIÓN DEL AUDIO ---
    def get_audio_duration(self, audio_path):
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            return float(result.stdout.strip())
        except ValueError:
            return 0

    # --- TRANSCRIBIR EN FRAGMENTOS USANDO WHISPER-CLI ---
    def transcribe_in_chunks(self, audio_path, chunk_duration=300):
        transcript_path = self.transcripts_dir / f"{audio_path.stem}.txt"
        total_duration = self.get_audio_duration(audio_path)
        total_chunks = math.ceil(total_duration / chunk_duration)

        logger.info(f"Duración total: {total_duration:.1f}s ({total_chunks} segmentos máx. de 5 min cada uno)")

        with open(transcript_path, "w", encoding="utf-8") as f_out:
            with tqdm(total=total_chunks, desc=f"Transcribiendo {audio_path.stem}", unit="segmento") as pbar:
                for i in range(total_chunks):
                    start_time = i * chunk_duration
                    end_time = min(start_time + chunk_duration, total_duration)

                    temp_chunk = Path(tempfile.gettempdir()) / f"chunk_{i}_{audio_path.stem}.wav"
                    cmd = [
                        "ffmpeg", "-ss", str(start_time), "-t", str(chunk_duration),
                        "-i", str(audio_path), "-ac", "1", "-ar", "16000", "-y", str(temp_chunk)
                    ]
                    subprocess.run(cmd, capture_output=True, text=True)

                    # Ejecutar whisper-cli.exe
                    out_path = self.transcripts_dir / f"{audio_path.stem}_chunk_{i}.txt"
                    cmd_whisper = [
                        str(self.whisper_cli_path),
                        "-m", str(self.model_path),
                        "-f", str(temp_chunk),
                        "-otxt",
                        "-l", "es",
                        "-of", str(out_path.with_suffix(""))  # salida sin extensión duplicada
                    ]
                    subprocess.run(cmd_whisper, capture_output=True, text=True)

                    # Leer resultado temporal
                    if out_path.exists():
                        with open(out_path, "r", encoding="utf-8") as f_chunk:
                            text = f_chunk.read().strip()
                        out_path.unlink(missing_ok=True)
                    else:
                        text = "[⚠️ No se generó salida en este fragmento]"

                    if not text:
                        text = "[⚠️ Fragmento sin voz detectada]"

                    f_out.write(f"\n\n{text}\n")
                    f_out.write(f"[⏱️ {math.floor(end_time / 60):02d}:00]\n")

                    f_out.flush()
                    os.fsync(f_out.fileno())
                    temp_chunk.unlink(missing_ok=True)
                    pbar.update(1)
                    time.sleep(0.2)

        if os.path.getsize(transcript_path) == 0:
            logger.warning(f"⚠️ Transcripción vacía: {transcript_path}")
        else:
            logger.info(f"✓ Transcripción final guardada en {transcript_path.name}")

    # --- FLUJO PRINCIPAL ---
    def run(self):
        video_files = list(self.videos_dir.glob("*.mp4"))
        if not video_files:
            logger.warning("No se encontraron videos para transcribir.")
            return False

        logger.info(f"{len(video_files)} videos encontrados.")
        for video_path in video_files:
            logger.info(f"\n=== Procesando: {video_path.name} ===")
            audio_path = self.extract_audio(video_path)
            if audio_path:
                self.transcribe_in_chunks(audio_path)

        logger.info("✅ Todas las transcripciones completadas.")
        return True


def main():
    if len(sys.argv) < 6:
        print("Uso: python transcriptor_videos_vulkan.py <ruta_videos> <ruta_audios> <ruta_transcripciones> <ruta_whisper_cli> <ruta_modelo>")
        sys.exit(1)

    videos_dir, audios_dir, transcripts_dir, whisper_cli_path, model_path = sys.argv[1:6]
    transcriber = WhisperTranscriberVulkan(videos_dir, audios_dir, transcripts_dir, whisper_cli_path, model_path)
    transcriber.run()


if __name__ == "__main__":
    main()
