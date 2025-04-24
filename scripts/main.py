import sys
import os
import subprocess
import shutil
import pandas as pd
import time
import logging
import signal
import psutil
from concurrent.futures import ThreadPoolExecutor

# Añadir ruta del proyecto al path para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extractor.email_extractor import extract_emails_from_url
from extractor.social_extractor import extract_essential_social_links_from_url
from extractor.column_editor import procesar_csvs_en_carpeta
from extractor.generador_excel import generar_excel

# Signal handler para Ctrl+C
signal.signal(signal.SIGINT, lambda sig, frame: (print("\n⏸ Proceso interrumpido por el usuario."), sys.exit(0)))

# Ruta absoluta al directorio del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Asegurar que el directorio 'logs/' existe
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configurar logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "procesamiento.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Reducir prioridad del proceso para no saturar la CPU del sistema
try:
    p = psutil.Process(os.getpid())
    # En Windows IDLE_PRIORITY_CLASS, en Linux un nice positivo
    if hasattr(psutil, 'IDLE_PRIORITY_CLASS'):
        p.nice(psutil.IDLE_PRIORITY_CLASS)
    else:
        p.nice(10)
except Exception:
    pass

# Rutas de datos y configuración
INPUT_FOLDER       = os.path.join(BASE_DIR, "data", "inputs")
CLEAN_INPUT_FOLDER = os.path.join(BASE_DIR, "data", "clean_inputs")
OUTPUT_FOLDER      = os.path.join(BASE_DIR, "data", "outputs")
EXTRACTOR_FOLDER   = os.path.join(BASE_DIR, "extractor")
TXT_CONFIG_DIR     = os.path.join(BASE_DIR, "config", "txt_config")

