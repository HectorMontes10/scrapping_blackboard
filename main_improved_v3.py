"""
Script mejorado v3 con gestión segura de credenciales mediante variables de entorno (.env)
Versión con selectores más robustos y manejo mejorado de errores.
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# === CARGAR VARIABLES DE ENTORNO ===
load_dotenv()

BLACKBOARD_URL = os.getenv("BLACKBOARD_URL")
USERNAME = os.getenv("BLACKBOARD_USER")
PASSWORD = os.getenv("BLACKBOARD_PASS")

if not all([BLACKBOARD_URL, USERNAME, PASSWORD]):
    raise EnvironmentError("❌ Variables de entorno incompletas. Verifica tu archivo .env")

# Lista de prueba: solo las primeras 3 asignaturas
# COURSE_NAMES = [
#     "01MBID_04_A_2025-26_Fundamentos de la tecnología Big Data",
#     "02MBID_04_A_2025-26_Sistemas de almacenamiento y gestión Big Data",
#     "03MBID_04_A_2025-26_Procesamiento de datos masivos",
#     "04MBID_04_A_2025-26_Riesgo, Seguridad y Legislación en Sistemas de Información",
#     "05MBID_04_A_2025-26_Minería de datos",
#     "06MBID_04_A_2025-26_Estadística avanzada",
#     "07MBID_04_A_2025-26_Machine Learning",
#     "08MBID_04_A_2025-26_Visualización de Datos",
#     "09MBID_04_A_2025-26_Soluciones de Inteligencia de negocio",
#     "10MBID_04_A_2025-26_Ciencia de datos para la toma de decisiones estratégicas",
#     "14MBID_04_A_2025-26_Trabajo Fin de Máster (Big Data y Ciencia de Datos)",
#     "15MBID_04_A_2025-26_Prácticas Externas (Big Data y Ciencia de Datos)",
#     "16MBID_04_A_2025-26_CF - Herramientas de programación",
#     "17MBID_04_A_2025-26_CF - Herramientas de bases de datos",
#     "18MBID_04_A_2025-26_CF - Herramientas de estadística",
#     "Aula Refuerzo Área Ciencia y Tecnología",
#     "00CCC_04_A_2025-26_CC - Solución de problemas",
#     "01CCC_04_A_2025-26_CC - Resiliencia",
#     "02CCC_04_A_2025-26_CC - Inteligencia Emocional",
#     "03CCC_04_A_2025-26_CC - Habilidades de Comunicación",
#     "04-2025 Elecciones Representante de Estudiantes",
#     "04-2025 Máster Universitario en Big Data y Ciencia de Datos",
#     "04-2025 Comunidad Universitaria VIU",
#     "Ágora de Ciencia y Tecnología"
# ]

COURSE_NAMES = ["Ágora de Ciencia y Tecnología"]
START_DATE = "2025-01-01"
END_DATE = "2025-09-30"
MAX_VIDEOS_PER_COURSE = 500  # Solo 2 videos por asignatura para prueba

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('webscrapping_improved_v3.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ImprovedVideoScraperV3:
    """Scraper mejorado v3 con selectores más robustos y manejo de credenciales seguras."""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configura el WebDriver de Chrome."""
        try:
            chromedriver_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "chromedriver.exe"
            )
            
            if not os.path.exists(chromedriver_path):
                raise FileNotFoundError(f"ChromeDriver no encontrado: {chromedriver_path}")
            
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 15)
            
            logger.info("ChromeDriver configurado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error configurando ChromeDriver: {e}")
            return False
    
    def login_to_blackboard(self):
        """Realiza el login en Blackboard."""
        try:
            logger.info(f"Navegando a Blackboard: {BLACKBOARD_URL}")
            self.driver.get(BLACKBOARD_URL)
            time.sleep(2)
            
            # Manejar pop-ups
            self._handle_popups()
            
            # Hacer clic en Login
            logger.info("Haciendo clic en el botón 'Login'...")
            login_button = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//a[contains(@href, 'learn.universidadviu.com/webapps/login/')]"
                ))
            )
            self.driver.execute_script("arguments[0].click();", login_button)
            
            # Esperar cambio de URL
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("learn.universidadviu.com/webapps/login/")
            )
            
            # Manejar pop-up de privacidad
            try:
                privacy_button = self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH, "//button[contains(., 'Aceptar')]"
                    ))
                )
                self.driver.execute_script("arguments[0].click();", privacy_button)
            except TimeoutException:
                pass
            
            # Introducir credenciales
            logger.info("Introduciendo credenciales...")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "user_id"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            
            username_field.clear()
            username_field.send_keys(USERNAME)
            password_field.clear()
            password_field.send_keys(PASSWORD)
            
            # Login final
            login_final_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "entry-login"))
            )
            login_final_button.click()
            
            # Esperar login exitoso
            WebDriverWait(self.driver, 20).until(
                EC.url_to_be("https://oncampus.universidadviu.com/?check_logged_in=1")
            )
            
            logger.info("Login exitoso!")
            return True
            
        except Exception as e:
            logger.error(f"Error durante el login: {e}")
            return False
    
    def _handle_popups(self):
        """Maneja pop-ups comunes."""
        try:
            # Pop-up de cookies
            cookie_popup = self.wait.until(
                EC.presence_of_element_located((By.ID, "sliding-popup"))
            )
            self.driver.execute_script(
                "arguments[0].style.display = 'none';", cookie_popup
            )
            logger.info("Pop-up de cookies ocultado")
        except TimeoutException:
            pass
        
        try:
            # Pop-up educativo
            education_popup = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//article[@data-component-id='wingsuit:card' and contains(., 'Nuevo acceso con cuenta educativa')]"
                ))
            )
            self.driver.execute_script(
                "arguments[0].style.display = 'none';", education_popup
            )
            logger.info("Pop-up educativo ocultado")
        except TimeoutException:
            pass
    
    def navigate_to_recordings(self):
        """Navega a la sección de grabaciones."""
        try:
            logger.info("Navegando a la sección de grabaciones...")
            
            # Desplazar para hacer visible el botón
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(3)
            
            # Hacer clic en Grabaciones
            recordings_button = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[contains(@class, 'tabs__summary')]//div[@data-component-id='wingsuit:button' and normalize-space(.//span)='Grabaciones']"
                ))
            )
            
            # Activar pestaña de grabaciones
            self._activate_recordings_tab(recordings_button)
            
            # Esperar contenido
            self._wait_for_recordings_content()
            
            logger.info("Navegación a grabaciones exitosa")
            return True
            
        except Exception as e:
            logger.error(f"Error navegando a grabaciones: {e}")
            return False
    
    def _activate_recordings_tab(self, recordings_button):
        """Activa la pestaña de grabaciones."""
        try:
            # Ejecutar script Alpine.js
            self.driver.execute_async_script("""
                const elem = arguments[0];
                const done = arguments[arguments.length - 1];
                (async () => {
                    try {
                        if (!elem) {
                            done({mode: 'error', detail: 'Elemento vacío'});
                            return;
                        }

                        let current = elem;
                        let alpineData = null;

                        while (current && !alpineData) {
                            if (current._x_dataStack) {
                                for (const scope of current._x_dataStack) {
                                    if (scope && (scope.active_tab !== undefined || scope.recordingsLoaded !== undefined)) {
                                        alpineData = scope;
                                        break;
                                    }
                                }
                            }
                            if (current.__alpine__) {
                                alpineData = current.__alpine__.$data || current.__alpine__;
                                break;
                            }
                            if (current.__x) {
                                alpineData = current.__x.$data || current.__x;
                                break;
                            }
                            current = current.parentElement;
                        }

                        if (!alpineData) {
                            elem.click();
                            done({mode: 'native-click'});
                            return;
                        }

                        alpineData.active_tab = 1;
                        if (alpineData.ajaxing !== undefined) alpineData.ajaxing = false;
                        if (alpineData.recordingsLoaded !== undefined) alpineData.recordingsLoaded = true;

                        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                        if (window.pfu && typeof window.pfu.ajaxRequest === 'function') {
                            try {
                                await window.pfu.ajaxRequest('/classes/recordings', 'recordings', {progressOptions: {}, body: {timezone}});
                            } catch (ajaxError) {
                                console.warn('pfu.ajaxRequest error:', ajaxError);
                            }
                        }

                        done({mode: 'alpine', detail: 'Pestaña activada'});
                    } catch (error) {
                        elem.click();
                        done({mode: 'fallback-click', detail: error.message});
                    }
                })();
            """, recordings_button)
            
            # Forzar visualización
            self.driver.execute_script("""
                const root = document.querySelector("div[data-component-id='wingsuit:tabs']");
                if (root) {
                    const buttons = root.querySelectorAll(".tabs__summary [data-component-id='wingsuit:button']");
                    const panels = root.querySelectorAll('.tabs__content > div');
                    buttons.forEach((btn, idx) => {
                        const isGrabaciones = idx === 0;
                        btn.classList.toggle('font-bold', isGrabaciones);
                        btn.classList.toggle('border-main-500', isGrabaciones);
                    });
                    panels.forEach((panel, idx) => {
                        const isGrabaciones = idx === 0;
                        if (isGrabaciones) {
                            panel.removeAttribute('hidden');
                            panel.style.removeProperty('display');
                        } else {
                            panel.setAttribute('hidden', 'true');
                            panel.style.display = 'none';
                        }
                    });
                }
            """)
            
        except Exception as e:
            logger.warning(f"Error activando pestaña: {e}")
    
    def _wait_for_recordings_content(self):
        """Espera a que el contenido de grabaciones esté disponible."""
        try:
            WebDriverWait(self.driver, 20).until(
                lambda d: d.execute_script("""
                    const root = document.querySelector("div[data-component-id='wingsuit:tabs']");
                    if (!root) return false;
                    const panel = root.querySelector('.tabs__content > div');
                    if (!panel) return false;
                    const hiddenAttr = panel.getAttribute('hidden');
                    const style = getComputedStyle(panel);
                    return hiddenAttr === null && style.display !== 'none' && style.visibility !== 'hidden' && panel.offsetHeight > 0;
                """)
            )
            
            WebDriverWait(self.driver, 20).until(
                lambda d: d.execute_script("""
                    const content = document.getElementById('recordings__content');
                    return content && content.children && content.children.length > 0;
                """)
            )
            
            time.sleep(1)
            
        except TimeoutException:
            logger.warning("Timeout esperando contenido de grabaciones")
    
    def reset_form_for_new_course(self):
        """Resetea el formulario para una nueva asignatura - VERSIÓN MEJORADA."""
        try:
            logger.info("Reseteando formulario para nueva asignatura...")
            
            # Estrategia mejorada: navegar directamente a la URL de grabaciones
            recordings_url = "https://oncampus.universidadviu.com/classes/recordings"
            logger.info(f"Navegando directamente a: {recordings_url}")
            
            self.driver.get(recordings_url)
            time.sleep(5)  # Esperar que la página cargue
            
            # Verificar que estamos en la página correcta
            current_url = self.driver.current_url
            logger.info(f"URL actual después de navegación: {current_url}")
            
            # Esperar a que el contenido de grabaciones esté disponible
            try:
                WebDriverWait(self.driver, 20).until(
                    lambda d: d.execute_script("""
                        const content = document.getElementById('recordings__content');
                        return content && content.children && content.children.length >= 0;
                    """)
                )
                logger.info("Contenido de grabaciones disponible")
            except TimeoutException:
                logger.warning("Timeout esperando contenido de grabaciones después del reseteo")
            
            logger.info("Formulario reseteado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error reseteando formulario: {e}")
            return False
    
    def apply_filters(self, course_name, start_date, end_date):
        """Aplica filtros para una asignatura con selectores más robustos."""
        try:
            logger.info(f"Aplicando filtros para: {course_name}")
            
            time.sleep(2)
            
            # Intentar múltiples estrategias para encontrar los campos
            success = False
            
            # Estrategia 1: XPaths específicos (originales)
            if self._try_specific_xpaths(course_name, start_date, end_date):
                success = True
            else:
                logger.warning("XPaths específicos fallaron, intentando selectores alternativos...")
                
                # Estrategia 2: Selectores por placeholder y tipo
                if self._try_alternative_selectors(course_name, start_date, end_date):
                    success = True
                else:
                    logger.warning("Selectores alternativos fallaron, intentando búsqueda por texto...")
                    
                    # Estrategia 3: Búsqueda por texto visible
                    if self._try_text_based_selectors(course_name, start_date, end_date):
                        success = True
            
            if success:
                time.sleep(3)
                logger.info("Filtros aplicados exitosamente")
                return True
            else:
                logger.error("Todas las estrategias de filtrado fallaron")
                return False
                
        except Exception as e:
            logger.error(f"Error aplicando filtros: {e}")
            return False
    
    def _try_specific_xpaths(self, course_name, start_date, end_date):
        """Intenta usar los XPaths específicos originales."""
        try:
            search_xpath = "//*[@id='block-wingsuit-content']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[2]/form/label[1]/span/input"
            start_date_xpath = "//*[@id='block-wingsuit-content']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[2]/form/label[2]/input"
            end_date_xpath = "//*[@id='block-wingsuit-content']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[2]/form/label[3]/input"
            
            self._set_filter_value(search_xpath, course_name, "búsqueda (XPath específico)")
            self._set_filter_value(start_date_xpath, self._format_date(start_date), "fecha inicio (XPath específico)")
            self._set_filter_value(end_date_xpath, self._format_date(end_date), "fecha fin (XPath específico)")
            
            return True
            
        except Exception as e:
            logger.debug(f"XPaths específicos fallaron: {e}")
            return False
    
    def _try_alternative_selectors(self, course_name, start_date, end_date):
        """Intenta usar selectores alternativos más genéricos."""
        try:
            # Buscar por placeholder
            search_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Buscar']")
            self._set_filter_value_js(search_input, course_name, "búsqueda (placeholder)")
            
            # Buscar campos de fecha por tipo
            date_inputs = self.driver.find_elements(By.XPATH, "//input[@type='date']")
            if len(date_inputs) >= 2:
                self._set_filter_value_js(date_inputs[0], self._format_date(start_date), "fecha inicio (tipo date)")
                self._set_filter_value_js(date_inputs[1], self._format_date(end_date), "fecha fin (tipo date)")
            
            return True
            
        except Exception as e:
            logger.debug(f"Selectores alternativos fallaron: {e}")
            return False
    
    def _try_text_based_selectors(self, course_name, start_date, end_date):
        """Intenta encontrar campos por texto visible."""
        try:
            # Buscar formulario por texto
            form_elements = self.driver.find_elements(By.XPATH, "//form//input")
            
            for element in form_elements:
                try:
                    # Verificar si es campo de búsqueda
                    if element.get_attribute("placeholder") and "buscar" in element.get_attribute("placeholder").lower():
                        self._set_filter_value_js(element, course_name, "búsqueda (texto)")
                    # Verificar si es campo de fecha
                    elif element.get_attribute("type") == "date":
                        # Determinar si es inicio o fin por posición o contexto
                        parent = element.find_element(By.XPATH, "./..")
                        if "inicio" in parent.text.lower() or "start" in parent.text.lower():
                            self._set_filter_value_js(element, self._format_date(start_date), "fecha inicio (texto)")
                        elif "fin" in parent.text.lower() or "end" in parent.text.lower():
                            self._set_filter_value_js(element, self._format_date(end_date), "fecha fin (texto)")
                except:
                    continue
            
            return True
            
        except Exception as e:
            logger.debug(f"Selectores basados en texto fallaron: {e}")
            return False
    
    def _set_filter_value(self, xpath, value, filter_name):
        """Establece el valor de un filtro usando XPath."""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            self._set_filter_value_js(element, value, filter_name)
            
        except Exception as e:
            logger.error(f"Error estableciendo filtro {filter_name}: {e}")
            raise
    
    def _set_filter_value_js(self, element, value, filter_name):
        """Establece el valor de un filtro usando JavaScript."""
        try:
            self.driver.execute_script("""
                const elem = arguments[0];
                const val = arguments[1];
                elem.focus();
                elem.value = '';
                elem.value = val;
                elem.dispatchEvent(new Event('input', { bubbles: true }));
                elem.dispatchEvent(new Event('change', { bubbles: true }));
                
                if (elem._x_model) {
                    elem._x_model.set(val);
                }
                
                let alpineEl = elem;
                while (alpineEl && !alpineEl.__x) {
                    alpineEl = alpineEl.parentElement;
                }
                if (alpineEl && alpineEl.__x) {
                    alpineEl.__x.$data.text = val;
                }
            """, element, value)
            
            logger.info(f"✓ Filtro {filter_name} establecido: {value}")
            
        except Exception as e:
            logger.error(f"Error estableciendo filtro {filter_name}: {e}")
            raise
    
    def _format_date(self, date_str):
        """Formatea fecha a YYYY-MM-DD."""
        parts = date_str.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1]}-{parts[2]}"
        return date_str
    
    def extract_recording_details(self):
        """Extrae detalles de grabaciones de la página actual."""
        try:
            recording_details = []
            recording_elements = self.driver.find_elements(
                By.XPATH, 
                "//div[@id='recordings__content']//a[contains(@href, '/classes/recordings/get-link/')]"
            )
            
            for element in recording_elements:
                try:
                    video_link = element.get_attribute("href")
                    
                    day_element = element.find_element(
                        By.XPATH, 
                        ".//div[contains(@class, 'circle-card__circle')]//div[contains(@class, 'font-bold')]"
                    )
                    day = day_element.text.strip()
                    
                    month_element = element.find_element(
                        By.XPATH, 
                        ".//div[contains(@class, 'circle-card__circle')]//div[contains(@class, 'uppercase')]"
                    )
                    month_abbr = month_element.text.strip()
                    
                    month_map = {
                        "ene": "01", "feb": "02", "mar": "03", "abr": "04", 
                        "may": "05", "mayo": "05", "jun": "06", "jul": "07", "ago": "08", 
                        "sep": "09", "oct": "10", "nov": "11", "dic": "12"
                    }
                    month_num = month_map.get(month_abbr.lower(), "00")
                    
                    year = START_DATE.split("-")[0]
                    file_date = f"{year}-{month_num}-{day.zfill(2)}"
                    
                    recording_details.append({
                        "link": video_link, 
                        "date": file_date
                    })
                    
                except Exception as e:
                    logger.warning(f"Error extrayendo detalles de grabación: {e}")
                    continue
            
            return recording_details
            
        except Exception as e:
            logger.error(f"Error extrayendo detalles de grabaciones: {e}")
            return []
    
    def process_course_recordings(self, course_name, start_date, end_date, is_first_course=False):
        """Procesa grabaciones de una asignatura."""
        try:
            logger.info(f"Procesando asignatura: {course_name}")
            
            # Resetear formulario si no es la primera asignatura
            if not is_first_course:
                if not self.reset_form_for_new_course():
                    logger.error("Error reseteando formulario")
                    return []
            
            # Aplicar filtros
            if not self.apply_filters(course_name, start_date, end_date):
                logger.error("Error aplicando filtros")
                return []
            
            all_recording_details = []
            page = 0
            max_pages = 50
            
            while page < max_pages:
                logger.info(f"Procesando página {page} para {course_name}")
                
                current_page_details = self.extract_recording_details()
                
                if not current_page_details:
                    logger.info("No hay más grabaciones")
                    break
                
                all_recording_details.extend(current_page_details)
                
                # Verificar siguiente página
                next_page_buttons = self.driver.find_elements(
                    By.XPATH, 
                    "//a[@data-tippy-content='Siguiente página']"
                )
                
                if not next_page_buttons or not next_page_buttons[0].is_displayed():
                    break
                
                button_disabled = self.driver.execute_script("""
                    const btn = arguments[0];
                    return btn.disabled || 
                           btn.classList.contains('disabled') || 
                           btn.getAttribute('aria-disabled') === 'true';
                """, next_page_buttons[0])
                
                if button_disabled:
                    break
                
                self.driver.execute_script("arguments[0].click();", next_page_buttons[0])
                page += 1
                time.sleep(5)
            
            logger.info(f"Total grabaciones encontradas para {course_name}: {len(all_recording_details)}")
            return all_recording_details
            
        except Exception as e:
            logger.error(f"Error procesando asignatura {course_name}: {e}")
            return []
    
    def get_video_download_link(self, video_session_url):
        """Obtiene enlace de descarga del video."""
        try:
            self.driver.get(video_session_url)
            video_source_element = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//video[@id='player-overlay']//source"
                ))
            )
            return video_source_element.get_attribute("src")
        except Exception as e:
            logger.error(f"Error obteniendo enlace de descarga: {e}")
            return None
    
    def download_video(self, download_url, folder_name, file_name):
        """Descarga un video, evitando sobrescrituras con un incremental único."""
        try:
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            base_path = os.path.join(folder_name, f"{file_name}.mp4")
            final_path = base_path
            counter = 1

            # En caso de colisión, agregar sufijo incremental
            while os.path.exists(final_path):
                final_path = os.path.join(folder_name, f"{file_name}_{counter}.mp4")
                counter += 1

            logger.info(f"Descargando {download_url} a {final_path}")

            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            with open(final_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Descarga completa: {os.path.basename(final_path)}")
            return True

        except Exception as e:
            logger.error(f"Error descargando video: {e}")
            return False
                
    def run(self):
        """Ejecuta el proceso completo."""
        try:
            logger.info("=== INICIANDO PROCESO MEJORADO V3 ===")
            
            # Configurar navegador
            if not self.setup_driver():
                return False
            
            # Login
            if not self.login_to_blackboard():
                return False
            
            # Navegar a grabaciones
            if not self.navigate_to_recordings():
                return False
            
            # Procesar cada asignatura
            for i, course_name in enumerate(COURSE_NAMES):
                logger.info(f"=== PROCESANDO ASIGNATURA {i+1}/{len(COURSE_NAMES)}: {course_name} ===")
                
                recording_details = self.process_course_recordings(
                    course_name, START_DATE, END_DATE, is_first_course=(i == 0)
                )
                
                if not recording_details:
                    logger.warning(f"No se encontraron grabaciones para {course_name}")
                    continue
                
                # Aplicar límite si es necesario
                if MAX_VIDEOS_PER_COURSE and len(recording_details) > MAX_VIDEOS_PER_COURSE:
                    logger.info(f"Limitando a {MAX_VIDEOS_PER_COURSE} videos")
                    recording_details = recording_details[:MAX_VIDEOS_PER_COURSE]
                
                # Descargar videos
                course_folder = os.path.join("videos", course_name)
                successful = 0
                
                for j, detail in enumerate(recording_details, 1):
                    session_link = detail["link"]
                    file_name_date = detail["date"]
                    
                    logger.info(f"Procesando video {j}/{len(recording_details)}: {file_name_date}")
                    
                    download_link = self.get_video_download_link(session_link)
                    if download_link:
                        if self.download_video(download_link, course_folder, file_name_date):
                            successful += 1
                    
                    time.sleep(1)
                
                logger.info(f"=== {course_name} COMPLETADA: {successful}/{len(recording_details)} videos descargados ===")
            
            logger.info("=== PROCESO COMPLETADO ===")
            return True
            
        except Exception as e:
            logger.error(f"Error en el proceso: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    scraper = ImprovedVideoScraperV3()
    success = scraper.run()
    exit(0 if success else 1)
