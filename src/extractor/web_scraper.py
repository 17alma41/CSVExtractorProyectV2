"""
web_scraper.py - Módulo para extracción de emails y redes sociales usando Selenium.
"""

import os
import sys
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import psutil
import multiprocessing
from .utils import setup_driver as _shared_setup_driver
from .email_extractor import extract_emails_from_url
from .social_extractor import extract_essential_social_links_from_url
from src.settings import (
    BASE_DIR, INPUTS_DIR, OUTPUTS_DIR, CLEAN_INPUTS_DIR, TXT_CONFIG_DIR, LOGS_DIR, HOJA_DATA
)
from src.utils.status_manager import load_status, save_status, update_status, get_next_scraping_index, is_stage_done, log_error
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from fake_useragent import UserAgent

# Logging
logging.basicConfig(
    filename=LOGS_DIR / "procesamiento.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Thread-local para los drivers
thread_local = threading.local()
DRIVERS = []

def _shared_setup_driver(browser="chrome", proxy=None):
    """Configura el driver del navegador con soporte para múltiples navegadores y rotación de User-Agent."""
    user_agent = UserAgent().random  # Generar un User-Agent aleatorio
    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument(f"--user-agent={user_agent}")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        return webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        options.set_preference("general.useragent.override", user_agent)
        if proxy:
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", proxy.split(":")[0])
            options.set_preference("network.proxy.http_port", int(proxy.split(":")[1]))
        return webdriver.Firefox(service=FirefoxService(), options=options)
    elif browser == "edge":
        options = EdgeOptions()
        options.add_argument(f"--user-agent={user_agent}")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        return webdriver.Edge(service=EdgeService(), options=options)
    else:
        raise ValueError("Navegador no soportado. Use 'chrome', 'firefox' o 'edge'.")

# Modificar _init_thread_driver para aceptar múltiples navegadores y proxies

def _init_thread_driver(browser="chrome", proxy=None):
    drv = _shared_setup_driver(browser=browser, proxy=proxy)
    drv.set_page_load_timeout(30)  # Configurar timeout de carga de página
    drv.implicitly_wait(10)  # Configurar espera implícita
    thread_local.driver = drv
    DRIVERS.append(drv)

EMAIL_VERIFICATION_MODE = "avanzado"
MAX_WORKERS = 4
MAX_URLS_PER_SESSION = 50  # Reiniciar navegador después de procesar 50 URLs

def cargar_lista_desde_txt(nombre_archivo):
    ruta = TXT_CONFIG_DIR / nombre_archivo
    if not ruta.exists():
        return []
    with open(ruta, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

COLUMNAS_A_ELIMINAR = cargar_lista_desde_txt("columnas_a_eliminar.txt")
RENOMBRAR_COLUMNAS = {}
for line in cargar_lista_desde_txt("renombrar_columnas.txt"):
    if ":" in line:
        old, new = line.split(":", 1)
        RENOMBRAR_COLUMNAS[old.strip()] = new.strip()
NUEVO_ORDEN = cargar_lista_desde_txt("orden_columnas.txt")

def get_optimal_workers():
    cpu_count = multiprocessing.cpu_count()
    ram_gb = psutil.virtual_memory().total / (1024**3)
    return max(1, min(cpu_count, int(ram_gb // 2)))

def procesar_sitio(row, wait_timeout=10):
    try:
        raw = row.get('website', '')
        if pd.isna(raw) or not isinstance(raw, str):
            return {**row, 'email':'', 'facebook':'', 'instagram':'', 'linkedin':'', 'x':''}
        url = raw.strip()
        if not url.lower().startswith(('http://', 'https://')):
            return {**row, 'email':'', 'facebook':'', 'instagram':'', 'linkedin':'', 'x':''}
        emails = extract_emails_from_url(
            url,
            modo_verificacion=EMAIL_VERIFICATION_MODE,
            driver=thread_local.driver,
            wait_timeout=wait_timeout
        )
        redes = extract_essential_social_links_from_url(
            url,
            driver=thread_local.driver,
            wait_timeout=wait_timeout
        )
        return {
            **row,
            'email':      ', '.join(emails),
            'facebook':   ', '.join(redes.get('facebook', [])),
            'instagram':  ', '.join(redes.get('instagram', [])),
            'linkedin':   ', '.join(redes.get('linkedin', [])),
            'x':          ', '.join(redes.get('x', [])),
        }
    except Exception as e:
        logging.error(f"Error procesando sitio {row.get('website')}: {e}")
        return {**row, 'email':'', 'facebook':'', 'instagram':'', 'linkedin':'', 'x':''}

def reiniciar_sesion():
    """Cierra y reinicia la sesión del navegador."""
    try:
        if hasattr(thread_local, 'driver'):
            thread_local.driver.quit()
    except Exception as e:
        logging.error(f"Error cerrando sesión del navegador: {e}")
    finally:
        _init_thread_driver()

def procesar_archivo(nombre_archivo, modo_prueba=False, max_workers=None, wait_timeout=10, resume=False):
    path_in  = CLEAN_INPUTS_DIR / nombre_archivo
    path_out = OUTPUTS_DIR / nombre_archivo
    if path_out.exists() and not resume:
        return
    df = pd.read_csv(path_in)
    if 'website' not in df.columns:
        return
    df.drop(columns=[c for c in COLUMNAS_A_ELIMINAR if c in df.columns], inplace=True)
    if modo_prueba:
        df = df.head(20)
    rows = df.to_dict(orient='records')
    # Reanudación por índice
    start_idx = get_next_scraping_index(nombre_archivo) if resume else 0
    resultados = []
    def process_with_retry(row, idx, retries=2):
        for attempt in range(retries):
            try:
                res = procesar_sitio(row, wait_timeout=wait_timeout)
                update_status(nombre_archivo, 'scraping_index', idx+1)
                return res
            except Exception as e:
                log_error(nombre_archivo, 'scraping', row.get('website',''), str(e))
                time.sleep(2)
        return {**row, 'email':'', 'facebook':'', 'instagram':'', 'linkedin':'', 'x':''}
    workers = max_workers if max_workers else get_optimal_workers()
    urls_procesadas = 0
    with ThreadPoolExecutor(max_workers=workers, initializer=_init_thread_driver) as executor:
        futures = {executor.submit(process_with_retry, row, idx): idx for idx, row in enumerate(rows[start_idx:], start=start_idx)}
        for future in as_completed(futures):
            try:
                resultados.append(future.result())
                urls_procesadas += 1
                if urls_procesadas % MAX_URLS_PER_SESSION == 0:
                    reiniciar_sesion()
            except Exception as e:
                print(f"[ERROR] Excepción en scraping: {e}")
    for drv in DRIVERS:
        try:
            drv.quit()
        except Exception as e:
            logging.error(f"Error cerrando driver: {e}")
    df_res = pd.DataFrame(resultados)
    print(f"[DEBUG] DataFrame de resultados generado con {len(df_res)} filas.")
    if RENOMBRAR_COLUMNAS:
        df_res.rename(columns=RENOMBRAR_COLUMNAS, inplace=True)
    if NUEVO_ORDEN:
        cols_validas = [c for c in NUEVO_ORDEN if c in df_res.columns]
        if cols_validas:
            df_res = df_res.reindex(columns=cols_validas)
    if not df_res.empty:
        from .generador_excel import generar_excel
        print(f"[DEBUG] Llamando a generar_excel para {nombre_archivo}")
        generar_excel(df_res, nombre_archivo)
    else:
        print(f"[WARNING] DataFrame vacío, no se genera archivo para {nombre_archivo}")
    update_status(nombre_archivo, 'scraping_index', 0)  # Reset index

def run_extraction(overwrite=False, test_mode=False, max_workers=None, wait_timeout=10, resume=False, single_file=None, browser="chrome", proxy_list=None):
    """
    Ejecuta el proceso de extracción de datos web.
    Si single_file está definido, solo procesa ese archivo.
    """
    import time
    inicio = time.time()
    workers = max_workers if max_workers else get_optimal_workers()
    print(f"[SCRAPER] Usando {workers} hilos (threads) para scraping.")
    if not CLEAN_INPUTS_DIR.is_dir():
        print(f"❌ No existe clean_inputs.")
        return
    archivos = [single_file] if single_file else [f for f in os.listdir(CLEAN_INPUTS_DIR) if f.lower().endswith('.csv')]
    for nombre in archivos:
        try:
            if not overwrite and is_stage_done(nombre, 'scraped'):
                print(f"[SKIP] {nombre} ya scrapeado.")
                continue
            print(f"\n▶️ Procesando: {nombre}")
            proxy = random.choice(proxy_list) if proxy_list else None
            _init_thread_driver(browser=browser, proxy=proxy)
            procesar_archivo(nombre, modo_prueba=test_mode, max_workers=workers, wait_timeout=wait_timeout, resume=resume)
            update_status(nombre, 'scraped', True)
        except KeyboardInterrupt:
            print('✋ Proceso cancelado por el usuario.')
            return
        except Exception as e:
            log_error(nombre, 'scraping', '', str(e))
    duracion = time.time() - inicio
    print(f"✅ Fin en {duracion:.2f}s.")

if __name__ == "__main__":
    print("[INFO] Ejecutando scraping sobre archivos en clean_inputs...")
    run_extraction(overwrite=True, test_mode=True)
