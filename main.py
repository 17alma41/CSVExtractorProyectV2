
import os
import subprocess
import shutil
import pandas as pd
import time
import logging
from multiprocessing import Pool, cpu_count
from extractor.email_extractor import extract_emails_from_url
from extractor.social_extractor import extract_essential_social_links_from_url
from extractor.column_editor import procesar_csvs_en_carpeta
from extractor.generador_excel import generar_excel

# 📝 Configurar logging (para testeos)
logging.basicConfig(
    filename="procesamiento.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 📂 Rutas
BASE_DIR = os.path.dirname(__file__)
INPUT_FOLDER = os.path.join(BASE_DIR, "inputs")
CLEAN_INPUT_FOLDER = os.path.join(BASE_DIR, "clean_inputs")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
EXTRACTOR_FOLDER = os.path.join(BASE_DIR, "extractor")
TXT_CONFIG_DIR = os.path.join(BASE_DIR, "txt_config")

# 🚀 Configuración
EMAIL_VERIFICATION_MODE = "avanzado"

# 🧩 Funciones para leer archivos de configuración
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
        return dict(line.strip().split(":") for line in f if ":" in line)

# 🔁 Cargar configuración desde archivos .txt
NUEVO_ORDEN = cargar_lista_desde_txt("orden_columnas.txt")
RENOMBRAR_COLUMNAS = cargar_diccionario_desde_txt("renombrar_columnas.txt")
COLUMNAS_A_ELIMINAR = cargar_lista_desde_txt("columnas_a_eliminar.txt")

# 🧹 Ejecutar limpieza
def ejecutar_script_limpieza():
    script_path = os.path.join(EXTRACTOR_FOLDER, "limpiar_csv_lote.py")
    if not os.path.exists(script_path):
        print(f"❌ No se encontró el script: {script_path}")
        exit(1)
    print(f"📂 Ejecutando limpieza con: {script_path}")
    resultado = subprocess.run(["python", script_path], capture_output=True, text=True, encoding="utf-8")
    if resultado.returncode == 0:
        print("✅ Limpieza completada correctamente.")
    else:
        print(f"❌ Error en limpieza:\n{resultado.stderr}")

# ✅ Validar y mover archivo
def filtrar_y_mover_archivos_limpios():
    print("\n🧹 Evaluando archivos tras limpieza...")

    for archivo in os.listdir(INPUT_FOLDER):
        if not archivo.endswith(".csv"):
            continue

        archivo_origen = os.path.join(INPUT_FOLDER, archivo)
        try:
            df = pd.read_csv(archivo_origen)

            if "website" not in df.columns:
                print(f"⚠️ {archivo} no contiene columna 'website'. Eliminando archivo...")
                os.remove(archivo_origen)
                continue

            if any(col in df.columns for col in COLUMNAS_A_ELIMINAR):
                print(f"⛔ {archivo} contiene columnas a eliminar. Eliminando archivo...")
                os.remove(archivo_origen)
                continue

            shutil.move(archivo_origen, os.path.join(CLEAN_INPUT_FOLDER, archivo))
            print(f"✅ {archivo} movido a clean_inputs.")

        except Exception as e:
            print(f"❌ Error al procesar {archivo}: {e}")
            os.remove(archivo_origen)


# 🌐 Extraer datos desde sitio
def procesar_sitio(row_dict):
    website = row_dict.get("website", "")
    print(f"🔍 Procesando {website}")

    emails = extract_emails_from_url(website, modo_verificacion=EMAIL_VERIFICATION_MODE)
    redes = extract_essential_social_links_from_url(website)

    return {
        **row_dict,
        "email": ", ".join(emails),
        "facebook": ", ".join(redes.get("facebook", [])),
        "instagram": ", ".join(redes.get("instagram", [])),
        "linkedin": ", ".join(redes.get("linkedin", [])),
        "x": ", ".join(redes.get("x", []))
    }

# 🧠 Procesar archivo individual
def procesar_archivo(nombre_archivo):
    path_entrada = os.path.join(CLEAN_INPUT_FOLDER, nombre_archivo)
    output_path = os.path.join(OUTPUT_FOLDER, nombre_archivo)

    if os.path.exists(output_path):
        print(f"⏩ {nombre_archivo} ya ha sido procesado. Saltando...")
        return

    if os.path.getsize(path_entrada) == 0:
        print(f"❌ El archivo {nombre_archivo} está vacío.")
        return

    try:
        df = pd.read_csv(path_entrada)
        if "website" not in df.columns:
            print(f"❌ El archivo {nombre_archivo} no contiene columna 'website'")
            return

        if COLUMNAS_A_ELIMINAR:
            df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True)

        if modo_prueba:
            df = df.head(20)

        data_dicts = df.to_dict(orient="records")
        with Pool(processes=cpu_count()) as pool:
            resultados = pool.map(procesar_sitio, data_dicts)

        df_resultado = pd.DataFrame(resultados)
        df_resultado.rename(columns=RENOMBRAR_COLUMNAS, inplace=True)
        df_resultado = df_resultado.reindex(columns=[col for col in NUEVO_ORDEN if col in df_resultado.columns])

        df_resultado.to_csv(output_path, index=False)
        print(f"✅ Datos guardados en {output_path}")

        try:
            generar_excel(df_resultado, nombre_archivo)
        except Exception as e:
            print(f"❌ Error al generar Excel para {nombre_archivo}: {e}")

    except Exception as e:
        print(f"⚠️ Error al procesar {nombre_archivo}: {e}")

# ▶️ Ejecutar script completo
if __name__ == "__main__":
    tiempo_inicio = time.time()
    logging.info("🔄 Iniciando proceso de extracción y procesamiento CSV.")
    print("Selecciona el modo de ejecución:")
    print("1 - Modo prueba (20 filas por archivo)")
    print("2 - Modo completo (todos los datos)")
    seleccion = input("Elige una opción (1 o 2): ").strip()
    modo_prueba = seleccion == "1"

    ejecutar_script_limpieza()

    if not os.path.exists(CLEAN_INPUT_FOLDER):
        print(f"❌ No se encontró la carpeta de entrada: {CLEAN_INPUT_FOLDER}")
        exit(1)

    filtrar_y_mover_archivos_limpios()

    for archivo in os.listdir(CLEAN_INPUT_FOLDER):
        if archivo.endswith(".csv"):
            procesar_archivo(archivo)

    print("\n🔧 Reordenando y renombrando columnas de los archivos generados...")
    procesar_csvs_en_carpeta(
        carpeta_outputs=OUTPUT_FOLDER,
        nuevo_orden=NUEVO_ORDEN,
        renombrar_columnas=RENOMBRAR_COLUMNAS
    )

    duracion = time.time() - tiempo_inicio
    logging.info(f"✅ Proceso completado en {duracion:.2f} segundos.")
    print(f"\n⏱ Proceso finalizado en {duracion:.2f} segundos. Revisa 'procesamiento.log'.")

