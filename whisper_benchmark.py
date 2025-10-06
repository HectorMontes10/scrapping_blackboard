"""
Benchmark de Whisper para medir rendimiento en la máquina local.
Extrae 5 minutos de un video y prueba los modelos small y medium.
"""

import os
import time
import logging
import whisper
import subprocess
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('whisper_benchmark.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class WhisperBenchmark:
    """Benchmark para medir rendimiento de Whisper."""
    
    def __init__(self):
        self.videos_dir = "videos"
        self.temp_dir = "temp_benchmark"
        self.results = {}
        
    def find_test_video(self):
        """Encuentra un video de prueba en el directorio de videos."""
        try:
            videos_path = Path(self.videos_dir)
            if not videos_path.exists():
                logger.error(f"Directorio {self.videos_dir} no encontrado")
                return None
            
            # Buscar el primer archivo .mp4
            for course_dir in videos_path.iterdir():
                if course_dir.is_dir():
                    for video_file in course_dir.glob("*.mp4"):
                        logger.info(f"Video de prueba encontrado: {video_file}")
                        return str(video_file)
            
            logger.error("No se encontraron videos .mp4 en el directorio")
            return None
            
        except Exception as e:
            logger.error(f"Error buscando video de prueba: {e}")
            return None
    
    def extract_5_minutes(self, video_path):
        """Extrae los primeros 5 minutos del video usando ffmpeg."""
        try:
            # Crear directorio temporal
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # Archivo de salida
            output_path = os.path.join(self.temp_dir, "test_5min.mp4")
            
            logger.info(f"Extrayendo 5 minutos de: {video_path}")
            logger.info(f"Guardando en: {output_path}")
            
            # Comando ffmpeg para extraer 5 minutos
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-t", "300",  # 5 minutos = 300 segundos
                "-c", "copy",     # Copiar sin re-encoding para velocidad
                "-y",           # Sobrescribir archivo si existe
                output_path
            ]
            
            logger.info(f"Ejecutando: {' '.join(cmd)}")
            
            # Ejecutar ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Extracción de 5 minutos completada")
                return output_path
            else:
                logger.error(f"Error en ffmpeg: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extrayendo 5 minutos: {e}")
            return None
    
    def extract_audio(self, video_path):
        """Extrae audio del video en formato WAV (mono, 16kHz)."""
        try:
            audio_path = os.path.join(self.temp_dir, "test_audio.wav")
            
            logger.info(f"Extrayendo audio de: {video_path}")
            logger.info(f"Guardando audio en: {audio_path}")
            
            # Comando ffmpeg para extraer audio
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ac", "1",        # Mono
                "-ar", "16000",     # 16 kHz
                "-y",               # Sobrescribir
                audio_path
            ]
            
            logger.info(f"Ejecutando: {' '.join(cmd)}")
            
            # Ejecutar ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Extracción de audio completada")
                return audio_path
            else:
                logger.error(f"Error en ffmpeg: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extrayendo audio: {e}")
            return None
    
    def benchmark_model(self, model_name, audio_path):
        """Ejecuta benchmark de un modelo de Whisper."""
        try:
            logger.info(f"=== INICIANDO BENCHMARK DE MODELO: {model_name.upper()} ===")
            
            # Cargar modelo
            logger.info(f"Cargando modelo {model_name}...")
            start_load = time.time()
            model = whisper.load_model(model_name)
            load_time = time.time() - start_load
            logger.info(f"✓ Modelo {model_name} cargado en {load_time:.2f} segundos")
            
            # Transcribir audio
            logger.info(f"Transcribiendo audio con modelo {model_name}...")
            start_transcribe = time.time()
            result = model.transcribe(audio_path, language="es")
            transcribe_time = time.time() - start_transcribe
            logger.info(f"✓ Transcripción completada en {transcribe_time:.2f} segundos")
            
            # Guardar resultado
            output_path = os.path.join(self.temp_dir, f"transcription_{model_name}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
            logger.info(f"✓ Transcripción guardada en: {output_path}")
            
            # Calcular métricas
            audio_duration = len(result["text"]) / 100  # Estimación aproximada
            speed_ratio = audio_duration / transcribe_time if transcribe_time > 0 else 0
            
            benchmark_result = {
                "model": model_name,
                "load_time": load_time,
                "transcribe_time": transcribe_time,
                "total_time": load_time + transcribe_time,
                "text_length": len(result["text"]),
                "speed_ratio": speed_ratio,
                "output_file": output_path
            }
            
            logger.info(f"=== RESULTADOS DEL MODELO {model_name.upper()} ===")
            logger.info(f"Tiempo de carga: {load_time:.2f} segundos")
            logger.info(f"Tiempo de transcripción: {transcribe_time:.2f} segundos")
            logger.info(f"Tiempo total: {benchmark_result['total_time']:.2f} segundos")
            logger.info(f"Longitud del texto: {len(result['text'])} caracteres")
            logger.info(f"Velocidad relativa: {speed_ratio:.2f}x")
            
            return benchmark_result
            
        except Exception as e:
            logger.error(f"Error en benchmark del modelo {model_name}: {e}")
            return None
    
    def run_benchmark(self):
        """Ejecuta el benchmark completo."""
        try:
            logger.info("=== INICIANDO BENCHMARK DE WHISPER ===")
            
            # 1. Encontrar video de prueba
            video_path = self.find_test_video()
            if not video_path:
                return False
            
            # 2. Extraer 5 minutos
            video_5min = self.extract_5_minutes(video_path)
            if not video_5min:
                return False
            
            # 3. Extraer audio
            audio_path = self.extract_audio(video_5min)
            if not audio_path:
                return False
            
            # 4. Benchmark de modelos
            models_to_test = ["small", "medium"]
            results = []
            
            for model_name in models_to_test:
                logger.info(f"\n{'='*50}")
                logger.info(f"PROBANDO MODELO: {model_name.upper()}")
                logger.info(f"{'='*50}")
                
                result = self.benchmark_model(model_name, audio_path)
                if result:
                    results.append(result)
                
                # Limpiar memoria
                if 'model' in locals():
                    del model
            
            # 5. Comparar resultados
            self.compare_results(results)
            
            return True
            
        except Exception as e:
            logger.error(f"Error en benchmark: {e}")
            return False
    
    def compare_results(self, results):
        """Compara los resultados de los diferentes modelos."""
        try:
            logger.info(f"\n{'='*60}")
            logger.info("COMPARACIÓN DE RESULTADOS")
            logger.info(f"{'='*60}")
            
            if len(results) < 2:
                logger.warning("No hay suficientes resultados para comparar")
                return
            
            # Ordenar por tiempo total
            results.sort(key=lambda x: x['total_time'])
            
            logger.info(f"{'Modelo':<10} {'Carga (s)':<12} {'Transcripción (s)':<18} {'Total (s)':<12} {'Velocidad':<12}")
            logger.info("-" * 80)
            
            for result in results:
                logger.info(f"{result['model']:<10} {result['load_time']:<12.2f} {result['transcribe_time']:<18.2f} {result['total_time']:<12.2f} {result['speed_ratio']:<12.2f}")
            
            # Recomendación
            fastest = results[0]
            logger.info(f"\n🏆 MODELO MÁS RÁPIDO: {fastest['model']}")
            logger.info(f"⏱️  Tiempo total: {fastest['total_time']:.2f} segundos")
            
            # Análisis de calidad vs velocidad
            if len(results) >= 2:
                small_result = next((r for r in results if r['model'] == 'small'), None)
                medium_result = next((r for r in results if r['model'] == 'medium'), None)
                
                if small_result and medium_result:
                    time_diff = medium_result['total_time'] - small_result['total_time']
                    improvement = (time_diff / small_result['total_time']) * 100
                    
                    logger.info(f"\n📊 ANÁLISIS:")
                    logger.info(f"Medium es {improvement:.1f}% más lento que Small")
                    
                    if improvement < 50:
                        logger.info("💡 RECOMENDACIÓN: Usar modelo 'medium' (diferencia de tiempo aceptable)")
                    else:
                        logger.info("💡 RECOMENDACIÓN: Usar modelo 'small' (diferencia de tiempo significativa)")
            
        except Exception as e:
            logger.error(f"Error comparando resultados: {e}")
    
    def cleanup(self):
        """Limpia archivos temporales."""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info("Archivos temporales eliminados")
        except Exception as e:
            logger.warning(f"Error limpiando archivos temporales: {e}")


def main():
    """Función principal del benchmark."""
    benchmark = WhisperBenchmark()
    
    try:
        success = benchmark.run_benchmark()
        if success:
            logger.info("=== BENCHMARK COMPLETADO EXITOSAMENTE ===")
        else:
            logger.error("=== BENCHMARK FALLÓ ===")
        
        return success
        
    except KeyboardInterrupt:
        logger.info("Benchmark interrumpido por el usuario")
        return False
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return False
    finally:
        benchmark.cleanup()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
