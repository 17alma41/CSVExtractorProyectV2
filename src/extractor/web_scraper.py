"""
web_scraper.py - Módulo para extracción de emails y redes sociales usando Selenium.
"""

import os
import sys
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import psutil
import multiprocessing
from extractor.utils import setup_driver as _shared_setup_driver
from extractor.email_extractor import extract_emails_from_url
from extractor.social_extractor import extract_essential_social_links_from_url
from src.settings import (
    BASE_DIR, INPUTS_DIR, OUTPUTS_DIR, CLEAN_INPUTS_DIR, TXT_CONFIG_DIR, LOGS_DIR, HOJA_DATA
)
from src.utils.status_manager import load_status, save_status, update_status, get_next_scraping_index, is_stage_done, log_error

# Logging
logging.basicConfig(
    filename=LOGS_DIR / "procesamiento.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Thread-local para los drivers
thread_local = threading.local()
DRIVERS = []

def _init_thread_driver():
    drv = _shared_setup_driver()
    thread_local.driver = drv
    DRIVERS.append(drv)

EMAIL_VERIFICATION_MODE = "avanzado"
MAX_WORKERS = 4

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
    # Reintentos y cierre seguro de drivers
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
    with ThreadPoolExecutor(max_workers=workers, initializer=_init_thread_driver) as executor:
        for idx, row in enumerate(rows[start_idx:], start=start_idx):
            resultados.append(process_with_retry(row, idx))
    for drv in DRIVERS:
        try:
            drv.quit()
        except Exception:
            pass
    df_res = pd.DataFrame(resultados)
    if RENOMBRAR_COLUMNAS:
        df_res.rename(columns=RENOMBRAR_COLUMNAS, inplace=True)
    if NUEVO_ORDEN:
        cols_validas = [c for c in NUEVO_ORDEN if c in df_res.columns]
        if cols_validas:
            df_res = df_res.reindex(columns=cols_validas)
    from extractor.generador_excel import generar_excel
    generar_excel(df_res, nombre_archivo)
    update_status(nombre_archivo, 'scraping_index', 0)  # Reset index

def run_extraction(overwrite=False, test_mode=False, max_workers=None, wait_timeout=10, resume=False):
    """
    Ejecuta el proceso de extracción de datos web.
    """
    import time
    inicio = time.time()
    # Determinar número de workers
    workers = max_workers if max_workers else get_optimal_workers()
    print(f"[SCRAPER] Usando {workers} hilos (threads) para scraping.")
    # Ejecutar limpieza previa
    from src.extractor.limpiar_csv_lote import main as limpiar_main
    limpiar_main()
    # Eliminar CSVs originales ya limpiados
    for fname in os.listdir(INPUTS_DIR):
        if fname.lower().endswith('.csv'):
            orig = INPUTS_DIR / fname
            if orig.exists():
                os.remove(orig)
    print("🗑️ Archivos originales eliminados de 'data/inputs'.")
    # Procesar clean_inputs
    if not CLEAN_INPUTS_DIR.is_dir():
        print(f"❌ No existe clean_inputs.")
        return
    from src.extractor.column_editor import procesar_csvs_en_carpeta
    procesar_csvs_en_carpeta(
        carpeta_outputs=str(CLEAN_INPUTS_DIR),
        nuevo_orden=None,
        renombrar_columnas=None,
        overwrite=overwrite,
        test_mode=test_mode
    )
    archivos = [f for f in os.listdir(CLEAN_INPUTS_DIR) if f.lower().endswith('.csv')]
    for nombre in archivos:
        try:
            # Control de reanudación por archivo
            if not overwrite and is_stage_done(nombre, 'scraped'):
                print(f"[SKIP] {nombre} ya scrapeado.")
                continue
            print(f"\n▶️ Procesando: {nombre}")
            procesar_archivo(nombre, modo_prueba=test_mode, max_workers=workers, wait_timeout=wait_timeout, resume=resume)
            update_status(nombre, 'scraped', True)
        except KeyboardInterrupt:
            print('✋ Proceso cancelado por el usuario.')
            return
        except Exception as e:
            log_error(nombre, 'scraping', '', str(e))
    duracion = time.time() - inicio
    print(f"✅ Fin en {duracion:.2f}s.")