# Configuración
EMAIL_VERIFICATION_MODE = "avanzado"
modo_prueba             = False
# Número de hilos para extracción concurrente (I/O-bound)
MAX_WORKERS = min(4, max(1, os.cpu_count() // 2))
# MAX_WORKERS = min(8, max(1, os.cpu_count() - 1))

# -----------------------------
# Funciones de configuración
# -----------------------------
def cargar_lista_desde_txt(nombre_archivo):
    ruta = os.path.join(TXT_CONFIG_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def cargar_diccionario_desde_txt(nombre_archivo):
    ruta = os.path.join(TXT_CONFIG_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return {}
    with open(ruta, "r", encoding="utf-8") as f:
        return dict(line.strip().split(":", 1) for line in f if ":" in line)

# Cargar configuración de columnas
NUEVO_ORDEN         = cargar_lista_desde_txt("orden_columnas.txt")
RENOMBRAR_COLUMNAS  = cargar_diccionario_desde_txt("renombrar_columnas.txt")
COLUMNAS_A_ELIMINAR = cargar_lista_desde_txt("columnas_a_eliminar.txt")

# -----------------------------
# Limpieza inicial
# -----------------------------
def ejecutar_script_limpieza():
    script_path = os.path.join(EXTRACTOR_FOLDER, "limpiar_csv_lote.py")
    if not os.path.exists(script_path):
        print(f"❌ No se encontró el script: {script_path}")
        sys.exit(1)
    print(f"📂 Ejecutando limpieza con: {script_path}")
    res = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if res.returncode == 0:
        print("✅ Limpieza completada correctamente.")
    else:
        print(f"❌ Error en limpieza:\n{res.stderr}")

def filtrar_y_mover_archivos_limpios():
    print("\n🧹 Evaluando archivos tras limpieza...")
    os.makedirs(CLEAN_INPUT_FOLDER, exist_ok=True)
    for archivo in os.listdir(INPUT_FOLDER):
        if not archivo.lower().endswith(".csv"):
            continue
        src = os.path.join(INPUT_FOLDER, archivo)
        try:
            df = pd.read_csv(src)
            if "website" not in df.columns:
                print(f"⚠️ {archivo} no contiene 'website', eliminando.")
                os.remove(src)
                continue
            if any(col in df.columns for col in COLUMNAS_A_ELIMINAR):
                print(f"⛔ {archivo} contiene columnas a eliminar, eliminando.")
                os.remove(src)
                continue
            dst = os.path.join(CLEAN_INPUT_FOLDER, archivo)
            shutil.move(src, dst)
            print(f"✅ {archivo} movido a clean_inputs.")
        except Exception as e:
            print(f"❌ Error al procesar {archivo}: {e}")
            os.remove(src)

# -----------------------------
# Extracción de datos
# -----------------------------
def procesar_sitio(row):
    raw = row.get("website", "")
    if pd.isna(raw) or not isinstance(raw, str):
        return {**row, "email":"", "facebook":"", "instagram":"", "linkedin":"", "x":""}
    url = raw.strip()
    if not url.lower().startswith(("http://", "https://")):
        return {**row, "email":"", "facebook":"", "instagram":"", "linkedin":"", "x":""}
    print(f"🔍 Procesando {url}")
    emails = extract_emails_from_url(url, modo_verificacion=EMAIL_VERIFICATION_MODE)
    redes  = extract_essential_social_links_from_url(url)
    return {
        **row,
        "email":     ", ".join(emails),
        "facebook":  ", ".join(redes.get("facebook", [])),
        "instagram": ", ".join(redes.get("instagram", [])),
        "linkedin":  ", ".join(redes.get("linkedin", [])),
        "x":         ", ".join(redes.get("x", [])),
    }

def procesar_archivo(nombre_archivo):
    path_in  = os.path.join(CLEAN_INPUT_FOLDER, nombre_archivo)
    path_out = os.path.join(OUTPUT_FOLDER, nombre_archivo)
    if os.path.exists(path_out):
        print(f"⏩ {nombre_archivo} ya procesado, saltando.")
        return
    if os.path.getsize(path_in) == 0:
        print(f"❌ {nombre_archivo} está vacío.")
        return

    df = pd.read_csv(path_in)
    if "website" not in df.columns:
        print(f"❌ {nombre_archivo} no contiene 'website'.")
        return
    df.drop(columns=[c for c in COLUMNAS_A_ELIMINAR if c in df.columns], inplace=True)
    if modo_prueba:
        df = df.head(20)

    rows = df.to_dict(orient="records")
    # Extracción concurrente ligera
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        resultados = list(executor.map(procesar_sitio, rows))

    df_res = pd.DataFrame(resultados)
    df_res.rename(columns=RENOMBRAR_COLUMNAS, inplace=True)
    df_res = df_res.reindex(columns=[c for c in NUEVO_ORDEN if c in df_res.columns])

    print(f"✅ Procesados {nombre_archivo}, generando Excel...")
    generar_excel(df_res, nombre_archivo)

# -----------------------------
# Punto de entrada
# -----------------------------
if __name__ == "__main__":
    inicio = time.time()
    logging.info("🔄 Inicio de procesamiento CSV.")

    print("1 - Modo prueba (20 filas)\n2 - Modo completo")
    if input("Elige (1 o 2): ").strip() == "1":
        modo_prueba = True

    ejecutar_script_limpieza()
    if not os.path.isdir(CLEAN_INPUT_FOLDER):
        print(f"❌ No existe: {CLEAN_INPUT_FOLDER}")
        sys.exit(1)
    filtrar_y_mover_archivos_limpios()

    archivos = [f for f in os.listdir(CLEAN_INPUT_FOLDER) if f.lower().endswith(".csv")]
    for nombre in archivos:
        while True:
            try:
                print(f"\n▶️ Procesando archivo: {nombre}")
                procesar_archivo(nombre)
                break
            except KeyboardInterrupt:
                choice = input("\nHas pulsado Ctrl+C. [R]eanudar, [C]ancelar: ").strip().upper()
                if choice == 'R':
                    print("⏩ Reanudando...")
                    continue
                elif choice == 'C':
                    print("✋ Proceso cancelado por el usuario.")
                    sys.exit(0)
                else:
                    print("Opción no válida. Pulsa R o C.")

    print("\n🔧 Reordenando y renombrando columnas finales...")
    procesar_csvs_en_carpeta(
        carpeta_outputs=OUTPUT_FOLDER,
        nuevo_orden= NUEVO_ORDEN,
        renombrar_columnas= RENOMBRAR_COLUMNAS
    )

    dur = time.time() - inicio
    logging.info(f"✅ Completado en {dur:.2f}s.")
    print(f"\n⏱ Fin en {dur:.2f}s. Revisa procesamiento.log")
