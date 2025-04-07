import os
import subprocess
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from extractor.email_extractor import extract_emails_from_url
from extractor.social_extractor import extract_essential_social_links_from_url
from extractor.column_editor import procesar_csvs_en_carpeta

# 📂 Rutas de carpetas (IMPORTANTE: cambiar rutas)
EXTRACTOR_FOLDER = os.path.abspath(r"C:\Users\Usuario\Desktop\CSVExtractorProyect\extractor")
INPUT_FOLDER = os.path.abspath(r"C:\Users\Usuario\Desktop\CSVExtractorProyect\clean_inputs")
OUTPUT_FOLDER = os.path.abspath(r"C:\Users\Usuario\Desktop\CSVExtractorProyect\outputs")

# 🚀 Configuración
DEMO_MODE = True  # True para prueba, False para procesar
MAX_WORKERS = 5   # Ajusta según tu CPU/ChromeDriver

# ⚙️ Configuración de columnas
NUEVO_ORDEN = ["name",
    "main_category",
    "categories",
    "reviews",
    "rating",
    "address",
    "website",
    "email",
    "phone",
    "facebook",
    "instagram",
    "linkedin",
    "twitter",
    "description",
    "seo_keywords",
    "workday_timing",
    "closed_on",
    "competitors",
    "featured_image",
    "link",
    "place_id"]  # Ajusta a tus columnas reales
RENOMBRAR_COLUMNAS = {
    "review_keywords": "seo_keywords"
}

def ejecutar_script_limpieza():
    """Ejecuta limpiar_csv_lote.py desde la ruta especificada."""
    script_path = os.path.join(EXTRACTOR_FOLDER, "limpiar_csv_lote.py")

    if not os.path.exists(script_path):
        print(f"❌ No se encontró el script: {script_path}")
        exit(1)

    print(f"📂 Ejecutando limpieza con: {script_path}")
    python_exe = r"C:\Users\Usuario\AppData\Local\Programs\Python\Python313\python.exe"
    resultado = subprocess.run([python_exe, script_path], capture_output=True, text=True, encoding="utf-8")

    if resultado.returncode == 0:
        print("✅ Limpieza completada correctamente.")
    else:
        print(f"❌ Error en limpieza:\n{resultado.stderr}")


def procesar_sitio(row):
    website = row["website"]
    print(f"🔍 Procesando {website}")
    emails = extract_emails_from_url(website)
    redes = extract_essential_social_links_from_url(website)

    print(f"🔗 Redes encontradas en {website}: {redes}")

    return {
        **row,
        "email": ", ".join(emails),
        "facebook": ", ".join(redes.get("facebook", [])),
        "instagram": ", ".join(redes.get("instagram", [])),
        "linkedin": ", ".join(redes.get("linkedin", [])),
        "twitter": ", ".join(redes.get("twitter", []))
    }


def procesar_archivo(nombre_archivo, demo_mode=False):
    path_entrada = os.path.join(INPUT_FOLDER, nombre_archivo)

    if os.path.getsize(path_entrada) == 0:
        print(f"❌ El archivo {nombre_archivo} está vacío.")
        return

    try:
        df = pd.read_csv(path_entrada)

        if "website" not in df.columns:
            print(f"❌ El archivo {nombre_archivo} no contiene columna 'website'")
            return

        if demo_mode:
            df = df.head(20)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            resultados = list(executor.map(procesar_sitio, [row for _, row in df.iterrows()]))

        df_resultado = pd.DataFrame(resultados)
        output_path = os.path.join(OUTPUT_FOLDER, f"emails_{nombre_archivo}")
        df_resultado.to_csv(output_path, index=False)
        print(f"✅ Datos guardados en {output_path}")

    except pd.errors.EmptyDataError:
        print(f"❌ El archivo {nombre_archivo} está vacío o no tiene datos válidos.")
    except Exception as e:
        print(f"⚠️ Error al procesar {nombre_archivo}: {e}")


if __name__ == "__main__":
    ejecutar_script_limpieza()

    if not os.path.exists(INPUT_FOLDER):
        print(f"❌ No se encontró la carpeta de entrada: {INPUT_FOLDER}")
        exit(1)

    for archivo in os.listdir(INPUT_FOLDER):
        if archivo.endswith(".csv"):
            procesar_archivo(archivo, demo_mode=DEMO_MODE)

    # ✅ Reordenar y renombrar columnas al final
    print("\n🔧 Reordenando y renombrando columnas de los archivos generados...")
    procesar_csvs_en_carpeta(
        carpeta_outputs=OUTPUT_FOLDER,
        nuevo_orden=NUEVO_ORDEN,
        renombrar_columnas=RENOMBRAR_COLUMNAS
    )
