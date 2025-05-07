
import sys
import os
import subprocess
import shutil
import pandas as pd
import time
import logging
import signal
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor

# Añadir ruta del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importaciones internas
from extractor.utils import setup_driver as _shared_setup_driver
from extractor.email_extractor import extract_emails_from_url
from extractor.social_extractor import extract_essential_social_links_from_url
from extractor.column_editor import procesar_csvs_en_carpeta
from extractor.generador_excel import generar_excel

# Ctrl+C amigable
def signal_handler(sig, frame):
    print("\n⏸ Proceso interrumpido. Puedes reanudar o cancelar cuando toque.")
signal.signal(signal.SIGINT, signal_handler)

# Thread-local para los drivers
thread_local = threading.local()
# Lista de drivers creados para cierre posterior
DRIVERS = []

def _init_thread_driver():
    """Inicializa un driver por hilo y lo añade a la lista DRIVERS."""
    drv = _shared_setup_driver()
    thread_local.driver = drv
    DRIVERS.append(drv)

# Configuración global de rutas
BASE_DIR           = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER       = os.path.join(BASE_DIR, "data", "inputs")
CLEAN_INPUT_FOLDER = os.path.join(BASE_DIR, "data", "clean_inputs")
OUTPUT_FOLDER      = os.path.join(BASE_DIR, "data", "outputs")
EXTRACTOR_FOLDER   = os.path.join(BASE_DIR, "extractor")
TXT_CONFIG_DIR     = os.path.join(BASE_DIR, "config", "txt_config")
LOG_DIR            = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "procesamiento.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
import urllib3
urllib3.disable_warnings()
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Reducir prioridad de proceso
def set_low_priority():
    try:
        p = psutil.Process(os.getpid())
        if hasattr(psutil, 'IDLE_PRIORITY_CLASS'):
            p.nice(psutil.IDLE_PRIORITY_CLASS)
        else:
            p.nice(10)
    except Exception:
        pass
set_low_priority()

# Modos y parámetros
EMAIL_VERIFICATION_MODE = "avanzado"
modo_prueba             = False
MAX_WORKERS             = 4  # Número de hilos para scraping

# ---------------- Configuración columnas ----------------
def cargar_lista_desde_txt(nombre_archivo):
    ruta = os.path.join(TXT_CONFIG_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return []
    with open(ruta, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

# Columnas a eliminar
COLUMNAS_A_ELIMINAR = cargar_lista_desde_txt("columnas_eliminar.txt")

# Diccionario de renombrado: formato "antiguo:Nuevo"
RENOMBRAR_COLUMNAS = {}
for line in cargar_lista_desde_txt("renombrar_columnas.txt"):
    if ":" in line:
        old, new = line.split(":", 1)
        RENOMBRAR_COLUMNAS[old.strip()] = new.strip()

# Orden de columnas: usa tu fichero real orden_columnas.txt
NUEVO_ORDEN = cargar_lista_desde_txt("orden_columnas.txt")

# ---------------- Funciones de procesamiento ----------------
def ejecutar_script_limpieza():
    scripts = [os.path.join(EXTRACTOR_FOLDER, 'limpiar_csv_lote.py')]
    for script_path in scripts:
        if not os.path.isfile(script_path):
            print(f"❌ No se encontró el script: {script_path}")
            sys.exit(1)
        print(f"📂 Ejecutando limpieza...")
        res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"❌ Error en limpieza: {res.stderr}")
            sys.exit(1)

def procesar_sitio(row):
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
            wait_timeout=10
        )
        redes = extract_essential_social_links_from_url(
            url,
            driver=thread_local.driver,
            wait_timeout=10
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

def procesar_archivo(nombre_archivo):
    path_in  = os.path.join(CLEAN_INPUT_FOLDER, nombre_archivo)
    path_out = os.path.join(OUTPUT_FOLDER, nombre_archivo)
    if os.path.exists(path_out) or os.path.getsize(path_in) == 0:
        return

    df = pd.read_csv(path_in)
    if 'website' not in df.columns:
        return
    df.drop(columns=[c for c in COLUMNAS_A_ELIMINAR if c in df.columns], inplace=True)
    if modo_prueba:
        df = df.head(20)

    rows = df.to_dict(orient='records')
    with ThreadPoolExecutor(max_workers=MAX_WORKERS, initializer=_init_thread_driver) as executor:
        resultados = list(executor.map(procesar_sitio, rows))

    # Cerrar todos los drivers creados
    for drv in DRIVERS:
        drv.quit()

    # Construir DataFrame final y aplicar renombrado/reindexado
    df_res = pd.DataFrame(resultados)
    if RENOMBRAR_COLUMNAS:
        df_res.rename(columns=RENOMBRAR_COLUMNAS, inplace=True)

    if NUEVO_ORDEN:
        cols_validas = [c for c in NUEVO_ORDEN if c in df_res.columns]
        if cols_validas:
            df_res = df_res.reindex(columns=cols_validas)

    generar_excel(df_res, nombre_archivo)

# ---------------- Script principal ----------------
if __name__ == '__main__':
    inicio = time.time()
    logging.info("🔄 Inicio del procesamiento CSV.")

    print('1 - Modo prueba (20 filas)\n2 - Modo completo')
    if input('Elige (1 o 2): ').strip() == '1':
        modo_prueba = True

    # 1) Ejecutar limpieza
    ejecutar_script_limpieza()

    # 2) Eliminar los CSVs originales que ya fueron limpiados
    for fname in os.listdir(CLEAN_INPUT_FOLDER):
        if fname.lower().endswith('.csv'):
            orig = os.path.join(INPUT_FOLDER, fname)
            if os.path.exists(orig):
                os.remove(orig)
    print("🗑️ Archivos originales eliminados de 'data/inputs'.")

    # 3) Procesar clean_inputs
    if not os.path.isdir(CLEAN_INPUT_FOLDER):
        print(f"❌ No existe clean_inputs.")
        sys.exit(1)

    procesar_csvs_en_carpeta(
        carpeta_outputs=CLEAN_INPUT_FOLDER,
        nuevo_orden=None,
        renombrar_columnas=None
    )

    archivos = [f for f in os.listdir(CLEAN_INPUT_FOLDER) if f.lower().endswith('.csv')]
    for nombre in archivos:
        try:
            print(f"\n▶️ Procesando: {nombre}")
            procesar_archivo(nombre)
        except KeyboardInterrupt:
            print('✋ Proceso cancelado por el usuario.')
            sys.exit(0)

    duracion = time.time() - inicio
    logging.info(f"✅ Completado en {duracion:.2f}s.")
    print(f"✅ Fin en {duracion:.2f}s.")
